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

Status rolls up automatically: flip a leaf to `approved` and every ancestor recomputes, reading `approved` only once all its active children do. Nobody hand-maintains a parent's state.

## What the agent runs, and what you can run yourself

The agent drives the tree through a committed CLI wrapper (`./superRA/superra`, bootstrapped once with `wrapper init`); you can run the same commands to inspect or steer the work. Setting one field is a direct edit to a `task.md` — a hook then validates the tree and propagates the rollup — but use the CLI for anything structural: scaffolding tasks from a template, bulk status changes, and `task move`, which carries the whole directory and rewrites links (never raw `mv`).

This page is the conceptual top of the task-tree subtree. The operational detail lives one level down, each on its own page:

- [**The task file**](#/04-utility-skills/01-task-tree/01-task-file) — the `task.md` anatomy: frontmatter fields and body sections.
- [**The CLI**](#/04-utility-skills/01-task-tree/02-cli-commands) — the command surface for reading, querying, and editing the tree.
- [**Status and the frontier**](#/04-utility-skills/01-task-tree/03-status-and-frontier) — the status lifecycle and how rollup and the frontier are computed.
- [**The dashboard**](#/04-utility-skills/01-task-tree/04-dashboard) — the live browser view and its shareable static export.

See [`task-tree`](skills/task-tree/SKILL.md) for the full skill.
