import pandas as pd
import xlwings as xw
from pathlib import Path

BOOK = "ncaab_dynamic_bracket.xlsx"
GAMES = "season_games_model_only.csv"
OUT = "backtest_results.csv"
BAD = "name_mismatch.csv"

SHEET = "Enhanced Matchup Model"

INPUT_VENUE = "B3"
INPUT_A = "B4"
INPUT_B = "B5"

OUT_SPREAD = "C34"
OUT_PA = "C35"
OUT_PB = "C36"
OUT_WINNER = "C37"
OUT_A_SCORE = "C31"
OUT_B_SCORE = "C32"
OUT_TOTAL = "C33"

df = pd.read_csv(GAMES)

app = xw.App(visible=False)
wb = app.books.open(str(Path(BOOK).resolve()))
sh = wb.sheets[SHEET]

results = []
bad_rows = []

for i,row in df.iterrows():

    sh.range(INPUT_VENUE).value = row["venue"]
    sh.range(INPUT_A).value = row["team_a"]
    sh.range(INPUT_B).value = row["team_b"]
    a_pts = sh.range(OUT_A_SCORE).value
    b_pts = sh.range(OUT_B_SCORE).value
    pred_total = sh.range(OUT_TOTAL).value

    app.calculate()

    spread = sh.range(OUT_SPREAD).value
    pa = sh.range(OUT_PA).value
    pb = sh.range(OUT_PB).value
    winner = sh.range(OUT_WINNER).value

    # Skip if model failed (usually name mismatch)
    if spread is None:
        bad_rows.append({
            "date": row["date"],
            "team_a": row["team_a"],
            "team_b": row["team_b"]
        })
        continue

    actual = row["actual_margin"]

    pick = "A" if spread > 0 else "B"
    actual_pick = "A" if actual > 0 else "B"

    results.append({
        "date": row["date"],
        "team_a": row["team_a"],
        "team_b": row["team_b"],
        "score_a": row["score_a"],
        "score_b": row["score_b"],
        "pred_spread": spread,
        "win_prob_a": pa,
        "win_prob_b": pb,
        "winner_text": winner,
        "actual_margin": actual,
        "correct": 1 if pick == actual_pick else 0,
        "pred_team_a_pts": a_pts,
        "pred_team_b_pts": b_pts,
        "pred_total": pred_total,
    })

    if i % 250 == 0:
        print("Processed", i)

wb.close()
app.quit()

out = pd.DataFrame(results)
out.to_csv(OUT,index=False)

if bad_rows:
    pd.DataFrame(bad_rows).to_csv(BAD,index=False)
    print("Name mismatches saved to", BAD)

print("Saved backtest_results.csv")
print("Games evaluated:", len(out))
print("Win rate:", out["correct"].mean())

print("\nSpread buckets:")
for thresh in [5,8,10,12]:
    sub = out[abs(out["pred_spread"]) >= thresh]
    if len(sub)>0:
        print(f"|spread| >= {thresh}: n={len(sub)}, win={sub['correct'].mean():.3f}")

print("\nWin prob buckets:")
for thresh in [0.60,0.65,0.70,0.75]:
    sub = out[out["win_prob_a"] >= thresh]
    if len(sub)>0:
        print(f"Prob >= {thresh}: n={len(sub)}, win={sub['correct'].mean():.3f}")