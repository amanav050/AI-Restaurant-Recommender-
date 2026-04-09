from __future__ import annotations

from app.domain.models import RecommendationItem, Restaurant


class FallbackPolicy:
    @staticmethod
    def heuristic_top_n(
        candidates: list[Restaurant],
        *,
        top_k: int,
    ) -> tuple[list[RecommendationItem], str]:
        # Simple heuristic: prefer higher rating; missing rating sorts last.
        def key(r: Restaurant) -> tuple[int, float]:
            if r.rating is None:
                return (1, 0.0)
            return (0, float(r.rating))

        ranked = sorted(candidates, key=key, reverse=True)[:top_k]
        items: list[RecommendationItem] = []
        for idx, r in enumerate(ranked, start=1):
            items.append(
                RecommendationItem(
                    restaurant_id=r.id,
                    name=r.name,
                    cuisines=r.cuisines,
                    rating=r.rating,
                    estimated_cost=r.estimated_cost or r.cost_band,
                    explanation="Selected using a non-LLM fallback ranking (rating-first).",
                    rank=idx,
                )
            )
        return items, "Recommendations generated using fallback ranking due to an LLM issue."

