---
title: "See Your Work (Dashboard)"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

You want to see what the agents have done, what is in progress, and what comes next.
The live dashboard gives you a tree view, a dependency DAG, and a kanban board — all auto-updating as tasks progress.

## Open the live dashboard

Run this in your project directory:

```bash
./superRA/superra dashboard
```

The server launches in the background and opens the dashboard in your browser.
If a server is already running for this project, the command reuses it rather than starting a second instance.
To stop it explicitly:

```bash
./superRA/superra dashboard stop
```

## Navigate the views

The dashboard has three panels:

**Tree view** — the task hierarchy with status badges.
Colored badges show each task's status at a glance: not started (grey), in progress (blue), implemented (gold), revise (red), approved (green), archived or postponed (muted).
Click a task to open its full `task.md` content in the side panel.

**DAG view** — the dependency graph.
Tasks with `depends_on` edges are connected; the graph makes parallel and serial structure visible at once.
Run `./superRA/superra task dag <subtask>` in the CLI to print the DAG for a specific subtree as Mermaid text.

**Kanban view** — tasks grouped by status across columns.
Useful for seeing how much work is in each stage at a glance.

## Share a snapshot

To share the current state of your task tree with a collaborator who does not have direct repo access, set up the GitHub Actions artifact workflow:

```bash
./superRA/superra dashboard artifact setup
```

After pushing your branch, the workflow runs automatically and uploads the exported dashboard HTML as a GitHub Actions artifact named `superra-dashboard-<branch-slug>-<ref-hash>`.
Anyone with repository read access can download it; the artifact is a self-contained HTML file, not a hosted webpage.

## Export a static snapshot locally

To generate a self-contained HTML file without GitHub Actions:

```bash
uv run --script skills/task-tree/scripts/plan_dashboard.py generate \
  --plan-root superRA/
```

The output is a single HTML file with all assets inlined — no server needed to open it.
Pass `--root <subtask>` to export only a subtree.

For full CLI options, see [Reference › CLI Commands](#/05-reference/02-cli-commands).
