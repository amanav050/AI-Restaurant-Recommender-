from typing import Literal

from pydantic import BaseModel, Field, confloat

BudgetBand = Literal["low", "medium", "high"]


class Restaurant(BaseModel):
    id: str
    name: str
    location: str
    cuisines: list[str] = Field(default_factory=list)
    cost_band: BudgetBand | None = None
    estimated_cost: float | None = None
    rating: confloat(ge=0, le=5) | None = None
    tags: list[str] = Field(default_factory=list)


class UserPreferences(BaseModel):
    location: str
    budget: BudgetBand
    cuisines: list[str] = Field(default_factory=list)
    min_rating: confloat(ge=0, le=5) = 0
    additional_preferences: str | None = None


class RecommendationItem(BaseModel):
    restaurant_id: str
    name: str
    cuisines: list[str] = Field(default_factory=list)
    rating: confloat(ge=0, le=5) | None = None
    estimated_cost: str | float | None = None
    explanation: str
    rank: int | None = None
    score: float | None = None


class RecommendationMeta(BaseModel):
    model: str
    latency_ms: int
    dataset_version: str


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    summary: str | None = None
    meta: RecommendationMeta
