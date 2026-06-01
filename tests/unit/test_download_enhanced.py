"""Tests for enhanced download retry and caching."""

from __future__ import annotations

from pathlib import Path

import pytest
import requests

from src.etl import download
from src.utils.exceptions import ETLDownloadError


def test_download_url_cache_hit(mocker, tmp_path: Path, test_settings) -> None:
    dest = tmp_path / "cached.csv"
    dest.write_text("existing", encoding="utf-8")
    get_mock = mocker.patch("src.etl.download.requests.get")
    download._download_url("http://example.com/x", dest)
    get_mock.assert_not_called()


def test_download_url_retries_on_failure(mocker, tmp_path: Path, test_settings) -> None:
    mocker.patch(
        "src.etl.download.requests.get",
        side_effect=requests.ConnectionError("network"),
    )
    dest = tmp_path / "fail.csv"
    with pytest.raises(ETLDownloadError):
        download._download_url("http://example.com/x", dest)


def test_download_fjelstul_file_skips_existing(mocker, tmp_path: Path, monkeypatch) -> None:
    fj_dir = tmp_path / "fjelstul"
    fj_dir.mkdir()
    (fj_dir / "teams.csv").write_text("x", encoding="utf-8")
    monkeypatch.setattr(download, "FJELSTUL_DIR", fj_dir)
    url_mock = mocker.patch("src.etl.download._download_url")
    download._download_fjelstul_file("teams.csv")
    url_mock.assert_not_called()


def test_download_fjelstul_file_downloads(mocker, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(download, "FJELSTUL_DIR", tmp_path / "fjelstul")
    url_mock = mocker.patch("src.etl.download._download_url")
    download._download_fjelstul_file("matches.csv")
    url_mock.assert_called_once()


def test_download_fjelstul_csvs(mocker, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(download, "FJELSTUL_DIR", tmp_path / "fjelstul")
    file_mock = mocker.patch("src.etl.download._download_fjelstul_file")
    download.download_fjelstul_csvs()
    assert file_mock.call_count == len(download.FJELSTUL_FILES)


def test_find_and_copy_results(mocker, tmp_path: Path, monkeypatch) -> None:
    raw = tmp_path / "raw"
    nested = raw / "sub"
    nested.mkdir(parents=True)
    src = nested / "results.csv"
    src.write_text("data", encoding="utf-8")
    dest = raw / "results.csv"
    monkeypatch.setattr(download, "RAW_DIR", raw)
    download._find_and_copy_results(dest)
    assert dest.exists()
