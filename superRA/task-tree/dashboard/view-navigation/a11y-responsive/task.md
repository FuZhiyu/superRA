---
title: "Sidebar chrome (collapse/auto-hide/resize) + keyboard nav + responsive + a11y"
status: approved
depends_on:
  - sidebar-nav
  - main-panel
tags: []
created: 2026-05-30
---

## Objective

Final polish: give the sidebar production-grade chrome (collapse, auto-hide, resizable width), make the workspace keyboard-navigable, responsive on narrow screens, and accessible. Load `frontend-design:frontend-design` before touching markup or CSS — the sidebar chrome is the part the user most wants to feel polished, so spend real design effort here. Live server only; edit `skills/task-tree/scripts/templates/base.html`. Runs after `sidebar-nav` and `main-panel`.

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

## Results

> **Superseded for touch (2026-06-04):** the unpinned hover-reveal rail and the width-only (`innerWidth <= 860`) mode selection described below were desktop-mouse-centric and unreachable/incorrect on touch devices. They are reworked into a capability- and orientation-aware model (pinned-or-drawer, never hover on touch) by [`task-tree/dashboard/mobile-ipad-ui`](../../mobile-ipad-ui/task.md). The desktop mouse behavior recorded here is unchanged.

All work is in [`base.html`](../../../../../skills/task-tree/scripts/templates/base.html) (live server only; +783/-11). Every addition is presentation/a11y layered on top of the existing router, sidebar load/fold/search, main-panel loaders, and SSE model — none of that working navigation logic was touched. The five prior tasks' code is untouched; the only behavioral edits to existing functions are additive hooks (a chrome auto-hide call in `setActive`, ARIA syncing in the nav fold/expand/load helpers, a focus-to-heading line in `loadActiveNode`).

### Sidebar chrome — pin/unpin auto-hide + resizable width (the user-priority piece)

The sidebar is restructured so a single GPU-friendly `transform` drives every mode, which is what keeps pin/unpin/drawer smooth rather than janky. `#nav-tree` (the `role="tree"` scroll region) now lives inside an `.nav-tree` box (`#sidebar`) that is **absolutely positioned** within the relatively-positioned `.workspace`; a separate `.sidebar-spacer` reserves the layout width the detail panel flows beside, and the sidebar slides *over* that reservation. Three modes are set by one class on `.workspace`:

- **`.sb-pinned`** — spacer = `--sidebar-width`, sidebar flush at `translateX(0)`. Side-by-side, the default.
- **`.sb-unpinned`** — spacer = `--rail-width` (16px), sidebar retracted via `translateX(-(width - rail))` so only a thin strip peeks. A decorative, pointer-transparent `.sidebar-rail` (grip-dot cue, accent on hover) sits over the peek; the retracted sidebar's own visible edge is the hover target (`mouseenter` → `revealSidebar`). Reveal adds `.sb-revealed` → `translateX(0)` as an overlay above the detail panel with a lifting shadow; `mouseleave` calls `hideSidebar()` with a ~220ms grace delay, and a navigation selection calls `hideSidebar(0)` (via `onNavigationChrome`). Main panel uses full width while retracted.
- **`.sb-drawer`** — narrow screens (see Responsive); pin state is ignored there.

A pin toggle (theme-aware inline-SVG pushpin that inherits `currentColor`, tilts 45° when unpinned, hidden in drawer mode) flips the mode; pin state persists in `localStorage['dashboard-sidebar-pinned']`. The width is a live `--sidebar-width` custom property on `.workspace`, clamped 200–480px, persisted in `localStorage['dashboard-sidebar-width']` and restored on load. The right-edge `.sidebar-resizer` is a `role="separator"` button: pointer-drag sets width = cursor-X relative to the workspace (transitions disabled mid-drag via `.sb-resizing` so it tracks the cursor 1:1), and it is keyboard-operable — `←/→` nudge ±16px (±48 with Shift), `Home`/`End` jump to the clamp bounds — with `aria-valuenow` kept in sync.

### Keyboard navigation — `role="tree"` + roving tabindex

`applyTreeAria()` (re-run after every `/nav` and lazy `/nav/{path}` injection, and after each active-row change) stamps the injected rows: `role="treeitem"`, `role="group"` on `.task-children`, `aria-level` from nesting depth, `aria-expanded` on parents, and a meaningful `aria-label` (`"<slug> — <title>, <status>"`). `refreshRovingTabindex()` keeps exactly one row `tabindex="0"` (the active row if visible, else the first visible row); all others are `-1`. `initTreeKeyboard()` delegates keydown from `#nav-tree`: `↑/↓` move among *visible* rows, `→` expands (lazy-loads) or steps into the first child, `←` collapses or moves to the parent row, `Enter`/`Space` call `setActive`, `Home`/`End` jump to first/last visible. `aria-selected` is set on the active row by `updateSidebar` and `aria-expanded` is kept current by `toggleNavCaret`/`expandNavNode`/`setNavFold`.

