"""Tests for Streamlit dashboard pages with mocked UI."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pandas as pd
import pytest

from tests.fixtures.simulation_mocks import mock_streamlit


@pytest.fixture
def dash_mocks(mocker, project_root, features_df, trained_pipeline):
    st = mock_streamlit(mocker)
    mocker.patch("app.dashboard.main._load_groups", return_value={"A": ["Mexico", "Brazil"]})
    mocker.patch(
        "app.dashboard.main._load_squads",
        return_value={"squads": {"Mexico": {"status": "final", "player_count": 23, "players": []}}},
    )
    mocker.patch("app.dashboard.main._load_features", return_value=features_df.head(100))
    mocker.patch("app.dashboard.main._load_pipeline", return_value=trained_pipeline)
    mocker.patch("app.dashboard.main.render_sidebar_nav", return_value="overview")
    mocker.patch("app.dashboard.main.init_session_state")
    mocker.patch("app.dashboard.main._model_ready", return_value=True)
    mocker.patch(
        "app.dashboard.main.all_wc2026_teams", return_value=["Mexico", "Brazil", "Argentina"]
    )
    mocker.patch("app.dashboard.components.render_hero")
    mocker.patch("app.dashboard.components.render_section")
    mocker.patch("app.dashboard.components.render_stat_cards")
    mocker.patch("app.dashboard.components.render_group_card")
    mocker.patch("app.dashboard.components.render_podium")
    mocker.patch("app.dashboard.components.render_match_result")
    mocker.patch("app.dashboard.components.styled_dataframe")
    mocker.patch("app.dashboard.components.team_row", return_value="<div></div>")
    return st


def test_page_overview(dash_mocks, wc2026_groups) -> None:
    from app.dashboard.main import page_overview

    page_overview(wc2026_groups)


def test_page_groups(dash_mocks, wc2026_groups) -> None:
    from app.dashboard.main import page_groups

    page_groups(wc2026_groups)


def test_page_simulation_no_run(dash_mocks, wc2026_groups, test_settings) -> None:
    from app.dashboard.main import page_simulation

    dash_mocks.button.return_value = False
    page_simulation(wc2026_groups)


def test_page_simulation_with_run(dash_mocks, wc2026_groups, mocker, test_settings) -> None:
    from unittest.mock import MagicMock

    from app.dashboard.main import page_simulation

    dash_mocks.button.return_value = True
    dash_mocks.selectbox = MagicMock(return_value=500)
    dash_mocks.number_input.return_value = 42
    test_settings.processed_dir.mkdir(parents=True, exist_ok=True)
    mocker.patch(
        "app.dashboard.main._cached_simulation",
        return_value={
            "n_simulations": 100,
            "seed": 42,
            "champion_probability": {"Brazil": 0.5, "Argentina": 0.5},
        },
    )
    page_simulation(wc2026_groups)
    assert dash_mocks.session_state.get("sim_result") is not None


def test_page_simulation_error(dash_mocks, wc2026_groups, mocker, test_settings) -> None:
    from unittest.mock import MagicMock

    from app.dashboard.main import page_simulation

    dash_mocks.button.return_value = True
    dash_mocks.selectbox = MagicMock(return_value=500)
    dash_mocks.number_input.return_value = 42
    test_settings.processed_dir.mkdir(parents=True, exist_ok=True)
    mocker.patch("app.dashboard.main._cached_simulation", side_effect=RuntimeError("fail"))
    page_simulation(wc2026_groups)
    dash_mocks.error.assert_called()


def test_page_predictions(dash_mocks, mocker) -> None:
    from app.dashboard.main import page_predictions

    dash_mocks.button.return_value = True
    mocker.patch(
        "app.dashboard.main.extract_team_snapshot",
        return_value={
            "elo": 1600,
            "fifa_rank": 1,
            "confederation": "UEFA",
            "form_wins_10": 5,
            "form_draws_10": 2,
            "form_losses_10": 3,
            "form_goals_for_10": 10,
            "form_goals_against_10": 5,
            "form_clean_sheets_10": 2,
            "form_points_10": 17,
            "form_goal_diff_10": 5,
            "form_win_rate_10": 0.5,
            "wc_titles": 1,
            "squad_value": 100,
        },
    )
    mocker.patch("app.dashboard.main.predict_match_proba", return_value=(0.5, 0.25, 0.25))
    page_predictions(["Argentina", "Brazil"])
    assert "match_pred" in dash_mocks.session_state


def test_page_rankings_compute(dash_mocks, mocker) -> None:
    from app.dashboard.main import page_rankings

    dash_mocks.button.return_value = True
    mocker.patch(
        "app.dashboard.main._cached_rankings",
        return_value=pd.DataFrame({"team": ["Brazil"], "avg_win_prob": [0.6], "rank": [1]}),
    )
    page_rankings()
    assert dash_mocks.session_state.get("rankings_df") is not None


def test_page_rankings_no_data(dash_mocks) -> None:
    from app.dashboard.main import page_rankings

    dash_mocks.button.return_value = False
    page_rankings()
    dash_mocks.info.assert_called()


def test_page_squads(dash_mocks, wc2026_groups, mocker) -> None:
    from app.dashboard.main import page_squads

    mocker.patch("app.dashboard.main.teams_with_squads", return_value=["Mexico"])
    mocker.patch(
        "app.dashboard.main.get_team_squad",
        return_value={"player_count": 23, "players": [{"name": "P1"}]},
    )
    page_squads(wc2026_groups, ["Mexico", "Brazil"])


def test_page_squads_empty_group(dash_mocks, wc2026_groups, mocker) -> None:
    from app.dashboard.main import page_squads

    dash_mocks.selectbox = MagicMock(side_effect=["B", "Mexico"])
    mocker.patch("app.dashboard.main.teams_with_squads", return_value=[])
    page_squads(wc2026_groups, ["Mexico"])
    dash_mocks.warning.assert_called()


def test_page_analytics_with_metrics(dash_mocks, test_settings, features_df, mocker) -> None:
    from app.dashboard.main import page_analytics

    test_settings.reports_dir.mkdir(parents=True, exist_ok=True)
    metrics = test_settings.reports_dir / "baseline_metrics.json"
    metrics.write_text(
        json.dumps({"accuracy": 0.5, "train_size": 100, "test_size": 20}), encoding="utf-8"
    )
    mocker.patch("app.dashboard.main._load_features", return_value=features_df.head(50))
    page_analytics()


def test_page_analytics_no_metrics(dash_mocks, test_settings, features_df, mocker) -> None:
    from app.dashboard.main import page_analytics

    test_settings.reports_dir.mkdir(parents=True, exist_ok=True)
    mocker.patch("app.dashboard.main.get_settings", return_value=test_settings)
    mocker.patch("app.dashboard.main._load_features", return_value=features_df.head(50))
    page_analytics()
    dash_mocks.info.assert_called()


def test_main_routes_overview(dash_mocks, mocker, wc2026_groups) -> None:
    from app.dashboard.main import main

    overview = mocker.patch("app.dashboard.main.page_overview")
    mocker.patch("app.dashboard.main.render_sidebar_nav", return_value="overview")
    mocker.patch("app.dashboard.main._load_groups", return_value=wc2026_groups)
    main()
    overview.assert_called_once()


def test_main_model_not_ready(mocker) -> None:
    from app.dashboard.main import main

    mock_st = mock_streamlit(mocker)
    mocker.patch("app.dashboard.main._model_ready", return_value=False)
    mocker.patch("app.dashboard.main.init_session_state")
    main()
    mock_st.error.assert_called()
    mock_st.stop.assert_called()
