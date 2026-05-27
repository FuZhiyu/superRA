---
title: "Auto-compute and persist parent status from children"
status: approved
depends_on:
  - status-consistency
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

Currently `effective_status()` computes rolled-up status at render time, but the `status:` field in parent task.md files is never updated — it stays at whatever value was last written manually. This causes confusion when reading task files directly (e.g., `live-server/task.md` says `status: not-started` even though most children are `implemented`).

**Implement automatic parent status propagation:**

1. Add a `propagate_parent_status(plan_root, task_path)` function to `_task_io.py` that:
   - Walks from the given task up to the root
   - For each ancestor that is not a leaf, computes `compute_status()` from its children
   - If the computed status differs from the stored `status:` field, rewrites the frontmatter via `write_task()`
   - Also propagates `review_status:` using an analogous rollup: all children `approved` → parent `approved`; any child `revise` → parent `revise`; any child `implemented` → parent `implemented`; otherwise `~`

2. Call `propagate_parent_status()` from `task_update.py` after every status change — this already does auto-rebuild, add propagation before the rebuild.

3. Call it from the `task_hook.py` post-tool validation hook as well, so that any status change (including from implementer/reviewer agents writing directly) triggers propagation.

4. Add a standalone CLI entry point: `python3 task_update.py --propagate-all` that walks the entire tree and fixes all parent statuses.

**Files to modify:**
- `skills/task-system/scripts/_task_io.py` — add `propagate_parent_status()` and `compute_review_status()`
- `skills/task-system/scripts/task_update.py` — call propagation after status writes; add `--propagate-all` flag
- `skills/task-system/scripts/task_hook.py` — call propagation in the post-write hook

**Validation:** Run `--propagate-all` on the current `.plan/` tree and verify that `live-server`, `comments`, `comment-ui`, and `tests` parent tasks all get their `status:` and `review_status:` updated to match their children. Add tests.

## Results

Implemented automatic parent status propagation across the task tree.

**Functions added to [`_task_io.py`](skills/task-system/scripts/_task_io.py):**
- `compute_review_status(task)` — analogous to `compute_status()`, rolls up `review_status` from children: all approved -> approved; any revise -> revise; any implemented -> implemented; otherwise ~.
- `propagate_parent_status(plan_root, task_path)` — walks from a task up to root, recomputing `status` and `review_status` for each branch ancestor via rollup, with cascade reset of `integration_status` when `review_status` is not approved.

**Changes to [`task_update.py`](skills/task-system/scripts/task_update.py):**
- `update_task()` now calls `propagate_parent_status()` after every status write.
- `fix_status_consistency()` updated to use `compute_review_status()` for branches (consistent with propagation — no oscillation between the two commands).
- Added `propagate_all()` function and `--propagate-all` CLI flag: walks all branch tasks bottom-up, re-reading from disk at each level to ensure correct cascading.

**Changes to [`task_hook.py`](skills/task-system/scripts/task_hook.py):**
- Post-tool hook now calls `propagate_parent_status()` after validation, so any direct task.md edit by agents triggers propagation (best-effort, never blocks).

**Design decision:** For branch tasks, `review_status` is purely rolled up from children rather than cascade-reset when status < implemented. Rationale: a branch with `status: in-progress` (not all children approved) can legitimately have children with completed reviews. The cascade is implicit — if children don't have reviews, `compute_review_status` returns `~` naturally. The explicit cascade (reset when status drops) only makes sense for leaf tasks where review requires implementation.

**Validation:** Ran `--propagate-all` on the live `.plan/` tree. Result: 7 parent tasks updated (live-server, comments, comment-ui, tests, dashboard, task-system, root). Second run confirms idempotency ("All parent statuses already consistent"). `--fix` and `--propagate-all` produce consistent state with no oscillation.

**Tests:** 13 new tests covering `compute_review_status`, `propagate_parent_status`, and `propagate_all` (including cascade, idempotency, and CLI entry point). All 113 tests pass.
