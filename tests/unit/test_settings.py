"""Tests for src.config.settings."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.config.settings import Environment, Settings, get_settings, get_settings_for_env


def test_settings_default_paths(project_root: Path) -> None:
    settings = Settings(project_root=project_root)
    settings.model_post_init(None)
    assert settings.data_dir == project_root / "data"
    assert settings.results_csv == settings.raw_dir / "results.csv"
    assert settings.features_parquet == settings.processed_dir / "features.parquet"


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("dev", Environment.DEVELOPMENT),
        ("test", Environment.TEST),
        ("prod", Environment.PRODUCTION),
        ("staging", Environment.STAGING),
    ],
)
def test_normalize_environment(raw: str, expected: Environment) -> None:
    settings = Settings(environment=raw)
    assert settings.environment == expected


def test_get_settings_for_env_test() -> None:
    settings = get_settings_for_env("test")
    assert settings.is_test
    assert settings.etl_cache_enabled is False


def test_get_settings_cached() -> None:
    get_settings.cache_clear()
    a = get_settings()
    b = get_settings()
    assert a is b


def test_model_path_prefers_champion(project_root: Path, tmp_path: Path) -> None:
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    champion = models_dir / "champion_model.joblib"
    champion.write_text("x")
    settings = Settings(
        project_root=project_root,
        processed_dir=tmp_path / "processed",
        models_dir=models_dir,
    )
    settings.model_post_init(None)
    assert settings.model_path == champion
