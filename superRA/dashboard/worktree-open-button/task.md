---
title: "Open-Worktree VS Code Deep-Link Button"
status: approved
depends_on: []
---

## Objective

Add a control to the dashboard that opens the **active worktree's checkout root** in VS Code via the existing deep-link mechanism, so a researcher can jump straight into the correct worktree window (and, as a side effect, subsequent "Open task.md" clicks land in that now-focused window).

**Behavior:**

- The control is an `<a href="vscode://file/<PROJECT_ROOT>">` — the same URI handler the per-task button uses, pointed at a directory instead of a file. VS Code opens (or focuses, if already open) a window rooted at that folder.
- Use `PROJECT_ROOT` (the worktree checkout root), **not** `RESOLVED_ROOT` (the `superRA/` task subdir) — the goal is to open the whole worktree. `PROJECT_ROOT` already follows the active worktree (re-pointed from `_wtProjectRoots[activeId]` when the worktree list loads, `base.html` ~4457-4459).
- The href must update when the active worktree changes (same code paths that re-point `PROJECT_ROOT`).

**Placement:** In the top header, next to the worktree selector (`#worktree-selector`, `base.html:1785`). It must **not** be gated by the selector's "hide when ≤1 worktree" logic (`populateWorktreeSelector`, `base.html:4392-4396`) — opening the worktree is useful with a single worktree too. Show it whenever the local deep-link target is valid: not `STANDALONE`, not doc-mode, and not `REPO_FILE_BASE` (GitHub-file mode has no local folder to open — mirror how the per-task button switches to GitHub in that mode).

**Reuse, don't duplicate:** factor the `vscode://file/` + path construction so the folder link and the existing `taskFileVscodeHref` share one code path where reasonable; match the existing VS Code button's styling (`.vscode-btn`) and icon.

**Success criteria:**

- With multiple worktrees, the button href resolves to the active worktree's checkout root and updates on `?wt=` switch.
- With a single worktree, the button is still visible and correct.
- In doc-mode / standalone / `REPO_FILE_BASE` mode, the button is hidden.
- Verify on the real rendered page (serve the dashboard, inspect the emitted `href` and click behavior), not just a unit assertion — per the "verify the real user path for UI" discipline.
- Extend `test_dashboard.py` (or the appropriate existing test) to cover href construction and the visibility conditions.

## Planner Guidance

The existing per-task button lives in the active-node card header (`loadActiveNode`, `base.html` ~2966-2994) and uses `taskFileVscodeHref` (~2926-2932). The worktree button is a header-level (global) control, so it pairs with the worktree selector rather than the per-task card. Keep the CSS additions minimal and consistent with `.vscode-btn`.

## Results

Added an "Open worktree in VS Code" header control that deep-links the active worktree's checkout root (`PROJECT_ROOT`) as a folder, alongside the existing per-task "Open task.md" button. All changes are in [base.html](../../../skills/task-tree/scripts/templates/base.html).

**Shared URI builder.** Factored the one place `vscode://file/` is composed into a helper `vscodeFileUri(absPath)` ([base.html:2934-2936](../../../skills/task-tree/scripts/templates/base.html#L2934)); `taskFileVscodeHref` now calls it for the local branch ([base.html:2947](../../../skills/task-tree/scripts/templates/base.html#L2947)) and the folder link calls it with `PROJECT_ROOT`. The GitHub-branch and in-body-markdown link paths are untouched (out of scope; keeps their guard tests green).

**Button.** A `<a class="vscode-btn" id="worktree-open-btn">` sits in the header immediately after `#worktree-selector`, inside the same `{%- if not standalone %}` block ([base.html:1797-1798](../../../skills/task-tree/scripts/templates/base.html#L1797)). It carries the shared `.vscode-btn` class (icon + hover styling), with one override `#worktree-open-btn { margin-left: 0; }` ([base.html:349](../../../skills/task-tree/scripts/templates/base.html#L349)) dropping the per-task button's `margin-left:auto` so it sits inline by the selector. Because it is a *sibling* of `#worktree-selector` (not a child), `populateWorktreeSelector`'s "≤1 worktree → hide" never touches it — visible with a single worktree too.

**Href updating + visibility.** `updateWorktreeOpenHref()` ([base.html:4455-4463](../../../skills/task-tree/scripts/templates/base.html#L4455)) fills the icon/label once, sets `href = vscodeFileUri(PROJECT_ROOT)`, and reveals the button; it hides the button when `REPO_FILE_BASE` is set (GitHub-file mode has no local folder to open). It is called (a) once at module init off the baked-in `PROJECT_ROOT` before the fetch resolves, and (b) inside `fetchWorktrees`' `.then` after `PROJECT_ROOT` is re-pointed — the same path that fires on initial load, `?wt=` navigation, and in-app selector switches. Doc-mode hides it via the pre-existing shared `html[data-doc-mode] .vscode-btn` rule (the button carries that class); standalone omits it via the template block.

**Verification (real rendered page).** Served this worktree's tree with a live dashboard on port 8971 and drove it with headless Chromium (Playwright):

- Fresh launch load: button visible (`display:flex`, `offsetParent` non-null), label "Worktree", VS Code SVG present, `href == vscode://file/<PROJECT_ROOT>` where `PROJECT_ROOT` is the checkout root (`.../dashboard-vscode-worktree`, **not** the `superRA/` subdir).
- `?wt=<other>` fresh load: `href` re-points to the other worktree's checkout root and differs from the launch href.
- In-app selector switch: `href` follows to the selected worktree's checkout root.

**Tests** (`test_dashboard.py`): new `TestWorktreeOpenButton` (6 tests) covers live-page render, sibling-not-child placement, `PROJECT_ROOT`-via-shared-builder href, `REPO_FILE_BASE` hide, refresh-on-worktree-change wiring, doc-mode shared-rule hide, and standalone omission. Updated `test_builders_use_resolved_root_not_hardcoded_superra` to assert the new `vscodeFileUri` factoring. Full related suite: 18 passed (`-k "WorktreeOpenButton or FileLinkConsistency or WorktreeRootFollowing or test_generate_has_no_live_server_calls or builders_use_resolved_root"`).
