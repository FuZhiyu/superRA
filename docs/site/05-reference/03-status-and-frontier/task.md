---
title: "Status and Frontier"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

Every `task.md` carries a `status` field that tracks where the task sits in the implement-review cycle.
Parent task status rolls up automatically from children — a parent is `approved` only when all active children are `approved`.
The authoritative contract (ownership rules, rollup algorithm, `archived`/`postponed` exclusion logic) lives in [skills/task-tree/references/task-file-contract.md](skills/task-tree/references/task-file-contract.md).

## Status enum

| Status | Meaning |
|---|---|
| `not-started` | Waiting to be dispatched. |
| `in-progress` | An implementer is actively working on it. |
| `implemented` | Implementer has finished; ready for review. |
| `revise` | Reviewer returned it with findings; implementer must address them. |
| `approved` | Reviewer has signed off. |
| `archived` | Removed from scope; treated as resolved so dependents can proceed. |
| `postponed` | Parked; blocks its dependents until resumed (reset to `not-started` to resume). |

## Lifecycle

The normal path through the dispatch cycle is:

```
not-started → in-progress → implemented → approved
                                        ↘ revise → implemented → approved
```

Implementers own transitions up to `implemented` (and `revise → implemented` on fix rounds).
Reviewers own `implemented → revise`, `implemented → approved`, and `approved → revise` during integration when integration review surfaces issues in a previously approved task.
`archived` and `postponed` are scope decisions set by the orchestrator or researcher, not dispatch verdicts.

## The frontier

The **frontier** is the set of leaf tasks that are ready to dispatch right now — their status is `not-started` and all their `depends_on` siblings are `approved`.

```bash
./superRA/superra task frontier
```

The frontier is what the orchestrator dispatches next.
As tasks move to `approved`, their downstream dependents enter the frontier.

## Status rollup

A branch task's status is computed from its children:

- `approved` if all active (non-`archived`, non-`postponed`) children are `approved`.
- `in-progress` if any child is `in-progress`, `implemented`, or `revise`.
- `not-started` if all children are `not-started`.

Run `./superRA/superra task check --propagate-all` after bulk edits to recompute stored rollups.
