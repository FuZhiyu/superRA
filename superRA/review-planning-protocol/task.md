---
title: "Review and Planning Protocol"
status: revise
depends_on: []
tags: []
created: 2026-06-01
---

## Objective

Improve superRA's planning and review workflow so reviewers evaluate whether work genuinely achieves the task objective, using their general research judgment and the active domain discipline together, not only whether it passes an enumerated checklist. Add an explicit task-authoring split between the authoritative `## Objective` and advisory `## Planner Guidance`, and formalize optional planning review for thorough planning / handoff scenarios.

This work must preserve the repo's source-of-truth boundaries:
- canonical reviewer behavior lives in `agents/reviewer.md`;
- canonical implementer behavior lives in `agents/implementer.md`;
- task anatomy and objective/guidance semantics live in `skills/task-system/references/planning.md`;
- superplan owns planning-phase choreography and optional planning review;
- generated Codex agents and direct-mode role references are regenerated, never hand-edited.

Success means a future implementer/reviewer pair can distinguish binding objectives from planner suggestions, reviewer approval reflects broad task-local judgment plus mandatory domain gates, and thorough planning can run a semantic planning-review pass without overloading implementation task statuses.

## Planner Guidance

Exploration from the design review identified three implementation slices:
- First update task anatomy so `## Objective` is the normative contract and optional `## Planner Guidance` holds non-binding starting points.
- Then update reviewer behavior so it reviews the objective, declared frontmatter outputs, implementer results, and the diff as a coherent whole, using the reviewer's own judgment and the active domain gates together.
- Finally add a `planning-review` reviewer mode owned by superplan, using task-local `## Review Notes` on the assigned planning target rather than normal task `status:`.

Avoid broad rewrites of domain skills. The domain skills own the specific gates; this work should only clarify how generic workflow/role protocols compose with those gates.

## Results

## Review Notes

1. MAJOR: [../../skills/refactor-and-integrate/SKILL.md:54-55](../../skills/refactor-and-integrate/SKILL.md#L54-L55) requires a fresh final diff self-check trail in the assigned task's `## Results`, but this parent task's [task.md:31](task.md#L31) `## Results` section is empty. Fix by recording the current `git diff 75a86ccebd0ec37a0a9e904f0fd5b824752cf6f1..HEAD` self-check, surviving change classes, suspicious hunk justifications for the `skills/*` / `agents/*` instruction edits and generated artifacts, and any pruned/unjustified hunks.
