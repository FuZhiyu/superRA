---
title: "Post-merge CLI fixes: create-path rollup + build-artifact gitignore"
status: approved
depends_on:
  - uv-package

tags: []
created: 2026-06-02
---

## Objective

Two loose ends from the cli-redesign merge into the task-tree CLI. Both are required for approval.

### Fix 1 — `superra task create` must roll up parent status (BLOCKING; primary)

`task_create.py:create_task` regenerates the dashboard after writing a new child but never calls `propagate_parent_status`. Adding a `not-started` child to an `approved` parent therefore leaves the parent's persisted `status: approved`, violating the task-tree invariant "a parent is `approved` only when all children are `approved`." Reproduced on this branch: `superra task create task-tree/cli-scripts/<new>` left `cli-scripts/task.md` at `approved` until `superra task status propagate` was run manually.

Required:
- `create_task` must recompute and persist the affected parent chain's status after creating the child, matching the path already used by `task_update.py` and the PostToolUse hook (`task_hook.py`) — both call `propagate_parent_status`. Reuse that same function/helper; do not invent a parallel rollup.
- Creating a `not-started` child under an `approved` parent must leave the parent (and its `approved` ancestors) `in-progress` with no manual `propagate` step.
- Add a regression test (in `scripts/test_task_tree.py` or `scripts/test_cli.py`, matching where the existing create/propagate coverage lives) that creates a child under an `approved` parent and asserts the parent's persisted `status` is no longer `approved`.

Scope note: `task_link.py` and `task_rename.py` also lack `propagate_parent_status`, but those operations do not change a parent's child-completion set (link edits sibling `depends_on`; rename is same-parent), so their rollup is unaffected — do **not** add propagation there unless you can demonstrate a status-changing case. Keep this fix to the create path.

### Fix 2 — gitignore the packaging build artifacts (BLOCKING; secondary)

Add gitignore coverage so the `superra-task-tree` package's build/install byproducts never clutter `git status` or get committed. After `uv build`, `uv tool install ./skills/task-tree`, or `uv run --project skills/task-tree ...`, `git status` must stay clean. Cover at minimum `build/`, `*.egg-info/`, and `uv.lock` generated under `skills/task-tree/`.

## Planner Guidance

- These artifacts appear untracked after any uv build/install/run in the package dir (observed during the merge: `skills/task-tree/build/`, `superra_task_tree.egg-info/`, `uv.lock`). The root `.gitignore` covers `__pycache__/` and `**.pyc` but no packaging outputs, and the repo commits no lockfiles, egg-info, or build trees anywhere. Prefer a scoped `skills/task-tree/.gitignore` to keep the concern local to the package. Ignoring `uv.lock` matches the current de-facto convention; if you instead choose to commit it for reproducible installs, document the reasoning in `## Results`.
- Verify Fix 2 by actually running `uv tool install ./skills/task-tree` (then `uv tool uninstall superra-task-tree`) and confirming `git status` stays clean.
- Commit the two fixes separately (one concern per commit) under this task.

## Results

### Fix 1 — create-path status rollup

[`task_create.py`](skills/task-tree/scripts/task_create.py) imported `propagate_parent_status` from `_task_io` and calls it immediately after writing the new `task.md` (before the dashboard rebuild). The call mirrors the identical call in `task_update.py:168` and `task_hook.py`.

Regression test `TestTaskCreate::test_create_child_under_approved_parent_rolls_up` added to [`test_task_tree.py`](skills/task-tree/scripts/test_task_tree.py): creates a `not-started` child under an `approved` parent and asserts the parent's persisted status is no longer `approved`.

Verification: `uv run --project skills/task-tree --with pytest python -m pytest skills/task-tree/scripts/test_task_tree.py -v` → 218 passed, 11 skipped. The new test and all 12 existing `TestTaskCreate` tests pass. Committed as `27cd2aa4`.

### Fix 2 — gitignore packaging artifacts

Created [`skills/task-tree/.gitignore`](skills/task-tree/.gitignore) covering `build/`, `dist/`, `*.egg-info/`, and `uv.lock`. Chose to ignore `uv.lock` matching the repo's de-facto convention (no lockfiles committed anywhere); no reproducible-install requirement exists for this package.

Verification: ran `uv build --project skills/task-tree`, `uv tool install ./skills/task-tree`, `uv tool uninstall superra-task-tree` — `git status` showed only the new `.gitignore` file and the pre-existing untracked `superRA/dashboard.html`. No packaging artifacts appeared as untracked. Committed as `c9ad0e58`.
