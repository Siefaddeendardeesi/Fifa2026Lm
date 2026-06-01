"""Tests for backward-compatible src.config module."""

from __future__ import annotations

import importlib


def test_config_compat_module_exports() -> None:
    cfg = importlib.import_module("src.config")
    assert cfg.PROJECT_ROOT.exists()
    assert cfg.DATA_DIR.name == "data"
    assert cfg.FEATURES_PARQUET.name == "features.parquet"
    assert cfg.MODEL_PATH.suffix == ".joblib"
    assert cfg.FORM_WINDOW == 10
    assert "Win" in cfg.TARGET_LABELS


def test_config_paths_under_project_root() -> None:
    import src.config as cfg

    assert cfg.RAW_DIR.parent == cfg.DATA_DIR
    assert cfg.REFERENCE_DIR.parent == cfg.DATA_DIR
