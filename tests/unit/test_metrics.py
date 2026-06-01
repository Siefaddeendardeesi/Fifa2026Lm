"""Tests for monitoring.metrics."""

from __future__ import annotations

import pytest

from monitoring.metrics import get_metrics, track_prediction


def test_get_metrics_returns_bytes() -> None:
    data = get_metrics()
    assert isinstance(data, bytes)
    assert b"fifa_" in data or len(data) > 0


def test_track_prediction_decorator_success() -> None:
    @track_prediction
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3


def test_track_prediction_decorator_reraises() -> None:
    @track_prediction
    def fail() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError):
        fail()
