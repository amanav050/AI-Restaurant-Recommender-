from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import pandas as pd
from datasets import Dataset, load_dataset

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.domain.models import BudgetBand, Restaurant

HF_DATASET_NAME = "ManikaSaini/zomato-restaurant-recommendation"


@dataclass
class RawRestaurant:
    """Thin wrapper over a raw HF row used for mapping/normalization."""

    data: Mapping[str, object]


class DatasetLoader:
    """Fetches the Zomato dataset from Hugging Face."""

    def __init__(self, dataset_name: str = HF_DATASET_NAME, split: str = "train") -> None:
        self._dataset_name = dataset_name
        self._split = split

    def load(self) -> Dataset:
        return load_dataset(self._dataset_name, split=self._split)


class SchemaMapper:
    """Maps HF columns to internal field names in a tolerant way."""

    NAME_CANDIDATES = ("name", "restaurant_name")
    LOCATION_CANDIDATES = ("location", "city", "locality")
    CUISINES_CANDIDATES = ("cuisines", "cuisine")
    COST_CANDIDATES = (
        "approx_cost(for two people)",
        "approx_cost_for_two",
        "average_cost_for_two",
        "cost",
    )
    RATING_CANDIDATES = ("rating", "aggregate_rating")
    TAG_CANDIDATES = ("establishment", "listed_in(type)", "listed_in(type)")

    def __init__(self, columns: Sequence[str]) -> None:
        self.columns = set(columns)

    def _pick(self, candidates: Sequence[str]) -> str | None:
        for key in candidates:
            if key in self.columns:
                return key
        return None

    def map_row(self, row: Mapping[str, object]) -> RawRestaurant:
        name_key = self._pick(self.NAME_CANDIDATES)
        location_key = self._pick(self.LOCATION_CANDIDATES)
        cuisines_key = self._pick(self.CUISINES_CANDIDATES)
        cost_key = self._pick(self.COST_CANDIDATES)
        rating_key = self._pick(self.RATING_CANDIDATES)
        tag_key = self._pick(self.TAG_CANDIDATES)

        mapped: dict[str, object] = {}
        if name_key:
            mapped["name"] = row.get(name_key, "")
        if location_key:
            mapped["location"] = row.get(location_key, "")
        if cuisines_key:
            mapped["cuisines_raw"] = row.get(cuisines_key, "")
        if cost_key:
            mapped["cost_raw"] = row.get(cost_key)
        if rating_key:
            mapped["rating_raw"] = row.get(rating_key)
        if tag_key:
            mapped["tags_raw"] = row.get(tag_key)

        return RawRestaurant(mapped)


def _parse_cost_to_band_and_value(raw_cost: object) -> tuple[BudgetBand | None, float | None]:
    if raw_cost is None:
        return None, None
    try:
        value = float(raw_cost)
    except (TypeError, ValueError):
        return None, None

    # Simple INR-based tiers; adjust if dataset has different semantics.
    if value <= 400:
        band: BudgetBand | None = "low"
    elif value <= 800:
        band = "medium"
    else:
        band = "high"
    return band, value


def _parse_rating(raw_rating: object) -> float | None:
    if raw_rating is None:
        return None
    try:
        value = float(raw_rating)
    except (TypeError, ValueError):
        return None
    if value < 0 or value > 5:
        return None
    return value


def _normalize_cuisines(raw: object) -> list[str]:
    if raw is None:
        return []
    text = str(raw)
    parts: list[str] = []
    for token in text.replace("/", ",").split(","):
        clean = token.strip()
        if clean:
            parts.append(clean)
    return parts


def _normalize_location(raw: object) -> str:
    if raw is None:
        return ""
    return str(raw).strip()


def _normalize_tags(raw: object) -> list[str]:
    if raw is None:
        return []
    text = str(raw)
    parts = [p.strip() for p in text.replace("/", ",").split(",") if p.strip()]
    return parts


def _stable_id(name: str, location: str) -> str:
    base = f"{name}|{location}".lower()
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()
    return digest[:12]


def normalize(raw: RawRestaurant) -> Restaurant:
    data = raw.data
    name = str(data.get("name", "") or "").strip()
    location = _normalize_location(data.get("location", ""))
    cuisines = _normalize_cuisines(data.get("cuisines_raw"))
    cost_band, estimated_cost = _parse_cost_to_band_and_value(data.get("cost_raw"))
    rating = _parse_rating(data.get("rating_raw"))
    tags = _normalize_tags(data.get("tags_raw"))
    restaurant_id = _stable_id(name=name, location=location)

    return Restaurant(
        id=restaurant_id,
        name=name,
        location=location,
        cuisines=cuisines,
        cost_band=cost_band,
        estimated_cost=estimated_cost,
        rating=rating,
        tags=tags,
    )


def ingest_to_parquet() -> list[Restaurant]:
    """End-to-end ingestion job: HF dataset -> normalized parquet cache.

    Returns the in-memory list of normalized Restaurant objects.
    """
    settings = get_settings()
    configure_logging(settings.log_level)

    ds = DatasetLoader().load()
    mapper = SchemaMapper(columns=list(ds.column_names))

    restaurants: list[Restaurant] = []
    for row in ds:
        raw = mapper.map_row(row)
        restaurant = normalize(raw)
        # Skip entries without a name or location.
        if restaurant.name and restaurant.location:
            restaurants.append(restaurant)

    if restaurants:
        df = pd.DataFrame([r.model_dump() for r in restaurants])
        df.to_parquet(settings.dataset_path, index=False)

    return restaurants


if __name__ == "__main__":
    ingest_to_parquet()
