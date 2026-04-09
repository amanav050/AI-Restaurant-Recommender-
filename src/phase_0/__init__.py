"""Phase 0: Foundations and cross-cutting concerns.

This package exposes the core Phase 0 building blocks so they can be imported
directly from a phase-oriented namespace, without changing the main `app` layout.
"""

from app.core.config import Settings, get_settings
from app.core.errors import AppError, ExternalProviderError, IntegrationError
from app.core.logging import configure_logging
from app.domain.models import (
    RecommendationItem,
    RecommendationMeta,
    RecommendationResponse,
    Restaurant,
    UserPreferences,
)

__all__ = [
    "Settings",
    "get_settings",
    "AppError",
    "ExternalProviderError",
    "IntegrationError",
    "configure_logging",
    "Restaurant",
    "UserPreferences",
    "RecommendationItem",
    "RecommendationMeta",
    "RecommendationResponse",
]

