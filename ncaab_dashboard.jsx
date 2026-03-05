import { useState, useMemo } from "react";

const REGION_COLORS = { EAST:"#3b82f6", SOUTH:"#f97316", MIDWEST:"#10b981", WEST:"#a855f7" };
const font = "'JetBrains Mono','SF Mono','Fira Code',monospace";
const BACKTEST = { win_rate:74.98, ats_rate:56.9, n:3290, edge5_rate:56.94, edge5_n:353 };

const BRACKET = {
  firstFour: [
    { region:"EAST", seedA:16, teamA:"Howard", scoreA:60.2, seedB:16, teamB:"UMBC", scoreB:62.5, spread:-2.3, winA:0.419, winner:"UMBC" },
    { region:"SOUTH", seedA:11, teamA:"Santa Clara", scoreA:66.8, seedB:11, teamB:"New Mexico", scoreB:66.3, spread:0.5, winA:0.518, winner:"Santa Clara" },
    { region:"MIDWEST", seedA:16, teamA:"LIU", scoreA:62.7, seedB:16, teamB:"Beth.-Cookman", scoreB:65.9, spread:-3.2, winA:0.388, winner:"Beth.-Cookman" },
    { region:"WEST", seedA:11, teamA:"TCU", scoreA:65.3, seedB:11, teamB:"Indiana", scoreB:65.1, spread:0.2, winA:0.507, winner:"TCU" },
  ],
  rounds: {
    "Round of 64": [
      { region:"EAST", seedA:1, teamA:"Duke", scoreA:81.0, seedB:16, teamB:"UMBC", scoreB:43.7, spread:37.3, winA:0.995, winner:"Duke" },
      { region:"EAST", seedA:8, teamA:"UCF", scoreA:68.2, seedB:9, teamB:"Missouri", scoreB:68.2, spread:0.0, winA:0.500, winner:"Missouri" },
      { region:"EAST", seedA:5, teamA:"Vanderbilt", scoreA:69.6, seedB:12, teamB:"Liberty", scoreB:63.6, spread:6.0, winA:0.702, winner:"Vanderbilt" },
      { region:"EAST", seedA:4, teamA:"Gonzaga", scoreA:71.7, seedB:13, teamB:"SFA", scoreB:55.4, spread:16.3, winA:0.911, winner:"Gonzaga" },
      { region:"EAST", seedA:6, teamA:"Louisville", scoreA:77.0, seedB:11, teamB:"Miami OH", scoreB:62.5, spread:14.5, winA:0.888, winner:"Louisville" },
      { region:"EAST", seedA:3, teamA:"Iowa State", scoreA:75.9, seedB:14, teamB:"Navy", scoreB:46.6, spread:29.3, winA:0.985, winner:"Iowa State" },
      { region:"EAST", seedA:7, teamA:"Utah State", scoreA:67.6, seedB:10, teamB:"UCLA", scoreB:63.6, spread:4.0, winA:0.639, winner:"Utah State" },
      { region:"EAST", seedA:2, teamA:"Illinois", scoreA:76.6, seedB:15, teamB:"ETSU", scoreB:54.1, spread:22.5, winA:0.961, winner:"Illinois" },
      { region:"SOUTH", seedA:1, teamA:"UConn", scoreA:69.2, seedB:16, teamB:"Merrimack", scoreB:52.2, spread:17.0, winA:0.919, winner:"UConn" },
      { region:"SOUTH", seedA:8, teamA:"Saint Louis", scoreA:70.7, seedB:9, teamB:"NC State", scoreB:66.6, spread:4.1, winA:0.642, winner:"Saint Louis" },
      { region:"SOUTH", seedA:5, teamA:"Tennessee", scoreA:68.4, seedB:12, teamB:"S. Florida", scoreB:66.4, spread:2.0, winA:0.571, winner:"Tennessee" },
      { region:"SOUTH", seedA:4, teamA:"Kansas", scoreA:67.9, seedB:13, teamB:"Utah Valley", scoreB:58.2, spread:9.7, winA:0.800, winner:"Kansas" },
      { region:"SOUTH", seedA:6, teamA:"St. John's", scoreA:68.5, seedB:11, teamB:"Santa Clara", scoreB:66.2, spread:2.3, winA:0.581, winner:"St. John's" },
      { region:"SOUTH", seedA:3, teamA:"Purdue", scoreA:74.1, seedB:14, teamB:"Hawai'i", scoreB:55.3, spread:18.8, winA:0.936, winner:"Purdue" },
      { region:"SOUTH", seedA:7, teamA:"Villanova", scoreA:67.1, seedB:10, teamB:"Texas", scoreB:66.2, spread:0.9, winA:0.532, winner:"Villanova" },
      { region:"SOUTH", seedA:2, teamA:"Florida", scoreA:76.5, seedB:15, teamB:"Wright State", scoreB:58.3, spread:18.2, winA:0.931, winner:"Florida" },
      { region:"MIDWEST", seedA:1, teamA:"Michigan", scoreA:79.3, seedB:16, teamB:"Beth.-Cookman", scoreB:55.5, spread:23.8, winA:0.968, winner:"Michigan" },
      { region:"MIDWEST", seedA:8, teamA:"Clemson", scoreA:60.7, seedB:9, teamB:"Iowa", scoreB:60.9, spread:-0.2, winA:0.493, winner:"Iowa" },
      { region:"MIDWEST", seedA:5, teamA:"Arkansas", scoreA:70.9, seedB:12, teamB:"Yale", scoreB:67.1, spread:3.8, winA:0.632, winner:"Arkansas" },
      { region:"MIDWEST", seedA:4, teamA:"Virginia", scoreA:76.4, seedB:13, teamB:"High Point", scoreB:56.2, spread:20.2, winA:0.947, winner:"Virginia" },
      { region:"MIDWEST", seedA:6, teamA:"BYU", scoreA:68.4, seedB:11, teamB:"Ohio State", scoreB:66.7, spread:1.7, winA:0.560, winner:"BYU" },
      { region:"MIDWEST", seedA:3, teamA:"Nebraska", scoreA:69.6, seedB:14, teamB:"Troy", scoreB:59.1, spread:10.5, winA:0.818, winner:"Nebraska" },
      { region:"MIDWEST", seedA:7, teamA:"Wisconsin", scoreA:70.9, seedB:10, teamB:"Texas A&M", scoreB:69.8, spread:1.1, winA:0.539, winner:"Wisconsin" },
      { region:"MIDWEST", seedA:2, teamA:"Houston", scoreA:72.7, seedB:15, teamB:"Austin Peay", scoreB:53.6, spread:19.1, winA:0.939, winner:"Houston" },
      { region:"WEST", seedA:1, teamA:"Arizona", scoreA:81.2, seedB:16, teamB:"Tenn. State", scoreB:52.8, spread:28.4, winA:0.983, winner:"Arizona" },
      { region:"WEST", seedA:8, teamA:"Miami", scoreA:69.5, seedB:9, teamB:"Georgia", scoreB:68.6, spread:0.9, winA:0.532, winner:"Miami" },
      { region:"WEST", seedA:5, teamA:"UNC", scoreA:68.2, seedB:12, teamB:"Belmont", scoreB:65.4, spread:2.8, winA:0.599, winner:"UNC" },
      { region:"WEST", seedA:4, teamA:"Alabama", scoreA:75.7, seedB:13, teamB:"UNCW", scoreB:60.4, spread:15.3, winA:0.899, winner:"Alabama" },
      { region:"WEST", seedA:6, teamA:"Kentucky", scoreA:67.2, seedB:11, teamB:"TCU", scoreB:64.8, spread:2.4, winA:0.585, winner:"Kentucky" },
      { region:"WEST", seedA:3, teamA:"Texas Tech", scoreA:76.2, seedB:14, teamB:"ND State", scoreB:56.2, spread:20.0, winA:0.946, winner:"Texas Tech" },
      { region:"WEST", seedA:7, teamA:"Saint Mary's", scoreA:67.5, seedB:10, teamB:"SMU", scoreB:64.0, spread:3.5, winA:0.622, winner:"Saint Mary's" },
      { region:"WEST", seedA:2, teamA:"Michigan St", scoreA:72.1, seedB:15, teamB:"Portland St", scoreB:53.6, spread:18.5, winA:0.934, winner:"Michigan St" },
    ],
    "Round of 32": [
      { region:"EAST", teamA:"Duke", scoreA:69.8, teamB:"Missouri", scoreB:60.6, spread:9.2, winA:0.788, winner:"Duke" },
      { region:"EAST", teamA:"Vanderbilt", scoreA:66.9, teamB:"Gonzaga", scoreB:69.5, spread:-2.6, winA:0.408, winner:"Gonzaga" },
      { region:"EAST", teamA:"Louisville", scoreA:65.1, teamB:"Iowa State", scoreB:66.8, spread:-1.7, winA:0.440, winner:"Iowa State" },
      { region:"EAST", teamA:"Illinois", scoreA:67.9, teamB:"Utah State", scoreB:65.5, spread:2.4, winA:0.585, winner:"Illinois" },
      { region:"SOUTH", teamA:"UConn", scoreA:65.0, teamB:"Saint Louis", scoreB:64.7, spread:0.3, winA:0.511, winner:"UConn" },
      { region:"SOUTH", teamA:"Tennessee", scoreA:64.5, teamB:"Kansas", scoreB:63.5, spread:1.0, winA:0.536, winner:"Tennessee" },
      { region:"SOUTH", teamA:"St. John's", scoreA:65.4, teamB:"Purdue", scoreB:66.3, spread:-0.9, winA:0.468, winner:"Purdue" },
      { region:"SOUTH", teamA:"Florida", scoreA:68.4, teamB:"Villanova", scoreB:63.6, spread:4.8, winA:0.665, winner:"Florida" },
      { region:"MIDWEST", teamA:"Michigan", scoreA:66.7, teamB:"Iowa", scoreB:60.6, spread:6.1, winA:0.705, winner:"Michigan" },
      { region:"MIDWEST", teamA:"Arkansas", scoreA:68.0, teamB:"Virginia", scoreB:69.1, spread:-1.1, winA:0.461, winner:"Virginia" },
      { region:"MIDWEST", teamA:"BYU", scoreA:64.8, teamB:"Nebraska", scoreB:66.6, spread:-1.8, winA:0.436, winner:"Nebraska" },
      { region:"MIDWEST", teamA:"Houston", scoreA:66.6, teamB:"Wisconsin", scoreB:61.9, spread:4.7, winA:0.662, winner:"Houston" },
      { region:"WEST", teamA:"Arizona", scoreA:69.1, teamB:"Miami", scoreB:64.2, spread:4.9, winA:0.668, winner:"Arizona" },
      { region:"WEST", teamA:"UNC", scoreA:69.9, teamB:"Alabama", scoreB:70.4, spread:-0.5, winA:0.482, winner:"Alabama" },
      { region:"WEST", teamA:"Kentucky", scoreA:66.1, teamB:"Texas Tech", scoreB:67.8, spread:-1.7, winA:0.440, winner:"Texas Tech" },
      { region:"WEST", teamA:"Michigan St", scoreA:62.8, teamB:"Saint Mary's", scoreB:61.9, spread:0.9, winA:0.532, winner:"Michigan St" },
    ],
    "Sweet 16": [
      { region:"EAST", teamA:"Duke", scoreA:65.5, teamB:"Gonzaga", scoreB:63.1, spread:2.4, winA:0.585, winner:"Duke" },
      { region:"EAST", teamA:"Illinois", scoreA:65.9, teamB:"Iowa State", scoreB:65.1, spread:0.8, winA:0.529, winner:"Illinois" },
      { region:"SOUTH", teamA:"UConn", scoreA:64.7, teamB:"Tennessee", scoreB:62.5, spread:2.2, winA:0.578, winner:"UConn" },
      { region:"SOUTH", teamA:"Florida", scoreA:67.4, teamB:"Purdue", scoreB:66.3, spread:1.1, winA:0.539, winner:"Florida" },
      { region:"MIDWEST", teamA:"Michigan", scoreA:68.2, teamB:"Virginia", scoreB:64.1, spread:4.1, winA:0.642, winner:"Michigan" },
      { region:"MIDWEST", teamA:"Houston", scoreA:62.7, teamB:"Nebraska", scoreB:63.8, spread:-1.1, winA:0.461, winner:"Nebraska" },
      { region:"WEST", teamA:"Arizona", scoreA:73.4, teamB:"Alabama", scoreB:69.1, spread:4.3, winA:0.649, winner:"Arizona" },
      { region:"WEST", teamA:"Michigan St", scoreA:65.5, teamB:"Texas Tech", scoreB:64.1, spread:1.4, winA:0.550, winner:"Michigan St" },
    ],
    "Elite 8": [
      { region:"EAST", teamA:"Duke", scoreA:66.7, teamB:"Illinois", scoreB:63.8, spread:2.9, winA:0.602, winner:"Duke" },
      { region:"SOUTH", teamA:"UConn", scoreA:64.8, teamB:"Florida", scoreB:65.3, spread:-0.5, winA:0.482, winner:"Florida" },
      { region:"MIDWEST", teamA:"Michigan", scoreA:68.4, teamB:"Arizona", scoreB:67.4, spread:1.0, winA:0.536, winner:"Michigan" },
      { region:"WEST", teamA:"Arizona", scoreA:65.7, teamB:"Michigan St", scoreB:63.4, spread:2.3, winA:0.581, winner:"Arizona" },
    ],
    "Final Four": [
      { region:"E vs S", teamA:"Duke", scoreA:66.9, teamB:"Florida", scoreB:64.0, spread:2.9, winA:0.602, winner:"Duke" },
      { region:"MW vs W", teamA:"Michigan", scoreA:68.4, teamB:"Arizona", scoreB:67.4, spread:1.0, winA:0.536, winner:"Michigan" },
    ],
    "Championship": [
      { region:"NATL", teamA:"Duke", scoreA:65.6, teamB:"Michigan", scoreB:64.9, spread:0.7, winA:0.525, winner:"Duke" },
    ],
  },
};

