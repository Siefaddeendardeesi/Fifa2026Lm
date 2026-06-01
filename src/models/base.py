"""Base model interface and concrete implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.config.constants import CATEGORICAL_COLS, FEATURE_COLS, NUMERIC_COLS, TARGET_LABELS


class BaseModel(ABC):
    """Unified interface for match outcome classifiers."""

    name: str = "base"

    @abstractmethod
    def build_pipeline(self, feature_cols: list[str]) -> Pipeline:
        """Build sklearn pipeline with preprocessor and classifier."""

    @abstractmethod
    def get_default_params(self) -> dict[str, Any]:
        """Return default hyperparameters."""

    def prepare_xy(self, df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
        """Extract features X and encoded target y."""
        available = [c for c in FEATURE_COLS if c in df.columns]
        x = df[available].copy()

        for col in NUMERIC_COLS:
            if col in x.columns and x[col].isna().all():
                x = x.drop(columns=[col])

        for col in CATEGORICAL_COLS:
            if col in x.columns:
                x[col] = x[col].astype(str)

        y = df["result"].map(TARGET_LABELS)
        mask = y.notna()
        return x[mask], y[mask].astype(int).values

    def _build_preprocessor(self, feature_cols: list[str]) -> ColumnTransformer:
        numeric_cols = [c for c in NUMERIC_COLS if c in feature_cols]
        categorical_cols = [c for c in CATEGORICAL_COLS if c in feature_cols]
        return ColumnTransformer(
            transformers=[
                ("num", SimpleImputer(strategy="median"), numeric_cols),
                (
                    "cat",
                    Pipeline(
                        steps=[
                            ("imputer", SimpleImputer(strategy="most_frequent")),
                            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                        ]
                    ),
                    categorical_cols,
                ),
            ],
            remainder="drop",
        )


class LogisticRegressionModel(BaseModel):
    name = "logistic_regression"

    def get_default_params(self) -> dict[str, Any]:
        return {"C": 1.0, "max_iter": 1000, "random_state": 42}

    def build_pipeline(self, feature_cols: list[str]) -> Pipeline:
        params = self.get_default_params()
        return Pipeline(
            steps=[
                ("preprocessor", self._build_preprocessor(feature_cols)),
                (
                    "classifier",
                    LogisticRegression(
                        solver="lbfgs",
                        n_jobs=-1,
                        **params,
                    ),
                ),
            ]
        )


class RandomForestModel(BaseModel):
    name = "random_forest"

    def get_default_params(self) -> dict[str, Any]:
        return {"n_estimators": 200, "max_depth": 12, "random_state": 42, "n_jobs": -1}

    def build_pipeline(self, feature_cols: list[str]) -> Pipeline:
        from sklearn.ensemble import RandomForestClassifier

        return Pipeline(
            steps=[
                ("preprocessor", self._build_preprocessor(feature_cols)),
                ("classifier", RandomForestClassifier(**self.get_default_params())),
            ]
        )


class XGBoostModel(BaseModel):
    name = "xgboost"

    def get_default_params(self) -> dict[str, Any]:
        return {
            "objective": "multi:softprob",
            "num_class": 3,
            "n_estimators": 200,
            "max_depth": 6,
            "learning_rate": 0.1,
            "random_state": 42,
            "n_jobs": -1,
            "eval_metric": "mlogloss",
        }

    def build_pipeline(self, feature_cols: list[str]) -> Pipeline:
        from xgboost import XGBClassifier

        return Pipeline(
            steps=[
                ("preprocessor", self._build_preprocessor(feature_cols)),
                ("classifier", XGBClassifier(**self.get_default_params())),
            ]
        )


class LightGBMModel(BaseModel):
    name = "lightgbm"

    def get_default_params(self) -> dict[str, Any]:
        return {
            "objective": "multiclass",
            "num_class": 3,
            "n_estimators": 200,
            "max_depth": 6,
            "learning_rate": 0.1,
            "random_state": 42,
            "n_jobs": -1,
            "verbose": -1,
        }

    def build_pipeline(self, feature_cols: list[str]) -> Pipeline:
        from lightgbm import LGBMClassifier

        return Pipeline(
            steps=[
                ("preprocessor", self._build_preprocessor(feature_cols)),
                ("classifier", LGBMClassifier(**self.get_default_params())),
            ]
        )


class CatBoostModel(BaseModel):
    name = "catboost"

    def get_default_params(self) -> dict[str, Any]:
        return {
            "loss_function": "MultiClass",
            "iterations": 200,
            "depth": 6,
            "learning_rate": 0.1,
            "random_seed": 42,
            "verbose": False,
        }

    def build_pipeline(self, feature_cols: list[str]) -> Pipeline:
        from catboost import CatBoostClassifier

        return Pipeline(
            steps=[
                ("preprocessor", self._build_preprocessor(feature_cols)),
                ("classifier", CatBoostClassifier(**self.get_default_params())),
            ]
        )


MODEL_REGISTRY: dict[str, type[BaseModel]] = {
    "logistic_regression": LogisticRegressionModel,
    "random_forest": RandomForestModel,
    "xgboost": XGBoostModel,
    "lightgbm": LightGBMModel,
    "catboost": CatBoostModel,
}


def get_model(model_type: str) -> BaseModel:
    """Factory for model instances."""
    if model_type not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model type: {model_type}. Available: {list(MODEL_REGISTRY)}")
    return MODEL_REGISTRY[model_type]()
