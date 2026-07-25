---
title: "Browse and Render Task Artifacts in the Dashboard"
status: not-started
depends_on:
  - 02-dashboard-artifact-data
---

## Objective

Expose task-local attachments as a lightweight file canvas inside the owning task's dashboard detail view.

- Add an Attachments block that groups nested paths without adding artifact rows to the task sidebar, dependency graph, status rollup, or Kanban board.
- Render Markdown sidecars in-dashboard through the existing markdown-it, KaTeX, syntax-highlighting, and DOMPurify boundary. Resolve their relative links and images from the sidecar's own directory rather than from `task.md`.
- Give every artifact an explicit open or download action; provide safe inline previews for supported image, PDF, and text/source types without executing scripts or active content.
- Refresh the block on the owning task's artifact event and re-render an open sidecar when it changes, while preserving task hash routing, breadcrumbs, comments, expanded branches, theme, scroll, and worktree selection.
- Keep live and standalone behavior aligned, including subtree exports and explicit unavailable/oversized states. Existing figures must continue to render inline in task results and appear only once in exported bytes.
- Add browser-facing and server-rendered regressions for sidecar-relative links, sanitization, nested grouping, supported previews, download actions, hot reload, worktree switches, standalone operation, accessibility, and unchanged task navigation; run the dashboard and full task-tree suites.

## Planner Guidance

Keep `activePath` as the owning task path and open an artifact within that task's detail surface, so browser history and every task-level view retain their existing semantics. Generalize the current Markdown renderer with a content-base directory instead of creating a second rendering stack. Relevant files are [task_body.html](../../../../skills/task-tree/scripts/templates/task_body.html), [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js), [dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css), [base.html](../../../../skills/task-tree/scripts/templates/base.html), and [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py).

Artifact search is optional for this scope: add it only if the existing index can accept owner-task artifact records without duplicating discovery or creating a second navigation model. The required discovery surface is the Attachments block on the owning task.

## Results
