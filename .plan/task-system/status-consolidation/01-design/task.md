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

1. **Field definitions.** Single `status` enum replacing `status` + `review_status` + `integration_status`. Valid values: `not-started`, `in-progress`, `implemented`, `revise`, `approved`, `archived`.

2. **Status semantics and rollup behavior.**

   | Status | Meaning | On frontier? | In rollup? |
   |---|---|---|---|
   | `not-started` | Planned, no work yet | Yes | Yes |
   | `in-progress` | Being worked on | Yes | Yes |
   | `implemented` | Code done, ready for review | No | Yes |
   | `revise` | Review found issues | No | Yes |
   | `approved` | Done | No | Yes |
   | `archived` | No longer relevant | No | **Excluded** |

   Archived tasks are invisible to `compute_status()` and `compute_frontier()`. A parent with 2 approved + 1 archived children is `approved`. An archived task does not block dependents.

3. **State machine.** Define allowed transitions and who owns each:
   - Implementer owns: `not-started → in-progress → implemented`, `revise → implemented`
   - Reviewer owns: `implemented → revise`, `implemented → approved`
   - Orchestrator owns: `approved → not-started` (scope invalidation), any state → `archived`
   - Integration reuses the same cycle: when integration review surfaces issues, `approved → revise`, then the fix cycle runs again

4. **Parent status is computed, not stored authoritatively.** `effective_status()` computes rollup at read time. Stored parent status may be stale — `task_check.py` reports mismatches. CLI warns when manually setting status on a branch task without `--cascade`.

5. **`--cascade` semantics.** Only for `approved`, `not-started`, and `archived`. Sets all descendant leaves to the given status. Other values (`in-progress`, `implemented`, `revise`) don't have clear recursive semantics and are rejected with `--cascade`.

6. **Migration mapping.** How to convert existing `(status, review_status, integration_status)` triples into the single `status`:
   - If `integration_status` is set and non-`~`, it takes highest precedence
   - Else if `review_status` is set and non-`~`, it takes precedence
   - Else keep existing `status` value

7. **Phase inference.** Workflow phase is inferred from the subtree's status distribution (not stored):
   - Any leaf `not-started` or `in-progress` → implementation phase
   - All leaves `approved` (or `approved`/`archived`) → ready for integration or done
   - Recursive: works on any subtree

8. **Removed artifacts.** `review_status` field, `integration_status` field, `## Workflow Status` section — all removed from task files.

9. **Diagnostic tool.** `task_check.py` — read-only diagnostic (no auto-fix). Three checks: status validity, dependency integrity, rollup consistency. Reports issues; agents or humans decide what to fix.

## Results
