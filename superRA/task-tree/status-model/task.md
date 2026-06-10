---
title: "Task status model"
status: in-progress
depends_on:
  - agent-interface
tags:
  - status
  - simplification
created: 2026-05-26
---

## Objective

Own the task-tree status model: the single `status` frontmatter field, lifecycle transitions, parked-state semantics, frontier and rollup behavior, CLI/dashboard rendering, documentation, migration, diagnostics, and regression tests.

The task tree uses one status field. Older `review_status` and `integration_status` fields are not part of the model. Workflow phase is inferred from the subtree's status distribution rather than stored separately, so any subtree can move through implementation, review, and integration using the same state machine.

## Design Spec

Design-time record for the task status model. The living owner of the status enum and lifecycle is [`task-file-contract.md`](../../../skills/task-tree/references/task-file-contract.md) §Field-by-Field Notes, per `CLAUDE.md` §Ownership Boundaries; that file is what agents load. This spec records the design decisions made here and is the authoritative reference for the subtasks that implemented those decisions.

### Field Definition

Single `status` field in task frontmatter. Replaces the previous `status` + `review_status` + `integration_status` triple.

```yaml
status: not-started   # not-started | in-progress | implemented | revise | approved | archived | postponed
```

No other status-like fields exist in frontmatter. `integration_status` and `review_status` are removed entirely.

### Status Semantics

| Status | Meaning | On frontier? | In rollup? |
|---|---|---|---|
| `not-started` | Planned, no work yet | Yes | Yes |
| `in-progress` | Being worked on | Yes | Yes |
| `implemented` | Code done, ready for review | No | Yes |
| `revise` | Review found blocking issues | No | Yes |
| `approved` | Review passed, task complete | No | Yes |
| `archived` | No longer relevant | No | **Excluded** |
| `postponed` | Deferred but may be resumed later | No | **Excluded** |

`archived` and `postponed` tasks are invisible to both `compute_status()` and `compute_frontier()`. A parent with 2 approved + 1 parked child computes as `approved`. An archived dependency is treated as satisfied and does not block dependents; a postponed dependency blocks dependents until resumed and approved.

### State Machine

```
                ┌──────────────────────────────┐
                │  any → archived / postponed   │  (orchestrator / user)
                └──────────────────────────────┘

not-started ──→ in-progress ──→ implemented ──→ approved
     │                               ↑    │
     │                               │    ↓
     │                               └─ revise
     │
     └──────────────────────── (orchestrator: scope invalidation)
                                approved → not-started
```

**Transition ownership:**

| Transition | Owner |
|---|---|
| `not-started → in-progress` | Implementer (starts work) |
| `in-progress → implemented` | Implementer (commits code, signals ready for review) |
| `implemented → approved` | Reviewer (no blocking findings) |
| `implemented → revise` | Reviewer (blocking findings) |
| `revise → implemented` | Implementer (fixes committed) |
| `approved → revise` | Reviewer during integration (integration review finds issues) |
| `approved → not-started` | Orchestrator (scope invalidation after plan change) |
| any → `archived` | Orchestrator or user (task no longer relevant) |
| any → `postponed` | Orchestrator or user (task deferred but not removed) |

Integration reuses the same state machine. When integration review surfaces issues in a previously approved task, it transitions `approved → revise`, the implementer fixes and sets `implemented`, the reviewer re-reviews. No separate field needed.

A postponed task is resumed by setting its status back to `not-started` (`--cascade` for a postponed subtree). Postpone is a deferral decision, not a dispatch verdict, and it does not preserve a prior in-progress or approved signal.

### Rollup Rules (`compute_status`)

For branch tasks (tasks with children), status is computed from children at read time via `effective_status()`. The stored `status` value in frontmatter may be stale for branch tasks.

Computation (after filtering out `archived` and `postponed` children), checked in this order:

