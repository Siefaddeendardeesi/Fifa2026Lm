"""End-to-end API tests using FastAPI TestClient."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api import main as api_main
from app.schemas.api import SimulateResponse
from src.simulation.engine import SimulationResult


@pytest.fixture
def client(test_settings) -> TestClient:
    return TestClient(api_main.app)


def test_health_endpoint(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_metrics_endpoint(client: TestClient) -> None:
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers.get("content-type", "")


def test_teams_endpoint(client: TestClient) -> None:
    resp = client.get("/teams")
    assert resp.status_code == 200
    assert resp.json()["count"] == 48


def test_groups_endpoint(client: TestClient) -> None:
    resp = client.get("/groups")
    assert resp.status_code == 200
    body = resp.json()
    assert body["group_count"] == 12
    assert "A" in body["groups"]


def test_predict_endpoint(client: TestClient, project_root) -> None:
    if not (project_root / "data" / "processed" / "features.parquet").exists():
        pytest.skip("features missing")
    resp = client.post(
        "/predict",
        json={"home_team": "Brazil", "away_team": "Argentina", "neutral": True},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert abs(body["home_win"] + body["draw"] + body["away_win"] - 1.0) < 0.05


def test_predict_unknown_team_returns_404(client: TestClient) -> None:
    resp = client.post(
        "/predict",
        json={"home_team": "NotARealTeamXYZ", "away_team": "Brazil", "neutral": True},
    )
    assert resp.status_code == 404
    assert "error" in resp.json()


def test_rankings_endpoint(client: TestClient, project_root) -> None:
    if not (project_root / "data" / "processed" / "baseline_model.joblib").exists():
        pytest.skip("model missing")
    resp = client.get("/rankings", params={"method": "elo", "pool_size": 8, "since": "2020-01-01"})
    assert resp.status_code == 200
    assert len(resp.json()["rankings"]) >= 2


def test_simulate_endpoint_mocked(client: TestClient, mocker) -> None:
    fake = SimulationResult(
        n_simulations=10,
        champion_probs={"Brazil": 0.4, "Argentina": 0.3},
        finalist_probs={"Brazil": 0.2},
        group_winner_probs={"A": {"Mexico": 0.5}},
        seed=42,
    )
    mocker.patch(
        "app.services.prediction.SimulationService.simulate",
        return_value=SimulateResponse(
            n_simulations=10,
            seed=42,
            champion_probability=fake.champion_probs,
            finalist_probability=fake.finalist_probs,
            group_winner_probability=fake.group_winner_probs,
        ),
    )
    resp = client.post("/simulate", json={"n_simulations": 10, "seed": 42})
    assert resp.status_code == 200
    assert resp.json()["n_simulations"] == 10


def test_simulate_validation_error(client: TestClient) -> None:
    resp = client.post("/simulate", json={"n_simulations": 5, "seed": 0})
    assert resp.status_code == 422
