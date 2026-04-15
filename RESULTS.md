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

## Task 3: Rewrite `execution-workflow/SKILL.md` for Domain Agnosticism

**Outcome.** `skills/execution-workflow/SKILL.md` now speaks in domain-neutral terms and delegates domain-specific verification to the active domain skill's §Review & Self-Check Discipline. The two-stage review (data integrity → implementation correctness) collapses into **one comprehensive review pass** per task whose verdict is `APPROVE` / `REVISE` / `CONDITIONAL APPROVE`, matching the verdict protocol established in Task 2's `econ-data-analysis/SKILL.md §Review & Self-Check Discipline`.

**Stage renames (D-Stage-1).** Implementer dispatch: `Stage: analysis task` → `Stage: implementation`. Reviewer dispatch: the former `Stage: data integrity` + `Stage: implementation` collapse into a single `Stage: implementation review`. The two former reviewer templates become one reviewer template.

**Key rewrites:**

- **Intro + Core principle + announce line** dropped "two-stage review (data integrity then implementation correctness)" in favor of "one comprehensive review pass per task. The reviewer walks the active domain skill's §Review & Self-Check Discipline top to bottom and returns APPROVE / REVISE / CONDITIONAL APPROVE." The description-line trigger list swaps `REVISE (...)` for `REVISE / CONDITIONAL APPROVE`.
- **Process flowchart** replaces the two-node data-integrity → implementation dispatch chain with a single "Dispatch reviewer (implementation review)" node whose three verdict branches are explicit: APPROVE (proceed), REVISE (fix items, re-dispatch), CONDITIONAL APPROVE (fix gating, narrow re-review that verifies the gating fix + cited downstream items still hold, loop until APPROVE).
- **Per-task execution steps (Step 2)** collapsed from five sub-steps (with separate data-integrity and implementation reviewer phases) to four: dispatch implementer → handle NEEDS_CONTEXT / BLOCKED → dispatch reviewer (one pass, three verdicts inlined with adjudication guidance) → handle APPROVE. The CONDITIONAL APPROVE branch explicitly calls out the narrow re-review as default with documented flexibility for a wider re-review via optional `Additionally:` steering when the gating fix casts doubt on downstream items.
- **Dispatch templates** — three templates → two templates (implementer, reviewer). Hardcoded "For every analysis-touching stage … loads `superRA:econ-data-analysis` and `superRA:script-to-notebook`" preamble removed — agent Stage tables per Task 4 drive stage-based loads. A sentence follows the reviewer template describing the CONDITIONAL APPROVE narrow-re-review steering pattern.
- **Step 3 (Verify Pipeline and Reproducibility)** rewritten as a five-check orchestrator skeleton: (1) all code committed, (2) PLAN.md current, (3) RESULTS.md current, (4) **domain completion verification** — "walk the active domain skill's §Completion verification `[GATING]` items. For data analysis, this is `econ-data-analysis/SKILL.md §Review & Self-Check Discipline §Completion verification` — pipeline runs end-to-end if the plan declares one, outputs from committed code, and any other domain-specific gating items. The domain skill owns the exact list; this workflow just routes you to it," (5) deferred MINORs resolved. Hardcoded data-analysis pipeline / outputs assumptions from the previous Steps 2–3 gone.
- **Step 4 completion menu** — the question prompt "Analysis complete and reproducible" → "Work complete and verified." The heading banner and option body are otherwise unchanged. The user's hand-edited Option 1/2 collapsed narrative (Options 1 and 2 both invoke `superRA:integration-workflow`) preserved.
- **Review Status table** collapses `REVISE (data integrity)` + `REVISE (implementation)` into a single `REVISE` row; adds a new `CONDITIONAL APPROVE` row with the orchestrator-action text pointing at gating-item adjudication + implementer re-dispatch + reviewer narrow re-review.
- **`## Sensitivity Analysis Tasks`** section deleted entirely — content lives in `econ-data-analysis/SKILL.md §Validate §Sensitivity analysis` and `references/data-robustness-checklist.md`.
- **`## Model Selection`** replaced with one paragraph: "Use the least capable model that handles the task; reviewers use the most capable available model. Domain-specific complexity examples live in the domain skill, not here."
- **Red Flags** scrubbed of "data integrity" / "implementation review" references; rewritten for the one-pass flow with explicit REVISE / CONDITIONAL APPROVE handling at the bottom. New red flag: "Proceed with unfixed `[GATING]` items (a CONDITIONAL APPROVE task is not complete until the narrow re-review promotes it to APPROVED)."
- **Agent Types section** shortened to two rows — implementer and reviewer — pointing at the agent file Stage tables for stage-scoped references instead of hardcoding `superRA:econ-data-analysis` / `superRA:script-to-notebook`.
- **Integration table** line replaced: `superRA:econ-data-analysis — REQUIRED: Data discipline all agents must follow` → `the active domain skill (for data analysis: superRA:econ-data-analysis) — REQUIRED: domain discipline all agents follow, loaded at dispatch-time per agents/implementer.md / agents/reviewer.md Stage tables. Carries the §Review & Self-Check Discipline that the reviewer walks on every pass.`