1. No active children remain → `postponed` if any child is postponed, otherwise `archived`
2. All children `approved` → `approved`
3. Any child `revise` → `revise`
4. Any child `in-progress` or `implemented` → `in-progress`
5. Any child `approved` (but not all) → `in-progress`
6. Otherwise → `not-started`

Note: Rule 4 maps all-`implemented` children to `in-progress` at the branch level, so a subtree fully ready for review is not distinguishable from one still being worked without inspecting children directly. Phase inference (above) or direct subtree inspection provides the review-ready signal; this is the intended trade-off.

### Frontier Rules (`compute_frontier`)

A leaf task is on the frontier (dispatchable) when:
1. Its `status` is `not-started` or `in-progress`
2. All sibling dependencies have `effective_status()` == `approved` (or are `archived`; `postponed` does not satisfy a dependency)
3. All ancestor tasks' sibling dependencies are met recursively
4. It is not `archived` or `postponed`

### Parent Status: Computed, Not Enforced

`effective_status()` computes rollup at read time. The stored `status` in branch task frontmatter is advisory — it may be stale after child changes.

- **No write-time enforcement.** Setting `status` on a branch task is allowed but the value is overridden by computation at read time.
- **CLI warning.** `task_update.py` warns when setting status on a branch task without `--cascade`: "This task has children; stored status is overridden by computed rollup."
- **`task_check.py` reports mismatches** between stored and computed parent status as a diagnostic finding.

### `--cascade` Semantics

`task_update.py --status <value> --path <branch-task> --cascade` sets all descendant leaves to the given status.

- **Allowed values:** `approved`, `not-started`, `archived`, `postponed` — these have clear recursive semantics.
- **Rejected values:** `in-progress`, `implemented`, `revise` — these are per-task states without meaningful recursive interpretation. CLI errors on `--cascade` with these values.
- **Archived descendants are skipped** unless the cascade value is itself `archived`. This prevents `--cascade not-started`, `--cascade postponed`, or `--cascade approved` from silently unarchiving tasks.

### Migration Mapping

For converting existing `(status, review_status, integration_status)` triples to the single `status`:

1. If `integration_status` is set and non-`~` → use `integration_status` as `status` (most recent lifecycle event)
2. Else if `review_status` is set and non-`~` → use `review_status` as `status`
3. Else → keep existing `status` value

In all cases: `approved` → `approved`, `revise` → `revise`, `implemented` → `implemented`.

### Phase Inference

Workflow phase is inferred from the subtree's status distribution, not stored. Orchestrators and readers can apply this pattern to any subtree. Checked in this order:

1. All non-archived and non-postponed leaves `approved` → ready for integration or done
2. Any leaf `not-started` or `in-progress` → implementation phase
3. Otherwise (mix of `approved`, `implemented`, `revise` with no `not-started`/`in-progress`) → review phase

No `## Workflow Status` section in task files. Phase is inferred by orchestrators and readers from the status distribution; no tooling computes or displays phase automatically.

### Diagnostic Tool (`task_check.py`)

Read-only diagnostic, no auto-fix. Four checks (the `--category` filter takes `status`, `dependency`, `rollup`, `placement`):

1. **Status validity.** All `status` values in the valid enum. Flags stale `review_status` or `integration_status` fields still present.
2. **Dependency integrity.** All `depends_on` resolve to existing siblings. No cycles. Flags dependencies on archived and postponed tasks.
3. **Rollup consistency.** Stored parent status matches `compute_status()` from children. Reports mismatches.
4. **Placement.** Structural checks on task placement (e.g. tasks at unexpected depth or with unexpected directory structure).

Output: text (default) or `--json`. Exit code 0 if clean, 1 if issues found.

Transition ownership is enforced in prose only: `task_check.py` validates enum membership, cascade allow-lists, and rollup consistency, but does not flag skipped states (e.g. `not-started → approved` passes silently). This is the intended trade-off: transition ordering is a human protocol, not a machine constraint.

## Results

