---
title: "Objective vs Planner Guidance Task Anatomy"
status: implemented
depends_on: []
tags: []
created: 2026-06-01
---

## Objective

Introduce an optional `## Planner Guidance` task-body section and clarify that `## Objective` is the authoritative contract for implementation and review. Update the task-system planning reference and planning workflow text so planners put hard deliverables, validation criteria, constraints, user/methodology decisions, and fixed `script` / `input` / `output` expectations in `## Objective` or frontmatter, while placing suggested routes, candidate files, prior exploration notes, likely sequence, and implementation hints in `## Planner Guidance`.

The change must keep existing task files valid. Do not bulk-migrate old objectives automatically; split objective/guidance opportunistically when a task is created or materially rewritten. Preserve the task system's free-form section behavior: arbitrary `##` sections are valid, rendered in order, and read through `task_read.py`.

Update implementer/reviewer role specs only where the distinction changes behavior: implementers may deviate from `## Planner Guidance` when a better route satisfies `## Objective`; reviewers must not fail a task merely because guidance was not followed, but should flag guidance that is misleading, contradicts the objective, or would fail to achieve it.

## Planner Guidance

Likely files:
- `skills/task-system/references/planning.md`
- `skills/superplan/SKILL.md`
- `agents/implementer.md`
- `agents/reviewer.md`
- possibly `skills/task-system/SKILL.md` if the consumer-facing task format needs a concise pointer
- possibly `skills/task-system/scripts/task_create.py` if the task scaffolder should support a guidance argument or template slot

Keep `## Planner Guidance` optional. A validator warning for missing guidance is not desirable; empty guidance should also not be required. If `task_create.py` is changed, prefer an optional CLI argument rather than forcing all created tasks to carry an empty section.

## Validation

- Run the task-system tests that cover section parsing, task creation, task reading, and dashboard rendering.
- Confirm arbitrary unknown sections remain preserved and displayed.
- Confirm no generated direct-mode or Codex agent file was hand-edited.
- Run a DRY/Necessity self-check on every added instruction line in `skills/*` and `agents/*`.

## Results

### Key Findings
- Added the optional `## Planner Guidance` task-body section as advisory planner-owned context while keeping `## Objective` authoritative for implementation and review ([../../../skills/task-system/references/planning.md](../../../skills/task-system/references/planning.md), [../../../skills/task-system/SKILL.md](../../../skills/task-system/SKILL.md), [../../../skills/superplan/SKILL.md](../../../skills/superplan/SKILL.md)).
- Updated canonical role behavior so implementers may deviate from guidance when they satisfy the objective, and reviewers evaluate objective success rather than guidance adherence ([../../../agents/implementer.md](../../../agents/implementer.md), [../../../agents/reviewer.md](../../../agents/reviewer.md)).
- Added optional `--guidance` support to `task_create.py`; omitted guidance still creates no empty `## Planner Guidance` section ([../../../skills/task-system/scripts/task_create.py](../../../skills/task-system/scripts/task_create.py)).

### Validation
- `uv run pytest skills/task-system/scripts/test_task_system.py skills/task-system/scripts/test_dashboard.py skills/task-system/scripts/tests/test_state_preservation.py skills/codex-superra-setup/scripts/test_sync_codex_agents.py` passed: 310 tests.
- `python3 skills/task-system/scripts/task_check.py --plan-root .plan` passed: all checks passed, no issues found.
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` passed: generated agent files and direct-mode role references are up to date.
- DRY/Necessity self-check: added instruction lines change behavior at the owner surfaces only; no validator requirement was added for missing or empty `## Planner Guidance`.

### Generated Artifacts
- Regenerated via `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`.
- Generated outputs updated from canonical role specs: [../../../skills/using-superRA/references/direct-mode-implementer.md](../../../skills/using-superRA/references/direct-mode-implementer.md), [../../../skills/using-superRA/references/direct-mode-reviewer.md](../../../skills/using-superRA/references/direct-mode-reviewer.md), [../../../.codex/agents/superra_implementer.toml](../../../.codex/agents/superra_implementer.toml), [../../../.codex/agents/superra_reviewer.toml](../../../.codex/agents/superra_reviewer.toml).

### Notes
- Root `.plan/task.md` has no `## Conventions` section; implementation used repo `AGENTS.md`, the task's `## Planner Guidance`, and owning files as on-demand convention sources.
