---
title: "Review and Planning Protocol"
status: revise
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

### Integration Status

**PR #29 follow-up integration (in progress).** Confirmed `BASE_REF = better-handoff` (the PR #29 head branch). Anchors: `PRE_SYNC_BASE_SHA = 75a86ccebd0e...` (prior fork/sync point), `BASE_HEAD_SHA = 876178e32d22...` (current `better-handoff` HEAD). The incoming range `75a86cce..876178e3` carries the not-started plans for this exact work (`b36d563f`) plus a dynamic-workflows task move (`876178e3`); the plan overlap on `task-tree/cli-scripts/path-containment/task.md` resolves toward this branch's implemented superset. This integration pass covers two approved tasks: `review-planning-protocol/05-recursive-context-conventions` and `task-tree/cli-scripts/path-containment`. **Protect:** key behaviors (task_create escape rejection; task_read full-objective ancestor rendering) are guarded by the regression tests added in those tasks; full suite passes (210 task-tree + 6 sync-codex).

- Synced onto `better-handoff` at `75a86ccebd0ec37a0a9e904f0fd5b824752cf6f1` and preserved the incoming `superRA/` task-root rename.
- Moved `review-planning-protocol` task records under `superRA/` and later consolidated them under `task-tree/planning-redesign/review-planning-protocol`; active planning-review command references use `--plan-root superRA`.
- Accepted the integration review's DRY/Necessity findings: planning-review dispatch shape now lives in `agent-orchestration`, while `superplan` and its thorough-planning reference point to that owner; the reviewer role no longer describes planning-review dispatch fields.

**Final diff self-check:** `git diff 75a86ccebd0ec37a0a9e904f0fd5b824752cf6f1..HEAD`; surviving change classes are the approved review/planning protocol edits, optional `## Planner Guidance` support in task creation/tests, generated Codex/direct-mode role artifacts, and the `superRA/task-tree/planning-redesign/review-planning-protocol` task records. Suspicious hunks are justified as follows: instruction edits under `agents/*` and `skills/*` implement the approved objective/guidance contract, broad reviewer protocol, planning-review mode, and guidance-deviation rationale requirement; `skills/agent-orchestration/SKILL.md` owns the planning-review dispatch-shape exception after integration review; generated artifacts under `.codex/agents/` and `skills/using-superRA/references/direct-mode-*` were regenerated from canonical role specs; task-record additions under `superRA/task-tree/planning-redesign/review-planning-protocol/` preserve approved task evidence after the incoming task-root rename. No unrelated hunks identified.

## Review Notes

1. **[MAJOR]** [task.md](task.md) — `## Results` of this approved parent is an integration-status dev log that still reads "(in progress)", with sync SHAs and merge anchors, and contains no rollup of the six approved children's outcomes. Stage-1 debris left as the permanent record. Fix: replace with a Key Findings rollup linking child `## Results`; drop the stale integration log.
2. **[MAJOR]** Cross-skill contradiction at this protocol's edge: [superintegrate/SKILL.md:63](../../../../skills/superintegrate/SKILL.md#L63) (also lines 237, 245, 301, 324) instructs flipping checkboxes in "root task.md §Workflow Status", but [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md) — owner of body-section vocabulary — never defines `## Workflow Status`, and [superplan/SKILL.md:108](../../../../skills/superplan/SKILL.md#L108) rules "No checkboxes" in tasks. INTEGRATE depends on a section PLAN forbids creating. Fix: define `## Workflow Status` in the contract (root-task integration record, exempt from the no-checkbox rule) or replace the checkbox flips with another durable record.
3. **[MINOR]** Descendant Results (children 01, 04, 05, 06) cite the deleted `skills/task-tree/references/planning.md` as live markdown links; historical-provenance retention is documented only in `task-tree-design/01-reference-ownership`, not at these sites, and the dashboard renders them as dead links. Fix: annotate the citations as historical or repoint to the split owners ([task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md), [task-tree-design.md](../../../../skills/superplan/references/task-tree-design.md)).
