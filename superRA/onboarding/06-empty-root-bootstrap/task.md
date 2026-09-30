---
title: "Create the First Task in an Empty superRA/"
status: implemented
depends_on: []
---

## Objective

`superra task create` succeeds in a project whose `superRA/` holds only the wrapper, so onboarding's first task needs no `--root` flag or hand-written file.

- Red-green test: an empty `superRA/` with only `superra` fails before the fix and creates the task after it.
- The auto-detect rule for existing trees is unchanged.

## Details

Reproduced 2026-09-30 in a scratch folder: after `wrapper init`, `./superRA/superra task create 01-data --title "Data"` exits with "could not auto-detect task root. Use --root." Root resolution is in `resolve_plan_root_arg` ([_task_io.py](../../../skills/task-tree/scripts/_task_io.py)).

## Results

`superra task create` now creates the first task in a `superRA/` that holds only the wrapper. When autodetect finds no root, the CLI mutators fall back to the nearest `superRA/` above the working directory that contains the `superra` wrapper ([cli.py](../../../skills/task-tree/scripts/cli.py), `_wrapper_only_root`). Autodetect itself is unchanged, so read commands and dashboard discovery behave as before.

- **Red-green:** `test_task_create_first_task_in_wrapper_only_root` failed with "could not auto-detect task root" before the fix and passes after; `test_task_create_without_wrapper_or_tasks_still_fails` keeps a bare empty `superRA/` an error ([test_cli.py](../../../skills/task-tree/scripts/test_cli.py)). All 43 tests in `test_cli.py` pass.
- **Scratch check:** in a folder with no git, `wrapper init` then `task create 01-data --title Data` wrote `superRA/01-data/task.md`.
