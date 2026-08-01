# Diagnosis: Over-Granular Decomposition in the v0.4 Planning Session

Hand-authored from a read-only diagnostic agent dispatch, 2026-08-01. Evidence: the 8-task tree at commit `f9ae6bf6` vs the 4-task consolidation at `53eee481`. Line numbers refer to the `ec5a4897` baseline.

## Failure signature

The 8-task tree mapped almost 1:1 onto the *sections of the exploration attachments*, not onto edit surfaces — seven of eight tasks were keyed to a distinct evidence section (role-skills → map §1, review-policy → map §2, checklist-recalibration → map §3c, review-calibration → map §4, conversation-boundary → writing map §5, …). The planner inherited the evidence partition as the task partition. The DAG did not repay the split: a 4-deep serial chain carried 8 tasks vs 3-deep carrying 4, and three tasks rewrote `skills/superimplement/SKILL.md`.

## (a) Causal instruction lines, ranked

1. **`task-tree-design.md:52`** — "Different concerns, data sources, artifact families, or domain skills apply" sits in **Split when** as an unqualified trigger. "Concerns" is the one abstraction-keyed member of the list and dominates: every plan has more concerns than artifacts.
2. **`decomposition.md:60`** — Self-Review item 9 ("No task carries implicit sub-steps that should be separate subtasks") is the only granularity item and can only *increase* task count. The other coverage-style items (1, 3, 4, 7, 8) are all easier to satisfy with more, narrower tasks — the self-review is a monotone pump. The 8-task tree passed all nine items cleanly.
3. **`decomposition.md:29`** — the no-checkbox rule names exactly one alternative for multi-part work: promote to subtask. Nothing says a task's objective may legitimately carry several concerns as bullets (the consolidated tree's normal mode).
4. **`task-tree-design.md:63`** — the right-sizing test has two too-big clauses and one trivially-too-small clause, no too-many clause; the passing condition ("success criteria in one sentence") gets *easier* the narrower the task, and it is applied per-task, never across siblings.
5. **`task-tree-design.md:15`** — "When an objective outgrows a short paragraph plus its must-bullets, either the task needs splitting…" — for broad cross-cutting work the correct consolidated objectives (8–9 bullets) violate this line.
6. **`task-tree-design.md:51,53`** — "each child has a meaningful objective…and review verdict" is satisfied by the act of drafting; "could run in parallel" never asks whether they'd run in parallel *against the same file*.
7. **`planning-review.md:11,14`** — the reviewer's enumerations omit §Splitting Tasks entirely; every item is per-task and completeness-directional. The reviewer at `ba35ee55` saw the exact symptom (three tasks in superimplement, two in refactor-and-integrate) and prescribed a `depends_on` edge — over-splitting diagnosed as a coordination defect, for lack of merge vocabulary. `superplan/SKILL.md:80` also gives no rule for choosing handoff-readiness vs design-review; only design-review would plausibly have reached the split.
8. **`decomposition.md:35`** — the only execution-economics pointer names parallel dispatch (a reason for more tasks), and `agent-orchestration` — whose §Workload Balancing tier-2 example is literally "Three edits in the same skill file." — is not loaded until Phase 4.
9. **`task-tree-design.md:69`** — "depth over breadth: update existing tasks over creating new separate ones" governs only insertion into an existing tree; a fresh subtree's cut is unguarded.
10. **`thorough-planning.md`** — parallel exploration frames the session as concerns-in-parallel; §Exploration Synthesis never warns the exploration split is an evidence partition, not a task partition; §Critical Files (:69) instructs listing "files that multiple tasks will read or modify" — the planner enumerated the shared surface and treated it as a prioritization aid rather than a smell.

## (b) Missing counterweights

1. No shared-edit-surface test anywhere in superplan (the mirror image of `agent-orchestration:22`'s bundling trigger).
2. No merge test symmetric to the split tests — all three **Do not split when** items are about declining a contemplated split, none about collapsing drafted ones.
3. The right instrument exists but is unreachable: `consolidation.md:30` (pairwise relationship matrix) and `:39` ("overlapping objectives or outputs → Merge") trigger only on accumulated structural debt, never on a freshly authored tree — a stage-routing failure.
4. No per-task fixed-cost line stated positively (each task costs a contract + context-distillation walk + results + status + verdict + researcher reading time, however dispatched), and no whole-tree sum.
5. No task-count sanity check in Self-Review or planning review.
6. No "don't inherit the exploration partition" guard in thorough-planning.
7. No statement that an objective may carry several concerns as bullets (:15 says the opposite).
8. `changing-the-tree.md:39` names "merge" but routes to a section with no merge policy.

## (c) Proposed edits (minimal; first two suffice to prevent recurrence)

1. `task-tree-design.md` **Do not split when**, add: "The children would edit the same files or reload the same context — one edit surface is one task, however many concerns it serves."
2. `decomposition.md:60`, make item 9 bidirectional: "…no two siblings share an edit surface or would be written by one agent in one pass — merge those."
3. `task-tree-design.md:52`, qualify: "Different concerns landing in different artifacts…"
4. `task-tree-design.md:63`, append: "If two siblings' success criteria read naturally as one sentence together, they are one task."
5. `planning-review.md:14`, add "split/merge sizing (§Splitting Tasks)" to the enumeration; add a mode-selection rule at `superplan/SKILL.md:80` (design-review for newly authored trees).
6. `task-tree-design.md:58` + `consolidation.md:45`, re-anchor the cost floor off dispatch: "too small to justify its own contract, results record, and verdict."
7. `decomposition.md:29`, name the alternative: "…otherwise it is a bullet in the objective."
8. `thorough-planning.md:69`, add: "three or more tasks modifying one file is a signal to re-cut by edit surface before listing it."
9. `decomposition.md:35`, mention bundling alongside parallel dispatch.

Not recommended: a numeric task-count cap or a new self-review item (fails the Necessity gate; edit 2 already carries the check).

## (d) Instruction-caused vs model-default

Predominantly instruction-caused with a model-default tailwind: concern-shaped *thinking* is the model prior; the concern-shaped *task tree* is instruction-caused. The same session produced the correct edit-surface cut once prompted; two independent agents (planner, reviewer) holding the same instructions both reached for coordination fixes instead of a merge — the signature of a shared frame with no merge vocabulary. Every instruction gradient points toward more tasks, and the one anti-proliferation rule is scoped where it could not bind.

**Economics footnote.** Every sizing line prices tasks in dispatch+review units (`:48,:51,:53,:54,:58,:63`); under v0.4's interactive default there is no dispatch, so the only floor test evaluates to ~zero and the "do not split" side collapses. The cost that survives the flip — per-task contract, results, verdict, reading time, explicitly non-amortizable per `agent-orchestration:28` — is invisible to the planner. Granularity was never free; the planner had no line saying so, and the line it had priced the wrong thing.
