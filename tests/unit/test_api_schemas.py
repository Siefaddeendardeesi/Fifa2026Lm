"""Tests for app.schemas.api."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.api import (
    ErrorResponse,
    GroupsResponse,
    HealthResponse,
    PredictRequest,
    PredictResponse,
    RankingsRequest,
    SimulateRequest,
    TeamInfo,
)


def test_health_response() -> None:
    h = HealthResponse(version="1.0.0", model_loaded=True)
    assert h.status == "healthy"


def test_predict_request_validation() -> None:
    req = PredictRequest(home_team="Brazil", away_team="Argentina")
    assert req.neutral is True


def test_predict_request_empty_team_fails() -> None:
    with pytest.raises(ValidationError):
        PredictRequest(home_team="", away_team="X")


def test_simulate_request_bounds() -> None:
    s = SimulateRequest(n_simulations=100, seed=1)
    assert s.n_simulations == 100
    with pytest.raises(ValidationError):
        SimulateRequest(n_simulations=5)


def test_rankings_request_pattern() -> None:
    r = RankingsRequest(method="elo")
    assert r.method == "elo"
    with pytest.raises(ValidationError):
        RankingsRequest(method="invalid")


def test_predict_response() -> None:
    p = PredictResponse(
        home_team="A",
        away_team="B",
        home_win=0.5,
        draw=0.25,
        away_win=0.25,
        confidence=0.5,
    )
    assert p.confidence == 0.5


def test_groups_and_teams_response() -> None:
    g = GroupsResponse(groups={"A": ["X"]}, group_count=1, team_count=1)
    assert g.team_count == 1
    t = TeamInfo(name="Brazil", group="A", has_squad=True)
    assert t.has_squad


def test_error_response() -> None:
    e = ErrorResponse(error="fail", details={"code": 1})
    assert e.details["code"] == 1
