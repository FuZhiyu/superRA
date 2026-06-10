---
title: "Review and Planning Protocol"
status: implemented
depends_on: []
tags: []
created: 2026-06-01
---

## Objective

Improve superRA's planning and review workflow so reviewers evaluate whether work genuinely achieves the task objective, using their general research judgment and the active domain discipline together, not only whether it passes an enumerated checklist. Add an explicit task-authoring split between the authoritative `## Objective` and advisory `## Planner Guidance`, and formalize optional planning review for thorough planning / handoff scenarios.

This work must preserve the repo's source-of-truth boundaries:
- canonical reviewer behavior lives in `agents/reviewer.md`;
- canonical implementer behavior lives in `agents/implementer.md`;
- task anatomy lives in `skills/task-tree/references/task-file-contract.md`; objective/guidance semantics live in `skills/superplan/references/task-tree-design.md`;
- superplan owns planning-phase choreography and optional planning review;
- generated Codex agents and direct-mode role references are regenerated, never hand-edited.

Success means a future implementer/reviewer pair can distinguish binding objectives from planner suggestions, reviewer approval reflects broad task-local judgment plus mandatory domain gates, and thorough planning can run a semantic planning-review pass without overloading implementation task statuses.

## Planner Guidance

Exploration from the design review identified three implementation slices:
- First update task anatomy so `## Objective` is the normative contract and optional `## Planner Guidance` holds non-binding starting points.
- Then update reviewer behavior so it reviews the objective, declared frontmatter outputs, implementer results, and the diff as a coherent whole, using the reviewer's own judgment and the active domain gates together.
- Finally add a `planning-review` reviewer mode owned by superplan, using task-local `## Review Notes` on the assigned planning target rather than normal task `status:`.

Avoid broad rewrites of domain skills. The domain skills own the specific gates; this work should only clarify how generic workflow/role protocols compose with those gates.

## Results

Six approved children shipped the review/planning protocol improvements:

- [01-objective-guidance-task-anatomy](01-objective-guidance-task-anatomy/task.md) — Added optional `## Planner Guidance` body section as advisory planner-owned context while keeping `## Objective` the authoritative contract ([task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md), [superplan/SKILL.md](../../../../skills/superplan/SKILL.md)).
- [02-objective-first-reviewer](02-objective-first-reviewer/task.md) — Revised canonical reviewer protocol to be task-local and objective-first: reviewers evaluate `## Objective`, scope frontmatter, `## Results`, git range, outputs, and active domain gates together ([agents/reviewer.md](../../../../agents/reviewer.md)).
- [03-planning-review-mode](03-planning-review-mode/task.md) — Added `Stage: planning-review` to the manifest; owned optional planning review in `superplan`/thorough-planning; moved dispatch-shape exception to `agent-orchestration`; regenerated reviewer artifacts ([using-superRA/SKILL.md](../../../../skills/using-superRA/SKILL.md), [superplan/SKILL.md](../../../../skills/superplan/SKILL.md), [agent-orchestration/SKILL.md](../../../../skills/agent-orchestration/SKILL.md)).
- [04-guidance-deviation-reporting](04-guidance-deviation-reporting/task.md) — Required material `## Planner Guidance` deviations to be recorded in `## Results`; deviation itself is not a failure but unexplained deviation is a MAJOR evidence gap ([agents/implementer.md](../../../../agents/implementer.md), [agents/reviewer.md](../../../../agents/reviewer.md)).
- [05-recursive-context-conventions](05-recursive-context-conventions/task.md) — Made `task_read.py` ancestor rendering full-objective; rewrote task anatomy as recursive; scoped domain planning references to the governing task; 384 tests pass.
- [06-context-section-and-tree](06-context-section-and-tree/task.md) — Renamed render header to `=== Context ===`; added focused tree showing spine + siblings + `▶ this task` marker; propagated "context" framing across skills/agents/roles.

## Review Notes

1. **[MAJOR]** [task.md](task.md) — `## Results` of this approved parent is an integration-status dev log that still reads "(in progress)", with sync SHAs and merge anchors, and contains no rollup of the six approved children's outcomes. Stage-1 debris left as the permanent record. Fix: replace with a Key Findings rollup linking child `## Results`; drop the stale integration log.
   → implemented: replaced stale integration dev log with selective rollup of six approved children's outcomes ([review-planning-protocol/task.md](task.md))
2. **[MAJOR]** Cross-skill contradiction at this protocol's edge: [superintegrate/SKILL.md:63](../../../../skills/superintegrate/SKILL.md#L63) (also lines 237, 245, 301, 324) instructs flipping checkboxes in "root task.md §Workflow Status", but [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md) — owner of body-section vocabulary — never defines `## Workflow Status`, and [superplan/SKILL.md:108](../../../../skills/superplan/SKILL.md#L108) rules "No checkboxes" in tasks. INTEGRATE depends on a section PLAN forbids creating. Fix: define `## Workflow Status` in the contract (root-task integration record, exempt from the no-checkbox rule) or replace the checkbox flips with another durable record.
   → implemented: defined `## Workflow Status` in [task-file-contract.md §Task Anatomy and §Field-by-Field Notes](../../../../skills/task-tree/references/task-file-contract.md) as root-task-only integration-phase progress record with the four superintegrate milestones, exempt from the no-checkbox rule
3. **[MINOR]** Descendant Results (children 01, 04, 05, 06) cite the deleted `skills/task-tree/references/planning.md` as live markdown links; historical-provenance retention is documented only in `task-tree-design/01-reference-ownership`, not at these sites, and the dashboard renders them as dead links. Fix: annotate the citations as historical or repoint to the split owners ([task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md), [task-tree-design.md](../../../../skills/superplan/references/task-tree-design.md)).
