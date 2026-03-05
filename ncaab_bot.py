#!/usr/bin/env python3
"""
NCAAB BETTING BOT — Model + Odds + EV Finder
==============================================
REQUIRES: openpyxl only (py -m pip install openpyxl)
Odds fetch uses urllib (built into Python, no install needed).

SETUP (one time):
  cd C:\\Users\\13032\\Downloads\\NCAAB
  py -m pip install openpyxl
  python ncaab_bot.py --set-key YOUR_API_KEY_HERE

DAILY USE:
  python ncaab_bot.py
"""

import json, math, os, sys, datetime as dt
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "ncaab_config.json"
BRACKET_FILE = "ncaab_dynamic_bracket.xlsm"
ODDS_SPORT = "basketball_ncaab"

P = {
    "off_w": 0.44, "def_w": 0.43,
    "hca": 1, "sor_w": 0.03,
    "win_scale": 18, "sos_alpha": 0.05,
    "close_foul": 4, "blow_foul": 1, "spread_thresh": 7,
    "pace_slow": 0.65, "pace_fast": 0.35,
}

EV_SPREAD_MIN = 3.0
EV_ML_MIN = 0.05
EV_TOTAL_MIN = 3.0

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f: return json.load(f)
    return {}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f: json.dump(cfg, f, indent=2)

def get_api_key():
    return os.environ.get("ODDS_API_KEY") or load_config().get("api_key", "")

class Team:
    def __init__(self, name):
        self.name = name; self.conf = ""
        self.pts=0; self.fga=0; self.fta=0; self.oreb=0; self.to=0
        self.opp_pts=0; self.opp_fga=0; self.opp_fta=0; self.opp_oreb=0; self.opp_to=0
        self.sos_rk=200; self.nc_sos=200; self.sor_rk=200
        self.wins=0; self.losses=0; self.qw=0; self.ql=0; self.sor_score=0.0

    @property
    def poss(self): return self.fga + 0.44*self.fta + self.to - self.oreb
    @property
    def ppp_off(self): return self.pts / self.poss if self.poss > 0 else 1.0
    @property
    def opp_poss(self): return self.opp_fga + 0.44*self.opp_fta + self.opp_to - self.opp_oreb
    @property
    def ppp_def(self): return self.opp_pts / self.opp_poss if self.opp_poss > 0 else 1.05
    def adj_off(self): return self.ppp_off * ((366-self.sos_rk)/365)**P["sos_alpha"]
    def adj_def(self): return self.ppp_def * (2-((366-self.sos_rk)/365)**P["sos_alpha"])

def load_teams(path):
    try: import openpyxl
    except ImportError: print("Need openpyxl:  py -m pip install openpyxl"); sys.exit(1)
    wb = openpyxl.load_workbook(path, data_only=True)
    teams = {}
    def n(v):
        try: return float(v) if v is not None else 0.0
        except: return 0.0

    ws = wb["Team Stats"]
    for r in range(2, ws.max_row+1):
        name = ws.cell(r,2).value
        if not name: continue
        name = str(name).strip(); t = Team(name)
        t.pts=n(ws.cell(r,4).value); t.fga=n(ws.cell(r,6).value)
        t.fta=n(ws.cell(r,12).value); t.oreb=n(ws.cell(r,14).value)
        t.to=n(ws.cell(r,20).value); teams[name]=t

    ws2 = wb["Opponents stats vs"]
    for r in range(2, ws2.max_row+1):
        name = ws2.cell(r,2).value
        if not name or str(name).strip() not in teams: continue
        t = teams[str(name).strip()]
        t.opp_pts=n(ws2.cell(r,4).value); t.opp_fga=n(ws2.cell(r,6).value)
        t.opp_fta=n(ws2.cell(r,12).value); t.opp_oreb=n(ws2.cell(r,14).value)
        t.opp_to=n(ws2.cell(r,20).value)

    ws3 = wb["SOS"]
    for r in range(2, ws3.max_row+1):
        name = ws3.cell(r,1).value
        if not name or str(name).strip() not in teams: continue
        t = teams[str(name).strip()]; t.conf=str(ws3.cell(r,2).value or "")
        t.sos_rk=int(ws3.cell(r,4).value or 200); t.nc_sos=int(ws3.cell(r,5).value or 200)
        t.wins=int(ws3.cell(r,6).value or 0); t.losses=int(ws3.cell(r,7).value or 0)
        t.qw=int(ws3.cell(r,8).value or 0); t.ql=int(ws3.cell(r,9).value or 0)

    for t in teams.values():
        tg=t.wins+t.losses
        if tg==0: continue
        wp=t.wins/tg; sf=(366-t.sos_rk)/365; nf=(366-t.nc_sos)/365
        qt=t.qw+t.ql; qr=(t.qw/qt) if qt>0 else 0; qv=qt/tg
        t.sor_score = 0.35*wp*sf + 0.30*wp*(0.7*sf+0.3*nf) + 0.20*qr*qv + 0.15*wp
    for i,t in enumerate(sorted(teams.values(), key=lambda x:-x.sor_score),1):
        t.sor_rk=i
    wb.close()
    return teams

