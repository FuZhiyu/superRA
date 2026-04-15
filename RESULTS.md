# superRA Plugin Restructure — Results

Stage 1 dev log. Populated as each task completes.

## Task 1: Standardize Dispatch-Prompt Protocol

**Outcome:** 16 dispatch templates across 5 workflow-adjacent skill files now open with the canonical prefix "Follow the standard stage-relevant workflow and load relevant skills and documents to proceed. Additionally, …". Legacy `Work from:` and `Counterpart:` fields are removed from every template; free-form `Note:` fields in `merge-workflow` and `semantic-merge` Tier 3 are folded into the `Additionally:` tail so all task-specific steering flows through one channel.

**Files touched:**

- `skills/execution-workflow/SKILL.md` — 3 primary templates (analysis-task implementer, data-integrity reviewer, implementation reviewer) rewritten; added a short prose preamble describing the prefix contract; the `Agent Teams only` Counterpart comments are gone (teammate pairing now lives in `agent-orchestration` team recipes only).
- `skills/integration-workflow/SKILL.md` — 6 templates rewritten: test-creator, test-reviewer, integration-reviewer, refactorer, Step 3 doc-writer, Step 3 doc-reviewer.
- `skills/merge-workflow/SKILL.md` — 2 templates rewritten: post-merge integration reviewer, post-merge refactorer; `Note:` fields folded into `Additionally:`.
- `skills/semantic-merge/SKILL.md` — 3 templates rewritten: Tier 2 merge-proposer, Tier 2 merge-reviewer, Tier 3 merge-proposer; Tier 3 context folded into `Additionally:`.
- `skills/refactor-and-integrate/SKILL.md` — 2 illustrative examples in §"Dispatch Convention" brought into alignment so the skill's own guidance matches what the workflow skills now emit.

**Structural-invariants test updated.** Two new assertions in `tests/structural-invariants.sh`:

1. Every `Agent(subagent_type: "superRA:implementer"|"superRA:reviewer")` dispatch template in the five files above carries the "Follow the standard stage-relevant workflow" prefix (prefix-count ≥ template-count).
2. No dispatch template retains `Work from:` or `Counterpart:` lines.

Full run: 24 PASS, 2 known WARN (pre-existing upstream refs), 0 FAIL.

**RELEASE-NOTES.md** top (Unreleased) entry expanded to cover the dispatch-protocol standardization alongside the DAV restructure that was already in the entry.

**Out of scope (tracked for follow-on tasks):** the domain-agnosticism restructure of `execution-workflow` (one-pass review, generic Step 3, generic completion menu), integrating §Review & Self-Check Discipline into `econ-data-analysis/SKILL.md` main body, and agent-file Stage table updates. These depend on Task 1 landing first.

## Task 2: Integrate §Review & Self-Check Discipline into `econ-data-analysis/SKILL.md`

**Outcome.** A new `## Review & Self-Check Discipline — shared gating for implementer and reviewer` section lands in the main body of `skills/econ-data-analysis/SKILL.md`, positioned directly after Validate (after §Sensitivity analysis) and before Common Rationalizations. It is the single source of truth for both implementer pre-handoff self-check and reviewer verification — no parallel checklist lives elsewhere, and no separate `implementation-review.md` / `integration-review.md` reference files were created (per `PLAN.md §Decisions` 2026-04-15 shared-gating decision).

**Structure.** The new section has a preamble with severity markers (`[GATING]` / `[STANDARD]` / `[ADVISORY]`), a reviewer verdict protocol sub-section encoding CONDITIONAL APPROVE, and six topical sub-sections:

- **Gating** — Iron Law applied per step (Describe, row-count logging, merge-key inspection).
- **Implementation standards** — plan conformance, notebook-compatible format, decision justification, outputs from committed code.
- **Validation completeness** — distribution re-check, economic sense, PLAN.md expectations comparison, sensitivity analysis (advisory).
- **Documentation and handoff** — RESULTS.md updated in place, markdown cells, figure embedding, no dangling placeholders.
- **Refactor integrity** — applies at `refactoring` and `integration review` stages; preserves Describe / row counts / Validate checks / drift tests.
- **Completion verification** — applies at `execution-workflow` Step 3; all code committed, pipeline runs end-to-end, outputs from committed code, PLAN/RESULTS current.

Total of 14 `[GATING]` markers in the file.

**CONDITIONAL APPROVE verdict protocol.** Explicitly states the reviewer walks the entire checklist top to bottom **even on gating failure** — halting early forces a full re-review on the next pass and reviewer dispatches are costly. Three verdicts: `APPROVE` (no findings), `REVISE` (only `[STANDARD]` failed), `CONDITIONAL APPROVE` (one or more `[GATING]` failed; downstream walked and looks correct contingent on the gating fix not invalidating). Re-dispatch after CONDITIONAL APPROVE: narrow pass that verifies (1) the gating fix is correct, (2) cited downstream items still hold; on both passing, promotes to unconditional APPROVE.

**Files touched:**

- `skills/econ-data-analysis/SKILL.md` — (a) added one-line note under `## Stage-Scoped References` stating the new §Review section loads with the main body at every stage; (b) inserted `## Review & Self-Check Discipline — shared gating for implementer and reviewer` between §Validate and §Common Rationalizations; (c) collapsed the prior `## Verification Checklist` into a one-line pointer back to the new section.
- `tests/structural-invariants.sh` — new assertion block #11 adding four checks: §Review heading exists in `econ-data-analysis/SKILL.md`; `[GATING]` marker count ≥ 8 (actual: 14); `CONDITIONAL APPROVE` string present; no `implementation-review.md` / `integration-review.md` reference file exists. Old section #11 (README Why-superRA? lead) renumbered to #12.
- `RELEASE-NOTES.md` — top (Unreleased) entry expanded from two paragraphs to three: title updated to mention `§Review & Self-Check Discipline shared between implementer and reviewer`, a new paragraph for the shared-gating integration, a new paragraph for the CONDITIONAL APPROVE verdict protocol. The previously duplicated dispatch-prompt paragraph is deduplicated. Structural-invariants summary updated to four new assertions on top of the prior two.

**Structural-invariants run.** 27 PASS, 2 known WARN (pre-existing upstream refs in writing-skills), 0 FAIL.

**Out of scope (tracked for follow-on tasks 3–6).** `execution-workflow` one-pass review rewrite, agent-file Stage tables + dispatch-prompt contract + CONDITIONAL APPROVE verdict extension, companion-workflow light audit, and final invariants+release-notes consolidation. All depend on Task 2 APPROVE.
