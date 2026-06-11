---
title: "Work With Task Files"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

<!-- intent: frame the purpose of task files as the human-agent collaboration surface -->
Task files are how you and the agents collaborate.
Agents write their findings and await your feedback in `task.md`; you steer the work by reading those files and making decisions.
This guide explains how to read what agents produce, how to give feedback, and when and how to edit task files yourself.

## Read what an agent produced

<!-- intent: show the right way to read a task and what the output looks like -->
After an agent completes a task, its findings live in the `## Results` section of that task's `task.md`.
Read it using the wrapper command, which also injects the ancestor context the agent inherited:

```bash
./superRA/superra task read <task-path>
```

For example:

```bash
./superRA/superra task read 01-data/02-merge
```

The output shows the task objective, any planner guidance, the `## Results` the agent wrote, and any active `## Review Notes`.
The reviewer's verdict (`APPROVE` or `REVISE`) and their specific findings are in `## Review Notes`.

## Review and approve work

<!-- intent: explain the researcher's role in the review step and when agents ask questions -->
When a reviewer agent approves a task, it sets the status to `approved` and the task advances.
When a reviewer finds problems, it sets the status to `revise` and writes specific findings in `## Review Notes`.

As a researcher, you are not the reviewer — the reviewer is an agent role that `superimplement` dispatches.
Your role is to watch the status advance, read `## Results` to evaluate the findings, and approve the overall outcome as each task completes.

The agent stops and asks you a question when it hits a decision that belongs to you:
a methodology choice the objective did not specify, a data availability question, a scope boundary it cannot resolve from the task file alone.
These questions are explicit — the agent stops and surfaces them via `AskUserQuestion`.
If the session is asynchronous (you check in later), the question appears in the task's `## Review Notes` or in the terminal where the agent is running.

When agents ask questions about scope — "Should I include pre-2000 observations?" — the answer shapes the task objective.
Record your answer by editing the `## Objective` directly, then tell the agent to continue.

## Give feedback or change scope mid-flight

<!-- intent: explain the comment mechanism and the material-change decision boundary -->
The cleanest way to give feedback on in-progress work is to pin a comment on the relevant section of a `task.md` via the dashboard.
Comments surface to the agent on the next `superra task read` and are resolved once the agent addresses them.

For small corrections — a note on a specific result, a clarification on what a variable should mean — use a comment.

For scope changes — changing the sample, changing the outcome variable, changing the methodology — these are material changes.
Material changes require going back through `superplan` to update the task tree before the agent can proceed; changing the task objective and rerunning without a plan revision will leave the task tree out of sync with what the agent actually did.
Tell the agent:

> "The scope has changed: [describe the change]. Please update the task tree before continuing."

The agent will load `superplan`, propose the necessary task-tree revisions, and stop for your approval before resuming.

## Edit a task file directly

<!-- intent: explain when and how to edit task files directly, and what sections you own -->
You can edit `task.md` files directly — they are plain Markdown files.
The authoring convention is "current state, not a log": edit in place rather than appending "Update:" notes.

As the researcher, you own:

- **`## Objective`** — what the agent is supposed to do. You can clarify or extend it.
- **Comments** — pin them via the dashboard or by editing `comments.yaml` next to the `task.md`.

Agents own `## Results` (what they did and found) and `## Review Notes` (active review items).
Editing those sections directly is fine for corrections, but be aware that the agent's next dispatch will treat the task file's current state as authoritative.

The full task-file field contract is in [Reference › Task File](#/05-reference/01-task-file).

## Read the current tree and see what is dispatchable

<!-- intent: show tree/frontier commands for monitoring -->
To see the full tree with status badges:

```bash
./superRA/superra task tree
```

To see only the tasks ready to dispatch (dependencies met, status `not-started`):

```bash
./superRA/superra task frontier
```

These commands are described fully in [Reference › CLI Commands](#/05-reference/02-cli-commands).

For a visual view of the tree, DAG, and kanban board, see [See Your Work (Dashboard)](#/04-how-to/04-see-your-work).
