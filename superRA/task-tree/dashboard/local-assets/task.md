---
title: "Serve Render Libraries Locally: Offline-Functional Live Mode"
status: approved
depends_on:
  - template-split
---

## Objective

Live server mode loads every JS/CSS render library from the server itself, so the dashboard is fully functional with no network access.

- **User decision (2026-07-19):** Google Fonts stay on CDN with the existing system-font fallback stacks — fonts are the only permitted network fetch, and their absence only degrades typography. Do not vendor the UI font families.
- Vendor pinned copies of htmx and its SSE extension into `vendor/`, recording exact versions and re-fetch URLs in `vendor/README.md` per its existing discipline.
- A static route serves the vendored assets; live-mode `<script>`/`<link>` tags point at it instead of jsdelivr; the standalone branch inlines htmx/sse the way it already inlines the other libraries (today exports still fetch htmx from CDN).
- Validation: with network access blocked, a live dashboard fully functions — markdown, math, code highlighting, SSE row swaps, comments — rendered in system fonts; a standalone export opens offline with no failed requests other than fonts; both suites green.

## Planner Guidance

From the 2026-07-19 review: `vendor/` (888KB, git-tracked, hand-managed per `vendor/README.md` — re-fetched, never generated) already holds markdown-it, KaTeX + its 20 woff2 fonts, highlight.js + julia, DOMPurify, and texmath; live mode ignores all of it and fetches the same libraries from jsdelivr with floating major-version pins ([base.html:7-34](../../../../skills/task-tree/scripts/templates/base.html#L7-L34)). htmx/sse.js and the font links sit *outside* the `{% if standalone %}` branch (lines 7-11), which is why exports still hit the CDN. `window.markdownit(…)` runs at script top level, so a blocked CDN currently kills all dashboard JS including the router — worth a regression test.

Only missing assets: `htmx.min.js` (~50KB) + `sse.js` (~5KB). The governing convention line in `task-tree/task.md` §Conventions was already updated at planning time to reflect this target.

## Results

Live mode and the standalone export now read every render library from the same nine vendored files (no dashboard code fetches a render library from a CDN); Google Fonts is the one remaining network reference.

- **Vendored `htmx.min.js` (2.0.10) and `sse.js` (2.2.4)** into [vendor/](../../../../skills/task-tree/scripts/vendor) via the pinned-version `curl` recipe, resolving the exact versions from `x-jsd-version` the same way the existing five libraries are pinned. `vendor/README.md`'s table, SHA-256 block, and re-fetch recipe are updated with both files ([vendor/README.md](../../../../skills/task-tree/scripts/vendor/README.md)).
- **Extended `GET /static/{name}`** ([plan_dashboard.py:1055-1119](../../../../skills/task-tree/scripts/plan_dashboard.py#L1055-L1119)) from a 2-name whitelist (`dashboard.css`/`.js`) to also serve every vendored render-library file via a new `_VENDOR_ASSET_TYPES` whitelist. The route now takes `{name:path}` (not a single segment) so it can serve `vendor/languages/julia.min.js` and the 20 `vendor/fonts/KaTeX_*.woff2` files at their real relative paths — required because `katex.min.css` and `highlight.min.js` reference those siblings by relative URL, so serving `katex.min.css` from `/static/katex.min.css` only works if `/static/fonts/KaTeX_*.woff2` also resolves. The font whitelist entries are generated once at import time from `vendor/fonts/*.woff2` rather than hand-listed. `_resource_dir`/`_VENDOR_DIR`/`_TEMPLATES_DIR` moved up to before this route (previously defined ~600 lines later, by `_build_standalone_assets`) since the route's whitelist now needs `_VENDOR_DIR` at module-load time.
- **`base.html`** ([templates/base.html:7-44](../../../../skills/task-tree/scripts/templates/base.html#L7-L44)): moved htmx/sse out of the unconditional head (they previously sat *outside* the `{% if standalone %}` branch, which is why exports still hit the CDN) and into both branches — live mode now points all nine `<script>`/`<link>` tags at `/static/...` instead of `cdn.jsdelivr.net`; standalone inlines `htmx_js`/`sse_js` the same way it already inlines the other seven libraries.
- **`_build_standalone_assets`** ([plan_dashboard.py:1768-1805](../../../../skills/task-tree/scripts/plan_dashboard.py#L1768-L1805)) reads and returns `htmx_js`/`sse_js` alongside the existing five inlined libraries.

**Validation:**
- `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts -q` → **713 passed, 2 skipped** (pre-existing skips, unrelated to this task).
- Updated/added tests in [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py): `test_served_page_loads_render_libraries_locally` (replaces the old `test_served_page_keeps_cdn_render_tags`, which asserted the opposite — that live mode *should* hit the CDN), `test_static_route_serves_vendored_render_libraries` (all 9 assets + a font, ETag/304), `test_katex_css_font_urls_resolve_under_static`, `test_static_route_still_rejects_unknown_names`, plus updated highlight/DOMPurify CDN-tag tests (`test_served_page_loads_highlight_locally`, `test_served_page_loads_purify_locally`) and the standalone-inlining test (`test_standalone_inlines_render_libraries`) to cover htmx/sse. `test_vendor_files_present` now requires `htmx.min.js`/`sse.js` on disk.
- Two pre-existing tests (`test_generate_has_no_live_server_calls`, `test_subtree_export_is_offline_clean`) asserted `"EventSource(" not in html` as a proxy for "the export makes no SSE calls." Once htmx/sse are inlined into every export, that literal string is present (as inert library source — the htmx SSE extension only opens a connection for an element carrying `sse-connect`/`hx-ext="sse"`, and standalone emits neither). Narrowed both tests to the actual wiring-attribute checks (`sse-connect=`, `hx-ext="sse"`), which the pre-existing assertions already carried; dropped the literal-string check with a docstring explaining why.
- Manual network-block proof (no browser harness in this suite, so recorded here — same pattern as the existing figure/highlight/DOMPurify standalone tests): started `plan_dashboard.py serve` and curled `/`, `/static/htmx.min.js`, `/static/sse.js`, `/static/katex.min.css`, `/static/fonts/KaTeX_Main-Regular.woff2`, and `/static/languages/julia.min.js` — all 200, and `grep -o 'cdn.jsdelivr.net[^"]*'` on the served `/` page returned no matches (`fonts.googleapis.com` still present). Ran `plan_dashboard.py generate --plan-root superRA` and confirmed the exported file has zero `cdn.jsdelivr.net` occurrences, one `fonts.googleapis.com` occurrence, and both `version:"2.0.10"` (htmx) and `"Server Sent Events Extension"` (sse.js) inlined.

No deviation from Planner Guidance — implemented as scoped (vendor htmx/sse, extend the static route, wire both template branches).
