---
name: refactor-and-integrate
description: Utility skill (any phase). Use when creating drift tests, refactoring analysis code for codebase integration, or writing clean merge integration commits. Indexes the three gated checklists — Drift-Test Integrity, Codebase Integration, Merge Quality — carried in stage-scoped references and shared by implementer (self-check before commit) and reviewer (verification). Standalone-invokable — usable outside the integration phase for any refactoring task. Dispatched implementer/reviewer subagents load this skill when their Stage is `drift-test` or `integration` (per `superRA:using-superra` §Skill-Load Manifest).
---

# Refactor and Integrate

Utility skill carrying the domain knowledge for three closely related tasks in the INTEGRATE phase:

1. **Creating drift tests** that guard key results from unintended changes during refactoring or future modifications.
2. **Refactoring analysis code** for codebase integration — making the code fit the host project's conventions, utilities, and style without losing data discipline or results.
3. **Writing clean merge integration commits** that preserve intent and research integrity when combining branches.

Load per stage; implementer self-checks, reviewer verifies the same content. Gated checklists live in the three references named per Stage in `superRA:using-superra` §Skill-Load Manifest.

## Three Concurrent Disciplines — Principles

The three disciplines are **concurrent, not sequential**. A single integration pass typically exercises at least two of them, and the checklists compose: load every reference whose stage your task touches.

### 1. Drift-Test Integrity

Stage `drift-test` → load `references/drift-test-quality.md`.

### 2. Codebase Integration

Stage `integration` → load `references/codebase-integration.md`. For data-analysis work, also load `econ-data-analysis/references/integration.md` as the primary reference.

### 3. Merge Quality

Load `references/merge-quality.md` when merging — inside `integration-workflow` Phase B when `semantic-merge` is invoked for conflict resolution, or on any standalone `semantic-merge` dispatch. No dedicated manifest Stage; merge work rides on top of `Stage: integration` or runs standalone.

---

## The Load-Bearing Top Item

Every round of drift-test creation, refactoring, and merge integration shares one top-level constraint that sits above all three checklists:

- `[BLOCKING]` **Minimum net diff to the governing baseline.** Every round of drift-test creation, refactor, and merge integration touches only what approved task objectives, drift-test preservation, convention fit, handoff-doc coherence, documentation currency, and explicit reviewer-recorded allowed deltas demand. No unrelated cleanup, no speculative abstractions, no "while I'm here" edits.
  **Phase B / upstream-contract path:** implementer runs `git diff <frozen-merge-base>..HEAD` before each commit and reviews the cumulative diff; reviewer computes the same diff as evidence and prunes it hunk by hunk. The base branch is authoritative by default: upstream deletions and relocations remain deleted or relocated unless the task objective explicitly requires restoration and the reviewer recorded that allowed delta in the task-local note.
  **Other paths (drift-test stage, standalone refactor, standalone merge):** when no frozen Phase B anchor exists, use the task's governing git range or touched-file diff as the baseline and apply the same scope-pruning rule. No hunk survives just because it was convenient to edit while nearby.

This item frames every checklist item below it — any hunk in the governing baseline diff must be justifiable against one of the three disciplines' checklists, an approved task objective, or an explicit reviewer-recorded allowed delta. A hunk without one of those justifications is out of scope and must be reverted or re-justified.

Verdict protocol and implementer self-check: `references/codebase-integration.md §Reviewer Verdict Protocol`.
