# Data Dictionary

## Raw Data

### results.csv
International match results (martj42 / Kaggle).

| Column | Type | Description |
|--------|------|-------------|
| date | datetime | Match date |
| home_team | string | Home nation (canonical name) |
| away_team | string | Away nation |
| home_score | int | Home goals (≥ 0) |
| away_score | int | Away goals (≥ 0) |
| neutral | bool | Neutral venue flag |
| tournament | string | Competition name |
| city | string | Host city |
| country | string | Host country |

### elo.csv
Point-in-time ELO ratings from eloratings.net.

| Column | Type | Description |
|--------|------|-------------|
| date | datetime | Rating date |
| team | string | Nation |
| elo | float | ELO rating (800–2500) |

### fifa_ranking*.csv
FIFA world ranking history.

| Column | Type | Description |
|--------|------|-------------|
| rank_date | datetime | Ranking publication date |
| team | string | Nation |
| rank | float | FIFA rank (≥ 1) |
| total_points | float | Ranking points |
| confederation | string | UEFA, CONMEBOL, CONCACAF, CAF, AFC, OFC |

### fjelstul/*.csv
World Cup database (teams, tournaments, qualified teams, matches).

## Processed Data

### features.parquet
Match-level feature matrix for ML training.

| Column | Type | Description |
|--------|------|-------------|
| date | datetime | Match date |
| home_team, away_team | string | Teams |
| home_elo, away_elo | float | Pre-match ELO |
| elo_diff | float | home_elo − away_elo |
| home_fifa_rank, away_fifa_rank | float | Pre-match FIFA rank |
| fifa_rank_diff | float | Rank difference |
| home/away_confederation | string | Confederation code |
| home/away_form_*_10 | float | Rolling 10-match form stats |
| home/away_squad_value | float | Transfermarkt squad value |
| home/away_wc_titles | int | Prior World Cup titles |
| neutral | bool | Neutral venue |
| result | string | Win / Draw / Loss (home perspective) |

## Reference Data

### wc2026_groups.json
Official 2026 draw: 12 groups × 4 teams (48 total).

### wc2026_squads.json
Announced squad rosters with player details.

### mapping.csv
Raw → canonical team name mapping.
