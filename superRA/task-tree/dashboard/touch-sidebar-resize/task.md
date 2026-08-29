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

Touch devices drag the sidebar edge in both the pinned landscape layout and the open drawer; the chosen width persists and survives the drawer's cap.

- Handle: [dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css) §Resize drag handle — on `.sb-touch` a 24px strip with `touch-action: none` and a visible grip pill; on an open drawer, fixed at `min(--sidebar-width, 86vw)`.
- Drag: [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js) `initSidebarResizer` accepts coarse pointers, captures the pointer, and measures from the viewport edge in drawer mode.
- Preference vs. shown width: `sbWidth` holds the user's choice; `renderSidebarWidth` paints `clampSidebarWidth(sbWidth)` on every mode change and syncs `aria-valuemax`, so the drawer's `0.86 * innerWidth` cap narrows the display only.
- Cache: `index` appends `?v=<content hash>` to `dashboard.css`/`dashboard.js` (`_asset_version` in [plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py)); Safari otherwise reused the hour-cached assets without revalidating.
- Protection: `TestSidebarResizeBrowser` in [test_artifact_ui.py](../../../../skills/task-tree/scripts/test_artifact_ui.py) (touch drag 280→400, 400px drawer clamps to 344 with `sbWidth` 400, restore at 1024px; local-only, skips without chromium) plus `TestTouchSidebar` template assertions in `test_dashboard.py`. Release note in [RELEASE-NOTES.md](../../../../RELEASE-NOTES.md).
- Open: nav rows still ellipsize slug, title, and badge on one line, so long titles stay partly hidden at any width; an SSE full reload closes an open drawer (`onFullReload → setActive → closeDrawer`).

## Review Notes

Thorough integration review of `0c0b4683..48d74377` — focus: codebase fit, minimum net diff, results-writing, correctness. The touch-resize behavior holds: the suite is 329 passed / 20 known sandbox failures, all six `test_artifact_ui.py` browser tests pass with chromium, and `TestSidebarResizeBrowser` is red on the pre-fix source for the preference-loss regression itself (reverting only `applySidebarMode`'s `renderSidebarWidth` → `applySidebarWidth` fails it at `sbWidth == 400`).

1. `[BLOCKING]` **No Final Diff Self-Check trail in the integrate commits.** `git log 0c0b4683..48d74377 --format=%B | grep -i self-check` returns nothing; `a7e88528` carries the Protect record (kept/dropped results) and `48d74377` the Mature note, neither of which recomputes the governing diff or classifies the surviving hunks. `refactor-and-integrate` §Final Diff Self-Check grades a missing trail blocking, including when no code changed. Fix: land an integrate commit (empty if nothing changes) whose body carries `Final diff self-check: git diff 0c0b4683..HEAD; <objective>; <surviving and removed change classes>; <suspicious hunk justifications or none>`.

2. `[ADVISORY]` **Two docstrings in `plan_dashboard.py` now claim opposite cache behavior.** [plan_dashboard.py:1184-1186](../../../../skills/task-tree/scripts/plan_dashboard.py#L1184-L1186) still says the assets are "ETag-revalidated so an edit during development … is picked up on the next request even under the 1-hour `max-age`", which [plan_dashboard.py:1126-1132](../../../../skills/task-tree/scripts/plan_dashboard.py#L1126-L1132) contradicts twenty lines above. Fix: point `static_asset`'s docstring at the `?v=` version instead of the revalidation claim.

3. `[ADVISORY]` **The open-drawer handle reaches the fine-pointer path, with a misplaced grip line.** [dashboard.css:717-725](../../../../skills/task-tree/scripts/templates/dashboard.css#L717-L725) is not scoped to `.sb-touch`, so a desktop window under 860px now shows a 24px resizer on the open drawer where the drawer previously had none — a change the objective's "keep the fine-pointer path unchanged" clause did not ask for. It also inherits the base `::after { left: 3px; width: 1px; }`, so the hover grip line renders 9px inside the drawer rather than on its edge (measured at a 700×800 fine-pointer viewport: strip `x=268 w=24`, `::after` left `3px`). Fix: extend the `::after { left: 11px; width: 2px; }` rule to `.sb-drawer.sb-drawer-open .sidebar-resizer::after`, and confirm the desktop drawer handle is intended.

4. `[ADVISORY]` **A failed `setPointerCapture` strands the drag.** [dashboard.js:2854-2857](../../../../skills/task-tree/scripts/templates/dashboard.js#L2854-L2857) swallows a capture failure but then binds `pointermove`/`pointerup`/`pointercancel` on `rz` alone, so without capture a pointer leaving the 24px strip stops driving the drag and never delivers `pointerup` — `sb-resizing` stays on. The pre-change code bound on `window`, which does not depend on capture. Fix: bind the three listeners on `window` and keep `setPointerCapture` as the additional guarantee.

5. `[ADVISORY]` **`aria-valuenow` can exceed `aria-valuemax` on very narrow viewports.** Below roughly 233px, `sidebarWidthMax()` drops under `SB_WIDTH_MIN`, so `clampSidebarWidth` returns the floor instead (measured at 220×700: `sidebarWidthMax()` 189, `clampSidebarWidth(100)` 200), publishing an invalid ARIA range. The painted sidebar is still capped by the CSS `min()`, so this is metadata only. Fix: clamp `SB_WIDTH_MIN` against the mode max in `clampSidebarWidth`.

6. `[ADVISORY]` **Asset versioning is a second concern the `## Objective` never scopes.** `_asset_version` and the `?v=` URLs (`4355de32`) fix a real cache bug and are recorded in `## Results` and `RELEASE-NOTES.md`, but the task contract a reviewer judges against covers only the touch resizer. Fix: add a clause to `## Objective` naming the cache-busting work before the PR.

7. `[ADVISORY]` **The objective's real-iPad verification is not recorded.** `## Objective` asks for a pass "on a real iPad against the TreasuryGIV-code tree served over the Tailscale interface"; `## Results` records only the Playwright drive and template assertions. Chromium's touch emulation cannot settle the two Safari-specific parts of this change — `touch-action: none` gesture handling and `max-age` revalidation. Fix: state in `## Results` that the iPad pass happened, or that it did not.
