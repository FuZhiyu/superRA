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

Scope: emit a standalone HTML file for a chosen subtree root (any task node) whose embedded data and pre-rendered nodes cover exactly that subtree — its nav tree, breadcrumb, and `TASK_PATHS`/internal-link set rooted at that node — rendering the same tree/views the live dashboard shows for it, fully offline from a `file://` open.

Two deliverables, both required:

1. **Share button in the live dashboard (primary).** Add a "Share" / "Export" control to the task UI (on the active-node card and/or each task node) that downloads *that node's subtree* as a single self-contained HTML file. Back it with a server route (e.g. `GET /export?root=<path>` or `/share/<path>`) that renders the subtree's standalone HTML and returns it with `Content-Disposition: attachment` (a sensible filename like `<slug>-dashboard.html`) so the browser saves it directly. This is the "share function" — clicking it on any task hands you a portable HTML of that task and its descendants.
2. **CLI subtree export.** Let the CLI export a chosen subtree to a file: a subtree-path argument plus an output-file path (extend the `generate` subcommand with a `--root <task-path>` option, or add an `export` subcommand — your choice). Whole-tree `generate` with no root stays the default.

Build both on the unified standalone machinery — `generate_dashboard()`, `_build_standalone_fragments()`, the `standalone` template flag — scoped to a subtree. The whole-tree path drives module state from `walk_plan(plan_root)`; for a subtree, locate the node with `_find_task(<path>)` and scope `_root_task` / the embedded data / the pre-rendered fragments / nav to that node so the export contains exactly the subtree (reuse the existing subtree scoping the server already does for `GET /dag?root=<path>`). Do **not** build a parallel renderer or reintroduce a separate template.

The offline-degradation behavior (comments, worktree-switching, SSE hidden/disabled cleanly; client-side filtering/search retained) is inherited from `unify-static-export` — reuse it; only re-verify it holds for a subtree-scoped export.

Validation:
- Clicking the Share button on a task in the live dashboard downloads a single HTML file scoped to that task's subtree; it opens offline via `file://`, shows exactly that subtree's tasks and the expected views, embeds the data inline (no network/SSE/`fetch` for task data), internal task-links navigate within the exported subtree, and there are no dead comment/worktree/SSE controls.
- The CLI subtree export produces the same file for a given `--root`; whole-tree `generate` is unchanged.
- The live `serve` path and the whole-tree static export are otherwise unchanged in behavior.
- Test coverage for the subtree-scoped build (subtree fragment/path set is scoped correctly; the export route returns an attachment; offline-clean) added to the dashboard/task-system suite; run `uv run pytest skills/task-system/scripts/test_task_system.py skills/task-system/scripts/test_dashboard.py`.

## Revision Notes

Updated 2026-05-31: added `depends_on: unify-static-export` and narrowed scope from "build the standalone-from-base.html machinery" to "add subtree scoping on top of it." The whole-tree unification + `DASHBOARD_HTML` deletion + server-less standalone mode are now owned by `unify-static-export`; this task is the subtree-scoping increment only. Substantive (dependency + scope narrowing).

Updated 2026-05-31 (later): researcher confirmed building this now and centered it on a **Share function** — a Share/Export button in the live dashboard that downloads any task's subtree as embedded HTML (via a server route returning `Content-Disposition: attachment`), with the CLI subtree export as the secondary path. Both are now required deliverables. Substantive (made the live Share button a hard requirement, was previously "CLI and/or button").

## Results

