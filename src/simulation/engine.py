"""Production Monte Carlo tournament simulation engine."""

from __future__ import annotations

import json
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from itertools import combinations
from multiprocessing import cpu_count
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from src.config.constants import HOSTS, WC2026_GROUP_COUNT, WC2026_KNOCKOUT_TEAMS, WC2026_TEAM_COUNT
from src.config.settings import get_settings
from src.rankings.predictor import (
    build_match_probability_cache,
    extract_team_snapshot,
)
from src.utils.exceptions import SimulationError
from src.utils.logging import get_logger
from src.utils.seeds import set_global_seed

logger = get_logger(__name__)

MatchProbs = tuple[float, float, float]


@dataclass
class GroupStanding:
    team: str
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0

    @property
    def points(self) -> int:
        return 3 * self.wins + self.draws

    @property
    def goal_diff(self) -> int:
        return self.goals_for - self.goals_against


@dataclass
class SimulationResult:
    n_simulations: int
    champion_probs: dict[str, float]
    finalist_probs: dict[str, float]
    group_winner_probs: dict[str, dict[str, float]]
    seed: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_simulations": self.n_simulations,
            "seed": self.seed,
            "champion_probability": self.champion_probs,
            "finalist_probability": self.finalist_probs,
            "group_winner_probability": self.group_winner_probs,
        }


@dataclass
class TournamentFormat:
    """Configurable tournament format."""

    team_count: int = WC2026_TEAM_COUNT
    group_count: int = WC2026_GROUP_COUNT
    teams_per_group: int = 4
    knockout_teams: int = WC2026_KNOCKOUT_TEAMS
    third_place_advancing: int = 8


DEFAULT_FORMAT = TournamentFormat()


def load_wc2026_groups(path: Path | None = None) -> dict[str, list[str]]:
    settings = get_settings()
    path = path or settings.groups_json
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    groups: dict[str, list[str]] = data["groups"]
    return groups


def all_wc2026_teams(groups: dict[str, list[str]] | None = None) -> list[str]:
    groups = groups or load_wc2026_groups()
    teams: list[str] = []
    for group_teams in groups.values():
        teams.extend(group_teams)
    if len(teams) != WC2026_TEAM_COUNT:
        raise SimulationError(f"Expected {WC2026_TEAM_COUNT} teams, got {len(teams)}")
    return teams


def _is_neutral(home: str, away: str) -> bool:  # noqa: SIM103
    if home in HOSTS and away not in HOSTS:
        return False
    if away in HOSTS and home not in HOSTS:
        return False
    return True


def _load_snapshots(features: pd.DataFrame, teams: list[str]) -> dict[str, dict[str, Any]]:
    snapshots: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for team in teams:
        snap = extract_team_snapshot(features, team)
        if snap is None:
            missing.append(team)
        else:
            snapshots[team] = snap
    if missing:
        raise SimulationError(f"No feature snapshot for: {', '.join(missing)}")
    return snapshots


def _sample_group_score(
    prob_cache: dict[tuple[str, str], MatchProbs],
    home: str,
    away: str,
    rng: np.random.Generator,
) -> tuple[int, int]:
    p_win, p_draw, _p_loss = prob_cache[(home, away)]
    u = rng.random()
    if u < p_win:
        return 2, 0
    if u < p_win + p_draw:
        return 1, 1
    return 0, 2


def _apply_result(
    standings: dict[str, GroupStanding], home: str, away: str, hs: int, as_: int
) -> None:
    h, a = standings[home], standings[away]
    h.played += 1
    a.played += 1
    h.goals_for += hs
    h.goals_against += as_
    a.goals_for += as_
    a.goals_against += hs
    if hs > as_:
        h.wins += 1
        a.losses += 1
    elif hs < as_:
        h.losses += 1
        a.wins += 1
    else:
        h.draws += 1
        a.draws += 1


def _rank_group(standings: list[GroupStanding]) -> list[GroupStanding]:
    return sorted(
        standings,
        key=lambda s: (s.points, s.goal_diff, s.goals_for, s.team),
        reverse=True,
    )


def _rank_third_placed(thirds: list[tuple[str, GroupStanding]], count: int = 8) -> list[str]:
    ranked = sorted(
        thirds,
        key=lambda x: (x[1].points, x[1].goal_diff, x[1].goals_for, x[0]),
        reverse=True,
    )
    return [team for team, _ in ranked[:count]]


def _knockout_winner(
    prob_cache: dict[tuple[str, str], MatchProbs],
    team_a: str,
    team_b: str,
    rng: np.random.Generator,
) -> str:
    p_win, _p_draw, p_loss = prob_cache[(team_a, team_b)]
    total = p_win + p_loss
    if total <= 0:
        return team_a if rng.random() < 0.5 else team_b
    return team_a if rng.random() < p_win / total else team_b


def _simulate_group(
    prob_cache: dict[tuple[str, str], MatchProbs],
    teams: list[str],
    rng: np.random.Generator,
) -> list[GroupStanding]:
    standings = {t: GroupStanding(team=t) for t in teams}
    for home, away in combinations(teams, 2):
        hs, as_ = _sample_group_score(prob_cache, home, away, rng)
        _apply_result(standings, home, away, hs, as_)
    return _rank_group(list(standings.values()))


def _seed_knockout(qualified: list[tuple[str, GroupStanding]]) -> list[str]:
    return [
        team
        for team, _ in sorted(
            qualified,
            key=lambda x: (x[1].points, x[1].goal_diff, x[1].goals_for, x[0]),
            reverse=True,
        )
    ]


