---
title: "Auto-compute and persist parent status from children"
status: not-started
review_status: ~
integration_status: ~
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