The task tree now uses a single `status` field across task files, CLI commands, dashboard rendering, workflow protocols, migration tooling, and diagnostics. The status lifecycle is `not-started` -> `in-progress` -> `implemented` -> `approved`, with `revise` for review fix rounds and orchestrator/researcher scope decisions for `archived` and `postponed`.

`postponed` was folded into this status-model owner during consolidation. Its implementation records are now the status-model subtasks for core semantics, rendering surfaces, and documentation: [11-postponed-core-semantics](11-postponed-core-semantics/task.md), [12-postponed-rendering-surfaces](12-postponed-rendering-surfaces/task.md), and [13-postponed-docs](13-postponed-docs/task.md). The key distinction is that `archived` satisfies dependents because the work is removed from scope, while `postponed` parks the work and blocks dependents until resumed.

## Review Notes

1. **MAJOR** — [task.md §Phase Inference](task.md) claims "No `## Workflow Status` section in task files. The dashboard computes and displays phase from tree state," but no phase computation exists anywhere in [plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py), [task_query.py](../../../skills/task-tree/scripts/task_query.py), or the templates (`grep -rn phase skills/task-tree/scripts/` returns nothing outside tests). No subtask owned it — [07-dashboard](07-dashboard/task.md)'s objective never mentions phase — and `## Results` does not flag the gap, so this approved root rolls up spec scope that was never delivered. Fix: implement phase display under a new task, or rewrite §Phase Inference to say phase is inferred by orchestrators/readers from the status distribution and record in `## Results` that no tooling computes it.
   → implemented: rewrote §Phase Inference last sentence to "Phase is inferred by orchestrators and readers from the status distribution; no tooling computes or displays phase automatically." No new task created — the spec accurately reflects current behavior.
2. **MINOR** — Dual self-declared authority: the Design Spec header says "Authoritative reference for the task status model," while [CLAUDE.md §Ownership Boundaries](../../../CLAUDE.md) assigns "status enum/lifecycle" to [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md), which restates the lifecycle without pointing here. The two copies have already drifted (the contract omits `approved → revise`; see [05-task-tree-docs](05-task-tree-docs/task.md) `## Review Notes`). Fix: demote this spec to a design-time record that names the living contract as authoritative, or make the contract point here.
   → implemented: demoted §Design Spec header to "Design-time record" with pointer to task-file-contract.md as the living owner ([task.md §Design Spec](task.md)).
3. **MINOR** — §Diagnostic Tool says "Three checks," but the live tool has a fourth `placement` category ([cli.py:479](../../../skills/task-tree/scripts/cli.py#L479)). Stale spec content; update the section or note that the spec describes the tool at design time only.
   → implemented: updated §Diagnostic Tool to list four checks with `--category` options, added `placement` as item 4 ([task.md §Diagnostic Tool](task.md)).
4. **MINOR** — §State Machine transition ownership is enforced nowhere in code: only enum membership ([_task_io.py:719](../../../skills/task-tree/scripts/_task_io.py#L719)), the cascade allow-list, and the branch-status warning are checked, so e.g. `not-started → approved` in one edit passes silently and `task_check.py` has no transition diagnostic. If prose-only enforcement is the intended trade-off, state it in the spec; otherwise add a warn-only hook or `task_check` category for skipped states.
   → implemented: added prose to §Diagnostic Tool stating transition ownership is enforced in prose only and naming this as the intended trade-off ([task.md §Diagnostic Tool](task.md)).
5. **MINOR** — Rollup rule 4 ([_task_io.py:587](../../../skills/task-tree/scripts/_task_io.py#L587)) maps all-`implemented` children to an `in-progress` parent, so a subtree fully ready for review is indistinguishable at branch level from one still being worked — and with item 1 unimplemented, no surface compensates. Consider an `implemented` rollup case or deliver the phase display.
   → implemented: added a note after the rollup rules acknowledging the all-implemented→in-progress trade-off and pointing to phase inference as the compensating signal ([task.md §Rollup Rules](task.md)).
