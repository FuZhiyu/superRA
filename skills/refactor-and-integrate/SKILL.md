---
name: refactor-and-integrate
description: Utility skill (any phase). Use when creating drift tests, refactoring analysis code for codebase integration, or writing clean merge integration commits. Indexes the three gated checklists — Drift-Test Integrity, Codebase Integration, Merge Quality — carried in stage-scoped references and shared by implementer (self-check before commit) and reviewer (verification). Standalone-invokable — usable outside the integration phase for any refactoring task. Dispatched implementer/reviewer subagents load this skill when their Stage is `drift-test`, `integration`, or `merge` (per `superRA:using-superRA` §Skill-Load Manifest).
---

# Refactor and Integrate

Utility skill carrying the domain knowledge for three closely related tasks in the INTEGRATE phase:

1. **Creating drift tests** that guard key results from unintended changes during refactoring or future modifications.
2. **Refactoring analysis code** for codebase integration — making the code fit the host project's conventions, utilities, and style without losing data discipline or results.
3. **Writing clean merge integration commits** that preserve intent and research integrity when combining branches.

This is a utility skill, not a workflow skill. Workflow skills (`superRA:integration-workflow`, `superRA:merge-workflow`) own procedural choreography — when to dispatch agents, how to sequence stages, how to handle iteration loops. This skill owns the content.

**This body describes principles only.** The gated checklists — with `[BLOCKING]` / `[ADVISORY]` severity markers, tuned Red Flags, escalation lists, worked examples, and operational procedures — live in the three references. The references are **required loads**, named per Stage in `superRA:using-superRA` §Skill-Load Manifest. The implementer walks the reference checklists as self-check before commit; the reviewer walks the same checklists as verification. Same content, two perspectives — no parallel review-only document, no duplication.

**Used by:**
- Dispatched `superRA:implementer` agents during drift-test creation, refactoring, and merge proposal stages
- Dispatched `superRA:reviewer` agents during drift-test review, integration review, and merge review stages
- Anyone invoking this skill directly for an ad-hoc refactoring task outside the formal integration workflow

## Three Concurrent Disciplines — Principles

The three disciplines are **concurrent, not sequential**. A single integration pass typically exercises at least two of them, and the checklists compose: load every reference whose stage your task touches.

### 1. Drift-Test Integrity

**Purpose.** Guard every user-confirmed key result with a test that (a) is calibrated on economic reasoning, (b) runs independently of the full pipeline, (c) has been red-green verified, and (d) is never silently weakened or bumped when a refactor or merge makes it fail.

**Full checklist + how-to:** `references/drift-test-quality.md` (coverage, tolerance calibration worked examples, independence, clarity/robustness, red-green cycle, test-format conventions, cross-cutting Red Flags). Loaded whenever `Stage:` is `drift-test`, or when any task creates, modifies, or assesses a drift test.

### 2. Codebase Integration

**Purpose.** Make the analysis fit the host codebase — naming, utilities, diff shape, debug-artifact cleanup, documentation currency — without sweeping in unrelated cleanup and without silently deciding methodology questions (those escalate to the researcher). Walk up every file in the diff to repo root and update stale module-level docs.

**Full checklist + how-to:** `references/codebase-integration.md` (code integration, handling-inconsistencies decision tree, PR quality, documentation currency, Project Doc Audit walk-up algorithm). Loaded whenever `Stage:` is `integration`. For data-analysis work, `econ-data-analysis/references/integration.md` is the primary reference and this file is the generic cross-cutting companion; load both.

### 3. Merge Quality

**Purpose.** Preserve incoming intent *and* current-branch work across a merge with no silent result changes and no mechanical ours/theirs on research-meaningful conflicts. Structure every merge as a two-commit pair: mechanical first, integration second. Escalate Tier 3 conflicts (variable definitions, sample construction, econometric specifications, data processing, results) to the researcher and log the decision before committing the resolution.

**Full checklist + how-to:** `references/merge-quality.md` (intent preservation, research integrity, two-commit templates, Tier 3 escalation procedure + Never-list, integration-map format, verification, data discipline). Loaded whenever `Stage:` is `merge`.

---

## The Load-Bearing Top Item

Every round of drift-test creation, refactoring, and merge integration shares one top-level constraint that sits above all three checklists:

- `[BLOCKING]` **Minimum net diff to merge base.** Cumulative refactor across all integration rounds touches only what drift-test preservation, convention fit, handoff-doc coherence, and documentation demand. No unrelated cleanup, no speculative abstractions, no "while I'm here" edits. Implementer runs `git diff <merge-base>..HEAD` before each commit and reviews the cumulative diff; reviewer computes the same diff as evidence.

