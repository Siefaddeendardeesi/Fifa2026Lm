"""Tests for src.models.base."""

from __future__ import annotations

import pytest

from src.models.base import MODEL_REGISTRY, LogisticRegressionModel, get_model


def test_get_model_known_types() -> None:
    for name in ("logistic_regression", "random_forest", "xgboost"):
        model = get_model(name)
        assert model.name == name


def test_get_model_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown model type"):
        get_model("invalid_model")


def test_prepare_xy(features_df) -> None:
    impl = LogisticRegressionModel()
    x, y = impl.prepare_xy(features_df.head(100))
    assert len(x) == len(y)
    assert set(y).issubset({0, 1, 2})


def test_build_pipeline_random_forest(features_df) -> None:
    from src.models.base import RandomForestModel

    impl = RandomForestModel()
    x, y = impl.prepare_xy(features_df.head(50))
    pipe = impl.build_pipeline(list(x.columns))
    pipe.fit(x, y)
    preds = pipe.predict(x)
    assert len(preds) == len(y)


def test_model_registry_complete() -> None:
    assert len(MODEL_REGISTRY) == 5
