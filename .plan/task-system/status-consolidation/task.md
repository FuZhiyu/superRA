---
title: "Consolidate to a single status field"
status: not-started
review_status: revise
integration_status: ~
depends_on:
  - agent-interface
tags: [status, simplification]
script: ""
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Drop `review_status` and `integration_status` from task frontmatter. Merge both into the single `status` field. Today, implementers set both `status: implemented` and `review_status: implemented` on commit — two writes for one event. Frontier computation and rollup only consume `status`, so the other fields are tracked but never auto-consumed. This makes auto-computation fragile and the protocol confusing.

**Target state:** A single `status` field with a clear state machine:

```
not-started → in-progress → implemented → revise → approved
```

- **Implementer** owns transitions up to `implemented` (and `revise → implemented` on fix rounds).
- **Reviewer** owns `implemented → revise` and `implemented → approved`.
- **Workflow phase is inferred** from the subtree's status distribution, not stored.
- Frontier computation, rollup, and dashboard rendering all use `status` directly.

No `## Workflow Status` section in task files. Phase inference is recursive — any subtree is a self-contained workflow.

**Deferred:** Rearchitecting the integration workflow to be scope-flexible (single task, subtree, or branch-wide) and to reuse `status` for its revise cycle. Tracked separately under `agent-interface`. This task focuses on removing the redundant fields from the data model and updating all consumers.

**Scope:** task-system data layer, CLI scripts, SKILL.md, agent specs, workflow skills (implementation-workflow, agent-orchestration, planning-workflow), dashboard rendering, migration of existing `.plan/` trees, and tests.

## Review Notes

1. **[MAJOR] Task 01 vs task 10 contradiction on `task_check.py` scope.** [01-design/task.md](01-design/task.md) item 9 specifies `task_check.py` with both `--check` (read-only) and `--fix` (auto-repair) modes. [10-tree-diagnostics/task.md](10-tree-diagnostics/task.md) says "Read-only -- no auto-fix mode." The dispatch context also says "No auto-fix mode." The implementer of task 01 or task 10 will receive contradictory instructions. **Fix:** Decide which is authoritative and align both tasks. If read-only, remove the `--fix` mode from task 01's design spec item 9.

2. **[MAJOR] Task 06 omits `integration-workflow/SKILL.md`.** [06-protocol-updates/task.md](06-protocol-updates/task.md) lists agent specs, implementation-workflow, agent-orchestration, planning-workflow, using-superRA references, and writing references -- but not `skills/integration-workflow/SKILL.md`, which has 6+ references to `integration_status` (lines 47, 196-197, 206, 214, 220, 230, 356). Even though integration rearchitecture is deferred, removing the `integration_status` field requires updating these references to use `status` instead. **Fix:** Add `skills/integration-workflow/SKILL.md` to task 06's objective with the specific lines that reference `integration_status`.

3. **[MAJOR] `archived` status data-layer changes have no clear owner.** Adding `archived` to `VALID_STATUSES` and updating `compute_status()` / `compute_frontier()` to exclude archived tasks from rollup and frontier are data-layer changes in `_task_io.py`. [02-data-layer/task.md](02-data-layer/task.md) focuses exclusively on removing `review_status` and `integration_status` and does not mention adding `archived`. [03-cli-scripts/task.md](03-cli-scripts/task.md) mentions "archived tasks excluded from frontier computation" under `task_query.py`, but `compute_frontier()` lives in `_task_io.py`, not in `task_query.py`. **Fix:** Add archived-status implementation to task 02's objective: add `archived` to `VALID_STATUSES`, update `compute_status()` to filter out archived children, update `compute_frontier()` to skip archived tasks.

4. **[MAJOR] Task 07 (dashboard) contains a contradictory line.** [07-dashboard/task.md](07-dashboard/task.md) says "The `integration_status` display stays unchanged." This contradicts the parent task objective (dropping `integration_status` entirely). Verified: `plan_dashboard.py` has zero references to either `review_status` or `integration_status` -- there is no display to keep or remove. **Fix:** Remove the "integration_status display stays unchanged" line. The objective should state that the dashboard already uses only `effective_status()` / `status` and confirm no changes are needed for `integration_status` removal, then focus on any remaining `review_status` traces (which also appear to be zero in the dashboard code -- the task may be a no-op requiring only verification).

5. **[MINOR] Task 06 references specific line numbers in workflow skills.** Lines like "Step 2 line 93", "line 190", "line 162", "line 211" in [06-protocol-updates/task.md](06-protocol-updates/task.md) are brittle -- earlier tasks (02, 03, 04) may shift line numbers before task 06 executes. Not blocking since the implementer can grep, but the objective should reference section headings or content patterns rather than line numbers.

6. **[MINOR] Task 02 title/objective mismatch with full scope.** If finding 3 is accepted (adding `archived` to task 02), the title "Update core data layer to remove review_status and integration_status" should be broadened to reflect the addition of `archived`. -- note: dependent on finding 3 being accepted.

## Results
