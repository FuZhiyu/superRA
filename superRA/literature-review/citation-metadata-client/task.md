---
title: "Citation-Graph & Metadata Client"
status: not-started
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
