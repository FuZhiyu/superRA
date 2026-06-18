---
title: "task-tree"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

You get a live view of your whole project — a tree with rollup status, the set of tasks ready to work next, a dependency DAG, and a kanban board — all computed from plain files git tracks. Reach for it once a project grows past a handful of moving parts and you start losing the thread of which task is done, which is ready next, and what a finished one actually found. Because the whole state lives in files, a fresh agent — or you, a week later — opens the repo and resumes from the files alone.

The idea underneath is that **the filesystem is the task hierarchy**. Every task is a directory with a `task.md` holding its objective and results; nesting a directory nests the task, and a task depends only on its siblings. There is no database and no separate index — the tree you see is the directory tree, and git versions all of it alongside your code.

From that committed structure the tooling derives everything else:

- **Status that rolls up.** Each task carries a status, and a parent's status is computed from its children — flip a leaf and every ancestor updates. You never hand-maintain a parent's state.
- **The dispatchable frontier.** The set of tasks ready to work right now — not blocked by an unfinished sibling — is computed from the dependency edges, so you always know what can start next.
- **The dependency DAG.** Sibling `depends_on` edges form a graph the tooling can show you, so the ordering constraints in a workstream are explicit rather than remembered.
- **The live dashboard.** A browser view of the tree, frontier, DAG, and a kanban board that updates as work progresses, and exports to a single shareable HTML file.

This page is the conceptual top of the task-tree subtree. The operational detail lives one level down, each on its own page:

- [**The task file**](#/04-utility-skills/01-task-tree/01-task-file) — the `task.md` anatomy: frontmatter fields and body sections.
- [**The CLI**](#/04-utility-skills/01-task-tree/02-cli-commands) — the command surface for reading, querying, and editing the tree.
- [**Status and the frontier**](#/04-utility-skills/01-task-tree/03-status-and-frontier) — the status lifecycle and how rollup and the frontier are computed.
- [**The dashboard**](#/04-utility-skills/01-task-tree/04-dashboard) — the live browser view and its shareable static export.

See [`task-tree`](skills/task-tree/SKILL.md) for the full skill.