def predict(a, b, venue="neutral"):
    a_blend = P["off_w"]*a.adj_off() + P["def_w"]*b.adj_def()
    b_blend = P["off_w"]*b.adj_off() + P["def_w"]*a.adj_def()
    pace = P["pace_slow"]*min(a.poss,b.poss) + P["pace_fast"]*max(a.poss,b.poss)
    sor_adj = -(a.sor_rk-b.sor_rk)*P["sor_w"]
    hca = P["hca"] if venue=="home" else (-P["hca"] if venue=="away" else 0)
    raw_a = a_blend*pace+hca+sor_adj; raw_b = b_blend*pace-hca-sor_adj
    spread = raw_a-raw_b
    foul = P["close_foul"] if abs(spread)<P["spread_thresh"] else P["blow_foul"]
    win_a = 1/(1+math.exp(-spread/P["win_scale"]))
    return {"team_a":a.name,"team_b":b.name,"venue":venue,
            "score_a":round(raw_a),"score_b":round(raw_b),
            "spread":round(spread,1),"total":round(raw_a)+round(raw_b)+foul,
            "win_a":round(win_a,4),"win_b":round(1-win_a,4),"pace":round(pace,1)}

def fetch_odds(api_key):
    params = urlencode({"apiKey":api_key,"regions":"us,us2",
        "markets":"spreads,h2h,totals","oddsFormat":"american","dateFormat":"iso"})
    url = f"https://api.the-odds-api.com/v4/sports/{ODDS_SPORT}/odds?{params}"
    req = Request(url, headers={"User-Agent":"NCAAB-Bot/1.0"})
    try:
        with urlopen(req, timeout=30) as resp:
            rem = resp.headers.get("x-requests-remaining","?")
            print(f"  API calls remaining this month: {rem}")
            return json.loads(resp.read().decode())
    except HTTPError as e:
        if e.code==401: print("  ERROR: Invalid API key")
        elif e.code==429: print("  ERROR: Monthly quota exceeded")
        else: print(f"  ERROR: HTTP {e.code}")
        return []
    except URLError as e:
        print(f"  ERROR: {e.reason}"); return []

def american_to_decimal(o):
    return (1+o/100) if o>0 else (1+100/abs(o)) if o<0 else 1.0

def imp_prob(o):
    return 100/(o+100) if o>0 else abs(o)/(abs(o)+100) if o<0 else 0.5

def find_ev(games, teams):
    bets = []
    for game in games:
        home,away = game.get("home_team",""), game.get("away_team","")
        ht,at = teams.get(home), teams.get(away)
        if not ht or not at: continue
        pred = predict(ht, at, venue="home")
        time = game.get("commence_time","")[:16]
        for bm in game.get("bookmakers",[]):
            book = bm.get("key","")
            for mkt in bm.get("markets",[]):
                k = mkt.get("key")
                for oc in mkt.get("outcomes",[]):
                    tm,odds,line = oc.get("name",""), oc.get("price",0), oc.get("point")
                    base = {"game":f"{away} @ {home}","time":time,"book":book,
                            "model_spread":pred["spread"],"pred":f"{pred['score_a']}-{pred['score_b']}"}
                    if k=="spreads" and line is not None:
                        edge = (pred["spread"]-(-line)) if tm==home else (-pred["spread"]-(-line))
                        if abs(edge)>=EV_SPREAD_MIN:
                            cp = min(0.85,max(0.15,0.5+edge*0.03))
                            ev = cp*(american_to_decimal(odds)-1)-(1-cp)
                            if ev>0:
                                bets.append({**base,"type":"SPREAD",
                                    "side":f"{'HOME' if tm==home else 'AWAY'} {tm}",
                                    "line":line,"odds":odds,"edge_pts":round(edge,1),
                                    "ev_pct":round(ev*100,1),"model_prob":round(cp,3),
                                    "implied":round(imp_prob(odds),3)})
                    elif k=="h2h":
                        mp = pred["win_a"] if tm==home else pred["win_b"]
                        ip = imp_prob(odds); edge = mp-ip
                        if edge>=EV_ML_MIN:
                            ev = mp*(american_to_decimal(odds)-1)-(1-mp)
                            if ev>0:
                                bets.append({**base,"type":"ML","side":tm,
                                    "line":None,"odds":odds,"edge_pts":None,
                                    "ev_pct":round(ev*100,1),"model_prob":round(mp,3),
                                    "implied":round(ip,3)})
                    elif k=="totals" and line is not None:
                        diff = pred["total"]-line; sn = oc.get("name","")
                        if sn=="Over" and diff>EV_TOTAL_MIN:
                            pr = min(0.85,0.5+diff*0.025)
                            ev = pr*(american_to_decimal(odds)-1)-(1-pr)
                            if ev>0:
                                bets.append({**base,"type":"TOTAL","side":f"OVER {line}",
                                    "line":line,"odds":odds,"edge_pts":round(diff,1),
                                    "ev_pct":round(ev*100,1),"model_prob":round(pr,3),
                                    "implied":round(imp_prob(odds),3)})
                        elif sn=="Under" and diff<-EV_TOTAL_MIN:
                            pr = min(0.85,0.5+abs(diff)*0.025)
                            ev = pr*(american_to_decimal(odds)-1)-(1-pr)
                            if ev>0:
                                bets.append({**base,"type":"TOTAL","side":f"UNDER {line}",
                                    "line":line,"odds":odds,"edge_pts":round(abs(diff),1),
                                    "ev_pct":round(ev*100,1),"model_prob":round(pr,3),
                                    "implied":round(imp_prob(odds),3)})
    best = {}
    for b in bets:
        k = (b["game"],b["type"],b["side"])
        if k not in best or b["ev_pct"]>best[k]["ev_pct"]: best[k]=b
    return sorted(best.values(), key=lambda x:-x["ev_pct"])

