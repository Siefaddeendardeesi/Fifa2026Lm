"""Shared mocks for fast simulation tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pandas as pd


def make_prob_cache(teams: list[str]) -> dict[tuple[str, str], tuple[float, float, float]]:
    cache: dict[tuple[str, str], tuple[float, float, float]] = {}
    for home in teams:
        for away in teams:
            if home != away:
                cache[(home, away)] = (0.45, 0.25, 0.30)
    return cache


def make_snapshots(teams: list[str]) -> dict[str, dict[str, Any]]:
    return {
        t: {
            "elo": 1600.0,
            "fifa_rank": 10.0,
            "confederation": "UEFA",
            "form_wins_10": 5,
            "form_draws_10": 2,
            "form_losses_10": 3,
            "form_goals_for_10": 12,
            "form_goals_against_10": 8,
            "form_clean_sheets_10": 2,
            "form_points_10": 17,
            "form_goal_diff_10": 4,
            "form_win_rate_10": 0.5,
            "wc_titles": 1,
            "squad_value": 100.0,
            "last_match_date": pd.Timestamp("2024-01-01"),
        }
        for t in teams
    }


def mock_streamlit(
    mocker: MagicMock, *, button: bool = False, selectbox_side_effect: list | None = None
) -> MagicMock:
    """Patch app.dashboard.main.st with sensible defaults."""
    st = mocker.patch("app.dashboard.main.st")
    st.session_state = {}
    col = MagicMock()
    col.__enter__ = MagicMock(return_value=col)
    col.__exit__ = MagicMock(return_value=False)

    container = MagicMock()
    container.__enter__ = MagicMock(return_value=col)
    container.__exit__ = MagicMock(return_value=False)
    st.container = MagicMock(return_value=container)

    def _columns(spec: Any) -> list:
        n = len(spec) if isinstance(spec, list) else spec
        return [col] * n

    st.columns = MagicMock(side_effect=_columns)
    st.selectbox = MagicMock(side_effect=selectbox_side_effect or ["model", "All", "Mexico"])
    st.number_input.return_value = 42
    st.slider.return_value = 12
    st.button.return_value = button
    st.date_input.return_value = pd.Timestamp("2024-01-01")
    st.checkbox.return_value = True
    st.spinner.return_value.__enter__ = MagicMock(return_value=None)
    st.spinner.return_value.__exit__ = MagicMock(return_value=False)
    return st
