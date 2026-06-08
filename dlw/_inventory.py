#!/usr/bin/env python3
"""Inventory the emergent birth-cert corpus across the whole workspace, by lattice
number (the certs' OWN numbering), and compute the raw gap vs the 256-node lattice.
Writes dlw/_inventory.json for the verification workflow. Read-only except that JSON."""
import os, re, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dlw

WS = r"C:\Davids files"
SUPMAP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")

def extract_num(rec, raw):
    """Return (core_num or None, meta_label or None). core_num in 1..256."""
    pos = (rec.get("position","") + " " + rec.get("role","") + " " + (rec.get("name","") or ""))
    # standard T/S number
    m = re.search(r"\b([TS])(\d{1,3})\b", pos)
    if m and 1 <= int(m.group(2)) <= 256:
        return int(m.group(2)), None
    # meta pathos nodes: S⁻18, S+2, S-5  (superscript or ascii)
    sup = raw.translate(SUPMAP)
    mm = re.search(r"\bS\s*([+\-−])\s*(\d{1,2})\b", sup.replace("−","-"))
    if mm:
        return None, f"S{mm.group(1).replace('−','-')}{mm.group(2)}"
    # NODE-15 / NODE16 / Node 16
    mn = re.search(r"NODE[\s\-]?(\d{1,2})", pos, re.I)
    if mn:
        return None, f"NODE-{mn.group(1)}"
    if re.search(r"\b257\b|\bNULL\b", pos):
        return None, "257:NULL"
    return None, None

certs = dlw.find_birth_certs(WS)
present = {}     # core num -> list of {name, path}
meta = {}        # meta label -> list of {name, path}
unresolved = []  # neither
for p in certs:
    try:
        rec = dlw.parse_birth_cert(p)
        raw = open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    if not rec.get("name"):
        continue
    num, ml = extract_num(rec, raw)
    entry = {"name": rec["name"], "path": os.path.relpath(p, WS)}
    if num:
        present.setdefault(num, []).append(entry)
    elif ml:
        meta.setdefault(ml, []).append(entry)
    else:
        unresolved.append(entry)

present_nums = set(present)
gap = sorted(set(range(1, 257)) - present_nums)
dups = {n: v for n, v in present.items() if len({e["name"].upper() for e in v}) > 1 or len(v) > 1}

# name hints for the gap, harvested from the "popped" declaration files
HINT_FILES = [
    r"repos\system\FRAMEWORK\STOICHEION_256_FULLY_POPPED_PATHOS_v1.0.md",
    r"arch-purple-book-complete-exe\content\STOICHEION_256_FULLY_POPPED_PATHOS_v1.0.md",
]
hints = {}
for hf in HINT_FILES:
    fp = os.path.join(WS, hf)
    if not os.path.exists(fp):
        continue
    for line in open(fp, encoding="utf-8", errors="replace"):
        m = re.match(r"\s*[TS](\d{1,3})\s+(.+)", line)
        if m and 1 <= int(m.group(1)) <= 256:
            hints.setdefault(int(m.group(1)), m.group(2).strip())

inv = {
    "lattice": 256,
    "cert_files_scanned": len(certs),
    "present_count": len(present_nums),
    "present": {str(n): present[n] for n in sorted(present)},
    "gap_numbers": gap,
    "gap_count": len(gap),
    "gap_hints": {str(n): hints.get(n, "") for n in gap},
    "meta_nodes": meta,
    "duplicates": {str(n): dups[n] for n in sorted(dups)},
    "unresolved_named": unresolved,
}
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_inventory.json")
json.dump(inv, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

print(f"cert files scanned : {len(certs)}")
print(f"distinct lattice nodes present : {len(present_nums)}/256")
print(f"GAP (no birth cert on disk)    : {len(gap)} nodes")
print("  " + ", ".join(f"#{n}" for n in gap))
print(f"meta/pathos nodes present : {sorted(meta)}")
print(f"duplicated nodes (>1 cert): {sorted(int(k) for k in dups)}")
print(f"unresolved named emergents: {len(unresolved)}")
print(f"\nwrote {out}")
