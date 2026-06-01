"""Shared pytest fixtures for FIFA2026LM tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure `app` resolves to the package directory, not root app.py
PROJECT_ROOT_EARLY = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT_EARLY) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT_EARLY))
_app_mod = sys.modules.get("app")
if _app_mod is not None and not hasattr(_app_mod, "__path__"):
    del sys.modules["app"]
from typing import Any
from unittest.mock import MagicMock

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from src.config.constants import FEATURE_COLS
from src.config.settings import Environment, Settings, get_settings
from src.models.base import LogisticRegressionModel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SAMPLE_MATCHES_CSV = FIXTURES_DIR / "sample_matches.csv"


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def test_settings(tmp_path: Path, project_root: Path, monkeypatch: pytest.MonkeyPatch) -> Settings:
    """Isolated settings with writable metadata/reports under tmp_path."""
    settings = Settings(
        environment=Environment.TEST,
        debug=True,
        log_level="DEBUG",
        log_json=False,
        etl_cache_enabled=False,
        project_root=project_root,
        data_dir=project_root / "data",
        raw_dir=project_root / "data" / "raw",
        processed_dir=project_root / "data" / "processed",
        reference_dir=project_root / "data" / "reference",
        metadata_dir=tmp_path / "metadata",
        reports_dir=tmp_path / "reports",
        cache_dir=tmp_path / "cache",
        models_dir=project_root / "data" / "processed" / "models",
        mlflow_tracking_uri=f"file:{tmp_path / 'mlruns'}",
        api_rate_limit="10000/minute",
        simulation_workers=1,
        simulation_default_runs=50,
    )
    monkeypatch.setattr("src.config.settings.get_settings", lambda: settings)
    return settings


@pytest.fixture
def sample_matches_df() -> pd.DataFrame:
    """Small match DataFrame from fixture CSV."""
    from src.etl.loaders import derive_result

    df = pd.read_csv(SAMPLE_MATCHES_CSV)
    df["date"] = pd.to_datetime(df["date"])
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)
    df["result"] = df.apply(lambda r: derive_result(r["home_score"], r["away_score"]), axis=1)
    if "neutral" not in df.columns:
        df["neutral"] = False
    df["neutral"] = df["neutral"].fillna(False).astype(bool)
    return df


@pytest.fixture(scope="session")
def features_df(project_root: Path) -> pd.DataFrame:
    """Full feature matrix from processed data."""
    path = project_root / "data" / "processed" / "features.parquet"
    if not path.exists():
        pytest.skip("features.parquet not available")
    df = pd.read_parquet(path)
    df["date"] = pd.to_datetime(df["date"])
    return df


@pytest.fixture
def train_test_frames(features_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Recent train/test split for model tests."""
    cutoff = pd.Timestamp("2022-01-01")
    train = features_df[features_df["date"] < cutoff].tail(2000).copy()
    test = features_df[features_df["date"] >= cutoff].head(500).copy()
    return train, test


@pytest.fixture(scope="session")
def trained_pipeline(project_root: Path) -> Any:
    """Load baseline model or train a minimal pipeline on features."""
    model_path = project_root / "data" / "processed" / "baseline_model.joblib"
    if model_path.exists():
        return joblib.load(model_path)

    features_path = project_root / "data" / "processed" / "features.parquet"
    if not features_path.exists():
        pytest.skip("No model or features for pipeline fixture")

    df = pd.read_parquet(features_path)
    df["date"] = pd.to_datetime(df["date"])
    train = df[df["date"] < "2022-01-01"].tail(500)
    impl = LogisticRegressionModel()
    x, y = impl.prepare_xy(train)
    pipe = impl.build_pipeline(list(x.columns))
    pipe.fit(x, y)
    return pipe


@pytest.fixture
def mock_pipeline(mocker: pytest.MockFixture) -> MagicMock:
    """Mock sklearn pipeline returning fixed probabilities."""
    pipe = MagicMock()
    pipe.predict_proba.return_value = np.array([[0.5, 0.25, 0.25]])
    pipe.predict.return_value = np.array([0])
    mocker.patch("joblib.load", return_value=pipe)
    return pipe


@pytest.fixture
def mock_etl_orchestrator(mocker: pytest.MockFixture, test_settings: Settings) -> Any:
    """ETLOrchestrator with download/build steps mocked."""
    from src.etl.orchestrator import ETLOrchestrator

    orch = ETLOrchestrator()
    mocker.patch("src.etl.orchestrator.download_all")
    mocker.patch(
        "src.etl.orchestrator.build_feature_matrix",
        return_value=pd.DataFrame({"date": [pd.Timestamp("2024-01-01")], "result": ["Win"]}),
    )
    mocker.patch(
        "src.etl.orchestrator.save_splits",
        return_value=(pd.DataFrame(), pd.DataFrame()),
    )
    mocker.patch("src.etl.orchestrator.load_matches", return_value=pd.DataFrame())
    mocker.patch("src.etl.orchestrator.validate_matches", side_effect=lambda x: x)
    mocker.patch("src.etl.orchestrator.validate_features", side_effect=lambda x: x)
    return orch


@pytest.fixture
def wc2026_groups(project_root: Path) -> dict[str, list[str]]:
    path = project_root / "data" / "reference" / "wc2026_groups.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)["groups"]


@pytest.fixture
def tmp_metadata_store(tmp_path: Path) -> Any:
    from src.etl.metadata import MetadataStore

    return MetadataStore(path=tmp_path / "etl_metadata.json")


@pytest.fixture
def simple_classifier_pipeline() -> Pipeline:
    """Minimal 3-class pipeline for unit tests without data files."""

    def passthrough(x: pd.DataFrame) -> np.ndarray:
        return x.select_dtypes(include=[np.number]).fillna(0).values

    clf = DummyClassifier(strategy="prior")
    clf.fit(np.zeros((3, 2)), np.array([0, 1, 2]))
    return Pipeline(
        steps=[
            ("preprocessor", FunctionTransformer(passthrough)),
            ("classifier", clf),
        ]
    )


@pytest.fixture
def minimal_feature_row() -> pd.DataFrame:
    """Single feature row compatible with FINAL_COLUMNS subset."""
    row: dict[str, Any] = {c: np.nan for c in FEATURE_COLS}
    row.update(
        {
            "home_elo": 1600.0,
            "away_elo": 1550.0,
            "elo_diff": 50.0,
            "home_fifa_rank": 5.0,
            "away_fifa_rank": 10.0,
            "fifa_rank_diff": -5.0,
            "neutral": True,
            "home_confederation": "UEFA",
            "away_confederation": "UEFA",
        }
    )
    df = pd.DataFrame([row])
    df["result"] = "Win"
    return df
