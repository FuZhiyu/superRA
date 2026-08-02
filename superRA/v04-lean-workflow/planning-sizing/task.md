---
title: "Planning Sizing: Stop Over-Granular Trees"
status: not-started
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
