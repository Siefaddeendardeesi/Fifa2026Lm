"""Tests for src.utils.logging."""

from __future__ import annotations

from src.utils.logging import configure_logging, get_logger


def test_configure_logging_runs(test_settings) -> None:
    configure_logging()
    logger = get_logger("test.module")
    logger.info("test_event", key="value")


def test_get_logger_returns_bound_logger() -> None:
    logger = get_logger(__name__)
    assert hasattr(logger, "info")
