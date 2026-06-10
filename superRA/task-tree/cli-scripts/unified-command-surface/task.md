---
title: "Unify task-tree command surface"
status: revise
depends_on:
  - uv-package
tags: []
created: 2026-06-02
---

## Objective

Implement the `superra` command hierarchy that wraps existing task-tree operations for both human and agent use, with dashboard launch promoted to `superra dashboard`.

### Scope

- Route existing read/query/check/create/update/add-result/link/rename/comment/migrate/hook behavior through `superra task ...`.
- Route dashboard launch and static export through top-level `superra dashboard` commands.
- Normalize task-root option naming to `--root` on the new CLI while preserving old script flags where compatibility wrappers still exist.
- Use task-root autodetection where safe, preferring `superRA/` and preserving `.plan/` compatibility where existing code supports it.
- Keep task command names action-oriented and stable for agent prompts: `read`, `tree`, `frontier`, `dag`, `check`, `create`, `update`, `status`, `result`, `dep`, `rename`, `comment`, `migrate`, `hook`.
- Preserve JSON output modes needed by agents and tests.
- Ensure mutation commands continue to validate task-root containment and sibling-only dependencies.

### Validation

- The new CLI can reproduce the current outputs for task reading, tree display, frontier selection, DAG rendering, dashboard launch/export, and comment listing on this `superRA/` tree.
- Mutation commands create or update task files with the same frontmatter/body format as the existing scripts.
- `task_check.py` or its new CLI equivalent reports no structural errors on `superRA/`.

## Planner Guidance

Prefer delegating to existing functions first, then tightening APIs only where current script-level argument parsing makes composition awkward. The first implementation should not redesign the task data model.

## Results

