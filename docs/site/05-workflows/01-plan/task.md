---
title: "PLAN: Scope and Decompose"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

PLAN turns "I want to work on X" into a **task tree** — a small set of `task.md` files, one per unit of work, that holds the project's state in git instead of in an agent's context window. You get a structure you can read, approve, and steer before any code is written, and a record a fresh session can reopen later and see exactly what was scoped.

You enter the phase by saying `superplan` and describing the work in plain language:

```text
Using superRA, superplan a small analysis: simulate a monthly equity panel,
sort firms into size and momentum portfolios, and report the long-short spread.
```

The planner explores your project, identifies the domain so the right discipline applies, and proposes a decomposition — a root task with its objective, and child tasks with dependencies between them. You can also point it at work you have already done and have it build the tree retroactively.

Planning is autonomous, but it stops before execution and shows you the proposed tree. This is the one gate you control. Read the objectives, adjust the scope or decomposition, and approve. The planner commits the tree to `superRA/`, so the structure is in git before any task runs. Reading and editing a `task.md` is covered on the [task-tree page](#/04-utility-skills/01-task-tree); how trees get scoped and decomposed is owned by [superplan](skills/superplan/SKILL.md).

**Planning is re-enterable.** When your scope shifts — a new finding, a task that turned out bigger than expected, a direction you want to drop — you return to `superplan` to revise the objective, add tasks, or restructure the tree. Finished work stays as it is; only the changed part replans.

### When can I skip PLAN?

For small or exploratory work, yes. You can create a single `task.md` by hand, fill in its `## Objective`, and dispatch an implementer directly. The full three-phase cycle is the recommended path for work that spans multiple tasks or will need a PR; skipping PLAN on one self-contained task is reasonable.

