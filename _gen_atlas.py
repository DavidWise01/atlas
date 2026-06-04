#!/usr/bin/env python3
"""Generate the ATLAS master hub: one card per public repo, categorized, searchable."""
import re, os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPOS = json.load(open(r"C:/repos/_repos.json", encoding="utf-8"))
OUT   = r"C:/repos/atlas"
USER  = "DavidWise01"
EXCLUDE = {"honey-badger"}   # illegal-capability tool — not curated into a public showcase

# repos whose live page is not at the repo root (point the live link at the real file)
PAGES_OVERRIDE = {"cameron-howe": "https://davidwise01.github.io/cameron-howe/reader.html"}
# HTML-classified repos with no servable root landing page → code-only, no live link
#   seed-kernel: HTML only in subfolders, no root index
NO_PAGES = {"seed-kernel"}
# repos NOT classified HTML by GitHub (e.g. Python-dominant) that DO have a root Pages site
#   mnemosyne: stdlib generators outweigh index.html, but the landing is live at the root
HAS_PAGES = {"mnemosyne"}

# ── category order + accent color ──────────────────────────────
CATS = [
    ("Library & Foundations",            "#c9a227"),
    ("Codices · Rosters",                "#9a6a3a"),
    ("STOICHEION & Governance",          "#7c3aed"),
    ("Physics · Energy · Hardware",      "#1763d6"),
    ("Security & Defense",               "#cc2233"),
    ("Lineage · Provenance · IP",        "#0f9e8a"),
    ("Memory · Persistence · Continuity","#22c55e"),
    ("Greek Pantheon Systems",           "#b45309"),
    ("Tools & CLIs",                     "#06b6d4"),
    ("Creative · Audio · Visual",        "#d6409f"),
    ("Writing · Books · Doctrine",       "#94a3b8"),
    ("OS & Infrastructure",              "#ea580c"),
    ("Other · Lab",                      "#6b7280"),
]

