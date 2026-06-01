---
title: "Planning Review Mode"
status: revise
depends_on: [01-objective-guidance-task-anatomy, 02-objective-first-reviewer]
tags: []
created: 2026-06-01
---

## Objective

Formalize optional semantic planning review for thorough planning and explicit handoff-review requests. The planning reviewer evaluates an assigned task or subtree before implementation, with the review mode chosen by the orchestrator: handoff-readiness review checks whether the task is clear, complete, human-readable, internally consistent, and ready for an implementer; design review checks whether the proposed architecture, decomposition, assumptions, and domain reasoning are actually good enough for the objective.

Planning review uses the existing `## Review Notes` mechanism rather than a new note section, so dashboard hooks and task-comment conventions keep working. It must not use normal task implementation status: `status:` remains the implementation/review validity marker and must not be set to `approved` merely because a task was well planned. On REVISE, the reviewer writes numbered `[BLOCKING]` / `[ADVISORY]` findings in the assigned task's `## Review Notes`, linking affected child task files when the finding concerns a descendant; the planner fixes the task tree inline; on re-review, fixed items are deleted; on APPROVE, the `## Review Notes` section is removed.

The review mode should be owned by `superplan` and its thorough-planning reference, while the reviewer-role spec teaches reviewer agents what planning review can mean and how to write/read the task-local notes. If a staged reviewer dispatch is used, add `Stage: planning-review` to the `using-superra` manifest so unknown-stage dispatch errors do not fire. Add the minimum reviewer-role exception needed for planning review: task/subtree-scoped input, no required git range, no task status edits, and `## Review Notes` ownership limited to the assigned planning target.

## Planner Guidance

Likely files:
- `skills/superplan/SKILL.md`
- `skills/superplan/references/thorough-planning.md`
- `skills/using-superRA/SKILL.md` if adding `Stage: planning-review`
- `agents/reviewer.md` for planning-review modes and the ownership exception
- generated reviewer artifacts after role-spec edits

Suggested dispatch shape:

```text
Agent(subagent_type: "superRA:reviewer"):
  Stage: planning-review
  Task: <task path or root>
  Review mode: handoff-readiness | design-review
  Context: <exploration synthesis, inline or path>
  Review target: assigned task/subtree design, not implementation diff

  Additionally: Run task_check.py --plan-root superRA. Review the assigned task/subtree under the requested mode and write findings only to the assigned task's ## Review Notes.
```

`task_check.py` is a structural preflight, not the semantic review. The planning reviewer must receive enough context for the requested mode: exploration synthesis for handoff-readiness, and the relevant design rationale / domain context for design-review. The orchestrator can use a simple agent for this when the review is lightweight; the protocol still needs the reviewer-role instructions so the same mechanism works for thorough review.

## Validation

- Run `python3 skills/task-system/scripts/task_check.py --plan-root superRA` on a representative task tree.
- Run generated-agent regeneration/checks if `agents/reviewer.md` changes.
- Exercise a small planning-review fixture or dry run: reviewer writes `## Review Notes` on the assigned planning target, planner fixes tree, re-review removes the notes without touching task statuses.
- Confirm quick/standard planning are not forced through planning review; thorough planning and explicit handoff review are the intended triggers.

## Results

### Key Findings

- Added `Stage: planning-review` to the manifest so staged reviewer dispatches no longer trip the unknown-stage guard, with no additional required skills beyond the always-loaded baseline ([../../../skills/using-superRA/SKILL.md](../../../skills/using-superRA/SKILL.md)).
- Updated `superplan` and its thorough-planning reference so optional planning review is owned by planning, runs only for thorough depth or explicit handoff-review requests, supports `handoff-readiness` and `design-review`, uses assigned-target `## Review Notes`, and never changes implementation `status:` ([../../../skills/superplan/SKILL.md](../../../skills/superplan/SKILL.md), [../../../skills/superplan/references/thorough-planning.md](../../../skills/superplan/references/thorough-planning.md)).
- Updated the reviewer role with the planning-review exception: task/subtree-scoped input, optional/no git range, `[BLOCKING]` / `[ADVISORY]` findings in the assigned target's `## Review Notes`, no child-note edits, and no `status:` / `## Revision Notes` edits ([../../../agents/reviewer.md](../../../agents/reviewer.md)).
- Regenerated reviewer artifacts after the role-spec change with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`: [../../../.codex/agents/superra_reviewer.toml](../../../.codex/agents/superra_reviewer.toml) and [../../../skills/using-superRA/references/direct-mode-reviewer.md](../../../skills/using-superRA/references/direct-mode-reviewer.md). The generator direct-mode preface was adjusted so the regenerated direct-mode reviewer does not describe planning review as diff-scoped ([../../../skills/codex-superra-setup/scripts/sync_codex_agents.py](../../../skills/codex-superra-setup/scripts/sync_codex_agents.py)).

### Validation

- `python3 skills/task-system/scripts/task_check.py --plan-root superRA` — passed.
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` — passed; generated project agents and direct-mode role references are up to date.
- `uv run pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py` — passed, 6 tests.
- Disposable fixture under `/private/tmp/superra-planning-review-fixture` — `task_check.py` passed after adding `[BLOCKING]` / `[ADVISORY]` `## Review Notes` to an assigned task with `status: not-started`, and passed again after simulating planner fixes and removing `## Review Notes`; `status:` remained `not-started` throughout.

## Review Notes

1. MAJOR: The planning-review dispatch instructions do not preserve the repo's source-of-truth boundary for dispatch shape. [../../../skills/agent-orchestration/SKILL.md:105-136](../../../skills/agent-orchestration/SKILL.md#L105-L136) owns canonical dispatch templates and forbids `Additionally:` lines that restate role protocol, but [../../../skills/superplan/references/thorough-planning.md:120-131](../../../skills/superplan/references/thorough-planning.md#L120-L131) embeds a full reviewer dispatch template and an `Additionally:` tail that repeats planning-review note ownership. At the same time, [../../../agents/reviewer.md:24](../../../agents/reviewer.md#L24) describes the planning-review dispatch fields directly in the role spec, which is the AGENTS.md "here is what you will receive" anti-pattern. Fix by putting any required planning-review dispatch-shape exception in the dispatch-template owner (`agent-orchestration`) or by pointing there, and keep `superplan` to stage-specific choreography and `agents/reviewer.md` to reviewer behavior.
