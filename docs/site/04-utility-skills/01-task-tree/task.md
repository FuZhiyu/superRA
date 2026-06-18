---
title: "task-tree"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Ask a bare agent "what's left on the holdings pipeline?" mid-project and you get a confident, wrong answer assembled from whatever happened to be in the chat scrollback. The load step was redone last Tuesday, but that turn scrolled off. The merge is blocked on a filter nobody flagged as unfinished. The regression result that justified the current spec lives in a message three sessions ago. An unaided agent keeps project state in the conversation — which steps are done, which are blocked, what the last run found — and that state evaporates when the session ends. The next session reconstructs it from scrollback, a drifting memory file, and TODO comments scattered across scripts, and the reconstruction fails in costly ways: a step gets redone because nothing recorded it finished, a downstream task starts on an input its dependency never produced, or a load-bearing result is forgotten because it lived only in a message that scrolled off.

The task tree makes the filesystem the single source of truth instead. Every task is a directory holding a `task.md` with its objective, status, dependencies, and (once done) its results. Nesting a directory nests the task; a task depends only on its siblings, by directory name. There is no database and no separate index — the tree you see is the directory tree, and git versions all of it alongside your code, so a fresh agent (or you, a week later) opens the repo and resumes from the files alone.

You scaffold the structure once, then operate on it from the shell. Bootstrap the committed wrapper once with `./superRA/superra wrapper init`; every command below runs through it. To stand up a workstream:

```bash
./superRA/superra task create 01-data/01-load --title "Load Raw Holdings" \
  --objective "Read the raw 13F filings into a typed parquet."
./superRA/superra task create 01-data/02-merge --title "Merge Fund Characteristics" \
  --objective "Left join holdings with fund chars on fund_id x date." \
  --depends-on 01-load
```

From that committed structure the tooling computes the answers an unaided agent has to guess:

```bash
./superRA/superra task tree         # whole tree with rollup status badges
./superRA/superra task frontier     # leaf tasks ready to start now
./superRA/superra task dag 01-data  # the sibling dependency graph, as Mermaid
./superRA/superra dashboard         # live browser view: tree, frontier, DAG, kanban
```

`task frontier` is the one you run most: it returns the leaf tasks whose dependencies are all satisfied and that are not yet done — the set you can dispatch right now, with no judgment call about ordering. `task tree` shows status that rolls up automatically: flip a leaf to `approved` and every ancestor recomputes, so you never hand-maintain a parent's state, and a parent reads `approved` only once all its active children do. `task dag` renders the sibling `depends_on` edges as a graph, so ordering constraints are explicit rather than remembered. `dashboard` serves all of this in the browser, reusing a running server, and exports to a single shareable HTML file.

Editing is deliberately split. Setting one field on one task — including `status` — is a direct edit to its `task.md` with your normal editor; a PostToolUse hook then validates the tree and propagates the rollup. The CLI is for the operations where hand-editing is tedious or error-prone: scaffolding from a template (`task create`), bulk status changes (`task status cascade 01-data --status approved`), and moving a task (`task move`, which carries the whole directory and rewrites relative Markdown links). Intentional path changes go through `task move`, never raw `mv`, so sibling `depends_on` edges and links stay consistent. Run `task check` after any bulk or raw-filesystem change to audit status validity, dependency integrity, and cycle-free ordering.

This page is the conceptual top of the task-tree subtree. The operational detail lives one level down, each on its own page:

- [**The task file**](#/04-utility-skills/01-task-tree/01-task-file) — the `task.md` anatomy: frontmatter fields and body sections.
- [**The CLI**](#/04-utility-skills/01-task-tree/02-cli-commands) — the command surface for reading, querying, and editing the tree.
- [**Status and the frontier**](#/04-utility-skills/01-task-tree/03-status-and-frontier) — the status lifecycle and how rollup and the frontier are computed.
- [**The dashboard**](#/04-utility-skills/01-task-tree/04-dashboard) — the live browser view and its shareable static export.

See [`task-tree`](skills/task-tree/SKILL.md) for the full skill.
