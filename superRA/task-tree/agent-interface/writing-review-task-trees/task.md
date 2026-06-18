---
title: "Writing Deep Review Task Trees"
status: implemented
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
- `bash tests/test-sync-integration-contract.sh` passed: 55 passed, 0 failed.
- `rg -n 'handoff doc|Project Conventions in the handoff|shared review-doc|review-doc|Long-form review retrofit|Retrofitting a Review Plan|PLAN-only|\.plan/' skills/writing tests/test-sync-integration-contract.sh -g '*.md' -g '*.sh'` returned only the contract test's assertion that `skills/superplan/SKILL.md` must not contain `PLAN-only`.
- `./superRA/superra task check` reported 0 errors and 2 pre-existing warnings: `task-tree/test-suite` depends on archived `auto-rebuild`, and `task-tree/dashboard/github-artifact-action` still carries temporary `## Sync Impact`.
