---
title: "The Dashboard"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

The dashboard is the visual side of the task tree: a browser view of your whole project that updates as work happens, plus a way to hand a collaborator a frozen snapshot of it. You launch it once and leave it open while you work.

```bash
./superRA/superra dashboard        # start the live view (background; reuses a running server)
./superRA/superra dashboard stop   # shut it down
```

It opens onto three views of the same tree. The **tree** shows every task with its rolled-up status, so you see the whole project at a glance. The **DAG** draws the `depends_on` edges within a subtree, so the ordering constraints are visible rather than remembered. The **kanban** board sorts tasks by status — not-started, in progress, in review, approved — so you watch work flow across the columns as agents pick it up and reviewers sign it off. The server watches your task files and refreshes the open page on its own, so what you see tracks the work without a manual reload. A **search box** filters across every task and page by title and content, which is how you jump to a task in a large tree instead of scrolling.

### A shareable snapshot

You can freeze the current state into a single self-contained HTML file and hand it to anyone:

```bash
./superRA/superra dashboard export --output dashboard.html
```

The result is one file — the tree, all task bodies, math, and images inlined, with working deep links — that a collaborator opens in a browser with no superRA install, no server, and no repo checkout. It is a browsable snapshot of project state: what is done, what is in flight, and what each finished task found. (This documentation site is itself one such export, built from a task tree.) Because the export carries every word of every `task.md`, treat it like the repo it came from — on a public project, keep real subject IDs, private group names, query results, and internal paths out of task bodies, and use placeholder or hypothetical content in examples. Anything in a task is in the snapshot you share.

### Comments: steering without editing

Comments are the human-in-the-loop channel. You pin a note to a specific task — a correction, a question, a constraint you want the next agent to honor — and resolve it once it is addressed. A pinned comment surfaces inline whenever anyone runs [`task read`](#/04-utility-skills/01-task-tree/02-cli-commands) on that task and shows on the dashboard, so your steering reaches the agent that picks the task up next without your having to rewrite the objective.

### Running in parallel across worktrees

When you split a project across several git worktrees to run tasks in parallel, the live dashboard resolves whichever worktree you are viewing — different browser tabs can show different worktrees off the same server. The code is versioned per worktree, but the data usually is not, so keep the non-git files in step with [`worktree-data-sync`](#/04-utility-skills/06-worktree-data-sync) rather than copying them by hand.

The dashboard's serving model, port derivation, and export internals are in the [`task-tree`](skills/task-tree/SKILL.md) skill and its references.
