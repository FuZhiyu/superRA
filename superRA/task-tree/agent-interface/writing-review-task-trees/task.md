---
title: "Writing Deep Review Task Trees"
status: approved
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Redesign the writing domain's long-form/deep review instructions so multi-lane academic review creates a review task subtree instead of a single review document. Update skills/writing/SKILL.md and writing references so large writing review routes through superplan to create lane/perspective tasks, reviewers record findings in task-local ## Review Notes, and any follow-up polish consumes accepted task-local review notes. Preserve the task-tree contract: status is task-local, review-only trees may skip implementer states, ## Results is not a shared review-file substitute, and task objectives carry binding target/lane/build/audience context while ## Planner Guidance remains advisory. Sweep stale handoff-doc, shared review-doc, single review.md/file, PLAN.md/RESULTS.md-era language in the touched writing surfaces; leave generic dispatch mechanics owned by agent-orchestration and role protocol owned by agents/reviewer.md. Verify with targeted grep and task-tree validation.

## Planner Guidance

Likely files: skills/writing/SKILL.md, references/planning.md, references/long-form-review.md, references/review.md, references/polish.md, references/draft.md, references/refactor-and-compile.md, references/integration.md, and skills/writing/CLAUDE.md if ownership text changes. Apply the repo DRY/Necessity gate line by line; point to task-tree/task-file-contract instead of restating generic task mechanics.

## Results

### Key Findings
- Replaced the writing vertical's old long-form review retrofit language with a review-only task-tree path. Multi-lane, deep, full-paper, and pre-submission review now create lane/perspective tasks whose durable findings live in task-local `## Review Notes`.
- Removed the stale shared review-doc protocol from [review.md](../../../../skills/writing/references/review.md) and [long-form-review.md](../../../../skills/writing/references/long-form-review.md). The long-form reference now explicitly forbids a shared `review.md` / equivalent findings file.
- Updated the writing planning marker in [planning.md](../../../../skills/writing/references/planning.md) to `**Writing workflow:** Review-only task tree`, and updated the sync/integration contract test to require that marker.
- Replaced handoff-doc-era convention pointers with manuscript-governing-task / task-tree wording across the writing skill and relevant references.

### Verification
- `bash tests/test-sync-integration-contract.sh` passed: 56 passed, 0 failed.
- `rg -n 'handoff' skills/writing/references -g '*.md'` returned no matches.
- `rg -n 'handoff doc|Project Conventions in the handoff|shared review-doc|review-doc|Long-form review retrofit|Retrofitting a Review Plan|PLAN-only|\.plan/' skills/writing tests/test-sync-integration-contract.sh -g '*.md' -g '*.sh'` returned only the contract test's assertion that `skills/superplan/SKILL.md` must not contain `PLAN-only`.
- `./superRA/superra task check` reported 0 errors and 2 warnings before Integrate cleanup: `task-tree/test-suite` depends on archived `auto-rebuild`, and `task-tree/dashboard/github-artifact-action` still carried a temporary `## Sync Impact`. Integrate closeout removed the stale temporary section.

**Final diff self-check:** `git diff 5af4c27d571cca58ee6187c248cf83f41ac641c0..HEAD`; surviving change classes are writing review-task workflow instructions, stale-handoff wording removal, sync-propagation of the minor re-review exception into workflow summaries, task/status records, and the required Integrate cleanup of a stale temporary `## Sync Impact` section. Suspicious hunk justifications: `skills/*` edits are justified by the approved task objective plus sync propagation from `better-handoff`; approved task-file edits are status/results/workflow-record updates required by superRA gates; the dashboard artifact task edit only removes temporary integration scaffold caught by `superra task check --category sync-impact`.

### Integration Closeout
- Synced onto `better-handoff` at `BASE_HEAD_SHA=5af4c27d571cca58ee6187c248cf83f41ac641c0`; the only incoming change was the minor re-review exception in `agent-orchestration`, propagated into `superimplement` and `superintegrate` summaries.
- Integration review approved the surviving diff as scoped to this task, sync propagation, workflow records, and required temporary Sync Impact cleanup.
- Permanent evidence: `tests/test-sync-integration-contract.sh` protects the review-only task-tree marker and stale-wording sweep; the full task-tree suite passed after sync.
