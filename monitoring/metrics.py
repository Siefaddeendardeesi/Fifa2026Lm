"""Prometheus metrics for API and ML operations."""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

from prometheus_client import Counter, Gauge, Histogram, generate_latest

T = TypeVar("T")

PREDICTION_LATENCY = Histogram(
    "fifa_prediction_latency_seconds",
    "Prediction request latency",
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
PREDICTION_COUNT = Counter("fifa_predictions_total", "Total predictions", ["status"])
SIMULATION_DURATION = Histogram(
    "fifa_simulation_duration_seconds",
    "Simulation duration",
    buckets=(1, 5, 10, 30, 60, 120, 300),
)
API_ERRORS = Counter("fifa_api_errors_total", "API errors", ["endpoint", "error_type"])
MODEL_CONFIDENCE = Gauge("fifa_model_confidence", "Last prediction confidence")
SIMULATION_RUNS = Counter("fifa_simulations_total", "Total simulations run")


def track_prediction(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args: object, **kwargs: object) -> T:
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            PREDICTION_COUNT.labels(status="success").inc()
            return result
        except Exception:
            PREDICTION_COUNT.labels(status="error").inc()
            raise
        finally:
            PREDICTION_LATENCY.observe(time.perf_counter() - start)

    return wrapper


def get_metrics() -> bytes:
    return generate_latest()
