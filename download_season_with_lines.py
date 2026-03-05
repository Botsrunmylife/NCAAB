import datetime as dt
import time
from pathlib import Path
import pandas as pd
import requests
import re

ESPN = (
    "https://site.api.espn.com/apis/site/v2/sports/"
    "basketball/mens-college-basketball/scoreboard"
)
UA = "Mozilla/5.0"
BASE_PARAMS = {"groups": "50", "limit": "500"}

def fmt(d): 
    return d.strftime("%Y%m%d")

def daterange(start, end):
    cur = start
    while cur <= end:
        yield cur
        cur += dt.timedelta(days=1)

def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None

def parse_espn_spread_to_home(details: str, home_team: str, away_team: str):
    """
    ESPN odds details usually look like:
      'Duke -7.5'
      'Kansas -3'
    We convert that to a numeric spread from HOME perspective:
      home_spread = -7.5 if home is favored by 7.5
      home_spread = +7.5 if away is favored by 7.5
    Returns None if cannot parse.
    """
    if not details or not isinstance(details, str):
        return None

    s = details.strip()

    # Extract trailing number (spread)
    m = re.search(r"([+-]?\d+(\.\d+)?)\s*$", s)
    if not m:
        return None
    spread = safe_float(m.group(1))
    if spread is None:
        return None

    # Team part is everything before the number
    team_part = s[:m.start()].strip()
    if not team_part:
        return None

    # If ESPN says "Team -7.5", that team is favored.
    # Determine if the favored team is home or away.
    favored = team_part

    # Loose match: exact equals or substring match either way
    home_match = (favored.lower() == home_team.lower()) or (favored.lower() in home_team.lower()) or (home_team.lower() in favored.lower())
    away_match = (favored.lower() == away_team.lower()) or (favored.lower() in away_team.lower()) or (away_team.lower() in favored.lower())

    if home_match and not away_match:
        # home favored: home line is negative
        return -abs(spread)
    if away_match and not home_match:
        # away favored: home line is positive
        return abs(spread)

    # Ambiguous team name parsing
    return None

def fetch_day(session, day):
    params = dict(BASE_PARAMS)
    params["dates"] = fmt(day)
    r = session.get(ESPN, params=params, headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    return r.json()

def main(start="2025-11-04", end="2026-02-21", out="season_games_with_lines.csv", sleep_s=0.12):
    start_d = dt.date.fromisoformat(start)
    end_d = dt.date.fromisoformat(end)

    session = requests.Session()
    rows = []

    for i, day in enumerate(daterange(start_d, end_d), 1):
        data = fetch_day(session, day)
        events = data.get("events", []) or []

        day_count = 0

        for ev in events:
            comps = ev.get("competitions", []) or []
            if not comps:
                continue
            comp = comps[0]

            st = (comp.get("status") or {}).get("type") or {}
            if not st.get("completed", False):
                continue

            neutral = bool(comp.get("neutralSite", False))
            venue = "neutral" if neutral else "home"

            home = away = None
            for c in comp.get("competitors", []) or []:
                if c.get("homeAway") == "home":
                    home = c
                elif c.get("homeAway") == "away":
                    away = c
            if not home or not away:
                continue

            home_team = (home.get("team") or {}).get("displayName") or (home.get("team") or {}).get("name")
            away_team = (away.get("team") or {}).get("displayName") or (away.get("team") or {}).get("name")
            home_team = str(home_team).strip()
            away_team = str(away_team).strip()

            hs = safe_float(home.get("score"))
            aws = safe_float(away.get("score"))
            if hs is None or aws is None:
                continue

            # Try to read ESPN odds
            odds_list = comp.get("odds", []) or []
            espn_details = None
            espn_total = None
            home_market_spread = None

            if odds_list:
                o0 = odds_list[0] or {}
                espn_details = o0.get("details")
                espn_total = safe_float(o0.get("overUnder"))
                home_market_spread = parse_espn_spread_to_home(espn_details, home_team, away_team)

            rows.append({
                "date": str(day),
                "team_a": home_team,     # keep your convention: A = home
                "team_b": away_team,     # B = away
                "venue": venue,
                "score_a": hs,
                "score_b": aws,
                "actual_margin": hs - aws,
                "market_spread_home": home_market_spread,  # HOME perspective
                "market_total": espn_total,
                "market_details_raw": espn_details,
            })
            day_count += 1

        print(f"[{i}] {day} finals={day_count}")
        time.sleep(sleep_s)

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.drop_duplicates(subset=["date", "team_a", "team_b", "score_a", "score_b"])
        df = df.sort_values(["date", "team_a", "team_b"]).reset_index(drop=True)

    Path(out).write_text(df.to_csv(index=False), encoding="utf-8")
    print(f"Saved {out} rows={len(df)}")
    print("Rows with market spread:", df["market_spread_home"].notna().sum())

if __name__ == "__main__":
    main()