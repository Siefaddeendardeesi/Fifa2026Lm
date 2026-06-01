"""Retry utilities with exponential backoff."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.config.settings import get_settings
from src.utils.exceptions import RetryableError

T = TypeVar("T")


def with_retry[T](
    func: Callable[..., T],
    *,
    max_attempts: int | None = None,
    backoff: float | None = None,
) -> Callable[..., T]:
    """Wrap a callable with tenacity retry on RetryableError."""
    settings = get_settings()
    attempts = max_attempts or settings.etl_max_retries
    wait_base = backoff or settings.etl_retry_backoff

    @retry(
        retry=retry_if_exception_type(RetryableError),
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=wait_base, min=1, max=60),
        reraise=True,
    )
    def wrapper(*args: object, **kwargs: object) -> T:
        return func(*args, **kwargs)

    return wrapper
