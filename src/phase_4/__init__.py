"""Phase 4: Recommendation engine (Groq LLM).

Exports the Phase 4 backend components under a phase-specific namespace.
"""

from app.services.fallback import FallbackPolicy
from app.services.groq_client import GroqLlmClient
from app.services.llm_client import LlmClient, LlmResult
from app.services.merger import Merger
from app.services.recommendation import RecommendationService
from app.services.response_parser import RankedItem, RankedOutput, ResponseParser

__all__ = [
    "LlmClient",
    "LlmResult",
    "GroqLlmClient",
    "ResponseParser",
    "RankedItem",
    "RankedOutput",
    "Merger",
    "FallbackPolicy",
    "RecommendationService",
]

