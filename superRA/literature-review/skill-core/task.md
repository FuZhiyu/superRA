---
title: "Skill Core — SKILL.md, Workflow & Ledger/Executor"
status: approved
depends_on: [citation-metadata-client]
---

## Objective

Author `skills/literature-review/SKILL.md` — frontmatter trigger metadata (explicit trigger conditions for discovery) plus a concise, procedural body that routes depth to the references owned by `skill-references`. The body owns the **execution shape**; discipline detail lives in references.

### The two-part workflow (the skill's core)
1. **Interactive setup (main agent).** Ask questions to settle: the research question/scope, the **inclusion/exclusion criteria + quality bar**, the **extraction/classification schema** (the per-paper fields and any classification axes), the **seed set**, and the **Zotero add policy** — whether to save discovered/included papers to Zotero, and if so which **library** (personal or a group) and **collection** (this answer also selects the add path per `zotero-add`). Then scaffold the ledger. This is an `AskUserQuestion`-driven elicitation, not a fixed template — the criteria and schema are the researcher's to define.
2. **Fan-out execution.** Screen / summarize / classify agents run **loop-until-dry**: each round selects the frontier, dispatches one agent per paper (fetch metadata/abstract, screen against the criteria, write its own ledger entry, return surfaced candidates), the orchestrator dedups returned candidates and grows the frontier. Each agent writes **only its own** ledger entry — no write contention.

### Ledger schema (both modes)
Define the per-paper entry: verbatim published-version-of-record **metadata**; **provenance** (`discovered_via` = seed | parent-key | web:lens | forward-cite; `bfs_depth`); the **decision** (included/excluded, reason, failing gate); **pdf/md path** with the **version-divergence flag**; and the researcher's **extraction/classification fields**. Specify both representations:
- **subtree-as-ledger** (inside a superRA tree) — dir = paper key, `status` encodes the frontier, in/out is a tag (`included`/`archived`), per the parent Conventions.
- **folder ledger** (standalone) — a ledger file + `Notes/papers/` store, following project convention.

### Executor template
Provide the `Workflow` loop-until-dry template (parallel per-round fan-out, dedup vs a `seen` set, stop when a round is dry) as the recommended executor, with the superimplement-style dispatch loop noted as the alternative.

### Validation criteria
- `SKILL.md` triggers on realistic lit-review prompts and reads cleanly standalone.
- The workflow is runnable both standalone (folder ledger) and inside a superRA tree (subtree ledger).
- The ledger schema captures the metadata-is-published + PDF-version-divergence rule.
- The executor template matches the loop-until-dry contract and cites the bundled client's command surface.

## Planner Guidance

Compose, do not restate: point to `zotero-paper-reader`, `mistral-pdf-to-markdown`, `writing`, and the `citation-metadata-client` command surface rather than paraphrasing them. Keep `SKILL.md` concise and procedural; every discipline detail belongs in a `skill-references` file. Load `skill-creator` before editing.

## Results

Authored [`skills/literature-review/SKILL.md`](../../../skills/literature-review/SKILL.md) (100 lines, markdown self-check clean). It is the concise, procedural core; all discipline detail is routed by pointer to the `skill-references` files and the bundled client's command surface.

**Frontmatter trigger.** A pushy `description` covering "literature review / survey / related-work / reading list for an econ/finance area" and the assemble-many-papers intent even when the phrase "literature review" is absent, with an explicit negative boundary against single-paper reads (routes those to `zotero-paper-reader`). `user-invocable: true`, matching the domain-skill convention.

**Body — execution shape only, depth routed out:**
- **`## References`** table routes the four `skill-references` files by name and load condition — [`references/search-and-screening.md`](../../../skills/literature-review/references/search-and-screening.md), [`references/econ-corpus.md`](../../../skills/literature-review/references/econ-corpus.md), [`references/grounding-and-extraction.md`](../../../skills/literature-review/references/grounding-and-extraction.md), [`references/synthesis-and-classification.md`](../../../skills/literature-review/references/synthesis-and-classification.md) — plus the already-authored [`references/citation-client.md`](../../../skills/literature-review/references/citation-client.md). These four names are the contract `skill-references` must author against.
- **`## Composed skills`** points to `zotero-paper-reader` (dedup / PDF fetch / BibTeX / the `add`-`attach` save path), `mistral-pdf-to-markdown` (shortlist OCR), and `writing` (prose) — by pointer, not restated.
- **`## Workflow`** — Part 1 interactive setup (the `AskUserQuestion` elicitation of scope, criteria + quality bar, extraction/classification schema, seed set, and Zotero add policy incl. library/collection → add-path selection); Part 2 the per-agent fan-out steps (verbatim metadata → screen-first → own-ledger-entry → return candidates).
- **`## Ledger schema`** — the per-paper entry (verbatim published-version metadata; `discovered_via`/`bfs_depth` provenance; decision + failing gate; PDF path + required version-divergence flag; researcher extraction fields), in both representations (subtree-as-ledger with `status`-as-frontier, and the standalone folder ledger).
- **`## Executor template`** — a loop-until-dry pseudocode block: `seen` dedup index, parallel per-round fan-out, cross-agent `citation_client dedup`, stop on a dry round, record the convergence judgment; with the `superimplement`-style subtree dispatch loop as the noted alternative.

**Validation criteria met:** trigger metadata explicit and standalone-legible; workflow runnable both standalone (folder ledger) and in a tree (subtree ledger); ledger schema carries the metadata-is-published + PDF-version-divergence rule; executor matches the loop-until-dry contract and cites the bundled client's subcommands. Composed skills are pointed to, never paraphrased; no cross-skill pattern citations or repo-internal contributor-doc references in the shipped prose.

Discovery-surface wiring (CATEGORIES / README / using-superra inventory + trigger test) is out of scope here — it belongs to the `discovery-wiring-and-tests` task.
