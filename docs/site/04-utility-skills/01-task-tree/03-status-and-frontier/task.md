---
title: "Status and the Frontier"
status: not-started
depends_on:  []
---

## Objective

Agents set each leaf task's status as they work; parent statuses and the frontier are computed from those. You mostly read them. You can set a leaf's status by editing its `task.md`, usually to drop or park it; a parent's status is recomputed and any hand edit is overwritten.

## A leaf task moves through implementation and review

```
not-started → in-progress → implemented → approved
                                        ↘ revise → implemented → approved
```

| Status | What it means for you |
|---|---|
| `not-started` | Waiting to be picked up. |
| `in-progress` | An implementer is on it. |
| `implemented` | Done; approval is still open — a review is running or deferred. |
| `revise` | A reviewer sent it back with findings. |
| `approved` | Signed off, by a reviewer or, when review is skipped, by the orchestrating agent after verifying the work. |
| `archived` | You dropped it: it leaves the active graph with its subtree, and downstream tasks get a warning. |
| `postponed` | You parked it: it blocks its dependents until you set it back to `not-started`. |

Say "drop this task" or "park this task" and the agent sets `archived` or `postponed`.

## A parent's status rolls up from its children

Archived and postponed children are left out. The first matching rule wins:

1. Every child archived or postponed → `postponed` if any is postponed, else `archived`.
2. All children `approved` → `approved`.
3. Any child `revise` → `revise`.
4. All children `implemented` or `approved` → `implemented`.
5. Any child `in-progress`, `implemented`, or `approved` → `in-progress`.
6. Otherwise → `not-started`.

One leaf flips and every ancestor updates. After bulk or manual edits leave parents out of sync, run `./superRA/superra task status fix`.

## The frontier is what to work on next

Ask "what's ready next?", or run `./superRA/superra task frontier`. The frontier lists unfinished leaf tasks whose `depends_on` prerequisites, own or inherited from a parent, are all `implemented`, `approved`, or `revise`.

- **Prerequisites still `not-started`, `in-progress`, or `postponed` block.** A prerequisite sent back to `revise` does not, and an `archived` one is dropped with a warning.
- **Number prefixes only set display order.** `01-` before `02-` orders the listing; only `depends_on` decides what runs first.
- **File inputs never block.** A file read from another task's [reproduction step](#/04-utility-skills/09-reproducibility) is listed beside the task when its producer is `stale`, `missing`, or `failed`, and the agent decides whether to rebuild it first.
- **Ready is not current.** Whether an output is up to date is a separate check, owned by [reproducibility](#/04-utility-skills/09-reproducibility).

The exact rules and edge cases are in the [task-file contract](skills/task-tree/references/task-file-contract.md#effective-dependencies).
