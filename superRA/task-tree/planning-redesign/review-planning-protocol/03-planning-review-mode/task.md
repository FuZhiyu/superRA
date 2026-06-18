---
title: "Planning Review Mode"
status: approved
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
- `skills/using-superra/SKILL.md` if adding `Stage: planning-review`
- `agents/reviewer.md` for planning-review modes and the ownership exception
- generated reviewer artifacts after role-spec edits

Suggested dispatch shape: use `agent-orchestration` §Dispatch Templates for the canonical planning-review reviewer template.

`task_check.py` is a structural preflight, not the semantic review. The planning reviewer must receive enough context for the requested mode: exploration synthesis for handoff-readiness, and the relevant design rationale / domain context for design-review. The orchestrator can use a simple agent for this when the review is lightweight; the protocol still needs the reviewer-role instructions so the same mechanism works for thorough review.

## Validation

- Run `python3 skills/task-tree/scripts/task_check.py --plan-root superRA` on a representative task tree.
- Run generated-agent regeneration/checks if `agents/reviewer.md` changes.
- Exercise a small planning-review fixture or dry run: reviewer writes `## Review Notes` on the assigned planning target, planner fixes tree, re-review removes the notes without touching task statuses.
- Confirm quick/standard planning are not forced through planning review; thorough planning and explicit handoff review are the intended triggers.

## Results

### Key Findings

- Added `Stage: planning-review` to the manifest so staged reviewer dispatches no longer trip the unknown-stage guard, with no additional required skills beyond the always-loaded baseline ([../../../skills/using-superra/SKILL.md](../../../../../skills/using-superra/SKILL.md)).
- Updated `superplan` and its thorough-planning reference so optional planning review is owned by planning, runs only for thorough depth or explicit handoff-review requests, supports `handoff-readiness` and `design-review`, uses assigned-target `## Review Notes`, and never changes implementation `status:` ([../../../skills/superplan/SKILL.md](../../../../../skills/superplan/SKILL.md), [../../../skills/superplan/references/thorough-planning.md](../../../../../skills/superplan/references/thorough-planning.md)).
- Integration review fix: moved the planning-review dispatch-shape exception to `agent-orchestration`, left `superplan` / thorough-planning responsible for planning choreography and mode selection, and removed dispatch-field description from the reviewer role ([../../../skills/agent-orchestration/SKILL.md](../../../../../skills/agent-orchestration/SKILL.md), [../../../skills/superplan/SKILL.md](../../../../../skills/superplan/SKILL.md), [../../../agents/reviewer.md](../../../../../agents/reviewer.md)).
- Updated the reviewer role with the planning-review exception: task/subtree-scoped input, optional/no git range, `[BLOCKING]` / `[ADVISORY]` findings in the assigned target's `## Review Notes`, no child-note edits, and no `status:` / `## Revision Notes` edits ([../../../agents/reviewer.md](../../../../../agents/reviewer.md)).
- Regenerated reviewer artifacts after the role-spec change with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`: [../../../.codex/agents/superra_reviewer.toml](../../../../../.codex/agents/superra_reviewer.toml) and [../../../skills/using-superra/references/direct-mode-reviewer.md](../../../../../skills/using-superra/references/direct-mode-reviewer.md). The generator direct-mode preface was adjusted so the regenerated direct-mode reviewer does not describe planning review as diff-scoped ([../../../skills/codex-superra-setup/scripts/sync_codex_agents.py](../../../../../skills/codex-superra-setup/scripts/sync_codex_agents.py)).

### Validation

- `python3 skills/task-tree/scripts/task_check.py --plan-root superRA` — passed.
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` — passed; generated project agents and direct-mode role references are up to date.
- `uv run pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py` — passed, 6 tests.
- Disposable fixture under `/private/tmp/superra-planning-review-fixture` — `task_check.py` passed after adding `[BLOCKING]` / `[ADVISORY]` `## Review Notes` to an assigned task with `status: not-started`, and passed again after simulating planner fixes and removing `## Review Notes`; `status:` remained `not-started` throughout.
