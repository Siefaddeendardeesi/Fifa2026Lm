"""Pydantic request/response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    model_loaded: bool


class PredictRequest(BaseModel):
    home_team: str = Field(..., min_length=1, max_length=100)
    away_team: str = Field(..., min_length=1, max_length=100)
    neutral: bool = True


class PredictResponse(BaseModel):
    home_team: str
    away_team: str
    home_win: float
    draw: float
    away_win: float
    confidence: float


class SimulateRequest(BaseModel):
    n_simulations: int = Field(default=500, ge=10, le=10000)
    seed: int = Field(default=42, ge=0)


class SimulateResponse(BaseModel):
    n_simulations: int
    seed: int
    champion_probability: dict[str, float]
    finalist_probability: dict[str, float]
    group_winner_probability: dict[str, dict[str, float]]


class RankingsRequest(BaseModel):
    method: str = Field(default="model", pattern="^(elo|model|hybrid)$")
    since: str = "2024-01-01"
    pool_size: int = Field(default=48, ge=2, le=48)


class RankingEntry(BaseModel):
    rank: int
    team: str
    score: float | None = None
    avg_win_prob: float | None = None
    elo: float | None = None
    fifa_rank: float | None = None


class RankingsResponse(BaseModel):
    method: str
    pool_size: int
    rankings: list[RankingEntry]


class TeamInfo(BaseModel):
    name: str
    group: str | None = None
    has_squad: bool = False


class TeamsResponse(BaseModel):
    teams: list[TeamInfo]
    count: int


class GroupsResponse(BaseModel):
    groups: dict[str, list[str]]
    group_count: int
    team_count: int


class ErrorResponse(BaseModel):
    error: str
    details: dict[str, Any] | None = None
