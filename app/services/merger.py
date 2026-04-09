from __future__ import annotations

from app.core.errors import IntegrationError
from app.domain.models import RecommendationItem, Restaurant
from app.services.response_parser import RankedOutput


class Merger:
    @staticmethod
    def merge(
        *,
        candidates: list[Restaurant],
        ranked: RankedOutput,
        allowed_ids: set[str],
        top_k: int,
    ) -> tuple[list[RecommendationItem], str | None]:
        by_id = {r.id: r for r in candidates}
        items: list[RecommendationItem] = []
        seen: set[str] = set()

        for idx, it in enumerate(ranked.items[:top_k], start=1):
            rid = it.restaurant_id
            if rid not in allowed_ids or rid in seen:
                continue
            seen.add(rid)
            r = by_id[rid]
            items.append(
                RecommendationItem(
                    restaurant_id=r.id,
                    name=r.name,
                    cuisines=r.cuisines,
                    rating=r.rating,
                    estimated_cost=r.estimated_cost or r.cost_band,
                    explanation=it.explanation.strip(),
                    rank=idx,
                )
            )

        if not items:
            raise IntegrationError("LLM returned no valid restaurant_ids from the candidate list.")

        return items, ranked.summary

