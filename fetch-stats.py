#!/usr/bin/env python3
"""Fetch Cooper Flagg's career stats and write data/stats.json.

Tries nba_api first; if NBA.com blocks the request (common in CI),
falls back to the existing stats.json so the workflow doesn't fail.
Run locally to get fresh data, then CI will commit the update.
"""

import json
import math
import os
import sys
import time
from datetime import datetime

LEBRON_TOTAL = 40474
FLAGG_BIRTH_YEAR = 2006
FLAGG_PLAYER_ID = 1642843

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SCRIPT_DIR, "data", "stats.json")


def fetch_from_nba():
    from nba_api.stats.endpoints import playercareerstats

    for attempt in range(3):
        try:
            career = playercareerstats.PlayerCareerStats(
                player_id=FLAGG_PLAYER_ID, timeout=60
            )
            df = career.get_data_frames()[0]
            return int(df["PTS"].sum()), int(df["GP"].sum())
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
    return None, None


def build_data(total_points, total_games):
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

    return {
        "points": total_points,
        "games": total_games,
        "ppg": ppg,
        "percentage": percentage,
        "projected_year": projected_year,
        "projected_age": projected_age,
        "lebron_total": LEBRON_TOTAL,
        "updated": datetime.utcnow().isoformat() + "Z",
    }


def main():
    total_points, total_games = fetch_from_nba()

    if total_points is None:
        print("NBA.com fetch failed. Keeping existing stats.json.")
        if os.path.exists(OUT_PATH):
            sys.exit(0)
        else:
            sys.exit("No existing stats.json and fetch failed.")

    data = build_data(total_points, total_games)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"Wrote {OUT_PATH}: {data}")


if __name__ == "__main__":
    main()