### Responsive overlay drawer

Below an 860px breakpoint JS adds `.sb-drawer` (spacer = 0, sidebar becomes a `position:fixed` off-canvas drawer, `width: min(--sidebar-width, 86vw)`), and a header hamburger appears. `openDrawer`/`closeDrawer`/`toggleDrawer` manage `.sb-drawer-open` → slide-in + fade-in backdrop (a `.sidebar-backdrop` inside `.workspace` so the mode class reaches it); a focus trap (`drawerKeydown` cycles Tab/Shift+Tab within the drawer, `Escape` closes), focus moves into the drawer on open and restores to the hamburger on close, and any navigation closes it (`onNavigationChrome`). The header is also tightened on narrow widths so it never forces horizontal scroll: it wraps under 860px, and under 620px the verbose summary stats / search / status-filter are hidden (title + hamburger + view toggle + theme control stay). The breadcrumb already wraps (`flex-wrap`); the children-DAG scrolls (`overflow-x:auto`) rather than overflowing.

### Focus & motion

`setActive` sets a one-shot `_moveFocusOnLoad` flag only on user-initiated navigation (`!restoring`, so initial load and `popstate` restores never steal page focus); `loadActiveNode` consumes it to move focus to the new card heading (`tabindex="-1"`, `focus({preventScroll:true})`) once it paints, and clears it so SSE re-renders of the same card never yank focus — preserving the clean htmx/router boundary (no `setActive` from the server channel). A `@media (prefers-reduced-motion: reduce)` block collapses all transition/animation durations to ~0 (covering the sidebar slide/auto-hide/drawer/resize, `reveal-flash`, node fade-in, and section expand/collapse). The new keyboard focus ring uses `:focus-visible` with the `--accent` token.

### Also fixed

The stale comment in `switchWorktree` ([base.html](../../../../../skills/task-tree/scripts/templates/base.html)) that still claimed the worktree switch triggers `location.reload()` — corrected to describe the actual in-place sidebar rebuild + `setActive` that `onFullReload` now performs.

### Verification

- `node --check` on the extracted client JS: **passes**.
- `pytest test_task_tree.py test_dashboard.py`: **209 passed** (152 + 57, baseline intact).
- Headless Chromium (Playwright) drive on the live server at 1280px and at 480/420px: **36/36 behavioral checks pass**, exercising every Validation point — tree ARIA (`role=tree`/`treeitem`/`group`, `aria-level`, `aria-expanded` flipping on collapse, exactly one `aria-selected` + one roving-tabbable row, verified via DOM ARIA snapshot), keyboard expand/descend/activate with focus landing on the heading, pin/unpin → rail → hover-reveal → mouse-leave auto-hide → re-pin, keyboard + pointer resize with `localStorage` persistence surviving reload, pin-state surviving reload, narrow drawer (backdrop, focus-trap-into-drawer, `Esc`-close, close-on-navigate, no horizontal overflow), and `prefers-reduced-motion` collapsing the sidebar transition to ~0. **No console errors during normal operation** (confirmed in a no-reload exercise of all chrome); the only error the harness surfaces is htmx's SSE-extension logging the `EventSource` disconnect when Playwright reloads the page mid-session — a test-harness artifact, not a page defect.
- Contrast audited against theme tokens in both themes: pin icon and focus ring 4.57:1 (light) / 5.2:1 (dark) — exceed the 3:1 non-text bar; tree titles 5.05/5.68; the sidebar `TASKS` label was moved from `--text-mute` (2.51) to `--text-mid` (5.05/5.68) to clear AA.

## Validation

- **Sidebar chrome:** unpinning retracts the sidebar to a hover-rail; hovering the rail/edge slides the full sidebar out as an overlay and it auto-hides on mouse-leave and after a selection; pinning restores the side-by-side layout. The right-edge drag handle resizes the sidebar within its clamp, the width persists across reload, and the handle is keyboard-resizable. Pin state + width survive reload.
- With the mouse unused: Tab to the sidebar, arrow through rows, expand/collapse with `←/→`, and `Enter` to open a node in the main panel; focus lands on the new content heading.
- `aria-expanded` / `aria-selected` reflect state; the tree exposes `role="tree"`/`treeitem` to the accessibility tree (verify via the browser a11y inspector or a headless snapshot).
- At a narrow viewport the sidebar becomes an overlay drawer with backdrop, focus trap, `Esc`-close, and close-on-navigate (regardless of pin state); the main panel is full width when closed; breadcrumb and DAG don't overflow.
- `prefers-reduced-motion` disables the slide/auto-hide and other animations; contrast is acceptable in both themes.
- `node --check` passes; live-server drive (with a headless browser for keyboard + a11y checks where available) confirms the above with no console errors. `pytest skills/task-tree/scripts/test_task_tree.py` still passes.
