from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.core.errors import IntegrationError


class RankedItem(BaseModel):
    restaurant_id: str
    explanation: str = Field(min_length=1)


class RankedOutput(BaseModel):
    items: list[RankedItem]
    summary: str | None = None


class ResponseParser:
    @staticmethod
    def extract_json(text: str) -> str:
        s = text.strip()
        if s.startswith("```"):
            # Drop markdown fences if present.
            s = s.replace("```json", "").replace("```", "").strip()
        start = s.find("{")
        end = s.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise IntegrationError("LLM did not return JSON.")
        return s[start : end + 1]

    @classmethod
    def parse(cls, text: str) -> RankedOutput:
        try:
            payload = json.loads(cls.extract_json(text))
            return RankedOutput.model_validate(payload)
        except (json.JSONDecodeError, ValidationError) as e:
            raise IntegrationError(
                "Failed to parse LLM output as the expected JSON schema.",
                details={"error": str(e)},
            ) from e

    @staticmethod
    def build_repair_messages(raw_text: str, schema_hint: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "role": "system",
                "content": (
                    "Return ONLY valid JSON matching the provided schema. "
                    "No markdown fences. No extra keys."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {"invalid_output": raw_text, "output_schema": schema_hint},
                    ensure_ascii=False,
                ),
            },
        ]

