from dataclasses import dataclass
from typing import Any


@dataclass
class AppError(Exception):
    message: str
    code: str = "APP_ERROR"
    details: dict[str, Any] | None = None


class IntegrationError(AppError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="INTEGRATION_ERROR", details=details)


class ExternalProviderError(AppError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="EXTERNAL_PROVIDER_ERROR", details=details)
