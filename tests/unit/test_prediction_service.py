"""Tests for app.services.prediction."""

from __future__ import annotations

import pytest

from app.services.prediction import (
    PredictionService,
    RankingsService,
    SimulationService,
    TeamsService,
)
from src.utils.exceptions import NotFoundError


def test_prediction_service_predict(trained_pipeline, features_df, mocker, test_settings) -> None:
    svc = PredictionService()
    mocker.patch.object(
        type(svc), "pipeline", new_callable=mocker.PropertyMock, return_value=trained_pipeline
    )
    mocker.patch.object(
        type(svc), "features", new_callable=mocker.PropertyMock, return_value=features_df
    )
    result = svc.predict("Brazil", "Argentina")
    assert 0 <= result.home_win <= 1
    assert abs(result.home_win + result.draw + result.away_win - 1.0) < 0.02


def test_prediction_service_not_found(features_df, mocker, test_settings) -> None:
    svc = PredictionService()
    mocker.patch.object(
        type(svc), "features", new_callable=mocker.PropertyMock, return_value=features_df
    )
    mocker.patch.object(
        type(svc), "pipeline", new_callable=mocker.PropertyMock, return_value=mocker.Mock()
    )
    with pytest.raises(NotFoundError):
        svc.predict("NonexistentTeamA", "NonexistentTeamB")


def test_prediction_service_is_ready(project_root, test_settings) -> None:
    svc = PredictionService()
    assert svc.is_ready() or (project_root / "data" / "processed" / "features.parquet").exists()


def test_teams_service(project_root) -> None:
    svc = TeamsService()
    teams = svc.get_teams()
    assert teams.count == 48
    groups = svc.get_groups()
    assert groups.group_count == 12


def test_rankings_service(features_df, trained_pipeline, mocker, test_settings) -> None:
    svc = RankingsService()
    mocker.patch.object(
        svc.engine,
        "compute",
        return_value=__import__("pandas").DataFrame(
            {"rank": [1], "team": ["Brazil"], "avg_win_prob": [0.6], "fifa_rank": [1.0]}
        ),
    )
    resp = svc.get_rankings(method="model", pool_size=1)
    assert resp.rankings[0].team == "Brazil"


def test_simulation_service(mocker, test_settings, tmp_path) -> None:
    from src.simulation.engine import SimulationResult

    svc = SimulationService()
    fake = SimulationResult(
        n_simulations=5,
        champion_probs={"Brazil": 0.5},
        finalist_probs={"Argentina": 0.5},
        group_winner_probs={"A": {"Brazil": 0.8}},
        seed=1,
    )
    mocker.patch.object(svc.engine, "run", return_value=fake)
    resp = svc.simulate(5, seed=1)
    assert resp.n_simulations == 5
