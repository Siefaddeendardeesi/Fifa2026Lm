"""Project-wide constants and column definitions."""

from __future__ import annotations

FORM_WINDOW = 10

TRAIN_CUTOFF_DEFAULT = "2022-01-01"
TEST_START_DEFAULT = "2022-01-01"
TRAIN_CUTOFF_WC2022 = "2022-11-01"
TEST_START_WC2022 = "2022-11-20"

FINAL_COLUMNS = [
    "date",
    "home_team",
    "away_team",
    "home_elo",
    "away_elo",
    "elo_diff",
    "home_fifa_rank",
    "away_fifa_rank",
    "fifa_rank_diff",
    "home_confederation",
    "away_confederation",
    "home_form_wins_10",
    "home_form_draws_10",
    "home_form_losses_10",
    "home_form_goals_for_10",
    "home_form_goals_against_10",
    "home_form_clean_sheets_10",
    "away_form_wins_10",
    "away_form_draws_10",
    "away_form_losses_10",
    "away_form_goals_for_10",
    "away_form_goals_against_10",
    "away_form_clean_sheets_10",
    "home_form_points_10",
    "away_form_points_10",
    "home_form_goal_diff_10",
    "away_form_goal_diff_10",
    "home_form_win_rate_10",
    "away_form_win_rate_10",
    "home_squad_value",
    "away_squad_value",
    "home_wc_titles",
    "away_wc_titles",
    "neutral",
    "result",
]

TARGET_LABELS: dict[str, int] = {"Win": 0, "Draw": 1, "Loss": 2}
LABEL_NAMES = ["Win (home)", "Draw", "Loss (home)"]

FEATURE_COLS = [c for c in FINAL_COLUMNS if c not in ("date", "home_team", "away_team", "result")]
NUMERIC_COLS = [
    c for c in FEATURE_COLS if c not in ("neutral", "home_confederation", "away_confederation")
]
CATEGORICAL_COLS = ["neutral", "home_confederation", "away_confederation"]

VALID_CONFEDERATIONS = {"UEFA", "CONMEBOL", "CONCACAF", "CAF", "AFC", "OFC"}

FJELSTUL_FILES = [
    "matches.csv",
    "teams.csv",
    "tournaments.csv",
    "qualified_teams.csv",
    "manager_appearances.csv",
    "tournament_standings.csv",
]

KAGGLE_DATASETS = {
    "results": "martj42/international-football-results-from-1872-to-2017",
    "fifa_ranking": "cashncarry/fifaworldranking",
    "wc_1930_2022": "jahaidulislam/fifa-world-cup-1930-2022-all-match-dataset",
    "wc_1930_2018": "evangower/fifa-world-cup",
    "fifa_ranking_alt": "lucasyukioimafuko/fifa-mens-world-ranking",
}

ELO_URL = "https://www.eloratings.net/World.tsv"
FJELSTUL_BASE_URL = "https://raw.githubusercontent.com/jfjelstul/worldcup/master/data-csv"

WC2026_TEAM_COUNT = 48
WC2026_GROUP_COUNT = 12
WC2026_KNOCKOUT_TEAMS = 32
HOSTS = {"Mexico", "Canada", "United States"}

MODEL_TYPES = [
    "logistic_regression",
    "random_forest",
    "xgboost",
    "lightgbm",
    "catboost",
]
