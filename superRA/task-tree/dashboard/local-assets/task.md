---
title: "Serve Render Libraries Locally: Offline-Functional Live Mode"
status: not-started
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
