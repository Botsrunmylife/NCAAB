"""
Build Dashboard — Embeds bot output into a single shareable HTML file.

Usage:
  python ncaab_bot.py          # generates output/latest.json
  python build_dashboard.py    # generates dashboard.html with data baked in

Friends just open dashboard.html — no server needed, works offline.
"""
import json, sys, os
from pathlib import Path

def main():
    # Find latest.json
    for p in ["output/latest.json", "latest.json"]:
        if os.path.exists(p):
            with open(p) as f:
                data = json.load(f)
            print(f"Loaded {p}: {len(data.get('ev_bets',[]))} EV bets, date={data.get('date')}")
            break
    else:
        print("No output/latest.json found. Run ncaab_bot.py first.")
        data = None

    data_json = json.dumps(data, default=str) if data else "null"

    html = BUILD_HTML(data_json)

    out = Path("dashboard.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard saved to {out} ({out.stat().st_size:,} bytes)")
    print("Open it in your browser or send to friends!")


def BUILD_HTML(data_json):
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>NCAAB Bracket + EV Dashboard</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'JetBrains Mono',monospace;background:#0a0f1a;color:#e2e8f0;min-height:100vh}}
.hd{{background:linear-gradient(135deg,#0f172a,#1e1b4b,#0f172a);border-bottom:1px solid #1e293b;padding:16px 24px 0}}
.tl{{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:4px}}
.tl h1{{font-size:22px;font-weight:800;letter-spacing:-1px}}
.tl .su{{font-size:22px;font-weight:300;color:#818cf8}}
.tl .ch{{font-size:11px;color:#fbbf24;margin-left:auto;font-weight:700}}
.mt{{display:flex;gap:10px;font-size:10px;color:#64748b;margin-bottom:12px;flex-wrap:wrap}}
.tabs{{display:flex;gap:0;overflow-x:auto}}
.tab{{padding:10px 18px;font-size:12px;font-weight:400;color:#64748b;background:0;border:none;border-bottom:2px solid transparent;cursor:pointer;font-family:inherit;border-radius:6px 6px 0 0;white-space:nowrap}}
.tab.on{{font-weight:700;color:#f8fafc;background:#1e293b;border-bottom-color:#818cf8}}
.ct{{padding:20px 24px}}.hid{{display:none!important}}
.pls{{display:flex;gap:4px;margin-bottom:10px;flex-wrap:wrap}}
.pl{{padding:5px 12px;font-size:11px;color:#94a3b8;background:#1e293b;border:1px solid #334155;border-radius:20px;cursor:pointer;font-family:inherit}}
.pl.on{{font-weight:700;color:#f8fafc;background:#818cf8;border-color:#818cf8}}
.rgs{{display:flex;gap:4px;margin-bottom:14px}}
.rb{{padding:3px 10px;font-size:10px;background:0;border:1px solid #334155;border-radius:4px;cursor:pointer;font-family:inherit}}
.gm{{background:#111827;border:1px solid #1e293b;border-radius:6px;padding:6px 10px;font-size:11px;margin-bottom:4px;border-left:3px solid #475569}}
.gm .rw{{display:flex;justify-content:space-between}}.gm .w{{color:#f8fafc;font-weight:700}}.gm .l{{color:#64748b}}
.gm .sd{{color:#475569;font-size:9px;margin-right:3px}}.gm .sc{{color:#94a3b8;min-width:28px;text-align:right}}
.gm .mr{{display:flex;justify-content:space-between;font-size:9px;color:#475569;margin-top:2px}}.gm .up{{color:#fbbf24}}
.gm.east{{border-left-color:#3b82f6}}.gm.south{{border-left-color:#f97316}}.gm.midwest{{border-left-color:#10b981}}.gm.west{{border-left-color:#a855f7}}
.gg{{display:grid;gap:6px}}.g4{{grid-template-columns:repeat(4,1fr)}}.g2{{grid-template-columns:1fr 1fr}}.g1{{grid-template-columns:1fr}}
.pt{{margin-top:16px;background:#111827;border:1px solid #1e293b;border-radius:8px;padding:16px}}
.pt h3{{font-size:12px;font-weight:700;color:#818cf8;margin-bottom:8px}}
.pg{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;font-size:11px}}
.pc{{padding-top:6px}}.pc .rn{{font-weight:700;font-size:10px;text-transform:uppercase;letter-spacing:1px}}
.pc .cn{{color:#f8fafc;font-weight:800;font-size:14px;margin:2px 0}}.pc .tr{{color:#475569;font-size:9px}}
.bt{{background:#111827;border:1px solid #1e293b;border-radius:8px;padding:14px;margin-bottom:8px;display:grid;grid-template-columns:1fr auto 1fr;gap:16px;align-items:center}}
.bt.hot{{border-left:3px solid #16a34a}}.bt.warm{{border-left:3px solid #ca8a04}}.bt.cool{{border-left:3px solid #6b7280}}
.bt .lb{{font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:1px}}
.bt .si{{font-size:14px;font-weight:700;margin-top:2px}}.bt .gn{{font-size:11px;color:#94a3b8;margin-top:2px}}
.bt .dt{{font-size:10px;color:#475569;margin-top:2px}}.bt .od{{font-size:24px;font-weight:800;text-align:center}}
.bt .li{{font-size:10px;color:#94a3b8;text-align:center}}
.eb{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;color:#fff}}
.eh{{background:#16a34a}}.ew{{background:#ca8a04}}.ec{{background:#6b7280}}
.pb{{position:relative;height:8px;background:#1e293b;border-radius:4px;overflow:hidden;margin-top:4px}}
.pi{{position:absolute;left:0;top:0;height:100%;background:#475569;border-radius:4px}}
.pm{{position:absolute;left:0;top:0;height:100%;background:#4ade80;border-radius:4px;opacity:.7}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{padding:8px 6px;color:#64748b;font-weight:600;font-size:10px;cursor:pointer;user-select:none;border-bottom:2px solid #1e293b}}
th.sr{{color:#818cf8}}td{{padding:7px 6px;border-bottom:1px solid #1e293b}}tr:nth-child(even){{background:#0d1321}}
.pn{{background:#111827;border:1px solid #1e293b;border-radius:8px;padding:20px;margin-bottom:16px}}
.pn h3{{font-size:14px;font-weight:700;color:#818cf8;margin-bottom:12px}}
.tc{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.sb{{text-align:center;padding:12px;background:#0a0f1a;border-radius:6px}}
.sb .n{{font-size:28px;font-weight:800}}.sb .la{{font-size:11px;color:#64748b;margin-top:4px}}.sb .sm{{font-size:10px;color:#475569}}
.ff{{background:linear-gradient(135deg,#1e1b4b,#172554);border:1px solid #3730a3;border-radius:8px;padding:16px;text-align:center}}
.ff .fl{{font-size:10px;color:#818cf8;text-transform:uppercase;letter-spacing:2px;margin-bottom:12px}}
.ff .fc{{margin-top:12px;font-size:18px;font-weight:800;color:#fbbf24}}
@media(max-width:768px){{.g4{{grid-template-columns:1fr 1fr}}.pg{{grid-template-columns:1fr 1fr}}.tc{{grid-template-columns:1fr}}.bt{{grid-template-columns:1fr;gap:8px}}}}
</style></head><body>
<div class="hd"><div class="tl"><h1>NCAAB</h1><span class="su">BRACKET + EV</span><span class="ch" id="champLbl">🏆 PROJECTED: Duke Blue Devils</span></div>
<div class="mt"><span style="color:#4ade80">74.98% SU</span><span>•</span><span style="color:#fbbf24">56.9% ATS</span><span>•</span><span>F4: Duke | Florida | Michigan | Arizona</span><span>•</span><span id="ds"></span></div>
<div class="tabs"><button class="tab on" onclick="st('bracket',this)">Bracket</button><button class="tab" onclick="st('ev',this)">EV Bets</button><button class="tab" onclick="st('rankings',this)">Rankings</button><button class="tab" onclick="st('model',this)">Model</button></div></div>
<div class="ct"><div id="t-bracket"></div><div id="t-ev" class="hid"></div><div id="t-rankings" class="hid"></div><div id="t-model" class="hid"></div></div>
<script>
// === EMBEDDED BOT DATA ===
const bd={data_json};

const RC={{EAST:"#3b82f6",SOUTH:"#f97316",MIDWEST:"#10b981",WEST:"#a855f7"}};
const RN=["First Four","Round of 64","Round of 32","Sweet 16","Elite 8","Final Four","Championship"];
const B={{"First Four":[{{r:"EAST",sA:16,a:"Howard",scA:60,sB:16,b:"UMBC",scB:63,sp:-2.3,w:.419,win:"UMBC"}},{{r:"SOUTH",sA:11,a:"Santa Clara",scA:67,sB:11,b:"New Mexico",scB:66,sp:.5,w:.518,win:"Santa Clara"}},{{r:"MIDWEST",sA:16,a:"LIU",scA:63,sB:16,b:"Beth.-Cookman",scB:66,sp:-3.2,w:.388,win:"Beth.-Cookman"}},{{r:"WEST",sA:11,a:"TCU",scA:65,sB:11,b:"Indiana",scB:65,sp:.2,w:.507,win:"TCU"}}],"Round of 64":[{{r:"EAST",sA:1,a:"Duke",scA:81,sB:16,b:"UMBC",scB:44,sp:37.3,w:.995,win:"Duke"}},{{r:"EAST",sA:8,a:"UCF",scA:68,sB:9,b:"Missouri",scB:68,sp:0,w:.5,win:"Missouri"}},{{r:"EAST",sA:5,a:"Vanderbilt",scA:70,sB:12,b:"Liberty",scB:64,sp:6,w:.702,win:"Vanderbilt"}},{{r:"EAST",sA:4,a:"Gonzaga",scA:72,sB:13,b:"SFA",scB:55,sp:16.3,w:.911,win:"Gonzaga"}},{{r:"EAST",sA:6,a:"Louisville",scA:77,sB:11,b:"Miami OH",scB:63,sp:14.5,w:.888,win:"Louisville"}},{{r:"EAST",sA:3,a:"Iowa State",scA:76,sB:14,b:"Navy",scB:47,sp:29.3,w:.985,win:"Iowa State"}},{{r:"EAST",sA:7,a:"Utah State",scA:68,sB:10,b:"UCLA",scB:64,sp:4,w:.639,win:"Utah State"}},{{r:"EAST",sA:2,a:"Illinois",scA:77,sB:15,b:"ETSU",scB:54,sp:22.5,w:.961,win:"Illinois"}},{{r:"SOUTH",sA:1,a:"UConn",scA:69,sB:16,b:"Merrimack",scB:52,sp:17,w:.919,win:"UConn"}},{{r:"SOUTH",sA:8,a:"Saint Louis",scA:71,sB:9,b:"NC State",scB:67,sp:4.1,w:.642,win:"Saint Louis"}},{{r:"SOUTH",sA:5,a:"Tennessee",scA:68,sB:12,b:"S. Florida",scB:66,sp:2,w:.571,win:"Tennessee"}},{{r:"SOUTH",sA:4,a:"Kansas",scA:68,sB:13,b:"Utah Valley",scB:58,sp:9.7,w:.8,win:"Kansas"}},{{r:"SOUTH",sA:6,a:"St. John's",scA:69,sB:11,b:"Santa Clara",scB:66,sp:2.3,w:.581,win:"St. John's"}},{{r:"SOUTH",sA:3,a:"Purdue",scA:74,sB:14,b:"Hawai'i",scB:55,sp:18.8,w:.936,win:"Purdue"}},{{r:"SOUTH",sA:7,a:"Villanova",scA:67,sB:10,b:"Texas",scB:66,sp:.9,w:.532,win:"Villanova"}},{{r:"SOUTH",sA:2,a:"Florida",scA:77,sB:15,b:"Wright State",scB:58,sp:18.2,w:.931,win:"Florida"}},{{r:"MIDWEST",sA:1,a:"Michigan",scA:79,sB:16,b:"Beth.-Cookman",scB:56,sp:23.8,w:.968,win:"Michigan"}},{{r:"MIDWEST",sA:8,a:"Clemson",scA:61,sB:9,b:"Iowa",scB:61,sp:-.2,w:.493,win:"Iowa"}},{{r:"MIDWEST",sA:5,a:"Arkansas",scA:71,sB:12,b:"Yale",scB:67,sp:3.8,w:.632,win:"Arkansas"}},{{r:"MIDWEST",sA:4,a:"Virginia",scA:76,sB:13,b:"High Point",scB:56,sp:20.2,w:.947,win:"Virginia"}},{{r:"MIDWEST",sA:6,a:"BYU",scA:68,sB:11,b:"Ohio State",scB:67,sp:1.7,w:.56,win:"BYU"}},{{r:"MIDWEST",sA:3,a:"Nebraska",scA:70,sB:14,b:"Troy",scB:59,sp:10.5,w:.818,win:"Nebraska"}},{{r:"MIDWEST",sA:7,a:"Wisconsin",scA:71,sB:10,b:"Texas A&M",scB:70,sp:1.1,w:.539,win:"Wisconsin"}},{{r:"MIDWEST",sA:2,a:"Houston",scA:73,sB:15,b:"Austin Peay",scB:54,sp:19.1,w:.939,win:"Houston"}},{{r:"WEST",sA:1,a:"Arizona",scA:81,sB:16,b:"Tenn. State",scB:53,sp:28.4,w:.983,win:"Arizona"}},{{r:"WEST",sA:8,a:"Miami",scA:70,sB:9,b:"Georgia",scB:69,sp:.9,w:.532,win:"Miami"}},{{r:"WEST",sA:5,a:"UNC",scA:68,sB:12,b:"Belmont",scB:65,sp:2.8,w:.599,win:"UNC"}},{{r:"WEST",sA:4,a:"Alabama",scA:76,sB:13,b:"UNCW",scB:60,sp:15.3,w:.899,win:"Alabama"}},{{r:"WEST",sA:6,a:"Kentucky",scA:67,sB:11,b:"TCU",scB:65,sp:2.4,w:.585,win:"Kentucky"}},{{r:"WEST",sA:3,a:"Texas Tech",scA:76,sB:14,b:"ND State",scB:56,sp:20,w:.946,win:"Texas Tech"}},{{r:"WEST",sA:7,a:"Saint Mary's",scA:68,sB:10,b:"SMU",scB:64,sp:3.5,w:.622,win:"Saint Mary's"}},{{r:"WEST",sA:2,a:"Michigan St",scA:72,sB:15,b:"Portland St",scB:54,sp:18.5,w:.934,win:"Michigan St"}}],"Round of 32":[{{r:"EAST",a:"Duke",scA:70,b:"Missouri",scB:61,sp:9.2,w:.788,win:"Duke"}},{{r:"EAST",a:"Vanderbilt",scA:67,b:"Gonzaga",scB:70,sp:-2.6,w:.408,win:"Gonzaga"}},{{r:"EAST",a:"Louisville",scA:65,b:"Iowa State",scB:67,sp:-1.7,w:.44,win:"Iowa State"}},{{r:"EAST",a:"Illinois",scA:68,b:"Utah State",scB:66,sp:2.4,w:.585,win:"Illinois"}},{{r:"SOUTH",a:"UConn",scA:65,b:"Saint Louis",scB:65,sp:.3,w:.511,win:"UConn"}},{{r:"SOUTH",a:"Tennessee",scA:65,b:"Kansas",scB:64,sp:1,w:.536,win:"Tennessee"}},{{r:"SOUTH",a:"St. John's",scA:65,b:"Purdue",scB:66,sp:-.9,w:.468,win:"Purdue"}},{{r:"SOUTH",a:"Florida",scA:68,b:"Villanova",scB:64,sp:4.8,w:.665,win:"Florida"}},{{r:"MIDWEST",a:"Michigan",scA:67,b:"Iowa",scB:61,sp:6.1,w:.705,win:"Michigan"}},{{r:"MIDWEST",a:"Arkansas",scA:68,b:"Virginia",scB:69,sp:-1.1,w:.461,win:"Virginia"}},{{r:"MIDWEST",a:"BYU",scA:65,b:"Nebraska",scB:67,sp:-1.8,w:.436,win:"Nebraska"}},{{r:"MIDWEST",a:"Houston",scA:67,b:"Wisconsin",scB:62,sp:4.7,w:.662,win:"Houston"}},{{r:"WEST",a:"Arizona",scA:69,b:"Miami",scB:64,sp:4.9,w:.668,win:"Arizona"}},{{r:"WEST",a:"UNC",scA:70,b:"Alabama",scB:70,sp:-.5,w:.482,win:"Alabama"}},{{r:"WEST",a:"Kentucky",scA:66,b:"Texas Tech",scB:68,sp:-1.7,w:.44,win:"Texas Tech"}},{{r:"WEST",a:"Michigan St",scA:63,b:"Saint Mary's",scB:62,sp:.9,w:.532,win:"Michigan St"}}],"Sweet 16":[{{r:"EAST",a:"Duke",scA:66,b:"Gonzaga",scB:63,sp:2.4,w:.585,win:"Duke"}},{{r:"EAST",a:"Illinois",scA:66,b:"Iowa State",scB:65,sp:.8,w:.529,win:"Illinois"}},{{r:"SOUTH",a:"UConn",scA:65,b:"Tennessee",scB:63,sp:2.2,w:.578,win:"UConn"}},{{r:"SOUTH",a:"Florida",scA:67,b:"Purdue",scB:66,sp:1.1,w:.539,win:"Florida"}},{{r:"MIDWEST",a:"Michigan",scA:68,b:"Virginia",scB:64,sp:4.1,w:.642,win:"Michigan"}},{{r:"MIDWEST",a:"Houston",scA:63,b:"Nebraska",scB:64,sp:-1.1,w:.461,win:"Nebraska"}},{{r:"WEST",a:"Arizona",scA:73,b:"Alabama",scB:69,sp:4.3,w:.649,win:"Arizona"}},{{r:"WEST",a:"Michigan St",scA:66,b:"Texas Tech",scB:64,sp:1.4,w:.55,win:"Michigan St"}}],"Elite 8":[{{r:"EAST",a:"Duke",scA:67,b:"Illinois",scB:64,sp:2.9,w:.602,win:"Duke"}},{{r:"SOUTH",a:"UConn",scA:65,b:"Florida",scB:65,sp:-.5,w:.482,win:"Florida"}},{{r:"MIDWEST",a:"Michigan",scA:68,b:"Arizona",scB:67,sp:1,w:.536,win:"Michigan"}},{{r:"WEST",a:"Arizona",scA:66,b:"Michigan St",scB:63,sp:2.3,w:.581,win:"Arizona"}}],"Final Four":[{{r:"E vs S",a:"Duke",scA:67,b:"Florida",scB:64,sp:2.9,w:.602,win:"Duke"}},{{r:"MW vs W",a:"Michigan",scA:68,b:"Arizona",scB:67,sp:1,w:.536,win:"Michigan"}}],"Championship":[{{r:"NATL",a:"Duke",scA:66,b:"Michigan",scB:65,sp:.7,w:.525,win:"Duke"}}]}};

let cr="Round of 64",cg="ALL",sc="rk",sd=1;
function st(id,el){{['bracket','ev','rankings','model'].forEach(t=>{{document.getElementById('t-'+t).classList.add('hid')}});document.getElementById('t-'+id).classList.remove('hid');document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));el.classList.add('on')}}
function gc(g){{const c=g.r?g.r.toLowerCase().split(' ')[0]:'';const u=g.w<.5;return`<div class="gm ${{c}}"><div class="rw"><span class="${{g.win===g.a?'w':'l'}}">${{g.sA!=null?'<span class="sd">'+g.sA+'</span>':''}}${{g.a}}</span><span class="sc">${{g.scA}}</span></div><div class="rw"><span class="${{g.win===g.b?'w':'l'}}">${{g.sB!=null?'<span class="sd">'+g.sB+'</span>':''}}${{g.b}}</span><span class="sc">${{g.scB}}</span></div><div class="mr"><span>${{g.sp>0?'+':''}}${{g.sp.toFixed(1)}}</span><span>${{(g.w*100).toFixed(0)}}-${{((1-g.w)*100).toFixed(0)}}%</span>${{u?'<span class="up">UPSET</span>':''}}</div></div>`}}
function rb(){{let gm=B[cr]||[];if(cg!=="ALL")gm=gm.filter(g=>g.r===cg||g.r?.includes(cg.substring(0,2)));const p=RN.map(r=>`<button class="pl ${{r===cr?'on':''}}" onclick="cr='${{r}}';rb()">${{r}}</button>`).join('');const rg=["ALL","EAST","SOUTH","MIDWEST","WEST"].map(r=>`<button class="rb ${{r===cg?'on':''}}" style="color:${{r===cg?'#f8fafc':(RC[r]||'#94a3b8')}};${{r===cg?'background:'+(RC[r]||'#475569')+';':''}}border-color:${{RC[r]||'#334155'}}" onclick="cg='${{r}}';rb()">${{r}}</button>`).join('');let bd2='';if(cr==="Final Four"||cr==="Championship"){{bd2=`<div class="ff"><div class="fl">${{cr==="Championship"?"NATIONAL CHAMPIONSHIP":"FINAL FOUR"}}</div>${{gm.map(gc).join('')}}${{cr==="Championship"?'<div class="fc">🏆 Duke — Projected Champions</div>':''}}</div>`}}else{{const cl=gm.length>8?'g4':gm.length>4?'g2':'g1';bd2=`<div class="gg ${{cl}}">${{gm.map(gc).join('')}}</div>`}}document.getElementById('t-bracket').innerHTML=`<div class="pls">${{p}}</div><div class="rgs">${{rg}}</div>${{bd2}}<div class="pt"><h3>Region Champions</h3><div class="pg"><div class="pc" style="border-top:2px solid #3b82f6"><div class="rn" style="color:#3b82f6">EAST</div><div class="cn">Duke</div><div class="tr">UMBC→Missouri→Gonzaga→Illinois</div></div><div class="pc" style="border-top:2px solid #f97316"><div class="rn" style="color:#f97316">SOUTH</div><div class="cn">Florida</div><div class="tr">Wright St→Villanova→Purdue→UConn</div></div><div class="pc" style="border-top:2px solid #10b981"><div class="rn" style="color:#10b981">MIDWEST</div><div class="cn">Michigan</div><div class="tr">Beth-Cook→Iowa→Virginia→Arizona</div></div><div class="pc" style="border-top:2px solid #a855f7"><div class="rn" style="color:#a855f7">WEST</div><div class="cn">Arizona</div><div class="tr">Tenn St→Miami→Alabama→Michigan St</div></div></div></div>`}}
function rev(){{const el=document.getElementById('t-ev');if(!bd||!bd.ev_bets||!bd.ev_bets.length){{el.innerHTML='<p style="color:#94a3b8">No EV bets loaded. Run bot first.</p>';return}}el.innerHTML=`<div style="font-size:12px;color:#94a3b8;margin-bottom:14px">${{bd.ev_bets.length}} +EV bets — ${{bd.date}}</div>`+bd.ev_bets.slice(0,30).map(b=>{{const e=b.ev_pct>=6?'hot':b.ev_pct>=4?'warm':'cool';const o=b.odds>0?'+'+b.odds:''+b.odds;const ed=((b.model_prob-b.implied)*100).toFixed(1);return`<div class="bt ${{e}}"><div><div class="lb">${{b.type}} • ${{b.book}}</div><div class="si">${{b.side}}</div><div class="gn">${{b.game}}</div><div class="dt">Pred: ${{b.pred}} • Spread: ${{b.model_spread>0?'+':''}}${{b.model_spread}}</div></div><div style="text-align:center"><div class="od">${{o}}</div>${{b.line!=null?`<div class="li">Line: ${{b.line>0?'+':''}}${{b.line}}</div>`:''}}` + `<span class="eb e${{e[0]}}">+${{b.ev_pct}}% EV</span></div><div><div style="display:flex;justify-content:space-between;font-size:10px;color:#64748b;margin-bottom:2px"><span>Probability</span><span style="color:#4ade80">Edge: +${{ed}}%</span></div><div class="pb"><div class="pi" style="width:${{b.implied*100}}%"></div><div class="pm" style="width:${{b.model_prob*100}}%"></div></div><div style="display:flex;justify-content:space-between;font-size:9px;color:#475569;margin-top:1px"><span>Model: ${{(b.model_prob*100).toFixed(0)}}%</span><span>Market: ${{(b.implied*100).toFixed(0)}}%</span></div></div></div>`}}).join('')}}
function rrk(){{const T=bd&&bd.top_25?bd.top_25.map((t,i)=>({{rk:t.rank||i+1,nm:t.name,cf:t.conf||'',rc:t.record,sr:t.sor,ss:t.sos||0,po:t.ppp_off,pd:t.ppp_def,q:t.qual}})):[{{rk:1,nm:"Michigan",rc:"27-2",sr:.833,ss:3,po:1.236,pd:.96,q:"13-2",cf:"Big Ten"}}];const s=[...T].sort((a,b)=>{{const av=a[sc],bv=b[sc];return typeof av==='number'?(av-bv)*sd:String(av||'').localeCompare(String(bv||''))*sd}});const cols=[{{k:'rk',l:'#'}},{{k:'nm',l:'TEAM'}},{{k:'cf',l:'CONF'}},{{k:'rc',l:'REC'}},{{k:'sr',l:'SOR'}},{{k:'ss',l:'SOS'}},{{k:'po',l:'PPP↑'}},{{k:'pd',l:'PPP↓'}},{{k:'q',l:'QUAL'}}];document.getElementById('t-rankings').innerHTML=`<div style="overflow-x:auto"><table><thead><tr>${{cols.map(c=>`<th class="${{sc===c.k?'sr':''}}" style="text-align:${{c.k==='nm'?'left':'center'}}" onclick="if(sc==='${{c.k}}')sd=-sd;else{{sc='${{c.k}}';sd=1}};rrk()">${{c.l}}${{sc===c.k?(sd===1?' ▲':' ▼'):''}}</th>`).join('')}}</tr></thead><tbody>${{s.map(t=>`<tr><td style="text-align:center;font-weight:800;color:${{t.rk<=4?'#818cf8':t.rk<=10?'#f8fafc':'#94a3b8'}}">${{t.rk}}</td><td style="font-weight:600">${{t.nm}}</td><td style="text-align:center;color:#64748b;font-size:10px">${{t.cf}}</td><td style="text-align:center">${{t.rc}}</td><td style="text-align:center;font-weight:700;color:${{t.sr>=.7?'#4ade80':t.sr>=.6?'#fbbf24':'#94a3b8'}}">${{t.sr.toFixed(3)}}</td><td style="text-align:center">${{t.ss}}</td><td style="text-align:center;color:${{t.po>=1.2?'#4ade80':'#e2e8f0'}}">${{t.po.toFixed(3)}}</td><td style="text-align:center;color:${{t.pd<=.97?'#4ade80':t.pd>=1.05?'#f87171':'#e2e8f0'}}">${{t.pd.toFixed(3)}}</td><td style="text-align:center">${{t.q}}</td></tr>`).join('')}}</tbody></table></div>`}}
document.getElementById('t-model').innerHTML=`<div class="tc"><div class="pn"><h3>Model Architecture</h3><div style="font-size:12px;line-height:1.8;color:#94a3b8"><div><span style="color:#4ade80">→</span> Blended PPP = Off_w × PPP_off(adj) + Def_w × PPP_def(adj)</div><div><span style="color:#4ade80">→</span> SOS Adj = PPP × ((366-SOS_RK)/365)^α</div><div><span style="color:#4ade80">→</span> Pace = 0.65×min(A,B) + 0.35×max(A,B)</div><div><span style="color:#4ade80">→</span> Score = PPP×Pace + HCA + SOR_adj + Foul</div><div><span style="color:#4ade80">→</span> Win% = 1/(1+e^(-spread/18))</div></div></div><div class="pn"><h3>Backtest</h3><div class="tc"><div class="sb"><div class="n" style="color:#4ade80">74.98%</div><div class="la">Straight Up</div><div class="sm">3,290 games</div></div><div class="sb"><div class="n" style="color:#fbbf24">56.94%</div><div class="la">ATS (5pt edge)</div><div class="sm">353 bets</div></div></div><div style="margin-top:12px;font-size:12px;color:#94a3b8"><b style="color:#f8fafc">Params:</b> Off=0.44 Def=0.43 SOR=0.03 HCA=1 Scale=18</div></div></div>`;
if(bd){{document.getElementById('ds').innerHTML=`<span style="color:#4ade80">● ${{bd.date}} — ${{bd.ev_bets.length}} EV bets</span>`}}else{{document.getElementById('ds').innerHTML='<span style="color:#fbbf24">○ No data</span>'}}
rb();rev();rrk();
</script></body></html>'''


if __name__ == "__main__":
    main()