const TOP25 = [
  { rank:1, name:"Michigan Wolverines", conf:"Big Ten", record:"27-2", sor:0.833, sos:2, pppO:1.236, pppD:0.960, qual:"13-2" },
  { rank:2, name:"Duke Blue Devils", conf:"ACC", record:"28-2", sor:0.805, sos:14, pppO:1.253, pppD:0.931, qual:"12-2" },
  { rank:3, name:"Arizona Wildcats", conf:"Big 12", record:"28-2", sor:0.796, sos:24, pppO:1.224, pppD:0.950, qual:"14-2" },
  { rank:4, name:"UConn Huskies", conf:"Big East", record:"27-3", sor:0.747, sos:9, pppO:1.186, pppD:0.986, qual:"11-3" },
  { rank:5, name:"Michigan State", conf:"Big Ten", record:"24-5", sor:0.721, sos:7, pppO:1.179, pppD:1.000, qual:"12-5" },
  { rank:6, name:"Florida Gators", conf:"SEC", record:"23-6", sor:0.701, sos:3, pppO:1.216, pppD:0.989, qual:"13-5" },
  { rank:7, name:"Alabama", conf:"SEC", record:"22-7", sor:0.675, sos:1, pppO:1.237, pppD:1.114, qual:"14-5" },
  { rank:8, name:"Houston Cougars", conf:"Big 12", record:"24-5", sor:0.669, sos:32, pppO:1.196, pppD:0.969, qual:"9-5" },
  { rank:9, name:"Purdue", conf:"Big Ten", record:"22-7", sor:0.663, sos:6, pppO:1.252, pppD:1.059, qual:"12-6" },
  { rank:10, name:"Illinois", conf:"Big Ten", record:"22-7", sor:0.653, sos:5, pppO:1.271, pppD:1.045, qual:"11-6" },
  { rank:11, name:"Auburn Tigers", conf:"SEC", record:"24-5", sor:0.652, sos:26, pppO:1.206, pppD:1.033, qual:"10-5" },
  { rank:12, name:"Iowa State", conf:"Big 12", record:"24-5", sor:0.649, sos:39, pppO:1.145, pppD:0.935, qual:"10-5" },
  { rank:13, name:"Tennessee", conf:"SEC", record:"22-7", sor:0.645, sos:4, pppO:1.201, pppD:1.013, qual:"12-7" },
  { rank:14, name:"Marquette", conf:"Big East", record:"24-5", sor:0.631, sos:51, pppO:1.201, pppD:0.976, qual:"8-4" },
  { rank:15, name:"Kansas", conf:"Big 12", record:"21-8", sor:0.624, sos:10, pppO:1.230, pppD:1.076, qual:"12-7" },
  { rank:16, name:"St. John's", conf:"Big East", record:"23-6", sor:0.611, sos:55, pppO:1.147, pppD:0.971, qual:"9-6" },
  { rank:17, name:"Wisconsin", conf:"Big Ten", record:"22-7", sor:0.598, sos:18, pppO:1.128, pppD:0.987, qual:"9-5" },
  { rank:18, name:"Texas A&M", conf:"SEC", record:"21-8", sor:0.592, sos:11, pppO:1.119, pppD:0.972, qual:"11-7" },
  { rank:19, name:"Louisville", conf:"ACC", record:"23-6", sor:0.585, sos:62, pppO:1.134, pppD:0.944, qual:"8-5" },
  { rank:20, name:"Oregon Ducks", conf:"Big Ten", record:"21-8", sor:0.583, sos:8, pppO:1.117, pppD:1.012, qual:"11-7" },
];

