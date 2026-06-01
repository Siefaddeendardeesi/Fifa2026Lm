"""Model registry with champion/challenger and rollback."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import joblib

from src.config.settings import get_settings
from src.utils.exceptions import ModelNotFoundError
from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ModelMetadata:
    """Model version metadata."""

    version: str
    model_type: str
    path: str
    metrics: dict[str, float]
    created_at: str
    status: str = "challenger"
    params: dict[str, Any] | None = None
    run_id: str | None = None


class ModelRegistry:
    """Local model registry with versioning."""

    def __init__(self, registry_path: Path | None = None) -> None:
        settings = get_settings()
        self.registry_path = registry_path or settings.model_registry_path
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.index_path = self.registry_path / "index.json"
        self._index: dict[str, Any] = self._load_index()

    def _load_index(self) -> dict[str, Any]:
        if self.index_path.exists():
            return cast(dict[str, Any], json.loads(self.index_path.read_text(encoding="utf-8")))
        return {"models": [], "champion": None}

    def _save_index(self) -> None:
        self.index_path.write_text(json.dumps(self._index, indent=2), encoding="utf-8")

    def register(
        self,
        model_path: Path,
        *,
        model_type: str,
        metrics: dict[str, float],
        params: dict[str, Any] | None = None,
        run_id: str | None = None,
    ) -> ModelMetadata:
        """Register a new model version."""
        version = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        dest = self.registry_path / f"{model_type}_{version}.joblib"
        shutil.copy2(model_path, dest)

        metadata = ModelMetadata(
            version=version,
            model_type=model_type,
            path=str(dest),
            metrics=metrics,
            created_at=datetime.now(UTC).isoformat(),
            status="challenger",
            params=params,
            run_id=run_id,
        )
        self._index["models"].append(asdict(metadata))
        self._save_index()
        logger.info("model_registered", version=version, model_type=model_type)
        return metadata

    def promote_to_champion(self, version: str) -> ModelMetadata:
        """Promote a model version to champion."""
        model = self._find_model(version)
        if model is None:
            raise ModelNotFoundError(f"Model version not found: {version}")

        for m in self._index["models"]:
            m["status"] = "archived" if m["version"] != version else "champion"

        self._index["champion"] = version
        self._save_index()

        champion_path = get_settings().model_path
        champion_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(model["path"], champion_path)
        logger.info("model_promoted", version=version)
        return ModelMetadata(**model)

    def rollback(self, version: str) -> ModelMetadata:
        """Rollback champion to a previous version."""
        return self.promote_to_champion(version)

    def get_champion(self) -> ModelMetadata | None:
        """Get current champion model metadata."""
        version = self._index.get("champion")
        if version is None:
            return None
        model = self._find_model(version)
        return ModelMetadata(**model) if model else None

    def load_champion(self) -> Any:
        """Load champion model pipeline."""
        settings = get_settings()
        if not settings.model_path.exists():
            champion = self.get_champion()
            if champion is None:
                raise ModelNotFoundError("No champion model available")
            return joblib.load(champion.path)
        return joblib.load(settings.model_path)

    def list_models(self) -> list[ModelMetadata]:
        return [ModelMetadata(**m) for m in self._index.get("models", [])]

    def _find_model(self, version: str) -> dict[str, Any] | None:
        for m in self._index.get("models", []):
            if m["version"] == version:
                return cast(dict[str, Any], m)
        return None
