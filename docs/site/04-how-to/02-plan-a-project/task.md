---
title: "Plan a Project"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

You want to break new research work into a task tree so agents can execute it step by step, each task reviewed before the next begins.
This guide shows you how to scope a project and create its task tree, how to adopt superRA in an existing project, and how to migrate from a legacy `PLAN.md`/`RESULTS.md` setup.

## Start the planning phase

Tell your harness to plan the work.
You can use plain language — superRA recognizes planning intent:

> "Let's analyze quarterly earnings surprises on stock returns. Make a plan."

Or invoke the skill directly:

> "superplan: I want to build a panel regression of earnings surprises on three-day abnormal returns, using CRSP and Compustat."

The `superplan` skill guides the agent through three phases: it explores your existing code and data, loads any relevant domain skill (data analysis, theory-modeling, writing), and then proposes a task tree.
The agent does not write any code during planning — it creates `task.md` files and stops for your approval.

For the full planning protocol, see the [`superplan` skill](skills/superplan/SKILL.md).

## Review and approve the task tree

The agent proposes a task tree and stops.
Read it before approving — the task tree is your contract with the agent.

Check that:

- Each task has a clear, testable objective (one sentence is a good sign; three paragraphs suggests it needs splitting).
- Tasks that depend on each other have a `depends_on` edge pointing to the right sibling.
- The scope matches what you actually want.

Once you approve, `superplan` commits the tree and hands off to `superimplement`.
If the tree needs changes, tell the agent what to fix; it revises and stops again.

## Design task objectives well

The quality of the task tree determines how well agents execute.
An objective is the implementation and review contract — it tells the agent what success looks like, not how to get there.

Guidance on writing good objectives, splitting tasks, and placing work in the right part of the tree is in [`superplan/references/task-tree-design.md`](skills/superplan/references/task-tree-design.md).
Key rules:

- Write the goal, not the steps.
- Include validation criteria (what must be true for the task to be complete).
- Name the outputs the task must produce.
- Keep tasks at the right size: one meaningful objective, one evidence trail, one review verdict.

## Adopt superRA on an existing project

If you already have code and results, you can create a task tree retroactively.
The `superplan` skill has a retroactive documentation mode: it reads your existing code and results, then creates `task.md` files that mirror the logical structure of the work (not just the file layout), and sets task statuses to match the work already done.

To start, open your project and say:

> "Create a superRA task tree for the work already done in this repo."

The agent will read your code and data, draft the tree, and stop for approval.
After you approve, you can pick up new work from the task frontier without losing the history of what was already completed.

For the full retroactive creation protocol, see [`superplan/references/task-tree-design.md §Retroactive Task-Tree Creation`](skills/superplan/references/task-tree-design.md).

## Migrate from PLAN.md / RESULTS.md

Earlier superRA projects used `PLAN.md` and `RESULTS.md` files instead of a `superRA/` task tree.
The `task-tree` skill provides a migration command that converts those files into a proper task tree:

```bash
./superRA/superra task migrate from-plan \
  --plan-md PLAN.md --results-md RESULTS.md --output superRA
```

The migrator reads the existing `PLAN.md` and `RESULTS.md`, scaffolds a `superRA/` task tree from their content, and preserves findings in `## Results` sections.
Review the generated tree and adjust task boundaries or statuses as needed.

Full migration details are in [`task-tree/references/internals.md §Migration`](skills/task-tree/references/internals.md).
