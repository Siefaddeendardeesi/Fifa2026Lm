"""Integration tests for tournament simulation."""

from __future__ import annotations

import pytest

from src.simulation.engine import SimulationEngine, run_monte_carlo
from tests.fixtures.simulation_mocks import make_prob_cache, make_snapshots


@pytest.fixture
def sim_engine_mocks(mocker, wc2026_groups, trained_pipeline, features_df):
    from src.simulation.engine import all_wc2026_teams

    teams = all_wc2026_teams(wc2026_groups)
    mocker.patch("src.simulation.engine.joblib.load", return_value=trained_pipeline)
    mocker.patch("src.simulation.engine.pd.read_parquet", return_value=features_df)
    mocker.patch(
        "src.simulation.engine.build_match_probability_cache",
        return_value=make_prob_cache(teams),
    )
    mocker.patch("src.simulation.engine._load_snapshots", return_value=make_snapshots(teams))
    return teams


def test_run_monte_carlo_small(project_root, sim_engine_mocks) -> None:
    result = run_monte_carlo(
        n_simulations=30,
        seed=99,
        model_path=project_root / "data" / "processed" / "baseline_model.joblib",
        features_path=project_root / "data" / "processed" / "features.parquet",
        groups_path=project_root / "data" / "reference" / "wc2026_groups.json",
    )
    assert result.n_simulations == 30
    assert len(result.champion_probs) > 0


def test_simulation_engine_serial_workers(project_root, sim_engine_mocks) -> None:
    engine = SimulationEngine()
    result = engine.run(
        n_simulations=25,
        seed=7,
        workers=1,
        model_path=project_root / "data" / "processed" / "baseline_model.joblib",
        features_path=project_root / "data" / "processed" / "features.parquet",
        groups_path=project_root / "data" / "reference" / "wc2026_groups.json",
    )
    top = max(result.champion_probs.values())
    assert top > 0
