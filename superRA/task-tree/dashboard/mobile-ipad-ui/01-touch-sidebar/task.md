---
title: "Touch-aware sidebar model + iPad breakpoints"
status: approved
depends_on:  []
tags: []
created: 2026-06-04
---

## Objective

Make the sidebar reachable and correct on every touch device, choosing its mode by input capability and orientation rather than raw viewport width. This is the highest-risk piece — settle it before the polish pass.

The current model (in [`base.html`](../../../../../skills/task-tree/scripts/templates/base.html)) has three modes set on `.workspace`: `.sb-pinned` (side-by-side), `.sb-unpinned` (retracted to a hover-rail, revealed on `mouseenter`), and `.sb-drawer` (off-canvas, below `innerWidth <= 860`). `applySidebarMode()` and `sbIsNarrow()` drive it from width alone, and the reveal is wired through `mouseenter`/`mouseleave` on `#sidebar`. On touch, the unpinned mode is a dead end.

**Required behavior:**

- **Capability detection.** Add a touch / coarse-pointer check via `matchMedia('(hover: none)')` and/or `'(pointer: coarse)'`, re-evaluated on `change` (an iPad gains/loses a pointer when a trackpad keyboard attaches). On a fine-pointer + hover device, nothing changes — the existing pinned/unpinned/drawer model and all its handlers behave exactly as today.
- **Never hover-reveal on touch.** On a coarse / no-hover device the `.sb-unpinned` hover-reveal state must never be entered — it is unreachable by tap. The pin toggle on touch switches between **pinned (persistent)** and **drawer**, not pinned/auto-hide; relabel/retitle it accordingly on touch.
- **Mode by capability + orientation, not width alone.** For touch devices, replace the pure `innerWidth <= 860` decision:
  - **Touch + landscape with room** (wide enough for the side-by-side layout) → **persistent pinned sidebar** with a visible, tap-sized control to collapse it to the drawer (and reopen).
  - **Touch + portrait, or touch + narrow** → the existing off-canvas **drawer**, toggled by the header hamburger. Resolve the 1024px-portrait iPad correctly: a 12.9" iPad in portrait (1024×1366) must get touch behavior, not desktop hover chrome — key off `matchMedia('(orientation: portrait)')` and/or `(pointer: coarse)` so a 1024px *portrait* width is treated as a tablet, while a true 1024px desktop window keeps its mouse chrome.
  - **Mouse/desktop path unchanged:** `innerWidth <= 860` → drawer; otherwise pinned/unpinned per the stored pin state, with hover-reveal intact.
- **Disable mouse-only chrome on touch.** The decorative hover-rail (`.sidebar-rail`), the `mouseenter`/`mouseleave` reveal/hide handlers, and the 7px drag-resizer are inert or hidden on touch (the resizer is already guarded in drawer mode — extend the guard to all touch). Persisted pin/width state still restores; it simply can't drive a hover mode on touch.
- **viewport-fit + safe areas for header/drawer.** Set `viewport-fit=cover` on the viewport `<meta>`, and pad the off-canvas drawer and the fixed header with `env(safe-area-inset-*)` so they clear the notch, home indicator, and rounded corners on iOS (drawer top/bottom/left; header top/left/right). Content-area insets for the detail panel belong to `02-touch-polish`.
- **Drawer touch ergonomics.** Confirm on a real touch context that the drawer opens/closes by tapping the hamburger and the backdrop, that `Esc`/close-on-navigate still fire, and the focus trap still behaves. A swipe-from-left-edge-to-open / swipe-to-close gesture is a nice-to-have — add it only if it stays simple and doesn't fight the tree's vertical scroll.

**Validation:** With Playwright touch contexts (iPhone; iPad portrait 768 and 1024; iPad landscape 1024 and 1366):

- The correct mode class is on `.workspace` for each size/orientation, and **no `.sb-unpinned` / `.sb-revealed` state is ever present on a touch context**.
- The sidebar is reachable and operable by tap in every case; tapping the hamburger opens the drawer and tapping the backdrop closes it.
- The persistent-pinned iPad-landscape sidebar collapses to the drawer via its tap control and reopens.
- On a desktop **mouse** context the mode classes, hover-reveal, auto-hide, and the resizer behave exactly as before (no regression).
- `cd skills/task-tree/scripts && pytest test_dashboard.py test_task_tree.py` stays green; `node --check` on the extracted client JS passes.

## Planner Guidance

- The reveal/hide and mode plumbing lives around `applySidebarMode`, `sbIsNarrow`, `revealSidebar`, `hideSidebar`, and `initSidebarChrome` in `base.html` (≈ lines 2585–2700). The CSS mode rules are at ≈ lines 250–405.
- Prefer a small `sbIsTouch()` helper (cached `matchMedia` result + `change` listener) and route `applySidebarMode()` through it, rather than sprinkling capability checks at call sites — that keeps the desktop path literally unchanged and the touch path in one place.
- A clean framing: on touch, the pin toggle's two states map to `pinned` ↔ `drawer` (not `pinned` ↔ `unpinned`), and `applySidebarMode` picks `pinned`-vs-`drawer` from orientation/room instead of `narrow`.

## Results

The sidebar is now reachable and mode-correct on every touch device, choosing its mode by input capability and orientation instead of raw viewport width. The desktop mouse path is byte-for-byte unchanged in effect — all touch behavior is additive and guarded by a single capability check. Everything lives in the one dashboard source, [`base.html`](../../../../../skills/task-tree/scripts/templates/base.html); the live server and the static export render it identically.

### What changed

