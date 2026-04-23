# Workflow Sync Author Mode

Use when `integration-workflow` dispatches a generic sync author to bring the current branch onto a confirmed base. Also load `sync-quality.md` and `sync-map-format.md`.

## Inputs

The dispatch supplies:

- `BASE_REF`
- `PRE_SYNC_BASE_SHA`
- `BASE_HEAD_SHA`
- incoming range `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`
- operation direction, defaulting to merging the confirmed base into the current branch

## Process

1. Confirm the worktree is clean enough to sync. If dirty state is unrelated, preserve it with a reversible named stash and report it.
2. Read PLAN.md header, `## Decisions`, any existing `## Sync Map`, RESULTS.md, and the incoming range.
3. Summarize current-branch intent from PLAN.md / RESULTS.md. Do not duplicate that full summary in task blocks.
4. Summarize incoming intent from commits, diffs, and docs in `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`.
5. Build a branch-level Sync Map when there is material overlap, a conflict, a user decision, sync-review carryover, or a post-sync obligation.
6. Run the requested sync operation after intent research. For the normal workflow path, merge `BASE_REF` into the current branch.
7. Resolve conflicts by intent. Preserve base-current deletions and relocations by default unless an approved task objective, logged user decision, or Sync Map / Sync impact obligation justifies restoring branch-side content.
8. Add task-local `**Sync impact:**` annotations only to affected task blocks. Keep them short and point back to the relevant Sync Map cluster.
9. Land exactly one sync commit. Include code, resolved docs, PLAN.md Sync Map, and task-local Sync impact annotations in the same commit.
10. Run targeted checks where cheap and relevant. Leave generated-output refreshes, broad refactor, drift-test expectation updates, and project-doc audit for Integrate.

## Status Return

Return one of:

- `DONE`: sync commit landed and is ready for sync review.
- `DONE_WITH_CONCERNS`: sync landed, but non-blocking concerns remain for the reviewer or Integrate.
- `NEEDS_CONTEXT`: missing upstream context or a research-owned decision is needed.
- `BLOCKED`: the sync cannot proceed safely.

Report the sync commit SHA, Sync Map location or why none was needed, task-local Sync impact annotations added, checks run, and post-sync obligations.
