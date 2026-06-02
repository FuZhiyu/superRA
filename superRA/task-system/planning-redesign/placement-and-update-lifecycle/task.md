---
title: "Cross-Stage Placement + the Update-Task Lifecycle"
status: not-started
depends_on:
  - entry-and-placement
  - consolidation
tags: [planning-redesign, placement, consolidation, lifecycle]
created: 2026-06-01
---

## Objective

Close the design gap that let new improvement work be created as a misplaced standalone task instead of being folded into the task that owns its concern. Make "modify/merge the existing owner" the default and "create a new task" the justified exception, reframe placement as a cross-stage concern (not planning-only), and define the stage-dependent lifecycle of an *update task* so these transient improvement tasks are spun out cleanly during planning and merged back at integration.

This evolves the two approved siblings it depends on — `entry-and-placement` (Entry Assessment + §Placing Work) and `consolidation` (survey protocol + symptom list + integration routing hook) — rather than overwriting them. Per the very rule below, a big planning-stage update is spun out as a self-contained subtask now and merged into its targets at integration.

### The problem (observed 2026-06-01)

During a superintegrate dogfood, an improvement to the integration workflow was created as a **new root-level task** (`integrate-cleanup`) when it was actually an update to the existing `task-system/agent-interface/integ-workflow` task, which owns the integration-workflow SKILL and was thereby left stale. Two skill weaknesses allowed it:

1. **Placement is passive and CREATE is frictionless.** `§Placing Work in the Tree` Step 1 ("walk the tree, find the concern") produces no evidence, so a confident agent skips the walk and jumps to "Create sibling." "Prefer modifying existing task.md files over adding new tasks" exists only as a buried one-liner in `superplan §User Feedback`, far from the entry-assessment placement decision. The anti-pattern is named in prose but not gated.
2. **The consolidation gate/survey cannot see misplacement.** The "Task at the wrong level or under the wrong parent → Restructure" symptom is inherently *whole-tree*, but the survey protocol builds its relationship matrix "for each pair of tasks at the same level," and the new superintegrate consolidation gate reads as frontier-internal. So the gate that is supposed to be the backstop rubber-stamped the misplaced subtree as "clean-enough."

### Design

**1. Flip the burden of proof at placement (cross-stage).** Rewrite `task-system/references/planning.md §Placing Work in the Tree` so the presumption is MODIFY/MERGE the owning task, and creating a new task — especially a root-level one — requires recording which existing task's concern was read and why it does not cover the work. The justification cannot be written without doing the walk, which forces the read and surfaces the owner. Frame placement explicitly as a **cross-stage** concern that applies in planning, consolidation, and integration — not a planning-only step. (The researcher's note: "it's not only about planning.") Decide and state the framing: reframe the §Placing Work section as cross-stage in place, OR — if consolidation and integration need to load placement rules directly — extract it into a dedicated `task-system/references/placement.md` that planning, consolidation, and the integration gate all point to. Tradeoff: extraction gives clean cross-stage loading but adds a file + links to maintain; in-place reframe is less churn but leaves placement inside a planning-named reference. Recommend the option that lets the consolidation gate and superintegrate point at one placement owner.

**2. Define the update-task lifecycle (the core new rule).** An *update task* — a task whose purpose is to improve or modify an existing task or artifact — has a stage-dependent disposition driven by a real tradeoff:

- **Tradeoff.** Merging the change into the target task keeps one source of truth, but done *prematurely* (before the change is built and validated) it overwrites the target's nuance/history and conflates unsettled work with settled work. Spinning out a separate self-contained subtask preserves a clear, independently reviewable objective, but proliferates tasks that are harder to clean up later. Weigh by complexity, validation maturity, and reviewability.
- **Rule of thumb.**
  - **Planning stage (pre-implementation):** for a substantial update, CREATE a self-contained subtask under the owning concern. Give it a full, dispatchable objective. Do not merge into the target yet — premature merge loses nuance before the change even exists.
  - **Consolidation / Integration stage:** MERGE update tasks into the task they update — fold the matured result into the target/parent and remove the update-task directory. An update task should not survive integration as a standalone artifact. This is the create-then-merge lifecycle: spin out during planning/implementation, merge back at consolidation/integration.
- **Worked example (already applied).** The integration-workflow redesign was first created as a misplaced root-level `integrate-cleanup` task, then — applying this rule ahead of its codification — merged into `integ-workflow` at integration (its objective/Results refreshed to the shipped design, stale content dropped) and the standalone task removed (2026-06-01). Use this as the concrete example in the rule text: an update task does not survive integration as a separate tree.

**3. Make the consolidation survey + gate whole-tree for placement.** Fix `skills/superplan/references/consolidation.md` so the wrong-parent/Restructure check compares each task/subtree's concern against parents and other subtrees, not only same-level pairs; and fix the superintegrate Consolidation Gate so its placement/Restructure check is whole-tree, not frontier-internal. Tie the gate to the lifecycle rule: at the consolidation gate, update tasks present in the frontier are merge candidates by default. (The gate implementation is in `skills/superintegrate/SKILL.md`; its task record now lives in `integ-workflow` after the 2026-06-01 merge — land the whole-tree fix there.)

**4. Auditability net (optional, cheap).** Add one line to `superplan` Phase 4 / User Review surfacing the placement decision: for each new task — especially root-level — state the existing concern considered and why it does not cover the work. Keeps a human catch in the loop without enforcement machinery.

### Owners / files (point, do not paraphrase)

- `task-system/references/planning.md §Placing Work` (or extracted `placement.md`) — authoritative placement + burden-of-proof + cross-stage framing + the update-task lifecycle rule.
- `skills/superplan/references/consolidation.md` — survey whole-tree scope; merge-as-default for update tasks at consolidation.
- `skills/superintegrate/SKILL.md` Consolidation Gate — whole-tree placement check; update-task merge at integration (land in the surviving post-merge location).
- `skills/superplan/SKILL.md` Entry Assessment + User Review — point at the placement owner; add the placement-justification surface. Pointer, not paraphrase.

### Constraints

- Do not overwrite the approved `entry-and-placement` / `consolidation` tasks; this subtask evolves their output (it is itself an instance of the planning-stage "spin out a self-contained subtask" rule).
- Mechanisms over contingency trees; positive, behavior-shaping instructions; one source of truth per concern. Apply the CLAUDE.md DRY/Necessity gate line by line. `skill-creator` is unavailable in this environment — use the discipline encoded in root `CLAUDE.md` as the fallback.
- No new `Stage:` value (placement/consolidation/gate are orchestrator/reference concerns).

## Planner Guidance

Likely decomposes at implementation into ~3 self-contained subtasks — (a) placement burden-of-proof + cross-stage reframe, (b) the update-task lifecycle rule, (c) consolidation survey + gate whole-tree scope — but leave that decomposition to the implement/superplan pass rather than imposing it now. The lifecycle rule (b) is the load-bearing idea; (a) and (c) are the placement and backstop halves that make it stick.

## Results

_(Filled by implementer.)_
