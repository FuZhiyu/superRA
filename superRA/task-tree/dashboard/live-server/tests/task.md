---
title: "Test suite for live dashboard"
status: approved
depends_on:
  - server
  - templates
  - live-reload
  - cli-entry
  - comments
tags: []
created: 2026-05-25
---

## Objective

Cover the live dashboard's server routes, in-memory data layer, SSE framing, Jinja2 template rendering, the comment sidecar data layer, and the agent comment CLI — the core functionality verified during review. All tests live in [`test_dashboard.py`](skills/task-tree/scripts/test_dashboard.py), extending the `test_task_tree.py` pattern.

## Results

Implemented in [`test_dashboard.py`](skills/task-tree/scripts/test_dashboard.py) (~49 tests across six classes), grouped by area:

**Server routes & data layer.**
- **TestServerRoutes** (14): `GET /`, `GET /task/{path}` (valid + 404), `GET /dag` (mermaid node IDs + arrows), `GET /kanban` (5 status columns), `GET /files` (serve + path-traversal rejection + 404), SSE heartbeat via generator, full comment API CRUD cycle, comment 404 cases.
- **TestDataLayer** (5): `rebuild_tree()` populates the index, `rebuild_task()` updates one task while preserving children, returns None for a deleted task, `_build_index()` creates the flat dict.

**SSE broadcast & template rendering.**
- **TestSSEBroadcast** (4): single-line broadcast, multi-line with per-line `data:` prefix, event naming `task:{path}`, full-queue client dropped.
- **TestTemplateRendering** (8): `_render_task_node()` `sse-swap`/`hx-swap` attrs, badge class, `_render_summary()` counts, `vscode_link` filter, `file_url` filter, `</template>` escaping in markdown, kanban 5 columns, DAG `../sibling` arrow resolution.

**Comment system & CLI.**
- **TestComments** (13): `load_comments` empty, `add_comment` auto-increment + gap handling, `resolve_comment` toggle + nonexistent, `delete_comment` bool, `split_into_blocks` (paragraphs, fenced code, lists), `resolve_anchors` (exact match, shifted block, orphan detection, missing section), YAML round-trip.
- **TestCLI** (5): `list` output, `list` with no comments, `resolve`, `list-tree` with comments, `list-tree` empty.
