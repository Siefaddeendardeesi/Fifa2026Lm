"""Tests for src.etl.build_dataset."""

from __future__ import annotations

import pandas as pd

from src.etl.build_dataset import get_split_dates, save_splits


def test_get_split_dates_default() -> None:
    train_cut, test_start = get_split_dates("default")
    assert train_cut == pd.Timestamp("2022-01-01")
    assert test_start == pd.Timestamp("2022-01-01")


def test_get_split_dates_wc2022() -> None:
    train_cut, _ = get_split_dates("wc2022")
    assert train_cut == pd.Timestamp("2022-11-01")


def test_save_splits_writes_parquet(
    features_df: pd.DataFrame, test_settings, tmp_path, monkeypatch
) -> None:
    proc = tmp_path / "processed"
    proc.mkdir()
    monkeypatch.setattr("src.etl.build_dataset.PROCESSED_DIR", proc)
    monkeypatch.setattr("src.etl.build_dataset.FEATURES_PARQUET", proc / "features.parquet")
    monkeypatch.setattr("src.etl.build_dataset.TRAIN_PARQUET", proc / "train.parquet")
    monkeypatch.setattr("src.etl.build_dataset.TEST_PARQUET", proc / "test.parquet")

    subset = features_df.head(200).copy()
    train, test = save_splits(subset, split="default")
    assert (proc / "features.parquet").exists()
    assert len(train) + len(test) <= len(subset)
