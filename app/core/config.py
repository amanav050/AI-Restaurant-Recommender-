import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _load_env_file_robust(path: str = ".env") -> None:
    """Load KEY=VALUE pairs into os.environ.

    On Windows, `.env` is sometimes saved as UTF-16; some dotenv loaders won't read it.
    This loader detects common BOMs and falls back to UTF-8.
    """
    p = Path(path)
    if not p.exists():
        return

    raw = p.read_bytes()
    encoding = "utf-8"
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        encoding = "utf-16"
    elif raw.startswith(b"\xef\xbb\xbf"):
        encoding = "utf-8-sig"

    text = raw.decode(encoding, errors="replace")
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if "=" not in s:
            continue
        k, v = s.split("=", 1)
        key = k.strip()
        value = v.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_env_file_robust(".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Restaurant Recommender"
    environment: Literal["development", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    api_prefix: str = "/api/v1"

    dataset_path: str = "./data/zomato.parquet"
    dataset_version: str = "unknown"

    llm_provider: Literal["groq"] = "groq"
    llm_model: str = "llama-3.1-8b-instant"
    # Supports both names for convenience; prefer GROQ_API_KEY.
    groq_api_key: str = Field(default="", validation_alias="GROQ_API_KEY", repr=False)
    llm_api_key: str = Field(default="", validation_alias="LLM_API_KEY", repr=False)
    llm_timeout_seconds: int = 20
    llm_max_retries: int = 2
    max_candidates: int = 30

    @property
    def effective_llm_api_key(self) -> str:
        return self.groq_api_key or self.llm_api_key


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
