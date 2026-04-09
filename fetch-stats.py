#!/usr/bin/env python3
"""Fetch Cooper Flagg's career stats from Basketball Reference and write data/stats.json."""

import json
import math
import os
import re
import urllib.request
from datetime import datetime

LEBRON_TOTAL = 40474
FLAGG_BIRTH_YEAR = 2006
BREF_URL = "https://www.basketball-reference.com/players/f/flaggco01.html"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SCRIPT_DIR, "data", "stats.json")


def fetch():
    req = urllib.request.Request(BREF_URL, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=15).read().decode()

    m = re.search(r'id="per_game.*?<tfoot>.*?<tr.*?>(.*?)</tr>', html, re.DOTALL)
    if not m:
        raise SystemExit("Could not parse career stats from Basketball Reference.")

    cells = re.findall(r"<td[^>]*>(.*?)</td>", m.group(1))
    # Career per_game row: [season, G, GS, MPG, FG, FGA, FG%, 3P, 3PA, 3P%, 2P, 2PA, 2P%, eFG%, FT, FTA, FT%, ORB, DRB, TRB, AST, STL, BLK, TOV, PF, PTS, ...]
    games = int(cells[1])
    ppg = float(cells[25])
    total_points = round(ppg * games)

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
        "games": games,
        "ppg": ppg,
        "percentage": percentage,
        "projected_year": projected_year,
        "projected_age": projected_age,
        "lebron_total": LEBRON_TOTAL,
        "updated": datetime.utcnow().isoformat() + "Z",
    }


def main():
    data = fetch()

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"Wrote {OUT_PATH}: {data}")


if __name__ == "__main__":
    main()
