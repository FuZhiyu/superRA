---
title: "Browse and Render Task Companion Files in the Dashboard"
status: not-started
depends_on:
  - 02-dashboard-artifact-data
---

## Objective

Expose task companion files as a lightweight, read-only canvas inside the owning task's dashboard detail view.

- Keep the sidebar semantic: task rows may show a companion-file count that opens the Files view, but files never become rows in the task hierarchy, dependency graph, status rollup, frontier, or Kanban board.
- Add a Files view that lists direct companions first and backward-compatible `attachments/` in a secondary group.
- Render Markdown companions through the existing markdown-it, KaTeX, syntax-highlighting, and DOMPurify boundary. Resolve their relative links and images from the companion's own directory rather than from `task.md`.
- Vendor and pin `notebookjs` for read-only `.ipynb` rendering, wiring it to the dashboard's existing Markdown, KaTeX, highlight.js (including Julia), and DOMPurify stack. Support Markdown, raw, and code cells plus stream, error, safe text/HTML/Markdown/LaTeX, and PNG/JPEG/sanitized-SVG outputs and cell attachments. Never execute notebook code, JavaScript outputs, widgets, or other active MIME types; show an explicit unsupported-output fallback.
- Give every companion an explicit open or download action; provide safe inline previews for supported image, PDF, and text/source types without executing scripts or active content.
- Refresh the block on the owning task's artifact event and re-render an open sidecar when it changes, while preserving task hash routing, breadcrumbs, comments, expanded branches, theme, scroll, and worktree selection.
- Keep live and standalone behavior aligned, including subtree exports and explicit unavailable/oversized states. Existing figures must continue to render inline in task results and appear only once in exported bytes.
- Add browser-facing and server-rendered regressions for companion-relative links, notebook cell/output types, malicious notebook content, unsupported MIME fallbacks, Python/Julia highlighting, sanitization, flat/attachment grouping, supported previews, download actions, hot reload, worktree switches, standalone operation, accessibility, and unchanged task navigation; run the dashboard and full task-tree suites.

## Planner Guidance

Keep `activePath` as the owning task path and open a companion within that task's detail surface, so browser history and every task-level view retain their existing semantics. Generalize the current Markdown renderer with a content-base directory instead of creating a second rendering stack. Relevant files are [task_body.html](../../../../skills/task-tree/scripts/templates/task_body.html), [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js), [dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css), [base.html](../../../../skills/task-tree/scripts/templates/base.html), [vendor/README.md](../../../../skills/task-tree/scripts/vendor/README.md), and [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py).

`notebookjs` 0.8.3 is approximately 8 KB minified and can reuse the renderer and sanitizer already shipped by the dashboard; do not add `nbconvert`, JupyterLab browser packages, notebook execution, or a second Markdown/highlighting stack. Its common static renderer is the intended fidelity boundary, with a narrow adapter for cell attachments and unsupported-output fallbacks. Record its pinned version, source URL, hash, and re-fetch command with the other hand-managed vendor assets.

Companion search is optional for this scope: add it only if the existing index can accept owner-task file records without duplicating discovery or creating a second navigation model. The required discovery surface is the Files view on the owning task.

## Results
