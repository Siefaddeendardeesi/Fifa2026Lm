"""ETL metadata and source version tracking."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from src.config.settings import get_settings
from src.utils.checksum import compute_sha256
from src.utils.logging import get_logger

logger = get_logger(__name__)


class MetadataStore:
    """Persist ETL run metadata and source checksums."""

    def __init__(self, path: Path | None = None) -> None:
        settings = get_settings()
        self.path = path or settings.metadata_dir / "etl_metadata.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if self.path.exists():
            return cast(dict[str, Any], json.loads(self.path.read_text(encoding="utf-8")))
        return {"sources": {}, "runs": []}

    def save(self) -> None:
        self.path.write_text(json.dumps(self._data, indent=2, default=str), encoding="utf-8")

    def record_source(
        self,
        name: str,
        file_path: Path,
        *,
        version: str | None = None,
        url: str | None = None,
    ) -> dict[str, Any]:
        """Record source file metadata with checksum."""
        entry = {
            "name": name,
            "path": str(file_path),
            "checksum_sha256": compute_sha256(file_path) if file_path.exists() else None,
            "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
            "version": version,
            "url": url,
            "updated_at": datetime.now(UTC).isoformat(),
        }
        self._data["sources"][name] = entry
        self.save()
        logger.info("source_recorded", source=name, checksum=entry["checksum_sha256"])
        return entry

    def record_run(
        self,
        pipeline: str,
        *,
        status: str,
        duration_seconds: float,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Record ETL pipeline run."""
        run = {
            "pipeline": pipeline,
            "status": status,
            "duration_seconds": duration_seconds,
            "timestamp": datetime.now(UTC).isoformat(),
            "details": details or {},
        }
        self._data.setdefault("runs", []).append(run)
        if len(self._data["runs"]) > 100:
            self._data["runs"] = self._data["runs"][-100:]
        self.save()
        logger.info("etl_run_recorded", pipeline=pipeline, status=status)

    def get_source_checksum(self, name: str) -> str | None:
        source = self._data.get("sources", {}).get(name, {})
        checksum = source.get("checksum_sha256")
        return str(checksum) if checksum else None

    def source_changed(self, name: str, file_path: Path) -> bool:
        """Check if file checksum differs from stored value."""
        stored = self.get_source_checksum(name)
        if stored is None or not file_path.exists():
            return True
        return compute_sha256(file_path) != stored
