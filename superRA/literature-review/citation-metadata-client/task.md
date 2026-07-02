---
title: "Citation-Graph & Metadata Client"
status: implemented
depends_on: []
---

## Objective

Build the bundled script `skills/literature-review/scripts/` (PEP 723 / `uv run --script`, stdlib-first, modeled on `zotero-paper-reader/scripts/zotero_tool.py`'s JSON-subcommand style) that exposes the citation-graph and metadata operations the review loop needs, each emitting documented JSON:

- **search** — Semantic Scholar relevance search and Crossref bibliographic search, with year/venue/field filters. This is **one discovery lens, not the entry point**: front-line discovery leads with web search (an agent capability at the workflow layer) because S2/Crossref lag on the newest working papers; the client's structured search complements it with filterable, dedupable results over indexed work.
- **references** — backward references of a paper (S2 `/paper/{id}/references`; Crossref `reference` array as a fallback, noting it is uneven and often DOI-less).
- **citations** — forward citations of a paper (S2 `/paper/{id}/citations`) — the snowball backbone; Crossref has none, so this is S2-only, backstopped by the forward web sweep at the workflow layer.
- **metadata** — hydrate by identifier (DOI / arXiv / S2 id): Crossref for the authoritative **published-version-of-record** record; S2/arXiv for abstracts. Returned **verbatim**.
- **dedup** — the cascade: normalized DOI → title+year (+ volume/pages) → fuzzy fallback (`SequenceMatcher` threshold ~0.98), **flag-for-review, never auto-drop** on borderline scores. Must handle DOI-less preprints (fuzzy title+year).

### Deliverables
1. The script with the subcommands above.
2. A command-surface reference doc (loaded on demand from `SKILL.md`).
3. An offline test suite over mocked/fixture API responses so it runs with **no network and no keys** in CI.

### Validation criteria
- Each subcommand emits the documented JSON shape; `--help` per subcommand.
- Dedup cascade unit-tested on synthetic records including DOI-less preprints and reordered author lists.
- **No-key path works**: S2 optional (anonymous pool), Crossref keyless (polite pool via `mailto`); the script degrades gracefully and says so when S2 is unavailable.
- No secret leakage to the transcript; any keys read from env / `Notes/.env` only.
- Version(s) of any pinned dependency logged so behavior drift is visible.

## Planner Guidance

Prefer S2 plain-text abstract, else arXiv for `q-fin.*`/`econ.EM`, else leave empty (Crossref abstracts are spotty for econ). Reconcile S2/Crossref via `externalIds` (DOI ↔ arXiv ↔ S2 id); anchor dedup on normalized DOI. Honor S2 backoff and Crossref `x-rate-limit-*` headers. S2 keys are now issued only to institutional email domains — treat the key as optional and read it from env when present. This is the one hard dependency for `skill-core` and `zotero-add`, so pin the command surface early.

## Results

Delivered the bundled client, its command-surface reference doc, and an offline (no-network, no-key) test suite. All three live under a new `skills/literature-review/` directory (no `SKILL.md` yet — that is `skill-core`'s deliverable, which will load the reference doc on demand).

**Files**

- [`skills/literature-review/scripts/citation_client.py`](../../../skills/literature-review/scripts/citation_client.py) — PEP 723 / `uv run --script`, stdlib-only (empty dependency block; runs equally under plain `python3`). Modeled on `zotero-paper-reader/scripts/zotero_tool.py`'s JSON-subcommand style.
- [`skills/literature-review/references/citation-client.md`](../../../skills/literature-review/references/citation-client.md) — the pinned command surface (subcommand flags + JSON output shapes) that `skill-core` and `zotero-add` read.
- [`skills/literature-review/scripts/test_citation_client.py`](../../../skills/literature-review/scripts/test_citation_client.py) — 42 offline tests via an injected `FakeTransport` over inline synthetic fixtures.

**Pinned command surface** (six subcommands, each JSON on stdout, `--help` on each):

| Subcommand | Purpose | Backends |
|---|---|---|
| `search QUERY` | indexed relevance/bibliographic search, `--source {s2,crossref,both}`, `--year-min/-max`, `--venue`, `--field`, `--limit`, `--raw` | S2 + Crossref |
| `references PAPER_ID` | backward references, `--source {s2,crossref}` (Crossref uneven fallback) | S2 primary, Crossref fallback |
| `citations PAPER_ID` | forward citations (snowball backbone) | S2-only |
| `metadata IDENTIFIER` | verbatim hydration, published-version-of-record | Crossref authoritative + S2/arXiv abstract |
| `dedup` | cascade over a JSON record array (`--file`/stdin) | offline (pure) |
| `health` | versions, config presence (booleans), `s2_key_mode`; `--probe` for one S2 reachability call | — |

The **normalized paper record** shape (the downstream contract) is documented in the reference doc: `id{doi,arxiv,s2,corpus_id}`, verbatim `title/authors/year/venue/abstract`, `abstract_source`, `is_open_access`, `external_ids`, `source`. `given`/`family` author split is populated only from Crossref; S2/arXiv give a display `name` only.

**Dedup cascade** — normalized DOI → exact normalized title+year → fuzzy title (`SequenceMatcher`). Auto-merge at ratio ≥ 0.98; **flag-for-review (never auto-merge/drop)** in `[0.90, 0.98)`; conflicting volume/pages on an otherwise exact title+year match is blocked and flagged. Output carries `clusters` (with richest-member `canonical`) plus `review_pairs`. Unit-tested on DOI-less preprints and reordered author lists.

**Validation evidence**

- Full suite: `uv run --with pytest python -m pytest skills/literature-review/scripts/test_citation_client.py` → **42 passed**. Covers normalization, the four mappers, the dedup cascade (all bands + guards), the API calls via `FakeTransport`, every command handler, S2-outage degradation, and secret hygiene.
- **No-key / no-network**: tests inject a fake transport (no `urllib`); `health` and `dedup` run offline. S2 is optional — on a 429/503/outage the S2-backed commands set `s2_available: false`, add an explanatory `notes` entry, and return remaining-source results with exit 0. Config read from env then `Notes/.env`; env wins.
- **Secret hygiene**: `health` reports key presence as booleans and an `s2_key_mode` label only; `test_health_never_leaks_key_value` asserts a secret value never appears on stdout/stderr.
- **Version logging**: `health` emits `tool_version`, `python_version`, and `dependencies: "stdlib-only"` so behavior drift is visible.
- **Live smoke** (real APIs, one public DOI): `metadata 10.1257/aer.101.5.1649` returned the authoritative Crossref record with structured authors, `version_of_record: true`, S2 `externalIds` reconciled (s2 id + corpus_id) — confirming the mappers match live payload shapes.

**Deviation from Planner Guidance (abstract policy).** Guidance says "else leave empty (Crossref abstracts are spotty)." Implemented as **prefer S2 → arXiv, then retain a Crossref abstract only as a last resort** rather than deleting an already-retrieved verbatim abstract. This honors the stated preference ordering (S2/arXiv win over Crossref) while avoiding lossy deletion of authoritative verbatim data; the consumer sees `abstract_source: "crossref"` and can ignore it. If the researcher wants strict blanking of Crossref abstracts, that is a one-line change in `cmd_metadata`.

**Scope note.** Inventory surfaces (`CATEGORIES.md`, `README.md`, the `using-superra` manifest) are intentionally untouched — those are updated when the `literature-review` skill's `SKILL.md` lands under `skill-core`, not by this script-only task.
