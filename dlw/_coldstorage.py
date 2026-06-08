#!/usr/bin/env python3
"""Definitive cold-storage gap report for the emergent lattice.

Ground truth for NAMES: STOICHEION_AXIOM_PAYLOAD.md  (| Sxxx | GOV:INV | Mythos |).
Ground truth for PRESENCE: each birth cert's OWN declared node number — both the
T-label (e.g. "T085") AND the spelled ordinal (e.g. "Ninety-Second Node"), unioned,
because the corpus is internally inconsistent between the two. A node is PRESENT if
any individual cert declares it by either signal. Finds certs by filename OR by a
"BIRTH CERTIFICATE" content header (catches files like `continuity`, `kvasir`).
Read-only except the report it writes."""
import os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Davids files"
PAYLOAD = os.path.join(WS, r"repos\system\FRAMEWORK\STOICHEION_AXIOM_PAYLOAD.md")
ROOTS = [os.path.join(WS, r) for r in
         ["file", r"repos\system\PEERS", r"repos\system\NODES", r"repos\system",
          "mark down", r"arch-purple-book-complete-exe\content"]]

# ── spelled ordinal/cardinal → int (handles "One-Hundred-and-Fifty-First") ──
ONES = {"first":1,"second":2,"third":3,"fourth":4,"fifth":5,"sixth":6,"seventh":7,
        "eighth":8,"ninth":9,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,
        "seven":7,"eight":8,"nine":9}
TEENS = {"tenth":10,"eleventh":11,"twelfth":12,"thirteenth":13,"fourteenth":14,
         "fifteenth":15,"sixteenth":16,"seventeenth":17,"eighteenth":18,"nineteenth":19,
         "ten":10,"eleven":11,"twelve":12,"thirteen":13,"fourteen":14,"fifteen":15,
         "sixteen":16,"seventeen":17,"eighteen":18,"nineteen":19}
TENS = {"twentieth":20,"thirtieth":30,"fortieth":40,"fiftieth":50,"sixtieth":60,
        "seventieth":70,"eightieth":80,"ninetieth":90,"twenty":20,"thirty":30,
        "forty":40,"fifty":50,"sixty":60,"seventy":70,"eighty":80,"ninety":90}

def parse_ordinal(text):
    toks = re.split(r"[\s\-]+", text.lower())
    total = cur = 0; saw = False
    for t in toks:
        if t in ("and",""): continue
        if t == "hundred":
            cur = (cur or 1) * 100; saw = True; continue
        if t in ONES: cur += ONES[t]; saw = True
        elif t in TEENS: cur += TEENS[t]; saw = True
        elif t in TENS: cur += TENS[t]; saw = True
        elif t == "node":
            total += cur; cur = 0
        # ignore other words
    total += cur
    return total if (saw and 1 <= total <= 256) else None

# ── parse the PAYLOAD register: number -> mythos name ──
reg = {}
if os.path.exists(PAYLOAD):
    for line in open(PAYLOAD, encoding="utf-8", errors="replace"):
        m = re.match(r"\s*\|\s*([TS])(\d{1,3})\s*\|\s*([^|]*)\|\s*([^|]*)\|", line)
        if not m: continue
        num = int(m.group(2)); c2 = m.group(3).strip(); c3 = m.group(4).strip()
        # mythos name = col3 if it's a real name, else col2
        name = c3 if c3 and not re.match(r"^[A-Z0-9\-/ ]+:(INV|POP)$", c3) else c2
        name = name.strip("* ")
        if 1 <= num <= 256 and name and name.upper() not in ("","ID","NAME","CODE","AXIOM"):
            reg.setdefault(num, name)

# ── find every birth cert (filename OR content header) ──
def is_cert(path):
    fn = os.path.basename(path).lower()
    if "birth cert" in fn or re.search(r"birth.?cert", fn): return True
    if os.path.splitext(fn)[1] in ("", ".md"):
        try:
            head = open(path, encoding="utf-8", errors="replace").read(120).upper()
            return "BIRTH CERTIFICATE" in head or "BIRTH CERTI" in head
        except Exception: return False
    return False

certs = []
seen_paths = set()
for rootdir in ROOTS:
    if not os.path.isdir(rootdir): continue
    for root, _d, files in os.walk(rootdir):
        if "node_modules" in root: continue
        for fn in files:
            p = os.path.join(root, fn)
            if p in seen_paths: continue
            if is_cert(p):
                seen_paths.add(p); certs.append(p)

