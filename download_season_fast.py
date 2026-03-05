import datetime as dt
from pathlib import Path
import time
import pandas as pd
import requests

ESPN = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"
UA = "Mozilla/5.0"
BASE_PARAMS = {"groups": "50", "limit": "500"}

def fmt(d): return d.strftime("%Y%m%d")

def parse_rows(data, day_override=None):
    rows = []
    for ev in data.get("events", []) or []:
        comp = (ev.get("competitions") or [None])[0]
        if not comp:
            continue
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

        try:
            hs = float(home.get("score"))
            aws = float(away.get("score"))
        except Exception:
            continue

        # Prefer competition date if present
        date_str = None
        if comp.get("date"):
            try:
                date_str = comp["date"][:10]
            except Exception:
                date_str = None
        if day_override:
            date_str = str(day_override)

        rows.append({
            "date": date_str,
            "team_a": str(home_team).strip(),
            "team_b": str(away_team).strip(),
            "venue": venue,
            "score_a": hs,
            "score_b": aws,
            "actual_margin": hs - aws
        })
    return rows

def fetch(session, dates_param):
    params = dict(BASE_PARAMS)
    params["dates"] = dates_param
    r = session.get(ESPN, params=params, headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    return r.json()

def daterange(start, end):
    cur = start
    while cur <= end:
        yield cur
        cur += dt.timedelta(days=1)

def week_chunks(start, end):
    cur = start
    while cur <= end:
        chunk_end = min(cur + dt.timedelta(days=6), end)
        yield cur, chunk_end
        cur = chunk_end + dt.timedelta(days=1)

def main(start="2025-11-04", end="2026-02-21", out="season_games.csv", polite_sleep=0.10):
    start_d = dt.date.fromisoformat(start)
    end_d = dt.date.fromisoformat(end)

    session = requests.Session()
    all_rows = []

    for ws, we in week_chunks(start_d, end_d):
        dates_param = f"{fmt(ws)}-{fmt(we)}"
        try:
            data = fetch(session, dates_param)
            rows = parse_rows(data)
            # If ESPN doesn't return what we need for a range call, fallback to daily
            if len(rows) == 0:
                raise RuntimeError("Range call returned 0 finals; falling back to daily.")
            all_rows.extend(rows)
            print(f"{ws}..{we} (range) -> {len(rows)} finals")
        except Exception as ex:
            print(f"{ws}..{we} (range) -> fallback daily due to: {ex}")
            for d in daterange(ws, we):
                try:
                    data = fetch(session, fmt(d))
                    rows = parse_rows(data, day_override=d)
                    all_rows.extend(rows)
                    print(f"  {d} -> {len(rows)} finals")
                except Exception as ex2:
                    print(f"  {d} -> ERROR: {ex2}")
                time.sleep(polite_sleep)

        time.sleep(polite_sleep)

    df = pd.DataFrame(all_rows)
    if not df.empty:
        df = df.drop_duplicates(subset=["date", "team_a", "team_b", "score_a", "score_b"])
        df = df.sort_values(["date", "team_a", "team_b"]).reset_index(drop=True)

    Path(out).write_text(df.to_csv(index=False), encoding="utf-8")
    print(f"Saved {out} rows={len(df)}")

if __name__ == "__main__":
    main()