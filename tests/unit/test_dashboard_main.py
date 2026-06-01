"""Tests for app.dashboard.main helpers."""

from __future__ import annotations


def test_team_group() -> None:
    from app.dashboard.main import _team_group

    groups = {"A": ["Mexico", "Brazil"], "B": ["Canada"]}
    assert _team_group("Mexico", groups) == "A"
    assert _team_group("Unknown", groups) is None


def test_model_ready_true(mocker, tmp_path, test_settings) -> None:
    from app.dashboard import main

    test_settings.processed_dir = tmp_path / "processed"
    test_settings.models_dir = tmp_path / "processed" / "models"
    test_settings.processed_dir.mkdir(parents=True)
    test_settings.model_path.write_bytes(b"model")
    test_settings.features_parquet.write_bytes(b"feat")
    mocker.patch.object(main, "get_settings", return_value=test_settings)
    assert main._model_ready() is True


def test_model_ready_false(mocker, tmp_path, test_settings) -> None:
    from app.dashboard import main

    test_settings.processed_dir = tmp_path / "empty"
    test_settings.models_dir = tmp_path / "empty" / "models"
    mocker.patch.object(main, "get_settings", return_value=test_settings)
    assert main._model_ready() is False


def test_load_groups(project_root) -> None:
    from app.dashboard.main import _load_groups

    _load_groups.clear()
    groups = _load_groups()
    assert len(groups) == 12
