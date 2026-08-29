---
title: "Touch-Resizable Sidebar on iPad and Other Coarse-Pointer Devices"
status: revise
depends_on: []
---

## Objective

On a touch device (iPad, phone) the dashboard sidebar cannot be resized: the drag handle is hidden by `.sb-touch .sidebar-resizer { display: none; }` and `initSidebarResizer` refuses `pointerdown` when `sbIsTouch()`, so the sidebar stays at the 280px default (or `min(280px, 86vw)` in drawer mode) and ellipsized nav rows hide most of every long task title. Make the sidebar width adjustable by touch in both the pinned landscape layout and the open drawer: keep the resizer visible on `.sb-touch` with a touch-sized hit area and `touch-action: none`, accept coarse-pointer drags, position the handle on the open drawer's right edge and clamp there to the drawer's `86vw` cap, and persist the chosen width as on desktop. Keep the fine-pointer path unchanged. Verify in the test suite (`test_dashboard.py` touch-sidebar tests) and on a real iPad against the TreasuryGIV-code tree served over the Tailscale interface.

## Details

Files: `skills/task-tree/scripts/templates/dashboard.css` (§Resize drag handle, §Narrow-screen overlay drawer), `dashboard.js` (§Sidebar chrome, `initSidebarResizer`), `test_dashboard.py` (touch-aware sidebar template assertions around line 1858). Run the suite per repo CLAUDE.md §Local Task-Tree CLI Development.

## Results

Touch devices can now drag the sidebar edge in both the pinned landscape layout and the open drawer.

- [dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css) §Resize drag handle: `.sb-touch .sidebar-resizer` is a 24px strip with `touch-action: none` and an always-visible grip pill; `.sb-drawer.sb-drawer-open .sidebar-resizer` fixes the handle on the open drawer's edge at `min(--sidebar-width, 86vw)`.
- [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js) `initSidebarResizer`: the coarse-pointer and narrow-width refusals are gone; the handle captures the pointer for the drag, measures from the viewport edge in drawer mode, and `clampSidebarWidth` caps at `0.86 * innerWidth` while a drawer; `applySidebarMode` re-clamps the persisted width on mode change.
- Verification: `test_dashboard.py` template assertions updated (`TestTouchSidebar`); a Playwright touch drive (iPad 1024×768 pinned and 768×1024 drawer, `is_mobile`, `has_touch`) dragged the handle 280→400px in both modes with the width persisted to `localStorage` and the drawer staying open. The 20 `TestBackgroundLaunch`/idle-shutdown failures are sandbox process restrictions and fail identically on `main`.
- Preference vs. shown width: `sbWidth` is the user's choice (drag, keyboard, `localStorage`); `renderSidebarWidth` paints `clampSidebarWidth(sbWidth)` on every mode change and syncs `aria-valuemax` from `sidebarWidthMax`, so a drawer's 86vw cap narrows the display only and the choice returns intact on rotation. Behavioral coverage: `TestSidebarResizeBrowser` in [test_artifact_ui.py](../../../../skills/task-tree/scripts/test_artifact_ui.py) (touch drag 280→400, 400px drawer clamp to 344 with `sbWidth` still 400, restore at 1024px).
- Asset cache-busting: `index` renders `dashboard.css`/`dashboard.js` URLs with `?v=<12-hex content hash>` ([plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py) `_asset_version`), because iPad Safari reused the hour-cached assets without revalidating and never received the fix on reload.
- Not covered: nav rows still ellipsize slug, title, and badge on one line, so a wide sidebar still hides part of a long title; wrapping touch rows is a separate design change.

## Review Notes

Tier: thorough. Focus: correctness, fine-pointer/desktop regressions, test coverage. Verified by the dashboard suite plus a Playwright drive (chromium, `is_mobile`/`has_touch`) over a standalone export at 1024×768, 768×1024, 390×844, and desktop 1400×900/500×900.

1. **[BLOCKING]** The mode re-clamp overwrites the user's persisted width, so every trip through drawer mode permanently narrows the sidebar. [dashboard.js:2700-2701](../../../../skills/task-tree/scripts/templates/dashboard.js#L2700-L2701) passes the clamped value to [`applySidebarWidth`](../../../../skills/task-tree/scripts/templates/dashboard.js#L2648), which assigns the global `sbWidth` — the same variable that is the stored preference and the value [`persistSidebarWidth`](../../../../skills/task-tree/scripts/templates/dashboard.js#L2864-L2866) writes back. Drive result: `localStorage` = 480, viewport 1400 → 500 (drawer, cap `floor(0.86*500)` = 430) → `sbWidth` 430; back to 1400 → still 430, `localStorage` still 480. The iPad rotation path is the same, and on a 390px phone the cap (335) binds on every load, so the first subsequent drag or ←/→ nudge writes the phone-sized width over the user's choice. Fix: clamp at apply time only — keep the chosen width in its own variable and let the mode set the CSS custom property from `clampSidebarWidth(pref)` without reassigning the preference.

2. **[ADVISORY]** `aria-valuemax` stays at the desktop `480` in drawer mode, where the reachable max is `floor(0.86 * innerWidth)` — 335 on a 390px phone. [base.html:194](../../../../skills/task-tree/scripts/templates/base.html#L194) hard-codes it and `applySidebarWidth` syncs only `aria-valuenow`; sync `aria-valuemax` from the same clamp.

3. **[ADVISORY]** The mode-class comment still says `.sb-touch` "disables the mouse-only chrome (hover-rail, drag-resizer)" ([dashboard.css:558-559](../../../../skills/task-tree/scripts/templates/dashboard.css#L558-L559)); the drag-resizer is now the touch path's main affordance.

4. **[ADVISORY]** The new coverage is source-string matching (`assert "window.innerWidth * 0.86" in BASE_HTML`, [test_dashboard.py:1900](../../../../skills/task-tree/scripts/test_dashboard.py#L1900)), which survives any rename of the expression and asserts nothing about behavior. Finding 1 reproduces in ~15 lines on the existing Playwright harness ([test_artifact_ui.py](../../../../skills/task-tree/scripts/test_artifact_ui.py)); a drawer-clamp + width-restore case there would hold the fix.

5. **[ADVISORY]** This file now carries two `## Results` headings — an empty one at line 15 and the filled one at line 18. Delete the empty heading.
