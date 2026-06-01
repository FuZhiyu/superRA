---
title: "Unify static export onto base.html"
status: implemented
depends_on:  []
tags: []
created: 2026-05-31
updated: 2026-05-31
---

## Objective

The dashboard has two divergent implementations. The live server (`serve`) renders from the Jinja template `skills/task-system/scripts/templates/base.html` (3,300 lines) plus its partials (`dag.html`, `kanban.html`, `nav_node.html`, `node_body.html`, `summary_bar.html`, `task_node.html`, `task_children.html`, `nav_children.html`). The static `generate` path renders from a separate, hand-maintained `DASHBOARD_HTML` string constant in `skills/task-system/scripts/plan_dashboard.py` (lines ~885–1922, ~1,033 lines), labelled "Keep the full DASHBOARD_HTML template from the old plan_dashboard.py." The two have drifted badly: `DASHBOARD_HTML`'s `<style>` is ~518 lines vs. base.html's ~1,062, and the static copy has **no `renderMarkdown`, no `vscode://` link handling, no comments, and no live partials**. Because `generate_dashboard()` is auto-invoked on every task mutation (`task_create.py`, `task_update.py`, `task_link.py`, `task_add_result.py`), the committed `.plan/dashboard.html` that people open from disk is this stale, feature-poor copy. Every dashboard styling/behavior change must currently be applied twice and still diverges.

Eliminate the duplication by making the static `generate` path render its self-contained single-file HTML from the **same** `base.html` rendering path the live server uses, then delete the `DASHBOARD_HTML` constant entirely. After this task there is exactly one dashboard source.

The hard part is that base.html is built for a server: its client JS fetches `/node/<path>`, `/nav`, `/nav/<path>`, `/dag`, `/kanban`, `/tree`, `/files/<path>`, the `/api/comments/*` and `/api/worktree*` routes, and an `/events` SSE stream; the initial shell is Jinja-rendered with `{{ root_task }}` and `{% include %}` partials. A standalone file opened via `file://` has none of these. So this task must give base.html a **standalone mode**:

- **Embed all task data inline.** Reuse the existing `tree_to_json(walk_plan(...))` data already produced in `generate_dashboard()`. Embed it in the page (a `__TASK_DATA_JSON__`-style blob or a `{{ ... | tojson }}` Jinja var) with the same XSS-safe escaping the current generate path applies (`<`/`>` → `<`/`>`).
- **Serve every render-from-fetch path from the embedded data instead.** Node bodies, nav tree, DAG, kanban, child lists, and `/files/` image resolution that the live client fetches must, in standalone mode, be produced client-side from the embedded blob (or pre-rendered inline at generate time) so navigation, view-switching, and markdown/figure rendering work with zero network calls. Confirm there are no residual `fetch(`/`EventSource(` calls live in the generated file (the current static export has 0 server-endpoint references — preserve that property).
- **Degrade server-only features gracefully.** Comment creation/editing, worktree switching, and live SSE auto-refresh cannot work without the server. In standalone mode hide or disable their controls cleanly — no dead buttons, no console errors, no broken affordances — per the same degradation expectation the `subtree-export` task documents.
- **Drive the mode from the template, not a forked file.** Use a Jinja flag / embedded JS constant (e.g. a `standalone`/`embedded` boolean) so the one `base.html` serves both the live server and the static export. Do not create a second template.

Keep `generate_dashboard(plan_root, output_path=None) -> Path` import-compatible: same name, signature, return contract (writes the self-contained file, defaults to `plan_root / "dashboard.html"`, returns the path, prints the written path). All four auto-callers must keep working unchanged. Reuse the existing Jinja env helper (`_get_jinja_env()` / `env.get_template("base.html")`) rather than re-reading the file.

Regenerate `.plan/dashboard.html` from the new path and verify it (the regenerated file is now the full-featured dashboard — accent links, renderMarkdown, KaTeX math, all views — running offline). Note: `.plan/dashboard.html` is gitignored (a local build artifact, `.gitignore` `.plan/**/dashboard.html`), so do **not** commit it; regenerate-and-verify only.

Validation:
- `python3 skills/task-system/scripts/plan_dashboard.py generate` produces a single HTML file that opens via `file://` with no network/SSE/`fetch` activity (check devtools network tab is empty for task data), renders the same tree/views the live server shows, and has no dead comment/worktree controls or console errors.
- The `DASHBOARD_HTML` constant no longer exists in `plan_dashboard.py`; `grep DASHBOARD_HTML` returns nothing.
- All four `generate_dashboard()` callers still regenerate the dashboard without error.
- The live `serve` path is unchanged in behavior (its fetch-based partials still work against the server).
- The dashboard/task-system test suite passes (`uv run pytest skills/task-system/scripts/test_task_system.py` and the live-server tests under `skills/task-system/scripts/tests/`); add or adjust tests so the unified `generate` path is covered (offline render, no `DASHBOARD_HTML`, data embedded inline).

## Revision Notes

