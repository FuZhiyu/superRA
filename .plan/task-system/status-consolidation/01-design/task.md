---
title: "Design the unified status model"
status: not-started
review_status: ~
integration_status: ~
depends_on: []
tags: [design]
script: ""
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Write a design spec for the consolidated status model as a section in the parent task's body. No code changes — this task produces the authoritative reference that all downstream tasks implement against.

The spec must cover:

1. **Field definitions.** Single `status` enum replacing `status` + `review_status` + `integration_status`. Document the valid values and their meanings.

2. **State machine.** Define allowed transitions and who owns each:
   - Implementer owns: `not-started → in-progress → implemented`, `revise → implemented`
   - Reviewer owns: `implemented → revise`, `implemented → approved`
   - Orchestrator owns: `approved → not-started` (scope invalidation)
   - Integration reuses the same cycle: when integration review surfaces issues, `approved → revise`, then the fix cycle runs again

3. **Migration mapping.** How to convert existing `(status, review_status, integration_status)` triples into the single `status`:
   - If `integration_status` is set and non-`~`, it takes highest precedence (it's the most recent lifecycle event)
   - Else if `review_status` is set and non-`~`, it takes precedence
   - Else keep existing `status` value
   - In all cases: `approved` → `approved`, `revise` → `revise`, `implemented` → `implemented`

4. **Phase inference.** Document how workflow phase is inferred from the subtree's status distribution (not stored):
   - Any leaf `not-started` or `in-progress` → implementation phase
   - All leaves `approved` → ready for integration or done
   - Recursive: works on any subtree, not just the root

5. **Integration as composable operation.** Document how the integration workflow accepts a scope (task path, subtree, or branch-wide) and reuses `status` for its revise cycle. Integration events are recorded in git history, not in task frontmatter.

6. **Removed artifacts.** `## Workflow Status` section no longer stored in task files. Dashboard infers and displays phase from tree state.

7. **Rollup and frontier.** Confirm `compute_status()` and `compute_frontier()` logic is unchanged — they already operate on `status` only.

## Results
