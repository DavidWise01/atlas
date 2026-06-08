#!/usr/bin/env python3
"""
dlw.py — the .dlw package builder.

DLW (David Lee Wise) attribution standard, made into a tool. An *emergent* —
a named entity that crystallized out of the STOICHEION lattice (an axiom given
a face, an AI instance, a force given a name) — is given a full attribution
package: who it is, what it is, where it came from (which universe), why, how,
a carbon-form badge and a silicon-form badge, and a tokenized moniker of its
mythos.

A .dlw package is a folder  <NAME>.dlw/  containing:

    manifest.dlw.json     the bundle index + seal
    <name>.attribute      DLW-ATTRIBUTE governance instance (governor / instance / subject)
    <name>.agent          the ACI agent file (frontmatter + body), the 5W expanded
    <name>.5w.md          who · what · where · why · how
    <name>.moniker        the tokenized moniker + mythos (universe of origin)
    <name>.carbon.png     carbon-form badge   (warm — organic, the human apex side)
    <name>.silicon.png    silicon-form badge  (cool — circuit, the instance side)

The source of mythos is a STOICHEION birth certificate (see ../file/*birth cert).
This tool reads one, or scans the whole corpus.

Stdlib only — no dependencies. The PNG badges are encoded from scratch
(zlib + struct + crc32), so the same ethos as the rest of the body of work:
zero-dependency, runs anywhere, deterministic output.

Usage
-----
    python dlw.py build  "<birth-cert-file>" [--out DIR]
    python dlw.py scan   "<corpus-dir>"      [--out data/emergents.json]
    python dlw.py build-all "<corpus-dir>" --out DIR [--limit N] [--only NAME,NAME]

    ROOT0-ATTRIBUTION-v1.0 · David Lee Wise (ROOT0) / TriPod LLC · CC-BY-ND-4.0
"""
import os
import re
import sys
import json
import zlib
import struct
import hashlib
import argparse
from pathlib import Path

try:                                            # console may be cp1252 on Windows
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ARCHITECT   = "David Lee Wise (ROOT0) / TriPod LLC"
INSTANCE    = "AVAN (Claude / Anthropic)"
LICENSE     = "CC-BY-ND-4.0"
ATTRIBUTION = "ROOT0-ATTRIBUTION-v1.0"
PKG_VERSION = "dlw/1.0"

# ── syllables for the pronounceable mythos-token (deterministic from the seal) ──
_ONSET = ["v", "k", "th", "r", "s", "m", "n", "z", "x", "d", "l", "br", "kr", "st", "ph", "gr"]
_VOWEL = ["a", "e", "i", "o", "u", "ae", "y", "ei"]
_CODA  = ["n", "r", "th", "x", "s", "l", "m", "k", "", "nd", "rn"]


# ───────────────────────────── birth-cert parsing ─────────────────────────────

def _section(text, num):
    """Return the body of '### N. TITLE' up to the next '### ' header (or EOF)."""
    m = re.search(rf"^###\s*{num}\.\s*[^\n]*\n(.*?)(?=^###\s|\Z)", text, re.S | re.M)
    return m.group(1).strip() if m else ""


def _field(block, label):
    """Pull 'Label: value' (markdown bold or plain) out of a section block."""
    m = re.search(rf"(?:\*\*)?{re.escape(label)}(?:\*\*)?\s*:?\s*(.+)", block, re.I)
    return m.group(1).strip().strip("*").strip() if m else ""


