---
title: "File links derive from the resolved absolute root (drop hardcoded superRA/)"
status: approved
depends_on:
  - 01-canonical-path-basis
tags: []
created: 2026-06-07
---

## Objective

Make every task-path → file hyperlink derive from the **resolved root's absolute path** (or each task's `dir_path`) instead of the hardcoded `…/superRA/<task.path>` string, so links are correct for a non-default `--root` and for a rootless forest. Also confirm the dashboard renders and routes a forest cleanly. See the parent for the design.

With [01-canonical-path-basis](../01-canonical-path-basis/task.md) done, `task.path` is resolved-root-relative, so the default-`./superRA` links already resolve correctly (`PROJECT_ROOT + '/superRA/' + path` reconstructs the file). This task removes the remaining hardcoded assumption that the root dir is named `superRA` directly under `PROJECT_ROOT`, which still breaks when `--root` points elsewhere.

**Required invariant:** for every task, each generated href (VS Code `vscode://file/…`, GitHub blob link, and the base for in-body relative links) points at the file that actually exists, for any resolved root (default `./superRA`, arbitrary `--root`, nested forest).

**Sites to fix (audit for others while here):**

1. Per-task VS Code / GitHub button — `taskFileVscodeHref(path)` ([base.html:2282](skills/task-tree/scripts/templates/base.html#L2282)): both the `PROJECT_ROOT + '/superRA/' + path + '/task.md'` and `repoFileHref('superRA/' + path + '/task.md')` branches.
2. In-body markdown relative links — `pathPrefix = 'superRA/' + taskPath + '/'` in `renderMarkdown` ([base.html:1758](skills/task-tree/scripts/templates/base.html#L1758)) and its `vscode://file/' + PROJECT_ROOT + '/' + filePath` rewrite ([base.html:1786](skills/task-tree/scripts/templates/base.html#L1786)).
3. Server-side `vscode_link(path, project_root)` ([plan_dashboard.py:570](skills/task-tree/scripts/plan_dashboard.py#L570)): `Path(project_root) / path`.
4. Client `resolveInternalTaskPath` ([base.html:1716](skills/task-tree/scripts/templates/base.html#L1716)) hardcodes `superRA/` / `.plan/` prefix stripping when turning an in-body link into an internal task navigation — reconcile it with the resolved-root basis so internal links work for a non-`superRA` root.

**Approach:** surface the resolved root from the server to the client as a single base (e.g. inject the resolved-root absolute path and/or the repo-relative root prefix as a template var alongside the existing `project_root` / `repo_file_base`), and have every builder prepend that instead of the literal `superRA/`. Preserve the GitHub (`REPO_FILE_BASE`, recently re-pointed at the trunk in `f0d7ac14`) vs local `vscode://file` branching, the per-worktree `PROJECT_ROOT` follow in `fetchWorktrees`, and standalone (`window.STANDALONE`) behavior.

**Forest UI/routing check:** confirm the synthetic container root (`path == ""`, no body) renders sensibly in the sidebar, breadcrumb (`root` crumb), and active-node panel when there is no umbrella `task.md`, and that deep-linking / `setActive('')` behaves. Fix only what the forest case breaks; do not redesign navigation.

**Scope:** the link/render builders in `base.html` and `plan_dashboard.py`, plus any small server change to expose the resolved root. Core path semantics are task 01.

## Validation

- **Regression test (required).** With a non-default `--root` and a nested-root fixture, assert the VS Code/GitHub href and the in-body relative-link base resolve to real on-disk paths (not a `superRA/`-prefixed guess); assert default-`./superRA` and conventional layouts are unchanged. Cover server `vscode_link` directly and the rendered-HTML expectations in `test_dashboard.py` per the file's string-assertion convention.
- **Real path (required).** On a served nested-root project, open a deep task and confirm the VS Code/GitHub button and an in-body relative link point at files that exist; confirm the forest renders (top-level tree(s) visible, breadcrumb/root sane). Inspect the rendered `href`, not the builder in isolation.
- Full suite green: `uv run --project skills/task-tree --with pytest --with httpx python -m pytest skills/task-tree/scripts -q`.

## Planner Guidance

- `PROJECT_ROOT` is `plan_root.parent` ([plan_dashboard.py:160](skills/task-tree/scripts/plan_dashboard.py#L160)); injecting the resolved-root absolute path (= `plan_root`) as its own var lets every builder use `<resolved_root_abs>/<path>/…` uniformly and drop the `parent + '/superRA/'` reconstruction.
- The multi-worktree selector re-points `PROJECT_ROOT` per worktree in `fetchWorktrees`; any new resolved-root var must follow the active worktree the same way.

## Results

Every task-path → file hyperlink now derives from the **resolved root's absolute path** instead of the hardcoded `…/superRA/<task.path>` string. Links resolve to real on-disk files for a non-default `--root`, a rootless forest, and a subtree export, while the conventional `superRA/` layout is byte-for-byte unchanged.

### Single resolved-root base injected from server to client

Following the planner's guidance, the server now injects the resolved root as its own template var (= `plan_root`, the dir `task.path` is relative to), alongside the existing `project_root`:

- `index` and `render_standalone_html` ([plan_dashboard.py:786](../../../../../../skills/task-tree/scripts/plan_dashboard.py#L786), [plan_dashboard.py:1585](../../../../../../skills/task-tree/scripts/plan_dashboard.py#L1585)) pass `resolved_root` (absolute) and `root_prefix` (its basename).
- base.html exposes them as `RESOLVED_ROOT` / `ROOT_PREFIX` ([base.html:1654](../../../../../../skills/task-tree/scripts/templates/base.html#L1654)), the single base every builder prepends in place of the literal `superRA/`.

**Subtree-export correctness fix (deviation-worthy detail).** For a `--root` subtree export, `render_standalone_html` re-bases every path to the subtree, so the resolved root must be the **subtree dir** (`subtree_dir = located.dir_path`), not the full `plan_root`. The in-flight draft used `str(plan_root.resolve())`, which would have dropped the subtree segment and pointed re-based links at missing files. Corrected to `str(subtree_dir.resolve())` ([plan_dashboard.py:1585-1591](../../../../../../skills/task-tree/scripts/plan_dashboard.py#L1585-L1591)); verified by `test_subtree_export_resolved_root_is_subtree_dir`.

### All four sites delinked (plus the worktree follow)

1. **VS Code / GitHub button** — `taskFileVscodeHref` ([base.html:2304](../../../../../../skills/task-tree/scripts/templates/base.html#L2304)): local link off `RESOLVED_ROOT`, GitHub blob off `ROOT_PREFIX`; no hardcoded `superRA/` segment.
2. **In-body relative links** — `renderMarkdown` ([base.html:1766](../../../../../../skills/task-tree/scripts/templates/base.html#L1766)): two bases — `taskDirRel` (`taskPath/`) prepended to `RESOLVED_ROOT` for the local `vscode://file` link, and `repoPathPrefix` (`ROOT_PREFIX/ + taskPath/`) for the GitHub branch.
3. **Server `vscode_link(path, project_root)`** ([plan_dashboard.py:570](../../../../../../skills/task-tree/scripts/plan_dashboard.py#L570)) was already a pure `Path(base) / path` join with no `superRA/` assumption — it is registered as a Jinja filter but **not invoked by any template** (task bodies render client-side via the `<script type="text/x-markdown">` payload). Left as-is and covered directly by `test_vscode_link_filter_joins_resolved_root`, which asserts it joins whatever base it is handed (resolved root or an arbitrary non-default root) without baking in `superRA/`.
4. **`resolveInternalTaskPath`** ([base.html:1714](../../../../../../skills/task-tree/scripts/templates/base.html#L1714)): now recognizes an href rooted at `ROOT_PREFIX + '/'` as tree-root-relative, keeping the literal `superRA/` and legacy `.plan/` prefixes accepted too (any root + migrated prose).
5. **Worktree follow** — `fetchWorktrees` ([base.html:3807](../../../../../../skills/task-tree/scripts/templates/base.html#L3807)) indexes each worktree's `plan_root` and re-points `RESOLVED_ROOT` / `ROOT_PREFIX` to the active `?wt=`, mirroring the existing `PROJECT_ROOT` follow. `/api/worktrees` already exposed `plan_root` per entry on trunk ([plan_dashboard.py:1147](../../../../../../skills/task-tree/scripts/plan_dashboard.py#L1147)); the change here is that the client now consumes it to re-point the resolved-root base. The non-empty `if (resolved)` guard preserves the server-injected roots in standalone (file://) mode.

### Verification (real rendered hrefs, not the builder in isolation)

Served a non-default root (`<proj>/tasks/`, basename ≠ `superRA`) and a rootless forest, and inspected the rendered page:

| Case | RESOLVED_ROOT / ROOT_PREFIX | Deep `task.md` link | Outcome |
|---|---|---|---|
| Non-default root `tasks/` | `<proj>/tasks` / `tasks` | `<proj>/tasks/01-alpha/01-model/task.md` | exists ✓ (old code → nonexistent `<proj>/superRA/…`) |
| Rootless forest | `<tmp>/superRA` / `superRA` | `<tmp>/superRA/01-alpha/01-model/task.md` | exists ✓; index 200, `/nav` lists `01-alpha` + `02-beta`, `/node/01-alpha/01-model` 200, `/node/` (synthetic root) 200 |
| Subtree export `--root 01-data-prep` | `<root>/01-data-prep` | re-based `01-load/task.md` → `<root>/01-data-prep/01-load/task.md` | exists ✓ |
| Conventional `superRA/` | `<root>` / `superRA` | unchanged | exists ✓ |

The forest synthetic container (`path == ""`, no umbrella `task.md`) renders as the `task-root` node, routes via `/node/`, and the breadcrumb builds a clickable `root` crumb that ascends via `setActive('')` — no navigation redesign needed.

### Regression tests

Added two classes to [test_dashboard.py](../../../../../../skills/task-tree/scripts/test_dashboard.py) in the file's string-assertion + served-HTML convention: `TestFileLinkConsistency` (injected vars for non-default root, on-disk link resolution, builder delink guards, forest render/route/link, subtree-export basis, conventional layout unchanged, server `vscode_link` filter) and `TestWorktreeRootFollowing` (`/api/worktrees` `plan_root` field, `fetchWorktrees` re-point). Updated the stale string assertion in `test_vscode_file_links_translate_line_anchors` ([test_task_tree.py:1163](../../../../../../skills/task-tree/scripts/test_task_tree.py#L1163)) — `repoFileHref(filePath)` → `repoFileHref(repoPathPrefix + href)` — to track the delinked GitHub branch while still guarding the `#L` anchor translation.

**Full suite green:** `592 passed, 2 skipped` via `uv run --project skills/task-tree --with pytest --with httpx python -m pytest skills/task-tree/scripts -q` (was `580 passed, 1 failed` on the in-flight draft; +11 new tests, the prior failure fixed).