**Preserved user edits.** The "If you need a non-default skill load, an extra domain reference, or an override of the standard handoff, add `Skills:` and `References:` lines as needed" sentence is intact. The Step 4 Option 1/2 collapsed narrative (both options dispatch `superRA:integration-workflow`) is intact.

**Structural-invariants additions.** New block #12 in `tests/structural-invariants.sh` with three assertions for execution-workflow domain-agnosticism: (a) two-stage-review phrasing absent (`data integrity|two-stage review|REVISE \(data integrity\)|REVISE \(implementation\)`); (b) `## Sensitivity Analysis Tasks` heading absent; (c) `CONDITIONAL APPROVE` verdict present. Old block #12 (README Why-superRA? lead) renumbered to #13.

**Files touched:**

- `skills/execution-workflow/SKILL.md` — full rewrite per above.
- `tests/structural-invariants.sh` — new assertion block #12; old #12 renumbered to #13.

**Structural-invariants run.** 29 PASS, 2 known WARN (pre-existing upstream refs in writing-skills), 0 FAIL.

**Out of scope (tracked for follow-on tasks 4–6).** Agent-file Stage tables that remove the need for dispatch-template preamble (Task 4), companion-workflow audit (Task 5), and final invariants + release-notes consolidation (Task 6). All depend on Task 3 APPROVE.

## Task 6: Structural Invariants + RELEASE-NOTES Finalization

**Outcome.** The restructure is wrapped: `tests/structural-invariants.sh` already carries every assertion the dispatch checklist calls for, and `RELEASE-NOTES.md`'s top (Unreleased) entry is rewritten as a single coherent description of the full `refactor/workflow-domain-split` restructure.

**Invariant audit — no gaps found.** Walked the dispatch-specified checklist against the live script; every item resolves to an existing `pass` line:

| Checklist item | Block in script |
|---|---|
| Dispatch prefix standardization (prefix count ≥ template count) | 10a |
| No `Work from:` / `Counterpart:` in dispatch templates | 10b |
| `## Review & Self-Check Discipline` heading in `econ-data-analysis/SKILL.md` | 11 |
| `[GATING]` marker count ≥ 8 in that file | 11 |
| `CONDITIONAL APPROVE` string in `econ-data-analysis/SKILL.md` | 11 |
| No shadow `implementation-review.md` / `integration-review.md` reference | 11 |
| `execution-workflow/SKILL.md` free of two-stage-review phrasing | 12 |
| `## Sensitivity Analysis Tasks` section removed from `execution-workflow/SKILL.md` | 12 |
| `CONDITIONAL APPROVE` in `execution-workflow/SKILL.md` | 12 |
| Stage table with core stage rows in `agents/implementer.md` | 13 |
| Stage table with core stage rows in `agents/reviewer.md` | 13 |
| Dispatch-prompt contract phrase in both agent files | 13 |
| `CONDITIONAL APPROVE` in `agents/reviewer.md` | 13 |

