# Workflow Sync Reviewer Mode

Workflow sync reviewer mode verifies the sync commit chain before Integrate. Walk `semantic-merge/SKILL.md` §Semantic Coherence Checklist; use `workflow-sync-author.md` for the workflow boundary and the `## Sync Impact` format.

## Review Scope

Review the sync commits (merge commit plus any propagation commits) before Integrate begins. The goal is to catch wrong branch intent, bad conflict resolution, missing user escalation, misleading `## Sync Impact` context, or scope creep before downstream refactor work builds on it.

Required inputs:

- `BASE_REF`
- `PRE_SYNC_BASE_SHA`
- `BASE_HEAD_SHA`
- incoming range `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`
- Sync commits (merge commit SHA plus any propagation-commit SHAs)

## Process

1. Verify the anchors: incoming intent comes from `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`; the post-sync governing baseline is `BASE_HEAD_SHA`.
2. Read incoming commits and diffs. Independently summarize incoming intent.
3. Read the `superRA/` task tree and independently summarize current-branch intent.
4. Inspect the sync commits (merge commit plus any propagation commits) and their combined diff. Confirm every kept, dropped, or synthesized hunk has a semantic rationale, classified by role per `SKILL.md §Shared Steps` step 2.
5. Walk `SKILL.md §Semantic Coherence Checklist` top to bottom.
6. Confirm the branch-level thesis is carried by the sync commit messages (the git log), not buried in task-local sections.
7. Check each affected task carries a `## Sync Impact` section when Integrate needs task-specific context to understand the post-sync diff.
8. Confirm the scope boundary. Generated outputs within the merge's semantic reach should be regenerated (or escalated per `SKILL.md §Shared Steps` step 4 and recorded) — flag if the author skipped regeneration or silently re-expected drift-test results. Flag any codebase-coherence work performed in the sync commit chain, and any `## Sync Impact` note that presents unresolved semantic work as an Integrate target.
9. Confirm the stale-reference sweep covered labels, paths, docs, and generated outputs — not just absence of conflict markers.

## Verdict

Two verdicts:

- `APPROVE`: no `[BLOCKING]` findings.
- `REVISE`: one or more `[BLOCKING]` findings.

Sync-review findings use the standard review mechanism. A task-scoped finding goes in that affected task's `## Review Notes` with specific file/path evidence; a branch-level finding with no single task home rides the REVISE return and is fixed before re-review. Commit only the task files whose `## Review Notes` you edit. Return the verdict plus the reviewed sync commit SHA(s).