const EV_BETS = [
  { game:"Houston @ Florida", type:"ML", side:"Florida Gators", odds:145, book:"draftkings", spread:3.1, ev:7.2, model:0.52, implied:0.408, score:"72-69" },
  { game:"Iowa St @ Kansas", type:"SPREAD", side:"AWAY (Iowa State)", line:3.5, odds:-105, book:"betmgm", spread:-1.2, ev:6.1, model:0.59, implied:0.512, score:"68-69" },
  { game:"Auburn @ Tennessee", type:"ML", side:"Tennessee Vols", odds:-135, book:"draftkings", spread:4.5, ev:5.5, model:0.63, implied:0.574, score:"74-70" },
  { game:"Alabama @ Michigan", type:"SPREAD", side:"HOME (Michigan)", line:-5.5, odds:-110, book:"fanduel", spread:8.2, ev:4.8, model:0.58, implied:0.524, score:"78-70" },
  { game:"Duke @ Arizona", type:"TOTAL", side:"OVER 149.5", line:149.5, odds:-110, book:"fanduel", spread:1.3, ev:3.9, model:0.57, implied:0.524, score:"79-77" },
];

function Game({ g, compact }) {
  const isUpset = g.winA < 0.5;
  const rc = REGION_COLORS[g.region] || "#64748b";
  return (
    <div style={{ background:"#111827", border:"1px solid #1e293b", borderRadius:compact?6:8, padding:compact?"6px 10px":12, borderLeft:`3px solid ${rc}`, marginBottom:compact?4:6 }}>
      {!compact && <div style={{ fontSize:9, color:rc, textTransform:"uppercase", letterSpacing:1, marginBottom:4 }}>{g.region}</div>}
      <div style={{ display:"flex", justifyContent:"space-between", fontSize:compact?11:13 }}>
        <span style={{ color:g.winner===g.teamA?"#f8fafc":"#64748b", fontWeight:g.winner===g.teamA?700:400 }}>
          {g.seedA!=null && <span style={{color:"#475569",fontSize:compact?9:10,marginRight:3}}>{g.seedA}</span>}{g.teamA}
        </span>
        <span style={{ color:"#94a3b8", minWidth:28, textAlign:"right" }}>{Math.round(g.scoreA)}</span>
      </div>
      <div style={{ display:"flex", justifyContent:"space-between", fontSize:compact?11:13, marginTop:1 }}>
        <span style={{ color:g.winner===g.teamB?"#f8fafc":"#64748b", fontWeight:g.winner===g.teamB?700:400 }}>
          {g.seedB!=null && <span style={{color:"#475569",fontSize:compact?9:10,marginRight:3}}>{g.seedB}</span>}{g.teamB}
        </span>
        <span style={{ color:"#94a3b8", minWidth:28, textAlign:"right" }}>{Math.round(g.scoreB)}</span>
      </div>
      <div style={{ display:"flex", justifyContent:"space-between", fontSize:compact?9:10, color:"#475569", marginTop:compact?2:4, borderTop:compact?"none":"1px solid #1e293b", paddingTop:compact?0:4 }}>
        <span>{g.spread>0?"+":""}{g.spread.toFixed(1)}</span>
        <span>{(g.winA*100).toFixed(0)}–{((1-g.winA)*100).toFixed(0)}%</span>
        {isUpset && <span style={{color:"#fbbf24"}}>UPSET</span>}
      </div>
    </div>
  );
}

