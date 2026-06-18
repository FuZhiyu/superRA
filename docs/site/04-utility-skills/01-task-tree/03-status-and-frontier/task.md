---
title: "Status and the Frontier"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

Status and the frontier are both computed from the tree. When you ask the agent to plan, implement, and review, the picture updates on its own — you read it, you do not maintain it.

A leaf task moves through the implement-review cycle, and the agent drives every step:

```
not-started → in-progress → implemented → approved
                                        ↘ revise → implemented → approved
```

The two statuses that are yours to set are scope decisions: tell the agent to drop a task and it becomes `archived` (treated as resolved so dependents can proceed); tell it to park a task and it becomes `postponed` (blocks its dependents until you reset it to `not-started`).

| Status | What it means for you |
|---|---|
| `not-started` | Waiting to be dispatched. |
| `in-progress` | An implementer is on it. |
| `implemented` | Done by the implementer; awaiting review. |
| `revise` | A reviewer sent it back with findings. |
| `approved` | Signed off. |
| `archived` | You dropped it from scope. |
| `postponed` | You parked it. |

A branch task never carries a status you set — it is **rolled up** from its children: `approved` once all active children are, `revise` if any child needs revision, `in-progress` while work is underway or partially approved, `not-started` otherwise. Parked (`archived`/`postponed`) children are excluded. One leaf flips and every ancestor updates.

The **frontier** is what to work on next: the leaf tasks ready to dispatch right now — `not-started` (or an interrupted `in-progress`) with every `depends_on` sibling already `approved`. Ask "what's ready next?" and the agent reads the frontier; as tasks reach `approved`, the work they blocked enters it.

The authoritative contract — transition ownership, the exact rollup algorithm, and edge cases — lives in [skills/task-tree/references/task-file-contract.md](skills/task-tree/references/task-file-contract.md).

### Commands, to inspect or repair the tree yourself

The agent runs these under the hood; run them yourself to look at the frontier or fix stored statuses directly:

```bash
./superRA/superra task frontier      # leaf tasks ready to dispatch now
./superRA/superra task status fix    # recompute rollups from the leaves
```

Run `status fix` when bulk edits or direct file changes have left the stored rollups out of sync with the leaf statuses.
