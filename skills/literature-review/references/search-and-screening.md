# Search & Screening — Snowball to Saturation

Load when running discovery: the two-phase snowball, screen-first triage, the dedup cascade, and the stopping judgment.

## Snowball to saturation, don't query once

A single keyword query never covers an economics/finance area — working papers circulate for years under shifting titles and indexes lag the frontier. Use **snowballing** (Wohlin's method): start from a seed set of known-relevant papers, follow citation edges outward — backward to the papers they cite, forward to the papers that cite them — screen each new paper, add the in-scope ones to the frontier, and repeat until a full round adds essentially nothing.

Keyword and semantic search seed and supplement the snowball; they do not replace it. Lead front-line discovery with web search — the citation graph misses the newest working papers.

## Phase 1 — Backward citation BFS

From every in-scope paper, pull its reference list (`citation_client references PAPER_ID`, S2-backed; Crossref is the DOI-less fallback). These are the intellectual ancestors — the work the authors built on. Screen them, add the in-scope ones to the next frontier, and record `discovered_via: <parent-key>` and `bfs_depth` on each. Run this as breadth-first: screen the whole current frontier before descending a level, so depth reflects citation distance from the seeds rather than the order agents happened to run.

## Phase 2 — Forward multi-lens web sweep

Forward expansion finds the descendants — newer work citing the current set. It has two sources:

- **Forward citations** — `citation_client citations PAPER_ID`. Under the default `--source auto` this is S2 → OpenCitations fallback (keyless, DOI→DOI) when S2 throttles → empty with a web-sweep note if both are down. **Union across version DOIs:** in economics a paper's forward citations fragment across its NBER (`10.3386/*`), SSRN (`10.2139/ssrn.*`), and journal DOIs, and OpenCitations is DOI-keyed — so for complete forward coverage call `citations` once per known version DOI and union the results (the client stays per-DOI; the union is this workflow step). Dedup the union with the cascade below.
- **Multi-lens web sweep** — several **blind** web queries, each formulated without reference to the others' results and each scoped to a different surface: `site:ssrn.com`, `site:nber.org`, RePEc/IDEAS, arXiv `q-fin`/`econ`, author pages, and an unscoped WebSearch that approximates Google Scholar (broadest working-paper coverage, no API). Union the hits and dedup — overlap is expected and is the dedup cascade's job, not a reason to run fewer lenses.

Record forward hits as `discovered_via: forward-cite` or `web:<lens>`.

## Screen-first triage

Screen every frontier paper from **metadata, abstract, and introduction only** — no full-text OCR during screening. The inclusion criteria settled in setup are the triage gates; each screen produces a decision (`included` / `excluded`), a one-line reason, and — when excluded — the specific gate it failed. Only the curated shortlist of central included papers is later OCR'd (via `mistral-pdf-to-markdown`); bulk OCR is deferred and screening never needs it.

Judge quality at the same time using the outlet-tier and identification-strategy bar in [econ-corpus.md](econ-corpus.md).

## The dedup cascade

Agents surface raw candidates; the orchestrator holds the single `seen` index (normalized DOI / title+year → paper key) and dedups across agents each round with `citation_client dedup`. The cascade is: normalized **DOI** → exact **title+year** → **fuzzy title** at the same year. Matches at ratio ≥ 0.98 auto-merge; borderline matches (0.90–0.98) are flagged for review and **never auto-merged**; an exact title+year with conflicting volume/pages is blocked and flagged.

A working paper and its published version are the **same** paper — merge them under the published key with a version-divergence flag (see [econ-corpus.md](econ-corpus.md)), not two entries. The paper key (`firstauthor-year`) is the dedup identity; two entries sharing it are the same paper.

## The stopping / convergence judgment

Stop when a full backward round **and** the forward sweep add essentially no new in-scope papers. "Essentially no new" is concrete: the round's candidates all dedup into `seen`, or all fail the scope gate. A dry round is the saturation signal — one dry round after both phases have run at least once is the stop.

Record the judgment explicitly: what the last round returned, and why that means the map is saturated (e.g. "final backward round surfaced 14 candidates, all already in `seen`; forward sweep across six lenses surfaced 3, all out of scope on the identification bar"). Then record **deliberate non-expansions** — in-scope-adjacent branches you chose not to follow (an adjacent literature scoped out, a methodological cluster deferred). Naming them tells a reader they are a boundary choice, not an oversight.

## Identification protocol — reading the ledger for under-saturation

Walk the ledger entry by entry and flag these tells:

- **Provenance missing.** An entry with no `discovered_via` / `bfs_depth` cannot be placed in the snowball — its coverage is unaudited. Every entry carries provenance.
- **Seed-only depth.** If every in-scope entry is `bfs_depth: 0`, the backward BFS never ran a second round — the ancestors are unexplored.
- **Single-lens forward.** If every forward hit shares one `web:<lens>` value, the sweep was not multi-lens; holes the other lenses cover are unsearched.
- **Excluded without a gate.** An `excluded` entry with a reason but no named failing gate hides which criterion did the work — the screen is not reproducible.
- **Over-read screen.** A screening reason that cites full-text page numbers or a results section means the paper was read past the abstract/intro to decide in/out. The triage should resolve from metadata/abstract/intro; if it did not, the criteria may be too fine for screen-first and should be revisited.
- **No stopping judgment.** A completed loop with no recorded convergence judgment cannot be shown to be saturated — the stop is an assertion, not evidence.
