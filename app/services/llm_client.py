from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class LlmResult:
    content: str


class LlmClient(Protocol):
    """Phase 4 contract for an LLM client (Groq implementation in groq_client.py)."""

    def complete(
        self,
        *,
        messages: list[dict[str, Any]],
        model: str,
        temperature: float,
    ) -> LlmResult: ...

