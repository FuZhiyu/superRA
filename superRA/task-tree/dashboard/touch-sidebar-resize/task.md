---
title: "Touch-Resizable Sidebar on iPad and Other Coarse-Pointer Devices"
status: approved
depends_on: []
---

## Objective

On a touch device (iPad, phone) the dashboard sidebar cannot be resized: the drag handle is hidden by `.sb-touch .sidebar-resizer { display: none; }` and `initSidebarResizer` refuses `pointerdown` when `sbIsTouch()`, so the sidebar stays at the 280px default (or `min(280px, 86vw)` in drawer mode) and ellipsized nav rows hide most of every long task title. Make the sidebar width adjustable by touch in both the pinned landscape layout and the open drawer: keep the resizer visible on `.sb-touch` with a touch-sized hit area and `touch-action: none`, accept coarse-pointer drags, position the handle on the open drawer's right edge and clamp there to the drawer's `86vw` cap, and persist the chosen width as on desktop. Keep the fine-pointer path unchanged. Verify in the test suite (`test_dashboard.py` touch-sidebar tests) and on a real iPad against the TreasuryGIV-code tree served over the Tailscale interface.

## Details

Files: `skills/task-tree/scripts/templates/dashboard.css` (§Resize drag handle, §Narrow-screen overlay drawer), `dashboard.js` (§Sidebar chrome, `initSidebarResizer`), `test_dashboard.py` (touch-aware sidebar template assertions around line 1858). Run the suite per repo CLAUDE.md §Local Task-Tree CLI Development.

## Results

Touch devices can now drag the sidebar edge in both the pinned landscape layout and the open drawer.

- [dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css) §Resize drag handle: `.sb-touch .sidebar-resizer` is a 24px strip with `touch-action: none` and an always-visible grip pill; `.sb-drawer.sb-drawer-open .sidebar-resizer` fixes the handle on the open drawer's edge at `min(--sidebar-width, 86vw)`.
- [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js) `initSidebarResizer`: the coarse-pointer and narrow-width refusals are gone; the handle captures the pointer for the drag, measures from the viewport edge in drawer mode, and `clampSidebarWidth` caps at `0.86 * innerWidth` while a drawer.
- Verification: `test_dashboard.py` template assertions updated (`TestTouchSidebar`); a Playwright touch drive (iPad 1024×768 pinned and 768×1024 drawer, `is_mobile`, `has_touch`) dragged the handle 280→400px in both modes with the width persisted to `localStorage` and the drawer staying open. The 20 `TestBackgroundLaunch`/idle-shutdown failures are sandbox process restrictions and fail identically on `main`.
- Preference vs. shown width: `sbWidth` is the user's choice (drag, keyboard, `localStorage`); `renderSidebarWidth` paints `clampSidebarWidth(sbWidth)` on every mode change and syncs `aria-valuemax` from `sidebarWidthMax`, so a drawer's 86vw cap narrows the display only and the choice returns intact on rotation. Behavioral coverage: `TestSidebarResizeBrowser` in [test_artifact_ui.py](../../../../skills/task-tree/scripts/test_artifact_ui.py) (touch drag 280→400, 400px drawer clamp to 344 with `sbWidth` still 400, restore at 1024px).
- Asset cache-busting: `index` renders `dashboard.css`/`dashboard.js` URLs with `?v=<12-hex content hash>` ([plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py) `_asset_version`), because iPad Safari reused the hour-cached assets without revalidating and never received the fix on reload.
- Not covered: nav rows still ellipsize slug, title, and badge on one line, so a wide sidebar still hides part of a long title; wrapping touch rows is a separate design change.
