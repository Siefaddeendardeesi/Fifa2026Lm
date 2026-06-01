"""Centralized exception hierarchy."""

from __future__ import annotations


class FifaPlatformError(Exception):
    """Base exception for the platform."""

    def __init__(self, message: str, *, details: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(FifaPlatformError):
    """Data or input validation failure."""


class DataValidationError(ValidationError):
    """Schema or business rule validation failure on datasets."""


class ConfigurationError(FifaPlatformError):
    """Invalid or missing configuration."""


class RetryableError(FifaPlatformError):
    """Transient failure that may succeed on retry."""


class ETLDownloadError(RetryableError):
    """Failed to download data from external source."""


class ETLProcessingError(FifaPlatformError):
    """ETL transformation or merge failure."""


class ModelNotFoundError(FifaPlatformError):
    """Requested model artifact does not exist."""


class ModelTrainingError(FifaPlatformError):
    """Model training pipeline failure."""


class SimulationError(FifaPlatformError):
    """Tournament simulation failure."""


class RankingError(FifaPlatformError):
    """Team ranking computation failure."""


class APIError(FifaPlatformError):
    """API layer error."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 500,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message, details=details)
        self.status_code = status_code


class NotFoundError(APIError):
    """Resource not found."""

    def __init__(self, message: str, *, details: dict[str, object] | None = None) -> None:
        super().__init__(message, status_code=404, details=details)


class RateLimitError(APIError):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, status_code=429)
