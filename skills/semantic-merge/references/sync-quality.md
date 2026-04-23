# Semantic Sync Quality Standards

Shared reference for semantic sync work and review. Load when `Stage:` is `sync`, when using `semantic-merge` standalone, or when reviewing a sync commit as part of post-sync integration review.

## Commit Structure

A semantic sync can land as one commit or many depending on the caller.

**Integration-workflow Sync:** exactly one sync commit. The commit resolves conflicts, preserves intent, restores a coherent tree, and records post-sync obligations in `## Sync Map`. Broader adaptation is left to the Integrate step.

**Standalone semantic-merge:** separate intent-bearing adaptation from sync when both are non-trivial. A common shape is one sync commit followed by one or more adaptation commits. A single commit is acceptable only when the sync and adaptation are both trivial enough for the commit message to describe honestly.

## Research-Meaningful Escalation

These choices must go to the researcher:

- Variable definitions used in analysis.
- Sample construction, filters, or data sources.
- Econometric specifications, controls, clustering, or model choices.
- Data-processing logic that changes analysis inputs.
- Analysis outputs, conclusions, or drift-test expectations.
- PLAN.md / RESULTS.md changes that add, remove, combine, or reorder tasks, flip DAG edges, or invalidate APPROVED status.

Ask with intent and consequences. Log the answer per `handoff-doc` §User Decisions Log before committing the resolution. If PLAN.md is absent, record the decision in the sync commit body.

## Governing Baseline

Identify the governing baseline before editing.

- **Integration-workflow:** `BASE_HEAD_SHA` is the current base branch head and governs post-sync minimum net diff. `PRE_SYNC_BASE_SHA` is historical evidence for incoming intent, not the post-sync diff baseline.
- **Standalone:** use the caller-declared governing baseline and direction. If the direction is ambiguous and affects results, scope, or architecture, ask before proceeding.

Base deletions and relocations survive by default in integration-workflow. Current-branch content that restores or contradicts base-current intent needs an approved task objective, logged user decision, or Sync Map obligation.

## Sync Map

Write `## Sync Map` in PLAN.md when there is material overlap, a conflict, a user decision, or a post-sync obligation. Omit it for no-op or trivial syncs with no obligations. If PLAN.md is absent, put the same content in the sync commit body.

Format:

```markdown
## Sync Map

**Base branch:** `origin/main`
**Pre-sync merge base:** `<PRE_SYNC_BASE_SHA>`
**Synced base head:** `<BASE_HEAD_SHA>`
**Incoming range:** `<PRE_SYNC_BASE_SHA>..origin/main`
**Sync commit:** `<SYNC_COMMIT_SHA>`

> **Sync cluster (YYYY-MM-DD):** commits `<sha...>`; paths `<paths>`; affects `<tasks/files>`.
> **Incoming intent:** <plain-language purpose of incoming/base changes>.
> **Sync resolution:** <what the sync commit kept, dropped, or synthesized>.
> **Post-sync obligations:** <stale paths, APIs, docs, generated outputs, tests, or task areas for Integrate>.
> **User decision:** <summary or "None">.
```

The Sync Map is temporary scaffolding. The integration reviewer consumes it, refactor implementers satisfy its obligations, and the orchestrator removes it when Integrate closes.

## Handoff-Doc Coherence

PLAN.md / RESULTS.md conflicts that change task structure are plan changes, not line conflicts. Escalate to `planning-workflow §User Feedback and Changing Plans` before the post-sync adaptation proceeds. Routine content conflicts inside unchanged task blocks can be resolved in the sync commit and recorded in the Sync Map when follow-up is needed.

## Gated Checklist

Walk every item. `[BLOCKING]` items must be satisfied for the sync to be accepted; `[ADVISORY]` items may be flagged without blocking.

**Intent preservation:**

- `[BLOCKING]` Incoming intent understood from commits, diffs, docs, and caller context.
- `[BLOCKING]` Governing baseline and direction identified before conflict resolution.
- `[BLOCKING]` No silent losses from either side; dropped hunks have a documented rationale.
- `[BLOCKING]` No silent restorations of base-current deletions or relocations in integration-workflow.
- `[ADVISORY]` Synthesized changes are coherent and minimal.

**Scope boundary:**

- `[BLOCKING]` Integration-workflow Sync lands at most one sync commit.
- `[BLOCKING]` Sync commit restores a coherent tree without broad refactor, output regeneration, project-doc audit, or drift expectation updates.
- `[BLOCKING]` Post-sync obligations are recorded in `## Sync Map` or the sync commit body.

**Research integrity:**

- `[BLOCKING]` Research-meaningful choices were escalated, logged, and implemented as stated.
- `[BLOCKING]` Data-discipline artifacts and drift tests were preserved.
- `[BLOCKING]` Meaningful result changes were not silently accepted or re-expected.

**Handoff docs:**

- `[BLOCKING]` PLAN.md and RESULTS.md remain coherent after the sync.
- `[BLOCKING]` Task-structure changes were routed through planning-workflow before adaptation proceeded.
- `[ADVISORY]` Routine handoff-doc conflict resolutions are summarized in the Sync Map.

**Verification:**

- `[BLOCKING]` No conflict markers remain.
- `[BLOCKING]` Targeted checks were run or explicitly reported as not applicable.
- `[BLOCKING]` Generated outputs are either regenerated or listed as post-sync obligations.