const TABS = ["Bracket", "EV Bets", "Rankings", "Model", "Setup"];

export default function App() {
  const [tab, setTab] = useState("Bracket");
  const [round, setRound] = useState("Round of 64");
  const [region, setRegion] = useState("ALL");
  const [sortCol, setSortCol] = useState("rank");
  const [sortDir, setSortDir] = useState(1);
  const rounds = ["First Four","Round of 64","Round of 32","Sweet 16","Elite 8","Final Four","Championship"];

  const games = useMemo(() => {
    if (round === "First Four") return BRACKET.firstFour;
    const g = BRACKET.rounds[round] || [];
    return region === "ALL" ? g : g.filter(x => x.region === region || x.region?.includes(region?.substring(0,2)));
  }, [round, region]);

  const sorted = useMemo(() => [...TOP25].sort((a,b) => {
    const av=a[sortCol], bv=b[sortCol];
    return typeof av==="number" ? (av-bv)*sortDir : String(av).localeCompare(String(bv))*sortDir;
  }), [sortCol, sortDir]);

  return (
    <div style={{ fontFamily:font, background:"#0a0f1a", color:"#e2e8f0", minHeight:"100vh" }}>
      <div style={{ background:"linear-gradient(135deg,#0f172a 0%,#1e1b4b 50%,#0f172a 100%)", borderBottom:"1px solid #1e293b", padding:"16px 24px 0" }}>
        <div style={{ display:"flex", alignItems:"baseline", gap:12, flexWrap:"wrap", marginBottom:4 }}>
          <span style={{ fontSize:22, fontWeight:800, letterSpacing:-1 }}>NCAAB</span>
          <span style={{ fontSize:22, fontWeight:300, color:"#818cf8" }}>BRACKET + EV</span>
          <span style={{ fontSize:11, color:"#fbbf24", marginLeft:"auto", fontWeight:700 }}>🏆 PROJECTED: Duke Blue Devils</span>
        </div>
        <div style={{ display:"flex", gap:10, fontSize:10, color:"#64748b", marginBottom:12, flexWrap:"wrap" }}>
          <span style={{color:"#4ade80"}}>{BACKTEST.win_rate}% SU</span><span>•</span>
          <span style={{color:"#fbbf24"}}>{BACKTEST.ats_rate}% ATS</span><span>•</span>
          <span>F4: Duke | Florida | Michigan | Arizona</span>
        </div>
        <div style={{ display:"flex", gap:0, overflowX:"auto" }}>
          {TABS.map(t => (
            <button key={t} onClick={() => setTab(t)} style={{
              padding:"10px 18px", fontSize:12, fontWeight:tab===t?700:400, color:tab===t?"#f8fafc":"#64748b",
              background:tab===t?"#1e293b":"transparent", border:"none",
              borderBottom:tab===t?"2px solid #818cf8":"2px solid transparent",
              cursor:"pointer", fontFamily:"inherit", borderRadius:"6px 6px 0 0", whiteSpace:"nowrap"
            }}>{t}</button>
          ))}
        </div>
      </div>

      <div style={{ padding:20 }}>
        {tab === "Bracket" && (<div>
          <div style={{ display:"flex", gap:4, marginBottom:10, flexWrap:"wrap" }}>
            {rounds.map(r => (
              <button key={r} onClick={() => setRound(r)} style={{
                padding:"5px 12px", fontSize:11, fontWeight:round===r?700:400, color:round===r?"#f8fafc":"#94a3b8",
                background:round===r?"#818cf8":"#1e293b", border:"1px solid", borderColor:round===r?"#818cf8":"#334155",
                borderRadius:20, cursor:"pointer", fontFamily:"inherit"
              }}>{r}</button>
            ))}
          </div>
          <div style={{ display:"flex", gap:4, marginBottom:14 }}>
            {["ALL","EAST","SOUTH","MIDWEST","WEST"].map(r => (
              <button key={r} onClick={() => setRegion(r)} style={{
                padding:"3px 10px", fontSize:10, fontWeight:region===r?700:400,
                color:region===r?"#f8fafc":REGION_COLORS[r]||"#94a3b8",
                background:region===r?(REGION_COLORS[r]||"#475569"):"transparent",
                border:`1px solid ${REGION_COLORS[r]||"#334155"}`, borderRadius:4, cursor:"pointer", fontFamily:"inherit"
              }}>{r}</button>
            ))}
          </div>

          {(round==="Final Four"||round==="Championship") ? (
            <div style={{ background:"linear-gradient(135deg,#1e1b4b,#172554)", border:"1px solid #3730a3", borderRadius:8, padding:16, textAlign:"center" }}>
              <div style={{ fontSize:10, color:"#818cf8", textTransform:"uppercase", letterSpacing:2, marginBottom:12 }}>
                {round==="Championship"?"NATIONAL CHAMPIONSHIP":"FINAL FOUR"}
              </div>
              {games.map((g,i) => <Game key={i} g={g} compact={false} />)}
              {round==="Championship" && <div style={{ marginTop:12, fontSize:18, fontWeight:800, color:"#fbbf24" }}>🏆 Duke Blue Devils — Projected Champions</div>}
            </div>
          ) : (
            <div style={{ display:"grid", gridTemplateColumns:games.length>8?"repeat(4,1fr)":games.length>4?"1fr 1fr":"1fr", gap:6 }}>
              {games.map((g,i) => <Game key={i} g={g} compact={games.length>8} />)}
            </div>
          )}

          <div style={{ marginTop:16, background:"#111827", border:"1px solid #1e293b", borderRadius:8, padding:16 }}>
            <div style={{ fontSize:12, fontWeight:700, color:"#818cf8", marginBottom:8 }}>Region Champions Path</div>
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr 1fr", gap:12, fontSize:11 }}>
              {[{r:"EAST",c:"Duke",p:"UMBC → Missouri → Gonzaga → Illinois"},
                {r:"SOUTH",c:"Florida",p:"Wright St → Villanova → Purdue → UConn"},
                {r:"MIDWEST",c:"Michigan",p:"Beth-Cook → Iowa → Virginia → Arizona"},
                {r:"WEST",c:"Arizona",p:"Tenn St → Miami → Alabama → Michigan St"}
              ].map(x => (
                <div key={x.r} style={{ borderTop:`2px solid ${REGION_COLORS[x.r]}`, paddingTop:6 }}>
                  <div style={{ color:REGION_COLORS[x.r], fontWeight:700, fontSize:10, textTransform:"uppercase", letterSpacing:1 }}>{x.r}</div>
                  <div style={{ color:"#f8fafc", fontWeight:800, fontSize:14, margin:"2px 0" }}>{x.c}</div>
                  <div style={{ color:"#475569", fontSize:9 }}>{x.p}</div>
                </div>
              ))}
            </div>
          </div>
        </div>)}

        {tab === "EV Bets" && (<div>
          <div style={{ fontSize:12, color:"#94a3b8", marginBottom:14 }}>{EV_BETS.length} +EV opportunities found</div>
          {EV_BETS.map((b,i) => (
            <div key={i} style={{ background:"#111827", border:"1px solid #1e293b", borderRadius:8, padding:14, marginBottom:8, borderLeft:`3px solid ${b.ev>=6?"#16a34a":b.ev>=4?"#ca8a04":"#6b7280"}`, display:"grid", gridTemplateColumns:"1fr auto 1fr", gap:16, alignItems:"center" }}>
              <div>
                <div style={{ fontSize:10, color:"#64748b", textTransform:"uppercase", letterSpacing:1 }}>{b.type} • {b.book}</div>
                <div style={{ fontSize:14, fontWeight:700, marginTop:2 }}>{b.side}</div>
                <div style={{ fontSize:11, color:"#94a3b8", marginTop:2 }}>{b.game}</div>
                <div style={{ fontSize:10, color:"#475569", marginTop:2 }}>Pred: {b.score} • Spread: {b.spread>0?"+":""}{b.spread}</div>
              </div>
              <div style={{ textAlign:"center" }}>
                <div style={{ fontSize:24, fontWeight:800 }}>{b.odds>0?"+":""}{b.odds}</div>
                {b.line!=null && <div style={{ fontSize:10, color:"#94a3b8" }}>Line: {b.line>0?"+":""}{b.line}</div>}
                <span style={{ background:b.ev>=6?"#16a34a":b.ev>=4?"#ca8a04":"#6b7280", color:"#fff", padding:"2px 8px", borderRadius:4, fontSize:11, fontWeight:700 }}>+{b.ev}% EV</span>
              </div>
              <div>
                <div style={{ display:"flex", justifyContent:"space-between", fontSize:10, color:"#64748b", marginBottom:2 }}>
                  <span>Probability</span>
                  <span style={{color:"#4ade80"}}>Edge: +{((b.model-b.implied)*100).toFixed(1)}%</span>
                </div>
                <div style={{ position:"relative", height:8, background:"#1e293b", borderRadius:4, overflow:"hidden" }}>
                  <div style={{ position:"absolute", left:0, top:0, height:"100%", width:`${b.implied*100}%`, background:"#475569", borderRadius:4 }} />
                  <div style={{ position:"absolute", left:0, top:0, height:"100%", width:`${b.model*100}%`, background:"#4ade80", borderRadius:4, opacity:0.7 }} />
                </div>
                <div style={{ display:"flex", justifyContent:"space-between", fontSize:9, color:"#475569", marginTop:1 }}>
                  <span>Model: {(b.model*100).toFixed(0)}%</span><span>Market: {(b.implied*100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>)}

        {tab === "Rankings" && (<div style={{ overflowX:"auto" }}>
          <table style={{ width:"100%", borderCollapse:"collapse", fontSize:12 }}>
            <thead><tr style={{ borderBottom:"2px solid #1e293b" }}>
              {[{k:"rank",l:"#"},{k:"name",l:"TEAM"},{k:"conf",l:"CONF"},{k:"record",l:"REC"},{k:"sor",l:"SOR"},{k:"sos",l:"SOS"},{k:"pppO",l:"PPP↑"},{k:"pppD",l:"PPP↓"},{k:"qual",l:"QUAL"}].map(c => (
                <th key={c.k} onClick={() => { if(sortCol===c.k) setSortDir(-sortDir); else { setSortCol(c.k); setSortDir(1); }}} style={{ padding:"8px 6px", textAlign:c.k==="name"?"left":"center", color:sortCol===c.k?"#818cf8":"#64748b", cursor:"pointer", userSelect:"none", fontWeight:600, fontSize:10 }}>{c.l}{sortCol===c.k?(sortDir===1?" ▲":" ▼"):""}</th>
              ))}
            </tr></thead>
            <tbody>{sorted.map((t,i) => (
              <tr key={t.name} style={{ borderBottom:"1px solid #1e293b", background:i%2?"#0d1321":"transparent" }}>
                <td style={{ padding:"7px 6px", textAlign:"center", fontWeight:800, color:t.rank<=4?"#818cf8":t.rank<=10?"#f8fafc":"#94a3b8" }}>{t.rank}</td>
                <td style={{ padding:"7px 6px", fontWeight:600 }}>{t.name}</td>
                <td style={{ padding:"7px 6px", textAlign:"center", color:"#64748b", fontSize:10 }}>{t.conf}</td>
                <td style={{ padding:"7px 6px", textAlign:"center" }}>{t.record}</td>
                <td style={{ padding:"7px 6px", textAlign:"center", fontWeight:700, color:t.sor>=0.7?"#4ade80":t.sor>=0.6?"#fbbf24":"#94a3b8" }}>{t.sor.toFixed(3)}</td>
                <td style={{ padding:"7px 6px", textAlign:"center" }}>{t.sos}</td>
                <td style={{ padding:"7px 6px", textAlign:"center", color:t.pppO>=1.2?"#4ade80":"#e2e8f0" }}>{t.pppO.toFixed(3)}</td>
                <td style={{ padding:"7px 6px", textAlign:"center", color:t.pppD<=0.97?"#4ade80":t.pppD>=1.05?"#f87171":"#e2e8f0" }}>{t.pppD.toFixed(3)}</td>
                <td style={{ padding:"7px 6px", textAlign:"center" }}>{t.qual}</td>
              </tr>
            ))}</tbody>
          </table>
        </div>)}

        {tab === "Model" && (<div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:16 }}>
          <div style={{ background:"#111827", border:"1px solid #1e293b", borderRadius:8, padding:20 }}>
            <div style={{ fontSize:14, fontWeight:700, marginBottom:12, color:"#818cf8" }}>Model Architecture</div>
            <div style={{ fontSize:12, lineHeight:1.8, color:"#94a3b8" }}>
              {["Blended PPP = Off_w × PPP_off(adj) + Def_w × PPP_def(adj)","SOS Adj = PPP × ((366 − SOS_RK) / 365)^α","Pace = 0.65 × min(A,B) + 0.35 × max(A,B)","Score = PPP × Pace + HCA + SOR_adj + Foul_adj","Win% = 1 / (1 + e^(−spread / 18))"].map((f,i) => (
                <div key={i}><span style={{color:"#4ade80"}}>→</span> {f}</div>
              ))}
            </div>
          </div>
          <div style={{ background:"#111827", border:"1px solid #1e293b", borderRadius:8, padding:20 }}>
            <div style={{ fontSize:14, fontWeight:700, marginBottom:12, color:"#818cf8" }}>Backtest Performance</div>
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
              {[{l:"Straight Up",v:`${BACKTEST.win_rate}%`,s:`${BACKTEST.n} games`,c:"#4ade80"},{l:"ATS (5pt edge)",v:`${BACKTEST.edge5_rate}%`,s:`${BACKTEST.edge5_n} bets`,c:"#fbbf24"}].map(m => (
                <div key={m.l} style={{ textAlign:"center", padding:12, background:"#0a0f1a", borderRadius:6 }}>
                  <div style={{ fontSize:28, fontWeight:800, color:m.c }}>{m.v}</div>
                  <div style={{ fontSize:11, color:"#64748b", marginTop:4 }}>{m.l}</div>
                  <div style={{ fontSize:10, color:"#475569" }}>{m.s}</div>
                </div>
              ))}
            </div>
            <div style={{ marginTop:12, fontSize:12, color:"#94a3b8" }}>
              <div><span style={{color:"#f8fafc",fontWeight:600}}>Params:</span> Off=0.44, Def=0.43, SOR=0.03, HCA=1, Scale=18</div>
            </div>
          </div>
        </div>)}

        {tab === "Setup" && (<div style={{ display:"flex", flexDirection:"column", gap:16 }}>
          <div style={{ background:"#111827", border:"1px solid #1e293b", borderRadius:8, padding:20 }}>
            <div style={{ fontSize:16, fontWeight:700, marginBottom:12, color:"#818cf8" }}>Commands — Your Machine</div>
            <div style={{ background:"#0a0f1a", padding:16, borderRadius:6, border:"1px solid #1e293b", fontSize:12, lineHeight:2.2 }}>
              <div style={{color:"#64748b"}}># Your project folder</div>
              <div style={{color:"#4ade80"}}>cd C:\Users\13032\Downloads\NCAAB</div>
              <br/>
              <div style={{color:"#64748b"}}># ──── ONE-TIME SETUP ────</div>
              <div style={{color:"#4ade80"}}>pip install requests beautifulsoup4 openpyxl pandas</div>
              <br/>
              <div style={{color:"#64748b"}}># Set Odds API key (free at the-odds-api.com)</div>
              <div style={{color:"#64748b"}}># PowerShell:</div>
              <div style={{color:"#4ade80"}}>$env:ODDS_API_KEY="your_key_here"</div>
              <div style={{color:"#64748b"}}># CMD:</div>
              <div style={{color:"#4ade80"}}>set ODDS_API_KEY=your_key_here</div>
              <br/>
              <div style={{color:"#64748b"}}># ──── DAILY COMMANDS ────</div>
              <br/>
              <div style={{color:"#64748b"}}># Full run: model + odds + EV bets</div>
              <div style={{color:"#4ade80"}}>python ncaab_bot.py --excel ncaab_dynamic_bracket.xlsx</div>
              <br/>
              <div style={{color:"#64748b"}}># Just odds + EV (skip ESPN scrape)</div>
              <div style={{color:"#4ade80"}}>python ncaab_bot.py --odds-only --excel ncaab_dynamic_bracket.xlsx</div>
              <br/>
              <div style={{color:"#64748b"}}># Full run + export updated bracket xlsx</div>
              <div style={{color:"#4ade80"}}>python ncaab_bot.py --export --excel ncaab_dynamic_bracket.xlsx</div>
              <br/>
              <div style={{color:"#64748b"}}># ──── ESPN UPDATE (VBA Macro) ────</div>
              <div style={{color:"#64748b"}}># Open bracket → Alt+F8 → ImportAll_ESPN</div>
              <div style={{color:"#64748b"}}># Select each downloaded ESPN file when prompted</div>
              <br/>
              <div style={{color:"#64748b"}}># ──── OR: SOR cleanup only ────</div>
              <div style={{color:"#4ade80"}}>python espn_cleaner.py</div>
            </div>
          </div>
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:16 }}>
            <div style={{ background:"#111827", border:"1px solid #1e293b", borderRadius:8, padding:20 }}>
              <div style={{ fontSize:14, fontWeight:700, marginBottom:8, color:"#818cf8" }}>Daily Workflow</div>
              <div style={{ fontSize:12, color:"#94a3b8", lineHeight:2 }}>
                {["Download 3 ESPN files (browser, ~2 min)","VBA macro: ImportAll_ESPN (Alt+F8)","python ncaab_bot.py (~30 sec)","Check output/latest.json for EV bets","Open dashboard to visualize"].map((s,i) => (
                  <div key={i}><span style={{color:"#818cf8",fontWeight:800,marginRight:6}}>{i+1}.</span><span style={{color:"#f8fafc",fontWeight:600}}>{s}</span></div>
                ))}
              </div>
            </div>
            <div style={{ background:"#111827", border:"1px solid #1e293b", borderRadius:8, padding:20 }}>
              <div style={{ fontSize:14, fontWeight:700, marginBottom:8, color:"#818cf8" }}>Files in C:\...\NCAAB</div>
              <div style={{ fontSize:11, color:"#94a3b8", lineHeight:1.8 }}>
                {[["ncaab_dynamic_bracket.xlsm","Bracket model (macro-enabled)"],["ncaab_bot.py","Daily bot — odds + EV finder"],["espn_cleaner.py","SOR date-fix (standalone)"],["ESPN_Import_Macro.bas","VBA macro source"],["output/latest.json","Most recent bot run"],["output/daily_run_*.json","Historical runs"]].map(([f,d]) => (
                  <div key={f} style={{display:"flex",gap:6}}><span style={{color:"#818cf8"}}>→</span><span style={{color:"#f8fafc",fontWeight:600}}>{f}</span><span style={{color:"#475569",fontSize:9,marginLeft:"auto"}}>{d}</span></div>
                ))}
              </div>
            </div>
          </div>
        </div>)}
      </div>
    </div>
  );
}