DAV-era invariants (blocks 3 / 3b / 3c) continue to guard the DAV restructure. No new assertions added.

**RELEASE-NOTES.md rewrite.** The prior Unreleased entry announced four sub-refactors and inherited the DAV paragraphs from the prior cycle, but never covered Tasks 4 (agent Stage tables + dispatch-prompt contract + implementer §Self-Review walk) or 5 (companion-workflow audit). Replaced with one coherent entry whose title names the full restructure and whose body walks seven pieces in logical order:

1. DAV restructure (Describe-Analyze-Validate).
2. Dispatch-prompt protocol standardization with the Additionally-anchor-last shape.
3. §Review & Self-Check Discipline shared gating in `econ-data-analysis/SKILL.md` main body with `[GATING]` / `[STANDARD]` / `[ADVISORY]` markers.
4. CONDITIONAL APPROVE verdict protocol.
5. `execution-workflow` domain-agnosticism (one-pass review, domain-parametric Step 3, generic completion menu, domain-neutral stage names).
6. Agent Stage tables + dispatch-prompt contract + implementer §Self-Review walk + reviewer CONDITIONAL APPROVE mechanics.
7. Companion-workflow light audit across `integration-workflow`, `merge-workflow`, `semantic-merge`, `planning-workflow`, `refactor-and-integrate/references/codebase-integration.md`, and `agents/reviewer.md` frontmatter.

A final paragraph enumerates the structural-invariants blocks (10a, 10b, 11, 12, 13, 3+3b+3c) that anchor each piece. Prior release entries preserved verbatim.

**Files touched:**

- `tests/structural-invariants.sh` — no edits (audit confirmed complete).
- `RELEASE-NOTES.md` — Unreleased entry rewritten; all prior entries preserved.
- `PLAN.md` — Task 6 steps marked `[x]`, Review status set to `IMPLEMENTED`.
- `RESULTS.md` — this Task 6 section added.

**Structural-invariants run.** All PASS, 2 known WARN (pre-existing upstream refs in `writing-skills`), 0 FAIL.

## Task 18: Manual-Review Fixes + Structural Invariants + RELEASE-NOTES Finalization (Round 3)

**Outcome.** Round 3 is wrapped. Four deliverables landed in one atomic commit:

1. **handoff-doc principles pruned to four.** `skills/handoff-doc/SKILL.md` principles #4 (Ownership by role) and #5 (Explicit what-changed deltas in both directions) deleted entirely. Old #6 ("The doc is the record") renumbers to new #4. Section heading "The Six Principles" → "The Four Principles". Downstream "six principles" mentions updated to "four principles" in `skills/CATEGORIES.md`, `README.md` (twice, including the principle-list parenthetical pruned to four items), `skills/planning-workflow/references/results-template.md`, `skills/using-superRA/SKILL.md`, `agents/implementer.md`, and `agents/reviewer.md`.

2. **`integration.md` Document-code consistency + restored preamble keyphrase.** `skills/econ-data-analysis/references/integration.md` gains a new `[STANDARD]` Document-code consistency item in the Integration-gates section: reconcile inconsistencies between refactored code and papers / slides / notes / long-standing downstream artifacts, or flag unreconciled ones in `RESULTS.md` §Limitations. The inline HTML-comment reminder from commit `3b25912` is removed (replaced by the materialized item). The shared-flow preamble phrase "single source of truth for data-analysis integration discipline" is restored at the top of the file — a prior manual edit had shortened it and dropped the invariant-#16 keyphrase.