- Completed the packaged `superra` command hierarchy in [cli.py:18](../../../../skills/task-tree/scripts/cli.py#L18): `superra dashboard` owns dashboard serve/export, `superra task ...` owns task operations, and no `superra task dashboard` command is registered.
- Normalized package CLI `--root` defaults to task-root autodetection, preferring `superRA/` and preserving `.plan/` fallback. For wrappers whose direct scripts still require a concrete path, the package CLI resolves the root before delegation while leaving direct script flags compatible ([cli.py:29](../../../../skills/task-tree/scripts/cli.py#L29), [cli.py:60](../../../../skills/task-tree/scripts/cli.py#L60), [cli.py:115](../../../../skills/task-tree/scripts/cli.py#L115), [cli.py:172](../../../../skills/task-tree/scripts/cli.py#L172)).
- Routed existing parity operations that were not in the first package shim: `superra task status fix` wraps `task_update.py --fix`, and `superra task migrate upgrade-status` wraps `plan_migrate.py --upgrade-status` ([cli.py:146](../../../../skills/task-tree/scripts/cli.py#L146), [cli.py:186](../../../../skills/task-tree/scripts/cli.py#L186), [cli.py:314](../../../../skills/task-tree/scripts/cli.py#L314), [cli.py:416](../../../../skills/task-tree/scripts/cli.py#L416)).
- Added package CLI regression tests for root autodetection from nested task directories, `superRA/` preference over `.plan/`, `.plan` fallback, legacy-wrapper create/comment JSON behavior, top-level dashboard export, `status fix`, and the rejected `task dashboard` shape ([test_cli.py:56](../../../../skills/task-tree/scripts/test_cli.py#L56), [test_cli.py:141](../../../../skills/task-tree/scripts/test_cli.py#L141), [test_cli.py:153](../../../../skills/task-tree/scripts/test_cli.py#L153)).
- Fixed the revise finding by adding package-side containment checks with `resolve_path()` before delegating task-path mutation commands to legacy mutators, and by rejecting path-like dependency slugs before `dep add/remove` can write them ([cli.py:44](../../../../skills/task-tree/scripts/cli.py#L44), [cli.py:56](../../../../skills/task-tree/scripts/cli.py#L56), [cli.py:150](../../../../skills/task-tree/scripts/cli.py#L150), [cli.py:177](../../../../skills/task-tree/scripts/cli.py#L177), [cli.py:186](../../../../skills/task-tree/scripts/cli.py#L186), [cli.py:194](../../../../skills/task-tree/scripts/cli.py#L194)).
- Added regression coverage proving `update`, `result add`, `dep add/remove`, `rename`, and `status cascade` reject `../outside` task paths without mutating an outside task, plus sibling-slug coverage for `dep add ../outside` ([test_cli.py:128](../../../../skills/task-tree/scripts/test_cli.py#L128), [test_cli.py:158](../../../../skills/task-tree/scripts/test_cli.py#L158)).

### Verification

- `~/.venv/bin/python -m pytest skills/task-tree/scripts/test_cli.py -v` — 16 passed.
- `~/.venv/bin/python -m py_compile skills/task-tree/scripts/cli.py skills/task-tree/scripts/test_cli.py` — passed.
- `~/.venv/bin/python -m pytest skills/task-tree/scripts/test_task_tree.py -v` — 210 passed.
- `uvx --no-cache --from ./skills/task-tree superra task update ../outside --root /tmp/sra-cli-escape.mi7jgb/superRA --title Escaped` — exited 1 with `escapes plan root`; `/tmp/sra-cli-escape.mi7jgb/outside/task.md` still had `title: "Outside"`.
- `uvx --no-cache --from ./skills/task-tree superra task read task-tree/cli-scripts/unified-command-surface --no-ancestors --json` — package CLI read succeeded with JSON output.
- `uvx --no-cache --from ./skills/task-tree superra task check --json` — `ok: true`, 0 findings.
- `uvx --no-cache --from ./skills/task-tree superra dashboard --root superRA --no-open --port 8997` — started Uvicorn on `http://0.0.0.0:8997`, then was stopped with Ctrl-C.
- `uvx --no-cache --from ./skills/task-tree superra dashboard export --output /tmp/superra-unified-dashboard.html --subtree task-tree/cli-scripts/unified-command-surface` — dashboard export succeeded.
- `uvx --no-cache --from ./skills/task-tree superra task dashboard --help` — exited 2 with `invalid choice: 'dashboard'`.
- `uvx --no-cache --from ./skills/task-tree superra task status fix --root superRA` — ran and reported no inconsistencies.
- `uvx --no-cache --from ./skills/task-tree superra task migrate upgrade-status --dry-run --root superRA` — ran and reported all task files already use unified status.

Plain `uvx --from ./skills/task-tree ...` reused a cached local wheel with the previous parser during verification. `--no-cache` forced a current-source rebuild and is the reliable package-entry verification form until the package version changes.

## Review Notes

> 1. [MAJOR] The scope item "Ensure mutation commands continue to validate task-root containment and sibling-only dependencies" is enforced only in the `cli.py` shim, not in the mutators it delegates to — and the direct scripts remain a shipped compatibility surface. Reproduced: [`task_update.py:84`](../../../../skills/task-tree/scripts/task_update.py#L84) with `--path ../outside` rewrote a `task.md` outside the root (rc=0); [`task_add_result.py:52`](../../../../skills/task-tree/scripts/task_add_result.py#L52) appended a finding to it; [`task_link.py:57`](../../../../skills/task-tree/scripts/task_link.py#L57) with `--depends-on ../outside` wrote a literal path edge into `depends_on` frontmatter. Containment exists in only two mutators (`task_create.py`, `task_rename.py`). Fix: move the `resolve_path` containment and the sibling-slug check into the mutator functions so there is one enforcement point regardless of entry surface.
> 2. [MAJOR] The unified surface is an argv-reserialization shim: every `_run_*` handler in [cli.py](../../../../skills/task-tree/scripts/cli.py#L217) defines a second argparse parser, then re-serializes flags back into the legacy script's parser via `_module_main`, giving each verb two parsers that can drift — item 1 and the `path-arg-resolution` CRITICAL (prefix tolerance enforced in only one layer) are both instances. Error output also leaks the internal surface: `superra task update x --status bogus` prints usage for `--plan-root`/`--path`/`--cascade`, flags the public command does not expose. Fix: call the mutator functions (`update_task`, `link_task`, …) directly instead of round-tripping through argv, and validate at that single layer.
> 3. [MINOR] [`_resolved_root_value`](../../../../skills/task-tree/scripts/cli.py#L68) masks autodetect failure by guessing `"superRA"`, so the packaged CLI errors with `parent directory does not exist: superRA` in a rootless directory while the direct scripts print the clean `could not auto-detect task root. Use --plan-root.` — make the failure messages consistent.