def main():
    args = sys.argv[1:]

    if "--set-key" in args:
        idx = args.index("--set-key")
        if idx+1 < len(args):
            cfg = load_config(); cfg["api_key"] = args[idx+1]; save_config(cfg)
            print(f"API key saved to {CONFIG_FILE}")
            print("From now on just run: python ncaab_bot.py")
        else: print("Usage: python ncaab_bot.py --set-key YOUR_KEY")
        return

    excel = BRACKET_FILE
    if "--excel" in args:
        idx = args.index("--excel")
        if idx+1 < len(args): excel = args[idx+1]
    if not Path(excel).exists():
        for name in ["ncaab_dynamic_bracket.xlsm","ncaab_dynamic_bracket.xlsx"]:
            if Path(name).exists(): excel=name; break
        else: print(f"ERROR: {excel} not found"); sys.exit(1)

    api_key = get_api_key()

    print("="*60)
    print("  NCAAB BETTING BOT")
    print(f"  {dt.date.today()}")
    print("="*60)

    print(f"\n[1/4] Loading model from {excel}...")
    teams = load_teams(excel)
    print(f"  {len(teams)} teams loaded")
    for t in sorted(teams.values(), key=lambda x:-x.sor_score)[:5]:
        print(f"  #{t.sor_rk} {t.name} ({t.wins}-{t.losses}) "
              f"Off:{t.ppp_off:.3f} Def:{t.ppp_def:.3f} QW:{t.qw}-{t.ql}")

    print(f"\n[2/4] Fetching odds...")
    if not api_key:
        print("  No API key. Run: python ncaab_bot.py --set-key YOUR_KEY")
        print("  Free key: https://the-odds-api.com"); games=[]
    else:
        games = fetch_odds(api_key)
        print(f"  {len(games)} games found")

    print(f"\n[3/4] Running predictions...")
    preds=[]
    for g in games:
        h,a = teams.get(g.get("home_team","")), teams.get(g.get("away_team",""))
        if h and a: preds.append(predict(h,a,venue="home"))
    print(f"  {len(preds)} matchups")

    print(f"\n[4/4] Finding +EV bets...")
    ev = find_ev(games, teams)
    print(f"  {len(ev)} +EV opportunities")

    if ev:
        print(f"\n{'='*60}")
        print(f"  +EV BETS")
        print(f"{'='*60}")
        for b in ev[:20]:
            o = f"+{b['odds']}" if b['odds']>0 else str(b['odds'])
            print(f"\n  {b['type']:6s} | {b['side']}")
            print(f"         {b['game']}  [{b['book']}]")
            print(f"         Odds: {o}  EV: +{b['ev_pct']}%  "
                  f"Model: {b['model_prob']:.0%}  Market: {b['implied']:.0%}")
            if b['line'] is not None:
                print(f"         Line: {b['line']:+.1f}  "
                      f"Model spread: {b['model_spread']:+.1f}  Pred: {b['pred']}")
            else:
                print(f"         Model spread: {b['model_spread']:+.1f}  Pred: {b['pred']}")

    # Save
    out_dir = Path("output"); out_dir.mkdir(exist_ok=True)
    ds = dt.date.today().isoformat()
    data = {"date":ds,"ev_bets":ev,"predictions":preds,
            "top_25":[{"rank":t.sor_rk,"name":t.name,"record":f"{t.wins}-{t.losses}",
                "sor":round(t.sor_score,4),"ppp_off":round(t.ppp_off,3),
                "ppp_def":round(t.ppp_def,3),"qual":f"{t.qw}-{t.ql}"}
                for t in sorted(teams.values(),key=lambda x:-x.sor_score)[:25]]}
    for f in [out_dir/f"daily_{ds}.json", out_dir/"latest.json"]:
        with open(f,"w") as fh: json.dump(data,fh,indent=2,default=str)
    print(f"\n  Saved to output/latest.json")
    print("="*60)

if __name__=="__main__":
    main()
