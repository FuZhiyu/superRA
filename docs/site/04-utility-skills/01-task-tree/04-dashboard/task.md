---
title: "The Dashboard"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

A browser view of your whole task tree that refreshes itself as agents work, so you read the run from it instead of reconstructing the state from chat or task files. Ask the agent to bring it up:

```text
Open the superRA dashboard and point me at what is in review.
```

The 0.5.0 workspace redesign is under development. **Tree** and **DAG** are alternative navigators sharing the selected task, reader, comments, and attachments; **Kanban** groups work by status. The DAG combines inferred file dependencies and logical prerequisites. Expand a task to reveal its own steps and immediate child groups; selecting or expanding keeps the surrounding scope. Use **Focus subtree** to narrow it explicitly.

Workflow status remains separate from reproduction counts. Step details show freshness, inputs, outputs, and the last actual execution; accepted results read as fresh with their review evidence available. Graph errors remain visible through filters, including cycles between task groups whose individual steps are acyclic.

### A shareable snapshot

To hand someone the project state (an advisor, coauthor, referee), ask for an export:

```text
Export the dashboard to a file I can send.
```

The result is one self-contained HTML file — tree, task bodies, math, and images inlined, with working deep links — that opens in any browser with no superRA install, server, or repo checkout. (This documentation site is one such export.) The export carries every word of every `task.md`, so anything in a task is in the snapshot you share: on a public project keep real subject IDs, private group names, query results, and internal paths out of task bodies.

### Comments: steering without editing

Pin a note to a specific task (a correction, question, or constraint) to steer it without editing the objective. The comment shows on the dashboard and surfaces inline whenever anyone runs [`task read`](#/04-utility-skills/01-task-tree/02-cli-commands) on that task, so it reaches the agent that picks the task up next. Resolve it once addressed.

### Running in parallel across worktrees

When you split a project across git worktrees to run tasks in parallel, the live dashboard resolves whichever worktree you are viewing, so different browser tabs can show different worktrees off one server. Code is versioned per worktree but data usually is not, so keep the non-git files in step with [`worktree-data-sync`](#/04-utility-skills/06-worktree-data-sync) rather than copying by hand.

### The commands behind it

What the agent runs, and what you can run yourself from a project terminal:

```bash
./superRA/superra dashboard                          # start the live view (background; reuses a running server)
./superRA/superra dashboard stop                     # shut it down
./superRA/superra dashboard export --output dashboard.html   # freeze the current state to one self-contained HTML file
```

The dashboard's serving model, port derivation, and export internals are in the [`task-tree`](skills/task-tree/SKILL.md) skill and its references.
