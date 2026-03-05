import requests
import pandas as pd
from datetime import date

API_KEY = "5a255b40e032c8b473df779d13197343"

SPORT = "basketball_ncaab"
REGION = "us"
MARKETS = "spreads"
ODDS_FORMAT = "american"

url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds-history/"

params = {
    "apiKey": API_KEY,
    "regions": REGION,
    "markets": MARKETS,
    "oddsFormat": ODDS_FORMAT,
    "dateFormat": "iso"
}

r = requests.get(url, params=params)
r.raise_for_status()

data = r.json()["data"]

rows = []

for g in data:
    if not g["bookmakers"]:
        continue

    book = g["bookmakers"][0]
    market = book["markets"][0]

    home = g["home_team"]
    away = g["away_team"]

    for o in market["outcomes"]:
        rows.append({
            "date": g["commence_time"][:10],
            "team": o["name"],
            "spread": o["point"]
        })

df = pd.DataFrame(rows)
df.to_csv("vegas_spreads.csv", index=False)

print("Saved vegas_spreads.csv")