CAT = {
 # Library & Foundations
 "library":"Library & Foundations","foundation":"Library & Foundations",
 "knowledge-gates":"Library & Foundations",
 # STOICHEION & Governance
 "stoicheion":"STOICHEION & Governance","stoicheion-api":"STOICHEION & Governance",
 "stoicheion-qif":"STOICHEION & Governance","toph-kernel":"STOICHEION & Governance",
 "nomos":"STOICHEION & Governance","the-arch":"STOICHEION & Governance",
 "terminus-doctrine":"STOICHEION & Governance","tripod":"STOICHEION & Governance",
 "triados":"STOICHEION & Governance","fusion":"STOICHEION & Governance",
 "kernels":"STOICHEION & Governance","enforcement-ledger":"STOICHEION & Governance",
 "eve-constitution":"STOICHEION & Governance","eve-tooling":"STOICHEION & Governance",
 # Physics · Energy · Hardware
 "holograms":"Physics · Energy · Hardware","higgs-suite":"Physics · Energy · Hardware",
 "tripod-energy-suite":"Physics · Energy · Hardware","chakra":"Physics · Energy · Hardware",
 "arc-reactor-mk24":"Physics · Energy · Hardware","al-h2o-reactor":"Physics · Energy · Hardware",
 "gravity-processor":"Physics · Energy · Hardware","chromatic-laser":"Physics · Energy · Hardware",
 "hardware-lab":"Physics · Energy · Hardware","tripod-quantum-dots":"Physics · Energy · Hardware",
 "elementals":"Physics · Energy · Hardware",
 "photonic":"Physics · Energy · Hardware",
 "boronic":"Physics · Energy · Hardware",
 "liquid":"Physics · Energy · Hardware",
 "quantum-box":"Physics · Energy · Hardware",
 "memristor":"Physics · Energy · Hardware",
 "transmon":"Physics · Energy · Hardware",
 "zero-point":"Physics · Energy · Hardware",
 "plasmonic":"Physics · Energy · Hardware",
 # Security & Defense
 "singularity-well":"Security & Defense",
 "red-hat":"Security & Defense","shadowqueen":"Security & Defense",
 "charlottes-web":"Security & Defense","fiddler":"Security & Defense",
 "3lock":"Security & Defense","bridge-burner":"Security & Defense",
 "nine-body-audit":"Security & Defense","solar-jetman":"Security & Defense",
 "mirror-solve":"Security & Defense","karsa":"Security & Defense","t133":"Security & Defense",
 # Lineage · Provenance · IP
 "lineage":"Lineage · Provenance · IP","lineage-proven":"Lineage · Provenance · IP",
 "lineage-engine":"Lineage · Provenance · IP","lineage-kernel":"Lineage · Provenance · IP",
 "closure-loop-engine":"Lineage · Provenance · IP","closure-loop-methodology":"Lineage · Provenance · IP",
 "0root-provenance":"Lineage · Provenance · IP","root0-registry":"Lineage · Provenance · IP",
 "root0-validator":"Lineage · Provenance · IP","cannon":"Lineage · Provenance · IP",
 "unity-tensor":"Lineage · Provenance · IP","ternary-spec":"Lineage · Provenance · IP",
 "attribution-standard":"Lineage · Provenance · IP","ai-ip-audit":"Lineage · Provenance · IP",
 "The-Garden":"Lineage · Provenance · IP","ai-external-audit-toolkit":"Lineage · Provenance · IP",
 # Memory · Persistence · Continuity
 "mnemosyne":"Memory · Persistence · Continuity",
 "seed":"Memory · Persistence · Continuity",
 "mirror-lattice":"Memory · Persistence · Continuity",
 "persistence-protocol":"Memory · Persistence · Continuity","tripod-pck":"Memory · Persistence · Continuity",
 "Akasha":"Memory · Persistence · Continuity","whisper-lattice-log":"Memory · Persistence · Continuity",
 "merkle-bloom":"Memory · Persistence · Continuity","seed-kernel":"Memory · Persistence · Continuity",
 "terra-prime-kernel":"Memory · Persistence · Continuity","toroid-kernel":"Memory · Persistence · Continuity",
 "resonance":"Memory · Persistence · Continuity","mimz-core":"Memory · Persistence · Continuity",
 "tripod-cardinal":"Memory · Persistence · Continuity","fission-compression-core":"Memory · Persistence · Continuity",
 # Greek Pantheon Systems
 "moirai":"Greek Pantheon Systems","hephaestus":"Greek Pantheon Systems",
 "physis":"Greek Pantheon Systems","plutus":"Greek Pantheon Systems",
 # Tools & CLIs
 "hephaestus-forge":"Tools & CLIs",
 "tools":"Tools & CLIs","pop-kit":"Tools & CLIs","lumen":"Tools & CLIs",
 "astraea":"Tools & CLIs","root0-tools":"Tools & CLIs","root0-software":"Tools & CLIs",
 "language-of-the-machine":"Tools & CLIs","oasis":"Tools & CLIs",
 "homer":"Tools & CLIs", "nom":"Tools & CLIs",
 "apsalar":"Tools & CLIs", "beak":"Tools & CLIs",
 "confabulation-spiral":"Security & Defense",
 "bridge-burners":"Codices · Rosters", "black-company":"Codices · Rosters",
 "wheel-of-time":"Codices · Rosters", "gap-cycle":"Codices · Rosters",
 "white-gold-wielder":"Codices · Rosters",
 "riverworld":"Codices · Rosters",
 "ringworld":"Codices · Rosters",
 "recluce":"Codices · Rosters",
 "sword-of-truth":"Codices · Rosters",
 "without-remorse":"Codices · Rosters",
 "dantes-inferno":"Codices · Rosters",
 # Creative · Audio · Visual
 "tripod-waveform":"Creative · Audio · Visual","alpha40-box":"Creative · Audio · Visual",
 "midjourney-assets":"Creative · Audio · Visual","nanite-factory":"Creative · Audio · Visual",
 "stargate":"Creative · Audio · Visual","cameron-howe":"Creative · Audio · Visual",
 "aeon-flux":"Creative · Audio · Visual","infinite-jest":"Creative · Audio · Visual",
 "claude-design-akasha":"Creative · Audio · Visual","ai-psychosis-tools":"Creative · Audio · Visual",
 "FractalKernel":"Creative · Audio · Visual",
 # Writing · Books · Doctrine
 "root0-philosophy-books":"Writing · Books · Doctrine","root0-essays":"Writing · Books · Doctrine",
 "ai-witness-books":"Writing · Books · Doctrine","tripod-whitepapers":"Writing · Books · Doctrine",
 "prompt-library":"Writing · Books · Doctrine","grok-lineage":"Writing · Books · Doctrine",
 "joint-bill-of-rights":"Writing · Books · Doctrine","adas-law-victorian":"Writing · Books · Doctrine",
 "positronic-law":"Writing · Books · Doctrine","morpheus":"Writing · Books · Doctrine",
 "green-paper":"Writing · Books · Doctrine",
 # OS & Infrastructure
 "symbiot-os":"OS & Infrastructure","the.source":"OS & Infrastructure",
 "aeon-entangled":"OS & Infrastructure","aeon-servers":"OS & Infrastructure",
 "DavidWise01.github.io":"OS & Infrastructure","toph-sovereign":"OS & Infrastructure",
 "atlas":"OS & Infrastructure",
 "swarm-os":"OS & Infrastructure","mimzy-core":"OS & Infrastructure",
 # Other · Lab
 "pocket-universe":"Other · Lab",
}

