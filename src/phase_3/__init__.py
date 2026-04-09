"""Phase 3: Integration layer (filter, context pack, prompt design).

This package surfaces the Phase 3 integration stubs under a phase-specific
namespace so they can be evolved independently of earlier phases.
"""

from app.services.integration import FilterService, IntegrationService, LlmRequest

__all__ = [
    "FilterService",
    "IntegrationService",
    "LlmRequest",
]

