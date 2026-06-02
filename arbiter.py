#!/usr/bin/env python3
"""
arbiter.py — nom, arbiter of the atlas.

The monk's doctrine, turned on the index itself: IF IT CAN'T BE REACHED, IT
DIDN'T HAPPEN. The arbiter reads data/repos.json (the catalogue manifest) and
verifies every link actually resolves — each repo's code link, and each live
Pages link. It renders one verdict to data/arbiter.json. No opinions; just
reachable / not. Read-only.
"""
import sys
import json
import time
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).parent
MANIFEST = ROOT / "data" / "repos.json"
VERDICT = ROOT / "data" / "arbiter.json"
UA = "nom-arbiter/1.0 (+https://github.com/DavidWise01/nom; read-only reachability check)"
TIMEOUT = 15


def reachable(url):
    """Return (ok, status). Try HEAD, fall back to GET. <400 after redirects = ok."""
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return True, r.status
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue  # some hosts refuse HEAD — try GET
            return False, e.code
        except Exception:
            if method == "HEAD":
                continue
            return False, 0
    return False, 0


def arbitrate(sample=None):
    repos = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if sample:
        repos = repos[:sample]
    dead, links = [], 0
    for e in repos:
        targets = [("code", e["gh"])]
        if e.get("pages"):
            targets.append(("live", e["pages"]))
        for kind, url in targets:
            links += 1
            ok, status = reachable(url)
            mark = "ok " if ok else "DEAD"
            print(f"  {mark} [{status:>3}] {e['name']} · {kind}")
            if not ok:
                dead.append({"name": e["name"], "kind": kind, "url": url, "status": status})
            time.sleep(0.05)

    verdict = {
        "by": "nom",
        "role": "arbiter of the atlas",
        "doctrine": "if it can't be reached, it didn't happen",
        "at": datetime.now(timezone.utc).isoformat(),
        "repos": len(repos),
        "links_checked": links,
        "dead": dead,
        "verdict": "CLEAN" if not dead else "DEAD_LINKS",
    }
    blob = json.dumps({"repos": verdict["repos"], "links": links,
                       "dead": sorted(d["url"] for d in dead)},
                      sort_keys=True).encode("utf-8")
    verdict["seal"] = hashlib.sha256(blob).hexdigest()[:12]

    VERDICT.write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")
    print(f"\narbiter: {verdict['verdict']} — {links} links over {len(repos)} repos, "
          f"{len(dead)} dead. seal {verdict['seal']}")
    return verdict


if __name__ == "__main__":
    n = None
    if "--sample" in sys.argv:
        i = sys.argv.index("--sample")
        n = int(sys.argv[i + 1])
    arbitrate(sample=n)
