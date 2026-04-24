---
name: refactor-and-integrate
description: Utility skill (any phase). Use when creating drift tests, refactoring analysis code for codebase integration, reviewing post-sync branch quality, auditing project docs, or using task-local Sync impact context recorded by semantic-merge. Indexes the two gated checklists — Drift-Test Integrity and Codebase Integration — carried in stage-scoped references and shared by implementer (self-check before commit) and reviewer (verification). Standalone-invokable outside the full integration workflow for any refactor that needs consistent quality gates. Dispatched implementer/reviewer subagents load this skill when their Stage is `drift-test` or `integration` (per `superRA:using-superra` §Skill-Load Manifest).
---

# Refactor and Integrate

Tool skill teaching techniques for **codebase coherence** — fitting the resulting code into the host project. Paired with `semantic-merge`: run `semantic-merge` first to reach semantic coherence; this skill picks up to reach codebase coherence.

Three techniques; no prescribed order:

1. **Creating drift tests** that guard key results from unintended changes during Sync, refactoring, Finish, or future modifications.
2. **Codebase-fit refactoring** — aligning naming and utility reuse with host conventions, keeping PR-friendly diffs, walking up project docs, and minimizing net diff against the host.
3. **Using task-local Sync impact context** recorded by `semantic-merge` in `## Sync Map` and task-local `**Sync impact:**` fields.

Semantic coherence itself belongs to `superRA:semantic-merge`. This skill reads task-local `**Sync impact:**` and referenced Sync Map clusters as context for the approved post-sync diff; it does not resolve branch syncs, review sync commits, or turn sync notes into independent refactor targets.

Load per stage; implementer self-checks and reviewer verifies the same checklist content.

## Disciplines

### 1. Drift-Test Integrity

Stage `drift-test` → load `references/drift-test-quality.md`.

### 2. Codebase Integration

Stage `integration` → load `references/codebase-integration.md`. For data-analysis work, also load `econ-data-analysis/references/integration.md` as the primary domain reference.

---

## The Load-Bearing Top Item

Every round of drift-test creation and post-sync integration shares one top-level constraint:

- `[BLOCKING]` **Minimum net diff to the governing baseline.** Touch only what approved task objectives, drift-test preservation, convention fit, handoff-doc coherence, documentation currency, logged user decisions, and codebase-coherence review demand. Use Sync impact as context for existing post-sync hunks, not as a separate work queue. No unrelated cleanup, speculative abstractions, or "while I'm here" edits.
  **Integration-workflow path:** after Sync, use `git diff <BASE_HEAD_SHA>..HEAD` as the evidence diff. `PRE_SYNC_BASE_SHA` is for semantic-merge intent investigation only; it is not the post-sync pruning baseline.
  **Standalone refactor path:** use the caller's governing git range or touched-file diff and apply the same hunk-by-hunk scope rule.

Review the governing diff line by line. Guard against unrelated cleanup, formatting churn, stale branch-side restorations, and any hunk that lacks a current justification. Each hunk must be justifiable against the loaded checklists, an approved task objective, approved semantic-sync context, or a logged user decision; otherwise it is out of scope and must be reverted or re-justified in the handoff record before commit.

Verdict protocol and implementer self-check: `references/codebase-integration.md §Reviewer Verdict Protocol`.
