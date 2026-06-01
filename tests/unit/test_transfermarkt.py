"""Tests for Transfermarkt optional enrichment."""

from __future__ import annotations

import pandas as pd


def test_load_squad_values_missing(tmp_path) -> None:
    from src.etl.transfermarkt import load_squad_values

    df = load_squad_values(tmp_path / "missing.csv")
    assert df.empty


def test_load_squad_values_existing(tmp_path) -> None:
    from src.etl.transfermarkt import load_squad_values

    path = tmp_path / "tm.csv"
    path.write_text("team,date,squad_value\nBrazil,2024-01-01,100\n", encoding="utf-8")
    df = load_squad_values(path)
    assert len(df) == 1


def test_merge_squad_values_empty(sample_matches_df) -> None:
    from src.etl.transfermarkt import merge_squad_values

    out = merge_squad_values(sample_matches_df.head(3), pd.DataFrame())
    assert "home_squad_value" in out.columns


def test_merge_squad_values_with_data(sample_matches_df) -> None:
    from src.etl.transfermarkt import merge_squad_values

    values = pd.DataFrame(
        {
            "team": ["Brazil", "Argentina"],
            "date": [pd.Timestamp("2020-01-01")] * 2,
            "squad_value": [100.0, 90.0],
        }
    )
    out = merge_squad_values(sample_matches_df.head(3), values)
    assert out["home_squad_value"].notna().any() or out["away_squad_value"].notna().any()


def test_fetch_via_apify_no_token(mocker) -> None:
    from src.etl.transfermarkt import fetch_via_apify

    mocker.patch.dict("os.environ", {}, clear=True)
    df = fetch_via_apify(["Brazil"])
    assert df.empty