**Capability + orientation detection (one place, cached + reactive).** Added `sbIsTouch()` (cached `matchMedia('(hover: none), (pointer: coarse)')`) and `sbIsPortrait()` (cached `matchMedia('(orientation: portrait)')`), each re-evaluated via a `change` listener registered in `initSidebarChrome` (with an `addListener` fallback for older Safari). An iPad that gains/loses a trackpad pointer, or is rotated, re-runs `applySidebarMode()` automatically. ([base.html JS, sbIsTouch/sbIsPortrait/sbTouchWantsDrawer](../../../../../skills/task-tree/scripts/templates/base.html))

**`applySidebarMode()` rewritten as two disjoint paths.** Per the planner's clean framing, the function routes through `sbIsTouch()`:
- **Touch:** never `.sb-unpinned` (`unpinned = false` hard-set — the hover-reveal is unreachable by tap). `sbTouchWantsDrawer()` picks drawer when portrait, narrow, below the side-by-side room threshold (`SB_TOUCH_PIN_MIN = 860`), or when the user collapsed it (`!sbPinned`); otherwise persistent pinned. The pin toggle's two states map to **pinned ↔ drawer**, not pinned ↔ auto-hide.
- **Mouse/desktop:** the original `narrow`-wins model, untouched — `innerWidth <= 860` → drawer; else pinned/unpinned per stored pin state with hover-reveal intact.

A new `.sb-touch` workspace class drives the touch CSS, and the drawer mode is mirrored onto `document.body` as `.sb-drawer-mode`. The body mirror is load-bearing: the hamburger lives in `.header`, which is a **sibling of** `#workspace`, so a `.sb-drawer .nav-hamburger` descendant selector can never reach it — `body.sb-drawer-mode .nav-hamburger { display: inline-flex }` shows the hamburger for a touch landscape iPad collapsed to the drawer above the 860px width media query. (This sibling/descendant trap was the one real bug found and fixed mid-implementation; it would have left the collapsed-iPad drawer unreachable.)

**1024px-portrait iPad resolved correctly.** Because the touch path keys off `(orientation: portrait)` + `(pointer: coarse)` rather than width, a 12.9" iPad at 1024×1366 portrait gets the drawer (tablet behavior), while a true 1024px desktop **window** stays non-touch and keeps its mouse chrome — both verified by Playwright.

**Mouse-only chrome disabled on touch.** Added `.sb-touch .sidebar-rail { display: none }` and `.sb-touch .sidebar-resizer { display: none }`, and guarded the resizer's `pointerdown` with `if (sbIsNarrow() || sbIsTouch()) return`. The hover `mouseenter`/`mouseleave` handlers are structurally inert on touch (they early-return unless `.sb-unpinned`, which never occurs on touch). The pin toggle is relabeled on touch via `syncPinToggle()` ("Collapse sidebar to drawer" / "Pin sidebar"), and kept reachable inside the open touch drawer (`.sb-drawer:not(.sb-touch) .pin-toggle { display: none }`) so re-pinning to the persistent layout is possible.

**viewport-fit + safe areas.** Set `viewport-fit=cover` on the viewport `<meta>`. Padded the fixed header (top/left/right) and the off-canvas drawer (top/bottom/left) with `max(<existing>, env(safe-area-inset-*))`, so the notch / home indicator / rounded corners are cleared on iOS while non-notched devices keep the exact existing padding (`env()` resolves to 0 there). The narrow-width header override was updated to preserve the safe-area floor. Detail-panel content insets are deferred to `02-touch-polish` per scope.

A swipe-to-open/close gesture (the listed nice-to-have) was **not** added — it risks fighting the tree's vertical scroll, and the brief gates it on "stays simple and doesn't fight scroll." The hamburger + backdrop + Esc fully cover drawer reachability.

### Verification (real device path, not CSS-only)

Drove the live server (`superra dashboard --foreground --no-open --port 57625`) with Playwright (Chromium, `hasTouch`/`isMobile` contexts) across the full matrix. **All 56 behavioral checks passed:**

| Context | Result |
|---|---|
| iPhone 390×844 | `.sb-drawer`, no `.sb-unpinned`/`.sb-revealed`; hamburger→open, backdrop-tap→close, Esc→close |
| iPad portrait 768×1024 | drawer; same tap/backdrop/Esc reachability |
| iPad portrait 1024×1366 (12.9") | drawer (treated as tablet, **not** desktop hover chrome) |
| iPad landscape 1024×768 | persistent `.sb-pinned`; resizer hidden; pin-tap collapses to drawer; hamburger reopens |
| iPad landscape 1366×1024 | persistent pinned; same collapse/reopen |
| desktop mouse 1024×768 | no `.sb-touch`, not drawer, pinned default; unpin→`.sb-unpinned`, hover reveals, resizer visible — unchanged |

Additional drives confirmed: rotation landscape-pinned ↔ portrait-drawer flips mode live; the focus trap moves focus into the drawer on open; desktop mouse at 840px narrow still → drawer (no regression); reduced-motion phone drawer opens/closes correctly.

`node --check` on the extracted client JS (rendered standalone HTML, largest inline `<script>`) passes.

`cd skills/task-tree/scripts && pytest test_dashboard.py test_task_tree.py` → **372 passed** (was 365; +7 cheap template-level regression tests in `TestTouchSidebar` asserting `viewport-fit=cover`, the capability/portrait media queries, the touch-never-unpinned hard-set, the `.sb-touch` chrome guards, the body-class hamburger rule, and the safe-area insets — present in both the raw template and the live render). ([test_dashboard.py TestTouchSidebar](../../../../../skills/task-tree/scripts/test_dashboard.py))

The static export (`superra dashboard export`) was spot-checked and carries all touch primitives. The generated `superRA/dashboard.html` is an untracked build artifact and is intentionally not committed.
