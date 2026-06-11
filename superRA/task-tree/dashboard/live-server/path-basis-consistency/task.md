---
title: "One task-path basis: the resolved root, with forest support"
status: approved
depends_on: []
tags: []
created: 2026-06-07
---

## Objective

Give the task tree **one** path basis and make every consumer obey it, so live-reload and every file hyperlink work for any task root — including a root that has no umbrella `task.md` (a forest of top-level trees) and a root set to a non-default `--root`.

### Design decision (researcher-confirmed)

The **resolved task root** is authoritative. It is the directory the CLI/dashboard resolved: `--root` when given, else auto-detected (`./superRA`, legacy `.plan`). Every task `path` is relative to that directory, and every file mapping derives from its **absolute** path (or each task's `dir_path`).

- **No enforced root `task.md`.** If `<root>/task.md` exists, it is the umbrella root task (`path == ""`), one tree. If it does not, `<root>/` is a container and each of its top-level subdirectories is an independent top-level tree — a **forest**. Both are supported; neither is required.
- **Nothing hardcodes `superRA/`.** A non-default `--root` must resolve files against its own absolute path.

### Root cause (note: the watcher is *not* the bug)

`parse_task` computes a task's canonical `path` via `_find_plan_root(task_dir)` ([_task_io.py:285](skills/task-tree/scripts/_task_io.py#L285), [_task_io.py:386](skills/task-tree/scripts/_task_io.py#L386)), which walks **up while the parent still contains a `task.md`** and returns the *topmost task-bearing directory*. When `<root>/task.md` is absent and the root is e.g. `superRA/01-intermediary-cost/`, this descends **below** the resolved root, so `task.path` drops the `01-intermediary-cost` segment (root becomes `""`, children become `01-model/…`). Meanwhile `resolve_path` ([_task_io.py:476](skills/task-tree/scripts/_task_io.py#L476)) and the dashboard SSE watcher ([plan_dashboard.py:342](skills/task-tree/scripts/plan_dashboard.py#L342)) both treat paths as **resolved-root-relative** (`01-intermediary-cost/01-model/…`). The two bases disagree exactly by the dropped prefix. In a multi-top-level forest the descend is also lossy: every top-level tree resolves to `path == ""`, colliding in any path-keyed index (one silently overwrites the others).

Consequences observed on a clean `better-handoff` server over the nested-root IntermediaryDemand layout:
- **Live-reload dead.** Watcher broadcasts `task:01-intermediary-cost/01-model/…` but rows carry `sse-swap="task:01-model/…"`; htmx never matches → editing a `task.md` does not refresh the page (the non-path-keyed `summary-updated` still fires, so the header bar updates and it looks half-broken).
- **Dead file links.** The VS Code / GitHub button, the in-body markdown relative-link base, and the server `vscode_link` helper build `…/superRA/<task.path>` from the descended path → they point at files missing the `01-intermediary-cost` segment.

### The fix, in two parts

1. **[01-canonical-path-basis](01-canonical-path-basis/task.md) — core.** Make `task.path` relative to the *resolved root* (consistent with `resolve_path` and the watcher), support a root with no `task.md` as a forest, and make root *detection* recognize a forest (not require a root `task.md`) so auto-detect and multi-worktree discovery find forests. With this in place the watcher needs no change, `/nav`+`/node` produce resolved-root-relative paths that match it (live-reload fixed), and the default-`./superRA` links resolve correctly because `PROJECT_ROOT + '/superRA/' + path` reconstructs the real file again.
2. **[02-file-link-consistency](02-file-link-consistency/task.md) — dashboard.** Delink the hardcoded `superRA/` so a non-default `--root` resolves against its absolute path, audit every task-path→file builder, and confirm the dashboard renders/routes a forest cleanly. Depends on 01.

### Conventions

This is superRA's own task-tree tooling. This repo's own `superRA/` **has** an umbrella `superRA/task.md` (the conventional single-tree case, where `_find_plan_root` already returns `superRA/` and paths are correct) — so it is the regression baseline that must keep working unchanged. The forest case (no root `task.md`) must be exercised with a fixture and/or the nested-root IntermediaryDemand layout. Work in this project worktree only: `/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/dashboard-path-consistency`. Run the CLI/tests from live source per the repo `CLAUDE.md` §Local Task-Tree CLI Development (`uv run --project skills/task-tree …`). Core path changes affect the whole CLI — the full suite must stay green: `uv run --project skills/task-tree --with pytest --with httpx python -m pytest skills/task-tree/scripts -q`.

## Results

The task tree now has **one** path basis — the resolved task root — and every consumer obeys it, so live-reload and every file hyperlink work for any root, including a rootless **forest** (a `superRA/`/`.plan/` dir with no umbrella `task.md`, whose top-level subdirectories are independent trees) and a non-default `--root`.

The root cause was a two-basis disagreement: the SSE watcher and `resolve_path` keyed tasks by their path *relative to the resolved root*, while `parse_task` re-derived the path by *descending* to the topmost task-bearing directory — so whenever `<root>/task.md` was absent, the derived path dropped a leading segment. The watcher then broadcast `task:01-tree/…` while the rendered row carried `sse-swap="task:…"` (segment missing), htmx never matched, and live-reload silently died; the same descended path fed `…/superRA/<path>` file links that pointed at nonexistent files. A multi-tree forest was additionally lossy — every top-level tree collapsed to `path == ""` and collided in any path-keyed index.

**[01-canonical-path-basis](01-canonical-path-basis/task.md)** made `task.path` always `task_dir.relative_to(resolved_root)`, threaded `plan_root` through every walk and the dashboard re-parse, corrected `_find_plan_root` and both CLI auto-detect copies (`task_read` *and* `task_query` — the latter a CRITICAL caught in review, since it drives the most-used `tree`/`frontier`/`dag`/`list` commands) to recognize a forest root, and exempted `task_check`'s single-child placement smell on a legitimate single-tree forest. With the bases unified the watcher needed no change and live-reload matches again.

**[02-file-link-consistency](02-file-link-consistency/task.md)** delinked every task-path→file hyperlink (VS Code button, GitHub blob, in-body relative-link base, `resolveInternalTaskPath`) from the hardcoded `superRA/` string, deriving each from a single server-injected resolved-root base (`RESOLVED_ROOT`/`ROOT_PREFIX`) that follows the active `?wt=` worktree. Verified against real rendered hrefs for default root, non-default `--root`, rootless forest, and subtree export; also fixed a subtree-export bug where the resolved root must be the subtree dir, not the full `plan_root`.

**Net effect:** the two original regressions — dead live-reload and dead file links on a nested/forest root — are both fixed and covered by new regression tests (forest path basis with no `""` collisions, forest detection through every CLI read command, link resolution across all four root cases). Whole suite green at **592 passed, 2 skipped**. The conventional `superRA/`-with-umbrella-`task.md` layout (this repo's own tree) is byte-for-byte unchanged.