This item frames every checklist item below it — any hunk in the cumulative diff must be justifiable against one of the three disciplines' checklists. A hunk not tied to drift-test integrity, codebase integration, or merge quality is out of scope and must be reverted or re-justified. Enforced by the Implementer Self-Check below.

---

## Scope by Integration Status

Refactor implementer and verify reviewer operate only on tasks whose `Integration status` is unset or `REVISE`. `APPROVED`-integration tasks are out of scope — do not walk their code, do not touch their output files except through legitimate merge resolution. The dispatch's `Task:` or `Tasks in scope:` field names the explicit in-scope list.

This mirrors the DAG cascade rule on `Review status:` and `Integration status:` — see `handoff-doc/references/plan-anatomy.md` (lines 178–179) for the cascade semantics. Without scoping, a second integration pass either redoes already-approved work or lets the reviewer flag already-APPROVED tasks, which violates the Minimum-net-diff top item above.

---

## Reviewer Verdict Protocol

Every reviewer walks top-to-bottom through the Minimum-net-diff top item plus every discipline's checklist that the task touches. **Never halt on a failure** — one comprehensive pass every time; halting early forces a full re-review on the next pass, and reviewer dispatches are costly.

Two verdicts:

- **APPROVE** — no `[BLOCKING]` findings.
- **REVISE** — at least one `[BLOCKING]` finding.

**Handling dependent findings.** When a later finding's assessment depends on an earlier `[BLOCKING]` item being fixed first (e.g., "couldn't fully assess the refactor until the drift tests are passing"), say so in plain prose alongside the finding. No separate verdict, no formal tag.

**Re-review after REVISE.** Implementer fixes all `[BLOCKING]` findings and re-dispatches. Reviewer then (1) verifies each fix is correct, and (2) re-checks any finding the first pass annotated as depending on an upstream fix. Everything else is accepted from the first pass — no third full walk. APPROVE once all `[BLOCKING]` findings are resolved.

---

## Implementer Self-Check (Before Every Commit)

The Minimum-net-diff top item is enforced by a concrete pre-commit procedure. Run it before every commit on the integration branch:

1. **Compute the cumulative diff.** `git diff <merge-base>..HEAD` where `<merge-base>` is the merge base the integration is targeting (e.g., `$(git merge-base HEAD main)` or whatever the workflow specifies).
2. **Review every hunk** against the loaded references' checklists. For each hunk, ask: *which `[BLOCKING]` or `[ADVISORY]` item justifies this change?* A hunk may be tied to drift-test preservation, codebase-convention fit, handoff-doc coherence, documentation currency, or an explicit item in the integration map.
3. **Any hunk without a justification is out of scope.** Revert it, OR re-justify it by adding the underlying need to the integration map (and the commit message) so the reviewer can check the same evidence.
4. **Stage only files you touched this turn** (per `superRA:using-superRA` §Commit Hygiene); `git diff --cached` before `git commit`.

The verify reviewer runs the same `git diff <merge-base>..HEAD` as evidence and walks each hunk through the same reference checklists. One source of truth, two perspectives.

---

## Dispatch Convention

Dispatches follow the canonical template in `superRA:agent-orchestration` §Dispatch Templates. The Skill-Load Manifest (`superRA:using-superRA`) names this skill and its reference files on the `drift-test`, `integration`, and `merge` rows — the dispatch prompt does not restate `Skills:` or reference lines. The agent loads this skill, receives the base directory, reads the manifest-named reference, and walks the gated checklist in that reference alongside the domain skill (for data analysis: `superRA:econ-data-analysis`).

Some tasks cross stages (a refactor during a merge; a drift-test review that flags a refactor-caused sign-flip). Load every reference whose stage your task touches — the checklist sections compose.

---

## Integration

**Used by workflow skills:**
- **`superRA:integration-workflow`** — Dispatches drift-test creation and review (`references/drift-test-quality.md`) and the integration review → refactor loop (`references/codebase-integration.md`).
- **`superRA:merge-workflow`** — Dispatches post-merge integration review and refactoring (`references/codebase-integration.md`) during the refactor-review loop triggered by drift-test failure or reviewer REVISE.
- **`superRA:semantic-merge`** — Dispatches merge proposer (`references/merge-quality.md`) and merge reviewer (`references/merge-quality.md`) for tier classification and conflict resolution.

**Auto-loaded alongside:**
- **`superRA:econ-data-analysis`** — Data discipline (loaded by `implementer` / `reviewer` agents whenever the stage involves analysis code, per the `superRA:using-superRA` §Skill-Load Manifest); the `implementation` row also loads `econ-data-analysis/references/notebook-format.md` for notebook formatting.
