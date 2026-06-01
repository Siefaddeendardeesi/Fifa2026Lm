"""Tests for src.models.evaluation."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from src.models.base import RandomForestModel
from src.models.evaluation import EvaluationReport, compute_metrics, generate_evaluation_report


def test_compute_metrics() -> None:
    y_true = np.array([0, 1, 2, 0])
    y_pred = np.array([0, 1, 2, 1])
    y_proba = np.array(
        [
            [0.8, 0.1, 0.1],
            [0.1, 0.7, 0.2],
            [0.1, 0.2, 0.7],
            [0.4, 0.4, 0.2],
        ]
    )
    metrics = compute_metrics(y_true, y_pred, y_proba)
    assert "accuracy" in metrics
    assert "f1_macro" in metrics
    assert 0 <= metrics["accuracy"] <= 1


def test_evaluation_report_save(train_test_frames, tmp_path: Path) -> None:
    train, test = train_test_frames
    impl = RandomForestModel()
    x_train, y_train = impl.prepare_xy(train)
    x_test, y_test = impl.prepare_xy(test)
    pipe = impl.build_pipeline(list(x_train.columns))
    pipe.fit(x_train, y_train)
    y_pred = pipe.predict(x_test)
    y_proba = pipe.predict_proba(x_test)

    report = generate_evaluation_report(y_test, y_pred, y_proba, pipe, x_test)
    assert report.metrics
    assert report.confusion_matrix
    assert "confusion_matrix" in report.plots

    html_path = tmp_path / "report.html"
    json_path = tmp_path / "report.json"
    report.save_html(html_path)
    report.save_json(json_path)
    assert html_path.exists()
    assert json_path.exists()


def test_evaluation_report_to_dict() -> None:
    r = EvaluationReport(metrics={"accuracy": 0.9})
    assert r.to_dict()["metrics"]["accuracy"] == 0.9
