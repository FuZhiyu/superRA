---
title: "Consolidate to a single status field"
status: in-progress
review_status: implemented
integration_status: ~
depends_on:
  - agent-interface
tags:
  - status
  - simplification
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


## Design Spec

Authoritative reference for the unified status model. All downstream tasks implement against this spec.

### Field Definition

Single `status` field in task frontmatter. Replaces the previous `status` + `review_status` + `integration_status` triple.

```yaml
status: not-started   # not-started | in-progress | implemented | revise | approved | archived
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

`archived` tasks are invisible to both `compute_status()` and `compute_frontier()`. A parent with 2 approved + 1 archived children computes as `approved`. An archived dependency is treated as satisfied — it does not block dependents.

### State Machine

```
                ┌──────────────────────────────┐
                │         any → archived        │  (orchestrator / user)
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

Integration reuses the same state machine. When integration review surfaces issues in a previously approved task, it transitions `approved → revise`, the implementer fixes and sets `implemented`, the reviewer re-reviews. No separate field needed.

### Rollup Rules (`compute_status`)

For branch tasks (tasks with children), status is computed from children at read time via `effective_status()`. The stored `status` value in frontmatter may be stale for branch tasks.

Computation (after filtering out `archived` children), checked in this order:

1. No non-archived children remain → `archived`
2. All children `approved` → `approved`
3. Any child `revise` → `revise`
4. Any child `in-progress` or `implemented` → `in-progress`
5. Any child `approved` (but not all) → `in-progress`
6. Otherwise → `not-started`

### Frontier Rules (`compute_frontier`)

A leaf task is on the frontier (dispatchable) when:
1. Its `status` is `not-started` or `in-progress`
2. All sibling dependencies have `effective_status()` == `approved` (or are `archived`)
3. All ancestor tasks' sibling dependencies are met recursively
4. It is not `archived`

### Parent Status: Computed, Not Enforced

`effective_status()` computes rollup at read time. The stored `status` in branch task frontmatter is advisory — it may be stale after child changes.

- **No write-time enforcement.** Setting `status` on a branch task is allowed but the value is overridden by computation at read time.
- **CLI warning.** `task_update.py` warns when setting status on a branch task without `--cascade`: "This task has children; stored status is overridden by computed rollup."
- **`task_check.py` reports mismatches** between stored and computed parent status as a diagnostic finding.

### `--cascade` Semantics

`task_update.py --status <value> --path <branch-task> --cascade` sets all descendant leaves to the given status.

- **Allowed values:** `approved`, `not-started`, `archived` — these have clear recursive semantics.
- **Rejected values:** `in-progress`, `implemented`, `revise` — these are per-task states without meaningful recursive interpretation. CLI errors on `--cascade` with these values.
- **Archived descendants are skipped** unless the cascade value is itself `archived`. This prevents `--cascade not-started` or `--cascade approved` from silently unarchiving tasks.

### Migration Mapping

For converting existing `(status, review_status, integration_status)` triples to the single `status`:

1. If `integration_status` is set and non-`~` → use `integration_status` as `status` (most recent lifecycle event)
2. Else if `review_status` is set and non-`~` → use `review_status` as `status`
3. Else → keep existing `status` value

In all cases: `approved` → `approved`, `revise` → `revise`, `implemented` → `implemented`.

### Phase Inference

Workflow phase is inferred from the subtree's status distribution, not stored. This works recursively on any subtree. Checked in this order:

1. All non-archived leaves `approved` → ready for integration or done
2. Any leaf `not-started` or `in-progress` → implementation phase
3. Otherwise (mix of `approved`, `implemented`, `revise` with no `not-started`/`in-progress`) → review phase

No `## Workflow Status` section in task files. The dashboard computes and displays phase from tree state.

### Diagnostic Tool (`task_check.py`)

Read-only diagnostic, no auto-fix. Three checks:

1. **Status validity.** All `status` values in the valid enum. Flags stale `review_status` or `integration_status` fields still present.
2. **Dependency integrity.** All `depends_on` resolve to existing siblings. No cycles. Flags dependencies on archived tasks.
3. **Rollup consistency.** Stored parent status matches `compute_status()` from children. Reports mismatches.

Output: text (default) or `--json`. Exit code 0 if clean, 1 if issues found.

## Results
