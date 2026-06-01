#!/usr/bin/env python3
"""CLI: Monte Carlo simulation of FIFA World Cup 2026."""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PROCESSED_DIR  # noqa: E402
from src.models.tournament import (  # noqa: E402
    all_wc2026_teams,
    load_wc2026_groups,
    run_monte_carlo,
)


def _print_groups(groups: dict[str, list[str]]) -> None:
    print("\n=== 48 teams / 12 groups (FIFA 2026 draw) ===\n")
    for letter in sorted(groups):
        teams = ", ".join(groups[letter])
        print(f"  Group {letter}: {teams}")


def _print_champion_probs(result, top: int) -> None:
    print(f"\n=== Cup winner probability (top {top}) ===")
    print(f"  ({result.n_simulations:,} simulations)\n")
    for i, (team, prob) in enumerate(result.champion_probs.items()):
        if i >= top:
            break
        bar = "#" * int(prob * 40)
        print(f"  {i + 1:2}. {team:<28} {prob * 100:5.1f}%  {bar}")


def _print_group_favorites(result, top_per_group: int = 2) -> None:
    print("\n=== Most likely group winners ===\n")
    for letter in sorted(result.group_winner_probs):
        ranked = sorted(
            result.group_winner_probs[letter].items(),
            key=lambda x: -x[1],
        )
        fav = ranked[0]
        second = ranked[1] if len(ranked) > 1 else ("—", 0)
        print(
            f"  Group {letter}: {fav[0]} ({fav[1] * 100:.0f}%)  |  "
            f"2nd: {second[0]} ({second[1] * 100:.0f}%)"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate FIFA World Cup 2026 (groups + knockout)")
    parser.add_argument(
        "--simulations",
        type=int,
        default=2000,
        help="Number of Monte Carlo runs (default: 2000)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=15,
        help="How many teams to show for title odds",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--list-teams",
        action="store_true",
        help="Print official groups and exit",
    )
    args = parser.parse_args()

    groups = load_wc2026_groups()
    if args.list_teams:
        _print_groups(groups)
        print(f"\nTotal: {len(all_wc2026_teams(groups))} teams")
        return

    _print_groups(groups)
    print(f"\nBuilding match probabilities for 48 teams, then {args.simulations:,} simulations...")

    result = run_monte_carlo(n_simulations=args.simulations, seed=args.seed)

    _print_champion_probs(result, args.top)
    _print_group_favorites(result)

    out_json = PROCESSED_DIR / "wc2026_simulation.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"\nFull results saved to {out_json}")
    print(
        "\nNote: Knockout bracket uses strength-based seeding (simplified), "
        "not the exact FIFA match schedule."
    )


if __name__ == "__main__":
    main()
