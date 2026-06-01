"""Tests for src.models.tuning."""

from __future__ import annotations

from src.models.tuning import SEARCH_SPACES, HyperparameterTuner


def test_search_spaces_defined() -> None:
    assert "xgboost" in SEARCH_SPACES
    assert "logistic_regression" in SEARCH_SPACES


def test_hyperparameter_tuner_random_forest(features_df, test_settings) -> None:
    train = features_df[features_df["date"] < "2022-01-01"].tail(800)
    tuner = HyperparameterTuner(model_type="random_forest", n_trials=3)
    result = tuner.tune(train, n_folds=2)
    assert "best_params" in result
    assert result["n_trials"] >= 1
