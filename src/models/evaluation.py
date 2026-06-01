"""Model evaluation with HTML reports, SHAP, and calibration."""

from __future__ import annotations

import base64
import io
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from jinja2 import Template
from matplotlib.figure import Figure
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline

matplotlib.use("Agg")

from src.config.constants import LABEL_NAMES


@dataclass
class EvaluationReport:
    """Container for evaluation results."""

    metrics: dict[str, float] = field(default_factory=dict)
    confusion_matrix: list[list[int]] = field(default_factory=list)
    classification_report: dict[str, Any] = field(default_factory=dict)
    plots: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics": self.metrics,
            "confusion_matrix": self.confusion_matrix,
            "classification_report": self.classification_report,
        }

    def save_html(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        html = _render_html(self)
        path.write_text(html, encoding="utf-8")

    def save_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")


def generate_evaluation_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray,
    pipeline: Pipeline,
    x_test: Any,
) -> EvaluationReport:
    """Generate comprehensive evaluation report."""
    report = EvaluationReport()
    report.metrics = compute_metrics(y_true, y_pred, y_proba)
    report.confusion_matrix = confusion_matrix(y_true, y_pred).tolist()
    report.classification_report = classification_report(
        y_true, y_pred, target_names=LABEL_NAMES, output_dict=True
    )
    report.plots["confusion_matrix"] = _plot_confusion_matrix(y_true, y_pred)
    report.plots["calibration"] = _plot_calibration(y_true, y_proba)
    report.plots["feature_importance"] = _plot_feature_importance(pipeline)
    report.plots["shap"] = _plot_shap(pipeline, x_test, y_true)
    return report


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray,
) -> dict[str, float]:
    """Compute classification metrics."""
    metrics: dict[str, float] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "log_loss": float(log_loss(y_true, y_proba)),
    }
    try:
        metrics["roc_auc_ovr"] = float(
            roc_auc_score(y_true, y_proba, multi_class="ovr", average="macro")
        )
    except ValueError:
        metrics["roc_auc_ovr"] = 0.0
    return metrics


def _fig_to_base64(fig: Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> str:
    fig, ax = plt.subplots(figsize=(6, 5))
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=LABEL_NAMES,
        yticklabels=LABEL_NAMES,
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix")
    return _fig_to_base64(fig)


def _plot_calibration(y_true: np.ndarray, y_proba: np.ndarray) -> str:
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for i, label in enumerate(LABEL_NAMES):
        y_binary = (y_true == i).astype(int)
        if y_binary.sum() == 0:
            continue
        prob_true, prob_pred = calibration_curve(y_binary, y_proba[:, i], n_bins=10)
        axes[i].plot(prob_pred, prob_true, marker="o")
        axes[i].plot([0, 1], [0, 1], linestyle="--", color="gray")
        axes[i].set_title(label)
        axes[i].set_xlabel("Predicted probability")
        axes[i].set_ylabel("True probability")
    fig.suptitle("Calibration Curves")
    fig.tight_layout()
    return _fig_to_base64(fig)


def _plot_shap(pipeline: Pipeline, x_test: Any, y_true: np.ndarray) -> str:
    """Generate SHAP summary plot when sample size permits."""
    fig, ax = plt.subplots(figsize=(8, 6))
    try:
        import shap

        if len(y_true) < 10:
            ax.text(0.5, 0.5, "Insufficient samples for SHAP", ha="center", va="center")
            ax.set_axis_off()
            return _fig_to_base64(fig)

        sample = x_test.head(100) if hasattr(x_test, "head") else x_test[:100]
        transformed = pipeline.named_steps["preprocessor"].transform(sample)
        classifier = pipeline.named_steps["classifier"]
        explainer = shap.Explainer(classifier, transformed)
        shap_values = explainer(transformed)
        shap.summary_plot(shap_values, show=False)
        fig = plt.gcf()
    except Exception:
        ax.text(0.5, 0.5, "SHAP explanation unavailable", ha="center", va="center")
        ax.set_axis_off()
    return _fig_to_base64(fig)


def _plot_feature_importance(pipeline: Pipeline) -> str:
    fig, ax = plt.subplots(figsize=(8, 6))
    classifier = pipeline.named_steps.get("classifier")
    if classifier is None or not hasattr(classifier, "feature_importances_"):
        ax.text(0.5, 0.5, "Feature importance not available", ha="center", va="center")
        ax.set_axis_off()
        return _fig_to_base64(fig)

    importances = classifier.feature_importances_
    indices = np.argsort(importances)[-15:]
    ax.barh(range(len(indices)), importances[indices])
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([f"feature_{i}" for i in indices])
    ax.set_title("Top 15 Feature Importances")
    fig.tight_layout()
    return _fig_to_base64(fig)


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Model Evaluation Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; background: #f5f5f5; }
    .card { background: white; padding: 1.5rem; margin: 1rem 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    h1 { color: #333; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background: #6750A4; color: white; }
    img { max-width: 100%; margin: 1rem 0; }
  </style>
</head>
<body>
  <h1>Model Evaluation Report</h1>
  <div class="card">
    <h2>Metrics</h2>
    <table>
      {% for k, v in metrics.items() %}
      <tr><th>{{ k }}</th><td>{{ "%.4f"|format(v) }}</td></tr>
      {% endfor %}
    </table>
  </div>
  {% for name, img in plots.items() %}
  <div class="card">
    <h2>{{ name | replace("_", " ") | title }}</h2>
    <img src="data:image/png;base64,{{ img }}" alt="{{ name }}">
  </div>
  {% endfor %}
</body>
</html>
"""


def _render_html(report: EvaluationReport) -> str:
    template = Template(HTML_TEMPLATE)
    return template.render(metrics=report.metrics, plots=report.plots)
