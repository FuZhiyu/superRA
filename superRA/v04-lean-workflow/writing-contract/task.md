---
title: "Concise Writing Contract for Task Files"
status: not-started
depends_on: [role-skills]
---

## Objective

Establish the concise-writing contract for task files: a selection step before writing, economy principles in the always-loaded style skill, and one home per fact across the tree.

- Teach principles, not rule catalogs: the contract is a small set of principles with a paired example or two, written in the register it prescribes, placed where agents already are at write time — not an enumerated rulebook. Agents apply the principle to cases the examples don't cover.
- Write-time DRY: a fact's home is decided when the output is produced. When the task's deliverable is itself an artifact (a written document, a code change), that artifact is the record — `## Results` points to it (file link, commit) with at most a high-level summary; it never restates the document's content or the diff. This generalizes the existing maturation-time trim-to-pointer disposition to write time.

- `report-in-markdown` gains a content-economy section applying to all markdown agents write: lead with the outcome; keep output short by selecting what to include, not by compressing prose (full sentences, no fragments, no invented abbreviations, no arrow chains); state each fact once; plain words, short sentences, consistent terminology defined at first use; structural budgets (bullets/lines) over word counts; one paired bad/good results example.
- Pre-writing selection step for `## Results`: before touching the file, decide who reads it, what they'll do next, and which few facts change that — everything else is omitted, not summarized. Frame as a decision, not written justification.
- `task-file-contract.md` §Results Shape: operationalize "terse" with an inclusion test mirroring the objective test (a line belongs in `## Results` only if a future reader needs it to use, reproduce, or trust the result) and an exclusion list (process telemetry, per-round logs, restated objective/parent content, numbers already in a child or sibling, verification detail beyond a one-liner); demote the five-slot template to an omit-by-default menu.
- Rebalance "self-contained account" (`using-superra` §Task Interface) with point-over-copy: self-contained through self-orienting pointers, not restatement; parents link to child findings rather than copying numbers up.
- End stage accretion: the final-diff-self-check trail (`refactor-and-integrate`) moves to the commit body; Protect decisions are not re-narrated into `## Results` (the protect commit already records them).
- No decision ledgers: a researcher decision enters the task file by rewriting the owning objective or constraint to its current state — never as a dated "decisions" section or "per user decision <date>" note (the date belongs in git). Add dated decision-log sections to the stale-content classes in `task-file-contract.md`, and sweep the few instruction files that model the pattern (e.g. `writing/references/consistency/numerical.md:5`).
- Role skills: implement self-check gains a results-economy item symmetric to the existing thin-results gate; the results-writing review focus (`review-calibration`) enforces this contract.
- Validation: the contract lives in one home per rule (economy in `report-in-markdown`, results shape in `task-file-contract.md`, role duties in role skills) with pointers, no restatement.

## Planner Guidance

- Ranked diagnosis of what makes current task files long, with `file:line` evidence and live examples (the showcase's triple-written result, stage-accreted leaves, four-way duplicated test counts): [writing-surfaces map](../attachments/map-writing-surfaces.md).
- Candidate rule set (16 rules) and compliance mechanics (short contracts beat catalogs on Fable-class models; paired examples are the highest-leverage device; file verbosity needs explicit targeting separate from chat verbosity; an anti-compression guardrail is as necessary as the anti-verbosity rule): [concise-writing research](../attachments/research-concise-writing.md) §C–D.
- The objective-side economy discipline to mirror (rejection test, overflow valve, point-over-copy ladder) already exists at `task-tree-design.md` §Writing Objectives and §Context Distillation — cite it, don't re-derive it. Add the missing trim counterpart to its §Objective rewrites on scope expansion.
- Placement question the researcher cares about: teach the principle where and when it's naturally loaded. `report-in-markdown` is the only always-loaded writing surface, so the principle lives there; role skills carry only the one-line self-check hook; the maturation menu's trim-to-pointer text becomes a pointer to the write-time principle rather than a second statement of it.
- Showcase/docs exemplar rewrite is explicitly out of v0.4 scope; do not touch `superRA/showcase-analysis/` or `docs/site` beyond statements your edits invalidate.

## Results
