---
title: "Export subtree dashboard to standalone HTML"
status: approved
depends_on:
  - unify-static-export
tags: []
created: 2026-05-30
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
- Test coverage for the subtree-scoped build (subtree fragment/path set is scoped correctly; the export route returns an attachment; offline-clean) added to the dashboard/task-tree suite; run `uv run pytest skills/task-tree/scripts/test_task_tree.py skills/task-tree/scripts/test_dashboard.py`.

## Results

Subtree scoping is layered onto the unified standalone machinery from `[unify-static-export](../unify-static-export/task.md)` — no parallel renderer, no second template. Both deliverables ship: a live-dashboard **Share** button backed by a `GET /export` route, and a CLI `generate --root <task-path>` flag. Whole-tree `generate` (the default, with no `--root`) is byte-identical to before.

### Key design decision: re-base, don't keep full paths

The Objective sketched "locate the node with `_find_task(<path>)` and scope `_root_task` to that node." A located node keeps its **full** tree path (e.g. `task-tree/dashboard`) because [`parse_task`](../../../../skills/task-tree/scripts/_task_io.py#L232) computes every `task.path` relative to the git-discovered `.plan` root, not relative to where the walk starts. Keeping full paths breaks the standalone+navigation machinery in three ways, all of which key on `task.path` treating the empty string as the root:

- The breadcrumb splits `activePath` and renders an ancestor crumb per segment; full paths produce dead crumbs (`root › task-tree › dashboard › …`) for ancestors not in the export, whose `/node/<ancestor>` fragments don't exist → empty cards.
- `_task_depth(task.path)` drives nav inline-vs-lazy: a depth-3 subtree root renders everything lazy-loaded immediately instead of inlining to depth 2.
- The JS router boots at `activePath = ''` and the nav root id is `task-root` ([nav_node.html:20](../../../../skills/task-tree/scripts/templates/nav_node.html#L20)); a full-path root row id (`task-task-tree-dashboard`) never matches, so the initial active node 404s and the highlight is lost.

So the increment **re-bases** the subtree: [`_rebase_subtree(task, root_path)`](../../../../skills/task-tree/scripts/plan_dashboard.py#L984) strips the `root_path + '/'` prefix from every path so the subtree node becomes `path=""` and descendants are relative to it. The identical machinery then renders the subtree exactly as it renders a whole tree. `depends_on` holds sibling slugs (last segment), unaffected by re-basing; `dir_path` is left untouched so figure/file resolution still points at real dirs.

### Implementation

- **Render extraction.** [`render_standalone_html(plan_root, output_path, root)`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1017) returns the standalone HTML string (no file write). When `root` is given it walks the full tree, `_build_index` + dict-lookup to locate the node (raising `KeyError` if absent), re-bases it, and drives module state (`_root_task`/`_task_index`/`_project_root`) off the re-based subtree — so `_build_standalone_fragments()`, `collect_all_tasks`, and `TASK_PATHS` all scope to the subtree automatically. [`generate_dashboard`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1089) is now a thin writer over it; its name/signature/return contract are preserved (the four auto-callers import it unchanged) with `root=None` added as an optional third arg.
- **Figure prefix.** `standalone_plan_dir` is computed from the **subtree** dir (its real on-disk `dir_path`) relative to the output file, so re-based task paths resolve their `<img>` sources from a `file://` open (e.g. default-output-into-`.plan` + `--root task-tree/dashboard` → prefix `task-tree/dashboard/`).
- **Share route.** [`GET /export?root=<path>`](../../../../skills/task-tree/scripts/plan_dashboard.py#L887) returns the subtree's standalone HTML with `Content-Disposition: attachment; filename="<slug>-dashboard.html"`. It snapshots and restores the live server's module state around the render (via [`_set_module_state`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1008)) so a Share click never perturbs the running server. Empty `root` exports the whole tree.
- **Share button.** The active-node card builder in [base.html](../../../../skills/task-tree/scripts/templates/base.html#L1838) emits a `Share` button (server-mode only — gated on `!window.STANDALONE`, since a downloaded file has no server to re-export from), and [`shareSubtree(path)`](../../../../skills/task-tree/scripts/templates/base.html#L1888) navigates a hidden `<a download>` to `/export?root=…` so the attachment download never replaces the page. Styled with a new `.share-btn` rule using the accent tokens.
- **CLI.** `generate` gains `--root <task-path>`; an unknown root prints an error and exits 1.

### Validation

- **Offline-clean (subtree).** A `--root task-tree/dashboard` export against the real `.plan` tree: `window.STANDALONE = true`, `window.fetch` overridden, no `hx-ext="sse"` / `sse-connect` / `EventSource(`, no `worktree-selector` / `sse-full-reload`, `resolveInternalTaskPath` + `TASK_PATHS` retained. All 45 embedded task paths and `/node` fragment keys are re-based (no `task-tree/` prefix, no out-of-subtree siblings).
- **Share route.** Returns 200 with `attachment` disposition; subtree scoping confirmed (`00-flow` export contains re-based child `a`, excludes sibling `01-flat`); unknown root → 404; live `/node` + `/` unchanged after an export (state restored).
- **Whole-tree unchanged.** `generate_dashboard(root=None)` is byte-identical to the bare call (regression-locked by a test). `.plan/dashboard.html` regenerates without error (gitignored — regenerate-only, not committed).
- **Tests.** `uv run pytest skills/task-tree/scripts/test_task_tree.py skills/task-tree/scripts/test_dashboard.py skills/task-tree/scripts/tests/` → **298 passed**. New: 5 subtree-build tests in `TestDashboard` (path-set scoping, fragment scoping, offline-clean, unknown-root, whole-tree-unchanged) and 5 route tests in `TestServerRoutes` (attachment, subtree scope+filename, unknown-root 404, live-state-undisturbed, Share-button wired).

### Accepted limitation: synchronous export render

`GET /export` runs the synchronous `render_standalone_html` on the event loop, pausing SSE heartbeats for the duration of a large export. This is deliberate: the module-state snapshot/restore around the render is only safe because nothing else runs concurrently. Offloading to a thread requires making that snapshot concurrency-safe first — deferred as a follow-up rather than fixed here.

### Figure portability (resolved by a sibling)

An earlier cut of this task left figures in a *downloaded* share file non-portable (the relative prefix resolved against the embedded tree's location, not beside a file saved to Downloads). That limitation is now **resolved** by [self-contained-export](../self-contained-export/task.md): the standalone export base64-embeds each figure as a data URI, so figures travel inside the single file and render offline from anywhere. The relative-path prefix described above survives only as a *fallback* for srcs that cannot be embedded. The export is otherwise fully self-contained and offline.

