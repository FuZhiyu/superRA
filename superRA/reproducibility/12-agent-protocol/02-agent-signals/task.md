---
title: "Advisory Signals: Missing Registration and the Staleness an Edit Causes"
status: not-started
depends_on: []
---

## Objective

Tell the agent, at the moment it can still act cheaply, that a retained result has no registered producer or that its edit made steps stale. Every signal is advisory and non-blocking: some retained artifacts legitimately have no producer step (a hand-edited `.tex`, a boundary input).

- **The producer-edit reminder names the fan-out.** When an edited file is a registered step's script, dep, or include, the existing reminder also lists the downstream steps the edit stales, with their last recorded durations. It reads the graph alone: no hashing, no `${VAR}` resolution, no subprocess.
- **Edits made through Bash draw the same reminder.** The changed paths come from the tool-agnostic detector that [edit-detection](../../../task-tree/edit-detection/task.md) builds; this task consumes that list, adds no detection of its own, and starts after that task is implemented. `code_roots` no longer exists, so the reminder covers registered scripts, deps, and includes only.
- **`task check` warning.** A `[WARNING]` in the `reproduction` category when a task's `## Results` links a generated-looking output file that no active step declares as an out and no step reads as a boundary dep. It names the file and the task.
- **Hook reminder at `implemented`.** When a leaf flips to `implemented` with such uncovered files, the task hook emits one non-blocking reminder naming them and pointing at `superRA:reproducibility`.
- **Quiet by default.** No finding for trees without reproduction config, for documents and source files, or for files under scratch paths. A false-positive rate that trains agents to ignore the signal fails the task.
- **Validation:** fixtures for the fan-out listing, a Bash-made edit, a covered artifact, an uncovered artifact, a linked `.tex` and `.md` (silent), a boundary dep (silent), and a tree without config (silent); each reminder fires once per file per session and the `implemented` reminder once per transition.

## Details

- Entry points: [task_hook.py](../../../../skills/task-tree/scripts/task_hook.py) (`_reproduction_reminder` at line 204 is the existing reminder), [task_check.py](../../../../skills/task-tree/scripts/task_check.py), [_task_validate.py](../../../../skills/task-tree/scripts/_task_validate.py).
- Which extensions count as generated output is the open design call: start from data and exhibit formats (`.csv`, `.parquet`, `.arrow`, `.png`, `.pdf`, generated `.tex` tables under an output root) and report the rule chosen and its misses.
- Load `superRA:task-tree` for every edit under `skills/task-tree/`.
