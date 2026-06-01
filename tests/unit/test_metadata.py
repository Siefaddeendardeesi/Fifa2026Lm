"""Tests for src.etl.metadata."""

from __future__ import annotations

from pathlib import Path

from src.etl.metadata import MetadataStore


def test_metadata_record_source(tmp_path: Path, test_settings) -> None:
    store = MetadataStore(path=tmp_path / "meta.json")
    f = tmp_path / "source.csv"
    f.write_text("a,b\n1,2\n", encoding="utf-8")
    entry = store.record_source("results", f, version="1.0")
    assert entry["checksum_sha256"] is not None
    assert store.get_source_checksum("results") == entry["checksum_sha256"]


def test_metadata_record_run_truncates(tmp_path: Path, test_settings) -> None:
    store = MetadataStore(path=tmp_path / "meta.json")
    for i in range(105):
        store.record_run("pipe", status="success", duration_seconds=0.1, details={"i": i})
    assert len(store._data["runs"]) == 100


def test_source_changed_detects_new_file(tmp_path: Path, test_settings) -> None:
    store = MetadataStore(path=tmp_path / "meta.json")
    f = tmp_path / "data.csv"
    f.write_text("v1", encoding="utf-8")
    store.record_source("src", f)
    assert store.source_changed("src", f) is False
    f.write_text("v2", encoding="utf-8")
    assert store.source_changed("src", f) is True


def test_source_changed_missing_stored(tmp_path: Path, test_settings) -> None:
    store = MetadataStore(path=tmp_path / "meta.json")
    f = tmp_path / "new.csv"
    f.write_text("x", encoding="utf-8")
    assert store.source_changed("missing", f) is True
