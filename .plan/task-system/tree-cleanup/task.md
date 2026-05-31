---
title: "Task tree consolidation"
status: approved
depends_on: []
tags: []
created: 2026-05-26
updated: 2026-05-30
---

## Objective

Proactive consolidation sweep over the current task tree to clear accumulated structural debt. The tree has grown through multi-session interactive work (the `live-server` subtree, the now-complete `status-consolidation` workstream, and the newly added `dynamic-workflows` workstream), and `task_check.py` currently reports 16 errors + 11 warnings. Run the survey-classify-propose-execute protocol in [`skills/superplan/references/consolidation.md`](skills/superplan/references/consolidation.md). The concrete debt as of this rewrite:

**1. Fix dependency-resolution errors (16).** Every `depends_on` in the `live-server` subtree uses a `../`-prefixed path, which violates the sibling-only constraint and resolves to nothing. Strip the `../` prefix so each entry names a bare direct-sibling directory — every one resolves once stripped (e.g. `cli-entry: ../server → server`; `tests: ../server, ../templates, ../live-reload, ../cli-entry, ../comments`; `comments/agent-cli` and `comments/comment-ui: ../sidecar-format → sidecar-format`). Fix `live-server`'s own malformed bare `depends_on: ../` — `live-server` is a child of `dashboard`, so replace with the correct sibling dependency or remove it if there was no real dependency.

**2. Collapse completed bug-fix tasks into one-line records.** A completed task whose entire scope was a single bug fix does not warrant a standalone task directory — collapse it into a one-line entry in the parent `live-server` task's `## Results` (a "Fixes" log: one line per fix with a commit ref), then delete its directory. Git history preserves the full detail. Apply to these approved fix-only children of `live-server`: `comment-badge-walkup-fix`, `math-template-escaping`, `rebuild-discovers-children`, `relative-path-resolution`, `section-rendering-fixes`, `status-consistency`, `root-task-rendering`. **Keep** the component subtasks as standalone tasks: `server`, `templates`, `live-reload`, `cli-entry`, `comments`, `math-rendering`, `deterministic-port`, `status-rollup-propagation`, `state-preservation`, `tests`. Before deleting each collapsed directory, carry its one-line summary + commit ref into the live-server Fixes log and repoint any sibling `depends_on` that referenced it.

**3. Remove stale status fields.** `review_status` and `integration_status` still linger in the `state-preservation` subtree — `state-preservation` and its three children `capture-restore`, `structural-reload`, `tests` — residue the `status-consolidation` migration missed. The single-`status` model is authoritative; delete both fields from these four tasks' frontmatter. (This task's own stale fields were removed in this rewrite.)

**4. Reconcile stored vs computed status.** `task_check.py` flags `migration` storing `status: approved` while its child rolls up to `not-started`. Also investigate `section-expand-uncap` (status `not-started`, but commit `4372f68` "impl: uncap task/section height after expand" suggests it was implemented and the status was never flipped). Recompute and persist correct branch statuses tree-wide so every stored parent status matches `compute_status()`.

**5. Flatten redundant nesting.** `migration` is a single-child parent (`deprecate-planmd-refs`) that adds no context beyond its child. Absorb the child into the parent, or leave it if `migration` is intended as a grouping for future migration tasks — orchestrator's call at survey time.

**Scope note.** The survey must cover the full current tree. The newly added `dynamic-workflows` workstream (4 tasks) has clean linear `depends_on` and needs no consolidation. The completed `status-consolidation` subtree's only residue is the stale fields in item 3.

## Validation

- `task_check.py --plan-root .plan` returns 0 errors and 0 stale-field / rollup warnings.
- No `depends_on` entry anywhere in the tree contains `../`.
- No standalone task directory whose sole content is one completed bug fix; each such fix is a one-line entry in the `live-server` Fixes log.
- All component subtasks and their `## Results` records are preserved intact.

## Results

Executed in commit `501e43f`. `task_check.py --plan-root .plan`: 25 issues → **0** (verification gate passed).

- **Dependency errors (16 → 0).** Stripped the `../` prefix from every `depends_on` in the `live-server` subtree (`comments`, `comments/comment-ui`, `comments/agent-cli`, `live-reload`, `templates`, `cli-entry`, `tests`); all now name bare direct siblings. Removed `live-server`'s malformed bare `../` (set `depends_on: []` — it had no real dependency).
- **Collapsed 8 single-fix tasks** into a `### Fixes` log in `live-server`'s `## Results`, one line + commit ref each, then deleted their directories: `section-rendering-fixes`, `math-template-escaping`, `comment-badge-walkup-fix`, `relative-path-resolution`, `rebuild-discovers-children`, `status-consistency`, `root-task-rendering`, and the placeholder `section-expand-uncap` (whose fix had shipped in `4372f68` but was never written up). Repointed `status-rollup-propagation` off its now-deleted `status-consistency` dependency. Component subtasks (`server`, `templates`, `live-reload`, `cli-entry`, `comments`, `math-rendering`, `deterministic-port`, `status-rollup-propagation`, `state-preservation`, `tests`) preserved with their results intact.
- **Stale fields removed** from the `state-preservation` subtree (`state-preservation` + `capture-restore`, `structural-reload`, `tests`) — residual `review_status`/`integration_status` the `status-consolidation` migration missed. Left `status` as-is (no auto-promotion); the `implemented` children correctly roll up to an `in-progress` parent.
- **Restructure (revised from "flatten").** Survey found `migration` is a substantive *completed* task, not a hollow single-child parent — its child `deprecate-planmd-refs` was independent not-started work wrongly nested under it. Promoted `deprecate-planmd-refs` to a `task-system` sibling, leaving `migration` a consistent childless leaf and clearing the rollup mismatch.
- **Scope confirmed clean:** the newly added `dynamic-workflows` workstream needed no consolidation.
