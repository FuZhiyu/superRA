---
title: "Design the unified status model"
status: implemented
review_status: revise
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

Design spec written in parent task's `## Design Spec` section. Covers all 9 items from the objective: field definition, status semantics table, state machine with transition ownership, rollup rules, frontier rules, parent-status computation policy, `--cascade` semantics, migration mapping, phase inference, and diagnostic tool spec.

## Review Notes

1. **[MAJOR] Phase inference rules are not exhaustive.** The [Phase Inference](../task.md#phase-inference) section defines three cases: (a) any leaf `not-started`/`in-progress` -> implementation, (b) all non-archived leaves `implemented`/`revise` -> review, (c) all non-archived leaves `approved` -> done. A subtree with a mix of `approved` and `implemented` leaves (no `not-started`/`in-progress`) falls through all three rules. Fix: either add a catch-all rule (e.g., "mix of `approved` and `implemented`/`revise` -> review"), or restructure as a priority cascade (check rule (a) first, then (c), then default to review).

2. **[MAJOR] All-children-archived edge case is unspecified in rollup rules.** The [Rollup Rules](../task.md#rollup-rules-compute_status) say "after filtering out `archived` children" but do not specify what happens when the filtered list is empty (i.e., all children are archived). The current code ([_task_io.py:423](../../../../../../skills/task-system/scripts/_task_io.py#L423)) falls back to `task.status` (the stored value) when `child_statuses` is empty. The spec's first rule ("All children `approved`") would be vacuously true for an empty list, producing `approved`, which contradicts the current behavior and may be surprising. Fix: add an explicit rule for empty-after-filtering, e.g., "If no non-archived children remain, return `archived`" or "return the stored `status`."

3. **[MINOR] `--cascade` behavior on already-archived descendants is unspecified.** The [--cascade Semantics](../task.md#--cascade-semantics) section says "sets all descendant leaves to the given status" but does not say whether `--cascade not-started` or `--cascade approved` should also change already-archived leaves. If it does, `--cascade not-started` would silently unarchive tasks, which is likely unintended. Suggest: document that `--cascade` skips archived descendants unless the cascade value is itself `archived`.

4. **[MINOR] Rollup rules should be explicitly ordered.** The [Rollup Rules](../task.md#rollup-rules-compute_status) present conditions as unordered bullets. Since multiple conditions can be true simultaneously (e.g., a parent with children [revise, in-progress] matches both "Any child `revise`" and "Any child `in-progress`"), the priority order matters. The current code checks them in the listed order, which is correct. Fix: number the rules or add "checked in this order" to make the priority cascade explicit for downstream implementers.
