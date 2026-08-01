---
title: "Reporting Contract: Concise Writing and the Conversation Boundary"
status: not-started
depends_on: [role-skills]
---

## Objective

Establish one reporting contract covering everything agents write — task files, documents, and conversation — built on selection before writing, one home per fact, and pointers across homes.

- Teach principles, not rule catalogs: a small principle set with a paired example or two, written in the register it prescribes, placed where agents already are at write time. Agents apply the principle to cases the examples don't cover.
- Core principles: decide before writing (who reads this, what they'll do next, which few facts change that — everything else is omitted, not summarized); lead with the outcome; short by selection, not compression (full sentences, no fragments, invented abbreviations, or arrow chains); state each fact once; plain words, consistent terminology; structural budgets over word counts.
- Write-time DRY: a fact's home is decided when the output is produced. When the deliverable is itself an artifact (a document, a code change), the artifact is the record — `## Results` points to it with at most a high-level summary, never restating its content or the diff. Generalizes the maturation-time trim-to-pointer disposition to write time.
- Conversation boundary: chat carries deltas and pointers — what changed at a high level plus the task-file/dashboard reference; content recorded in a task file is referenced, never reproduced. Extras the agent chose not to record go to conversation with an offer to add to `## Results` if the researcher wants them. Replace the unbounded `<summarize the results>` placeholder in `superimplement`; parent rollups link to child findings instead of restating their numbers.
- Results shape (`task-file-contract.md`): operationalize "terse" with an inclusion test mirroring the objective test (a line belongs in `## Results` only if a future reader needs it to use, reproduce, or trust the result); demote the five-slot template to an omit-by-default menu; rebalance the `using-superra` "self-contained account" line with point-over-copy (self-contained through self-orienting pointers, not restatement).
- End stage accretion: the final-diff-self-check trail (`refactor-and-integrate`) moves to the commit body; Protect decisions are not re-narrated into `## Results` (the protect commit records them).
- No decision ledgers: a researcher decision enters a task file by rewriting the owning objective or constraint to its current state — never as a dated "decisions" section or "per user decision <date>" note (the date belongs in git). Add dated decision logs to the stale-content classes in `task-file-contract.md`; sweep the instruction files that model the pattern (e.g. `writing/references/consistency/numerical.md:5`).
- Role skills carry only one-line hooks (a results-economy self-check item symmetric to the thin-results gate); the review skill's results-writing focus enforces this contract.
- Validation: each rule has one home with pointers elsewhere; no surviving instruction invites reproducing `## Results` in conversation or restating an artifact in `## Results`.

### Placement

One instruction home, one enforcement hook; `report-in-markdown` retires:

- **Craft and boundary → `using-superra`.** The reporting principles (how to write, for files and conversation alike) and the boundary rules (which home owns which fact) both land in the framework skill every agent already loads, next to §Task Interface's existing files-vs-commit-vs-return rules. The few conventions a checker cannot judge (file citations as clickable line anchors, figures under `attachments/`) come along as a short subsection.
- **Syntax → the hook.** Mechanical markdown rules (math renders, links resolve, figures exist, table syntax) move to the existing render-integrity hook — extend it where it falls short of what `report-in-markdown` teaches, keep it warn-only with error messages that carry the fix. Inventory each `report-in-markdown` rule as hook-checkable vs prose-worthy vs droppable; the always-loaded pair becomes a single always-loaded skill.
- Known limitation to note where relevant: the hook fires on task-tree edits, so standalone reports outside `superRA/` lean on the `using-superra` conventions alone.

## Planner Guidance

- Ranked diagnosis of what makes task files long, with `file:line` evidence and live examples: [writing-surfaces map](../attachments/map-writing-surfaces.md); candidate rules and compliance mechanics (short contracts beat catalogs; paired examples are the highest-leverage device; file verbosity needs targeting separate from chat verbosity; the anti-compression guardrail is as necessary as the anti-verbosity rule): [concise-writing research](../attachments/research-concise-writing.md) §C–D.
- The objective-side economy discipline to mirror (rejection test, overflow valve, point-over-copy ladder) exists at `task-tree-design.md` §Writing Objectives and §Context Distillation — cite it; add the missing trim counterpart to its §Objective rewrites on scope expansion.
- Showcase/docs exemplar rewrite is out of v0.4 scope; touch `docs/site` only where statements are invalidated.

## Results
