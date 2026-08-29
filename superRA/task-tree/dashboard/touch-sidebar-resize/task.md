---
title: "Touch-Resizable Sidebar on iPad and Other Coarse-Pointer Devices"
status: not-started
depends_on:  []
---

## Objective

On a touch device (iPad, phone) the dashboard sidebar cannot be resized: the drag handle is hidden by `.sb-touch .sidebar-resizer { display: none; }` and `initSidebarResizer` refuses `pointerdown` when `sbIsTouch()`, so the sidebar stays at the 280px default (or `min(280px, 86vw)` in drawer mode) and ellipsized nav rows hide most of every long task title. Make the sidebar width adjustable by touch in both the pinned landscape layout and the open drawer: keep the resizer visible on `.sb-touch` with a touch-sized hit area and `touch-action: none`, accept coarse-pointer drags, position the handle on the open drawer's right edge and clamp there to the drawer's `86vw` cap, and persist the chosen width as on desktop. Keep the fine-pointer path unchanged. Verify in the test suite (`test_dashboard.py` touch-sidebar tests) and on a real iPad against the TreasuryGIV-code tree served over the Tailscale interface.

## Details

Files: `skills/task-tree/scripts/templates/dashboard.css` (§Resize drag handle, §Narrow-screen overlay drawer), `dashboard.js` (§Sidebar chrome, `initSidebarResizer`), `test_dashboard.py` (touch-aware sidebar template assertions around line 1858). Run the suite per repo CLAUDE.md §Local Task-Tree CLI Development.

## Results

