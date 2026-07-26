---
title: "IMPLEMENT: Build and Review"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

IMPLEMENT runs the task tree. Say `superimplement` and superRA works through the **frontier** — every task whose dependencies are satisfied — one task at a time, recording results in each `task.md` as it goes. You watch and read it all on the [dashboard](#/04-utility-skills/01-task-tree/04-dashboard); you rarely need the chat.

```text
superimplement @superRA/showcase-analysis/01-data.
```

By default, every task runs through implementer and reviewer seats. The implementer does the work, writes what it found into the task's `## Results`, and hands off. A **reviewer** then inspects the committed result adversarially (the actual files and diff, not the implementer's summary) and returns one of two verdicts: **APPROVE** advances the task to `approved`; **REVISE** sends numbered, specific findings back for a fix pass. Work does not advance past a REVISE.

The reviewer is adversarial: its job is to find what the implementer missed. An agent reviewing its own work shares its own blind spots, so a fresh reviewer with a different prompt and a mandate to hunt for failure catches the silent bad merge, the wrong aggregation, the unreproducible output. As each task is approved, the next ready one is picked up, and you watch the order unfold on the dashboard. The role behavior is owned by the [implementer](agents/implementer.md) and [reviewer](agents/reviewer.md) specs and orchestrated by [superimplement](skills/superimplement/SKILL.md).

### Execution modes and seat assignment

The default is **subagent mode**: autonomous execution with an implementer seat and a reviewer seat. The orchestrator fills those seats per task — both with subagents for large or routine work, or one with the main agent for a small, high-stakes, or context-heavy task. Whoever fills a seat runs that role's full protocol.

**Interactive mode** (`direct` remains an alias) is the explicit opt-in for work you want to steer closely. The main agent co-edits the task as a live canvas, executes it, always self-reviews, and asks whether to run independent review now, defer it, or skip it. Select interactive by the human cadence you want, not because a task is trivial.
