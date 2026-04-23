# Semantic Sync Quality Standards

Shared gated checklist for workflow Sync, sync review, and standalone semantic-merge. The canonical procedure (repo-state grounding, intent investigation with role classification, resolution planning, intent-changing escalation, stale-reference sweep) lives in `semantic-merge/SKILL.md §Shared Procedure`. Commit-shape constraints and format specs live in the owning mode references (`workflow-sync-author.md`, `standalone-merge.md`). This reference carries only the gated checklist both modes walk.

## Gated Checklist

Walk every item. `[BLOCKING]` items must be satisfied for the sync to be accepted; `[ADVISORY]` items may be flagged without blocking.

**Intent preservation:**

- `[BLOCKING]` Incoming intent understood from commits, diffs, docs, and caller context.
- `[BLOCKING]` Governing baseline and direction identified before conflict resolution.
- `[BLOCKING]` Each overlapping cluster classified by role (behavior/API, data/schema, docs/narrative, generated outputs, tests, config/build) before resolution.
- `[BLOCKING]` No silent losses from either side; dropped hunks have a documented rationale.
- `[BLOCKING]` No silent restorations of base-current deletions or relocations in workflow Sync.
- `[ADVISORY]` Synthesized changes are coherent and minimal.

**Scope boundary:**

- `[BLOCKING]` Exactly one minimal merge commit lands in both modes — no semantic propagation commits in semantic-merge's scope.
- `[BLOCKING]` Existing protection passes after the merge commit (drift tests + key-result coverage in workflow mode; existing tests and drift tests in standalone mode). Protection-pass is the unambiguous "coherent tree" test.
- `[BLOCKING]` Broader propagation — caller updates for renames, output regeneration, drift-test expectation updates, project-doc audit, broad refactor — is deferred, not performed in this skill.
- `[BLOCKING]` Deferred propagation is recorded in `## Sync Map` + task-local `**Sync impact:**` (workflow mode) or the `SEMANTIC_MERGE.md` File / Script Impact Map + Remaining Obligations (standalone mode), so `refactor-and-integrate` or the caller can satisfy it later.

**Intent integrity:**

- `[BLOCKING]` Intent-changing choices were escalated, logged per `handoff-doc §User Decisions Log`, and implemented as stated.
- `[BLOCKING]` Data-discipline artifacts and drift tests were preserved.
- `[BLOCKING]` Meaningful result changes were not silently accepted or re-expected.

**Handoff docs and merge records:**

- `[BLOCKING]` PLAN.md and RESULTS.md remain coherent after the sync when present.
- `[BLOCKING]` Task-structure changes were routed through `planning-workflow §User Feedback and Changing Plans` before adaptation proceeded.
- `[BLOCKING]` Affected task blocks have task-local `**Sync impact:**` annotations when workflow Sync leaves task-specific obligations.
- `[ADVISORY]` Routine handoff-doc conflict resolutions are summarized in the Sync Map.

**Verification:**

- `[BLOCKING]` No conflict markers remain.
- `[BLOCKING]` Stale-reference sweep covered labels, paths, docs, and generated outputs — not just absence of conflict markers.
- `[BLOCKING]` Targeted checks were run or explicitly reported as not applicable.
- `[BLOCKING]` Generated outputs needing regeneration are listed as post-sync obligations (Sync Map in workflow mode; merge record Follow-up column in standalone mode) — regeneration itself is deferred.
- `[BLOCKING]` Dirty-state stash (when used) was reported in the status return so the user can restore it.
