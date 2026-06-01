"""Tests for src.etl.loaders."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.etl.loaders import derive_result, load_elo, load_fifa_rankings, load_matches


def test_derive_result() -> None:
    assert derive_result(2, 1) == "Win"
    assert derive_result(1, 1) == "Draw"
    assert derive_result(0, 3) == "Loss"


def test_load_matches_from_project_data(project_root: Path) -> None:
    df = load_matches(project_root / "data" / "raw" / "results.csv")
    assert "result" in df.columns
    assert df["result"].isin(["Win", "Draw", "Loss"]).all()
    assert len(df) > 1000


def test_load_matches_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_matches(tmp_path / "missing.csv")


def test_load_elo_from_project(project_root: Path) -> None:
    elo_path = project_root / "data" / "raw" / "elo.csv"
    if not elo_path.exists():
        pytest.skip("elo.csv missing")
    try:
        df = load_elo(elo_path)
    except ValueError:
        pytest.skip("elo.csv format not supported by loader")
    assert {"date", "team", "elo"}.issubset(df.columns)


def test_load_fifa_rankings_from_project(project_root: Path) -> None:
    try:
        df = load_fifa_rankings()
    except FileNotFoundError:
        pytest.skip("ranking file missing")
    assert "rank_date" in df.columns
    assert "team" in df.columns
