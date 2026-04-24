# Workflow Sync Reviewer Mode

Use when `integration-workflow` dispatches a generic sync reviewer after the workflow sync author lands the sync commits (merge commit plus any propagation commits). Walk the Shared Steps and §Semantic Coherence Checklist in `semantic-merge/SKILL.md` — the checklist is the gated verification list; the §Scope boundary within it is the stopping rule. The reviewer inherits the Workflow Sync scope boundary from `workflow-sync-author.md §Boundary`. For the Sync Map and task-local Sync impact shape the author produced, see `workflow-sync-author.md §Workflow Sync Map Format` and `§Task-Local Sync Impact Format`.

## Review Scope

Review the sync commits (merge commit plus any propagation commits) and their handoff artifacts before Integrate begins. The goal is to catch wrong branch intent, bad conflict resolution, missing user escalation, misleading task-local Sync impact context, or scope creep before downstream refactor work builds on it.

Inputs include:

- `BASE_REF`
- `PRE_SYNC_BASE_SHA`
- `BASE_HEAD_SHA`
- incoming range `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`
- Sync commits (merge commit SHA plus any propagation-commit SHAs)
- PLAN.md `## Sync Map`, if present

## Process

1. Verify the anchors: incoming intent comes from `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`; the post-sync governing baseline is `BASE_HEAD_SHA`.
2. Read incoming commits and diffs. Independently summarize incoming intent.
3. Read PLAN.md / RESULTS.md and independently summarize current-branch intent.
4. Inspect the sync commits (merge commit plus any propagation commits) and their combined diff. Confirm every kept, dropped, or synthesized hunk has a semantic rationale, classified by role per `SKILL.md §Shared Steps` step 2.
5. Walk `SKILL.md §Semantic Coherence Checklist` top to bottom.
6. Check the Sync Map against the diff and incoming intent. It should explain the branch-level thesis, not bury everything in task-local notes.
7. Check each affected task block has a compact `**Sync impact:**` pointer when Integrate needs task-specific context to understand the post-sync diff.
8. Confirm scope boundary at the semantic-vs-codebase-coherence line. Generated outputs within the merge's semantic reach should be regenerated (or escalated per `SKILL.md §Shared Steps` step 4 and recorded) — flag if the author skipped regeneration or silently re-expected drift-test results. Codebase-coherence work — convention fit, utility reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff against the host — should not be performed in the sync commit chain; Sync notes may explain context but must not present unresolved semantic work as an Integrate target.
9. Confirm the stale-reference sweep covered labels, paths, docs, and generated outputs — not just absence of conflict markers.

## Verdict

Two verdicts:

- `APPROVE`: no `[BLOCKING]` findings.
- `REVISE`: one or more `[BLOCKING]` findings.

When a Sync Map exists, record the verdict in `**Sync review status:**`. On REVISE, add `> **Sync review notes:**` under the Sync Map with specific findings and file/path evidence. On APPROVE, remove resolved sync-review notes and set `**Sync review status:** APPROVED`.

If no Sync Map exists and the sync is truly no-op/trivial, report the verdict without editing PLAN.md. If the review finds a material issue, create a minimal Sync Map with sync-review notes so the issue is in the handoff record before returning REVISE.

Commit only PLAN.md when you edit review status or notes.
