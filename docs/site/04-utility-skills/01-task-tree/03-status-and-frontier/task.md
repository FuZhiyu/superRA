---
title: "Status and the Frontier"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

Agents update each task's status as they work; parent statuses and the frontier are computed from those. You read them; the only statuses you set are scope decisions.

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

1. All children `approved` → `approved`.
2. Any child `revise` → `revise`.
3. All children `implemented` or `approved` → `implemented`.
4. Any child `in-progress`, `implemented`, or `approved` → `in-progress`.
5. Otherwise → `not-started`.

One leaf flips and every ancestor updates. After bulk or manual edits leave parents out of sync, run `./superRA/superra task status fix`.

## The frontier is what to work on next

Ask "what's ready next?", or run `./superRA/superra task frontier`. The frontier lists unfinished leaf tasks whose `depends_on` prerequisites, own or inherited from a parent, are all `implemented`, `approved`, or `revise`.

- **Prerequisites still `not-started`, `in-progress`, or `postponed` block.**
- **File inputs never block.** A file read from another task's [reproduction step](#/04-utility-skills/09-reproducibility) is listed beside the task when its producer is `stale`, `missing`, or `failed`, and the agent decides whether to rebuild it first.
- **Ready is not current.** Whether an output is up to date is a separate check, owned by [reproducibility](#/04-utility-skills/09-reproducibility).

The exact rules and edge cases are in the [task-file contract](skills/task-tree/references/task-file-contract.md#effective-dependencies).
