---
title: "Shared reveal-in-tree navigation primitive + Kanban click-through"
status: not-started
depends_on: []
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Build the one navigation primitive that the whole `view-navigation` workstream reuses: clicking any task reference (a Kanban card now; DAG nodes in the sibling tasks) must land the reader on that task **in the tree view, with the node expanded and its rendered details visible** — not merely scrolled to a collapsed row. Wire the Kanban cards to it as the first consumer. Load `frontend-design` before touching markup or CSS.

**Current state.** In `skills/task-system/scripts/templates/base.html`, `showView(view)` toggles the tree / `#view-dag` / `#view-kanban` containers, and there is an existing `showTreeAndExpand(path)` function (around line 931). The Kanban cards in `skills/task-system/scripts/templates/kanban.html` already call `onclick="showTreeAndExpand('{{ t.path }}')"`, but that does not reliably reveal the task's content. Read what `showTreeAndExpand` actually does today before changing it — find the real gap (does it switch to the tree view, expand every ancestor on the path, scroll the node into view, and expand the node's own rendered-markdown details?) rather than assuming.

**Deliverable.** A single, generally-callable JS function keyed by task path (extend `showTreeAndExpand` or introduce a clearly-named `revealTask(path)` it delegates to) that: (1) switches to the tree view, (2) expands every ancestor task node along the path so the target is visible, (3) scrolls the target node into view, and (4) expands the target's details so its rendered markdown content shows. Keep it callable from any view by task path, since `dag-inline-panels` and `dag-global-tab` will reuse it for their clickable nodes. Wire the Kanban cards to this function (replace or keep the `showTreeAndExpand` call site as appropriate).

This task ships the Kanban half of the workstream; do not touch the DAG views here — they are the sibling tasks.

## Validation

- Clicking any Kanban card switches to the tree view and opens that exact task, expanded, with its rendered markdown details visible (not just a highlighted collapsed row).
- The reveal works for a deeply nested task (ancestors all expand) and for a root-level task.
- The function is reusable by path from outside the Kanban (so the DAG tasks can call it) — confirm by calling it from the browser console with a known task path.
- Serve the dashboard (`bash .plan/serve`) and confirm in both light and dark themes.
