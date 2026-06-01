"""Tests for app.dashboard.components with mocked Streamlit."""

from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd
import pytest


@pytest.fixture
def mock_st(mocker):
    st = mocker.patch("app.dashboard.components.st")
    st.session_state = {}
    st.sidebar = MagicMock()
    st.sidebar.toggle.return_value = False
    st.sidebar.radio.return_value = "overview"
    st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
    return st


def test_init_session_state(mocker) -> None:
    from app.dashboard.components import init_session_state

    mock_state: dict = {}
    mocker.patch("app.dashboard.components.st").session_state = mock_state
    init_session_state()
    assert mock_state["page"] == "overview"
    assert mock_state["dark_mode"] is False


def test_render_sidebar_nav(mock_st) -> None:
    from app.dashboard.components import render_sidebar_nav

    page = render_sidebar_nav()
    assert page == "overview"
    mock_st.sidebar.radio.assert_called_once()


def test_render_hero(mock_st) -> None:
    from app.dashboard.components import render_hero

    render_hero()
    mock_st.markdown.assert_called()


def test_render_section(mock_st) -> None:
    from app.dashboard.components import render_section

    render_section("Title", "Subtitle")
    mock_st.markdown.assert_called()


def test_render_stat_cards(mock_st, mocker) -> None:
    from app.dashboard.components import render_stat_cards

    cols = [MagicMock(), MagicMock()]
    mock_st.columns.return_value = cols
    render_stat_cards([("A", "1", "hint"), ("B", "2", "hint")])
    assert mock_st.columns.called


def test_render_group_card(mock_st) -> None:
    from app.dashboard.components import render_group_card

    render_group_card("A", "<div>team</div>")
    mock_st.markdown.assert_called()


def test_team_row() -> None:
    from app.dashboard.components import team_row

    html = team_row("Brazil", "badge-final", "F")
    assert "Brazil" in html
    assert "badge-final" in html


def test_render_podium(mock_st, mocker) -> None:
    from app.dashboard.components import render_podium

    mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
    render_podium([("A", 30.0), ("B", 20.0), ("C", 10.0)])
    mock_st.markdown.assert_called()


def test_render_podium_short_list(mock_st) -> None:
    from app.dashboard.components import render_podium

    render_podium([("A", 30.0)])
    mock_st.markdown.assert_not_called()


def test_render_match_result(mock_st) -> None:
    from app.dashboard.components import render_match_result

    render_match_result("Home", "Away", 0.5, 0.3, 0.2)
    assert mock_st.markdown.called
    mock_st.success.assert_called_once()


def test_styled_dataframe(mock_st) -> None:
    from app.dashboard.components import styled_dataframe

    styled_dataframe(pd.DataFrame({"a": [1, 2]}))
    mock_st.dataframe.assert_called_once()
