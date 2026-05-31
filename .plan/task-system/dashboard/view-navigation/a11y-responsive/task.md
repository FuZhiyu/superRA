---
title: "Sidebar chrome (collapse/auto-hide/resize) + keyboard nav + responsive + a11y"
status: not-started
depends_on:
  - sidebar-nav
  - main-panel
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Final polish: give the sidebar production-grade chrome (collapse, auto-hide, resizable width), make the workspace keyboard-navigable, responsive on narrow screens, and accessible. Load `frontend-design:frontend-design` before touching markup or CSS — the sidebar chrome is the part the user most wants to feel polished, so spend real design effort here. Live server only; edit `skills/task-system/scripts/templates/base.html`. Runs after `sidebar-nav` and `main-panel`.

**Sidebar chrome — collapse, auto-hide, resize (desktop).** The persistent sidebar needs a real, pleasant chrome instead of a fixed-width rail:

- **Pin / unpin (auto-hide).** A pin toggle controls two modes. *Pinned:* the sidebar holds its set width and the main panel sits beside it. *Unpinned (auto-hide):* the sidebar retracts to a thin hover-rail at the screen edge (a slim strip or hamburger affordance, not zero-width); hovering the rail (or the screen edge) slides the full sidebar out as an overlay above the main panel, and it auto-hides again on mouse-leave (small grace delay) and after a navigation selection. The main panel uses the full width while the sidebar is hidden. Persist the pin state in `localStorage`.
- **Resizable width.** A drag handle on the sidebar's right edge adjusts its width (clamped to a sensible min/max), with a visible grab affordance and a smooth (non-janky) drag. Persist the chosen width in `localStorage` and restore it on load. The handle must be keyboard-operable (focusable, `←/→` to resize) and theme-aware.
- Both modes compose with the narrow-screen overlay drawer below — on a phone width the sidebar is always the drawer regardless of pin state.

Reuse existing theme tokens and transitions; keep the motion subtle and honor `prefers-reduced-motion` for the slide/auto-hide too.

**Keyboard navigation (sidebar).** Treat `#nav-tree` as a `role="tree"` with roving `tabindex` (one row focusable at a time):
- `↑` / `↓` move focus to the previous / next visible row.
- `→` expands a collapsed row (or moves into the first child); `←` collapses (or moves to parent).
- `Enter` / `Space` on the focused row calls `setActive(focusedPath)`.
- Set `aria-expanded` on parent rows, `aria-selected` on the active row, and a sensible `aria-label`.

**Responsive.** Below a narrow breakpoint, the sidebar collapses to an **overlay drawer** toggled by a button (the `⟨` collapse control becomes a hamburger): backdrop, focus trap while open, `Esc` to close, and close-on-navigate. The main panel goes full width when the drawer is closed. Verify the breadcrumb wraps gracefully and the children-DAG scrolls rather than overflowing.

**Focus & motion.** Logical focus order header → breadcrumb → active card → children-DAG; move focus to the main panel heading on `setActive` so screen-reader users land on the new content. Honor `prefers-reduced-motion` (disable expand/scroll/`reveal-flash` animations). Audit color contrast against the existing theme tokens in both light and dark.

Reuse existing theme tokens and transitions; add only what these behaviors require. Keep the htmx/router boundary intact (no `setActive` from SSE).

## Validation

- **Sidebar chrome:** unpinning retracts the sidebar to a hover-rail; hovering the rail/edge slides the full sidebar out as an overlay and it auto-hides on mouse-leave and after a selection; pinning restores the side-by-side layout. The right-edge drag handle resizes the sidebar within its clamp, the width persists across reload, and the handle is keyboard-resizable. Pin state + width survive reload.
- With the mouse unused: Tab to the sidebar, arrow through rows, expand/collapse with `←/→`, and `Enter` to open a node in the main panel; focus lands on the new content heading.
- `aria-expanded` / `aria-selected` reflect state; the tree exposes `role="tree"`/`treeitem` to the accessibility tree (verify via the browser a11y inspector or a headless snapshot).
- At a narrow viewport the sidebar becomes an overlay drawer with backdrop, focus trap, `Esc`-close, and close-on-navigate (regardless of pin state); the main panel is full width when closed; breadcrumb and DAG don't overflow.
- `prefers-reduced-motion` disables the slide/auto-hide and other animations; contrast is acceptable in both themes.
- `node --check` passes; live-server drive (with a headless browser for keyboard + a11y checks where available) confirms the above with no console errors. `pytest skills/task-system/scripts/test_task_system.py` still passes.

## Revision Notes

**2026-05-30 — scope addition (user).** After seeing the working sidebar, the user asked for a better-designed nav bar: hover-to-reveal / auto-hide behavior and an adjustable (resizable) width. Folded both into this task's Sidebar-chrome section (it already owned sidebar collapse + responsive behavior) rather than adding a separate task, and retitled accordingly. Substantive but self-contained — no change to the other five tasks.
