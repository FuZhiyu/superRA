---
title: "SSE broadcast and template rendering tests"
status: implemented
depends_on: []
tags: []
created: 2026-05-25
---

## Objective

Test SSE event framing and Jinja2 template rendering correctness.

**Tests:**
- `_broadcast()` formats multi-line data with per-line `data:` prefix
- Per-task events use `event: task:{path}` naming
- `_render_task_node()` produces HTML with correct `sse-swap` and `hx-swap="outerHTML"` attrs
- `_render_summary()` produces summary bar with task counts
- Template rendering: task_node macro generates correct structure (badge, slug, toggle, sections)
- Template rendering: `</template>` in markdown content is escaped
- Template rendering: DAG dependency arrows resolve `../sibling` paths correctly
- Jinja2 filters: `vscode_link` and `file_url` produce correct URIs

## Results

Implemented in [`test_dashboard.py`](skills/task-system/scripts/test_dashboard.py).

**TestSSEBroadcast** (4 tests): single-line broadcast, multi-line with per-line `data:` prefix, event naming `task:{path}`, full-queue client dropped.

**TestTemplateRendering** (8 tests): `_render_task_node()` sse-swap + hx-swap attrs, badge class, `_render_summary()` counts, vscode_link filter, file_url filter, `</template>` escaping, kanban 5 columns, DAG dependency arrows.
