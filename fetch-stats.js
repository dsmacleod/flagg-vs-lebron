#!/usr/bin/env node

/**
 * Fetches Cooper Flagg's career stats from balldontlie.io and writes data/stats.json.
 *
 * Usage: BALLDONTLIE_API_KEY=your_key node fetch-stats.js
 */

const fs = require('fs');
const path = require('path');

const LEBRON_TOTAL = 40474;
const FLAGG_BIRTH_YEAR = 2006;
const API_BASE = 'https://api.balldontlie.io/nba/v1';

async function apiFetch(path, apiKey) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { Authorization: apiKey },
  });
  if (!res.ok) {
    console.error(`API ${path} responded ${res.status}: ${await res.text()}`);
    process.exit(1);
  }
  return res.json();
}

async function fetchStats() {
  const apiKey = process.env.BALLDONTLIE_API_KEY;
  if (!apiKey) {
    console.error('Missing BALLDONTLIE_API_KEY environment variable.');
    process.exit(1);
  }

  // Look up Flagg's player ID by name
  const players = await apiFetch('/players?search=Cooper+Flagg', apiKey);
  if (!players.data || players.data.length === 0) {
    console.error('Could not find Cooper Flagg in player database.');
    process.exit(1);
  }
  const playerId = players.data[0].id;
  console.log(`Found Cooper Flagg: player ID ${playerId}`);

  // Fetch season averages for current season
  const currentSeason = new Date().getFullYear();
  const body = await apiFetch(
    `/season_averages?season=${currentSeason}&player_id=${playerId}`,
    apiKey
  );

  if (!body.data || body.data.length === 0) {
    console.error('No season data returned for Flagg.');
    process.exit(1);
  }

  let totalPoints = 0;
  let totalGames = 0;

  for (const season of body.data) {
    const games = season.games_played || 0;
    const pts = season.pts || 0;
    totalPoints += Math.round(pts * games);
    totalGames += games;
  }

  const ppg = totalGames > 0 ? Math.round((totalPoints / totalGames) * 10) / 10 : 0;
  const percentage = Math.round((totalPoints / LEBRON_TOTAL) * 1000) / 10;
  const currentYear = new Date().getFullYear();

  let projectedYear = null;
  let projectedAge = null;

  if (ppg > 0) {
    const seasonsRemaining = (LEBRON_TOTAL - totalPoints) / (ppg * 82);
    projectedYear = currentYear + Math.ceil(seasonsRemaining);
    projectedAge = projectedYear - FLAGG_BIRTH_YEAR;
  }

  const data = {
    points: totalPoints,
    games: totalGames,
    ppg,
    percentage,
    projected_year: projectedYear,
    projected_age: projectedAge,
    lebron_total: LEBRON_TOTAL,
    updated: new Date().toISOString(),
  };

  const outDir = path.join(__dirname, 'data');
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir);
  }

  fs.writeFileSync(path.join(outDir, 'stats.json'), JSON.stringify(data, null, 2) + '\n');
  console.log('Wrote data/stats.json:', data);
}

fetchStats();
