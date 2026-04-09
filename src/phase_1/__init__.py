"""Phase 1: Data ingestion and preprocessing.

This package surfaces the ingestion pipeline and repository under a
phase-specific namespace.
"""

from app.data.ingestion import (
    HF_DATASET_NAME,
    DatasetLoader,
    RawRestaurant,
    ingest_to_parquet,
    normalize,
)
from app.data.repository import FilterCriteria, RestaurantRepository

__all__ = [
    "HF_DATASET_NAME",
    "DatasetLoader",
    "RawRestaurant",
    "normalize",
    "ingest_to_parquet",
    "FilterCriteria",
    "RestaurantRepository",
]

