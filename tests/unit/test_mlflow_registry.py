"""Tests for MLflow Model Registry integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.models.mlflow_registry import (
    ensure_champion_registered,
    get_production_model_version,
    register_champion_model,
    registry_summary,
)
from src.utils.exceptions import ModelNotFoundError


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock()
    version = MagicMock()
    version.version = "1"
    version.name = "champion"
    version.current_stage = "Production"
    return client


def test_register_champion_model(mock_client: MagicMock) -> None:
    registered = MagicMock()
    registered.version = "3"
    registered.name = "champion"

    with (
        patch("src.models.mlflow_registry._client", return_value=mock_client),
        patch("src.models.mlflow_registry.mlflow.register_model", return_value=registered) as reg,
    ):
        result = register_champion_model(model_uri="runs:/abc/model")

    reg.assert_called_once()
    mock_client.transition_model_version_stage.assert_called_once()
    assert result.version == "3"


def test_ensure_champion_returns_existing(mock_client: MagicMock) -> None:
    existing = MagicMock()
    existing.name = "champion"
    existing.version = "2"
    existing.current_stage = "Production"

    with (
        patch("src.models.mlflow_registry._client", return_value=mock_client),
        patch("src.models.mlflow_registry.get_production_model_version", return_value=existing),
    ):
        result = ensure_champion_registered()

    assert result.version == "2"


def test_ensure_champion_missing_model_raises(tmp_path, test_settings) -> None:
    with (
        patch("src.models.mlflow_registry.get_production_model_version", return_value=None),
        patch("src.models.mlflow_registry.get_settings", return_value=test_settings),
    ):
        with pytest.raises(ModelNotFoundError):
            ensure_champion_registered()


def test_registry_summary(mock_client: MagicMock) -> None:
    mock_client.search_registered_models.return_value = [MagicMock()]
    with (
        patch("src.models.mlflow_registry._client", return_value=mock_client),
        patch("src.models.mlflow_registry.get_production_model_version") as prod,
    ):
        prod.return_value = MagicMock()
        prod.return_value.name = "champion"
        prod.return_value.version = "1"
        summary = registry_summary()

    assert summary["registered_model_count"] == 1
    assert summary["production_model"] == "champion"
