---
title: "Server-Side Escaping: One Trust Boundary for Task Content"
status: not-started
depends_on:
  - dead-code-removal
---

## Objective

Make server-rendered HTML treat task-file content as untrusted, matching the client's existing DOMPurify posture, so agent-written task files cannot inject markup into the live page or into shared standalone exports.

- Turn on Jinja autoescape for the dashboard environment; audit every remaining template and mark only intentional raw spots `| safe` (pre-rendered fragment embedding, `text/x-markdown` payloads, `| tojson` sites which are already safe).
- **User decision (2026-07-19):** titles and section previews display HTML as literal text; markdown bodies keep full HTML support through the client DOMPurify gate. Do not add per-site sanitization to preserve raw titles.
- Remove the kanban inline `onclick` built by interpolating the task path; use a data attribute + delegated handler (the sidebar already uses delegation).
- Fix string-built HTML and selectors in client JS: active-card assembly goes through the existing escaping helpers; comment-anchor `querySelector` strings use `CSS.escape`.
- Validation: an adversarial fixture (title and section text containing `<script>`, `<img src=x onerror=…>`, single/double quotes, and a standalone ` --> ` line) renders as literal text in the sidebar, kanban, page `<title>`, section previews, and inside a standalone export; regression tests cover these; both suites green.

## Planner Guidance

Findings (2026-07-19 review): `autoescape=False` at [plan_dashboard.py:744-747](../../../../skills/task-tree/scripts/plan_dashboard.py#L744-L747); raw `{{ task.title }}` at [nav_node.html:36](../../../../skills/task-tree/scripts/templates/nav_node.html#L36), [kanban.html:31-32](../../../../skills/task-tree/scripts/templates/kanban.html#L31-L32), [base.html:6](../../../../skills/task-tree/scripts/templates/base.html#L6); the section preview strips `>` but not `<`. `dag.html:86,91` already escapes manually with `| e` — those become redundant-but-harmless under autoescape. JS sites: string-concat `innerHTML` card assembly at base.html:2985-3000 (helpers `escapeHtml`/`escapeAttr` exist at 3349-3354 and are used elsewhere — the safe pattern is in-file); selector building from user-derived section names at base.html:4674-4724 (a `"` in a `##` header currently throws and aborts comment loading for the task).

Audit scope after `dead-code-removal` lands: `base.html`, `nav_node.html`, `node_body.html`, `summary_bar.html`, `kanban.html`, `dag.html`. Check what `_render_summary` and the breadcrumb do with titles (breadcrumb uses `textContent` — already safe).