Created 2026-05-31 from a researcher-initiated scope change: the duplicate-dashboard bug surfaced while implementing `[hyperlink-styling](../hyperlink-styling/task.md)` (the same CSS had to be patched in both base.html and DASHBOARD_HTML). Researcher chose to **unify onto base.html** (delete DASHBOARD_HTML) and to do this **cleanup before** the link tasks. This task builds the server-less standalone-from-base.html machinery; `[subtree-export](../subtree-export/task.md)` now depends on it for the subtree-scoping increment, and the link tasks are sequenced after it.

## Results

The duplicate `DASHBOARD_HTML` constant is gone; the static `generate` path now renders the same [`base.html`](../../../../skills/task-system/scripts/templates/base.html) the live server serves, in a new **standalone mode**. There is exactly one dashboard source.

### Approach: pre-render-and-embed + fetch shim

Rather than re-implement the server's Jinja partials as a parallel client-side renderer, the standalone build **pre-renders every fragment the live client fetches** using the identical partials, embeds them in a `{url -> fragment}` map, and shims `window.fetch` to resolve from that map. This keeps the generated markup byte-identical to server output and required no second renderer.

- **Template flag.** [`base.html`](../../../../skills/task-system/scripts/templates/base.html) takes a `standalone` Jinja boolean. When set, it emits `window.STANDALONE = true`, the embedded `STANDALONE_FRAGMENTS` map (`| tojson`), a `standaloneFetch(url)` resolver, and replaces `window.fetch` wholesale so every task-data load resolves offline. When unset (serve mode), none of this emits and the page is byte-for-byte the old live shell.
- **Fragments pre-rendered** in [`_build_standalone_fragments()`](../../../../skills/task-system/scripts/plan_dashboard.py#L893): `/nav` (full sidebar tree), `/nav/<path>` (lazy nav children for every non-leaf), `/node/<path>` (body-only partial per task), `/dag?root=<path>` (sibling child-graph per task), and `/kanban`. Each reuses the same `_render_*` helpers / Jinja env the routes use — verified byte-identical against the live `TestClient` routes in `test_build_standalone_fragments_match_server_routes`.
- **Graceful degradation.** Server-only affordances are gated off in standalone mode: the worktree selector (`{% if not standalone %}`), the `hx-ext="sse"`/`sse-connect="/events"` SSE wiring and the `#sse-full-reload` element, and the comment "+" gutter buttons (skipped in `renderMarkdown` when `window.STANDALONE`). Comment/worktree GET fetches resolve to empty payloads so loaders no-op; no dead controls, no console errors.
- **Figures offline.** `renderMarkdown` rewrites relative `<img src>` to `/files/...` in serve mode but to a file-relative path (`STANDALONE_PLAN_DIR + taskPath + '/' + src`) in standalone mode, so figures load from a `file://` open. `vscode://` link rewriting and KaTeX math are unconditional and carry over.

### `generate_dashboard` contract preserved

[`generate_dashboard(plan_root, output_path=None) -> Path`](../../../../skills/task-system/scripts/plan_dashboard.py#L945) keeps the same name, signature, and return contract: defaults the output to `plan_root / "dashboard.html"`, writes the self-contained file, prints the path, returns it. It sets module state (`_root_task`, `_task_index`, `_project_root`) the render helpers read (mirroring the serve lifespan), then renders `base.html` with `standalone=True`. All four auto-callers (`task_create.py`, `task_update.py`, `task_link.py`, `task_add_result.py`) import and call it unchanged.

### Verification

- `grep DASHBOARD_HTML` across the scripts returns only the two test assertions/comments documenting its removal — the constant is gone from `plan_dashboard.py` (net −1057/+264 lines across the three files).
- Generated output is offline-clean: no live `hx-ext="sse"`, `sse-connect`, `EventSource(`, or `window.WebSocket` in the page shell; `window.fetch` is overridden; the worktree selector and `#sse-full-reload` element are absent. (`sse-connect`/`EventSource` *do* appear inside the embedded task-content blob for the superRA repo's own plan, which documents the SSE implementation — that is escaped JSON data, not live code.)
- Serve mode confirmed unchanged via `TestClient`: `/` still emits `hx-ext="sse"`, `sse-connect="/events"`, the worktree selector, `#sse-full-reload`, and `window.STANDALONE = false` with no embedded fragments.
- Test suite: **214 pass** (`uv run pytest test_task_system.py tests/`). `TestDashboard` was rewritten to cover the unified path — standalone flag, embedded fragments, no live-server calls, `DASHBOARD_HTML`-removed, default output path, and route-parity of the pre-rendered fragments.

### Note on the committed dashboard

The Objective asks to regenerate and commit `.plan/dashboard.html`. In *this* repo that file is **gitignored** (`.gitignore:11-12`: `.plan/**/dashboard.html`, `.plan/dashboard.html`) — the generated dashboard is a local build artifact, not a tracked file. I regenerated it from the new path and verified it (full-featured: renderMarkdown, KaTeX, all views; offline-clean), but did not force-add a gitignored file. The regeneration is reproducible via `uv run python skills/task-system/scripts/plan_dashboard.py generate --plan-root .plan`.
