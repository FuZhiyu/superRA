---
title: "Objective vs Planner Guidance Task Anatomy"
status: not-started
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

