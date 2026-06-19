---
title: "task-tree"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

You ask the agent to plan and work a project, and you want it to know what is actually left to do. Say "superra, plan this analysis" and the agent breaks the work into a tree of tasks; say "superimplement" and it works the ready ones in dependency order. Ask "what's left on the holdings pipeline?" mid-project and the answer comes from recorded state, not from guessing.

A bare agent keeps project state in the conversation — which steps are done, which are blocked, what the last run found — and that state evaporates when the session ends. The next session reconstructs it from scrollback and scattered TODOs, and gets it wrong in costly ways: a finished step gets redone, a task starts on an input its dependency never produced, or a load-bearing result is forgotten because it lived in a message that scrolled off.

The task tree makes the filesystem the single source of truth instead. Every task is a directory holding a `task.md` with its objective, status, dependencies, and (once done) its results. Nesting a directory nests the task; a task depends only on its siblings, by directory name. There is no database — the tree you see is the directory tree, and git versions it alongside your code, so a fresh agent (or you, a week later) resumes from the files alone.

From that structure the agent computes answers you can ask for in plain language: "show me the tree" (whole tree with rollup status), "what can I start now?" (the **frontier** — leaf tasks whose dependencies are all satisfied and that are not yet done, ready to dispatch with no ordering call), "what's blocking the merge?" (the sibling dependency graph), "open the dashboard" (live browser view of tree, frontier, DAG, and kanban).

## What the agent runs, and what you can run yourself

### One wrapper drives the tree

The agent reads and edits the tree through a small committed script, `./superRA/superra`, that lives in your repo. It is a thin wrapper: every command in the subpages — `task tree`, `task frontier`, `task read` — is run through it. You can run the exact same commands yourself when you want to inspect the tree or steer the work by hand, so nothing the agent does to the tree is hidden behind a tool only it can reach. If a project does not have the wrapper yet, the agent writes it on first use, so you never set this up by hand.

### Agents edit; hooks keep the tree honest

The agent edits task files continuously as the work moves — flipping a status, appending a result, adding a dependency. A **hook** is a check your harness (Claude Code or Codex) runs automatically right after each edit to the tree — not a git hook, but part of the agent session; here it validates the structure (no dependency pointing at a task that does not exist, no status that contradicts its children) and recomputes the rolled-up status. The division is that the agent makes the edits and the hook catches the ones that would leave the tree inconsistent, so a careless write cannot quietly corrupt the project's recorded state. The hooks superRA ships are listed on the [Hooks page](../../06-hooks/task.md).

### Status rolls up on its own

**Rollup** means a parent task's status is computed from its children, never set by hand. Flip a leaf to `approved` and every directory above it recomputes: a parent reads `approved` only once all of its active children do, so the top of the tree always reflects what is actually finished underneath. You never edit a parent's status to match its children — the hook does it for you.

### Set a field by hand; move a task with the CLI

The split between editing a file directly and reaching for a command is worth knowing. Setting one field — marking a task `not-started`, fixing a typo in an objective — is a direct edit to that `task.md`, and the hook revalidates from there. Anything *structural* goes through the CLI instead. `task move` carries the whole task directory to its new home and rewrites every dependency link that pointed at it; a raw `mv` would move the files but leave those links pointing at the old path, so the tree would still compile but its dependencies would silently dangle. Use the command for moves and renames, edit the file directly for everything else.

This page is the conceptual top of the task-tree subtree. The operational detail lives one level down, each on its own page:

- [**The task file**](#/04-utility-skills/01-task-tree/01-task-file) — the `task.md` anatomy: frontmatter fields and body sections.
- [**The CLI**](#/04-utility-skills/01-task-tree/02-cli-commands) — the command surface for reading, querying, and editing the tree.
- [**Status and the frontier**](#/04-utility-skills/01-task-tree/03-status-and-frontier) — the status lifecycle and how rollup and the frontier are computed.
- [**The dashboard**](#/04-utility-skills/01-task-tree/04-dashboard) — the live browser view and its shareable static export.

See [`task-tree`](skills/task-tree/SKILL.md) for the full skill.
