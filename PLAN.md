# superRA Plugin Restructure Plan — Round 2 (DRY / Composability)

> **For agentic workers:** this is a PLUGIN META-REFACTOR — the "analysis" is the superRA plugin itself. Use `superRA:execution-workflow` (one-pass review per the canonical post-Task-6 protocol). The domain skill `superRA:econ-data-analysis` applies only when tasks touch data-analysis content; most tasks here are skill-file edits.

**Objective (Round 2).** Remove duplication and mis-homed content across skills. Cross-stage orchestration patterns (how to dispatch, how to relay, how to adjudicate, direct-mode rubric) consolidate into `agent-orchestration`. `integration-workflow` is stripped to workflow-choreography only; *what to check* during refactor/integration moves into `refactor-and-integrate` (generic) + a new `econ-data-analysis/references/integration.md` (data-specific), both carrying `[GATING]` / `[STANDARD]` / `[ADVISORY]` markers so implementer and reviewer always walk the same file. Delete the `implementer-protocol` / `reviewer-protocol` alias skills — one-sentence pointers in `agent-orchestration` §Direct Mode replace them. Elevate DRY / composability / extensibility + shared-flow to documented design principles in `CLAUDE.md` + `README.md`, and add a workflow-stage-to-skill map.

**Methodology.** Implementer + reviewer pair per task (one comprehensive pass, APPROVE / REVISE / CONDITIONAL APPROVE). Atomic commits on `refactor/workflow-domain-split`. `bash tests/structural-invariants.sh` green at each step. PR #1 updates on push.

**Data Inventory.** N/A — plugin meta-refactor. No datasets.

**Output.** Rewritten skill / reference / agent / doc files. New `econ-data-analysis/references/integration.md`. Deleted `implementer-protocol` / `reviewer-protocol` skill directories. Updated `tests/structural-invariants.sh`. New `RELEASE-NOTES.md` entry. New workflow-stage-to-skill map in `README.md`.

**Pipeline.** `bash tests/structural-invariants.sh`.

**Background plan document.** `/Users/zhiyufu/.claude/plans/agile-orbiting-star.md` carries the full design rationale, decisions, and risk-rollback. This PLAN.md is the task tracker.

---

## Decisions

> **User decision (2026-04-15, Round 1):** one comprehensive review pass per task; `APPROVE` / `REVISE` / `CONDITIONAL APPROVE` verdict protocol. Reviewer walks the full checklist even on gating failure; CONDITIONAL re-review is narrow (verify gating fix + downstream still holds).

> **User decision (2026-04-15, Round 1):** shared gating lives in `econ-data-analysis/SKILL.md` main body. One source of truth for implementer self-check and reviewer verification.

> **User decision (2026-04-15, Round 1):** dispatch prompts use the "Follow the standard stage-relevant workflow and load relevant skills and documents to proceed. Additionally, …" prefix; required fields first, `Additionally:` anchor last.

> **User decision (2026-04-15, Round 2):** **DRY / composability / extensibility** becomes a first-class design principle. One source of truth per concern. Workflow skills own choreography (what steps run in what order); `agent-orchestration` owns cross-stage orchestration (dispatch shape, relay protocol, verdict adjudication, team recipes, direct-mode rubric); domain skills own domain discipline; `refactor-and-integrate` owns generic integration discipline. Adding a new vertical = compose existing pieces, don't fork workflow skills.

> **User decision (2026-04-15, Round 2):** **Shared-flow** for every gated checklist. Implementer and reviewer always walk the same file; `[GATING]` / `[STANDARD]` / `[ADVISORY]` markers encode severity. Both the existing §Review & Self-Check Discipline and the new `econ-data-analysis/references/integration.md` carry this preamble.

> **User decision (2026-04-15, Round 2):** delete `implementer-protocol` + `reviewer-protocol` alias skills. `agent-orchestration` §Direct Mode covers the direct-execution rubric in one section; workflow skills link there.