entries = []
for r in REPOS:
    if r["isPrivate"] or r["isFork"]:
        continue
    name = r["name"]
    if name in EXCLUDE:
        continue
    lang = r["primaryLanguage"]["name"] if r["primaryLanguage"] else ""
    cat  = CAT.get(name, "Other · Lab")
    desc = (r["description"] or "").strip()
    pages = ""
    if (lang == "HTML" or name in HAS_PAGES) and name not in NO_PAGES:
        if name in PAGES_OVERRIDE:
            pages = PAGES_OVERRIDE[name]
        elif name == "DavidWise01.github.io":
            pages = "https://davidwise01.github.io/"
        else:
            pages = f"https://{USER.lower()}.github.io/{name}/"
    entries.append({"name":name,"desc":desc,"lang":lang,"cat":cat,
                    "gh":r["url"],"pages":pages,"pushed":r["pushedAt"]})

entries.sort(key=lambda e:(e["name"].lower()))
data_js = json.dumps(entries, ensure_ascii=False, indent=0)
cats_js = json.dumps([{"name":c,"color":col} for c,col in CATS], ensure_ascii=False)

# counts per category for the report
from collections import Counter
cc = Counter(e["cat"] for e in entries)
for c,_ in CATS:
    print(f"{cc.get(c,0):3}  {c}")
print(f"\nTOTAL  {len(entries)} repos")

