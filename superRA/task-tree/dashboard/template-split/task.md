---
title: "Split base.html into Cacheable Static CSS and JS"
status: not-started
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
