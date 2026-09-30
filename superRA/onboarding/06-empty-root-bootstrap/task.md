---
title: "Create the First Task in an Empty superRA/"
status: not-started
depends_on: []
---

## Objective

`superra task create` succeeds in a project whose `superRA/` holds only the wrapper, so onboarding's first task needs no `--root` flag or hand-written file.

- Red-green test: an empty `superRA/` with only `superra` fails before the fix and creates the task after it.
- The auto-detect rule for existing trees is unchanged.

## Details

Reproduced 2026-09-30 in a scratch folder: after `wrapper init`, `./superRA/superra task create 01-data --title "Data"` exits with "could not auto-detect task root. Use --root." Root resolution is in `resolve_plan_root_arg` ([_task_io.py](../../../skills/task-tree/scripts/_task_io.py)).
