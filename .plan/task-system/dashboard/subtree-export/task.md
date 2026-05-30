---
title: "Export subtree dashboard to standalone HTML"
status: not-started
depends_on:  []
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Add an export feature to the dashboard: export the dashboard for a chosen subtree as a single self-contained HTML file with the task data embedded inline, so it can be opened or shared without the live server or the `.plan/` tree present.

The export targets a subtree root (any task node, not only the whole tree) and emits one HTML file whose task data is embedded directly in the document (e.g. inlined JSON / pre-rendered nodes) rather than fetched from server endpoints. The exported file must render the same tree/views the live dashboard shows for that subtree and work fully offline from a `file://` open — no calls back to the SSE/live-server routes, no dependency on local `.plan/` files. Reuse the existing rendering path (`plan_dashboard.py` + the Jinja templates under `skills/task-system/scripts/templates/`) rather than building a parallel renderer; the static dashboard generator already produces a standalone page, so the work is scoping it to a subtree and guaranteeing zero live-server coupling in the output.

Decide and document how interactive features degrade in the static export (filtering/search can stay since they are client-side; comments and worktree-switching, which need server routes, should be hidden or disabled gracefully rather than producing dead controls). Expose the export via the dashboard CLI (and/or a button in the live server) with an argument selecting the subtree path and the output file.

Validation: exporting a subtree produces a single HTML file that opens offline via `file://`, shows that subtree's tasks and the expected views, contains the data inline (no network fetches for task data), and has no broken/dead server-dependent controls.

## Results

