---
title: "Review and Planning Protocol"
status: approved
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
