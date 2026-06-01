"""Application services layer."""

from __future__ import annotations

import json
from typing import Any

import joblib
import pandas as pd

from app.schemas.api import (
    GroupsResponse,
    PredictResponse,
    RankingEntry,
    RankingsResponse,
    SimulateResponse,
    TeamInfo,
    TeamsResponse,
)
from src.config.settings import get_settings
from src.etl.squads import get_team_squad, teams_with_squads
from src.models.registry import ModelRegistry
from src.rankings.engine import RankingEngine, RankingMethod
from src.rankings.predictor import extract_team_snapshot, predict_match_proba
from src.simulation.engine import SimulationEngine, all_wc2026_teams, load_wc2026_groups
from src.utils.exceptions import NotFoundError
from src.utils.logging import get_logger

logger = get_logger(__name__)


class PredictionService:
    """Match prediction service."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._pipeline: Any = None
        self._features: pd.DataFrame | None = None

    @property
    def pipeline(self) -> Any:
        if self._pipeline is None:
            if self.settings.model_path.exists():
                self._pipeline = joblib.load(self.settings.model_path)
            else:
                registry = ModelRegistry()
                self._pipeline = registry.load_champion()
        return self._pipeline

    @property
    def features(self) -> pd.DataFrame:
        if self._features is None:
            self._features = pd.read_parquet(self.settings.features_parquet)
            self._features["date"] = pd.to_datetime(self._features["date"])
        return self._features

    def is_ready(self) -> bool:
        return self.settings.model_path.exists() or self.settings.features_parquet.exists()

    def predict(self, home_team: str, away_team: str, *, neutral: bool = True) -> PredictResponse:
        hs = extract_team_snapshot(self.features, home_team)
        aws = extract_team_snapshot(self.features, away_team)
        if hs is None:
            raise NotFoundError(f"No feature data for team: {home_team}")
        if aws is None:
            raise NotFoundError(f"No feature data for team: {away_team}")

        w, d, loss_prob = predict_match_proba(self.pipeline, hs, aws, neutral=neutral)
        confidence = max(w, d, loss_prob)
        logger.info("prediction_made", home=home_team, away=away_team, confidence=confidence)
        return PredictResponse(
            home_team=home_team,
            away_team=away_team,
            home_win=w,
            draw=d,
            away_win=loss_prob,
            confidence=confidence,
        )


class SimulationService:
    """Tournament simulation service."""

    def __init__(self) -> None:
        self.engine = SimulationEngine()
        self.settings = get_settings()

    def simulate(self, n_simulations: int = 500, seed: int = 42) -> SimulateResponse:
        result = self.engine.run(n_simulations=n_simulations, seed=seed)
        out_path = self.settings.processed_dir / "wc2026_simulation.json"
        out_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
        return SimulateResponse(
            n_simulations=result.n_simulations,
            seed=result.seed,
            champion_probability=result.champion_probs,
            finalist_probability=result.finalist_probs,
            group_winner_probability=result.group_winner_probs,
        )


class RankingsService:
    """Team rankings service."""

    def __init__(self) -> None:
        self.engine = RankingEngine()

    def get_rankings(
        self,
        method: str = "model",
        since: str = "2024-01-01",
        pool_size: int = 48,
    ) -> RankingsResponse:
        method_enum = RankingMethod(method)
        df = self.engine.compute(method=method_enum, since=since, pool_size=pool_size)
        entries: list[RankingEntry] = []
        for _, row in df.iterrows():
            score = row.get("hybrid_score") or row.get("avg_win_prob") or row.get("elo_score")
            entries.append(
                RankingEntry(
                    rank=int(row["rank"]),
                    team=str(row["team"]),
                    score=float(score) if pd.notna(score) else None,
                    avg_win_prob=(
                        float(row["avg_win_prob"])
                        if "avg_win_prob" in row and pd.notna(row["avg_win_prob"])
                        else None
                    ),
                    elo=float(row["elo"]) if "elo" in row and pd.notna(row.get("elo")) else None,
                    fifa_rank=(
                        float(row["fifa_rank"])
                        if "fifa_rank" in row and pd.notna(row.get("fifa_rank"))
                        else None
                    ),
                )
            )
        return RankingsResponse(method=method, pool_size=pool_size, rankings=entries)


class TeamsService:
    """Teams and groups service."""

    def get_groups(self) -> GroupsResponse:
        groups = load_wc2026_groups()
        teams = all_wc2026_teams(groups)
        return GroupsResponse(groups=groups, group_count=len(groups), team_count=len(teams))

    def get_teams(self) -> TeamsResponse:
        groups = load_wc2026_groups()
        squads = set(teams_with_squads())
        team_infos: list[TeamInfo] = []
        for letter, group_teams in groups.items():
            for team in group_teams:
                team_infos.append(TeamInfo(name=team, group=letter, has_squad=team in squads))
        team_infos.sort(key=lambda t: t.name)
        return TeamsResponse(teams=team_infos, count=len(team_infos))

    def get_squad(self, team: str) -> dict[str, Any]:
        squad = get_team_squad(team)
        if squad is None:
            raise NotFoundError(f"Squad not found for team: {team}")
        return squad
