---
title: "Planning Sizing: Stop Over-Granular Trees"
status: approved
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

## Details

- The diagnosis attachment carries the causal lines with quotes and `file:line`, the missing counterweights, and the reasoning behind each proposed edit — read it before editing.
- `review-skill` also edits `planning-review.md` (severity vocabulary); the dependency edge serializes the shared file.
- The failure evidence pair for the validation replay: commit `f9ae6bf6` (8-task tree) vs `53eee481` (4-task consolidation).

## Results

All nine ranked edits from the [diagnosis](../attachments/diagnosis-overgranular-planning.md) §c landed across six files, plus three counterweights the diagnosis did not list. No numeric task-count cap was introduced — the objective forbids one, and the bidirectional self-review item carries the check instead.

**[task-tree-design.md](../../../skills/superplan/references/task-tree-design.md) gained the merge side of the split decision.** A new "do not split when" item: children editing the same files or reloading the same context are one task, however many concerns it serves. "Split when" is qualified to different artifacts, data sources, or domain skills. The right-sizing test gained its first cross-sibling clause — two siblings whose success criteria read as one sentence together are one task — and the cost floor is re-anchored off dispatch: a task's fixed cost is its contract, results record, verdict, and researcher reading time, paid in every execution mode.

**The self-review item is now bidirectional.** Item 9 in [build-and-review.md](../../../skills/superplan/references/build-and-review.md) prescribes merging siblings that share an edit surface or that one agent could write in one pass, not only splitting oversized ones. §Task Dependencies states the planning-side consequence — siblings sharing an edit surface are not a dependency case, they are a merge — which corrects the `depends_on`-instead-of-merge reflex the failure evidence showed. The no-checkbox rule names its second alternative: otherwise it is a bullet in the objective.

**Reviewers get the same test.** [planning-review.md](../../../skills/superplan/references/planning-review.md) enumerates split/merge sizing and states that a shared edit surface is a merge finding rather than a dependency finding. [thorough-planning.md](../../../skills/superplan/references/thorough-planning.md) adds the re-cut signal — three or more tasks modifying one file — and guards the exploration split as an evidence partition rather than a task partition.

**Two counterweights protect the new rule from its own side effects.** [consolidation.md](../../../skills/superplan/references/consolidation.md)'s detection bullet and Merge row broadened from "overlapping objectives or outputs" to include edit surfaces, so a consolidation pass reaches the merge action for tasks whose objectives differ but whose files do not. And the split-or-demote dichotomy gained a third branch — a one-edit-surface task carries a binding bullet per concern it serves — without which the line would push a correctly merged objective's binding bullets down into `## Details`.

**Validation is an instruction-level replay, not an executed one.** Against the failure evidence (`f9ae6bf6`'s 8-task tree, consolidated at `53eee481`), the tree is now caught at three independent points, two of them before the researcher sees it: self-review item 9 fails because four of the eight objectives name `superimplement`; the thorough §Critical Files threshold routes the same overlap to §Splitting Tasks instead of listing the file; and planning review's enumeration names the exact misdiagnosis the reviewer at `ba35ee55` made. The premise — three or more tasks on one file — is verified against the commit; the agent behavior under the new lines is argued, not measured.

### Notes

**One counterweight is deliberately unfixed.** The consolidation edits make merge reachable *within* a pass already entered; they do not change *when* it is entered, and `superplan` still routes new work away from consolidation. A freshly authored tree therefore never loads `consolidation.md`. The three in-band catches above cover the failure mode where a new tree already goes, so routing new trees into a debt-cleanup pass would duplicate the check on a second surface. Reopen only if the in-band catches prove insufficient in practice.
