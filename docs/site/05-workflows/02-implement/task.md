---
title: "IMPLEMENT: Build and Review"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

IMPLEMENT runs the task tree — the **frontier**, every task whose dependencies are satisfied, one task at a time, with results recorded in each `task.md` as they land. Ask the agent to work a task and it does the work itself, alongside you:

```text
Work @superRA/showcase-analysis/01-data.
```

You steer as it goes, and you read the state on the [dashboard](#/04-utility-skills/01-task-tree/04-dashboard) rather than in the chat. When a task lands, the agent asks whether to run an **independent review** — now, deferred, or skipped — and recommends a depth and focus. Skip it and the agent verifies the work itself and marks the task `approved`; the commit records which of the two happened, so later you can see what depth of review each result got.

A review is a separate agent reading the committed evidence — the actual files and diff, not the implementer's summary — and returning one of two verdicts: **APPROVE** advances the task to `approved`; **REVISE** sends numbered, specific findings back for a fix pass. Work does not advance past a REVISE.

Independence is what makes review worth its cost. An agent reviewing its own work shares its own blind spots, so the review is a scoped independent pass: the dispatch names a depth tier and one or more focuses, and the reviewer reports every finding it has evidence for — a `file:line`, an artifact, a quoted line — leaving severity calls to the orchestrator. That is what catches the silent bad merge, the wrong aggregation, the unreproducible output. Take one when a result is load-bearing, when the plan flagged the task as high-stakes, or when the agent comes back uncertain. Whatever individual tasks got, INTEGRATE reviews the accumulated work once before anything ships. The role behavior is owned by the [implement-task](skills/implement-task/SKILL.md) and [review-task](skills/review-task/SKILL.md) skills.

### Execution modes and seat assignment

The default is **interactive mode** (`direct` remains an alias): the main agent co-edits the task as a live canvas, executes it, always self-reviews, and pauses often for your feedback.

Say `superimplement` and the run goes **autonomous**: the agent works the frontier through an implementer seat per task, plus a reviewer seat wherever a review is warranted, without stopping for you. It fills those seats per task — both with subagents for large or routine work, or one with the main agent for a small, high-stakes, or context-heavy task; whoever fills a seat runs that role's full protocol. Ask for it when the frontier is broad, parallelizable, or context-heavy; the agent will also recommend it, with a reason, when it sees one of those. That mode is orchestrated by [superimplement](skills/superimplement/SKILL.md).
