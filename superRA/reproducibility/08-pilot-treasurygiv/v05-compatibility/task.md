---
title: "Validate the 0.5 Upgrade and Selective Rebuilds"
status: not-started
depends_on: []
---

## Objective

Verify the [0.5 contract](../../attachments/v05-design.md#verification-and-upgrade) on an isolated current TreasuryGIV project/worktree, including the heterogeneity reproduction pipeline when available. Record compatibility findings and land plugin defects in their owning implementation tasks.

- Audit the combined dependency graph before building. Repair genuine logical/declaration errors or task-boundary cycles explicitly, preserving true data dependencies, stable step IDs, declared outputs, and result meaning. Parent-owned steps do not need relocation simply because a task has children.
- Measure direct and transitive impact of representative edits to shared specifications/helpers. Refactor a bounded example by consumer/module or derived configuration artifact and verify selective rebuilding without changing results.
- Demonstrate exact-scope acceptance of an irrelevant edit, ordinary-build reuse as fresh, independent dirty descendants, later invalidation, revocation, and forced execution. Link the evidence supporting acceptance and the real-run records.
- Verify the live and offline task/step/mixed graph journeys on the repaired project; distinguish preserved historical approvals from new compatibility evidence. Keep research outputs sandboxed and do not alter the user's active worktree or published exhibits.

## Details

- Existing pilot evidence includes an inferred edge contradicting declared task order. The heterogeneity dashboard showed broad shared-code dependencies; its graph is a diagnostic fixture, not a constraint on the new contract.
- Use [worktree-data-sync](../../../../skills/worktree-data-sync/SKILL.md) before working with untracked data. Choose a current source worktree and an isolated destination through the project's own task tree; do not reuse the old pilot's worktree as an implicit writable target.
- Historical baseline: [parent results](../task.md#results). Validation is bounded to the changed behavior; BondElasticity adoption and file-open tracing remain postponed.
- Retained scripts, measurements, and screenshots belong in this task's attachments, with producer commands and reproduction coverage when they support results. Record project source/commit, machine/environment, and exercised runtime version.
