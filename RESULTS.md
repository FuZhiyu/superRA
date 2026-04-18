# Plan Stage Marker + Iterative Re-entry Mechanism — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-17 (Bundle A IMPLEMENTED)
**Status:** Bundle A (Tasks 1+2) implemented; awaiting reviewer.

---

## Task 1: Reframe `## Mid-Session Scope Changes` → `## Scope Changes and Re-entry` in `handoff-doc/SKILL.md`

**Status:** IMPLEMENTED (Bundle A, awaiting reviewer)

### Key Findings
- `## Mid-Session Scope Changes` renamed to `## Scope Changes and Re-entry` in `skills/handoff-doc/SKILL.md`.
- Preamble rewritten to frame the protocol as covering both (a) mid-execution researcher pings and (b) post-integration / post-merge scope additions (PR-review requests, adjacent features, follow-on ideas).
- "Material" bullets extended with explicit post-integration case.
- Protocol Step 3 gains "prefer modifying existing tasks over appending" bullet.
- Protocol Step 4 gains orchestrator-judgment language: orchestrator declares which boxes and why; per-task status clearing rules for fully-re-implemented / untouched / minor-edited tasks.
- Protocol Step 6 gains full-drift-suite-always rule and doc-writer/doc-reviewer scope rule.
- New DAG cascade paragraph added after protocol: transitive closure clearing, exemption mechanism via §Decisions blockquote, cross-reference to `plan-anatomy.md §Field-by-Field`.
- Banned shortcuts extended: one new bullet forbidding subset drift-test runs on re-entry.
- Validation: `grep "Mid-Session Scope Changes" skills/handoff-doc/` → zero hits; all cross-references (§User Decisions Log, §PLAN.md Is the Task Tracker, `plan-anatomy.md`) resolve; four-principles framing preserved.

---

## Task 2: Add `**Integration status:**` field + re-entry semantics to `plan-anatomy.md`

**Status:** IMPLEMENTED (Bundle A, awaiting reviewer)

### Key Findings
- `**Integration status:** *(set during integration — not filled at planning time)*` added to task-block template immediately below `**Review status:**`.
- `## Workflow Status` description in header template expanded: boxes are now described as a rollup over per-task `**Review status:**` / `**Integration status:**`; re-entry unchecks by orchestrator judgment; full drift-test suite required before rechecking `Drift tests created`; pointer updated to `SKILL.md §Scope Changes and Re-entry`.
- Field-by-Field updated: `**Review status:**` bullet gains DAG cascade language (downstream closure cleared by default, orchestrator exemptions in §Decisions). New `**Integration status:**` bullet with same values vocabulary and same cascade rule. `## Workflow Status checkboxes` bullet pointer renamed from `§Mid-Session Scope Changes` → `§Scope Changes and Re-entry`; rollup logic described.
- Validation: fenced block count still 12 (even, template balanced); `grep "Mid-Session Scope Changes" skills/handoff-doc/references/plan-anatomy.md` → zero hits.

---

## Task 3: Wire box-flip and protocol pointers into the four workflow skills

**Status:** Completed (APPROVED 2026-04-17, commit `04cec53`)

### Key Findings
- All four workflow skills now reference `## Workflow Status` and flip the milestone they own:
  - `planning-workflow` Execution Handoff (line ~130) — flips `Plan approved` after researcher confirms.
  - `execution-workflow` Step 3 (line ~200) — flips `Execution complete` once all five reproducibility checks pass. (Was "six checks" in the stash — adapted to the current Step 3 structure.)
  - `integration-workflow` Stage 1 step 8 (new, line ~162) — flips `Drift tests created`.
  - `integration-workflow` Stage 2 step 6 (new, line ~232) — flips `Refactored`, with rollback note for post-merge re-entry.
  - `integration-workflow` Step 3 doc-reviewer (after APPROVE, line ~352) — flips `Docs finalized` before Sub-part C disposition.
  - `merge-workflow` Step 4 before-action (line ~134) — flips `Merged` on the analysis branch (conditional on PLAN.md still being present after disposition).
- `merge-workflow` Step 3 entry — unchecks `Refactored` on post-merge re-entry (conditional, same disposition guard).
- `§Mid-Session Scope Changes` pointers added to:
  - `planning-workflow` Living Plan section (distinguishes agent-discovered drift from researcher-initiated scope changes).
  - `execution-workflow` Stop-Points class (b) (rewritten "scope change" line to point at the new protocol).
- `execution-workflow` Step 1 expanded from 7 to 8 sub-steps to fold in three new concepts (PLAN.md as authoritative tracker, Read Workflow Status, TodoWrite as derived view) without undoing the recent refactor that added domain-skill loading and project-guidance walk-up.

### Notes
- All six milestone names appear in exactly one owning workflow skill — no milestone is flipped by a skill that does not own its completion criterion.
- Cross-references all resolve to real headings (verified by reviewer at the heading line numbers above).

---

## Task 4: Add header-ownership bullet to `agents/implementer.md` and `agents/reviewer.md`

**Status:** Completed (APPROVED 2026-04-17, commit `04cec53`)

### Key Findings
- `agents/implementer.md` line 99 — new bullet inside "**You may NOT edit:**" list naming the PLAN.md header (`## Workflow Status` and `## Decisions`) as orchestrator-owned. Implementer-voice: "report it in your status return; the orchestrator handles the doc edit."
- `agents/reviewer.md` line 122 — same bullet with reviewer-voice: "raise it in your status report; do not edit the header yourself."
- Both bullets cite `superRA:handoff-doc references/plan-anatomy.md §Header ownership` — the cross-reference resolves to the heading promoted in Task 2.

### Notes
- Bullets land inside the existing "may NOT edit" list (not adjacent to it). Existing items in the list are unchanged.
- Reviewer's "ad-hoc stage is report-only with no document updates" exception is preserved.

---

## Cross-Bundle Verification (post-Bundle B)

- All 4 PLAN.md tasks: APPROVED.
- Working tree: clean.
- No deferred MINOR items remain in any blockquote.
- All `§<heading>` cross-references introduced by Bundles A and B resolve to real headings.
- Six milestone-flip instructions across four workflow skills match the six checkboxes in `plan-anatomy.md` exactly.
- `## Workflow Status` checklist in this very PLAN.md is the first end-to-end usage of the new mechanism — a meta-test that the design is self-applicable.
