---
title: "Status and the Frontier"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

Status is how you see, at a glance, where every task sits — and the frontier is how you know what to work on next. Both are computed from the tree, so you read them rather than maintain them.

A leaf task moves through the implement-review cycle:

```
not-started → in-progress → implemented → approved
                                        ↘ revise → implemented → approved
```

You rarely set these by hand — the agents do, as they pick up, finish, and review work. An implementer takes a task to `implemented`; a reviewer sends it back to `revise` with findings or signs it off as `approved`. The two statuses that are yours to set are scope decisions: `archived` (dropped from scope, treated as resolved so dependents can proceed) and `postponed` (parked; blocks its dependents until you reset it to `not-started`).

| Status | What it means for you |
|---|---|
| `not-started` | Waiting to be dispatched. |
| `in-progress` | An implementer is on it. |
| `implemented` | Done by the implementer; awaiting review. |
| `revise` | A reviewer sent it back with findings. |
| `approved` | Signed off. |
| `archived` | You dropped it from scope. |
| `postponed` | You parked it. |

A branch task never carries a status you set — it is **rolled up** from its children: `approved` once all its active children are, `revise` if any child needs revision, `in-progress` while work is underway or partially approved, `not-started` otherwise. Parked (`archived`/`postponed`) children are excluded from the rollup. Flip one leaf and every ancestor updates on its own.

The **frontier** is the payoff: the set of leaf tasks ready to dispatch right now — `not-started` (or an interrupted `in-progress`) with every `depends_on` sibling already `approved`.

```bash
./superRA/superra task frontier
```

This is what you dispatch next. As tasks reach `approved`, the work they were blocking enters the frontier, so the list always reflects what can start now. If you have made bulk edits or touched files directly, `./superRA/superra task status fix` recomputes the stored rollups from the leaf statuses.

The authoritative contract — ownership of each transition, the exact rollup algorithm, and the all-parked edge cases — lives in [skills/task-tree/references/task-file-contract.md](skills/task-tree/references/task-file-contract.md).
