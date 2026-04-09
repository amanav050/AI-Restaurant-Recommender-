from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from app.data.repository import FilterCriteria, RestaurantRepository
from app.domain.models import Restaurant, UserPreferences


@dataclass
class LlmRequest:
    messages: list[dict[str, Any]]
    allowed_restaurant_ids: list[str]
    model_params: dict[str, Any]


class FilterService:
    """Deterministic filter over RestaurantRepository based on UserPreferences.

    This is a minimal Phase 3 stub; the full scoring and candidate selection
    strategy can be fleshed out when implementing the complete integration layer.
    """

    def __init__(self, repository: RestaurantRepository) -> None:
        self._repository = repository

    def filter(self, prefs: UserPreferences) -> list[Restaurant]:
        criteria = FilterCriteria(
            city=prefs.location, 
            min_rating=float(prefs.min_rating),
            cuisines=prefs.cuisines
        )
        return self._repository.filter(criteria)


class IntegrationService:
    """Builds an LlmRequest from preferences and filtered candidates.

    This keeps the surface aligned with the architecture doc while allowing
    the concrete Groq prompt/parameters to be added in Phase 4.
    """

    def build_llm_request(
        self,
        prefs: UserPreferences,
        candidates: list[Restaurant],
        model: str,
    ) -> LlmRequest:
        allowed_ids = [r.id for r in candidates]
        candidate_payload = [
            {
                "restaurant_id": r.id,
                "name": r.name,
                "location": r.location,
                "cuisines": r.cuisines,
                "cost_band": r.cost_band,
                "estimated_cost": r.estimated_cost,
                "rating": r.rating,
                "tags": r.tags,
            }
            for r in candidates
        ]
        user_payload = {
            "location": prefs.location,
            "budget": prefs.budget,
            "cuisines": prefs.cuisines,
            "min_rating": prefs.min_rating,
            "additional_preferences": prefs.additional_preferences,
        }
        schema = {
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
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are a restaurant recommendation assistant.\n"
                    "You MUST ONLY recommend restaurants from the provided candidate list.\n"
                    "For each recommended restaurant, provide a highly specific, unique explanation "
                    "that mentions:\n"
                    "- The restaurant's actual cuisine types from the dataset\n"
                    "- Specific cost information (estimated cost or cost band)\n"
                    "- The actual rating if available\n"
                    "- Why it matches the user's preferences\n"
                    "Make each explanation different and specific to that restaurant. "
                    "Avoid generic phrases like 'good food' or 'nice place'.\n"
                    "Return ONLY valid JSON that matches the requested schema.\n"
                    "Do not include markdown fences. Do not invent any restaurants."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "user_preferences": user_payload,
                        "candidates": candidate_payload,
                        "output_schema": schema,
                        "top_k": 5,
                    },
                    ensure_ascii=False,
                ),
            },
        ]
        model_params = {"model": model, "temperature": 0.2}
        return LlmRequest(
            messages=messages,
            allowed_restaurant_ids=allowed_ids,
            model_params=model_params,
        )

