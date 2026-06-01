"""Parse Wikipedia WC 2026 squads text into reference JSON."""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WIKI_TEXT = Path(__file__).resolve().parent / "_wiki_squads.txt"
OUTPUT = PROJECT_ROOT / "data" / "reference" / "wc2026_squads.json"

POS_MAP = {"1 GK": "GK", "2 DF": "DF", "3 MF": "MF", "4 FW": "FW"}

# Wikipedia name -> canonical name in wc2026_groups.json
TEAM_ALIASES = {
    "The United States": "United States",
    "The Netherlands": "Netherlands",
    "Czechia": "Czech Republic",
    "Republic of Korea": "South Korea",
    "Korea Republic": "South Korea",
    "Côte d'Ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
    "DR Congo": "DR Congo",
    "Democratic Republic of the Congo": "DR Congo",
    "Congo DR": "DR Congo",
}


def _normalize_team(name: str) -> str:
    return TEAM_ALIASES.get(name.strip(), name.strip())


def _parse_status(text: str) -> tuple[str, str | None]:
    text_lower = text.lower()

    if re.search(
        r"(?:announced their final squad|final squad was announced|"
        r"their final squad was announced|final roster announced|"
        r"announced their final squad through)",
        text_lower,
    ):
        squad_type = "final"
    elif (
        re.search(r"final squad will be announced", text_lower)
        or "preliminary" in text_lower
        or "pre-list" in text_lower
        or "prelist" in text_lower
    ):
        squad_type = "preliminary"
    elif "announced" in text_lower:
        squad_type = "final"
    else:
        squad_type = "preliminary"

    date_match = re.search(
        r"(?:on|was announced on|announced on|confirmed on|announced)\s+"
        r"(January|February|March|April|May|June)\s+(\d{1,2})",
        text,
        re.I,
    )
    announced = None
    if date_match:
        month, day = date_match.group(1), date_match.group(2)
        month_num = {
            "Jan": "01",
            "Feb": "02",
            "Mar": "03",
            "Apr": "04",
            "May": "05",
            "Jun": "06",
            "Jul": "07",
            "Aug": "08",
            "Sep": "09",
            "Oct": "10",
            "Nov": "11",
            "Dec": "12",
        }
        announced = f"2026-{month_num[month[:3].title()]}-{int(day):02d}"

    return squad_type, announced


def _parse_player_row(line: str) -> dict | None:
    if not line.startswith("|") or line.startswith("| ---"):
        return None
    if "| No. | Pos." in line:
        return None

    parts = [p.strip() for p in line.strip("|").split("|")]
    if len(parts) < 6:
        return None

    # Two formats: with shirt number column or without
    if re.match(r"^\d+$", parts[0]) and len(parts) >= 7:
        shirt = int(parts[0])
        pos_raw = parts[1]
        name = parts[2]
        caps = parts[4]
        goals = parts[5]
        club = parts[6]
    else:
        pos_raw = parts[0]
        name = parts[1]
        shirt = None
        caps = parts[3]
        goals = parts[4]
        club = parts[5]

    pos_match = re.match(r"(\d\s+\w+)", pos_raw)
    if not pos_match:
        return None
    position = POS_MAP.get(pos_match.group(1))
    if not position:
        return None

    captain = "(captain)" in name
    name = re.sub(r"\(captain\)", "", name).strip()

    age_match = re.search(r"\(aged (\d+)\)", parts[2 if shirt is None else 3])
    age = int(age_match.group(1)) if age_match else None

    return {
        "name": name,
        "position": position,
        "club": club,
        "caps": int(caps) if caps.isdigit() else 0,
        "goals": int(goals) if goals.isdigit() else 0,
        "age": age,
        "captain": captain,
        **({"shirt_number": shirt} if shirt is not None else {}),
    }


def parse_wiki(text: str) -> dict:
    squads: dict = {}
    current_team: str | None = None
    status_text = ""
    players: list[dict] = []
    in_table = False

    for line in text.splitlines():
        if line.startswith("### "):
            if current_team and players:
                squad_type, announced = _parse_status(status_text)
                squads[current_team] = {
                    "status": squad_type,
                    "announced_date": announced,
                    "player_count": len(players),
                    "players": players,
                }
            current_team = _normalize_team(line[4:].strip())
            status_text = ""
            players = []
            in_table = False
            continue

        if current_team is None:
            continue

        if line.startswith("| No. | Pos."):
            in_table = True
            continue

        if in_table and line.startswith("| ---"):
            continue

        if in_table and line.startswith("|"):
            player = _parse_player_row(line)
            if player:
                players.append(player)
            continue

        if not in_table and line.strip() and not line.startswith("---"):
            if not line.startswith("##"):
                status_text += " " + line.strip()

    if current_team and players:
        squad_type, announced = _parse_status(status_text)
        squads[current_team] = {
            "status": squad_type,
            "announced_date": announced,
            "player_count": len(players),
            "players": players,
        }

    return squads


def main() -> None:
    src = WIKI_TEXT
    if not src.exists():
        alt = Path(
            r"C:\Users\.NET Trainee\.cursor\projects"
            r"\c-Users-NET-Trainee-Desktop-Fifa2026Lm"
            r"\agent-tools\caa1ead5-cc99-4085-932e-7c9b04de9879.txt"
        )
        if alt.exists():
            src = alt
        else:
            raise FileNotFoundError("Wikipedia squads text not found")

    text = src.read_text(encoding="utf-8")
    squads = parse_wiki(text)

    payload = {
        "source": "Wikipedia – 2026 FIFA World Cup squads",
        "updated": "2026-05-31",
        "note": (
            "Includes teams that publicly announced preliminary or final squads. "
            "Official FIFA confirmation on 2026-06-02."
        ),
        "squads": squads,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(squads)} squads to {OUTPUT}")
    for team, data in sorted(squads.items()):
        print(f"  {team}: {data['player_count']} players ({data['status']})")


if __name__ == "__main__":
    main()