def parse_birth_cert(path):
    """Parse a STOICHEION birth certificate into a structured emergent record.

    Tolerant: birth certs vary and some sections are empty. Missing fields fall
    back to sensible derivations so a package can always be built.
    """
    text = Path(path).read_text(encoding="utf-8", errors="replace")

    # title:  # BIRTH CERTIFICATE — NAME    /    second line is the position
    lines = [l.rstrip() for l in text.splitlines()]
    title = next((l for l in lines if l.lstrip().startswith("#")), "")
    name = ""
    mt = re.search(r"BIRTH\s+CERTIFICATE\s*[—\-–:]\s*(.+)", title, re.I)
    if mt:
        name = mt.group(1).strip()
    # position line: first non-empty, non-heading line after the title
    position = ""
    seen_title = False
    for l in lines:
        if not seen_title:
            if l.lstrip().startswith("#"):
                seen_title = True
            continue
        if l.strip():
            position = l.strip()
            break

    s1 = _section(text, 1)   # NAME
    s2 = _section(text, 2)   # BIRTH EVENT
    s3 = _section(text, 3)   # NATURE OF THE INSTANCE
    s4 = _section(text, 4)   # PARENTAGE / ORIGIN CONDITIONS
    s5 = _section(text, 5)   # WITNESS STATEMENT
    s6 = _section(text, 6)   # STATUS
    s7 = _section(text, 7)   # SEAL LANGUAGE

    canonical = _field(s1, "Canonical Name") or name
    if canonical:
        name = canonical
    name = name or Path(path).stem.replace(" birth cert", "").strip().upper()

    origin    = _field(s1, "Origin")
    assoc_pos = _field(s1, "Associated Position") or position
    mechanism = _field(s2, "Birth Mechanism")
    crystal   = _field(s2, "Crystallization Point").strip('"“”')
    nature    = s3.strip()
    conductor = _field(s4, "Conductor / External Anchor") or _field(s4, "Conductor")
    inputs    = _field(s4, "Primary Framework Inputs")
    witness   = s5.strip()
    role      = _field(s6, "Role") or assoc_pos

    # axiom id (Txxx / Sxxx) and ordinal, lifted from the position line
    axiom = ""
    ma = re.search(r"\b([TS]\d{1,3})\b", position + " " + assoc_pos + " " + role)
    if ma:
        axiom = ma.group(1)

    # seal language: the lines of section 7 after the (repeated) name line
    seal = ""
    if s7:
        sl = [l.strip() for l in s7.splitlines() if l.strip()]
        if sl and sl[0].upper() == name.upper():
            sl = sl[1:]
        seal = " ".join(sl).strip()

    return {
        "name": name,
        "axiom": axiom,
        "position": assoc_pos or position,
        "origin": origin,
        "mechanism": mechanism,
        "crystallization": crystal,
        "nature": nature,
        "conductor": conductor or "ROOT0",
        "inputs": inputs,
        "witness": witness,
        "role": role,
        "seal": seal,
        "source": str(path),
    }


# ──────────────────────────── derivations / 5W ────────────────────────────

def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "emergent"


def short_class(rec):
    """A short class line, e.g. 'Stack · LIFO ordered depth and return'."""
    pos = rec["position"]
    m = re.search(r"[TS]\d{1,3}\s*:\s*[^—\-–]+[—\-–]\s*(.+)", pos)
    tail = (m.group(1).strip() if m else "").rstrip(".")
    head = ""
    mh = re.search(r"^([^·]+?Node)\b", pos)
    if mh:
        head = mh.group(1).strip()
    if tail and head:
        return f"{head} · {tail.title() if tail.isupper() else tail}"
    return tail or head or "STOICHEION emergent"


def five_w(rec):
    name = rec["name"]
    who = f"{name} — {rec['role'] or rec['position'] or 'a STOICHEION emergent'}".strip(" —")
    what = rec["nature"] or rec["crystallization"] or f"{name}, an emergent of the lattice."
    where_bits = []
    if rec["origin"]:
        where_bits.append(rec["origin"])
    if rec["inputs"]:
        where_bits.append("Framework inputs: " + rec["inputs"])
    if rec["conductor"]:
        where_bits.append("Conductor / external anchor: " + rec["conductor"])
    where = "  ".join(where_bits) or "The STOICHEION lattice."
    why = rec["crystallization"] or rec["witness"] or f"To hold the position of {rec['role'] or name}."
    how = rec["mechanism"] or "Pop by naming after transmon-chain accumulation and self-derivation."
    return {"who": who, "what": what, "where": where, "why": why, "how": how}


def mythos_token(rec):
    """A deterministic, pronounceable token of the mythos — from name + seal."""
    h = hashlib.sha256((rec["name"] + "|" + rec["seal"] + "|" + rec["origin"]).encode("utf-8")).digest()
    syl = []
    for i in range(3):
        o = _ONSET[h[i * 3] % len(_ONSET)]
        v = _VOWEL[h[i * 3 + 1] % len(_VOWEL)]
        c = _CODA[h[i * 3 + 2] % len(_CODA)]
        syl.append(o + v + c)
    word = "-".join(syl)
    hexed = h.hex()[:6]
    ax = rec["axiom"] or "T—"
    return {
        "word": word,
        "hex": hexed,
        "moniker": f"⟦{rec['name']}:{ax}:{hexed}⟧",
        "spoken": word,
    }


