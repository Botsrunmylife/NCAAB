import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

MODEL_CSV = "backtest_results.csv"
VEGAS_CSV = "vegas_spreads_daily_snapshot.csv"

def to_et_date(ts: str):
    if not ts or str(ts).lower() in {"nan", "none"}:
        return None
    try:
        s = str(ts)
        if s.endswith("Z"):
            s = s.replace("Z", "+00:00")
        dt_utc = datetime.fromisoformat(s).astimezone(ZoneInfo("America/New_York"))
        return dt_utc.date().isoformat()
    except Exception:
        return None

model = pd.read_csv(MODEL_CSV)
vegas = pd.read_csv(VEGAS_CSV)

# Required columns
need_model = ["date","team_a","team_b","pred_total","score_a","score_b"]
need_vegas = ["commence_time","home_team","away_team","market_total"]

missing_model = [c for c in need_model if c not in model.columns]
missing_vegas = [c for c in need_vegas if c not in vegas.columns]

if missing_model:
    raise SystemExit(f"backtest_results.csv missing columns: {missing_model}. Found: {list(model.columns)}")
if missing_vegas:
    raise SystemExit(f"vegas_spreads_daily_snapshot.csv missing columns: {missing_vegas}. Found: {list(vegas.columns)}")

# ET game-date for vegas
vegas["date_et"] = vegas["commence_time"].apply(to_et_date)
vegas = vegas[vegas["market_total"].notna()].copy()

# Merge model with vegas (home/away alignment)
m = model.merge(
    vegas,
    left_on=["date","team_a","team_b"],
    right_on=["date_et","home_team","away_team"],
    how="inner"
)

# Compute actual total directly from backtest_results scores
m["actual_total"] = m["score_a"] + m["score_b"]
m["over_hits"] = m["actual_total"] > m["market_total"]
m["under_hits"] = m["actual_total"] < m["market_total"]

# Edge: + = model likes Over, - = model likes Under
m["total_edge"] = m["pred_total"] - m["market_total"]

print("Merged totals games:", len(m))

print("\nTOTAL EDGE BUCKETS (bet Over if edge >= t, bet Under if edge <= -t):")
for t in [2, 3, 4, 5, 6, 7]:
    overs = m[m["total_edge"] >= t]
    unders = m[m["total_edge"] <= -t]
    n = len(overs) + len(unders)
    if n == 0:
        continue
    wins = overs["over_hits"].sum() + unders["under_hits"].sum()
    print(f"t={t}: bets={n} (over={len(overs)}, under={len(unders)}), win%={wins/n:.3f}")

print("\n=== OVERS ONLY ===")
for t in [2,3,4,5,6,7]:
    overs = m[m["total_edge"] >= t]
    if len(overs):
        print(f"t={t}: bets={len(overs)}, win%={overs['over_hits'].mean():.3f}")

print("\n=== UNDERS ONLY ===")
for t in [2,3,4,5,6,7]:
    unders = m[m["total_edge"] <= -t]
    if len(unders):
        print(f"t={t}: bets={len(unders)}, win%={unders['under_hits'].mean():.3f}")

m.to_csv("totals_edge_results.csv", index=False)
print("\nSaved totals_edge_results.csv")