---
title: "IMPLEMENT: Build and Review"
status: not-started
depends_on:  []
---

## Objective

IMPLEMENT works through the **frontier** — every task whose dependencies are satisfied — and records each result in its `task.md` as it lands. By default the agent does the work itself, with you; on request it runs autonomously. Watch progress on the [dashboard](#/04-utility-skills/01-task-tree/04-dashboard) rather than in the chat.

## Work a task together (default)

Point the agent at a task:

```text
Work @superRA/showcase-analysis/01-data.
```

The agent co-edits the task file with you, executes it, checks its own work, commits, and pauses often for feedback. This is **interactive mode** (`direct` is an alias), owned by [interactive-mode.md](skills/using-superra/references/interactive-mode.md).

- **Your edit is the instruction.** Edit the task file alongside the agent and it applies the change without asking again; a passing remark in chat that would change scope gets confirmed first.
- **Explore first, write up after.** Say "write up what I just did" and the agent records the work as a task: results first, then `approved` if verified or `implemented` if review is still open. Exploratory scripts and figures go in the task's [`attachments/`](#/04-utility-skills/01-task-tree/01-task-file).

## Choose review per task

When a task lands, the agent asks whether to run an **independent review** — now, deferred, or skipped — and recommends a depth and focus.

- **What a review is:** a separate agent reads the committed files and diff, not the implementer's summary, and cites evidence (`file:line`, an artifact, a quoted line) for every finding.
  - **APPROVE** moves the task to `approved`.
  - **REVISE** sends numbered findings back for a fix pass; the task does not advance until they are resolved.
- **Depth and focus:** `quick` (a careful read) or `thorough` (re-derives numbers, traces values to artifacts); focus on `correctness`, `scope-fidelity`, or `results-writing`. Owned by [review-task](skills/review-task/SKILL.md).
- **When to take one:** a load-bearing result, a task the plan marked high-stakes, or an agent reporting uncertainty.
- **Skip it:** the agent verifies the work itself and marks the task `approved`.
- **The commit records which happened**, so you can later see what review each result got. INTEGRATE reviews all accumulated work once regardless.

## Hand off a broad frontier: `superimplement`

Say `superimplement` and the agent works the frontier without stopping for you: an implementer seat per task, plus a reviewer seat wherever review is warranted. Subagents usually fill the seats; the main agent fills one itself for a small, high-stakes, or context-heavy task.

- **Ask for it** when the frontier is broad, parallelizable, or context-heavy. The agent recommends it, with a reason, when it sees one of these.
- **It still stops** for a decision that changes a task's objective, and for the completion menu.
- Owned by [superimplement](skills/superimplement/SKILL.md).

## Closing the phase

When every task is approved, the agent verifies the work is committed, recorded, and reproducible: it rebuilds cheap stale steps and asks you before a costly rerun ([reproducibility](#/04-utility-skills/09-reproducibility)). Then it asks what to do next:

1. Proceed with integration
2. Change the task tree
3. Keep the branch as-is
4. Discard this work (you confirm by typing `discard`)
