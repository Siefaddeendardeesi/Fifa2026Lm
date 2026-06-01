"""Tests for src.simulation.engine."""

from __future__ import annotations

import numpy as np
import pytest

from src.simulation.engine import (
    GroupStanding,
    SimulationEngine,
    SimulationResult,
    TournamentFormat,
    _apply_result,
    _is_neutral,
    _knockout_winner,
    _rank_group,
    _rank_third_placed,
    _sample_group_score,
    _seed_knockout,
    all_wc2026_teams,
    load_wc2026_groups,
    simulate_tournament_once,
)
from src.utils.exceptions import SimulationError
from tests.fixtures.simulation_mocks import make_prob_cache, make_snapshots


@pytest.fixture
def sim_engine_mocks(mocker, wc2026_groups, trained_pipeline, features_df):
    """Mock expensive simulation I/O for fast tests."""
    teams = all_wc2026_teams(wc2026_groups)
    mocker.patch("src.simulation.engine.joblib.load", return_value=trained_pipeline)
    mocker.patch("src.simulation.engine.pd.read_parquet", return_value=features_df)
    mocker.patch(
        "src.simulation.engine.build_match_probability_cache",
        return_value=make_prob_cache(teams),
    )
    mocker.patch("src.simulation.engine._load_snapshots", return_value=make_snapshots(teams))
    return teams


def test_load_wc2026_groups(project_root) -> None:
    groups = load_wc2026_groups(project_root / "data" / "reference" / "wc2026_groups.json")
    assert len(groups) == 12
    teams = all_wc2026_teams(groups)
    assert len(teams) == 48


def test_is_neutral_hosts() -> None:
    assert _is_neutral("Mexico", "Brazil") is False
    assert _is_neutral("Brazil", "France") is True


def test_group_standing_points() -> None:
    s = GroupStanding(team="A", wins=2, draws=1)
    assert s.points == 7
    assert s.goal_diff == 0


def test_apply_result_and_rank() -> None:
    standings = {"H": GroupStanding("H"), "A": GroupStanding("A")}
    _apply_result(standings, "H", "A", 2, 0)
    ranked = _rank_group(list(standings.values()))
    assert ranked[0].team == "H"


def test_sample_group_score() -> None:
    rng = np.random.default_rng(0)
    cache = {("A", "B"): (0.9, 0.05, 0.05)}
    score = _sample_group_score(cache, "A", "B", rng)
    assert sum(score) >= 0


def test_knockout_winner() -> None:
    rng = np.random.default_rng(1)
    cache = {("A", "B"): (0.7, 0.2, 0.1)}
    winner = _knockout_winner(cache, "A", "B", rng)
    assert winner in ("A", "B")


def test_knockout_winner_zero_total() -> None:
    rng = np.random.default_rng(0)
    cache = {("A", "B"): (0.0, 0.5, 0.0)}
    assert _knockout_winner(cache, "A", "B", rng) in ("A", "B")


def test_rank_third_placed() -> None:
    thirds = [
        ("T1", GroupStanding("T1", wins=1, draws=1, goals_for=3)),
        ("T2", GroupStanding("T2", wins=2, draws=0, goals_for=4)),
    ]
    ranked = _rank_third_placed(thirds, count=1)
    assert ranked == ["T2"]


def test_seed_knockout() -> None:
    qualified = [
        ("A", GroupStanding("A", wins=3, goals_for=5)),
        ("B", GroupStanding("B", wins=1, goals_for=2)),
    ]
    seeded = _seed_knockout(qualified)
    assert seeded[0] == "A"


def test_simulate_tournament_once(wc2026_groups, sim_engine_mocks) -> None:
    teams = sim_engine_mocks
    cache = make_prob_cache(teams)
    rng = np.random.default_rng(42)
    champion, runner_up, tables = simulate_tournament_once(cache, wc2026_groups, rng)
    assert champion in teams
    assert runner_up in teams
    assert len(tables) == 12


def test_simulation_engine_run_small(wc2026_groups, sim_engine_mocks, project_root) -> None:
    engine = SimulationEngine()
    result = engine.run(
        n_simulations=20,
        seed=42,
        model_path=project_root / "data" / "processed" / "baseline_model.joblib",
        features_path=project_root / "data" / "processed" / "features.parquet",
        groups_path=project_root / "data" / "reference" / "wc2026_groups.json",
        workers=1,
    )
    assert result.n_simulations == 20
    assert abs(sum(result.champion_probs.values()) - 1.0) < 0.01


def test_simulation_engine_multiprocessing(
    wc2026_groups, sim_engine_mocks, project_root, mocker
) -> None:
    from concurrent.futures import Future

    def fake_submit(fn, *args, **kwargs):
        fut: Future = Future()
        fut.set_result(fn(*args, **kwargs))
        return fut

    mock_executor = mocker.patch("src.simulation.engine.ProcessPoolExecutor")
    mock_executor.return_value.__enter__.return_value.submit.side_effect = fake_submit

    engine = SimulationEngine()
    result = engine.run(
        n_simulations=100,
        seed=7,
        model_path=project_root / "data" / "processed" / "baseline_model.joblib",
        features_path=project_root / "data" / "processed" / "features.parquet",
        groups_path=project_root / "data" / "reference" / "wc2026_groups.json",
        workers=4,
    )
    assert result.n_simulations == 100
    mock_executor.assert_called_once()


def test_load_snapshots_missing_team(features_df, mocker) -> None:
    from src.simulation.engine import _load_snapshots

    mocker.patch("src.simulation.engine.extract_team_snapshot", return_value=None)
    with pytest.raises(SimulationError, match="No feature snapshot"):
        _load_snapshots(features_df, ["NonexistentTeam"])


def test_all_wc2026_teams_wrong_count() -> None:
    with pytest.raises(SimulationError):
        all_wc2026_teams({"A": ["X", "Y"]})


def test_tournament_format_defaults() -> None:
    fmt = TournamentFormat()
    assert fmt.team_count == 48


def test_simulation_result_to_dict() -> None:
    result = SimulationResult(
        n_simulations=10,
        champion_probs={"Brazil": 1.0},
        finalist_probs={"Argentina": 0.5},
        group_winner_probs={"A": {"Mexico": 0.3}},
        seed=1,
    )
    d = result.to_dict()
    assert d["n_simulations"] == 10
    assert d["seed"] == 1