> **User decision (2026-04-15, Round 2):** `integration-workflow` is purely a workflow skill. Data-specific integration checks (no redundant intermediaries, variable-construction consistency, transformation-pattern consistency, etc.) move to `econ-data-analysis/references/integration.md`. Generic code-integration standards stay in `refactor-and-integrate/references/codebase-integration.md`, stripped of data-specific sections.

---

## Completed (PR #1 — Workflow-Domain-Split Restructure, Round 1)

Tasks 1–6 all APPROVED and pushed through commit `b8c6239` on `refactor/workflow-domain-split`. Structural-invariants green (34 PASS, 2 known WARN, 0 FAIL).

Seven outcomes landed as the Round 1 restructure:

1. **DAV rename.** `describe-analyze-doc` → `describe-analyze-validate` across agents and workflow skills; validation elevated to a first-class concurrent discipline.
2. **Dispatch-prompt protocol standardization.** All 16 dispatch templates across 5 workflow-adjacent skills use the canonical "Follow the standard stage-relevant workflow and load relevant skills and documents to proceed. Additionally, …" prefix; required fields precede the `Additionally:` anchor.
3. **§Review & Self-Check Discipline shared gating in `econ-data-analysis/SKILL.md` main body.** 14 `[GATING]` / `[STANDARD]` / `[ADVISORY]` markers across six sub-sections (Gating, Implementation standards, Validation completeness, Documentation and handoff, Refactor integrity, Completion verification). Single source of truth — no shadow `implementation-review.md` / `integration-review.md` references.
4. **CONDITIONAL APPROVE verdict protocol.** Reviewer walks the entire checklist even on gating failure; CONDITIONAL APPROVE surfaces gating items for narrow re-review.
5. **`execution-workflow` domain-agnosticism.** One-pass review, domain-parametric Step 3 via active domain skill's §Completion verification, generic completion menu, domain-neutral stage names (`implementation`, `implementation review`, `refactoring`, `integration review`, `drift test creation/review`, `merge proposer/review`, `doc writer/reviewer`). `## Sensitivity Analysis Tasks` deleted (content lives in the domain skill).
6. **Agent Stage tables + dispatch-prompt contract + §Self-Review walk.** `agents/implementer.md` and `agents/reviewer.md` now carry authoritative 11-row Stage → references tables, a "What the dispatch prompt carries — and doesn't" contract section, an implementer §Self-Review walk of the domain §Review, and the reviewer's CONDITIONAL APPROVE mechanics.
7. **Companion-workflow light audit.** `integration-workflow`, `merge-workflow`, `semantic-merge`, `planning-workflow`, `refactor-and-integrate/references/codebase-integration.md` aligned with the new one-pass language and Stage-table auto-load.

Structural-invariants blocks added: 10a/10b (dispatch prefix + no `Work from:`/`Counterpart:`), 11 (§Review heading + `[GATING]` count + `CONDITIONAL APPROVE` + no shadow review files), 12 (no two-stage-review phrasing + no Sensitivity Analysis Tasks + CONDITIONAL APPROVE in execution-workflow), 13 (agent Stage tables + dispatch-prompt contract phrase + CONDITIONAL APPROVE in reviewer).

See `RELEASE-NOTES.md` Unreleased entry for the full narrative.

---

## Task 7: Update `PLAN.md` — condense Tasks 1–6; queue Tasks 8–12

**Review status:** IMPLEMENTED (orchestrator-owned; no subagent dispatch)

**Objective:** This file. Rewrite the Round 1 task-by-task content as a single Completed summary; queue Round 2 tasks 8–12 (with 10b and 11b folded in); update Objective to name the DRY/composability goal; add Round 2 decision entries.

**Steps:**

- [x] Collapse Tasks 1–6 into `## Completed (PR #1 — Workflow-Domain-Split Restructure, Round 1)`.
- [x] Rewrite Objective to describe DRY/composability.
- [x] Append Round 2 decision entries to `## Decisions`.
- [x] Queue Tasks 8–12 as new checklist blocks (below).
- [ ] Atomic commit: `docs(plan): condense completed restructure and queue DRY/composability tasks`.

---

