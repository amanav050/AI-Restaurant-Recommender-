"""Phase 2: User input collection and validation.

This package exposes the preference request/response schemas and the
`UserPreferences` domain model under a phase-specific namespace.
"""

from app.api.schemas import PreferenceRequest, PreferenceResponse
from app.domain.models import UserPreferences

__all__ = [
    "PreferenceRequest",
    "PreferenceResponse",
    "UserPreferences",
]

