---
title: "Shared reveal-in-tree navigation primitive + Kanban click-through"
status: approved
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
- Serve the dashboard (`python skills/task-system/scripts/plan_dashboard.py serve --root .plan`) and confirm in both light and dark themes.

## Results

Replaced the old `showTreeAndExpand(path)` in [base.html](../../../../../skills/task-system/scripts/templates/base.html) with a clearly-named, generally-callable `revealTask(path)` primitive (plus a thin `showTreeAndExpand` back-compat alias) and pointed the Kanban cards in [kanban.html](../../../../../skills/task-system/scripts/templates/kanban.html) at `revealTask` directly.

### The real gap in the old function
The previous `showTreeAndExpand` switched to the tree view, expanded ancestor *and* target task **bodies**, and scrolled to the target — but it never opened the target's per-section detail blocks. Each `## Objective` / `## Results` section is a separate collapsed `.section-content` whose markdown is lazy-rendered only on `toggleSection`, so the reader landed on a task body showing only one-line section *previews*, not rendered content. Second gap: for a deeply nested target (depth ≥ 3, lazy-loaded children) it fired the ancestor htmx loads without awaiting them, so the target node and its sections could be absent from the DOM when the scroll/expand ran.

### What `revealTask(path)` now does
1. `showView('tree')`.
2. Walks each path segment, expanding ancestors; `await`s `htmx.ajax(...)` on any ancestor with `data-needsLoad` so the next segment exists before descending — this fixes the deep-nesting race.
3. Calls a new `expandTaskDetails(node)` helper that opens the target's body and every `[data-section]` block, rendering each section's markdown via the existing `renderMarkdown(...)` path (mirrors `toggleSection`'s lazy-render, guarded by `dataset.rendered`).
4. `scrollIntoView({block:'center'})` and applies a brief `reveal-flash` highlight (new `@keyframes revealPulse`, theme-aware via existing `--accent` / `--accent-soft` vars, so it adapts to dark/light with no extra CSS).

`revealTask` is async and keyed purely by task path, callable from any view or the console — the two sibling DAG tasks reuse it unchanged. `showTreeAndExpand(path)` remains as `return revealTask(path)` so no other call site breaks.

### Verification
- JS syntax: extracted the main script block from the served page and `node --check` passed.
- Functional (Playwright, headless Chromium against the live `serve` server):
  - **Deep nested** (`task-system/dashboard/view-navigation/navigate-to-task`, depth 4, lazy-loaded) via `revealTask(...)` from the console — tree shown, all 3 ancestors expanded, target body open, sections rendered, zero JS errors.
  - **Root-level leaf** (`figure-attachments`) via an actual Kanban card click — tree shown, body open, markdown rendered, `reveal-flash` applied, zero JS errors.
- `~/.venv/bin/python -m pytest skills/task-system/scripts/test_task_system.py` — 143 passed.

The `## Validation` line references `bash .plan/serve`, but no such script exists in this tree; the dashboard is launched with `python skills/task-system/scripts/plan_dashboard.py serve --root .plan` (flags are `--root` / `--port` / `--no-open`, not `--plan-root`).
