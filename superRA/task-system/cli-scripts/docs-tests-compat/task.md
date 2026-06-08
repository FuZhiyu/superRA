---
title: "Migrate docs and tests to packaged CLI"
status: approved
depends_on:
  - wrappers-and-hooks
tags: []
created: 2026-06-02
---

## Objective

Update active instructions, role references, tests, and compatibility notes so users and agents learn the packaged task-system CLI as the normal interface.

### Scope

- Update `skills/task-system/SKILL.md`, `skills/task-system/references/planning.md`, and `skills/task-system/references/internals.md` to document `superra task ...` commands instead of `<skill-dir>/scripts/...` for normal use.
- Update workflow and role references that mention direct task-system scripts, including `skills/superplan/SKILL.md`, `skills/using-superRA/references/main-agent.md`, `agents/implementer.md`, and `agents/reviewer.md`.
- Replace dashboard instructions with `superra dashboard`; remove instructions to run or generate `superRA/serve`.
- Keep historical task `## Results` records intact unless they are active instructions that would mislead future agents.
- Add or update tests for package entry points, no-serve task creation, dashboard asset loading from package data, and backwards-compatible direct script execution.
- Update README installation or usage text only where needed to teach `superra dashboard`.

### Validation

- `rg "superRA/serve|skills/task-system/scripts|plan_dashboard.py|task_read.py|task_query.py|task_check.py" skills agents hooks README.md` has only intentional compatibility or historical references.
- The packaged CLI tests and existing task-system tests pass.
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` passes if role specs or generated direct-mode references are affected.

## Planner Guidance

Apply the AGENTS.md DRY and Necessity gate to instruction edits. Replace path examples with the new command only where the line actively teaches behavior; do not churn archived task results just to remove old command names.

## Results

### Key Findings

- Active task-system instructions now teach packaged CLI commands for normal use: `superra task read/tree/frontier/dag/create/status/result/dep/rename/migrate` and `superra dashboard`, while direct script names remain only in internals, tests, script usage text, or compatibility references ([../../../../skills/task-system/SKILL.md](../../../../skills/task-system/SKILL.md), [../../../../skills/task-system/references/planning.md](../../../../skills/task-system/references/planning.md), [../../../../skills/task-system/references/internals.md](../../../../skills/task-system/references/internals.md)).
- Workflow, orchestration, and role references that teach agents how to inspect task trees now point at packaged commands, including implementer/reviewer task reads and planning-review diagnostics ([../../../../agents/implementer.md](../../../../agents/implementer.md), [../../../../agents/reviewer.md](../../../../agents/reviewer.md), [../../../../skills/using-superRA/references/main-agent.md](../../../../skills/using-superRA/references/main-agent.md), [../../../../skills/superimplement/SKILL.md](../../../../skills/superimplement/SKILL.md), [../../../../skills/superplan/SKILL.md](../../../../skills/superplan/SKILL.md)).
- Generated direct-mode references and project Codex agent files were refreshed from the canonical role specs with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` ([../../../../skills/using-superRA/references/direct-mode-implementer.md](../../../../skills/using-superRA/references/direct-mode-implementer.md), [../../../../skills/using-superRA/references/direct-mode-reviewer.md](../../../../skills/using-superRA/references/direct-mode-reviewer.md), [../../../../.codex/agents/superra_implementer.toml](../../../../.codex/agents/superra_implementer.toml), [../../../../.codex/agents/superra_reviewer.toml](../../../../.codex/agents/superra_reviewer.toml)).
- CLI tests now cover packaged dashboard export through `uv run --project ... superra`, assert task creation does not create a `serve` wrapper, and verify direct `task_query.py` script compatibility during the transition ([../../../../skills/task-system/scripts/test_cli.py](../../../../skills/task-system/scripts/test_cli.py)).

### Verification

- `uv run pytest skills/task-system/scripts/test_cli.py -q` — 18 passed.
- `uv run pytest skills/task-system/scripts/test_cli.py skills/task-system/scripts/test_task_system.py skills/task-system/scripts/test_dashboard.py skills/task-system/scripts/test_worktree_selector.py skills/task-system/scripts/tests/test_state_preservation.py -q` — 396 passed.
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` — generated project agent files and direct-mode role references are up to date.
- `rg "superRA/serve|skills/task-system/scripts|plan_dashboard.py|task_read.py|task_query.py|task_check.py" skills agents hooks README.md` — remaining hits are intentional compatibility or implementation references: task-system internals inventory, script usage text, script/test comments, direct-script compatibility tests, and vendor/template implementation notes; no active normal-use instruction still teaches `superRA/serve` or `<skill-dir>/scripts/...`.
- `python3 skills/task-system/scripts/task_check.py --plan-root superRA` — all checks passed.
- `git diff --check` — no whitespace errors.
