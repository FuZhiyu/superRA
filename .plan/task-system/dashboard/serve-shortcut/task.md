---
title: "Generate .plan/serve shortcut script"
status: implemented
review_status: revise
integration_status: ~
depends_on:  []
tags: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Generate a `.plan/serve` shell script when `.plan/` is first created, so users can launch the dashboard with `bash .plan/serve` (or `./.plan/serve` if executable) with zero knowledge of where `plan_dashboard.py` lives.

**The script itself:**
- Resolves the path to `plan_dashboard.py` relative to `.plan/`'s location. The agent creating `.plan/` knows the skill-dir at creation time (e.g. `skills/task-system/scripts/plan_dashboard.py` for in-repo use); bake that resolved path into the script.
- Uses `uv run` so PEP 723 inline metadata handles dependencies automatically.
- Passes `--root` pointing to the `.plan/` directory (derived from the script's own location via `dirname "$0"`).
- Forwards any extra arguments (`"$@"`) so users can add `--port`, `--no-open`, etc.
- Should be short — under 10 lines.

**Generation mechanism — two sites need updating:**
1. `skills/planning-workflow/SKILL.md` §Create the `.plan/` Directory — add instruction to generate `.plan/serve` alongside root `task.md`. The agent knows `<skill-dir>` at planning time and writes the resolved path.
2. `skills/task-system/scripts/task_create.py` — when creating the root task (path has no `/` separator, i.e. it's a top-level task in a fresh `.plan/`), also generate `.plan/serve` if it doesn't exist. This covers retroactive creation and script-driven flows.

**Path resolution strategy:** Use a relative path from `.plan/` back to the skill directory. For in-repo usage: `../skills/task-system/scripts/plan_dashboard.py`. For plugin usage: the agent resolves `<skill-dir>` to an absolute path and writes that. The script should check that the resolved path exists and print a helpful error if not.

**Version control:** `.plan/serve` is committed alongside the task tree — not gitignored. For in-repo usage the relative path is stable across clones. For plugin usage the path may need updating, but that's preferable to the script being invisible to collaborators.

## Results

### Changes

1. **[`task_create.py`](skills/task-system/scripts/task_create.py)** — Added `_maybe_generate_serve_script()` function and a call site in `create_task()`. Generates `.plan/serve` when creating a root-level task (no `/` in path) and the script does not already exist. Path resolution: uses `relative_to()` for in-repo paths (produces `../skills/task-system/scripts/plan_dashboard.py`), falls back to absolute path for out-of-repo usage.

2. **[`planning-workflow/SKILL.md`](skills/planning-workflow/SKILL.md)** — Added step 2 to §Create the `.plan/` Directory instructing agents to generate `.plan/serve` alongside root `task.md`.

3. **[`task-system/SKILL.md`](skills/task-system/SKILL.md)** — Updated §Dashboard to show `bash .plan/serve` as the primary invocation and explain the shortcut script.

4. **[`test_task_system.py`](skills/task-system/scripts/test_task_system.py)** — Added three tests: `test_create_root_task_generates_serve_script` (verifies creation, content, executable bit), `test_create_root_task_does_not_overwrite_serve` (idempotency), `test_create_nested_task_does_not_generate_serve` (nested tasks skip generation).

### Script content (9 lines)

The generated `.plan/serve` script resolves `PLAN_DIR` from its own location, checks that the dashboard script exists, and runs it via `uv run` with `--root` and forwarded arguments.

### Verification

All 116 tests pass including the 3 new tests.

## Review Notes

1. **[MAJOR]** [task_create.py:38-41](skills/task-system/scripts/task_create.py#L38-L41) — Absolute path fallback produces a broken serve script. When `plan_root` is outside the repo tree, `dashboard_relpath` becomes an absolute path (e.g., `/Users/.../plan_dashboard.py`), but the template at line 18 always prepends `$PLAN_DIR/`, producing `$PLAN_DIR//Users/.../plan_dashboard.py` — a nonsensical concatenation. The script's `[ ! -f "$DASHBOARD" ]` guard catches this at runtime (prints error and exits 1), so it is fail-safe, but the generated serve script is non-functional for the plugin/out-of-repo case. Fix: either (a) use two template variants — one with `$PLAN_DIR/` prefix for relative paths and one without for absolute paths, or (b) use `os.path.relpath(dashboard.resolve(), plan_root.resolve())` which always produces a relative path and avoids the fallback entirely.

2. **[MINOR]** [test_task_system.py:461-475](skills/task-system/scripts/test_task_system.py#L461-L475) — `test_create_root_task_generates_serve_script` runs in a tmp directory (outside the repo), so it exercises the absolute-path fallback, but only asserts that `plan_dashboard.py` and `exec uv run` appear in the content. It does not detect the `$PLAN_DIR/` + absolute path concatenation bug. Add an assertion that the `DASHBOARD=` line does not contain `$PLAN_DIR/` followed by a `/`-rooted path (or, if item 1 is fixed via `os.path.relpath`, assert the path is relative).