## Task 8: Move cross-stage orchestration content into `agent-orchestration`

**Review status:** APPROVED

**Objective:** Lift `## Dispatch Templates`, `## Handling Reviewer Feedback (Orchestrator Discipline)`, and `## Review Status Reference` out of `execution-workflow/SKILL.md` into `agent-orchestration/SKILL.md` as new top-level sections. Add `## Direct Mode` to `agent-orchestration` (one-section rubric for orchestrator-executed steps). Shrink `handoff-doc/SKILL.md` principles #4 (role ownership) and #5 (deltas in both directions) to one-line pointers. `execution-workflow` and `integration-workflow` keep only workflow-choreography prose plus one-line pointers to the new `agent-orchestration` sections.

**Files touched:**

- `skills/agent-orchestration/SKILL.md` — add four new top-level sections: `## Dispatch Templates` (domain-neutral: `<stage-name>` placeholders, canonical shape, required-fields-first / `Additionally:` anchor-last rule, the "Follow the standard stage-relevant workflow" prefix, the banned-in-dispatch list), `## Handling Reviewer Feedback (Orchestrator Discipline)` (lifted verbatim), `## Review Status Reference` (verdict table), `## Direct Mode` (when orchestrator executes directly, read `agents/implementer.md` / `agents/reviewer.md` and follow the same protocol; Stage tables drive reference-loads; self-review gate, handoff-doc edit discipline, and verdict protocol all apply).
- `skills/execution-workflow/SKILL.md` — replace the three lifted sections with one-line pointers; keep the workflow-specific prose (Step 2 sub-steps, CONDITIONAL APPROVE narrow re-review sentence, flowchart node labels).
- `skills/integration-workflow/SKILL.md` — §Dispatch Convention shrinks to a pointer to `agent-orchestration` §Dispatch Templates + §Handling Reviewer Feedback.
- `skills/handoff-doc/SKILL.md` — principle #5 → "See `agent-orchestration` §Handling Reviewer Feedback for how dispatch prompts and status returns carry what-changed deltas." Principle #4 → "Role-scoped edit permissions live in `agents/implementer.md` + `agents/reviewer.md`."

**Steps:**

