from __future__ import annotations

import time

from app.core.config import get_settings
from app.core.errors import ExternalProviderError, IntegrationError
from app.data.repository import RestaurantRepository
from app.domain.models import (
    RecommendationMeta,
    RecommendationResponse,
    UserPreferences,
)
from app.services.fallback import FallbackPolicy
from app.services.groq_client import GroqLlmClient
from app.services.integration import FilterService, IntegrationService
from app.services.merger import Merger
from app.services.response_parser import RankedOutput, ResponseParser


class RecommendationService:
    def __init__(self, repository: RestaurantRepository) -> None:
        self._repo = repository
        self._settings = get_settings()
        self._filter = FilterService(repository)
        self._integration = IntegrationService()
        self._llm = GroqLlmClient(self._settings)

    def recommend(self, prefs: UserPreferences, *, top_k: int = 5) -> RecommendationResponse:
        start = time.perf_counter()

        candidates = self._filter.filter(prefs)
        candidates = candidates[: max(1, self._settings.max_candidates)]

        if not candidates:
            raise IntegrationError("No candidates found for the given preferences.")

        llm_request = self._integration.build_llm_request(
            prefs=prefs,
            candidates=candidates,
            model=self._settings.llm_model,
        )

        allowed_ids = set(llm_request.allowed_restaurant_ids)
        schema_hint = {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "restaurant_id": {"type": "string"},
                            "explanation": {"type": "string"},
                        },
                        "required": ["restaurant_id", "explanation"],
                    },
                },
            },
            "required": ["items"],
        }

        try:
            raw = self._llm.complete_typed(
                messages=llm_request.messages,
                model=llm_request.model_params["model"],
                temperature=float(llm_request.model_params.get("temperature", 0.2)),
            ).content

            try:
                ranked: RankedOutput = ResponseParser.parse(raw)
            except IntegrationError:
                # Retry once with a repair prompt.
                repair_messages = ResponseParser.build_repair_messages(raw, schema_hint)
                raw2 = self._llm.complete_typed(
                    messages=repair_messages,
                    model=llm_request.model_params["model"],
                    temperature=0.0,
                ).content
                ranked = ResponseParser.parse(raw2)

            items, summary = Merger.merge(
                candidates=candidates,
                ranked=ranked,
                allowed_ids=allowed_ids,
                top_k=top_k,
            )
        except (ExternalProviderError, IntegrationError):
            # Provider outage / parse failure / validation failure → fallback.
            items, summary = FallbackPolicy.heuristic_top_n(candidates, top_k=top_k)

        latency_ms = int((time.perf_counter() - start) * 1000)
        meta = RecommendationMeta(
            model=self._settings.llm_model,
            latency_ms=latency_ms,
            dataset_version=self._settings.dataset_version,
        )
        return RecommendationResponse(recommendations=items, summary=summary, meta=meta)

