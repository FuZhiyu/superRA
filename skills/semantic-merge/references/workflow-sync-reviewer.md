# Workflow Sync Reviewer Mode

Use when `integration-workflow` dispatches a generic sync reviewer after the workflow sync author lands the sync commit. Also load `sync-quality.md` and `sync-map-format.md`.

## Review Scope

Review the sync commit and its handoff artifacts before Integrate begins. The goal is to catch wrong branch intent, bad conflict resolution, missing user escalation, missing task-local Sync impact, or scope creep before downstream refactor work builds on it.

Inputs include:

- `BASE_REF`
- `PRE_SYNC_BASE_SHA`
- `BASE_HEAD_SHA`
- incoming range `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`
- sync commit SHA
- PLAN.md `## Sync Map`, if present

## Process

1. Verify the anchors: incoming intent comes from `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`; the post-sync governing baseline is `BASE_HEAD_SHA`.
2. Read incoming commits and diffs. Independently summarize incoming intent.
3. Read PLAN.md / RESULTS.md and independently summarize current-branch intent.
4. Inspect the sync commit diff. Confirm every kept, dropped, or synthesized hunk has a semantic rationale.
5. Walk `sync-quality.md` top to bottom.
6. Check the Sync Map against the diff and incoming intent. It should explain the branch-level thesis, not bury everything in task-local notes.
7. Check each affected task block has a compact `**Sync impact:**` pointer when Integrate needs task-specific propagation.
8. Confirm the sync author did not perform broad refactor, generated-output refresh, drift-test expectation update, or project-doc audit.

## Verdict

Two verdicts:

- `APPROVE`: no `[BLOCKING]` findings.
- `REVISE`: one or more `[BLOCKING]` findings.

When a Sync Map exists, record the verdict in `**Sync review status:**`. On REVISE, add `> **Sync review notes:**` under the Sync Map with specific findings and file/path evidence. On APPROVE, remove resolved sync-review notes and set `**Sync review status:** APPROVED`.

If no Sync Map exists and the sync is truly no-op/trivial, report the verdict without editing PLAN.md. If the review finds a material issue, create a minimal Sync Map with sync-review notes so the issue is in the handoff record before returning REVISE.

Commit only PLAN.md when you edit review status or notes.
