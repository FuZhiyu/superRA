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

**Review status:** IMPLEMENTED

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

**Review status:** *(not started)*

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

- [ ] **Describe.** Read `integration-workflow/SKILL.md`; mark every sentence that describes *what to check* (vs *what step runs*). Read `codebase-integration.md`; mark §Economic Integration + §Data Discipline Through Refactoring for move. Draft the new `econ-data-analysis/references/integration.md` outline.
- [ ] **Analyze — write the moves.**
  - Create `econ-data-analysis/references/integration.md` with shared-flow preamble + gated items per Task 10b.
  - Strip moved sections from `codebase-integration.md`; add shared-flow preamble.
  - Rewrite `integration-workflow/SKILL.md` "what to check" prose into one-line pointers.
  - Update agent Stage tables.
  - Add §Refactor integrity pointer in `econ-data-analysis/SKILL.md`.
- [ ] **Validate.**
  - Grep `integration-workflow/SKILL.md` for `winsorization` / `variable construction` / `transformation` / `describe step` / `row count` — expect 0 hits.
  - Grep `codebase-integration.md` for the same — expect 0 hits.
  - Grep `econ-data-analysis/references/integration.md` for `[GATING]` — expect ≥ 3 hits.
  - Add invariant block #16 with the three greps + existence of `econ-data-analysis/references/integration.md` + absence of `## Economic Integration` / `## Data Discipline Through Refactoring` headings in `codebase-integration.md`.
  - Atomic commit: `refactor(integration): separate workflow-choreography from integration-discipline; add econ-data-analysis/integration.md`.

---

## Task 11: Elevate DRY / composability / extensibility as a design principle in `CLAUDE.md` + `README.md`

**Review status:** *(not started)*

**Objective:** Add `### DRY, composability, extensibility` to `CLAUDE.md` §Design Principles (between the Architectural pattern and Domain verticals subsections), with D-Shared-Flow-1 as a sub-bullet. Add a matching fifth principle to `README.md` §Design Principles. Refresh the stale `README.md` §Key Design Decisions (currently references two-stage review / REVISE (data integrity)) to match one-pass review + CONDITIONAL APPROVE + Stage tables.

**Depends on:** Tasks 8–10 APPROVE (so the text matches the post-move reality).

**Files touched:**

- `CLAUDE.md` — new §DRY, composability, extensibility under §Design Principles.
- `README.md` — new principle under §Design Principles; refreshed §Key Design Decisions + §Philosophy bullet on adversarial review.

**Steps:**

- [ ] **Describe.** Read `CLAUDE.md` §Design Principles and §Architectural pattern. Read `README.md` §Design Principles, §Key Design Decisions, §Philosophy.
- [ ] **Analyze — write the new content.** CLAUDE.md paragraph per the D-Design-1 text in the background plan, with D-Shared-Flow-1 as a sub-bullet ("Shared-flow checklists: implementer + reviewer walk the same file, with `[GATING]` / `[STANDARD]` / `[ADVISORY]` markers — single-source-of-truth applied to review gates"). README.md: add fifth principle; rewrite stale review-protocol sections.
- [ ] **Validate.**
  - Grep `README.md` for `two-stage review` / `REVISE \(data integrity\)` / `REVISE \(implementation\)` — expect 0 hits.
  - Add invariant block #17: `CLAUDE.md` contains the string "DRY, composability, extensibility"; `README.md` does NOT contain `two-stage review`.
  - Atomic commit: `docs(claude+readme): elevate DRY/composability as a design principle; refresh stale review language`.

---

## Task 11b: Add workflow-stage-to-skill map (markdown diagram)

**Review status:** *(not started)*

**Objective:** After Tasks 7–11 land, add a markdown diagram (Mermaid preferred so GitHub renders it, pipe-table fallback) showing how each skill is used in each workflow stage. Stages: session-start → PLAN → IMPLEMENT → VALIDATE → INTEGRATE (drift tests / refactor / doc finalization) → MERGE. For each stage: primary workflow skill + active domain skill + cross-cutting loads (`agent-orchestration`, `handoff-doc`, `semantic-merge`) + stage-scoped references + agents dispatched. Legend explains the DRY-composition pattern + extension path (new verticals swap only the domain column).

**Depends on:** Tasks 8–11 APPROVE (so the map reflects the post-refactor reality).

**Files touched:**

- `README.md` (preferred) — new `## Workflow Map` section after §How It Works, before §Design Principles. If the diagram is too large, create `skills/WORKFLOW.md` and link from README.

**Steps:**

- [ ] **Describe.** Enumerate every workflow stage end-to-end with its skill/reference/agent cells, cross-checked against the post-Task-10 agent Stage tables.
- [ ] **Analyze — draft the diagram.** Mermaid `flowchart` with lanes for (a) workflow skill, (b) domain skill body + reference, (c) cross-cutting, (d) agents dispatched. Fall back to a pipe-table if Mermaid complexity gets out of hand. Add legend + extension note.
- [ ] **Validate.**
  - Confirm the map matches the agent Stage tables cell-by-cell.
  - Add invariant block #18 (light): `README.md` (or `skills/WORKFLOW.md`) contains a `mermaid` code fence OR a workflow-map pipe-table with ≥5 stage rows.
  - Atomic commit: `docs(readme): add workflow-stage-to-skill map`.

---

## Task 12: Structural invariants + RELEASE-NOTES finalization

**Review status:** *(not started)*

**Objective:** Consolidate new blocks #14–#18; renumber tail blocks if needed. Rewrite/append RELEASE-NOTES.md Unreleased entry to cover the six Round 2 pieces. Push to PR #1.

**Depends on:** Tasks 8–11b APPROVE.

**Files touched:**

- `tests/structural-invariants.sh` — consolidate blocks #14–#18.
- `RELEASE-NOTES.md` — extend/rewrite Unreleased entry.

**Steps:**

- [ ] Walk each new invariant block for correctness.
- [ ] Write (or extend) the Unreleased entry naming the six pieces: orchestration-out (Task 8), protocol-skill deletion (Task 9), integration-workflow genericization + `econ-data-analysis/references/integration.md` with shared-flow preamble (Tasks 10 + 10b), CLAUDE.md/README.md DRY + shared-flow principles (Task 11), workflow-stage-to-skill map (Task 11b). Reference the new invariant blocks.
- [ ] `bash tests/structural-invariants.sh` → all PASS, 2 known WARN, 0 FAIL.
- [ ] Atomic commit: `test+docs: finalize invariants and release notes for DRY/composability refactor`.
- [ ] Push `refactor/workflow-domain-split` to origin.
