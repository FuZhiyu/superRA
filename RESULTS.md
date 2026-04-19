# Unified Integration-Workflow Refactor — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-19 (bootstrap)
**Status:** In Progress

---

## Task 1: Rebuild `refactor-and-integrate` as a gated checklist

**Status:** IMPLEMENTED

**Summary:** `skills/refactor-and-integrate/SKILL.md` rewritten as a shared gated checklist structured after `econ-data-analysis/SKILL.md §Three Concurrent Disciplines`. Three top-level disciplines — **Drift-Test Integrity**, **Codebase Integration**, **Merge Quality** — each carry `[BLOCKING]` / `[ADVISORY]` severity-marked items. Load-bearing top item `[BLOCKING] Minimum net diff to merge base` is called out above the disciplines (verbatim from PLAN.md Task 1 Step 2). A dedicated **Implementer Self-Check** subsection at the end restates the pre-commit `git diff <merge-base>..HEAD` procedure and the revert-or-re-justify rule.

**Key structural choices:**

- **References preserved (no deletion).** `drift-test-quality.md`, `codebase-integration.md`, `merge-quality.md` kept intact as long-form operational references. Checklist items in SKILL.md point at the references for worked examples, the red-green verification cycle, the Project Doc Audit walk-up algorithm, two-commit commit-message templates, and the integration-map format. This satisfies Task 1 Step 3 — long-form operational content stays in references; short checklist items fold into body.
- **Tuned content preserved verbatim, not paraphrased.**
  - Drift-Test Integrity "Cross-cutting Red Flags" (the four-bullet "Never" list) reproduced in the SKILL.md body as a blockquote, matching the wording in `references/drift-test-quality.md` §Drift Test Integrity — Cross-Cutting Red Flags.
  - Merge Quality "Research-Meaningful Escalation (Tier 3)" (escalation prose + five-conflict-type list + four-bullet "Never" list) reproduced verbatim from `references/merge-quality.md`.
  - RA-framing language ("methodology is a research decision, not a code-quality decision") preserved in the Codebase Integration inconsistency-handling item.
- **Shared-flow checklist, one source of truth.** Implementer walks the SKILL.md body as self-check before commit; reviewer walks the same items as verification. Verdict protocol (APPROVE / REVISE, dependent findings, narrow re-review after REVISE) mirrors `econ-data-analysis/SKILL.md`. No parallel review-only document exists.
- **Agent-file cross-check.** `agents/implementer.md` and `agents/reviewer.md` load `refactor-and-integrate` via the `superRA:using-superRA` §Skill-Load Manifest (no hard-coded path in either agent file), so both point at the same file by construction.

**Scope notes:**

- Caller-side wording in `integration-workflow/SKILL.md`, `merge-workflow/SKILL.md`, and `using-superRA/SKILL.md` still references the references by filename (e.g., "`codebase-integration.md` §Project Doc Audit"). Those pointers remain valid since the references were not deleted. Task 2 / Task 6 will update any stage-naming or skill-inventory language that depends on the new SKILL.md structure.
- `[BLOCKING] Handoff-doc coherence` in merge-quality is deferred to Task 4 per plan.

**Verification:**

- Top item wording matches PLAN.md Task 1 Step 2 verbatim.
- `grep` for "Red Flag", "AskUserQuestion", "Tier 3", "ASK USER" in the new SKILL.md shows preserved wording.
- No other files modified in this task.



## Task 2: Unify `integration-workflow` — Phases A–D with iterative Phase B

**Status:** Not started

## Task 3: Delete `skills/merge-workflow/`

**Status:** Not started

## Task 4: Update `semantic-merge` caller paths and handoff-doc coherence rule

**Status:** Not started

## Task 5: Minimal `planning-workflow §Changing Plans` extension

**Status:** Not started

## Task 6: Sync peripheral surfaces

**Status:** Not started

## Task 7: End-to-end dry-run verification

**Status:** Not started
