---
title: "Children Panel Consumes JSON, Not Regex-Parsed Mermaid Text"
status: implemented
depends_on: []
---

## Objective

The children dependency panel is driven by a structured JSON payload instead of regex-parsing never-rendered mermaid diagram source, and the status→color mapping lives in exactly one place.

- A JSON endpoint (new `/api/children-graph?root=<path>`, or `/dag` returning JSON) provides nodes (`path`, `slug`, `title`, `status`) and dependency edges; the client builds the panel from it.
- The `DAG_FILL_STATUS` color-inversion map and the mermaid-source regex parsing are deleted from the client.
- The standalone export embeds the JSON payloads through the existing fetch-shim fragment map, same as other per-task fragments.
- The global DAG view's behavior is unchanged — investigate whether it shares the text-parsing path and scope it in only if it does.
- Validation: the children panel renders identically (statuses, colors, edges, ordering) live and in a standalone export; a task title containing a standalone ` --> ` line no longer corrupts the panel; both suites green.

## Planner Guidance

Findings (2026-07-19 review): `dag.html:16-17` states the `.mermaid` div "is no longer rendered — it is the line-based source the parser reads"; the client recovers status by regexing `style <id> fill:#…` and inverting the hard-coded `DAG_FILL_STATUS` map at [base.html:3209-3248](../../../../skills/task-tree/scripts/templates/base.html#L3209-L3248), which must stay byte-synced with `status_colors` in [dag.html:22-30](../../../../skills/task-tree/scripts/templates/dag.html#L22-L30); edges come from a `/^\s*(\S+)\s*-->\s*(\S+)\s*$/gm` scan. The JSON precedent already exists in the same template: the `data-node-paths` attribute on `.dag-controls` carries JSON.

Server-side, the sibling-graph data is trivially available from `Task.children` + `depends_on` (see the `/dag` route at plan_dashboard.py:1111-1132). Standalone embedding pattern: `_build_standalone_fragments` at plan_dashboard.py:1481-1530.

## Results

Added `GET /api/children-graph?root=<path>` — a plain JSON route built directly off `Task` data (no template render): `{"children": [{path, slug, title, status}, ...], "edges": {childPath: [depPath, ...]}}`, computed by [plan_dashboard.py:777-798](../../../../skills/task-tree/scripts/plan_dashboard.py#L777-L798) (`_children_graph_payload`). The route itself is [plan_dashboard.py:1081-1091](../../../../skills/task-tree/scripts/plan_dashboard.py#L1081-L1091).

Client side ([base.html:3084-3187](../../../../skills/task-tree/scripts/templates/base.html#L3084-L3187)): `loadChildrenDag` now fetches `/api/children-graph?root=<path>` and calls `.json()` instead of `.text()`; the old `parseChildrenDag` (DOM-parse `.dag-controls[data-node-paths]`, regex-scan `style <id> fill:#color` lines, regex-scan `<dep_id> --> <child_id>` lines) and the `DAG_FILL_STATUS` color-inversion map are both deleted, replaced by a small `childrenGraphFromPayload` that reads the JSON fields directly (title prefers the payload's own non-lossy title, falling back to the shared `pathTitles` DOM-harvest map, then the slug).

**Global DAG view scoping (per the "investigate, scope in only if shared" guidance):** the global (root-less) `GET /dag` view was never fetched by any client code with a `root=` value — only the children panel used that branch, confirmed by grep across `templates/` and `plan_dashboard.py`. Rather than leave a now-orphaned `root=<path>` branch, standalone fragment (`_render_dag_fragment`), and DAG_FILL_STATUS/`status_colors` byte-sync obligation in place, I removed the `root` parameter from the `/dag` route entirely — it now always renders the whole-tree mermaid view, unchanged in every other respect (still exercised by `test_dag_returns_mermaid`). This is a **deviation from the literal Planner Guidance** (which only asked to delete client-side parsing and add the JSON source) toward a slightly larger but still-surgical change: it directly satisfies the objective's "the status→color mapping lives in exactly one place" bullet — `dag.html`'s `status_colors` map is now consumed by exactly one thing (the global mermaid view's own `fill:` styling), with no client-side inverse map to keep byte-synced. `dag.html`'s docstring and the `/dag` route's docstring were updated to reflect the narrower scope.

**Standalone export:** `_build_standalone_fragments` now embeds `/api/children-graph?root=<path>` fragments (a real JSON object per task, not an HTML string) instead of `/dag?root=<path>` fragments; `_render_dag_fragment` (now unused) was removed. `dict[str, str]` widened to `dict[str, object]` since the fragment map now carries mixed HTML-string and JSON-object values — `standalone_fragments | tojson` in base.html serializes both correctly, and the standalone fetch shim's `.json()`/`.text()` already special-case per-consumer (unchanged).

**Regression coverage for the title-corruption pitfall:** added `test_title_with_standalone_arrow_line_does_not_corrupt_edges` — a task titled literally `-->` no longer forges a bogus dependency edge (impossible by construction now: titles are a JSON string field, never scanned for graph structure). Rewrote `TestChildrenDagContract` in [test_dashboard.py:1540-1618](../../../../skills/task-tree/scripts/test_dashboard.py#L1540-L1618) to assert against the JSON contract instead of regex-parsing mermaid HTML; updated the three standalone-fragment tests that pinned `/dag?root=` fragment identity to pin `/api/children-graph?root=` instead; updated `TestServerSideEscaping::test_standalone_export_escapes_titles_and_previews` — the DAG-label escaped-title occurrence is gone (title is no longer HTML-escaped-then-JSON-escaped in this fragment; it is JSON-escaped once, still script-safe, verified by a new assertion); dropped `DAG_FILL_STATUS` from the `_run_node` JS-harness dependency list (no longer defined in base.html).

**Verification:** `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts -q` → 706 passed, 2 skipped (pre-existing, unrelated), run fresh in this session. Manually verified against the live `superRA/` tree: `GET /api/children-graph?root=task-tree/dashboard` returns the 10 children with correct statuses/titles; `GET /dag` (no root) still returns the mermaid `graph LR` source unchanged.

**Not changed:** `nonloopback-host-serve` and `backend-robustness` (sibling in-flight tasks) are untouched; edits were scoped to `/dag`, the new `/api/children-graph` route, `_build_standalone_fragments`, and the children-panel client code, per the dispatch's merge-conflict-minimization steer.