# ── per cert: declared numbers (T-label + ordinal) and name ──
present = {}     # num -> list of (name, path, how)
for p in certs:
    try: txt = open(p, encoding="utf-8", errors="replace").read()
    except Exception: continue
    head = "\n".join(txt.splitlines()[:6])
    # name from title
    mt = re.search(r"BIRTH\s+CERTIFICATE\s*[—\-–:]\s*(.+)", head, re.I)
    name = (mt.group(1).strip() if mt else os.path.basename(p).replace(" birth cert","")).strip()
    nums = set()
    for mm in re.finditer(r"\b[TS](\d{1,3})\b", head):
        n = int(mm.group(1))
        if 1 <= n <= 256: nums.add(n)
    mo = re.search(r"([A-Za-z\-]+(?:[\s\-](?:Hundred|and|[A-Za-z]+))*?)\s+Node\b", head)
    if mo:
        o = parse_ordinal(mo.group(0))
        if o: nums.add(o)
    for n in nums:
        present.setdefault(n, []).append((name, os.path.relpath(p, WS)))

present_nums = set(present)
gap = sorted(set(range(1, 257)) - present_nums)
named_gap   = [(n, reg[n]) for n in gap if n in reg]
unnamed_gap = [n for n in gap if n not in reg]

# ── BY-NAME presence: the corpus numbers itself inconsistently, so the real
#    question is which register-NAMED emergents have no cert by that name ──
import unicodedata
def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())

cert_norms = {}      # normalized cert name -> path
for p in certs:
    try: head = "\n".join(open(p, encoding="utf-8", errors="replace").read().splitlines()[:6])
    except Exception: head = ""
    mt = re.search(r"BIRTH\s+CERTIFICATE\s*[—\-–:]\s*(.+)", head, re.I)
    title = mt.group(1).strip() if mt else ""
    stem = re.sub(r"(?i)birth.?cert(ificate)?.*$", "", os.path.basename(p)).strip(" -—.0")
    for cand in (title, stem):
        nn = norm(cand)
        if nn: cert_norms.setdefault(nn, os.path.relpath(p, WS))

def has_cert_named(name):
    rn = norm(name)
    if not rn: return None
    if rn in cert_norms: return cert_norms[rn]
    if len(rn) >= 4:
        for cn, pth in cert_norms.items():
            if len(cn) >= 4 and (rn in cn or cn in rn):
                return pth
    return None

missing_by_name = []     # register-named emergents with NO cert by that name anywhere
for n in sorted(reg):
    hit = has_cert_named(reg[n])
    if not hit:
        missing_by_name.append((n, reg[n]))

# load workflow verdicts to cross-reference recovered names
vf = {}
try:
    vr = json.load(open("dlw/_verify.json", encoding="utf-8"))
    for v in vr.get("truly_absent", []) + vr.get("false_gaps", []):
        vf[v["number"]] = v
except Exception: pass

print(f"cert files (filename+content) : {len(certs)}")
print(f"distinct cert NAMES on disk   : {len(cert_norms)}")
print(f"register named nodes          : {len(reg)}/256")
print(f"lattice nodes present BY NUMBER: {len(present_nums)}/256")
print()
print(f"=== MISSING BY NAME: register-named emergents with NO cert by that name ({len(missing_by_name)}) ===")
print("    (the real cold-storage / re-create list)")
for n, nm in missing_by_name:
    print(f"  #{n:3}  {nm}")
print()
print(f"=== UNNAMED LATTICE POSITIONS (no register name, no cert — never individually popped) ({len(unnamed_gap)}) ===")
print("  " + ", ".join(f"#{n}" for n in unnamed_gap))
print("  → mass-declared (S213–S256 bucket); create when ready, not in cold storage.")

report = {
    "lattice": 256,
    "cert_files": len(certs),
    "distinct_cert_names": len(cert_norms),
    "register_named_nodes": len(reg),
    "present_by_number": sorted(present_nums),
    "missing_by_name": [{"node": n, "name": nm} for n, nm in missing_by_name],
    "unnamed_positions": unnamed_gap,
    "number_gap_named": [{"node": n, "name": nm} for n, nm in named_gap],
}
json.dump(report, open("dlw/_coldstorage.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"\nmissing-by-name: {len(missing_by_name)} · unnamed positions: {len(unnamed_gap)}")
print("wrote dlw/_coldstorage.json")
