from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter

from app.api.schemas import RecommendationRequest
from app.data.repository import RestaurantRepository
from app.domain.models import RecommendationResponse
from app.services.recommendation import RecommendationService

router = APIRouter(tags=["recommendations"])


@lru_cache(maxsize=1)
def _repo() -> RestaurantRepository:
    return RestaurantRepository.from_parquet()


@lru_cache(maxsize=1)
def _svc() -> RecommendationService:
    return RecommendationService(_repo())


@router.post("/recommendations", response_model=RecommendationResponse)
def recommendations(payload: RecommendationRequest) -> RecommendationResponse:
    prefs = payload.to_domain()
    return _svc().recommend(prefs, top_k=payload.top_k)

@router.get("/cuisines", response_model=list[str])
def get_cuisines() -> list[str]:
    return _repo().get_unique_cuisines()

@router.get("/localities", response_model=list[str])
def get_localities() -> list[str]:
    return _repo().get_unique_localities()

