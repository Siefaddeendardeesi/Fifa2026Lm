"""Tests for src.utils.exceptions."""

from __future__ import annotations

from src.utils.exceptions import (
    APIError,
    DataValidationError,
    ETLDownloadError,
    FifaPlatformError,
    ModelNotFoundError,
    NotFoundError,
    RateLimitError,
    RetryableError,
)


def test_fifa_platform_error_details() -> None:
    err = FifaPlatformError("msg", details={"k": 1})
    assert err.message == "msg"
    assert err.details == {"k": 1}


def test_data_validation_inherits_validation() -> None:
    err = DataValidationError("bad data")
    assert isinstance(err, FifaPlatformError)


def test_etl_download_is_retryable() -> None:
    assert isinstance(ETLDownloadError("x"), RetryableError)


def test_not_found_status_code() -> None:
    err = NotFoundError("missing")
    assert err.status_code == 404


def test_rate_limit_status_code() -> None:
    err = RateLimitError()
    assert err.status_code == 429


def test_api_error_default_status() -> None:
    err = APIError("fail")
    assert err.status_code == 500


def test_model_not_found() -> None:
    err = ModelNotFoundError("no model")
    assert str(err) == "no model"
