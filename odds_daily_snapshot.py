import datetime as dt
import time
import pandas as pd
import requests

API_KEY = "cc9eb803e92f663e9c393520f13ec331"

SPORT = "basketball_ncaab"
REGIONS = "us,us2"
MARKETS = "spreads,totals"
ODDS_FORMAT = "american"

BASE = f"https://api.the-odds-api.com/v4/historical/sports/{SPORT}/odds"

def daterange(start, end):
    cur = start
    while cur <= end:
        yield cur
        cur += dt.timedelta(days=1)

def iso_z(d: dt.date, hour: int, minute: int, second: int) -> str:
    return dt.datetime(d.year, d.month, d.day, hour, minute, second, tzinfo=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def main(start="2025-11-04", end="2026-02-21", snapshot_hour_utc=22):
    """
    snapshot_hour_utc=22 means we query a snapshot at 22:00Z each day.
    We filter games by an ET-aligned window:
      commenceTimeFrom = 05:00Z (midnight ET, standard time)
      commenceTimeTo   = 04:59:59Z next day
    If you find coverage is better with a later snapshot, try snapshot_hour_utc=4 (close to end of ET day).
    """
    s = dt.date.fromisoformat(start)
    e = dt.date.fromisoformat(end)

    session = requests.Session()
    rows = []

    for i, day in enumerate(daterange(s, e), 1):
        snapshot = iso_z(day, snapshot_hour_utc, 0, 0)

        # ET-day window in UTC (standard time assumption)
        commence_from = iso_z(day, 5, 0, 0)  # 00:00 ET
        next_day = day + dt.timedelta(days=1)
        commence_to = iso_z(next_day, 4, 59, 59)  # 23:59:59 ET

        params = {
            "apiKey": API_KEY,
            "regions": REGIONS,
            "markets": MARKETS,
            "oddsFormat": ODDS_FORMAT,
            "date": snapshot,
            "commenceTimeFrom": commence_from,
            "commenceTimeTo": commence_to,
        }

        r = session.get(BASE, params=params, timeout=30)
        if r.status_code != 200:
            print(f"[{i}] {day} HTTP {r.status_code}: {r.text[:200]}")
            continue

        data = r.json().get("data", []) or []
        day_lines = 0

        for ev in data:
            home = ev.get("home_team")
            away = ev.get("away_team")
            commence = ev.get("commence_time")
            bookmakers = ev.get("bookmakers", []) or []
            if not bookmakers:
                continue

            market_spread_home = None
            market_total = None
            book_used = None

            # Find first bookmaker with spreads AND totals
            for bm in bookmakers:
                spreads_market = None
                totals_market = None
                for m in (bm.get("markets", []) or []):
                    if m.get("key") == "spreads":
                        spreads_market = m
                    elif m.get("key") == "totals":
                        totals_market = m

                if not spreads_market and not totals_market:
                    continue

                # Spread: home team's point
                spread_val = None
                if spreads_market:
                    for o in (spreads_market.get("outcomes", []) or []):
                        if o.get("name") == home:
                            spread_val = o.get("point")
                            break

                # Total: Over point
                total_val = None
                if totals_market:
                    for o in (totals_market.get("outcomes", []) or []):
                        if o.get("name") == "Over":
                            total_val = o.get("point")
                            break

                # Require at least one, prefer both
                if spread_val is not None or total_val is not None:
                    market_spread_home = spread_val
                    market_total = total_val
                    book_used = bm.get("key")
                    # If we got both, stop
                    if spread_val is not None and total_val is not None:
                        break

            # You can choose to require totals only for totals testing:
            # if market_total is None: continue
            if market_spread_home is None and market_total is None:
                continue

            rows.append({
                "date": commence[:10] if commence else str(day),
                "commence_time": commence,
                "home_team": home,
                "away_team": away,
                "market_spread_home": market_spread_home,
                "market_total": market_total,
                "bookmaker": book_used,
                "snapshot_used_utc": snapshot,
            })
            day_lines += 1

        print(f"[{i}] {day} lines={day_lines}")
        time.sleep(0.15)

    df = pd.DataFrame(rows)
    df.to_csv("vegas_spreads_daily_snapshot.csv", index=False)
    print("\nSaved vegas_spreads_daily_snapshot.csv rows=", len(df))
    print("Rows with totals:", df["market_total"].notna().sum())
    print("Rows with spreads:", df["market_spread_home"].notna().sum())

if __name__ == "__main__":
    main()