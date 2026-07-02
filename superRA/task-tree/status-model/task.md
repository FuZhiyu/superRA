---
title: "Task status model"
status: approved
depends_on:
  - agent-interface
---

## Objective

Own the task-tree status model: the single `status` frontmatter field, lifecycle transitions, parked-state semantics, frontier and rollup behavior, CLI/dashboard rendering, documentation, migration, diagnostics, and regression tests.

The task tree uses one status field. Older `review_status` and `integration_status` fields are not part of the model. Workflow phase is inferred from the subtree's status distribution rather than stored separately, so any subtree can move through implementation, review, and integration using the same state machine.

## Results

The task tree uses a single `status` field across task files, CLI commands, dashboard rendering, workflow protocols, migration tooling, and diagnostics. The living owner of the status enum and lifecycle is `skills/task-tree/references/task-file-contract.md §Task Anatomy` (the file agents load); the notes below record the model this task settled.

- **Enum and lifecycle.** `not-started → in-progress → implemented → approved`, with `revise` for review fix rounds, plus `archived` and `postponed` as orchestrator/researcher scope decisions. Transition ownership: the implementer drives up to `implemented` (and `revise → implemented`); the reviewer drives `implemented → approved`, `implemented → revise`, and `approved → revise` at integration; the orchestrator drives `approved → not-started` on scope invalidation and `any → archived/postponed`. Integration reuses the same state machine — no separate field.
- **Parked states.** `archived` and `postponed` are excluded from both `compute_status()` and `compute_frontier()`. The key distinction: an `archived` dependency is treated as satisfied (the work is out of scope, so dependents proceed), while a `postponed` dependency blocks its dependents until resumed (set back to `not-started`, `--cascade` for a subtree).
- **Rollup and frontier.** Branch status is computed from children at read time via `effective_status()` (stored branch status is advisory, not enforced); a leaf is dispatchable when it is `not-started`/`in-progress`, all its sibling deps are `approved` (or `archived`), and every ancestor's deps are recursively met.
- **`--cascade`.** Allowed for `approved` / `not-started` / `archived` / `postponed` (clear recursive semantics); rejected for `in-progress` / `implemented` / `revise`. Archived descendants are skipped unless the cascade value is itself `archived`, so a cascade never silently unarchives.
- **Diagnostics.** `task_check.py` is a read-only diagnostic (no auto-fix) with status-validity, dependency-integrity, and rollup-consistency checks; it validates enum membership and cascade allow-lists but does not flag skipped transitions (transition ordering is a human protocol, not a machine constraint).
- **Migration.** `plan_migrate.py --upgrade-status` collapses legacy `(status, review_status, integration_status)` triples to the single `status` field.

`postponed` was folded into this status-model owner during consolidation; its core-semantics, rendering-surface, and documentation work is part of the model above.
