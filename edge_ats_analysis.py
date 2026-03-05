import pandas as pd

model = pd.read_csv("backtest_results.csv")
vegas = pd.read_csv("vegas_spreads_daily_snapshot.csv")

# Your convention: team_a = HOME, team_b = AWAY
m = model.merge(
    vegas,
    left_on=["date","team_a","team_b"],
    right_on=["date","home_team","away_team"],
    how="inner"
)

# ATS result for betting HOME (Team A):
# Home covers if actual_margin + market_spread_home > 0
m["home_covers"] = (m["actual_margin"] + m["market_spread_home"]) > 0

# Model edge in points (HOME perspective)
m["edge_pts"] = m["pred_spread"] - m["market_spread_home"]

print("Merged games with lines:", len(m))

print("\nEDGE BUCKETS (bet with edge):")
for t in [1,2,3,4,5,6,7]:
    a = m[m["edge_pts"] >= t]       # bet HOME
    b = m[m["edge_pts"] <= -t]     # bet AWAY
    n = len(a) + len(b)
    if n == 0:
        continue
    wins = a["home_covers"].sum() + (~b["home_covers"]).sum()
    print(f"t={t}: bets={n} (home={len(a)}, away={len(b)}), win%={wins/n:.3f}")

m.to_csv("edge_results_ats.csv", index=False)
print("\nSaved edge_results_ats.csv")