"""Tests for SHAP plot in evaluation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from src.models.evaluation import _plot_shap, generate_evaluation_report


def test_plot_shap_insufficient_samples() -> None:
    pipe = Pipeline(
        steps=[
            ("preprocessor", FunctionTransformer(lambda x: np.zeros((len(x), 2)))),
            ("classifier", DummyClassifier(strategy="prior")),
        ]
    )
    x = pd.DataFrame({"a": [1.0, 2.0]})
    y = np.array([0, 1])
    img = _plot_shap(pipe, x, y)
    assert isinstance(img, str)
    assert len(img) > 100


def test_generate_evaluation_includes_shap(train_test_frames) -> None:
    train, test = train_test_frames
    from src.models.base import LogisticRegressionModel

    impl = LogisticRegressionModel()
    x_train, y_train = impl.prepare_xy(train.head(200))
    x_test, y_test = impl.prepare_xy(test.head(50))
    pipe = impl.build_pipeline(list(x_train.columns))
    pipe.fit(x_train, y_train)
    y_pred = pipe.predict(x_test)
    y_proba = pipe.predict_proba(x_test)
    report = generate_evaluation_report(y_test, y_pred, y_proba, pipe, x_test)
    assert "shap" in report.plots
