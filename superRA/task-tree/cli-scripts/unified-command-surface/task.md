---
title: "Unify task-tree command surface"
status: implemented
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
- **Single enforcement point in the mutators (revise round).** Containment (`resolve_path`, which rejects `../` escapes) and the sibling-only dependency check now live inside the mutator functions themselves — [`update_task`](../../../../skills/task-tree/scripts/task_update.py#L84), [`add_result`](../../../../skills/task-tree/scripts/task_add_result.py#L52), [`link_task`](../../../../skills/task-tree/scripts/task_link.py#L57) (plus `task_create`/`task_rename` which already had it). So a `../outside` path or a path-like dependency slug is rejected regardless of entry surface (packaged CLI **or** direct script), closing the gap where the direct scripts were an unguarded shipped surface.
- **Direct function calls, not argv round-tripping (revise round).** The mutation handlers in [cli.py](../../../../skills/task-tree/scripts/cli.py#L240) now call the mutator functions (`create_task`, `update_task`, `add_result`, `link_task`, `rename_task`) directly via a lazy `_load(module)` import instead of re-serializing flags into each legacy script's argparse parser. This removes the second parser per verb (the drift surface the review flagged), and the public `update`/`cascade` parsers carry `choices=VALID_STATUSES` so a bad `--status` errors on the public `superra task update` surface without leaking the internal `--plan-root`/`--path`/`--cascade` flags.
- **Consistent autodetect-failure message (revise round).** [`_plan_root`](../../../../skills/task-tree/scripts/cli.py#L91) exits 1 with `could not auto-detect task root. Use --root.` in a rootless directory instead of guessing `superRA` and surfacing a downstream `directory does not exist`.
- Regression coverage: `cli.py`-shim escape rejection retained ([test_cli.py `test_mutation_commands_reject_paths_outside_root`](../../../../skills/task-tree/scripts/test_cli.py#L152), [`test_dep_add_rejects_path_like_dependency_slug`](../../../../skills/task-tree/scripts/test_cli.py#L170)); new direct-mutator containment tests ([`TestTaskUpdate`](../../../../skills/task-tree/scripts/test_task_tree.py#L805)/[`TestTaskLink`](../../../../skills/task-tree/scripts/test_task_tree.py#L840)/[`TestTaskAddResult`](../../../../skills/task-tree/scripts/test_task_tree.py#L895) escape cases); public-surface error and autodetect-failure tests in [`TestCliPrefixTolerantMutations`](../../../../skills/task-tree/scripts/test_task_tree.py#L292).

### Verification

- Full suite: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts` — **631 passed, 2 skipped**.
- Direct mutator escape now blocked: `uv run --script skills/task-tree/scripts/task_update.py --plan-root /tmp/scratch_tree/superRA --path ../outside --status approved` exits 1 with `Task path '../outside' escapes plan root` (previously rc=0, rewrote the outside file).
- Public-surface error: `uv run --script skills/task-tree/scripts/cli.py task update superRA/01-x --root … --status bogus` prints usage for `superra task update` with only public flags (`--root`/`--status`/`--title`/…) — no `--plan-root`/`--path`/`--cascade` leak.
- Rootless autodetect: the packaged CLI now prints `could not auto-detect task root. Use --root.` (matching the direct scripts' clean message) instead of `directory does not exist: superRA`.

Note: the package is run with `uv run --script` (PEP 723 per-script deps), not `uvx --from`, per [CLAUDE.md §Local Task-Tree CLI Development](../../../CLAUDE.md) — there is no installable wheel.

## Review Notes

> 1. [MAJOR] The scope item "Ensure mutation commands continue to validate task-root containment and sibling-only dependencies" is enforced only in the `cli.py` shim, not in the mutators it delegates to — and the direct scripts remain a shipped compatibility surface. Reproduced: [`task_update.py:84`](../../../../skills/task-tree/scripts/task_update.py#L84) with `--path ../outside` rewrote a `task.md` outside the root (rc=0); [`task_add_result.py:52`](../../../../skills/task-tree/scripts/task_add_result.py#L52) appended a finding to it; [`task_link.py:57`](../../../../skills/task-tree/scripts/task_link.py#L57) with `--depends-on ../outside` wrote a literal path edge into `depends_on` frontmatter. Containment exists in only two mutators (`task_create.py`, `task_rename.py`). Fix: move the `resolve_path` containment and the sibling-slug check into the mutator functions so there is one enforcement point regardless of entry surface.
>    → implemented: moved `resolve_path` containment into [`update_task`](../../../../skills/task-tree/scripts/task_update.py#L91), [`add_result`](../../../../skills/task-tree/scripts/task_add_result.py#L60), [`link_task`](../../../../skills/task-tree/scripts/task_link.py#L76); added the sibling-only check to `link_task` via `_is_sibling_slug` ([task_link.py:21](../../../../skills/task-tree/scripts/task_link.py#L21)). Direct-script escapes now exit 1 (regression tests in `TestTaskUpdate`/`TestTaskLink`/`TestTaskAddResult`).
> 2. [MAJOR] The unified surface is an argv-reserialization shim: every `_run_*` handler in [cli.py](../../../../skills/task-tree/scripts/cli.py#L217) defines a second argparse parser, then re-serializes flags back into the legacy script's parser via `_module_main`, giving each verb two parsers that can drift — item 1 and the `path-arg-resolution` CRITICAL (prefix tolerance enforced in only one layer) are both instances. Error output also leaks the internal surface: `superra task update x --status bogus` prints usage for `--plan-root`/`--path`/`--cascade`, flags the public command does not expose. Fix: call the mutator functions (`update_task`, `link_task`, …) directly instead of round-tripping through argv, and validate at that single layer.
>    → implemented: mutation handlers now call mutator functions directly via `_load(module)` ([cli.py:240](../../../../skills/task-tree/scripts/cli.py#L240)) instead of re-serializing argv; public `update`/`cascade` parsers carry `choices=VALID_STATUSES` so the bad-status error stays on the public surface ([cli.py:553](../../../../skills/task-tree/scripts/cli.py#L553)). New test asserts no `--plan-root`/`--path`/`--cascade` leak.
> 3. [MINOR] [`_resolved_root_value`](../../../../skills/task-tree/scripts/cli.py#L68) masks autodetect failure by guessing `"superRA"`, so the packaged CLI errors with `parent directory does not exist: superRA` in a rootless directory while the direct scripts print the clean `could not auto-detect task root. Use --plan-root.` — make the failure messages consistent.
>    → implemented: mutation handlers route through [`_plan_root`](../../../../skills/task-tree/scripts/cli.py#L91), which exits 1 with `could not auto-detect task root. Use --root.` on autodetect failure instead of guessing `superRA` (test `test_autodetect_failure_reports_cleanly_not_missing_superra_dir`).
