---
name: literature-review
description: Economics/finance literature-review discipline — search, screen, snowball, and classify a curated, provenance-tracked collection of papers. Use whenever the user wants to build a literature review, survey, related-work section, or reading list for an econ/finance research area: finding, screening, deduping, and organizing many papers via snowball citation search, inclusion/exclusion criteria, and per-paper extraction. Reach for this even when the user does not say "literature review" but is assembling or mapping the papers on a topic. Not for reading, summarizing, or citing a single already-known paper — that is zotero-paper-reader.
user-invocable: true
---

# Literature Review

Discipline for economics/finance literature reviews. A review here produces a **curated, provenance-tracked, classified collection** — a screened paper set, a per-paper justification and extraction, a classification/gap analysis, and a convergence judgment. Drafting prose from that collection is a separate, later step; the deliverable is the organized evidence, not written synthesis.

Discovery is **web-first and multi-modal**: no single index is authoritative. Lead with the agent's own web search across several blind lenses, use the citation graph for snowballing, and take every bibliographic field verbatim from the published version of record — an agent never types metadata.

## References

Load per workflow point; do not load them all at once.

| Reference | Load when |
|---|---|
| `references/search-and-screening.md` | running discovery — snowball method (backward citation BFS + forward multi-lens web sweep), screen-first triage, the dedup cascade, and the stopping/convergence judgment. |
| `references/econ-corpus.md` | judging coverage and quality — working-paper-first sourcing (SSRN / NBER / RePEc), published-version metadata with the WP-divergence flag, JEL codes, and weighting by outlet tier + identification strategy. |
| `references/grounding-and-extraction.md` | extracting from a paper — DOI resolution before trusting a cite, the quote-grounded concept matrix, and honest null vs "not reported". |
| `references/synthesis-and-classification.md` | organizing the collection — concept-centric organization, matrix-sparsity gap detection, and the optional classification-axis pass. |
| `references/citation-client.md` | calling the bundled citation-graph + metadata client — subcommands (`search`, `references`, `citations`, `metadata`, `dedup`, `health`) and their JSON shapes. |

## Composed skills

Route to these rather than reimplementing their work:

- **`zotero-paper-reader`** — dedup a candidate against the existing library, fetch PDFs, export BibTeX / insert cites, and (via its `add` / `attach` path) save discovered papers into the target library the setup survey selected.
- **`mistral-pdf-to-markdown`** — OCR only the curated shortlist of central included papers. Bulk OCR is deferred; screening never needs it.
- **`writing`** — any reader-facing prose (gap analysis, a synthesis note, a related-work draft).

## Workflow

The skill runs in two parts: a main-agent **interactive setup**, then a **loop-until-dry fan-out**.

### Part 1 — Interactive setup (main agent)

Before any discovery, ask the researcher (via `AskUserQuestion`) to settle the parameters below, then scaffold the ledger. These are the researcher's to define — this is elicitation, not a fixed template.

- **Research question and scope** — the topic boundary the review covers.
- **Inclusion/exclusion criteria + quality bar** — the gates a paper must pass, and the outlet-tier / identification-strategy bar (see `references/econ-corpus.md`).
- **Extraction/classification schema** — the per-paper fields to record and any classification axes (e.g. model structure, identification method).
- **Seed set** — the starting papers the snowball expands from.
- **Zotero add policy** — whether to save discovered/included papers to Zotero, and if so which **library** (personal or a specific group) and **collection**. This answer also selects the add path in `zotero-paper-reader`: "my library / current selection" saves via the local connector; a specific group or collection it cannot target uses the cloud Web API. Before any local save, report the currently-selected Zotero destination so the researcher can switch it in the desktop UI first.

### Part 2 — Fan-out execution (loop-until-dry)

Screen / summarize / classify agents run in rounds. Each round selects the current frontier, dispatches **one agent per paper**, and the orchestrator dedups what the agents surface and grows the frontier. Each agent writes **only its own** ledger entry — no two agents touch the same file, so there is no write contention.

Per dispatched agent, for its one paper:

1. Fetch metadata + abstract — verbatim, from the published version of record (`citation_client metadata`, or a source-page `citation_*` / Dublin Core tag when no structured record exists).
2. Screen against the criteria from metadata / abstract / intro only — no full-text OCR during screening.
3. Write its ledger entry (schema below): decision, reason, failing gate, provenance, PDF path + divergence flag, and the researcher's extraction fields.
4. Return surfaced candidates — backward references (`citation_client references`) and forward-citation / web-sweep hits — for the orchestrator to dedup.

## Ledger schema

Each considered paper — included or excluded — gets one entry keyed on `firstauthor-year` (the dedup identity). The entry records:

- **metadata** — verbatim published-version-of-record fields.
- **provenance** — `discovered_via` (`seed` | `<parent-key>` | `web:<lens>` | `forward-cite`) and `bfs_depth`.
- **decision** — `included` / `excluded`, the reason, and the failing gate when excluded.
- **pdf/md path** — plus the **version-divergence flag** when the PDF is a preprint/WP that differs from the published metadata (e.g. metadata = published JF 2024; PDF = 2021 SSRN WP). Required — WP and published versions differ materially in economics.
- **extraction/classification fields** — the schema the setup survey defined.

Two representations, same fields:

- **subtree-as-ledger** (inside a superRA tree) — one subtask per paper; directory name = paper key; `status` encodes the discovery frontier (`not-started` = unscreened frontier, `implemented` = screened, `approved` = confirmed, `postponed` = can't fetch); in/out is a tag (`included` / `archived`).
- **folder ledger** (standalone) — a papers ledger file plus a `Notes/papers/` store, following the project's convention.

## Executor template

Run the fan-out as a loop-until-dry snowball. The orchestrator owns the `seen` dedup index and frontier growth; each round is a parallel fan-out.

```
seen = {}                      # normalized DOI / title+year → paper key
frontier = seed set            # from the setup survey

while frontier is non-empty:
    # one round — parallel fan-out, one agent per paper
    dispatch a screening agent for each paper in frontier   (in parallel)
    returned = union of every agent's surfaced candidates
               (backward references + forward-cite / web-sweep hits)

    clusters = citation_client dedup over returned           # cross-agent dedup
    new = in-scope canonicals not already in seen
    add new to seen
    frontier = new

    if new is empty:           # a dry round
        break

record the convergence judgment and any deliberate non-expansions
```

Stop when a full backward round and the forward web sweep add essentially no new in-scope papers, and record that stopping judgment plus any in-scope areas you deliberately did not expand.

**Alternative executor.** Inside a superRA tree, run the rounds as a `superimplement`-style dispatch loop over the per-paper subtasks — the subtree-as-ledger `status` field is the frontier, so each round dispatches the `not-started` frontier and marks entries as they are screened. Use this when the review lives in a task tree; use the plain loop above when it is standalone.
