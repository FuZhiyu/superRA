---
title: "Touch-Resizable Sidebar on iPad and Other Coarse-Pointer Devices"
status: approved
depends_on: []
---

## Objective

On a touch device (iPad, phone) the dashboard sidebar cannot be resized: the drag handle is hidden by `.sb-touch .sidebar-resizer { display: none; }` and `initSidebarResizer` refuses `pointerdown` when `sbIsTouch()`, so the sidebar stays at the 280px default (or `min(280px, 86vw)` in drawer mode) and ellipsized nav rows hide most of every long task title. Make the sidebar width adjustable by touch in both the pinned landscape layout and the open drawer: keep the resizer visible on `.sb-touch` with a touch-sized hit area and `touch-action: none`, accept coarse-pointer drags, position the handle on the open drawer's right edge and clamp there to the drawer's `86vw` cap, and persist the chosen width as on desktop. Keep the fine-pointer path unchanged. Version the served `dashboard.css`/`dashboard.js` URLs by content so a reload after a relaunch fetches current assets instead of the hour-cached copy. Verify in the test suite (`test_dashboard.py` touch-sidebar tests) and on a real iPad against the TreasuryGIV-code tree served over the Tailscale interface.

## Details

Files: `skills/task-tree/scripts/templates/dashboard.css` (§Resize drag handle, §Narrow-screen overlay drawer), `dashboard.js` (§Sidebar chrome, `initSidebarResizer`), `test_dashboard.py` (touch-aware sidebar template assertions around line 1858). Run the suite per repo CLAUDE.md §Local Task-Tree CLI Development.

## Results

Touch devices drag the sidebar edge in both the pinned landscape layout and the open drawer; the chosen width persists and survives the drawer's cap.

- Handle: [dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css) §Resize drag handle — on `.sb-touch` a 24px strip with `touch-action: none` and a visible grip pill; on an open drawer, fixed at `min(--sidebar-width, 86vw)`.
- Drag: [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js) `initSidebarResizer` accepts coarse pointers, captures the pointer, and measures from the viewport edge in drawer mode.
- Preference vs. shown width: `sbWidth` holds the user's choice; `renderSidebarWidth` paints `clampSidebarWidth(sbWidth)` on every mode change and syncs `aria-valuemax`, so the drawer's `0.86 * innerWidth` cap narrows the display only.
- Cache: `index` appends `?v=<content hash>` to `dashboard.css`/`dashboard.js` (`_asset_version` in [plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py)); Safari otherwise reused the hour-cached assets without revalidating.
- Real-device check: the researcher confirmed the drag works on an iPad against the TreasuryGIV-code tree served over Tailscale after a plain reload (Safari `touch-action: none` and the versioned-asset reload, which chromium emulation cannot settle).
- Protection: `TestSidebarResizeBrowser` in [test_artifact_ui.py](../../../../skills/task-tree/scripts/test_artifact_ui.py) (touch drag 280→400, 400px drawer clamps to 344 with `sbWidth` 400, restore at 1024px; local-only, skips without chromium) plus `TestTouchSidebar` template assertions in `test_dashboard.py`. Release note in [RELEASE-NOTES.md](../../../../RELEASE-NOTES.md).
- Open: nav rows still ellipsize slug, title, and badge on one line, so long titles stay partly hidden at any width; an SSE full reload closes an open drawer (`onFullReload → setActive → closeDrawer`).

