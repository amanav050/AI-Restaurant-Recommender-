from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import pandas as pd

from app.core.config import get_settings
from app.domain.models import Restaurant


@dataclass
class FilterCriteria:
    city: str
    min_rating: float = 0.0
    cuisines: list[str] | None = None


class RestaurantRepository:
    """Data-centric access to normalized restaurant records."""

    def __init__(self, restaurants: Iterable[Restaurant]) -> None:
        self._items: list[Restaurant] = list(restaurants)

    @classmethod
    def from_parquet(cls) -> RestaurantRepository:
        settings = get_settings()
        df = pd.read_parquet(settings.dataset_path)
        records = df.to_dict("records")
        cleaned: list[dict] = []
        for row in records:
            # Pandas uses NaN for missing values; convert to None for Pydantic.
            for key in ("cost_band", "estimated_cost", "rating"):
                if key in row and pd.isna(row[key]):
                    row[key] = None
            cleaned.append(row)

        restaurants: list[Restaurant] = [Restaurant.model_validate(row) for row in cleaned]
        return cls(restaurants)

    def load_all(self) -> list[Restaurant]:
        return list(self._items)

    def get_by_id(self, restaurant_id: str) -> Restaurant | None:
        for r in self._items:
            if r.id == restaurant_id:
                return r
        return None

    def get_unique_cuisines(self) -> list[str]:
        cuisines = set()
        for r in self._items:
            for c in r.cuisines:
                if c and c.strip():
                    cuisines.add(c.strip())
        return sorted(list(cuisines))

    def get_unique_localities(self) -> list[str]:
        localities = set()
        for r in self._items:
            if r.location and r.location.strip():
                localities.add(r.location.strip())
        return sorted(list(localities))

    def filter(self, criteria: FilterCriteria) -> list[Restaurant]:
        query = criteria.city.lower().strip()
        min_rating = criteria.min_rating
        filtered: list[Restaurant] = []
        for r in self._items:
            if query:
                # Dataset locations are typically neighborhood/locality strings
                # (e.g., "BTM", "HSR").
                loc = r.location.lower().strip()
                if query not in loc and loc not in query:
                    continue
            if r.rating is not None and r.rating < min_rating:
                continue
            if criteria.cuisines:
                req_cuisines = {c.lower().strip() for c in criteria.cuisines if c.strip()}
                rest_cuisines = {c.lower().strip() for c in r.cuisines if c.strip()}
                if req_cuisines and not req_cuisines.intersection(rest_cuisines):
                    continue
            filtered.append(r)
        return filtered

