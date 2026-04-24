---
name: refactor-and-integrate
description: Utility skill (any phase). Use when creating drift tests, refactoring analysis code for codebase integration, reviewing post-sync branch quality, auditing project docs, or propagating task-local Sync impact obligations recorded by semantic-merge. Indexes the two gated checklists — Drift-Test Integrity and Codebase Integration — carried in stage-scoped references and shared by implementer (self-check before commit) and reviewer (verification). Standalone-invokable outside the full integration workflow for any refactor that needs consistent quality gates. Dispatched implementer/reviewer subagents load this skill when their Stage is `drift-test` or `integration` (per `superRA:using-superra` §Skill-Load Manifest).
---

# Refactor and Integrate

Tool skill teaching techniques for **codebase coherence** — fitting the resulting code into the host project. Paired with `semantic-merge`: run `semantic-merge` first to reach semantic coherence; this skill picks up to reach codebase coherence.

Three techniques; no prescribed order:

1. **Creating drift tests** that guard key results from unintended changes during Sync, refactoring, Finish, or future modifications.
2. **Codebase-fit refactoring** — aligning naming and utility reuse with host conventions, keeping PR-friendly diffs, walking up project docs, and minimizing net diff against the host.
3. **Propagating task-local Sync impact obligations** recorded by `semantic-merge` in `## Sync Map` and task-local `**Sync impact:**` fields.

Semantic coherence itself belongs to `superRA:semantic-merge`. This skill consumes task-local `**Sync impact:**` and referenced Sync Map clusters; it does not resolve branch syncs, review sync commits, or own sync commit discipline.

Load per stage; implementer self-checks and reviewer verifies the same checklist content.

## Disciplines

### 1. Drift-Test Integrity

Stage `drift-test` -> load `references/drift-test-quality.md` (coverage, tolerance calibration, independence, red-green cycle, test-format conventions, Red Flags).

### 2. Codebase Integration

Stage `integration` -> load `references/codebase-integration.md` (minimum surviving branch delta, Sync impact propagation, naming, utility reuse, PR quality, documentation currency, Project Doc Audit walk-up). For data-analysis work, also load `econ-data-analysis/references/integration.md` as the primary domain reference.

---

## The Load-Bearing Top Item

Every round of drift-test creation and post-sync integration shares one top-level constraint:

- `[BLOCKING]` **Minimum net diff to the governing baseline.** Touch only what approved task objectives, drift-test preservation, convention fit, handoff-doc coherence, documentation currency, task-local Sync impact obligations, and logged user decisions demand. No unrelated cleanup, speculative abstractions, or "while I'm here" edits.
  **Integration-workflow path:** after Sync, use `git diff <BASE_HEAD_SHA>..HEAD` as the evidence diff. `PRE_SYNC_BASE_SHA` is for semantic-merge intent investigation only; it is not the post-sync pruning baseline.
  **Standalone refactor path:** use the caller's governing git range or touched-file diff and apply the same hunk-by-hunk scope rule.

Any hunk in the governing diff must be justifiable against the loaded checklists, an approved task objective, a task-local Sync impact obligation, or a logged user decision. A hunk without one of those justifications is out of scope and must be reverted or re-justified in the handoff record before commit.

Verdict protocol and implementer self-check: `references/codebase-integration.md §Reviewer Verdict Protocol`.
