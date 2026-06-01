"""Tests for src.config.constants."""

from __future__ import annotations

from src.config.constants import (
    FEATURE_COLS,
    FINAL_COLUMNS,
    KAGGLE_DATASETS,
    TARGET_LABELS,
    VALID_CONFEDERATIONS,
    WC2026_GROUP_COUNT,
    WC2026_TEAM_COUNT,
)


def test_target_labels_mapping() -> None:
    assert TARGET_LABELS["Win"] == 0
    assert TARGET_LABELS["Draw"] == 1
    assert TARGET_LABELS["Loss"] == 2


def test_feature_cols_exclude_metadata() -> None:
    assert "date" not in FEATURE_COLS
    assert "result" not in FEATURE_COLS
    assert "home_elo" in FEATURE_COLS


def test_final_columns_contains_result() -> None:
    assert "result" in FINAL_COLUMNS
    assert len(FINAL_COLUMNS) >= 30


def test_wc2026_constants() -> None:
    assert WC2026_TEAM_COUNT == 48
    assert WC2026_GROUP_COUNT == 12


def test_valid_confederations() -> None:
    assert "UEFA" in VALID_CONFEDERATIONS
    assert len(VALID_CONFEDERATIONS) == 6


def test_kaggle_datasets_keys() -> None:
    assert "results" in KAGGLE_DATASETS
    assert "fifa_ranking" in KAGGLE_DATASETS
