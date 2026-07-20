---
title: "Split base.html into Cacheable Static CSS and JS"
status: approved
depends_on:
  - template-trust-boundary
  - children-graph-json
---

## Objective

`base.html` carries page structure and a small config block only; the CSS and JS live in static files that the live server serves cacheably and the standalone export inlines — no behavior or visual change.

- Extract the ~1,740 CSS lines to `dashboard.css` and the ~3,100 JS lines to `dashboard.js` (or a few coherent files if the existing banner-comment module boundaries suggest it); a small inline `<script>` keeps the Jinja-templated config constants (`| tojson` values, standalone/doc-mode flags).
- The live server serves them as static routes with cache-friendly headers; the standalone export inlines their contents exactly the way `_build_standalone_assets` already inlines the vendored libraries.
- Only content that genuinely needs Jinja templating remains inline in `base.html`.
- Validation: live page and standalone export render identically before/after (spot-check master-detail, kanban, DAG, search palette, comments, dark mode); a page reload serves the css/js from browser cache; both suites green.

## Planner Guidance

From the 2026-07-19 review: the template is 5,032 lines / 209KB (CSS ≈ lines 36-1779, static HTML ≈ 1780-1936, JS ≈ 1937-5030) re-templated and re-sent on every page load with zero caching, unlintable, unmappable. The JS is already organized into de-facto modules by banner comments (router, sidebar, children panel, comments UI, search palette, SSE wiring) — follow those seams. Inlining precedent: [base.html:20-26](../../../../skills/task-tree/scripts/templates/base.html#L20-L26) + `_build_standalone_assets` ([plan_dashboard.py:1704-1731](../../../../skills/task-tree/scripts/plan_dashboard.py#L1704-L1731)).

Dependencies exist because `template-trust-boundary` and `children-graph-json` both edit the JS heavily — land them first so the extraction moves settled code. Adding a JS/CSS linter is enabled by this split but is **not** in scope.

Downstream tasks (`local-assets`, `frontend-polish`) cite pre-split `base.html` line numbers — after this task those locations live in the extracted files; the citations remain valid as content anchors, not line anchors.

## Results

`base.html` shrank from 4,970 to 252 lines. The ~1,743 CSS lines moved verbatim to [dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css) and the ~2,984 JS lines to [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js); `base.html` now carries page structure, a small inline `<script>` for the Jinja-templated config constants, and the `<link>`/`<script src>` (or standalone-inline) tags that pull the two files in ([base.html:36-40](../../../../skills/task-tree/scripts/templates/base.html#L36-L40), [base.html:198-250](../../../../skills/task-tree/scripts/templates/base.html#L198-L250)).

**What stayed inline vs. moved:**
- The two Jinja `{% if standalone %}` config blocks that assign `window.STANDALONE`/`window.DOC_MODE` and the `| tojson`-templated vars (`PROJECT_ROOT`, `RESOLVED_ROOT`, `ROOT_PREFIX`, `REPO_FILE_BASE`, `REPO_ROOT_PREFIX`, `DOC_LOCAL_LINKS`, `SEARCH_INDEX`, plus the standalone-only `STANDALONE_FRAGMENTS`/`STANDALONE_PLAN_DIR`/`STANDALONE_IMAGES`) are the only Jinja-templated content left in `base.html`'s script.
- One new templated var, `ALL_TASK_PATHS` ([base.html:239](../../../../skills/task-tree/scripts/templates/base.html#L239)), replaced the old `{% for t in all_tasks %}set[...]=true{% endfor %}` inline loop; `dashboard.js`'s `TASK_PATHS` IIFE now builds the same set from that array in pure JS ([dashboard.js:129-133](../../../../skills/task-tree/scripts/templates/dashboard.js#L129-L133)) — same membership set, no behavior change.
- The standalone `window.fetch` override (`_standaloneResponse`/`standaloneFetch`) moved to `dashboard.js` unconditionally-defined but only wired up `if (window.STANDALONE)` ([dashboard.js:61-66](../../../../skills/task-tree/scripts/templates/dashboard.js#L61-L66)) — equivalent to the old `{% if standalone %}...{% else %}...{% endif %}` branch, since `window.STANDALONE` is set by the inline config script before `dashboard.js` loads.
- A stray JS doc-comment that quoted `nav_node.html`'s Jinja `id="task-{{ ... }}"` syntax verbatim ([dashboard.js:1409-1411](../../../../skills/task-tree/scripts/templates/dashboard.js#L1409-L1411)) used to get accidentally Jinja-rendered by the old single-file template (evaluating to `id="task-root"` since `path` was undefined in that scope) — a latent double-render artifact, not real behavior. Reworded to prose so it can't be mistaken for live templating now that `dashboard.js` is a plain static/inlined file, never re-parsed by Jinja.

**Serving:** live mode adds `GET /static/{name}` ([plan_dashboard.py:1055-1084](../../../../skills/task-tree/scripts/plan_dashboard.py#L1055-L1084)), whitelisted to `dashboard.css`/`dashboard.js`, with `Cache-Control: public, max-age=3600` plus a SHA-256 ETag and 304 support (verified via `TestClient`: first request 200 with `ETag`, a repeat with `If-None-Match` returns 304). Standalone export extends `_build_standalone_assets()` to also inline `dashboard.css`/`dashboard.js` ([plan_dashboard.py:1741-1773](../../../../skills/task-tree/scripts/plan_dashboard.py#L1741-L1773)), the same `</script>`/`</style>`-escaping treatment the vendored libraries already get.

**Validation:**
- Rendered `base.html` directly (fake context) and confirmed the live-mode output links `/static/dashboard.css` and `/static/dashboard.js` with no leftover `{{`/`{%` tokens.
- Rendered the real `superRA/` tree standalone (`render_standalone_html`) and confirmed `dashboard.css`/`dashboard.js` are inlined byte-for-byte where the CDN/static tags used to sit, all config vars resolve to real values, and the standalone fetch shim + `TASK_PATHS`/`ALL_TASK_PATHS` wiring work end to end.
- `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts/test_dashboard.py -q` → 287 passed, 2 skipped (playwright/chromium unavailable in this environment, pre-existing), 0 failed.
- Full suite: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts -q` → 710 passed, 2 skipped, 0 failed.
- No live-browser spot-check (no headless browser available in this environment); master-detail, kanban, DAG, search palette, comments, and dark-mode coverage instead comes from the passing test suite, which asserts on the same CSS/JS content now served from the two new files (`TestChildrenDagContract`, `TestClientSearch`, `TestServerSideEscaping`, `TestDocMode`, `TestTouchSidebar`/`TestTouchPolish`, comment-route tests, etc.).

**Test-suite updates required by the split** (in [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py)): `BASE_HTML` now concatenates `dashboard.css` + `base.html` + `dashboard.js` so the many "template source contains X" literal-content assertions keep working regardless of which file a rule/function now lives in; 13 call sites that locally re-read `base.html` were pointed at `BASE_HTML`; tests that fetched `client.get("/")` expecting inline JS/CSS (`test_index_wires_share_button`, the two `test_served_page_carries_*_primitives` tests) now additionally fetch `/static/dashboard.js`/`/static/dashboard.css`; the two `TASK_PATHS` substring checks (`test_export_subtree_scopes_and_names_file`, `test_subtree_export_scopes_paths_to_subtree`) now parse the `ALL_TASK_PATHS` JSON array instead of matching the old `set["x"] = true` loop text; `test_forest_synthetic_root_renders_and_routes` now checks `navNodeId`'s real fallback logic in `dashboard.js` instead of the accidental `id="task-root"` comment-rendering artifact described above.
