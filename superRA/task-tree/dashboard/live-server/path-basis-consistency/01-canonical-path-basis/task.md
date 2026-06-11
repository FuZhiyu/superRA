---
title: "Task paths are relative to the resolved root; support a rootless forest"
status: approved
depends_on: []
tags: []
created: 2026-06-07
---

## Objective

Make a task's canonical `path` always relative to the **resolved task root** (the directory the CLI/dashboard resolved via `--root` / auto-detect), and treat a root with no `task.md` as a forest of top-level trees. See the parent for the full diagnosis and confirmed design.

**Required invariant:** for any task whose `task.md` lives at `<resolved-root>/A/B/`, its `path` is `A/B` — never a value that drops a leading segment by descending below the resolved root. This is the basis `resolve_path` ([_task_io.py:476](skills/task-tree/scripts/_task_io.py#L476)) and the dashboard SSE watcher already use; the bug is that `parse_task` derives `path` from `_find_plan_root` ([_task_io.py:285](skills/task-tree/scripts/_task_io.py#L285), [_task_io.py:386](skills/task-tree/scripts/_task_io.py#L386)), which walks up *while the parent has a `task.md`* and so descends past the resolved root when `<root>/task.md` is absent.

**What to change:**

- When the resolved root is known (the tree walk has it), compute each task's `path` as `task_dir.relative_to(resolved_root)` rather than re-deriving via `_find_plan_root`. `walk_plan` / `_walk_children` ([_task_io.py:402](skills/task-tree/scripts/_task_io.py#L402), [_task_io.py:461](skills/task-tree/scripts/_task_io.py#L461)) already receive `plan_root` — thread it so child `path`s are root-relative, with `<root>/task.md` (if present) at `path == ""` and a missing `<root>/task.md` producing a synthetic container root (`path == ""`) whose children are the top-level trees. Eliminate the current collision where, with no root `task.md`, multiple top-level tasks each resolve to `path == ""`.
- Correct `_find_plan_root` (the standalone heuristic used when no root is passed, e.g. `parse_task` on a bare path) so it returns the nearest ancestor that is the **task-root directory** (a `TASK_ROOT_DIRNAMES` member: `superRA`/`.plan`) rather than the topmost task-bearing directory — so a bare-path parse agrees with a known-root walk. Preserve existing tolerances in `resolve_path` (redundant leading `superRA/` segment stripping).
- **Do not enforce a root `task.md`.** A rootless root is a valid forest; an umbrella `<root>/task.md` is also valid. Both must round-trip.
- **Root *detection* must recognize a forest** (design review BLOCKING ×2 — without this, forests are reachable only via an explicit `--root`, defeating the design's "auto-detected" and multi-worktree forest cases). A directory is a task root when it is a `TASK_ROOT_DIRNAMES` member (`superRA`/`.plan`) containing at least one child task dir — **not** only when it holds a root `task.md`. Apply this to both detection paths: `autodetect_plan_root` ([_task_io.py:30](skills/task-tree/scripts/_task_io.py#L30)), which today returns `None` for a rootless forest so every auto-detecting CLI command fails on one; and `_worktree_discovery._find_plan_root` ([_worktree_discovery.py:154](skills/task-tree/scripts/_worktree_discovery.py#L154)), which today requires `task.md` so `filter_worktrees` drops forest-root worktrees and the dashboard `?wt=` selector 404s on them.
- **Unify `task_check.py`'s own walk** ([task_check.py](skills/task-tree/scripts/task_check.py)): its `_walk_children` happy path inherits the same descend bug while its error path already uses the correct basis — converge both on the resolved-root basis. Its `check_placement` single-child-root smell ([task_check.py:249](skills/task-tree/scripts/task_check.py#L249)) must not fire spuriously on a legitimate single-top-level forest — exempt or adjust it.

**Scope:** the task-tree core path computation **and root detection** in `_task_io.py`, `_worktree_discovery.py`, and `task_check.py` (plus any dashboard tree-build glue in `plan_dashboard.py` that needs the resolved root threaded). This task does **not** change the SSE watcher (already correct) or the link builders (task 02). Keep `walk_plan`'s public contract usable by every existing caller (CLI `task read/tree/frontier/dag/create`, `task_check`, the dashboard).

## Validation

- **Regression tests (required) — the gap that let this ship.** Add `tmp_path` fixtures for both layouts: (a) **forest** — no `<root>/task.md`, one or more top-level task dirs with descendants; assert every task `path` is root-relative (top-level dir name retained, no `""` collisions, deep task = full root-relative path) and that `resolve_path(root, path)` round-trips back to the on-disk dir. (b) **conventional** — `<root>/task.md` present; assert paths are unchanged from current behavior (root `""`, children as before). Include a multi-top-level forest to prove the no-collision fix.
- **Forest detection (required).** Assert `autodetect_plan_root` resolves a rootless forest (from the repo root and from inside the root dir), so auto-detecting CLI commands work without `--root`; assert a forest-root worktree survives `_worktree_discovery` / `filter_worktrees` (so `?wt=` lists it); assert `task_check` runs clean on a forest and its single-child placement smell does not fire spuriously.
- **Dashboard consequence (required).** On a served nested-root project, `/nav` rows' `data-path` and the watcher's `task:{path}` events must now agree (both root-relative); editing a deep `task.md` live-updates. Confirm the conventional repo tree is byte-for-byte unchanged.
- **Whole suite green** (core change has CLI-wide blast radius): `uv run --project skills/task-tree --with pytest --with httpx python -m pytest skills/task-tree/scripts -q`. Investigate any test that encodes the old descend behavior and update it intentionally (note it in Results).

## Planner Guidance

- The smallest correct change is likely to pass `plan_root` through `_walk_children` into the per-task path computation, and set `parse_task`'s `path` from the caller's root when supplied, falling back to the corrected `_find_plan_root` only for bare-path parses.
- Audit other `_find_plan_root` / `walk_plan` callers (`task_check.py` has its own `_walk_children`; CLI commands; `_worktree_discovery.py`) for the same descend assumption.

## Results

A task's canonical `path` is now always relative to the **resolved task root**, and a `superRA/`/`.plan/` directory with no umbrella `task.md` is a valid **forest** of independent top-level trees. The two path bases that disagreed (the watcher/`resolve_path` "resolved-root-relative" basis vs. `parse_task`'s descend-derived basis) are now one and the same.

### What changed

**`parse_task` takes an optional `plan_root`** ([_task_io.py](../../../../../../skills/task-tree/scripts/_task_io.py)). When the caller already resolved the root (every tree walk and CLI command does), the path is computed as `task_dir.relative_to(plan_root)` — never re-derived by descending. When omitted (bare-path parse), it infers the root via the corrected `_find_plan_root`. Every walk site threads the root: `walk_plan` / `_walk_children`, `propagate_parent_status`, `validate_plan`, and the dashboard's `rebuild_state_task` (the live-reload re-parse) now all pass `plan_root` to `parse_task`.

**`_find_plan_root` corrected** to return the nearest ancestor (or self) whose basename is a `TASK_ROOT_DIRNAMES` member (`superRA`/`.plan`), instead of the topmost task-bearing directory. This is the same basis a known-root walk uses, so a bare parse and a walk agree on every path — including a forest root with no umbrella `task.md`. A legacy fallback (topmost task-bearing ancestor) is retained only for trees not nested under a `superRA`/`.plan` container, so ad-hoc fixtures still resolve.

**Forest detection added to both detection paths.** `autodetect_plan_root` ([_task_io.py](../../../../../../skills/task-tree/scripts/_task_io.py)) now recognizes a task root as a `TASK_ROOT_DIRNAMES` member that holds either an umbrella `task.md` **or** at least one child task dir (helpers `_is_task_root_dir` / `_has_child_task_dir`); it also keeps climbing past a deep-but-rootless `task.md` toward a task-root-dir ancestor, so it resolves the forest from the repo root, from inside the root, and from a deep subdir. `_worktree_discovery._find_plan_root` ([_worktree_discovery.py](../../../../../../skills/task-tree/scripts/_worktree_discovery.py)) gained the same forest acceptance (helper `_is_task_root`), so `filter_worktrees` keeps a forest-root worktree and the dashboard `?wt=` selector lists it.

**`task_check` unified on the resolved-root basis** ([task_check.py](../../../../../../skills/task-tree/scripts/task_check.py)): its `_walk_plan_tolerant` happy path now passes `plan_root` to `parse_task` (its error path already used the correct basis). `check_placement` takes an `is_forest` flag (`not (plan_root / "task.md").exists()`); on a forest the synthetic container is not a root task, so the leaf-only-frontmatter and single-child-wrapper smells are skipped — a legitimate single-top-level forest no longer trips the wrapper smell.

**Both CLI auto-detect copies deduplicated onto the shared `autodetect_plan_root`.** `task_read.py` **and** `task_query.py` ([task_query.py](../../../../../../skills/task-tree/scripts/task_query.py)) each carried their own root-detection copy that required an umbrella `task.md` (`(candidate / "task.md").exists()`), so both would fail on a forest. `task_query.main` is the entry point for `task tree`/`frontier`/`dag`/`list` — the most-used read commands — so its stale copy broke forest auto-detect for all of them and, run from inside a deep tree dir, silently returned a top-level tree dir rather than the `superRA/` container (paths then disagreeing with the dashboard/`task read` basis this task unifies). Both now import and use the shared `autodetect_plan_root`, removing the drift and gaining forest support; the read commands resolve a forest identically to `task read`.

### Verification

- **Whole suite green:** `uv run --project skills/task-tree --with pytest --with httpx python -m pytest skills/task-tree/scripts -q` → **581 passed, 2 skipped** (the 2 skips and 4 deprecation warnings are pre-existing, unrelated to this change).
- **New regression tests** (in [test_task_tree.py](../../../../../../skills/task-tree/scripts/test_task_tree.py), classes `TestCanonicalPathBasisForest` and `TestForestDetection`, with a `forest_root` fixture — a `superRA/` with no umbrella `task.md` holding two independent trees with descendants):
  - Forest task paths are root-relative with both a known root and a bare parse; a deep task keeps its full prefix (`01-alpha/01-model/01-derive`).
  - `walk_plan` produces no `""` collisions in a multi-top-level forest (top-level paths `01-alpha`, `02-beta` distinct), and `resolve_path(root, path)` round-trips back to every on-disk dir.
  - Conventional layout (umbrella `task.md`) is unchanged: root `""`, children carry their own slug.
  - `autodetect_plan_root` resolves a rootless forest from the repo root and from inside the root; a forest-root `WorktreeInfo` survives `filter_worktrees`; `task_check` runs without firing the single-child smell on a forest, including a single-top-level forest; `task_check`'s own walk reports root-relative paths.
  - **Forest auto-detect through the CLI read path** (the gap that let the `task_query` copy ship green): `task_query.autodetect_plan_root` resolves a forest from the repo root and from inside a top-level tree; `task_query.main(["--tree", "--json"])` run (via `monkeypatch.chdir`) from the repo root with no `--plan-root` does not error and reports root-relative top-level paths (`01-alpha`, `02-beta`); `task_query.main(["--frontier", "--json"])` from inside a deep tree dir auto-detects the forest container and emits full root-relative frontier paths.
- **CLI smoke (live source) on a forest fixture** (no umbrella `task.md`, two top-level trees): `superra task tree` from the fixture repo root prints the synthetic container with root-relative children; `superra task frontier` from inside `01-alpha/01-model` resolves the `superRA/` container (not the top-level tree) and lists root-relative paths — both previously errored / descended.
- **Dashboard consequence (live):** built a forest `WorktreeState` for a fixture forest; the path-keyed index keys are root-relative (`''`, `01-alpha`, `01-alpha/01-model`, `02-beta`), and `rebuild_state_task(state, "01-alpha/01-model")` (the watcher-triggered re-parse, keyed by the path the watcher emits) returns a task whose `path` is exactly `01-alpha/01-model`. The nav/index basis and the watcher event basis now agree, which is what makes live-reload match on a forest. The conventional repo tree (`superra task read`) is unchanged (verified the focused tree for `task-tree/dashboard/live-server`).

### Intentional test update

Three `TestTaskRead` tests called the now-removed `task_read._autodetect_plan_root`; they were repointed to `task_read.autodetect_plan_root` (the re-exported shared function). This is a rename to follow the deduplication, not a behavior change — those tests assert the same root-resolution outcomes as before. No test encoded the old descend behavior, so none had to be relaxed.

### Out of scope (left for task 02)

The SSE watcher (already correct) and the file-link builders (the hardcoded `superRA/` prefix and `vscode_link` helper) are untouched — those are [02-file-link-consistency](../02-file-link-consistency/task.md).
