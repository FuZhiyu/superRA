---
title: "Planning Review Mode"
status: not-started
depends_on: [01-objective-guidance-task-anatomy, 02-objective-first-reviewer]
tags: []
created: 2026-06-01
---

## Objective

Formalize optional semantic planning review for thorough planning and explicit handoff-review requests. The planning reviewer evaluates the `.plan/` task tree itself before implementation: objective clarity, completeness, human readability, enough learned context from exploration, objective/guidance separation, dependency/coherence, handoff quality, and decomposition granularity.

Planning review must not use normal task implementation status. `status:` remains the implementation/review validity marker and must not be set to `approved` merely because a task was well planned. Use a root-level transient `## Planning Review Notes` section instead: on REVISE, the reviewer writes numbered `[BLOCKING]` / `[ADVISORY]` findings with links to affected task files; the planner fixes the tree inline; on re-review, fixed items are deleted; on APPROVE, the section is removed.

The review mode should be owned by `superplan` and its thorough-planning reference. If a staged reviewer dispatch is used, add `Stage: planning-review` to the `using-superra` manifest so unknown-stage dispatch errors do not fire. Add the minimum reviewer-role exception needed for planning review: tree-scoped input, no required git range, no task status edits, root-only `## Planning Review Notes` ownership for this mode.

## Planner Guidance

Likely files:
- `skills/superplan/SKILL.md`
- `skills/superplan/references/thorough-planning.md`
- `skills/using-superRA/SKILL.md` if adding `Stage: planning-review`
- `agents/reviewer.md` for the planning-review ownership exception
- generated reviewer artifacts after role-spec edits

Suggested dispatch shape:

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: planning-review
  Task tree: .plan
  Context: <exploration synthesis, inline or path>
  Review target: task-tree design, not implementation diff

  Additionally: Run task_check.py --plan-root .plan. Review semantic planning quality and write findings only to root ## Planning Review Notes.
```

`task_check.py` is a structural preflight, not the semantic review. The planning reviewer must receive the exploration synthesis; without it, the reviewer cannot judge whether the task tree captured enough learned context.

## Validation

- Run `python3 skills/task-system/scripts/task_check.py --plan-root .plan` on a representative task tree.
- Run generated-agent regeneration/checks if `agents/reviewer.md` changes.
- Exercise a small planning-review fixture or dry run: reviewer writes root `## Planning Review Notes`, planner fixes tree, re-review removes the notes without touching task statuses.
- Confirm quick/standard planning are not forced through planning review; thorough planning and explicit handoff review are the intended triggers.

## Results

