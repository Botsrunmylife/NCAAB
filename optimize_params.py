import numpy as np
import pandas as pd
import subprocess
import time
import re
import sys

EXCEL_PATH = r"C:\ncaab\ncaab_dynamic_bracket.xlsx"
SHEET_NAME = "Enhanced Matchup Model"

# IMPORTANT: Update these cells if your parameters live somewhere else
CELL_OFF = "F3"
CELL_DEF = "F4"

# Start small to confirm it works, then expand
off_weights = [0.46, 0.49, 0.52]
def_weights = [0.44, 0.47, 0.50]

def set_excel_params(off, de):
    ps = f"""
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$wb = $excel.Workbooks.Open("{EXCEL_PATH}")
$ws = $wb.Worksheets.Item("{SHEET_NAME}")
$ws.Range("{CELL_OFF}").Value = {off}
$ws.Range("{CELL_DEF}").Value = {de}
$wb.Save()
$wb.Close($true)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($ws) | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($wb) | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
"""
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], text=True)
    if r.returncode != 0:
        raise RuntimeError("PowerShell failed setting Excel params")

def parse_t_line(stdout, t=8):
    # matches: t=8: bets=274 (over=.., under=..), win%=0.566
    pat = re.compile(rf"t={t}:\s+.*win%=(\d+\.\d+)")
    m = pat.search(stdout)
    return float(m.group(1)) if m else None

results = []
total_iters = len(off_weights) * len(def_weights)
k = 0

print(f"Running {total_iters} parameter combos...\n", flush=True)

for off in off_weights:
    for de in def_weights:
        k += 1
        print(f"[{k}/{total_iters}] off={off:.3f}, def={de:.3f} -> setting Excel...", flush=True)
        t0 = time.time()

        set_excel_params(off, de)

        print("  running backtest_excel.py ...", flush=True)
        bt = subprocess.run([sys.executable, "backtest_excel.py"], text=True)
        if bt.returncode != 0:
            print("  backtest FAILED", flush=True)
            continue

        print("  running totals_edge_analysis.py ...", flush=True)
        p = subprocess.run([sys.executable, "totals_edge_analysis.py"], capture_output=True, text=True)
        if p.returncode != 0:
            print("  totals analysis FAILED:", p.stderr[:200], flush=True)
            continue

        win8 = parse_t_line(p.stdout, t=8)
        win7 = parse_t_line(p.stdout, t=7)
        bets8 = None

        # quick parse bets count for t=8
        for line in p.stdout.splitlines():
            if line.startswith("t=8:"):
                # t=8: bets=274 ...
                try:
                    bets8 = int(line.split("bets=")[1].split()[0])
                except Exception:
                    bets8 = None

        dt_sec = time.time() - t0
        print(f"  done in {dt_sec:.1f}s | t=7={win7} t=8={win8} bets8={bets8}\n", flush=True)

        results.append({"off": off, "def": de, "win7": win7, "win8": win8, "bets8": bets8, "secs": dt_sec})

df = pd.DataFrame(results)
df.to_csv("param_sweep_small.csv", index=False)

print("Top by win8:\n")
print(df.sort_values("win8", ascending=False).head(10).to_string(index=False))
print("\nSaved param_sweep_small.csv")