3. **Structural invariants updated.** `tests/structural-invariants.sh` got two block rewrites and six new blocks:
   - **Block #13 — updated** from "both agent files carry the authoritative 11-row Stage table" to "both agent files point at `superRA:using-superRA` §Skill-Load Manifest (grep `Skill-Load Manifest`)"; both files preserve the `dispatch prompt carries` contract paragraph; `agents/reviewer.md` still encodes `CONDITIONAL APPROVE`.
   - **Block #14 — updated** from "five cross-stage sections including `## Direct Mode`" to "four cross-stage sections (Dispatch Templates, Dispatch-Return Deltas, Handling Reviewer Feedback, Review Status Reference)". Direct Mode assertion dropped — it was relocated to `using-superRA` §Execution Modes in Round 3 Task 16.
   - **Block #20 — new.** `using-superRA/SKILL.md` contains `## Skill-Load Manifest`, `## Skill Inventory`, `## Execution Modes`; carries exactly 6 Stage rows (grep of `^| \`(implementation|refactoring|drift-test|merge|documentation|planning-review)\``); mentions `handoff-doc` ≥ 6 times; `<SUBAGENT-STOP>` absent; `references/session-bootstrap.md` exists.
   - **Block #21 — new.** Both agent files' frontmatter preload `superRA:using-superRA` (head-of-file grep); neither file carries the old `| \`implementation\`` or `| \`drift test creation\`` Stage-table rows; the retired `auto-load` token is absent across `agents/`, `skills/`, and `README.md` (PLAN.md, RELEASE-NOTES.md, and RESULTS.md are excluded — they carry self-referential retirement language).
   - **Block #22 — new.** `skills/agent-orchestration/references/agent-teams.md` exists with ≥ 3 TeamCreate mentions; `agent-orchestration/SKILL.md` no longer contains `### Team Recipes` or `^## Direct Mode`.
   - **Block #23 — new.** `using-superRA/SKILL.md` contains both `## Execution Modes` and `Direct mode`; no other SKILL.md carries a `§Direct Mode` reference.
   - **Block #24 — new.** `skills/handoff-doc/SKILL.md` has no `^4\. \*\*Ownership by role` or `^5\. \*\*Explicit what-changed` opening phrases; numbered-principle count is exactly 4.
   - **Block #25 — new.** `skills/econ-data-analysis/references/integration.md` contains `Document-code consistency`.

4. **RELEASE-NOTES extended.** The Unreleased entry header title now covers all three rounds. Four Round 3 paragraphs were added just before the Structural-invariants paragraph: (a) `using-superRA` promoted to master skill with skill-load manifest + `references/session-bootstrap.md`; (b) frontmatter preload + Stage-table retirement + auto-load retirement; (c) `agent-orchestration` split with `references/agent-teams.md` + Team Recipes deletion + Direct Mode relocation; (d) small semantic fixes (handoff-doc principle deletion + integration.md Document-code consistency + restored shared-flow preamble). The Structural-invariants paragraph was rewritten to enumerate the new + updated invariant blocks (#13 updated, #14 updated, #20 new, #21 new, #22 new, #23 new, #24 new, #25 new).

**Files touched:**

- `skills/handoff-doc/SKILL.md` — principles #4 and #5 deleted; old #6 renumbered to new #4; section heading updated.
- `skills/econ-data-analysis/references/integration.md` — Document-code consistency item added; shared-flow preamble phrase restored; HTML-comment reminder removed.
- `skills/CATEGORIES.md`, `README.md`, `skills/planning-workflow/references/results-template.md`, `skills/using-superRA/SKILL.md`, `agents/implementer.md`, `agents/reviewer.md` — downstream "six principles" → "four principles".
- `tests/structural-invariants.sh` — block #13 rewritten, block #14 rewritten, blocks #20–#25 added.
- `RELEASE-NOTES.md` — Unreleased header title extended; four Round 3 paragraphs added; Structural-invariants paragraph rewritten.
- `PLAN.md` — Task 18 steps marked `[x]`, Review status set to `IMPLEMENTED`. Tasks 13 and 17 final checkbox cleaned up.
- `RESULTS.md` — this Task 18 section added.

**Structural-invariants run.** All PASS, 2 known WARN (pre-existing upstream refs in `writing-skills`), 0 FAIL.
