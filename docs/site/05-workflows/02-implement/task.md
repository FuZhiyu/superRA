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

**Every task runs through an implementer–reviewer pair.** The implementer does the work, writes what it found into the task's `## Results`, and hands off. A separate **reviewer** then inspects the committed result independently (the actual files and diff, not the implementer's summary) and returns one of two verdicts: **APPROVE** advances the task to `approved`; **REVISE** sends numbered, specific findings back for a fix pass. Work does not advance past a REVISE, regardless of how small the task looks, and review is not skippable.

The reviewer is adversarial: its job is to find what the implementer missed. An agent reviewing its own work shares its own blind spots, so a fresh reviewer with a different prompt and a mandate to hunt for failure catches the silent bad merge, the wrong aggregation, the unreproducible output. As each task is approved, the next ready one is picked up, and you watch the order unfold on the dashboard. The role behavior is owned by the [implementer](agents/implementer.md) and [reviewer](agents/reviewer.md) specs and orchestrated by [superimplement](skills/superimplement/SKILL.md).

### Direct vs. subagent mode

The default is **subagent mode**: a fresh implementer subagent per task, then a reviewer subagent that catches what self-review cannot. **Direct mode**, where the main agent implements the task itself, is available for small, clearly-scoped tasks where dispatching two subagents is more overhead than it is worth. Direct mode still dispatches a reviewer; review is never skipped either way.

### Resuming a project

Pick a project back up wherever it stands — months later or after a revision — without re-reading the whole history. The frontier is computed from committed task status, so you ask what is ready and dispatch it the same way as new work:

```bash
./superRA/superra task frontier   # what is ready to dispatch now
./superRA/superra task tree       # the full status picture
./superRA/superra dashboard       # a visual overview
```

A task left in `revise` is resumed too: superRA re-dispatches the fix, the reviewer re-checks the cited findings, and the loop continues to APPROVE. Resuming and revising mid-flight is owned by [superimplement](skills/superimplement/SKILL.md).

