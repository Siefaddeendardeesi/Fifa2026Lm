"""Tests for optional Wikipedia manager enrichment."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.etl import managers


def test_wiki_slug() -> None:
    assert managers._wiki_slug("Brazil") == "Brazil_national_football_team_manager_history"


def test_fetch_manager_history_from_cache(tmp_path: Path) -> None:
    cache = tmp_path / "managers"
    cache.mkdir()
    csv = cache / "Brazil.csv"
    csv.write_text(
        "manager,from,to,team\nTite,2020-01-01,2022-12-31,Brazil\n",
        encoding="utf-8",
    )
    df = managers.fetch_manager_history("Brazil", cache_dir=cache)
    assert df is not None
    assert len(df) == 1


def test_fetch_manager_history_from_wikipedia(mocker, tmp_path: Path) -> None:
    mock_resp = mocker.Mock()
    mock_resp.raise_for_status = mocker.Mock()
    mock_resp.text = "<html></html>"
    mocker.patch("src.etl.managers.requests.get", return_value=mock_resp)
    table = pd.DataFrame(
        {"Manager": ["Coach A"], "From": ["2020"], "To": ["2022"]},
    )
    mocker.patch("src.etl.managers.pd.read_html", return_value=[table])
    df = managers.fetch_manager_history("Testland", cache_dir=tmp_path / "mgr")
    assert df is not None
    assert "manager" in df.columns


def test_fetch_manager_history_network_error(mocker, tmp_path: Path) -> None:
    mocker.patch("src.etl.managers.requests.get", side_effect=Exception("network"))
    assert managers.fetch_manager_history("Failteam", cache_dir=tmp_path / "mgr") is None


def test_fetch_manager_history_no_table(mocker, tmp_path: Path) -> None:
    mock_resp = mocker.Mock()
    mock_resp.raise_for_status = mocker.Mock()
    mock_resp.text = "<html><body></body></html>"
    mocker.patch("src.etl.managers.requests.get", return_value=mock_resp)
    mocker.patch("src.etl.managers.pd.read_html", return_value=[])
    assert managers.fetch_manager_history("Empty", cache_dir=tmp_path / "mgr") is None


def test_resolve_manager() -> None:
    history = pd.DataFrame(
        {
            "manager": ["Alice"],
            "from": [pd.Timestamp("2020-01-01")],
            "to": [pd.Timestamp("2024-01-01")],
        }
    )
    cache = {"Brazil": history}
    name = managers.resolve_manager("Brazil", pd.Timestamp("2022-06-01"), cache)
    assert name == "Alice"


def test_resolve_manager_open_ended() -> None:
    history = pd.DataFrame(
        {
            "manager": ["Bob"],
            "from": [pd.Timestamp("2020-01-01")],
            "to": [pd.NaT],
        }
    )
    cache = {"France": history}
    name = managers.resolve_manager("France", pd.Timestamp("2025-01-01"), cache)
    assert name == "Bob"


def test_add_manager_features(mocker, sample_matches_df) -> None:
    mocker.patch(
        "src.etl.managers.fetch_manager_history",
        return_value=pd.DataFrame(
            {
                "manager": ["Coach"],
                "from": [pd.Timestamp("1990-01-01")],
                "to": [pd.Timestamp("2030-01-01")],
            }
        ),
    )
    out = managers.add_manager_features(sample_matches_df.head(5))
    assert "home_manager" in out.columns
    assert "away_manager" in out.columns
