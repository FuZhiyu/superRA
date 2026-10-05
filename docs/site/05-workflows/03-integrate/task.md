---
title: "INTEGRATE: Protect, Sync, and Ship"
status: not-started
depends_on:  []
---

## Objective

INTEGRATE lands approved work on your shared base branch (usually `main`) so its results stay reproducible and the codebase stays coherent. Say `superintegrate` to enter it. The phase is owned by [superintegrate](skills/superintegrate/SKILL.md).

## You decide twice

1. **At Protect:** which results to keep, what the permanent documentation looks like, and how each result is protected.
2. **At Integrate:** the finished permanent record together with one proposed refactoring task.

The agent also stops to confirm the base branch if no earlier decision recorded it, and for a merge conflict that would change what your work means.

## Five stages

| Stage | What happens | Your part |
|---|---|---|
| **Protect** | The agent surveys the provisional findings and proposes what to keep or drop, where the documentation and result files live, how the task tree consolidates, and how each result is guarded. | Choose; the choices land in one decision commit. |
| **Sync** | The agent merges the base branch's new changes by what they mean, not line by line ([semantic-merge](#/04-utility-skills/02-semantic-merge)). | Answer only if a conflict would change your work's meaning. |
| **Mature & Consolidate** | One agent writes the agreed documentation and result files and consolidates the task tree: update tasks fold into the task they changed, and each task's `## Results` is distilled, sometimes to a one-line pointer; a reviewer checks them against your Protect decision and drafts one temporary refactoring task, including what to prune. | — |
| **Integrate** | Agents execute the approved refactoring task, and a reviewer checks the final diff. This is the one independent review of all accumulated work. | Approve the record and the task together, before execution. |
| **Finish** | The agent re-checks that the base has not moved (looping back to Sync if it has), then opens a pull request or fast-forwards into the base, and removes the worktree if the work ran in one. | — |

## Protection options

- **Documentation alone** is valid protection for most results.
- **Add a drift test** for a headline coefficient or another result worth guarding automatically: a check that fails when a later sync or refactor moves the saved value ([result-protection](#/04-utility-skills/03-result-protection)).
- **Name external inputs** — files no step produces, such as a vendor download ([reproducibility](#/04-utility-skills/09-reproducibility)).

## Changes after approval go back a step

A materially different protected result returns to Mature & Consolidate; a materially different refactoring action returns to your approval. Codebase-fit refactoring follows [refactor-and-integrate](#/04-utility-skills/04-refactor-and-integrate).