def simulate_tournament_once(
    prob_cache: dict[tuple[str, str], MatchProbs],
    groups: dict[str, list[str]],
    rng: np.random.Generator,
    fmt: TournamentFormat = DEFAULT_FORMAT,
) -> tuple[str, str, dict[str, list[str]]]:
    qualified: list[tuple[str, GroupStanding]] = []
    thirds: list[tuple[str, GroupStanding]] = []
    group_tables: dict[str, list[str]] = {}

    for letter, teams in groups.items():
        ranked = _simulate_group(prob_cache, teams, rng)
        group_tables[letter] = [s.team for s in ranked]
        qualified.append((ranked[0].team, ranked[0]))
        qualified.append((ranked[1].team, ranked[1]))
        thirds.append((ranked[2].team, ranked[2]))

    for team in _rank_third_placed(thirds, fmt.third_place_advancing):
        standing = next(s for t, s in thirds if t == team)
        qualified.append((team, standing))

    bracket = _seed_knockout(qualified)
    while len(bracket) > 2:
        next_round: list[str] = []
        for i in range(0, len(bracket), 2):
            winner = _knockout_winner(prob_cache, bracket[i], bracket[i + 1], rng)
            next_round.append(winner)
        bracket = next_round

    champion = _knockout_winner(prob_cache, bracket[0], bracket[1], rng)
    runner_up = bracket[1] if champion == bracket[0] else bracket[0]
    return champion, runner_up, group_tables


def _run_simulation_batch(
    batch_size: int,
    seed: int,
    prob_cache: dict[tuple[str, str], MatchProbs],
    groups: dict[str, list[str]],
) -> tuple[dict[str, int], dict[str, int], dict[str, dict[str, int]]]:
    rng = np.random.default_rng(seed)
    champion_counts: dict[str, int] = defaultdict(int)
    finalist_counts: dict[str, int] = defaultdict(int)
    group_win_counts: dict[str, dict[str, int]] = {letter: defaultdict(int) for letter in groups}

    for _ in range(batch_size):
        champion, runner_up, tables = simulate_tournament_once(prob_cache, groups, rng)
        champion_counts[champion] += 1
        finalist_counts[runner_up] += 1
        for letter, ranking in tables.items():
            group_win_counts[letter][ranking[0]] += 1

    return (
        dict(champion_counts),
        dict(finalist_counts),
        {k: dict(v) for k, v in group_win_counts.items()},
    )


class SimulationEngine:
    """Monte Carlo tournament simulation with multiprocessing."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def run(
        self,
        n_simulations: int = 500,
        *,
        seed: int | None = None,
        model_path: Path | None = None,
        features_path: Path | None = None,
        groups_path: Path | None = None,
        workers: int | None = None,
        tournament_format: TournamentFormat = DEFAULT_FORMAT,
    ) -> SimulationResult:
        seed = seed if seed is not None else self.settings.random_seed
        set_global_seed(seed)
        groups = load_wc2026_groups(groups_path)
        teams = all_wc2026_teams(groups)

        features = pd.read_parquet(features_path or self.settings.features_parquet)
        features["date"] = pd.to_datetime(features["date"])
        snapshots = _load_snapshots(features, teams)
        pipeline = joblib.load(model_path or self.settings.model_path)
        prob_cache = build_match_probability_cache(pipeline, snapshots, teams)

        workers = workers or min(self.settings.simulation_workers, cpu_count())
        batch_size = max(1, n_simulations // workers)
        batches = [batch_size] * workers
        batches[-1] += n_simulations - sum(batches)

        champion_total: dict[str, int] = defaultdict(int)
        finalist_total: dict[str, int] = defaultdict(int)
        group_total: dict[str, dict[str, int]] = {letter: defaultdict(int) for letter in groups}

        if workers > 1 and n_simulations >= workers * 10:
            with ProcessPoolExecutor(max_workers=workers) as executor:
                futures = [
                    executor.submit(_run_simulation_batch, bs, seed + i, prob_cache, groups)
                    for i, bs in enumerate(batches)
                    if bs > 0
                ]
                for future in futures:
                    ch, fi, gr = future.result()
                    for k, v in ch.items():
                        champion_total[k] += v
                    for k, v in fi.items():
                        finalist_total[k] += v
                    for letter, counts in gr.items():
                        for team, count in counts.items():
                            group_total[letter][team] += count
        else:
            ch, fi, gr = _run_simulation_batch(n_simulations, seed, prob_cache, groups)
            champion_total.update(ch)
            finalist_total.update(fi)
            for letter, counts in gr.items():
                group_total[letter].update(counts)

        champion_probs = dict(
            sorted(
                ((t, champion_total.get(t, 0) / n_simulations) for t in teams), key=lambda x: -x[1]
            )
        )
        finalist_probs = dict(
            sorted(
                ((t, finalist_total.get(t, 0) / n_simulations) for t in teams), key=lambda x: -x[1]
            )
        )
        group_winner_probs = {
            letter: {
                team: group_total[letter].get(team, 0) / n_simulations for team in groups[letter]
            }
            for letter in groups
        }

        logger.info("simulation_complete", n_simulations=n_simulations, seed=seed)
        return SimulationResult(
            n_simulations=n_simulations,
            champion_probs=champion_probs,
            finalist_probs=finalist_probs,
            group_winner_probs=group_winner_probs,
            seed=seed,
        )


def run_monte_carlo(
    n_simulations: int = 2000,
    *,
    model_path: Path | None = None,
    features_path: Path | None = None,
    groups_path: Path | None = None,
    seed: int = 42,
) -> SimulationResult:
    """Backward-compatible entry point."""
    return SimulationEngine().run(
        n_simulations=n_simulations,
        seed=seed,
        model_path=model_path,
        features_path=features_path,
        groups_path=groups_path,
    )
