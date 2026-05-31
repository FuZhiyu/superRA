---
title: "Keyboard nav, responsive drawer, a11y polish"
status: not-started
depends_on:
  - sidebar-nav
  - main-panel
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Final polish: make the workspace keyboard-navigable, responsive on narrow screens, and accessible. Load `frontend-design:frontend-design` before touching markup or CSS. Live server only; edit `skills/task-system/scripts/templates/base.html`. Runs after `sidebar-nav` and `main-panel`.

**Keyboard navigation (sidebar).** Treat `#nav-tree` as a `role="tree"` with roving `tabindex` (one row focusable at a time):
- `↑` / `↓` move focus to the previous / next visible row.
- `→` expands a collapsed row (or moves into the first child); `←` collapses (or moves to parent).
- `Enter` / `Space` on the focused row calls `setActive(focusedPath)`.
- Set `aria-expanded` on parent rows, `aria-selected` on the active row, and a sensible `aria-label`.

**Responsive.** Below a narrow breakpoint, the sidebar collapses to an **overlay drawer** toggled by a button (the `⟨` collapse control becomes a hamburger): backdrop, focus trap while open, `Esc` to close, and close-on-navigate. The main panel goes full width when the drawer is closed. Verify the breadcrumb wraps gracefully and the children-DAG scrolls rather than overflowing.

**Focus & motion.** Logical focus order header → breadcrumb → active card → children-DAG; move focus to the main panel heading on `setActive` so screen-reader users land on the new content. Honor `prefers-reduced-motion` (disable expand/scroll/`reveal-flash` animations). Audit color contrast against the existing theme tokens in both light and dark.

Reuse existing theme tokens and transitions; add only what these behaviors require. Keep the htmx/router boundary intact (no `setActive` from SSE).

## Validation

- With the mouse unused: Tab to the sidebar, arrow through rows, expand/collapse with `←/→`, and `Enter` to open a node in the main panel; focus lands on the new content heading.
- `aria-expanded` / `aria-selected` reflect state; the tree exposes `role="tree"`/`treeitem` to the accessibility tree (verify via the browser a11y inspector or a headless snapshot).
- At a narrow viewport the sidebar becomes an overlay drawer with backdrop, focus trap, `Esc`-close, and close-on-navigate; the main panel is full width when closed; breadcrumb and DAG don't overflow.
- `prefers-reduced-motion` disables the animations; contrast is acceptable in both themes.
- `node --check` passes; live-server drive (with a headless browser for keyboard + a11y checks where available) confirms the above with no console errors. `pytest skills/task-system/scripts/test_task_system.py` still passes.
