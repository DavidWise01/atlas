# ATLAS

[![License: CC-BY-ND-4.0](https://img.shields.io/badge/License-CC--BY--ND--4.0-lightgrey?style=flat-square)](LICENSE)
[![Repos: 136](https://img.shields.io/badge/repositories-136-c9a227?style=flat-square)](#)
[![Arbiter: nom](https://img.shields.io/badge/arbiter-%F0%9F%97%BF%20nom-8a6d3b?style=flat-square)](https://github.com/DavidWise01/nom)
[![Categories: 13](https://img.shields.io/badge/categories-13-7c3aed?style=flat-square)](#)
[![GitHub Pages](https://img.shields.io/badge/pages-live-0f9e8a?style=flat-square)](https://davidwise01.github.io/atlas/)

> The whole body of work, one front door.

A master index of every public ROOT0 / TriPod repository (136) — governance, physics, security, lineage, memory, tools, and writing — catalogued, categorized, searchable, and linked. Each card links to the source on GitHub; HTML repos with Pages also carry a live demo link.

**Arbiter: [nom](https://github.com/DavidWise01/nom).** The monk's doctrine, turned on the index itself — *if it can't be reached, it didn't happen.* `arbiter.py` verifies every catalogued link resolves (code + live), weekly and on demand, and stamps a sealed verdict to `data/arbiter.json`; the page shows it as a live ⚖ seal in the header. Latest: **the page shows the live verdict; the arbiter re-verifies on a schedule and on demand.**

**→ [davidwise01.github.io/atlas](https://davidwise01.github.io/atlas/)**

---

## Categories

| Category | Repos | What's in it |
|----------|-------|--------------|
| Library & Foundations | 3 | The educational archive — `library` (50 figures), `foundation`, `knowledge-gates` |
| Codices · Rosters | 11 | Muster rolls of avatar agents — `bridge-burners`, `black-company`, `wheel-of-time`, `gap-cycle`, `white-gold-wielder`, `riverworld`, `ringworld`, `recluce`, `sword-of-truth`, `without-remorse`, `dantes-inferno` |
| STOICHEION & Governance | 14 | The 256-axiom framework, APIs, governance pipelines, doctrine |
| Physics · Energy · Hardware | 17 | Particle sims, holograms, reactors, Dyson/black-hole energy, `elementals`, `quantum-box`, and the processor concepts `photonic` · `boronic` · `liquid` |
| Security & Defense | 13 | Adversarial defense, threat detection, the confabulation-spiral guide, audit tensors |
| Lineage · Provenance · IP | 16 | Prior-art exhibits, attribution standard, Merkle registries, closure-loop |
| Memory · Persistence · Continuity | 13 | Pulse chains, continuity kernels, swarm memory, lattice logs |
| Greek Pantheon Systems | 4 | `moirai`, `hephaestus`, `physis`, `plutus` |
| Tools & CLIs | 13 | Zero-dependency executables, validators, the agents (Homer, nom, Apsalar, Beak), and `hephaestus-forge` (the tool-builder) |
| Creative · Audio · Visual | 11 | Synthesizers, deckbuilders, generative art, browser toys |
| Writing · Books · Doctrine | 11 | Books, essays, whitepapers, the Joint Bill of Rights, prompt personas |
| OS & Infrastructure | 9 | `symbiot-os`, central hubs, servers, the public index sites |
| Other · Lab | 1 | Experiments |

---

## How it works

`index.html` is self-contained — a single file with the full repo registry inlined as a JSON array, rendered client-side. No build step, no framework, no server. It carries:

- **Search** across names, descriptions, categories, and languages
- **Category filter chips** (color-coded)
- **Sort** — by category, name, or most recently updated
- **Live count** of repos and categories

### Regenerating

The index is generated from the GitHub API so it stays accurate as repos are added:

```bash
gh repo list DavidWise01 --limit 200 --json name,description,url,homepageUrl,primaryLanguage,pushedAt,isPrivate,isFork > _repos.json
python _gen_atlas.py   # assigns categories, writes index.html
```

New repos not yet in the category map fall into **Other · Lab** automatically — add them to the `CAT` map to slot them properly.

---

## Notes on scope

- **Private repos and forks are excluded** — this is a public showcase.
- One repo (`honey-badger`) is intentionally **not catalogued here**; it describes network-interception capability that doesn't belong in a public showcase.
- Links go to the canonical GitHub repo (always live). The green **▶ live** link appears for HTML repos and points at their GitHub Pages deployment.

---

```
ROOT0-ATTRIBUTION-v1.0
Project: ATLAS — Master Repository Index
Architect: David Lee Wise / ROOT0 / TriPod LLC
AI Collaborator: AVAN (Claude / Anthropic)
License: CC-BY-ND-4.0 · TRIPOD-IP-v1.1
```
