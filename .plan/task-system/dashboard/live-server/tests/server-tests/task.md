---
title: "Server route and data layer tests"
status: not-started
review_status: ~
integration_status: ~
depends_on: []
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

Test FastAPI routes and the in-memory data layer.

**Tests:**
- `GET /` returns 200 with rendered HTML containing task nodes
- `GET /task/{path}` returns children fragment for valid path, 404 for invalid
- `GET /dag` returns mermaid diagram with correct node IDs and dependency arrows
- `GET /kanban` returns 5 status columns with correct task counts
- `GET /files/{path}` serves files, rejects path traversal attempts
- `GET /events` returns SSE stream with heartbeat
- `rebuild_tree()` populates task index correctly
- `rebuild_task()` updates single task without losing children
- Comment API routes: POST create, GET list, PATCH resolve, DELETE
