# Feature Catalog

Version: **1.0.0**

## Registered Transformers

| Name | Version | Output Columns |
|------|---------|----------------|
| form_features | 1.0.0 | home/away_form_{wins,draws,losses,goals_for,goals_against,clean_sheets,points,goal_diff,win_rate}_10 |
| wc_features | 1.0.0 | home_wc_titles, away_wc_titles |
| elo_features | 1.0.0 | home_elo, away_elo, elo_diff |
| ranking_features | 1.0.0 | home/away_fifa_rank, fifa_rank_diff, home/away_confederation |

## Feature Definitions

### ELO (`elo_features`)
Chronological ELO replay or backward as-of join from historical ratings. Captures relative team strength.

### FIFA Rank (`ranking_features`)
Most recent FIFA rank before match date via backward as-of join. Confederation from ranking or Fjelstul fallback.

### Form (`form_features`)
Rolling sum/rate over last 10 matches per team, shifted to exclude current match (no leakage).

### World Cup Titles (`wc_features`)
Count of prior WC titles before match date from Fjelstul tournament history.

### Squad Value
Optional Transfermarkt squad market value (backward as-of join). NaN when unavailable.

## Lineage

Feature lineage is persisted to `data/metadata/feature_lineage.json` after each build, recording transformer chain, version, row count, and output schema.

## Adding Features

1. Subclass `FeatureTransformer` in `src/features/store.py`
2. Register in `get_default_registry()`
3. Add columns to `src/config/constants.py` → `FINAL_COLUMNS`
4. Update Pandera schema in `src/etl/validation.py`
5. Retrain model — no changes to model interface required
