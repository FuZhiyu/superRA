---
title: "Resume and Revise"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

<!-- intent: address two related scenarios: session interruption and scope revision -->
Research is rarely linear.
Sessions get interrupted, scope changes after results come in, and reviewers send tasks back.
This guide covers two related situations: picking up work that was interrupted mid-session, and revising the task tree after a discovery or scope change.

## Resume an interrupted project

<!-- intent: explain how re-entry works and what the agent reads to catch up -->
When you open a new session on a project in progress, the agent re-reads the `superRA/` task tree to find its place.
The task tree is durable state — it survives session boundaries because it is committed to git.

Start a new session and say:

> "Resume the superRA project."

The agent loads `superRA:using-superra` and reads the current frontier — the set of dispatchable tasks whose dependencies are met.
It picks up from where the approved tasks left off.

If you are not sure where things stand, check the tree first:

```bash
./superRA/superra task tree
./superRA/superra task frontier
```

For the visual version, run `./superRA/superra dashboard` — see [See Your Work (Dashboard)](#/04-how-to/04-see-your-work).

## Handle a task sent back for revision

<!-- intent: explain the REVISE loop from the researcher perspective -->
When a reviewer finds problems, the task's status is set to `revise` and the reviewer's findings appear in `## Review Notes` inside the `task.md`.
The agent reads the findings and fixes them; you do not need to intervene unless a finding requires a decision only you can make (methodology, scope, data availability).

The task stays in the `revise` → `implemented` → `approved` loop until the reviewer approves it.
You can read the active findings at any time:

```bash
./superRA/superra task read <task-path>
```

## Revise the task tree mid-flight

<!-- intent: explain how to change scope after work has started -->
When a discovery during implementation or a scope change from your research changes what the project should do, go through `superplan` to update the task tree before the agent continues.

Tell the agent:

> "The methodology has changed: [describe the change]. Please revise the task tree."

The `superplan` skill assesses which approved tasks the change invalidates, proposes revisions, and stops for your approval.
Tasks in the transitive downstream closure of the changed task are reset to `not-started` so they re-enter the frontier; unrelated approved tasks keep their status.

This is always the right path for material changes — updating an objective in place without a plan revision leaves the task tree out of sync with the work.

For the scope-change and re-entry protocol, see [`superplan` §User Feedback and Changing the Task Tree](skills/superplan/SKILL.md).
