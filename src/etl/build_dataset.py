"""Assemble final feature matrix and train/test splits."""

from __future__ import annotations

import pandas as pd

from src.config import (
    FEATURES_PARQUET,
    FINAL_COLUMNS,
    PROCESSED_DIR,
    TEST_PARQUET,
    TEST_START_DEFAULT,
    TEST_START_WC2022,
    TRAIN_CUTOFF_DEFAULT,
    TRAIN_CUTOFF_WC2022,
    TRAIN_PARQUET,
)
from src.etl.form_features import add_form_features
from src.etl.loaders import load_fifa_rankings, load_matches
from src.etl.merge_elo import merge_elo
from src.etl.merge_rankings import merge_rankings
from src.etl.transfermarkt import load_squad_values, merge_squad_values
from src.etl.wc_features import add_wc_features


def get_split_dates(split: str = "default") -> tuple[pd.Timestamp, pd.Timestamp]:
    if split == "wc2022":
        return pd.Timestamp(TRAIN_CUTOFF_WC2022), pd.Timestamp(TEST_START_WC2022)
    return pd.Timestamp(TRAIN_CUTOFF_DEFAULT), pd.Timestamp(TEST_START_DEFAULT)


def build_feature_matrix(
    min_date: str = "1992-01-01",
    include_managers: bool = False,
) -> pd.DataFrame:
    """Run full ETL pipeline and return feature DataFrame."""
    matches = load_matches()
    matches = matches[matches["date"] >= pd.Timestamp(min_date)].copy()

    try:
        rankings = load_fifa_rankings()
        matches = merge_rankings(matches, rankings)
    except FileNotFoundError as exc:
        print(f"Warning: {exc}")
        for col in (
            "home_fifa_rank",
            "away_fifa_rank",
            "fifa_rank_diff",
            "home_confederation",
            "away_confederation",
        ):
            matches[col] = pd.NA

    try:
        matches = merge_elo(matches)
    except Exception as exc:
        print(f"Warning: ELO merge failed: {exc}")
        matches["home_elo"] = pd.NA
        matches["away_elo"] = pd.NA
        matches["elo_diff"] = pd.NA

    matches = add_form_features(matches)
    matches = add_wc_features(matches)

    squad = load_squad_values()
    matches = merge_squad_values(matches, squad)

    if include_managers:
        from src.etl.managers import add_manager_features

        matches = add_manager_features(matches)

    for col in FINAL_COLUMNS:
        if col not in matches.columns:
            matches[col] = pd.NA

    return matches[FINAL_COLUMNS].copy()


def save_splits(df: pd.DataFrame, split: str = "default") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Save features.parquet plus train/test splits."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    train_cutoff, test_start = get_split_dates(split)

    df.to_parquet(FEATURES_PARQUET, index=False)

    train = df[df["date"] < train_cutoff].copy()
    test = df[df["date"] >= test_start].copy()

    train.to_parquet(TRAIN_PARQUET, index=False)
    test.to_parquet(TEST_PARQUET, index=False)

    print(f"Saved {len(df)} rows to {FEATURES_PARQUET}")
    print(f"Train: {len(train)} rows (< {train_cutoff.date()})")
    print(f"Test:  {len(test)} rows (>= {test_start.date()})")
    return train, test