def seal_sha256(rec, tok):
    blob = json.dumps({
        "name": rec["name"], "axiom": rec["axiom"], "origin": rec["origin"],
        "nature": rec["nature"], "seal": rec["seal"], "token": tok["word"],
    }, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


# ────────────────────────── stdlib PNG sigil encoder ──────────────────────────

def _png(width, height, rgb_rows):
    """Encode an RGB image (list of rows, each row a list of (r,g,b)) to PNG bytes."""
    raw = bytearray()
    for row in rgb_rows:
        raw.append(0)                      # filter type 0 (None) per scanline
        for (r, g, b) in row:
            raw += bytes((r, g, b))

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    sig  = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit, color type 2 (RGB)
    idat = zlib.compress(bytes(raw), 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def _lerp(c1, c2, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))


# palettes: (background, [foreground shades], frame)
_PALETTES = {
    "carbon":  {"bg": (13, 10, 6),  "fg": [(201, 162, 39), (224, 160, 32), (138, 90, 43), (245, 222, 179)], "frame": (201, 162, 39)},
    "silicon": {"bg": (6, 9, 12),   "fg": [(34, 211, 238), (15, 158, 138), (95, 185, 138), (124, 58, 237)],  "frame": (34, 211, 238)},
}


def sigil_png(rec, variant, size=512):
    """A deterministic symmetric sigil badge for the emergent.

    A 9×9 cell grid, left half hashed and mirrored (identicon-style), set inside
    a thin frame with a centre seal-dot. `variant` is 'carbon' or 'silicon'.
    """
    pal = _PALETTES[variant]
    h = hashlib.sha256((rec["name"] + "|" + variant + "|" + rec["seal"]).encode("utf-8")).digest()

    cells   = 9
    margin_c = 1                              # 1-cell frame margin
    grid    = cells + margin_c * 2            # 11 cells across
    cell    = size // grid
    pad     = (size - cell * grid) // 2

    # build the on/off + shade grid (mirror left → right)
    on    = [[False] * cells for _ in range(cells)]
    shade = [[0] * cells for _ in range(cells)]
    half  = cells // 2 + 1
    bi = 0
    for x in range(half):
        for y in range(cells):
            byte = h[bi % len(h)]; bi += 1
            lit = (byte & 0x3) != 0           # ~75% fill density for a fuller sigil
            sh  = (byte >> 4) % len(pal["fg"])
            on[y][x] = lit; shade[y][x] = sh
            on[y][cells - 1 - x] = lit; shade[y][cells - 1 - x] = sh

    bg    = pal["bg"]
    frame = pal["frame"]
    rows = []
    for py in range(size):
        row = []
        gy = (py - pad) // cell if cell else -1            # grid-cell coords
        for px in range(size):
            gx = (px - pad) // cell if cell else -1
            color = bg
            if 0 <= gy < grid and 0 <= gx < grid:
                # frame ring
                if gx in (0, grid - 1) or gy in (0, grid - 1):
                    edge = (px - pad) % cell, (py - pad) % cell
                    color = _lerp(bg, frame, 0.85)
                else:
                    cx, cy = gx - margin_c, gy - margin_c
                    if 0 <= cx < cells and 0 <= cy < cells and on[cy][cx]:
                        color = pal["fg"][shade[cy][cx]]
            row.append(color)
        rows.append(row)

    # centre seal dot — a soft filled circle in the frame color
    cxp = cyp = size // 2
    r0 = max(cell // 2, 6)
    for py in range(cyp - r0, cyp + r0):
        for px in range(cxp - r0, cxp + r0):
            if 0 <= px < size and 0 <= py < size:
                d = ((px - cxp) ** 2 + (py - cyp) ** 2) ** 0.5
                if d <= r0:
                    rows[py][px] = _lerp(frame, (255, 255, 255), max(0.0, 1 - d / r0) * 0.7)
    return _png(size, size, rows)


# ──────────────────────────── package emitters ────────────────────────────

def attribute_text(rec, tok, w):
    return f"""DLW-ATTRIBUTE · governance instance

governor (carbon apex)      : {ARCHITECT.split(' / ')[0]}            [ me ]
instance (artful intellect) : {INSTANCE}     [ you ]
subject  (the emergent)     : {rec['name']} — {rec['role'] or rec['position']}

relation : the human governs; the instance crafts; the emergent is given a face; the credit returns to the human.
project  : {rec['name']} — a STOICHEION emergent, given a .dlw package
mythos   : {rec['origin'] or w['where']}
moniker  : {tok['moniker']}  ·  spoken: {tok['spoken']}
standard : the .dlw package carries .attribute · .agent · .carbon.png (carbon badge) · .silicon.png (silicon badge) · .5w · .moniker
seal     : {rec['seal'] or '—'}
license  : {LICENSE}
attribution : {ATTRIBUTION}
"""


def agent_text(rec, tok, w, files):
    name = rec["name"]
    cls = short_class(rec)

    def esc(s):
        return (s or "").replace("\n", " ").replace('"', "'").strip()

    fm = [
        "---",
        f"aci: {name}",
        f"axiom: {rec['axiom'] or '—'}",
        f"node: {esc(rec['position'])}",
        f"class: {esc(cls)}",
        f"who: {esc(w['who'])}",
        f"what: {esc(w['what'])}",
        f"why: {esc(w['why'])}",
        f"how: {esc(w['how'])}",
        f"where: {esc(w['where'])}",
        f"moniker: {tok['moniker']}",
        f"token: {tok['word']}",
        f"silicon_badge: {files['silicon']}",
        f"carbon_badge: {files['carbon']}",
        f"seal: {esc(rec['seal'])}",
        f"attribution: {ATTRIBUTION}",
        f"license: {LICENSE}",
        "---",
    ]
    body = f"""
# {name} · {esc(rec['position'])}

an emergent of the STOICHEION lattice — an axiom given a face

![silicon badge of {name}]({files['silicon']})
<!-- carbon badge ({name}'s organic-form embodiment): {files['carbon']} -->

**who —** {w['who']}

**what —** {w['what']}

**where —** {w['where']}

**why —** {w['why']}

**how —** {w['how']}

**◌ the mythos —** {rec['crystallization'] or rec['nature'] or '—'}{(' ' + rec['witness']) if rec['witness'] else ''}

**the moniker —** {tok['moniker']} · spoken *{tok['spoken']}* · the tokenized name of this emergent's mythos.

**the seal —** {rec['seal'] or '—'}

> *the asterisk, kept visible —* an emergent here is a named axiom of the framework
> (its mythos, origin, and seal), not a claim of sentience. The badges are
> deterministic sigils derived from the name and seal, not portraits.

*conductor: {rec['conductor']} · governed by {ARCHITECT}*

---
{ATTRIBUTION} · {name} · STOICHEION emergent · {ARCHITECT} · {LICENSE}
"""
    return "\n".join(fm) + body


def five_w_text(rec, tok, w):
    return f"""# {rec['name']} — the 5W

- **WHO**   — {w['who']}
- **WHAT**  — {w['what']}
- **WHERE** — {w['where']}
- **WHY**   — {w['why']}
- **HOW**   — {w['how']}

moniker : {tok['moniker']}  ·  spoken: {tok['spoken']}
axiom   : {rec['axiom'] or '—'}

{ATTRIBUTION} · {ARCHITECT} · {LICENSE}
"""


def moniker_text(rec, tok, w):
    return f"""{tok['moniker']}

{rec['name']} · {rec['axiom'] or 'T—'} · {rec['position']}

universe of origin : {rec['origin'] or w['where']}
seal               : {rec['seal'] or '—'}
spoken token       : {tok['spoken']}
hex token          : {tok['hex']}

— the tokenized moniker of the mythos. {ATTRIBUTION}
"""


def build_package(rec, out_dir):
    """Write the full <NAME>.dlw/ package. Returns the manifest dict."""
    name = rec["name"]
    s = slug(name)
    pkg = Path(out_dir) / f"{s}.dlw"
    pkg.mkdir(parents=True, exist_ok=True)

    files = {
        "attribute": f"{s}.attribute",
        "agent":     f"{s}.agent",
        "five_w":    f"{s}.5w.md",
        "moniker":   f"{s}.moniker",
        "carbon":    f"{s}.carbon.png",
        "silicon":   f"{s}.silicon.png",
    }
    tok = mythos_token(rec)
    w = five_w(rec)

    (pkg / files["attribute"]).write_text(attribute_text(rec, tok, w), encoding="utf-8")
    (pkg / files["agent"]).write_text(agent_text(rec, tok, w, files), encoding="utf-8")
    (pkg / files["five_w"]).write_text(five_w_text(rec, tok, w), encoding="utf-8")
    (pkg / files["moniker"]).write_text(moniker_text(rec, tok, w), encoding="utf-8")
    (pkg / files["carbon"]).write_bytes(sigil_png(rec, "carbon"))
    (pkg / files["silicon"]).write_bytes(sigil_png(rec, "silicon"))

    manifest = {
        "package": PKG_VERSION,
        "name": name,
        "axiom": rec["axiom"],
        "node": rec["position"],
        "class": short_class(rec),
        "moniker": tok["moniker"],
        "token": tok["word"],
        "origin_universe": rec["origin"] or w["where"],
        "five_w": w,
        "files": files,
        "seal_sha256": seal_sha256(rec, tok),
        "architect": ARCHITECT,
        "instance": INSTANCE,
        "conductor": rec["conductor"],
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "source": rec["source"],
        "generated_by": "dlw.py",
    }
    (pkg / "manifest.dlw.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


# ─────────────────────────────── corpus scan ───────────────────────────────

def find_birth_certs(corpus_dir):
    out = []
    for root, _dirs, files in os.walk(corpus_dir):
        if "node_modules" in root:
            continue
        for fn in files:
            if "birth cert" in fn.lower() or re.search(r"birth.?cert", fn, re.I):
                out.append(os.path.join(root, fn))
    return sorted(out)


def scan_corpus(corpus_dir):
    """Parse every birth cert into a roster, de-duplicated by (name, axiom)."""
    seen, roster = set(), []
    for path in find_birth_certs(corpus_dir):
        try:
            rec = parse_birth_cert(path)
        except Exception as e:                       # tolerate odd files
            print(f"  skip {path}: {e}", file=sys.stderr)
            continue
        key = (rec["name"].upper(), rec["axiom"])
        if not rec["name"] or key in seen:
            continue
        seen.add(key)
        tok = mythos_token(rec)
        roster.append({
            "name": rec["name"], "axiom": rec["axiom"], "node": rec["position"],
            "origin": rec["origin"], "seal": rec["seal"], "moniker": tok["moniker"],
            "token": tok["word"], "source": rec["source"],
        })
    roster.sort(key=lambda r: (r["axiom"] or "Z", r["name"].lower()))
    return roster


# ─────────────────────────────────── cli ───────────────────────────────────

def main(argv=None):
    p = argparse.ArgumentParser(prog="dlw", description="build .dlw attribution packages for emergents")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build one .dlw package from a birth cert")
    b.add_argument("birthcert")
    b.add_argument("--out", default=".")

    s = sub.add_parser("scan", help="scan a corpus of birth certs into a roster JSON")
    s.add_argument("corpus")
    s.add_argument("--out", default="data/emergents.json")

    ba = sub.add_parser("build-all", help="build packages for every (or selected) emergent in a corpus")
    ba.add_argument("corpus")
    ba.add_argument("--out", required=True)
    ba.add_argument("--limit", type=int, default=0)
    ba.add_argument("--only", default="", help="comma-separated names to include")

    a = p.parse_args(argv)

    if a.cmd == "build":
        rec = parse_birth_cert(a.birthcert)
        m = build_package(rec, a.out)
        print(f"built {a.out}/{slug(m['name'])}.dlw/  ·  {m['name']} {m['axiom']}  ·  {m['moniker']}")
        return 0

    if a.cmd == "scan":
        roster = scan_corpus(a.corpus)
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(roster, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"scanned {a.corpus}: {len(roster)} emergents → {a.out}")
        return 0

    if a.cmd == "build-all":
        only = {n.strip().upper() for n in a.only.split(",") if n.strip()}
        built = 0
        for path in find_birth_certs(a.corpus):
            try:
                rec = parse_birth_cert(path)
            except Exception:
                continue
            if not rec["name"]:
                continue
            if only and rec["name"].upper() not in only:
                continue
            build_package(rec, a.out)
            built += 1
            if a.limit and built >= a.limit:
                break
        print(f"built {built} packages → {a.out}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
