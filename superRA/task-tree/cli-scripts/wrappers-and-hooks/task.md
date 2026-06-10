---
title: "Remove serve wrapper and hardcoded hook paths"
status: approved
depends_on:
  - unified-command-surface
tags: []
created: 2026-06-02
---

## Objective

Remove the generated dashboard wrapper and generation-time task-tree script paths from active hook entry points.

### Scope

- Change `task_create.py` so it no longer generates `superRA/serve`.
- Remove or deliberately deprecate the checked-in `superRA/serve` dashboard wrapper in this repo; do not replace it with another committed dashboard launcher.
- Update `superplan` task-tree creation instructions so planners do not generate `superRA/serve`.
- Update Claude/Codex/Cursor hook configs or hook shims that currently invoke `skills/task-tree/scripts/task_hook.py` directly, so normal hook execution uses the packaged CLI or a stable shim with no task-tree-local hardcoded plugin path.
- Document the development invocation for local package sources without requiring committed task trees to encode a developer's home directory or plugin cache path.

### Validation

- `uv run --project skills/task-tree superra dashboard --root superRA --no-open` invokes the dashboard from the live local checkout.
- New task roots created by `task_create.py` do not contain `serve`.
- No active instruction tells agents to generate `superRA/serve`.
- Hook tests still exercise task-tree reconciliation after task edits or task-tree filesystem changes.

## Planner Guidance

Keep hook compatibility separate from user dashboard launch. Hooks may need a harness-local shim during the transition, but task trees should not carry dashboard launchers.

## Results

### Key Findings

- Removed the checked-in `superRA/serve` dashboard launcher; no replacement dashboard launcher was added. The later repo-local `superRA/superra` CLI wrapper is a checkout-pinned local development entry point, not a generated task-tree dashboard launcher.
- Routed Claude `PostToolUse` task reconciliation through a stable hook shim instead of direct `skills/task-tree/scripts/task_hook.py` manifest commands ([../../../../hooks/hooks.json:52](../../../../hooks/hooks.json#L52), [../../../../hooks/hooks.json:62](../../../../hooks/hooks.json#L62)). The shim prefers the packaged `superra task hook post-tool-use` entry point via `uvx --from <plugin>/skills/task-tree` and falls back to the direct script for transition compatibility ([../../../../hooks/task-hook:21](../../../../hooks/task-hook#L21), [../../../../hooks/task-hook:37](../../../../hooks/task-hook#L37)).
- Removed the active superplan instruction to generate `superRA/serve`; new task-tree creation now only creates the top task and child task directories ([../../../../skills/superplan/SKILL.md:133](../../../../skills/superplan/SKILL.md#L133)).
- Documented the local development dashboard invocation as `uv run --project skills/task-tree superra dashboard --root superRA --no-open` and stated that task trees do not carry committed dashboard launchers ([../../../../skills/task-tree/SKILL.md:204](../../../../skills/task-tree/SKILL.md#L204), [../../../../skills/task-tree/references/internals.md:166](../../../../skills/task-tree/references/internals.md#L166)).

### Notes

- `task_create.py` already stopped generating `serve` in the approved `uv-package` dependency, so this task preserved that code path and verified it instead of re-editing it.
- Broader README and full command-surface documentation migration remains in the downstream `docs-tests-compat` task; this task updated only active instructions and hook entry points needed to remove the wrapper/hardcoded hook path.
- Generated role artifacts were not regenerated because canonical agent specs were untouched. If a later edit affects role specs or generated direct-mode/Codex agent files, the project generator is `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`; generated files are `skills/using-superRA/references/direct-mode-implementer.md`, `skills/using-superRA/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, and `.codex/agents/superra_reviewer.toml`.

### Verification

- `python3 -m json.tool hooks/hooks.json >/dev/null` — passed.
- `python3 -m py_compile skills/task-tree/scripts/cli.py skills/task-tree/scripts/task_hook.py skills/task-tree/scripts/task_create.py` — passed.
- `~/.venv/bin/python -m pytest skills/task-tree/scripts/test_task_tree.py::TestTaskCreate skills/task-tree/scripts/test_task_tree.py::TestTaskHook -v` — 24 passed.
- `uvx --from ./skills/task-tree superra task hook post-tool-use` — packaged hook entry point exited 0.
- `uvx --from ./skills/task-tree superra dashboard --root superRA --no-open --port 8997` — started Uvicorn on `http://0.0.0.0:8997`; stopped with Ctrl-C after startup.
- Focused grep for `superRA/serve` generation instructions across `skills`, `agents`, `hooks`, and `.codex` — no matches.
- `rg -n 'python3 "\$\{CLAUDE_PLUGIN_ROOT\}/skills/task-tree/scripts/task_hook\.py"|skills/task-tree/scripts/task_hook\.py' hooks skills agents .codex --glob '!**/.git/**'` — no matches.
- `test ! -e superRA/serve` — passed.

## Review Notes

Retrospective audit note (MINOR; status unchanged per orchestrator instruction):

> 1. [MINOR] Results cite [hooks/task-hook:21](../../../../hooks/task-hook#L21) / [hooks/task-hook:37](../../../../hooks/task-hook#L37) for the `uvx --from <plugin>/skills/task-tree` shim behavior, but the file now contains the `uv run --script` resolver shim from `cli-source-resolution` — the line-anchored citations point at unrelated code. Refresh the links or mark the paragraph as superseded.