- [x] **Describe — locate the exact blocks.** Confirmed the line ranges (execution-workflow L171–203, L205–238, L295–306; handoff-doc principles #4, #5) and audited pointer-update sites (`merge-workflow/SKILL.md`, `semantic-merge/SKILL.md`, `refactor-and-integrate/references/drift-test-quality.md`, `integration-workflow/SKILL.md` §Dispatch Convention).
- [x] **Analyze — execute the moves.**
  - Added four new top-level sections to `agent-orchestration/SKILL.md`: `## Dispatch Templates` (domain-neutral with `<stage-name>` placeholders + required-fields-first / `Additionally:` anchor + "Follow the standard stage-relevant workflow" prefix rule + banned-in-dispatch list), `## Handling Reviewer Feedback (Orchestrator Discipline)` (lifted verbatim), `## Review Status Reference` (verdict table), `## Direct Mode` (~10-line rubric for orchestrator-executed steps).
  - Replaced the three lifted sections in `execution-workflow/SKILL.md` with one-line pointers; preserved Step 2 sub-steps, the CONDITIONAL APPROVE narrow re-review sentence, and flowchart node labels.
  - Shrank `integration-workflow/SKILL.md` §Dispatch Convention to a pointer at agent-orchestration §Dispatch Templates + §Handling Reviewer Feedback.
  - Shrank `handoff-doc/SKILL.md` principle #4 (role ownership → agents/implementer.md + agents/reviewer.md) and #5 (deltas → agent-orchestration §Handling Reviewer Feedback); preserved principle numbering 1..6.
  - Rewired `merge-workflow/SKILL.md` (3 sites), `semantic-merge/SKILL.md` (1 site), and `refactor-and-integrate/references/drift-test-quality.md` (1 site) to point at `superRA:agent-orchestration` §Handling Reviewer Feedback instead of `superRA:execution-workflow`.
- [x] **Validate.**
  - Added invariant block #14 to `tests/structural-invariants.sh` checking agent-orchestration owns the four headings and execution-workflow no longer carries `## Dispatch Templates`.
  - `bash tests/structural-invariants.sh` → all PASS, 2 known WARN (writing-skills), 0 FAIL.
- [ ] Atomic commit: `refactor(agent-orchestration): own cross-stage dispatch and adjudication patterns`.

---

## Task 9: Delete `implementer-protocol` + `reviewer-protocol` alias skills

**Review status:** APPROVED

**Objective:** Remove the two 22-line wrappers. Replace their role with `agent-orchestration` §Direct Mode (added in Task 8) + direct links to `agents/implementer.md` / `agents/reviewer.md` at call sites.

**Depends on:** Task 8 APPROVE (needs §Direct Mode in place).

**Files touched:**

- `skills/implementer-protocol/` — delete directory.
- `skills/reviewer-protocol/` — delete directory.
- `skills/execution-workflow/SKILL.md` — any direct-mode reference to the protocol skills is rewired to `agent-orchestration` §Direct Mode.
- `README.md`, `skills/CATEGORIES.md` — remove the two rows under Utility.
- Any other file referencing the protocol skills — rewire.

**Steps:**

- [x] **Describe — audit all references.** Grep catalog: `skills/implementer-protocol/SKILL.md` + `skills/reviewer-protocol/SKILL.md` (delete); `skills/execution-workflow/SKILL.md` L161 and L169 (direct-mode mentions → retarget to `agent-orchestration` §Direct Mode); `README.md` L113–114 + `skills/CATEGORIES.md` L41–42 (Utility table rows → remove); `RELEASE-NOTES.md` L91+L95 (historical, leave alone); `PLAN.md` (this task block). No other sites. `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, and `skills/using-superRA/` carry no references.
- [x] **Analyze — delete + rewire.** `git rm -r` on both skill directories. Rewrote both execution-workflow call sites to point at `superRA:agent-orchestration` §Direct Mode. Removed the two Utility rows from `README.md` and `skills/CATEGORIES.md`.
- [x] **Validate.** Grep across the plugin shows 0 remaining non-historical references (only PLAN.md self-references, RELEASE-NOTES.md historical, and the new invariant block remain). Added invariant block #15 to `tests/structural-invariants.sh` asserting absence of both directories; renumbered the subsequent README-lead block to #16. `bash tests/structural-invariants.sh` → all PASS, 2 known WARN (writing-skills), 0 FAIL.
- [ ] Atomic commit: `refactor(skills): remove alias-only protocol skills; agent-orchestration §Direct Mode covers direct-execution rubric`.

---

## Task 10: Make `integration-workflow` generic; move data-specific content to domain reference

**Review status:** APPROVED

**Objective:** `integration-workflow/SKILL.md` retains ONLY workflow sequencing (Stage 1 drift-test creation, Stage 2 integration review → refactor loop, Step 3 doc finalization, four stop points, handoff to `merge-workflow`). *What to check* content moves to `refactor-and-integrate/references/codebase-integration.md` (generic) and to a new `skills/econ-data-analysis/references/integration.md` (data-specific). Both references carry `[GATING]` / `[STANDARD]` / `[ADVISORY]` markers + the shared-flow preamble.

**Task 10b (folded into the same commit):** The new `integration.md` opens with:
> This reference is the single source of truth for data-analysis integration discipline at the `refactoring` and `integration review` stages. The implementer walks it as pre-handoff self-check; the reviewer walks it as verification criteria. Same content, two perspectives — no drift possible. `[GATING]` items block unconditional APPROVE; `[STANDARD]` items become REVISE findings; `[ADVISORY]` items are suggestions the reviewer MAY flag as MINOR. The verdict protocol is the same as `econ-data-analysis/SKILL.md` §Review & Self-Check Discipline (APPROVE / REVISE / CONDITIONAL APPROVE).

**Depends on:** Tasks 8 and 9 APPROVE.

**Files touched:**

- `skills/integration-workflow/SKILL.md` — strip "what to check" prose; keep workflow sequencing.
- `skills/refactor-and-integrate/references/codebase-integration.md` — strip `## Economic Integration` + `## Data Discipline Through Refactoring` sections. Keep §Code Integration, §Handling Inconsistencies, §PR Quality, §Documentation Currency. Add shared-flow preamble.
- **New file:** `skills/econ-data-analysis/references/integration.md` — ≥7 items across `[GATING]` / `[STANDARD]` / `[ADVISORY]` tiers covering: no redundant intermediary datasets; variable-construction consistency (log vs D-H growth, winsorization thresholds); transformation-pattern consistency (outlier treatment, sample filters, control variables); variable naming; shared utilities; documented deviations; migration pointers. Shared-flow preamble (Task 10b) at the top.
- `skills/econ-data-analysis/SKILL.md` — §Refactor integrity gets a one-line pointer to the new `references/integration.md` for integration-stage work.
- `agents/implementer.md` + `agents/reviewer.md` — Stage table rows for `refactoring` and `integration review` add `integration.md` (alongside `codebase-integration.md`).
- Audit `skills/refactor-and-integrate/references/drift-test-quality.md` and `merge-quality.md` for residual data-specific language; leave generic framework intact.

**Steps:**

- [x] **Describe.** Read `integration-workflow/SKILL.md`; confirmed the file is already mostly workflow-sequencing; only two lines in Red Flags / Always carried data-specific tokens (`row counts`, `describe steps`). Read `codebase-integration.md`; §Economic Integration + §Data Discipline Through Refactoring marked for move. Drafted `econ-data-analysis/references/integration.md` with three sub-sections (Consistency / Data discipline preserved / Utility reuse and documented deviations).
- [x] **Analyze — write the moves.**
  - Created `skills/econ-data-analysis/references/integration.md` with the shared-flow preamble (Task 10b), a pointer back to `codebase-integration.md`, and 12 tiered items: 4 `[GATING]` on consistency (no redundant intermediaries, variable-construction consistency, transformation-pattern consistency) + 4 `[GATING]` on data discipline preservation (describe steps, row-count prints, validation checks, drift tests pass post-refactor) + 5 `[STANDARD]` (naming, sample preserved, jupytext cells match, no artifact deleted, shared utilities, documented deviations) + 1 `[ADVISORY]` (migration pointers). Verdict protocol section references the shared CONDITIONAL APPROVE protocol in the domain SKILL.
  - Rewrote `codebase-integration.md`: deleted `## Economic Integration` and `## Data Discipline Through Refactoring`; kept §Code Integration, §Handling Inconsistencies, §PR Quality, §Documentation Currency; updated the top blockquote to point at BOTH the domain skill's §Refactor integrity AND the new `econ-data-analysis/references/integration.md`. Removed the orphan "Drift tests exist and pass" checkbox from §PR Quality since it is now owned by the domain reference.
  - Updated `integration-workflow/SKILL.md`: replaced data-specific phrasing in two Red Flags / Always bullets with generic "domain-discipline artifacts" language pointing at the Stage-table references. Stripped the hardcoded `Domain reference:` line from the Stage 2 refactorer and integration-reviewer dispatch prompts; added a follow-up paragraph noting that the Stage table owns the reference load. Updated the Agent Types and Domain References table rows for Stage 2 refactoring / integration review to cite both `codebase-integration.md` (generic) and `econ-data-analysis/references/integration.md` (data-specific).
  - Updated agent Stage tables in `agents/implementer.md` and `agents/reviewer.md`: rows for `refactoring` and `integration review` now load §Refactor integrity + `econ-data-analysis/references/integration.md` + `refactor-and-integrate/references/codebase-integration.md` (plus `integrate-drift-tests.md` when drift tests exist).
  - Added a one-line pointer at the top of `econ-data-analysis/SKILL.md` §Refactor integrity: "For integration-stage refactoring discipline (cross-codebase consistency, no redundant intermediaries, variable-construction consistency, transformation-pattern consistency, documented deviations, migration pointers), see `references/integration.md`."
  - Audit of `drift-test-quality.md` and `merge-quality.md`: left intact. Both are cross-cutting quality frameworks; the only data-specific phrasing (`merge-quality.md` §Data Discipline bullet and §Research Integrity bullets on variable definitions / sample construction) is load-bearing for the merge flow itself and already redirects to the loaded `econ-data-analysis` skill for the full artifact list.
- [x] **Validate.**
  - Grep confirmed: `integration-workflow/SKILL.md` has 0 hits for `winsorization|variable construction|transformation|describe step|row count|Data discipline|Economic Integration`. `codebase-integration.md` has 0 hits for the same tokens. `integration.md` has 9 `[GATING]` markers (≥3 required).
  - Added invariant block #16 to `tests/structural-invariants.sh` (renumbered the prior README 'Why superRA?' block to #17): (a) `integration.md` exists; (b) ≥3 `[GATING]` markers; (c) shared-flow preamble phrase present; (d) `codebase-integration.md` does not carry `## Economic Integration` or `## Data Discipline Through Refactoring` headings; (e) `integration-workflow/SKILL.md` does not contain `winsorization` or `Economic Integration`.
  - `bash tests/structural-invariants.sh` → all 44 PASS, 2 known WARN (writing-skills upstream refs), 0 FAIL.
- [x] Atomic commit: `refactor(integration): separate workflow-choreography from integration-discipline; add econ-data-analysis/integration.md`.

---

## Task 11: Elevate DRY / composability / extensibility as a design principle in `CLAUDE.md` + `README.md`

**Review status:** APPROVED (docs-only; user authored the principle; landed early in commit `64d31a7` without formal subagent review per orchestrator adjudication)

**Objective:** Add `### DRY, composability, extensibility` to `CLAUDE.md` §Design Principles (between the Architectural pattern and Domain verticals subsections), with D-Shared-Flow-1 as a sub-bullet. Add a matching fifth principle to `README.md` §Design Principles. Refresh the stale `README.md` §Key Design Decisions (currently references two-stage review / REVISE (data integrity)) to match one-pass review + CONDITIONAL APPROVE + Stage tables.

**Depends on:** Tasks 8–10 APPROVE (so the text matches the post-move reality).

**Files touched:**

- `CLAUDE.md` — new §DRY, composability, extensibility under §Design Principles.
- `README.md` — new principle under §Design Principles; refreshed §Key Design Decisions + §Philosophy bullet on adversarial review.

**Steps:**

- [x] **Describe.** `CLAUDE.md` §Design Principles and `README.md` §Design Principles / §Key Design Decisions / §Philosophy audited by user.
- [x] **Analyze — write the new content.** User-authored `### DRY, composability, extensibility` subsection added to `CLAUDE.md` §Design Principles with ownership map + shared-flow sub-bullet; matching fifth principle added to `README.md`; stale review-protocol language scrubbed from README.
- [x] **Validate.** Grep confirmed 0 hits for `two-stage review` / `REVISE (data integrity)` / `REVISE (implementation)` in `README.md`. Invariant block #19 (added in Task 12) locks both the presence of "DRY, composability, extensibility" in `CLAUDE.md` and the absence of `two-stage review` in `README.md`. Landed in commit `64d31a7`.

---

## Task 11b: Add workflow-stage-to-skill map (markdown diagram)

**Review status:** APPROVED

**Objective:** After Tasks 7–11 land, add a markdown diagram (Mermaid preferred so GitHub renders it, pipe-table fallback) showing how each skill is used in each workflow stage. Stages: session-start → PLAN → IMPLEMENT → VALIDATE → INTEGRATE (drift tests / refactor / doc finalization) → MERGE. For each stage: primary workflow skill + active domain skill + cross-cutting loads (`agent-orchestration`, `handoff-doc`, `semantic-merge`) + stage-scoped references + agents dispatched. Legend explains the DRY-composition pattern + extension path (new verticals swap only the domain column).

**Depends on:** Tasks 8–11 APPROVE (so the map reflects the post-refactor reality).

**Files touched:**

- `README.md` — new `## Workflow Map` section between §How It Works and §Design Principles.
- `tests/structural-invariants.sh` — new block #17 (Workflow Map heading + Mermaid fence / pipe-table fallback); prior block #17 (README 'Why superRA?' lead) renumbered to #18.

**Steps:**

- [x] **Describe.** Enumerated every workflow stage (Session start, PLAN, IMPLEMENT, VALIDATE, INTEGRATE Stage 1/2/Step 3, MERGE), cross-checked against the 11-row Stage tables in `agents/implementer.md` and `agents/reviewer.md`.
- [x] **Analyze — draft the diagram.** Added a Mermaid `flowchart TB` with one node per stage carrying the workflow skill, domain skill / references, agent `Stage:` value, and agents dispatched. A shared `CROSS` node captures `agent-orchestration`, `handoff-doc`, and `using-superRA` (dotted edges from every stage). REVISE / APPROVE loops at VALIDATE wired explicitly. Added a legend explaining the DRY-composition pattern and an extension note that new verticals swap only the Domain column.
- [x] **Validate.**
  - Cross-checked every reference cell against the agent Stage tables: `planning.md`, `integrate-drift-tests.md`, `integration.md`, `codebase-integration.md`, `drift-test-quality.md`, `merge-quality.md`, `baseline-io.md`, `rich-content.md`, `final-form.md`, plus the `econ-data-analysis` main-body §Review & Self-Check / §Refactor integrity anchors. All resolve to real files.
  - Added invariant block #17 to `tests/structural-invariants.sh`: (a) `README.md` contains `## Workflow Map` heading; (b) within the 100 lines following that heading, a ```` ```mermaid ```` fenced code block exists OR a pipe-table with ≥5 data rows exists. Renumbered the prior README-'Why superRA?' block to #18.
  - `bash tests/structural-invariants.sh` → all PASS, 2 known WARN (writing-skills upstream refs), 0 FAIL.
- [x] Atomic commit: `docs(readme): add workflow-stage-to-skill map`.

---

## Task 12: Structural invariants + RELEASE-NOTES finalization

**Review status:** IMPLEMENTED

**Objective:** Consolidate new blocks #14–#19; renumber tail blocks if needed. Rewrite/append RELEASE-NOTES.md Unreleased entry to cover the Round 2 pieces. Push to PR #1.

**Depends on:** Tasks 8–11b APPROVE.

**Files touched:**

- `tests/structural-invariants.sh` — consolidate blocks #14–#19.
- `RELEASE-NOTES.md` — extend/rewrite Unreleased entry.

**Steps:**

- [x] Walked each new invariant block (#14–#18) for correctness — all PASS on the pre-Task-12 run. Block numbering contiguous.
- [x] Added new invariant block #19 locking the DRY/composability design-principle elevation: `CLAUDE.md` contains `DRY, composability, extensibility`; `README.md` is free of stale `two-stage review` phrasing. Both assertions PASS.
- [x] Rewrote the `RELEASE-NOTES.md` Unreleased entry to cover both rounds as one coherent narrative: the Round 1 lede preserved; new dedicated paragraphs for Round 2 — cross-stage orchestration into `agent-orchestration` (Task 8), alias-skill retirement (Task 9), `integration-workflow` genericization + new `econ-data-analysis/references/integration.md` with shared-flow preamble (Tasks 10 + 10b), DRY/composability/extensibility design-principle elevation in `CLAUDE.md` + `README.md` with stale review-language scrub (Task 11), workflow-stage-to-skill map (Task 11b); final invariants paragraph enumerating blocks 3/3b/3c, 10a/10b, 11, 12, 13, 14, 15, 16, 17, 18, 19. Prior release entries preserved verbatim.
- [x] `bash tests/structural-invariants.sh` → all PASS, 2 known WARN (writing-skills upstream refs), 0 FAIL.
- [x] Atomic commit: `test+docs: finalize invariants and release notes for DRY/composability refactor`.
- [x] Push `refactor/workflow-domain-split` to origin; PR #1 updated.
