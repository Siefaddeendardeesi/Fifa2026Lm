"""Tests for API lifecycle and error paths."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api import main as api_main
from src.utils.exceptions import SimulationError


@pytest.fixture
def client(test_settings) -> TestClient:
    return TestClient(api_main.app)


@pytest.mark.asyncio
async def test_lifespan() -> None:
    app = api_main.create_app()
    async with api_main.lifespan(app):
        pass


def test_run_server(mocker, test_settings) -> None:
    mock_uvicorn = mocker.patch("uvicorn.run")
    mocker.patch.object(api_main, "get_settings", return_value=test_settings)
    api_main.run_server()
    mock_uvicorn.assert_called_once()


def test_platform_error_500(client: TestClient, mocker) -> None:
    mocker.patch(
        "app.services.prediction.PredictionService.predict",
        side_effect=SimulationError("sim failed"),
    )
    resp = client.post(
        "/predict",
        json={"home_team": "Brazil", "away_team": "Argentina", "neutral": True},
    )
    assert resp.status_code == 500
    assert resp.json()["error"] == "sim failed"


def test_create_app_module_entry() -> None:
    assert api_main.app is not None
    assert api_main.app.title
