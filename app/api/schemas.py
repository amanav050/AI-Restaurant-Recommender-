from pydantic import BaseModel, Field, field_validator

from app.domain.models import BudgetBand, UserPreferences


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str


class PreferenceRequest(BaseModel):
    location: str = Field(..., min_length=1)
    budget: BudgetBand
    cuisine: list[str] = Field(default_factory=list)
    min_rating: float = Field(0, ge=0, le=5)
    additional_preferences: str | None = Field(default=None, max_length=500)

    @field_validator("cuisine", mode="before")
    @classmethod
    def normalize_cuisine(cls, value: str | list[str] | None) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        return [c.strip() for c in value if c.strip()]

    def to_domain(self) -> UserPreferences:
        return UserPreferences(
            location=self.location.strip(),
            budget=self.budget,
            cuisines=list(dict.fromkeys(self.cuisine)),
            min_rating=self.min_rating,
            additional_preferences=self.additional_preferences,
        )


class PreferenceResponse(BaseModel):
    preferences: UserPreferences


class RecommendationRequest(PreferenceRequest):
    top_k: int = Field(5, ge=1, le=10)
