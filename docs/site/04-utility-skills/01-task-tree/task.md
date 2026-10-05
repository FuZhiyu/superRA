---
title: "task-tree"
status: not-started
depends_on:  []
---

## Objective

The task tree keeps your project's state — what is done, what is blocked, what each step found — in files under `superRA/` instead of the chat. Git versions it with your code, so a fresh session, or you a week later, resumes from the files rather than from scrollback.

## Ask in plain language

| Say | You get |
|---|---|
| "superra, plan this analysis" | The work broken into a tree of tasks for you to review |
| "work the ready tasks" | Tasks done in dependency order |
| "show me the tree" | The whole tree with rolled-up status |
| "what can I start now?" | The **frontier**: unfinished leaf tasks whose prerequisites are met |
| "what's left on the holdings pipeline?" / "what's blocking the merge?" | An answer read from recorded state, not guessed |
| "open the dashboard" | A live browser view of the tree and its reproduction graph |

## The tree is the directory tree

- **Each task is a directory holding a `task.md`** with its objective, status, prerequisites, and, once done, its results. Nesting a directory nests the task. There is no database.
- **`depends_on` names the sibling tasks that must finish first.** Files a task reads from another task's [reproduction steps](#/04-utility-skills/09-reproducibility) are reported as inputs but never hold it back.
- **A parent's status is computed from its children**, never set by hand.

## The agent edits; you can too

- **One committed wrapper, `./superRA/superra`, runs every command.** The agent writes it on first use; run the same commands yourself to inspect or steer the tree.
- **Edit one field directly; restructure with the CLI.** Fix an objective, or drop or park a task, by editing its `task.md`. Move or rename a task with `task move`, which carries the directory and repairs links and dependencies.
- **Hooks check every edit.** After each agent edit to the tree, a harness hook validates the structure and recomputes rollups; see the [Hooks page](#/06-hooks).

## Reference pages

- [**The task file**](#/04-utility-skills/01-task-tree/01-task-file) — frontmatter fields and body sections.
- [**The CLI**](#/04-utility-skills/01-task-tree/02-cli-commands) — commands to read, query, and edit the tree.
- [**Status and the frontier**](#/04-utility-skills/01-task-tree/03-status-and-frontier) — the status lifecycle, rollup, and what counts as ready.
- [**The dashboard**](#/04-utility-skills/01-task-tree/04-dashboard) — the live browser view and its shareable export.

The full skill is [`task-tree`](skills/task-tree/SKILL.md).
