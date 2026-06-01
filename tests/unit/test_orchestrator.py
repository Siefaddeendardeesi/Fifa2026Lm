"""Tests for src.etl.orchestrator."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.etl.orchestrator import ETLOrchestrator
from src.utils.exceptions import ETLProcessingError


def test_run_download_success(mock_etl_orchestrator, mocker, project_root: Path) -> None:
    results = project_root / "data" / "raw" / "results.csv"
    if results.exists():
        mocker.patch.object(
            mock_etl_orchestrator.metadata,
            "record_source",
            return_value={"name": "results"},
        )
    result = mock_etl_orchestrator.run_download(skip_kaggle=True)
    assert result["status"] == "success"


def test_run_download_failure_records_metadata(mocker, test_settings, tmp_path: Path) -> None:
    orch = ETLOrchestrator()
    mocker.patch("src.etl.orchestrator.download_all", side_effect=RuntimeError("network"))
    with pytest.raises(RuntimeError):
        orch.run_download(skip_kaggle=True)
    assert orch.metadata._data["runs"][-1]["status"] == "failed"


def test_run_build_features_success(mock_etl_orchestrator) -> None:
    result = mock_etl_orchestrator.run_build_features(validate=True)
    assert result["status"] == "success"


def test_run_build_features_failure(mocker, test_settings) -> None:
    orch = ETLOrchestrator()
    mocker.patch("src.etl.orchestrator.load_matches", side_effect=ValueError("bad"))
    with pytest.raises(ETLProcessingError):
        orch.run_build_features(validate=True)


def test_run_full_pipeline(mock_etl_orchestrator) -> None:
    result = mock_etl_orchestrator.run_full_pipeline(skip_download=True)
    assert "features" in result
