"""MLflow Model Registry integration for champion promotion."""

from __future__ import annotations

from typing import Any

import mlflow
from mlflow.entities.model_registry import ModelVersion
from mlflow.tracking import MlflowClient

from src.config.settings import get_settings
from src.utils.exceptions import ModelNotFoundError
from src.utils.logging import get_logger

logger = get_logger(__name__)

STAGE_PRODUCTION = "Production"
STAGE_STAGING = "Staging"
STAGE_ARCHIVED = "Archived"


def _client() -> MlflowClient:
    settings = get_settings()
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    if settings.mlflow_registry_uri:
        mlflow.set_registry_uri(settings.mlflow_registry_uri)
    return MlflowClient(tracking_uri=settings.mlflow_tracking_uri)


def _latest_run_with_model(client: MlflowClient, experiment_name: str) -> str | None:
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        return None
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="attributes.status = 'FINISHED'",
        order_by=["attributes.start_time DESC"],
        max_results=20,
    )
    for run in runs:
        artifacts = [a.path for a in client.list_artifacts(run.info.run_id)]
        if "model" in artifacts or any(a.endswith("model.joblib") for a in artifacts):
            return str(run.info.run_id)
    return None


def register_champion_model(
    *,
    run_id: str | None = None,
    model_uri: str | None = None,
    model_name: str | None = None,
) -> ModelVersion:
    """Register champion model in MLflow Model Registry and promote to Production."""
    settings = get_settings()
    client = _client()
    name = model_name or settings.champion_model_name

    if model_uri is None:
        resolved_run = run_id or _latest_run_with_model(client, settings.mlflow_experiment_name)
        if resolved_run is None:
            raise ModelNotFoundError("No MLflow run with a model artifact found")
        model_uri = f"runs:/{resolved_run}/model"

    version = mlflow.register_model(model_uri, name)
    client.transition_model_version_stage(
        name=name,
        version=version.version,
        stage=STAGE_PRODUCTION,
        archive_existing_versions=True,
    )
    logger.info(
        "mlflow_model_registered",
        model_name=name,
        version=version.version,
        stage=STAGE_PRODUCTION,
        source=model_uri,
    )
    return version


def promote_model_version(model_name: str, version: str, *, stage: str = STAGE_PRODUCTION) -> None:
    """Promote a registered model version to the given stage."""
    client = _client()
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage=stage,
        archive_existing_versions=stage == STAGE_PRODUCTION,
    )
    logger.info("mlflow_model_promoted", model_name=model_name, version=version, stage=stage)


def get_production_model_version(model_name: str | None = None) -> ModelVersion | None:
    """Return the current Production stage model version, if any."""
    settings = get_settings()
    client = _client()
    name = model_name or settings.champion_model_name
    for version in client.search_model_versions(f"name='{name}'"):
        if version.current_stage == STAGE_PRODUCTION:
            return version
    return None


def registry_summary() -> dict[str, Any]:
    """Summarize registry state for verification scripts."""
    settings = get_settings()
    client = _client()
    models = client.search_registered_models()
    production = get_production_model_version()
    return {
        "tracking_uri": settings.mlflow_tracking_uri,
        "registry_uri": settings.mlflow_registry_uri or settings.mlflow_tracking_uri,
        "registered_model_count": len(models),
        "production_model": production.name if production else None,
        "production_version": production.version if production else None,
    }


def ensure_champion_registered(*, run_id: str | None = None) -> ModelVersion:
    """Register champion if no Production model exists; otherwise return existing."""
    existing = get_production_model_version()
    if existing is not None:
        logger.info(
            "mlflow_production_model_exists",
            model_name=existing.name,
            version=existing.version,
        )
        return existing
    champion_path = get_settings().model_path
    if not champion_path.exists():
        raise ModelNotFoundError(f"Champion model file not found: {champion_path}")
    return register_champion_model(run_id=run_id)
