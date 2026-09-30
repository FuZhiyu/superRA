---
title: "Create the First Task in an Empty superRA/"
status: approved
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
- **Migration into the same state:** `task migrate from-plan --output superRA` refused a `superRA/` holding only the wrapper ("output directory is not empty"), which breaks onboarding's legacy `PLAN.md` path once the wrapper exists. [plan_migrate.py](../../../skills/task-tree/scripts/plan_migrate.py) now ignores the wrapper when checking emptiness; `test_migrate_into_wrapper_only_root` failed before and passes after, and `test_migrate_refuses_root_with_tasks` keeps a populated root refused ([test_task_tree.py](../../../skills/task-tree/scripts/test_task_tree.py)).
- **Scratch check:** in a folder with no git, `wrapper init` then `task create 01-data --title Data` wrote `superRA/01-data/task.md`.

## Review Notes

Tier: quick. Focuses: correctness of the two CLI fixes.

1. **[ADVISORY] A farther populated root beats a nearer wrapper-only root.** [cli.py:116](../../../skills/task-tree/scripts/cli.py#L116) tries the fallback only when autodetect returns nothing, and autodetect walks up without bound ([_task_io.py:128-153](../../../skills/task-tree/scripts/_task_io.py#L128-L153)). A project with a wrapper-only `superRA/` nested under a directory whose `superRA/` has tasks — a scratch onboarding trial under this repo's `work/`, say — gets its first task created in the outer tree. Checking the nearest `superRA/` with a wrapper before accepting a farther autodetected root would fix it; low likelihood in real projects.
