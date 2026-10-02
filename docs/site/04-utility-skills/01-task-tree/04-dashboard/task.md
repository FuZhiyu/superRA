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

Two views share the selected task, the reader, comments, and attachments:

- **Tree** navigates the task hierarchy, for reading task bodies and results.
- **Graph** draws each task as a card holding its [reproduction steps](#/04-utility-skills/09-reproducibility), with file edges between steps as solid arrows and `depends_on` prerequisites as dashed ones. It opens at 80% on the selected task; expand a task to show its own steps and child tasks.

### Step freshness in the Graph view

Each step card shows its state (`fresh`, `stale`, `missing`, `failed`, or `unverified`) and how long its last run took; each task card and Tree row counts its steps per state. Freshness is separate from workflow status, so an `approved` task can still hold a stale step. A task whose `## Reproduction` declaration has an error is outlined in red, with a link to the finding.

Read a card in two parts:

- **Border, glyph, and label: the state a build acts on.** A step whose producer is stale reads `stale · upstream`.
- **Fill: the step's own evidence.**
  - Tinted: its own state, so a stale tint marks where the staleness starts.
  - Empty: inherited from upstream. The step reruns only if rebuilding its producers changes its inputs.
  - Hatched: some of its files are online-only on this machine (a Dropbox, Box, or iCloud file not downloaded), so this machine cannot check it: its own state is `unverified`.

Select a step to see its inputs, its outputs, and its last actual run. The panel names where an inherited staleness starts and marks each online-only file with its size. An accepted step reads `fresh` with the recorded reason.

On the live dashboard, each task and step card has a **Build** button. Its menu offers a build with the producers the selection reads, a build of only this task or step, or a forced rerun of it, and shows the `superra repro build` command and an estimate from the last recorded runs. A build that would read a file not on this machine runs nothing and lists the files. Hover a step that is not fresh to see why. An exported snapshot shows the same graph and states without these controls.

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
