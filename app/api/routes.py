from fastapi import APIRouter

from app.api.schemas import HealthResponse, PreferenceRequest, PreferenceResponse
from app.api.recommendations import router as recommendations_router
from app.core.config import get_settings

router = APIRouter(tags=["system"])
router.include_router(recommendations_router)


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", app=settings.app_name, environment=settings.environment)


@router.post("/preferences", response_model=PreferenceResponse, tags=["preferences"])
def create_preferences(payload: PreferenceRequest) -> PreferenceResponse:
    """Validate and normalize raw user preference input into UserPreferences."""
    domain = payload.to_domain()
    return PreferenceResponse(preferences=domain)
