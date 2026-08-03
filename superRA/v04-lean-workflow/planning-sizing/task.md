---
title: "Planning Sizing: Stop Over-Granular Trees"
status: implemented
depends_on: [review-skill]
---

## Objective

Fix the planning instructions that produce over-granular, concern-per-task trees, so planners cut tasks by edit surface and merge drafted splits.

- Apply the ranked edits in the [over-granularity diagnosis](../attachments/diagnosis-overgranular-planning.md) §c across the superplan references (`task-tree-design.md`, `decomposition.md`, `planning-review.md`, `thorough-planning.md`, `consolidation.md`, `superplan/SKILL.md`). The first two are mandatory: a shared-edit-surface rule under "Do not split when" (one edit surface is one task, however many concerns it serves) and a bidirectional granularity self-review item (merge siblings that share an edit surface or would be written by one agent in one pass); apply the rest unless implementation shows a better placement, and skip any the DRY/Necessity gate rejects.
- Re-anchor the sizing cost floor off dispatch: a task's fixed cost is its contract, results record, verdict, and researcher reading time, paid regardless of execution mode.
- Give the planning reviewer the split/merge vocabulary and a mode-selection rule (design-review for newly authored trees).
- Guard the thorough-depth pipeline: exploration/evidence partitions are not task partitions; multiple tasks modifying one critical file is a re-cut signal, not just a listing.
- No numeric task-count caps.
- Validation: replaying this plan's own inputs against the updated instructions would flag the 8-task tree (three tasks editing one file) at self-review or planning review.

## Planner Guidance

- The diagnosis attachment carries the causal lines with quotes and `file:line`, the missing counterweights, and the reasoning behind each proposed edit — read it before editing.
- `review-skill` also edits `planning-review.md` (severity vocabulary); the dependency edge serializes the shared file.
- The failure evidence pair for the validation replay: commit `f9ae6bf6` (8-task tree) vs `53eee481` (4-task consolidation).

## Results

All nine ranked edits from the diagnosis §c are applied, plus the two guards the objective names beyond §c (exploration-partition warning, reviewer merge vocabulary). Net +14/-13 lines across six files; no line was added that fails the DRY/Necessity gate, and no numeric task-count cap was introduced.

### Edits by file

| Diagnosis §c | Landed at | Change |
|---|---|---|
| 1 (mandatory) | [task-tree-design.md:62](../../../skills/superplan/references/task-tree-design.md#L62) | New **Do not split when** item: children editing the same files or reloading the same context are one task, however many concerns it serves. |
| 2 (mandatory) | [decomposition.md:60](../../../skills/superplan/references/decomposition.md#L60) | Self-Review item 9 retitled "Granularity, both directions" and made bidirectional — merge siblings sharing an edit surface or writable by one agent in one pass. |
| 3 | [task-tree-design.md:54](../../../skills/superplan/references/task-tree-design.md#L54) | **Split when** qualified to "Different concerns land in different artifacts, or different data sources or domain skills apply." Dropped the now-redundant "artifact families". |
| 4 | [task-tree-design.md:66](../../../skills/superplan/references/task-tree-design.md#L66) | Right-sizing test gains its first cross-sibling clause: two siblings whose success criteria read as one sentence together are one task. |
| 5 | [planning-review.md:12](../../../skills/superplan/references/planning-review.md#L12), [superplan/SKILL.md:81](../../../skills/superplan/SKILL.md#L81) | Reviewer enumeration gains "split/merge sizing (§Splitting Tasks)" plus the corrective for the observed failure — siblings sharing an edit surface are a merge finding, not a `depends_on` finding. Mode-selection rule: design-review for a newly authored tree, handoff-readiness once the design is settled. |
| 6 | [task-tree-design.md:60](../../../skills/superplan/references/task-tree-design.md#L60), [consolidation.md:47](../../../skills/superplan/references/consolidation.md#L47) | Cost floor re-anchored off dispatch: "its own contract, results record, verdict, and researcher reading time — a fixed cost paid in every execution mode." Section lead and the two consolidation table rows shifted from "independent dispatch and review" / "dispatch cost" to execution-mode-neutral wording. |
| 7 | [decomposition.md:31](../../../skills/superplan/references/decomposition.md#L31) | No-checkbox rule names the second alternative: "otherwise it is a bullet in the objective." |
| 8 | [thorough-planning.md:69](../../../skills/superplan/references/thorough-planning.md#L69) | Critical-files criterion gains the re-cut signal: three or more tasks modifying one file means re-cut by edit surface before listing it. |
| 9 | [decomposition.md:37](../../../skills/superplan/references/decomposition.md#L37) | Execution-economics pointer now names both directions: "independent branches for parallel dispatch, same-surface work for bundling." |
| — (objective bullet 4) | [thorough-planning.md:28](../../../skills/superplan/references/thorough-planning.md#L28) | Exploration Synthesis states the guard: the exploration split is an evidence partition, not a task partition — cut by edit surface, not by which agent or report section found a thing. |
| — (objective bullet 3) | [consolidation.md:47](../../../skills/superplan/references/consolidation.md#L47) | Merge row also triggers on "sharing an edit surface with a sibling", so the retroactive instrument fires on a freshly authored tree, not only on accumulated debt. |

### Skipped

- **Diagnosis (a)5** ([task-tree-design.md:17](../../../skills/superplan/references/task-tree-design.md#L17), "An objective outgrowing a short paragraph plus its must-bullets: either the task needs splitting…"), which counterweight (b)7 wants softened so an objective may carry several concerns as bullets. Not in the §c ranked list, and it fails DRY: the line already routes to §Splitting Tasks, which now carries the shared-edit-surface rule as the answer. Adding a second statement of that rule here would be the paraphrase the gate forbids.
- **A numeric task-count check in Self-Review or planning review** — the objective forbids caps and the diagnosis flags it as a Necessity failure; edit 2 carries the check.

### Validation replay

Replaying the failure evidence (`f9ae6bf6` 8-task tree vs `53eee481` 4-task consolidation) against the updated instructions, the tree is caught at three independent points, at least two of them before the user ever sees it:

1. **Self-Review item 9** — four of the eight tasks (`review-policy`, `mode-default`, `conversation-boundary`, `review-calibration`) name `superimplement` in their objectives, `review-policy` naming `skills/superimplement/SKILL.md` outright. The bidirectional item now fails on "no two siblings share an edit surface" and prescribes merge. Verified by grepping the objectives at `f9ae6bf6`.
2. **Thorough §Critical Files** — the same four-task overlap exceeds the three-task re-cut threshold, and the instruction now routes to §Splitting Tasks instead of listing the file as a prioritization aid. This was the exact step where the original planner enumerated the shared surface and moved on.
3. **Planning review** — the reviewer at `ba35ee55` saw the symptom and prescribed a `depends_on` edge. The enumeration now includes split/merge sizing and states that a shared edit surface is a merge finding rather than a dependency finding, which is the specific misdiagnosis that occurred.

Caveat: this is an instruction-level trace, not an executed replay — there is no harness test that re-runs a planning session against a prior evidence set. The replay's premise (three-plus tasks on one file) is verified against the commit; the agent behavior under the new lines is argued, not measured.
