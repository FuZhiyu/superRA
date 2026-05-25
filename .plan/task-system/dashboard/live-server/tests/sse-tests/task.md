---
title: "SSE broadcast and template rendering tests"
status: not-started
review_status: ~
integration_status: ~
depends_on: []
tags: []
created: 2026-05-25
updated: 2026-05-25
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
