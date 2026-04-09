from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from groq import Groq

from app.core.config import Settings
from app.core.errors import ExternalProviderError
from app.services.llm_client import LlmResult


@dataclass
class GroqChatResult:
    content: str


class GroqLlmClient:
    def __init__(self, settings: Settings) -> None:
        api_key = settings.effective_llm_api_key
        if not api_key:
            raise ExternalProviderError(
                "Missing Groq API key. Set GROQ_API_KEY (preferred) or LLM_API_KEY in .env."
            )
        self._client = Groq(api_key=api_key)
        self._timeout = settings.llm_timeout_seconds

    def complete(
        self,
        *,
        messages: list[dict[str, Any]],
        model: str,
        temperature: float = 0.2,
    ) -> GroqChatResult:
        try:
            resp = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                timeout=self._timeout,
            )
        except Exception as e:  # noqa: BLE001
            raise ExternalProviderError("Groq request failed.", details={"error": str(e)}) from e

        content = resp.choices[0].message.content if resp.choices else ""
        return GroqChatResult(content=content or "")

    def complete_typed(
        self,
        *,
        messages: list[dict[str, Any]],
        model: str,
        temperature: float = 0.2,
    ) -> LlmResult:
        res = self.complete(messages=messages, model=model, temperature=temperature)
        return LlmResult(content=res.content)

