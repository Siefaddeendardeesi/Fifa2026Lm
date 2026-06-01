"""Application settings with pydantic-settings and environment support."""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Central configuration — all paths derived from project root."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app_name: str = "FIFA World Cup 2026 Prediction Platform"
    app_version: str = "1.0.0"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    log_level: str = "INFO"
    log_json: bool = False
    random_seed: int = 42

    project_root: Path = Field(default_factory=_project_root)
    data_dir: Path = Field(default_factory=lambda: _project_root() / "data")
    raw_dir: Path = Field(default_factory=lambda: _project_root() / "data" / "raw")
    processed_dir: Path = Field(default_factory=lambda: _project_root() / "data" / "processed")
    reference_dir: Path = Field(default_factory=lambda: _project_root() / "data" / "reference")
    features_dir: Path = Field(
        default_factory=lambda: _project_root() / "data" / "processed" / "features"
    )
    models_dir: Path = Field(
        default_factory=lambda: _project_root() / "data" / "processed" / "models"
    )
    reports_dir: Path = Field(
        default_factory=lambda: _project_root() / "data" / "processed" / "reports"
    )
    cache_dir: Path = Field(default_factory=lambda: _project_root() / "data" / "cache")
    metadata_dir: Path = Field(default_factory=lambda: _project_root() / "data" / "metadata")
    model_registry_path: Path = Field(
        default_factory=lambda: _project_root() / "data" / "processed" / "models" / "registry"
    )

    train_cutoff: str = "2022-01-01"
    test_start: str = "2022-01-01"
    form_window: int = 10
    min_match_date: str = "1992-01-01"

    mlflow_tracking_uri: str = "file:./mlruns"
    mlflow_experiment_name: str = "fifa2026-match-outcome"
    mlflow_registry_uri: str | None = None

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    api_rate_limit: str = "100/minute"
    api_cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    streamlit_port: int = 8501

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "fifa2026"
    postgres_password: str = "fifa2026"
    postgres_db: str = "fifa2026"

    kaggle_username: str | None = None
    kaggle_key: str | None = None
    apify_token: str | None = None

    dvc_remote: str = "localstorage"
    dvc_remote_url: str = "./dvc-storage"

    prometheus_port: int = 9090
    grafana_port: int = 3000
    grafana_admin_user: str = "admin"
    grafana_admin_password: str = Field(default="changeme", min_length=8)
    simulation_workers: int = 4
    simulation_default_runs: int = 500

    champion_model_name: str = "champion"
    etl_max_retries: int = 3
    etl_retry_backoff: float = 2.0
    etl_cache_enabled: bool = True

    @field_validator("environment", mode="before")
    @classmethod
    def normalize_env(cls, v: str | Environment) -> Environment:
        if isinstance(v, Environment):
            return v
        mapping = {
            "dev": Environment.DEVELOPMENT,
            "development": Environment.DEVELOPMENT,
            "test": Environment.TEST,
            "testing": Environment.TEST,
            "staging": Environment.STAGING,
            "stage": Environment.STAGING,
            "prod": Environment.PRODUCTION,
            "production": Environment.PRODUCTION,
        }
        return mapping.get(str(v).lower(), Environment.DEVELOPMENT)

    @property
    def results_csv(self) -> Path:
        return self.raw_dir / "results.csv"

    @property
    def elo_csv(self) -> Path:
        return self.raw_dir / "elo.csv"

    @property
    def fjelstul_dir(self) -> Path:
        return self.raw_dir / "fjelstul"

    @property
    def mapping_csv(self) -> Path:
        return self.reference_dir / "mapping.csv"

    @property
    def squads_json(self) -> Path:
        return self.reference_dir / "wc2026_squads.json"

    @property
    def groups_json(self) -> Path:
        return self.reference_dir / "wc2026_groups.json"

    @property
    def features_parquet(self) -> Path:
        return self.processed_dir / "features.parquet"

    @property
    def train_parquet(self) -> Path:
        return self.processed_dir / "train.parquet"

    @property
    def test_parquet(self) -> Path:
        return self.processed_dir / "test.parquet"

    @property
    def model_path(self) -> Path:
        champion = self.models_dir / "champion_model.joblib"
        baseline = self.processed_dir / "baseline_model.joblib"
        if champion.exists():
            return champion
        return baseline

    @property
    def unmapped_log(self) -> Path:
        return self.processed_dir / "unmapped_teams.log"

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    @property
    def is_test(self) -> bool:
        return self.environment == Environment.TEST

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


def get_settings_for_env(env: Literal["development", "test", "staging", "production"]) -> Settings:
    """Factory for environment-specific settings."""
    if env == "development":
        return Settings(environment=Environment.DEVELOPMENT, debug=True, log_level="DEBUG")
    if env == "test":
        return Settings(
            environment=Environment.TEST,
            debug=True,
            log_level="DEBUG",
            log_json=False,
            etl_cache_enabled=False,
        )
    if env == "staging":
        return Settings(
            environment=Environment.STAGING,
            debug=False,
            log_level="INFO",
            log_json=True,
        )
    return Settings(
        environment=Environment.PRODUCTION,
        debug=False,
        log_level="WARNING",
        log_json=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
