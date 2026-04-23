# Semantic Sync Quality Standards

Shared checklist for workflow Sync, sync review, and standalone semantic-merge. Load this reference from the mode-specific semantic-merge references.

## Commit Structure

**Workflow Sync:** land exactly one sync commit when the confirmed base has advanced. The commit resolves conflicts, preserves intent, restores a coherent tree, writes or updates branch-level `## Sync Map` and task-local `**Sync impact:**` annotations when needed, and leaves post-sync refactor work to Integrate.

**Standalone semantic-merge:** separate intent-bearing propagation from the mechanical sync when both are non-trivial. A common shape is one sync commit followed by one or more semantic propagation commits. A single commit is acceptable only when the sync and propagation are both trivial enough for the commit message to describe honestly.

## Research-Meaningful Escalation

These choices must go to the researcher:

- Variable definitions used in analysis.
- Sample construction, filters, or data sources.
- Econometric specifications, controls, clustering, or model choices.
- Data-processing logic that changes analysis inputs.
- Analysis outputs, conclusions, or drift-test expectations.
- PLAN.md / RESULTS.md changes that add, remove, combine, or reorder tasks, flip DAG edges, or invalidate APPROVED status.

Ask with intent and consequences. Log the answer per `handoff-doc` §User Decisions Log before committing the resolution. If PLAN.md is absent, record the decision in the merge record or sync commit body.

## Governing Baseline

Identify the governing baseline before editing.

- **Workflow Sync:** `BASE_HEAD_SHA` is the current base branch head and governs post-sync minimum net diff. `PRE_SYNC_BASE_SHA` is historical evidence for incoming intent, not the post-sync diff baseline.
- **Standalone:** use the caller-declared governing baseline and direction. If the direction is ambiguous and affects results, scope, or architecture, ask before proceeding.

Base-current deletions and relocations survive by default in workflow Sync. Current-branch content that restores or contradicts base-current intent needs an approved task objective, logged user decision, or Sync Map / Sync impact obligation.

## Handoff-Doc Coherence

PLAN.md / RESULTS.md conflicts that change task structure are plan changes, not line conflicts. Escalate to `planning-workflow §User Feedback and Changing Plans` before the post-sync adaptation proceeds. Routine content conflicts inside unchanged task blocks can be resolved in the sync commit and recorded in the Sync Map when follow-up is needed.

## Gated Checklist

Walk every item. `[BLOCKING]` items must be satisfied for the sync to be accepted; `[ADVISORY]` items may be flagged without blocking.

**Intent preservation:**

- `[BLOCKING]` Incoming intent understood from commits, diffs, docs, and caller context.
- `[BLOCKING]` Governing baseline and direction identified before conflict resolution.
- `[BLOCKING]` No silent losses from either side; dropped hunks have a documented rationale.
- `[BLOCKING]` No silent restorations of base-current deletions or relocations in workflow Sync.
- `[ADVISORY]` Synthesized changes are coherent and minimal.

**Scope boundary:**

- `[BLOCKING]` Workflow Sync lands at most one sync commit.
- `[BLOCKING]` Workflow Sync restores a coherent tree without broad refactor, output regeneration, project-doc audit, or drift expectation updates.
- `[BLOCKING]` Standalone semantic-merge completes requested semantic propagation commits when the caller asked for full integration rather than sync-only.
- `[BLOCKING]` Post-sync obligations are recorded in `## Sync Map`, task-local `**Sync impact:**`, the standalone merge record, or the sync commit body.

**Research integrity:**

- `[BLOCKING]` Research-meaningful choices were escalated, logged, and implemented as stated.
- `[BLOCKING]` Data-discipline artifacts and drift tests were preserved.
- `[BLOCKING]` Meaningful result changes were not silently accepted or re-expected.

**Handoff docs and merge records:**

- `[BLOCKING]` PLAN.md and RESULTS.md remain coherent after the sync when present.
- `[BLOCKING]` Task-structure changes were routed through planning-workflow before adaptation proceeded.
- `[BLOCKING]` Affected task blocks have task-local `**Sync impact:**` annotations when workflow Sync leaves task-specific obligations.
- `[ADVISORY]` Routine handoff-doc conflict resolutions are summarized in the Sync Map.

**Verification:**

- `[BLOCKING]` No conflict markers remain.
- `[BLOCKING]` Targeted checks were run or explicitly reported as not applicable.
- `[BLOCKING]` Generated outputs are either regenerated in standalone mode or listed as post-sync obligations in workflow mode.
