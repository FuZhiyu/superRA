---
title: "Reproduction Reminders When a Producer Changes"
status: approved
depends_on: [01-section-contract]
---

## Objective

Tell the agent, in the same turn and without blocking, when an edit touches a registered producer or leaves a retained result without one. The changed files come from the tool-agnostic detector in [edit-detection](../../task-tree/edit-detection/task.md), so Bash, Edit, Write, and `apply_patch` edits are treated alike.

- **Producer edit:** a changed dep, script, or include of a registered step — including files inside a declared directory and paths written with literal or `env:` variables — reminds once per file per session and names the steps the edit stales with their last durations. A step's out and a task file never remind.
- **New or unregistered script:** an unregistered script under the task root reminds; a new script beside the registered ones draws a softer reminder that it may need a step.
- **Result coverage:** a leaf reaching `implemented` whose `## Results` links generated-looking files no step writes or reads reminds once per transition.
- **Cheap and fail-open:** no `shell:` resolver or other subprocess runs on an edit; a tree with no reproduction config stays silent; the Claude hook and the Codex manifest emit the same reminders.

## Results

The reminders ship in [task_hook.py](../../../skills/task-tree/scripts/task_hook.py), with the shared analysis in [_repro_signals.py](../../../skills/task-tree/scripts/_repro_signals.py) and change detection in [_edit_detect.py](../../../skills/task-tree/scripts/_edit_detect.py). [internals.md §Hook Architecture](../../../skills/task-tree/references/internals.md#hook-architecture) documents the watched set, baseline, markers, and messages.

- **One emission point.** `_repro_emit` takes project-relative paths from any detector and applies the marker, the owner lookup, and the fan-out once: `Stales build-panel (12.4s), fit-model (3.0s), make-figure (no recorded duration).` Upstream steps are excluded, since an edit to a consumer never implies rerunning its producers.
- **Variables resolve without a subprocess.** `_hook_graph` resolves literal and `env:` variables and gives `shell:` variables an inert placeholder, so a `sed -i` on `${CODE}/est.jl` is caught while a path built from a `shell:` variable matches nothing.
- **The first tool call is covered.** A `UserPromptSubmit` event, registered in [hooks.json](../../../hooks/hooks.json) and [hooks-codex.json](../../../hooks/hooks-codex.json), seeds the session's baseline; a harness without it seeds on the first tool call.
- **Both harnesses carry a session id:** Claude Code and Codex CLI (0.152.1) PostToolUse payloads include `session_id`; a payload without one falls back to a one-hour window per file. Editing a task's `## Reproduction` section clears the markers for its steps' deps, so the reminder fires again.
- **The tree is found from the edited file**, walking up for a `superRA/` child, never from the process cwd, since producers sit beside the task tree.
- **A `task.md` edit reports warnings for the edited tasks only**; a structural Bash move still reports the whole tree.

Tests: [test_edit_detect.py](../../../skills/task-tree/scripts/test_edit_detect.py) and the hook cases in [test_task_tree.py](../../../skills/task-tree/scripts/test_task_tree.py).
