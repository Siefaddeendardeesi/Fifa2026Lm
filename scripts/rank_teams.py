#!/usr/bin/env python3
"""CLI: rank national teams by model-based win probability."""

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PROCESSED_DIR  # noqa: E402
from src.models.ranking import rank_teams  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rank teams by average predicted win probability (baseline model)"
    )
    parser.add_argument(
        "--since",
        default="2024-01-01",
        help="Only include teams with a match on or after this date",
    )
    parser.add_argument(
        "--pool",
        type=int,
        default=48,
        help="Max teams in comparison pool (by FIFA rank, then ELO)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of teams to print",
    )
    parser.add_argument(
        "--home-advantage",
        action="store_true",
        help="Treat matches as non-neutral (default: neutral venue)",
    )
    args = parser.parse_args()

    rankings = rank_teams(
        since=args.since,
        pool_size=args.pool,
        neutral=not args.home_advantage,
    )

    out_path = PROCESSED_DIR / "team_rankings.csv"
    rankings.to_csv(out_path, index=False)

    print("\n=== Top teams by model win probability ===")
    print(
        f"(Pool: {args.pool} teams active since {args.since}; "
        f"neutral={'yes' if not args.home_advantage else 'no'})\n"
    )
    display = rankings.head(args.top)
    for _, row in display.iterrows():
        rank = int(row["rank"])
        team = row["team"]
        win_pct = row["avg_win_prob"] * 100
        fifa = row["fifa_rank"]
        elo = row["elo"]
        fifa_s = f"{int(fifa)}" if pd.notna(fifa) else "—"
        elo_s = f"{elo:.0f}" if pd.notna(elo) else "—"
        print(f"{rank:2}. {team:<28} win ~{win_pct:5.1f}%   FIFA #{fifa_s}   ELO {elo_s}")

    print(f"\nFull rankings saved to {out_path}")
    print(
        "\nNote: This ranks expected match wins vs other strong teams — "
        "not a full World Cup tournament simulation."
    )


if __name__ == "__main__":
    main()
