#!/usr/bin/env python3
"""Fetch Cooper Flagg's career stats from NBA.com and write data/stats.json."""

import json
import math
import os
from datetime import datetime

from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players


LEBRON_TOTAL = 40474
FLAGG_BIRTH_YEAR = 2006


def main():
    matches = [p for p in players.get_players() if p["full_name"] == "Cooper Flagg"]
    if not matches:
        raise SystemExit("Cooper Flagg not found in NBA player database.")

    player_id = matches[0]["id"]
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    df = career.get_data_frames()[0]

    total_points = int(df["PTS"].sum())
    total_games = int(df["GP"].sum())
    ppg = round(total_points / total_games, 1) if total_games > 0 else 0
    percentage = round((total_points / LEBRON_TOTAL) * 100, 1)

    current_year = datetime.now().year
    if ppg > 0:
        seasons_remaining = (LEBRON_TOTAL - total_points) / (ppg * 82)
        projected_year = current_year + math.ceil(seasons_remaining)
        projected_age = projected_year - FLAGG_BIRTH_YEAR
    else:
        projected_year = None
        projected_age = None

    data = {
        "points": total_points,
        "games": total_games,
        "ppg": ppg,
        "percentage": percentage,
        "projected_year": projected_year,
        "projected_age": projected_age,
        "lebron_total": LEBRON_TOTAL,
        "updated": datetime.utcnow().isoformat() + "Z",
    }

    os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), "data", "stats.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"Wrote {out_path}: {data}")


if __name__ == "__main__":
    main()
