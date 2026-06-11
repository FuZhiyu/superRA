---
title: "Client-Side Search Over Tasks/Pages"
status: not-started
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
