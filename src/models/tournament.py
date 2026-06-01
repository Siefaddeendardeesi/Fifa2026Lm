"""Backward-compatible re-exports."""

from src.rankings.predictor import build_match_probability_cache
from src.simulation.engine import (
    SimulationResult,
    all_wc2026_teams,
    load_wc2026_groups,
    run_monte_carlo,
    simulate_tournament_once,
)

__all__ = [
    "SimulationResult",
    "all_wc2026_teams",
    "build_match_probability_cache",
    "load_wc2026_groups",
    "run_monte_carlo",
    "simulate_tournament_once",
]
