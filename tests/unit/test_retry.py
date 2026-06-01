"""Tests for src.utils.retry."""

from __future__ import annotations

import pytest

from src.utils.exceptions import RetryableError
from src.utils.retry import with_retry


def test_with_retry_succeeds_after_transient_failure(test_settings) -> None:
    calls = {"n": 0}

    @with_retry
    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 2:
            raise RetryableError("transient")
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 2


def test_with_retry_reraises_after_max_attempts(test_settings) -> None:
    @with_retry
    def always_fail() -> None:
        raise RetryableError("still failing")

    with pytest.raises(RetryableError):
        always_fail()
