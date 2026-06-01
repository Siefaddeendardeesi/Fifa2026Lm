"""Integration tests for ETL pipeline."""

from __future__ import annotations

from src.etl.build_dataset import build_feature_matrix, get_split_dates
from src.etl.loaders import load_matches
from src.etl.validation import validate_matches


def test_load_and_validate_real_results(project_root) -> None:
    df = load_matches(project_root / "data" / "raw" / "results.csv")
    recent = df[df["date"] >= "2020-01-01"].head(500)
    validated = validate_matches(recent)
    assert len(validated) == len(recent)


def test_build_feature_matrix_subset() -> None:
    """Build features on recent matches only (faster integration check)."""
    matches = load_matches()
    matches = matches[matches["date"] >= "2018-01-01"].head(300)
    from src.etl.form_features import add_form_features
    from src.etl.loaders import load_fifa_rankings
    from src.etl.merge_elo import merge_elo
    from src.etl.merge_rankings import merge_rankings

    matches = merge_elo(matches)
    try:
        rankings = load_fifa_rankings()
        matches = merge_rankings(matches, rankings)
    except FileNotFoundError:
        pass
    matches = add_form_features(matches)
    assert "home_elo" in matches.columns


def test_build_feature_matrix_from_project() -> None:
    df = build_feature_matrix(min_date="2019-01-01")
    assert len(df) > 100
    assert "result" in df.columns
    assert df["result"].isin(["Win", "Draw", "Loss"]).all()


def test_split_dates_integration() -> None:
    train_cut, test_start = get_split_dates("default")
    assert test_start >= train_cut
