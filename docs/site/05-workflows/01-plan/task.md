---
title: "PLAN: Scope and Decompose"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

PLAN turns "I want to work on X" into a **task tree**: one `task.md` per unit of work, committed under `superRA/` before any code runs. You review the structure up front, and a fresh session can reopen it later and see exactly what was scoped. The planning protocol is owned by [superplan](skills/superplan/SKILL.md); reading and editing a `task.md` is on the [task-tree page](#/04-utility-skills/01-task-tree).

## Start by describing the work

Say `superplan` and describe the work in plain language:

```text
Using superRA, superplan a small analysis: simulate a monthly equity panel,
sort firms into size and momentum portfolios, and report the long-short spread.
```

- **Depth scales with the work.** Small changes plan quickly; ask to "plan hard" or "explore thoroughly" for a complex or unfamiliar project, and parallel agents explore before the planner proposes a design.
- **Work already done counts.** Point the planner at existing code or results and it builds the tree retroactively.

## You answer the decisions; the planner finds the facts

- **Facts:** the planner reads the codebase, data, and docs itself.
- **Decisions:** methodology, scope tradeoffs, and sample definitions come to you as **grilling** — rounds of questions, each with the planner's recommended answer, until no decision is open.
  - Grilling also runs standalone: ask the agent to *grill* or *stress-test* a loose idea.

## The planner shows you the tree, then starts execution

The planner shows the proposed tree with a dashboard link, commits it, and moves on to execution. Read the objectives and redirect or ask for changes to the scope or decomposition at any point.

## Replan when the scope shifts

Say `superplan` again to revise an objective, add tasks, or restructure. Only the changed part replans.

- **New work nests under the task whose concern owns it.** The planner widens an existing objective rather than starting a parallel tree; a new top-level task is reserved for unrelated work.
- **Consolidation cleans up structural debt.** Over a long project, ask for a consolidation pass: the planner proposes merges and prunes across the whole tree, and applies them in one commit once you approve.

## Skip PLAN for one small task

For small or exploratory work, ask the agent to work it directly: it writes a single `task.md` and executes it with you (see [IMPLEMENT](#/05-workflows/02-implement)). Use the full cycle for work that spans several tasks or will need a PR.
