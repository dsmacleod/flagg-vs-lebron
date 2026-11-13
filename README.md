# Flagg vs. LeBron

A tongue-in-cheek embeddable graphic for the Bangor Daily News that tracks Cooper Flagg's NBA career scoring against LeBron James' all-time total (hardcoded at 40,474 points) and projects when Flagg would pass him at his current pace.

**Live:** https://dsmacleod.github.io/flagg-vs-lebron/

## How it works

1. `fetch-stats.py` scrapes Flagg's career per-game row from his [Basketball Reference](https://www.basketball-reference.com/players/f/flaggco01.html) page (standard library only, no dependencies).
2. It computes career points (PPG x games), percentage of LeBron's total, and a projected passing year/age assuming 82-game seasons at the current PPG.
3. Results are written to `data/stats.json`:
   `points`, `games`, `ppg`, `percentage`, `projected_year`, `projected_age`, `lebron_total`, `updated`.
4. `index.html` / `embed.html` (identical files) fetch `data/stats.json` and render a headline, progress bar and projection. The HTML is meant to be pasted into a Newspack Custom HTML block; set `DATA_URL` in the script to the hosted `stats.json` URL when embedding outside this site.

`docs/plans/` holds the original design doc, which describes a WordPress plugin + balldontlie.io approach. The shipped version uses the static page and Basketball Reference scrape described above.

## GitHub Actions

`.github/workflows/fetch-stats.yml` runs every 6 hours (`0 */6 * * *`) and on manual dispatch. It runs `fetch-stats.py` and commits `data/stats.json` if it changed. No secrets are required.

## Run locally

```bash
python3 fetch-stats.py          # refresh data/stats.json
python3 -m http.server 8000     # then open http://localhost:8000/
```
