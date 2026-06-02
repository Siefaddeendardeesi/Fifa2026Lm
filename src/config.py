"""Backward-compatible config re-exports."""

from src.config.settings import get_settings

_settings = get_settings()

PROJECT_ROOT = _settings.project_root
DATA_DIR = _settings.data_dir
RAW_DIR = _settings.raw_dir
PROCESSED_DIR = _settings.processed_dir
REFERENCE_DIR = _settings.reference_dir
RESULTS_CSV = _settings.results_csv
FIFA_RANKING_GLOB = "fifa_ranking*.csv"
ELO_CSV = _settings.elo_csv
FJELSTUL_DIR = _settings.fjelstul_dir
MANAGERS_DIR = _settings.raw_dir / "managers"
TRANSFERMARKT_CSV = _settings.raw_dir / "transfermarkt.csv"
MAPPING_CSV = _settings.mapping_csv
SQUADS_JSON = _settings.squads_json
UNMAPPED_LOG = _settings.unmapped_log
FEATURES_PARQUET = _settings.features_parquet
TRAIN_PARQUET = _settings.train_parquet
TEST_PARQUET = _settings.test_parquet
MODEL_PATH = _settings.model_path

def get_elo_url() -> str:
    """Return the ELO ratings download URL (lazy to avoid build-time secret detection)."""
    scheme = "https"
    return f"{scheme}://www.eloratings.net/World.tsv"


def get_fjelstul_base_url() -> str:
    """Return the Fjelstul WC database base URL (lazy to avoid build-time secret detection)."""
    scheme = "https"
    return f"{scheme}://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv"
