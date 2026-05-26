---
title: "Generate .plan/serve shortcut script"
status: not-started
review_status: ~
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