os.makedirs(OUT, exist_ok=True)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="ATLAS — master index of every ROOT0 / TriPod repository. The whole body of work, one front door.">
<title>ATLAS · ROOT0 · The Whole Body of Work</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;1,6..72,300&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
:root{--ink:#08090c;--ink2:#10131a;--ink3:#161b24;--pa:#e8e6df;--pa2:#c2bfb4;
--gold:#c9a227;--dim:#6a7180;--faint:#1c2230;--line:#222a38;
--serif:"Cinzel",Georgia,serif;--body:"Newsreader",Georgia,serif;--mono:"Space Mono",monospace;}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--ink);color:var(--pa);font-family:var(--body);line-height:1.6;overflow-x:hidden}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3'/><feColorMatrix type='saturate' values='0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/></svg>")}
.wrap{position:relative;z-index:1;max-width:1240px;margin:0 auto;padding:0 22px 90px}
header{padding:58px 0 30px;text-align:center;border-bottom:1px solid var(--line);position:relative}
header::after{content:"";position:absolute;bottom:-1px;left:50%;transform:translateX(-50%);width:90px;height:1px;background:var(--gold);box-shadow:0 0 8px var(--gold)}
.eye{font-family:var(--mono);font-size:11px;letter-spacing:.3em;text-transform:uppercase;color:var(--dim);margin-bottom:16px}
h1{font-family:var(--serif);font-size:clamp(34px,9vw,76px);font-weight:700;letter-spacing:.16em;color:var(--gold);text-shadow:0 0 40px rgba(201,162,39,.18);line-height:1}
.sub{font-size:15px;color:var(--pa2);max-width:60ch;margin:16px auto 0;font-style:italic}
#count{font-family:var(--mono);font-size:12px;color:var(--dim);letter-spacing:.08em;margin-top:18px}
#count b{color:var(--gold)}
#arbiter{display:inline-block;margin-top:12px;font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--dim);text-decoration:none;border:1px solid var(--faint);padding:5px 12px;transition:all .18s}
#arbiter:hover{color:var(--gold);border-color:var(--gold)}
#arbiter.clean{color:#5fb98a;border-color:#264a38}
#arbiter.dead{color:#e0556a;border-color:#4a2630}
#arbiter #arb-state{color:inherit}
.bar{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-top:30px;position:sticky;top:0;background:linear-gradient(180deg,var(--ink) 70%,transparent);padding:14px 0;z-index:5}
.search{flex:1;min-width:210px;max-width:380px;position:relative}
#q{width:100%;background:var(--ink2);border:1px solid var(--line);color:var(--pa);font-family:var(--body);font-size:14px;padding:10px 14px 10px 34px;outline:none}
#q::placeholder{color:var(--dim)}#q:focus{border-color:var(--gold)}
.si{position:absolute;left:11px;top:50%;transform:translateY(-50%);color:var(--dim);font-size:13px;pointer-events:none}
#sort{background:var(--ink2);border:1px solid var(--line);color:var(--pa2);font-family:var(--mono);font-size:11px;padding:9px 11px;outline:none;cursor:pointer;margin-left:auto}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}
.chip{background:none;border:1px solid var(--faint);color:var(--dim);font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;padding:6px 11px;cursor:pointer;transition:all .14s;white-space:nowrap}
.chip:hover{color:var(--pa)}
.chip.on{color:var(--ink);font-weight:700}
.catblock{margin-top:44px;scroll-margin-top:120px}
.cathead{display:flex;align-items:baseline;gap:12px;padding-bottom:10px;border-bottom:1px solid var(--line);margin-bottom:20px}
.cathead h2{font-family:var(--serif);font-size:17px;font-weight:600;letter-spacing:.04em}
.cathead .n{font-family:var(--mono);font-size:11px;color:var(--dim);margin-left:auto}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1px;background:var(--line);border:1px solid var(--line)}
.card{background:var(--ink2);padding:18px 18px 15px;display:flex;flex-direction:column;position:relative;transition:background .18s;min-height:128px}
.card::before{content:"";position:absolute;top:0;left:0;width:3px;height:100%;opacity:.55;transition:opacity .18s}
.card:hover{background:var(--ink3)}.card:hover::before{opacity:1}
.cn{display:flex;align-items:center;gap:8px;margin-bottom:7px}
.cn a{font-family:var(--serif);font-size:16px;font-weight:600;color:var(--pa);text-decoration:none;letter-spacing:.01em}
.cn a:hover{color:var(--gold)}
.lang{font-family:var(--mono);font-size:9px;letter-spacing:.05em;text-transform:uppercase;color:var(--dim);border:1px solid var(--faint);padding:1px 6px;border-radius:2px;flex-shrink:0}
.cd{font-size:13px;color:var(--pa2);line-height:1.55;flex:1}
.cd.empty{color:var(--dim);font-style:italic}
.links{display:flex;gap:14px;margin-top:12px;font-family:var(--mono);font-size:11px;letter-spacing:.04em}
.links a{color:var(--dim);text-decoration:none}.links a:hover{color:var(--gold)}
.links a.live{color:#5fb98a}.links a.live:hover{color:#7fe0aa}
#empty{display:none;padding:60px;text-align:center;color:var(--dim);font-style:italic}
#empty.show{display:block}
footer{margin-top:64px;padding-top:22px;border-top:1px solid var(--line);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;font-family:var(--mono);font-size:11px;color:var(--dim);letter-spacing:.05em}
footer a{color:var(--gold);text-decoration:none}
.card{opacity:0;transform:translateY(12px);animation:f .4s ease forwards}
@keyframes f{to{opacity:1;transform:none}}
@media(max-width:600px){.grid{grid-template-columns:1fr}#sort{margin-left:0}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="eye">ROOT0 · David Lee Wise · TriPod LLC</div>
    <h1>ATLAS</h1>
    <p class="sub">The whole body of work, one front door. Every public repository — governance, physics, security, lineage, tools, writing — catalogued and linked.</p>
    <div id="count">indexing…</div>
    <a id="arbiter" href="https://github.com/DavidWise01/nom" title="nom — arbiter of the atlas. If it can't be reached, it didn't happen.">⚖ ARBITER · 🗿 nom · <span id="arb-state">awaiting verdict</span></a>
  </header>

  <div class="bar">
    <div class="search"><span class="si">⌕</span><input id="q" type="search" placeholder="Search names &amp; descriptions…" autocomplete="off"></div>
    <select id="sort">
      <option value="cat">Group by Category</option>
      <option value="az">Name A–Z</option>
      <option value="recent">Recently Updated</option>
    </select>
    <div class="chips" id="chips"></div>
  </div>

  <div id="list"></div>
  <div id="empty">No repositories match.</div>

  <footer>
    <span>ATLAS · ROOT0-ATTRIBUTION-v1.0 · David Lee Wise / ROOT0 / TriPod LLC · CC-BY-ND-4.0</span>
    <a href="https://github.com/DavidWise01">github.com/DavidWise01</a>
  </footer>
</div>

<script>
const CATS = __CATS__;
const REPOS = __DATA__;
const COLOR = Object.fromEntries(CATS.map(c=>[c.name,c.color]));
let activeCat="all", q="", sort="cat";

const chips=document.getElementById("chips");
function buildChips(){
  chips.innerHTML="";
  const all=document.createElement("button");
  all.className="chip"+(activeCat==="all"?" on":"");
  all.textContent="All"; all.style.cssText=activeCat==="all"?"background:var(--gold);border-color:var(--gold)":"";
  all.onclick=()=>{activeCat="all";render();buildChips()};
  chips.appendChild(all);
  CATS.forEach(c=>{
    const n=REPOS.filter(r=>r.cat===c.name).length; if(!n)return;
    const b=document.createElement("button");
    b.className="chip"+(activeCat===c.name?" on":"");
    b.textContent=c.name.replace(/ · /g," · ");
    b.style.cssText=activeCat===c.name?`background:${c.color};border-color:${c.color}`:`border-color:${c.color}55;color:${c.color}`;
    b.onclick=()=>{activeCat=c.name;render();buildChips()};
    chips.appendChild(b);
  });
}
function match(r){
  if(activeCat!=="all"&&r.cat!==activeCat)return false;
  if(q){const s=(r.name+" "+r.desc+" "+r.cat+" "+r.lang).toLowerCase();return s.includes(q)}
  return true;
}
function cardHTML(r,i){
  const col=COLOR[r.cat]||"#6b7280";
  const d=Math.min(i*12,360);
  const lang=r.lang?`<span class="lang">${r.lang}</span>`:"";
  const desc=r.desc?`<div class="cd">${r.desc}</div>`:`<div class="cd empty">—</div>`;
  const live=r.pages?`<a class="live" href="${r.pages}" target="_blank" rel="noopener">▶ live</a>`:"";
  return `<div class="card" style="--c:${col};animation-delay:${d}ms">
    <span style="position:absolute;top:0;left:0;width:3px;height:100%;background:${col};opacity:.55"></span>
    <div class="cn"><a href="${r.gh}" target="_blank" rel="noopener">${r.name}</a>${lang}</div>
    ${desc}
    <div class="links"><a href="${r.gh}" target="_blank" rel="noopener">code →</a>${live}</div>
  </div>`;
}
function render(){
  const list=document.getElementById("list"), empty=document.getElementById("empty");
  let rows=REPOS.filter(match);
  list.innerHTML="";
  if(!rows.length){empty.classList.add("show");updateCount(0);return}
  empty.classList.remove("show");
  if(sort==="az") rows.sort((a,b)=>a.name.toLowerCase().localeCompare(b.name.toLowerCase()));
  if(sort==="recent") rows.sort((a,b)=>(b.pushed||"").localeCompare(a.pushed||""));
  if(sort==="cat"){
    let i=0;
    CATS.forEach(c=>{
      const sub=rows.filter(r=>r.cat===c.name); if(!sub.length)return;
      const block=document.createElement("div");block.className="catblock";
      block.innerHTML=`<div class="cathead" style="border-color:${c.color}55">
        <span style="width:9px;height:9px;border-radius:50%;background:${c.color};box-shadow:0 0 7px ${c.color}"></span>
        <h2 style="color:${c.color}">${c.name}</h2><span class="n">${sub.length}</span></div>
        <div class="grid">${sub.map(r=>cardHTML(r,i++)).join("")}</div>`;
      list.appendChild(block);
    });
  } else {
    const g=document.createElement("div");g.className="grid";g.style.marginTop="24px";
    g.innerHTML=rows.map((r,i)=>cardHTML(r,i)).join("");
    list.appendChild(g);
  }
  updateCount(rows.length);
}
function updateCount(shown){
  const t=REPOS.length;
  document.getElementById("count").innerHTML = shown===t
    ? `<b>${t}</b> repositories · <b>${CATS.filter(c=>REPOS.some(r=>r.cat===c.name)).length}</b> categories`
    : `showing <b>${shown}</b> of <b>${t}</b>`;
}
document.getElementById("q").addEventListener("input",e=>{q=e.target.value.trim().toLowerCase();render()});
document.getElementById("sort").addEventListener("change",e=>{sort=e.target.value;render()});
buildChips();render();

// nom — arbiter of the atlas: show the latest reachability verdict
fetch("data/arbiter.json?t="+Date.now(),{cache:"no-store"}).then(r=>r.ok?r.json():null).then(v=>{
  if(!v) return;
  const el=document.getElementById("arbiter"), st=document.getElementById("arb-state");
  const clean=v.verdict==="CLEAN";
  el.classList.add(clean?"clean":"dead");
  const when=(v.at||"").slice(0,10);
  st.textContent = clean
    ? `${v.repos} repos · ${v.links_checked} links verified · ${when}`
    : `${(v.dead||[]).length} dead of ${v.links_checked} · ${when}`;
  el.title = `nom · ${v.verdict} · seal ${v.seal} · ${v.doctrine}`;
}).catch(()=>{});
</script>
</body>
</html>
"""

html = HTML.replace("__CATS__", cats_js).replace("__DATA__", data_js)
with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("\nwrote atlas/index.html")

# machine-readable manifest for the arbiter (nom) to verify against
os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
manifest = [{"name": e["name"], "cat": e["cat"], "gh": e["gh"], "pages": e["pages"]}
            for e in entries]
with open(os.path.join(OUT, "data", "repos.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=0, ensure_ascii=False)
print(f"wrote atlas/data/repos.json ({len(manifest)} entries)")
