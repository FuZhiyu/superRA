---
title: "Skill Core — SKILL.md, Workflow & Ledger/Executor"
status: not-started
depends_on: [citation-metadata-client]
---

## Objective

Author `skills/literature-review/SKILL.md` — frontmatter trigger metadata (explicit trigger conditions for discovery) plus a concise, procedural body that routes depth to the references owned by `skill-references`. The body owns the **execution shape**; discipline detail lives in references.

### The two-part workflow (the skill's core)
1. **Interactive setup (main agent).** Ask questions to settle: the research question/scope, the **inclusion/exclusion criteria + quality bar**, the **extraction/classification schema** (the per-paper fields and any classification axes), and the **seed set**. Then scaffold the ledger. This is an `AskUserQuestion`-driven elicitation, not a fixed template — the criteria and schema are the researcher's to define.
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
