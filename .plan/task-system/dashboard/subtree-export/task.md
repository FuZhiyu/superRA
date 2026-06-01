---
title: "Export subtree dashboard to standalone HTML"
status: not-started
depends_on:
  - unify-static-export
tags: []
created: 2026-05-30
updated: 2026-05-31
---

## Objective

Add **subtree scoping** to the standalone HTML export. The sibling `[unify-static-export](../unify-static-export/task.md)` task makes the whole-tree `generate` path render a self-contained, offline, server-less single-file dashboard from `base.html` with task data embedded inline (no `/node`, `/dag`, SSE, or `/files` fetches; comments/worktree controls degraded gracefully). This task builds on that single rendering path — do **not** build a parallel renderer or reintroduce a separate template — to let the export target **any subtree root**, not only the whole tree.

Scope: emit a standalone HTML file for a chosen subtree root (any task node) whose embedded data and pre-rendered nodes cover exactly that subtree, rendering the same tree/views the live dashboard shows for it, fully offline from a `file://` open. Expose the export via the dashboard CLI (a subtree-path argument plus an output-file argument) and/or a button in the live server.

The offline-degradation behavior (comments, worktree-switching, SSE hidden/disabled cleanly; client-side filtering/search retained) is inherited from `unify-static-export` — reuse it; only re-verify it holds for a subtree-scoped export.

Validation: exporting a subtree produces a single HTML file that opens offline via `file://`, shows that subtree's tasks and the expected views, contains the data inline (no network fetches for task data), and has no broken/dead server-dependent controls.

## Revision Notes

Updated 2026-05-31: added `depends_on: unify-static-export` and narrowed scope from "build the standalone-from-base.html machinery" to "add subtree scoping on top of it." The whole-tree unification + `DASHBOARD_HTML` deletion + server-less standalone mode are now owned by `unify-static-export`; this task is the subtree-scoping increment only. Substantive (dependency + scope narrowing).

## Results

