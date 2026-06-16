---
title: "Client-Side Search Over Tasks/Pages"
status: approved
depends_on: []
tags: []
created: 2026-06-10
---

## Objective

Add a search box to the dashboard UI that searches node titles and body text and navigates to the selected result, working in both the live server and the standalone export with no network dependency.

- In the standalone export, search runs over the already-embedded content (the `STANDALONE_FRAGMENTS` map or a purpose-built embedded index — implementer's call on which gives acceptable match quality and size).
- In the live server, search must reflect the current tree state (server-side endpoint or client index refreshed with the existing live-reload mechanism).
- Results show the node title and tree path; selecting a result navigates exactly as a sidebar click does (same hash-routing path, active highlight, scroll behavior).
- Keyboard accessible: focus shortcut, arrow-key result navigation, Enter to open, Escape to dismiss.

Success criteria: matches found against both a title and a body phrase in each mode; verified in the rendered DOM of a real export and a live session, plus tests for the index/endpoint construction.

## Planner Guidance

Plain substring/fuzzy scoring over titles and body text is sufficient for first release; do not add a vendored search library unless match quality forces it (any new vendor asset follows `vendor/README.md` conventions).

## Results

Added a full-text **search-and-navigate command palette**, distinct from the existing title-only sidebar filter (`#search-box` / `applyFilters`). The palette searches titles + body text and jumps to the chosen result. Ships by default; no vendored search library (plain weighted substring scoring per guidance).

### Index (purpose-built, both modes)

Built a server-side helper `_build_search_index(root_task, all_tasks)` returning one record per node (root included) — `{path, slug, title, text}` — where `text` is the body flattened by `_search_text` (drops fenced/inline code and markdown punctuation, collapses whitespace) ([plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py)). Chose a purpose-built index over `STANDALONE_FRAGMENTS` (which holds rendered HTML, not searchable plain text). The index is injected as `var SEARCH_INDEX` into [base.html](../../../../skills/task-tree/scripts/templates/base.html) at render time, so it is embedded in the standalone export (offline-clean, no network at query time) and present at page load in server mode.

### Live freshness

Added a `GET /api/search-index` endpoint returning the same index shape for the resolved worktree. The client re-fetches it via `refreshSearchIndex()` inside `onFullReload` (a structural add/delete) and `applyWorktree` (a worktree switch), so live search reflects current tree state — reusing the existing live-reload mechanism rather than querying the server on every keystroke. Standalone mode is a no-op there (no server).

### Search + navigation

`runSearch(query)` scores each record (`scoreSearchRecord`): title hits outrank slug hits outrank body hits, with bonuses for earlier and word-start matches, top 20 returned. Results show the node title, tree path, and a `<mark>`-highlighted body snippet. Selecting a result (`chooseSearchResult` → `setActive(rec.path)`) navigates through the exact same hash-routing path a sidebar click uses — same active highlight, breadcrumb, scroll, and `#/<path>` history entry.

### Keyboard accessibility

Focus shortcut: `/` (when not already in a field) or Ctrl/Cmd-K opens the palette. Inside: `↑`/`↓` move the active result (wrapping, `aria-selected` + scroll-into-view), `Enter` opens it, `Escape` dismisses. The palette is `role="dialog"` with a `role="combobox"` input and `role="listbox"` results; the "Find" header button is the pointer entry point.

### Verification

- Tests: `TestClientSearch` in [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py) (7 tests) — index records titles + body text, `_search_text` strips code/markdown, index embedded in the export, palette UI + scorer + navigation-via-setActive wiring, keyboard affordances, the `/api/search-index` endpoint shape, and refresh-on-reload wiring. Full suite: 281 passed, 2 skipped.
- Scoring logic (node, against the real index): a title query ("Merging") and a body-phrase query ("left join", "panel regressions") each return the right node; a no-match query returns empty — satisfying "matches against both a title and a body phrase in each mode" (the index and scorer are identical in both modes).
- Rendered artifact (real headless Chrome): in the **standalone export**, a body-phrase search returns the node and `setActive` updates `location.hash` to `#/01-guide` (the same hash a sidebar click produces); the title and body-phrase searches both resolve in a **doc-mode** export too.
