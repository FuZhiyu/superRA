---
title: "Showcase: A Real Task Tree"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

You have read about the task tree. Here you can open one and click around.

This page links to a live export of a real superRA task tree. It is not a screenshot and not a simplified mock-up — it is the actual task-tracker interface, rendered by the same dashboard you get when you run superRA yourself. The documentation site you are reading is itself a dashboard export, so the chrome around the tree is the chrome around this page. Everything you read about in the [Quickstart](#/02-quickstart) and the [task-tree skill](#/04-utility-skills) is something you can now see directly: the status of every task, how a parent's status rolls up from its children, the dependency graph, and the review conversation inside an individual task.

The tree is a finished, real empirical study, run end-to-end through the workflow on fully public data: the canonical time-series test of linear factor models. It estimates CAPM and the Fama-French three-factor model on Ken French's 25 portfolios sorted by size and book-to-market, then uses the Gibbons-Ross-Shanken (GRS) joint test to ask whether either model prices the cross-section. Every task is `approved`, so you are reading the completed handoff: real regression tables, real figures embedded in the `## Results`, and the review history that got each task there. Open a task's `02-analysis` results to see the GRS verdict, or its `03-writeup` for the reader-facing narrative with the math.

[Open the asset-pricing study →](showcase-analysis-tree.html)

### What you are looking at

The export is a self-contained page with the full task-tracker chrome. As you explore, these are the elements to notice — each one maps back to a concept page.

- **Status pills.** Every task carries a colored status: green for `approved`, yellow for `implemented` (done but not yet reviewed), red for `revise` (a reviewer sent it back), blue for `in-progress`, grey for `not-started`. The [status lifecycle](#/04-utility-skills/01-task-tree/03-status-and-frontier) explains how a task moves between them.
- **Rollup.** A parent task's status is computed from its children, not set by hand. A tree with one child in `revise` shows the parent as un-finished — you can see at a glance that the project is not done, and where the holdup is.
- **The DAG.** The dependency graph view draws the edges between tasks: which task must finish before which can start. A task with an unmet dependency is off the [frontier](#/04-utility-skills/01-task-tree/03-status-and-frontier) — the set of tasks ready to be worked right now.
- **The kanban board.** The same tasks, grouped into columns by status, so a whole project's progress reads as one glance across the board.
- **Inside a task.** Click any task to open its `task.md`: the objective at the top, the results an implementer wrote, and the review notes a reviewer left — including findings that were sent back for revision. This is the handoff surface agents and humans share; the [Task File reference](#/04-utility-skills/01-task-tree/01-task-file) is the full anatomy.

Every task path is a deep link. The address bar updates as you navigate, so you can bookmark or share a link straight to one task.

### How this is built

The export is produced by the task-tree dashboard's standalone export — the same `generate` command documented in the [task-tree skill](skills/task-tree/SKILL.md) — which writes a single self-contained HTML file with everything inlined, no server required. The export is rebuilt fresh in CI on every deploy and is never committed to the repository; only the task sources are. The exact build invocation lives in the deploy pipeline, which regenerates the tree with:

```
uv run --script skills/task-tree/scripts/plan_dashboard.py generate --plan-root superRA --root showcase-analysis
```

The study is a subtree of superRA, scoped with `--root`. The export script is [plan_dashboard.py](skills/task-tree/scripts/plan_dashboard.py); the task-tree tooling that produces and reads this tree is documented in the [task-tree skill](skills/task-tree/SKILL.md).
