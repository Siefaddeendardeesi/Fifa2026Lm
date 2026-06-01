"""Configuration package."""

from src.config.constants import (
    CATEGORICAL_COLS,
    FEATURE_COLS,
    FINAL_COLUMNS,
    FJELSTUL_FILES,
    FORM_WINDOW,
    HOSTS,
    KAGGLE_DATASETS,
    LABEL_NAMES,
    MODEL_TYPES,
    NUMERIC_COLS,
    TARGET_LABELS,
    TEST_START_DEFAULT,
    TEST_START_WC2022,
    TRAIN_CUTOFF_DEFAULT,
    TRAIN_CUTOFF_WC2022,
    WC2026_GROUP_COUNT,
    WC2026_KNOCKOUT_TEAMS,
    WC2026_TEAM_COUNT,
)
from src.config.settings import Environment, Settings, get_settings, get_settings_for_env

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
ELO_URL = "http://elofootball.com/World/World.csv"
FJELSTUL_BASE_URL = "https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv"

__all__ = [
    "DATA_DIR",
    "ELO_CSV",
    "ELO_URL",
    "FEATURES_PARQUET",
    "FJELSTUL_BASE_URL",
    "FJELSTUL_DIR",
    "MANAGERS_DIR",
    "MAPPING_CSV",
    "MODEL_PATH",
    "PROCESSED_DIR",
    "PROJECT_ROOT",
    "RAW_DIR",
    "REFERENCE_DIR",
    "RESULTS_CSV",
    "SQUADS_JSON",
    "TEST_PARQUET",
    "TRAIN_PARQUET",
    "TRANSFERMARKT_CSV",
    "UNMAPPED_LOG",
    "FIFA_RANKING_GLOB",
    "CATEGORICAL_COLS",
    "Environment",
    "FEATURE_COLS",
    "FINAL_COLUMNS",
    "FJELSTUL_FILES",
    "FORM_WINDOW",
    "HOSTS",
    "KAGGLE_DATASETS",
    "LABEL_NAMES",
    "MODEL_TYPES",
    "NUMERIC_COLS",
    "Settings",
    "TARGET_LABELS",
    "TEST_START_DEFAULT",
    "TEST_START_WC2022",
    "TRAIN_CUTOFF_DEFAULT",
    "TRAIN_CUTOFF_WC2022",
    "WC2026_GROUP_COUNT",
    "WC2026_KNOCKOUT_TEAMS",
    "WC2026_TEAM_COUNT",
    "get_settings",
    "get_settings_for_env",
]
