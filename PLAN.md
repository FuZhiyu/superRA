# Manifest-Workflow Alignment Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. Domain is plugin-engineering (not data analysis) — the `econ-data-analysis` Iron Law does not apply; discipline comes from the four workflow principles in `CLAUDE.md` and the skill-authoring discipline in `document-skills:skill-creator`. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff.

**Objective:** Tighten the superRA skill layer's Stage contract: align `superRA:using-superRA` §Skill-Load Manifest with the Stage values actually emitted by workflows, add explicit Stage → workflow mapping, and rename `execution-workflow` → `implementation-workflow` for naming coherence with `Stage: implementation`. Also captures in-flight skill-description simplifications retroactively.

**Methodology:** Editing skill / agent / test / doc prose. No data or code pipelines involved. `tests/structural-invariants.sh` is the gate.

**Output:**
- `skills/using-superRA/SKILL.md` manifest: split into generic + domain-add-on tables; `merge` and `planning-review` rows dropped; "Emitted by" column added.
- Four skill files with tightened frontmatter descriptions (`agent-orchestration`, `econ-data-analysis`, `execution-workflow`, `handoff-doc`).
- `skills/execution-workflow/` → `skills/implementation-workflow/`; all references repointed.
- `tests/structural-invariants.sh` aligned with the new manifest shape + rename.

**Pipeline:** `bash tests/structural-invariants.sh` after each task and at the end.

---

## Workflow Status

- [x] **Plan approved** — researcher signed off on this plan
- [x] **Execution complete** — all tasks `APPROVED`, invariants green
- [x] **Drift tests created** — *(n/a for skill-edit work; `structural-invariants.sh` is the standing guard and passes)*
- [x] **Refactored** — codebase-fit swept as part of Tasks 3–5 (manifest restructure + rename sweep)
- [x] **Docs finalized** — README / CATEGORIES / CLAUDE.md / AGENTS.md references all repointed in Task 5
- [ ] **Merged** — branch merged to main or PR opened

---

## Project Conventions

Walked at planning time (2026-04-20). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD): contributor guidelines — four workflow principles, DRY/composability/extensibility, lean-agents-rich-references, flat `skills/` layout, prefer-positive-instructions, minimum-instruction, "agents only load what they need".
- `/README.md`: user-facing overview; skill inventory grouped Workflow / Domain / Utility / Meta mirrors `skills/CATEGORIES.md`.

### Not walked
- `docs/plans/` archive — historical; do not touch.

---

### Task 1: Skill Frontmatter Simplifications
**Depends on:** *(none)*
**Review status:** APPROVED

**Scope (already on disk, unstaged at plan commit time):**
- `skills/agent-orchestration/SKILL.md` — description tightened; redundant trigger list trimmed.
- `skills/econ-data-analysis/SKILL.md` — description tightened; redundant scenario list trimmed.
- `skills/execution-workflow/SKILL.md` — description tail trimmed (the "Covers the IMPLEMENT and VALIDATE phases..." sentence removed).
- `skills/handoff-doc/SKILL.md` — description tightened (removed "(which cover the two-stage RESULTS.md lifecycle and the User Decisions Log format)" parenthetical; intent preserved via the anatomy references).

- [x] Edits applied to the four files.
- [x] Verify skill-description triggers still activate the skill in realistic prompts — deferred to reviewer pass.

### Task 2: Manifest Restructure — Generic + Domain Add-on Split; Drop `planning-review`
**Depends on:** *(none)*
**Review status:** APPROVED *(retroactive review of commit 1c25b13, 2026-04-20)*

**Scope (already on disk, unstaged at plan commit time):**
- `skills/using-superRA/SKILL.md` — Skill-Load Manifest split into two tables: (1) **Generic (stage-driven)** — `implementation`, `integration`, `drift-test`, `merge`, `documentation`; (2) **Domain add-ons (topic-driven)** — one row per vertical, currently just `econ-data-analysis`. Removed `planning-review` Stage (no dispatcher emits it). `planning.md` is now labeled a "Plan authoring" reference used in-session by `planning-workflow` Phase 1.
- `tests/structural-invariants.sh` — stage-row regex updated; expected count 6 → 5; comment updated to explain the `planning-review` drop.

- [x] Edits applied.
- [x] `bash tests/structural-invariants.sh` — Manifest row-count invariant passes with 5 rows.

> **Review notes (retroactive, 2026-04-20):**
>
> No [BLOCKING] findings. One [ADVISORY] noted below; APPROVE.
>
> 1. **[ADVISORY] MINOR — `skills/using-superRA/SKILL.md:83-85` — add-on row packs all Stages into one cell.** The add-on table uses one row per domain with per-Stage references inside a single cell separated by `<br>` and Stage-prefix labels (`implementation: …`, `integration: …`, `drift-test: …`). The composability prose at line 81 makes the union rule clear, and the prefix labels are unambiguous, so readers should not be misled. But when a second vertical is added the single-cell shape will be hard to scan — consider re-shaping to a long-form `| domain | Stage | Also load | Additional references |` table at that point. No action now.
>
> **Verification performed (all green):**
> - **Emitted-Stage coverage.** Grep of `skills/`, `agents/`, `hooks/` (excluding `docs/plans/` historical) shows live `Stage:` emissions are `implementation`, `drift-test`, `integration`, `documentation` — all present in the generic table. `merge` is kept as a standalone-dispatch row per the post-table prose at line 77. Zero live `Stage: planning-review` / `Stage: planning` emissions — drop is safe.
> - **Content-loss check (pre-restructure single table vs post-restructure generic ∪ data-analysis add-on).** All Stages compose to the same load set as before: `implementation` → `econ-data-analysis` + §Three Concurrent Disciplines + implementer's `notebook-format.md` / reviewer SKILL.md-only; `integration` → `refactor-and-integrate` + `econ-data-analysis` + `codebase-integration.md` + `integration.md` + `integrate-drift-tests.md` (if drift tests exist); `drift-test` → `refactor-and-integrate` + `econ-data-analysis` + `drift-test-quality.md` + `integrate-drift-tests.md`; `merge` → `refactor-and-integrate` + `semantic-merge` + `econ-data-analysis` (row-level "Also load" applies to all Stages) + `merge-quality.md`; `documentation` unchanged. No silent drops.
> - **Invariant test.** `bash tests/structural-invariants.sh` — manifest row-count passes at 5. The one remaining FAIL is the pre-existing unrelated README `## Workflow Map` check, explicitly out of scope.
> - **Stale-prose sweep.** All pointers at §Skill-Load Manifest across `skills/`, `agents/`, `README.md`, `CLAUDE.md` remain valid. No live file references the dropped `planning-review` row or the old single-table shape.

### Task 3: Drop `merge` Stage from Manifest
**Depends on:** Task 2 (restructured manifest)
**Review status:** APPROVED

Grep confirms zero live `Stage: merge` emissions. Standalone `semantic-merge` dispatches should carry their Stage on the dispatch side; the manifest stops enumerating it.

- [x] **Step 1: Remove the `merge` row** from the generic Stage table in `skills/using-superRA/SKILL.md`.
- [x] **Step 2: Remove the post-table prose paragraph** that explains the `merge` stage's standalone-`semantic-merge` role. Preserved the sentence about `integration-workflow` Phase B loading `semantic-merge` (still valid and useful).
- [x] **Step 3: Update `tests/structural-invariants.sh`** — dropped `merge` from the Stage-row regex, changed expected count 5 → 4, updated the comment to explain the drop.
- [x] **Step 4: Run `bash tests/structural-invariants.sh`** — manifest row-count invariant passes at 4. Pre-existing `README.md missing '## Workflow Map'` failure is unrelated and out of scope.

### Task 4: Add "Emitted by" Column to Generic Manifest Table
**Depends on:** Task 3
**Review status:** APPROVED

- [x] **Step 1: Add a middle column** to the generic Stage table mapping each Stage to the workflow + phase that emits it. Used `execution-workflow` for `implementation` row (Task 5 rename sweep will update). Row order reordered to match workflow phase order (implementation → drift-test → integration → documentation).
- [x] **Step 2: Verify each workflow file already names its Stage.** Confirmed:
  - `execution-workflow` lines 108 + 211 mention `Stage: implementation` (dispatch template prose + Agent Loads section).
  - `integration-workflow` line 69 uses inline `Stage \`drift-test\`` (canonical shape reference); lines 93 + 132 have `Stage: integration`; lines 167 + 188 have `Stage: documentation`.
  No additions needed — all stages are named in their emitting phase.
- [x] **Step 3: Run invariants.** `bash tests/structural-invariants.sh` — manifest 4-row invariant passes. Pre-existing README `## Workflow Map` failure is out of scope.

### Task 5: Rename `execution-workflow` → `implementation-workflow`
**Depends on:** Task 3 (structural), Task 4 (content)
**Review status:** APPROVED

- [x] **Step 1: Rename the directory.** `git mv skills/execution-workflow skills/implementation-workflow`.
- [x] **Step 2: Update the skill frontmatter** in `skills/implementation-workflow/SKILL.md` — `name: implementation-workflow`; refresh self-announce line and internal self-references (resume line, stop-points section).
- [x] **Step 3: Sweep all references across repo.** Updated files: `CLAUDE.md` (2 hits), `skills/CATEGORIES.md`, `skills/using-superRA/SKILL.md` (2 hits: inventory row + manifest table), `skills/using-superRA/references/main-agent.md`, `skills/using-superRA/references/codex-tools.md`, `skills/using-superRA/references/gemini-tools.md`, `skills/planning-workflow/SKILL.md` (5 hits), `skills/integration-workflow/SKILL.md` (3 hits), `skills/handoff-doc/references/plan-anatomy.md` (3 hits), `skills/agent-orchestration/references/agent-teams.md` (1 hit), `skills/econ-data-analysis/SKILL.md`, `skills/econ-data-analysis/references/planning.md`, `skills/report-in-markdown/SKILL.md`, `hooks/exit-plan-mode`, `tests/structural-invariants.sh`. README.md had zero hits. Re-grep confirmed zero remaining `execution-workflow` occurrences outside `docs/plans/`.
- [x] **Step 4: Run `bash tests/structural-invariants.sh`.** Updated all `execution-workflow` references in the test to `implementation-workflow`. All invariants pass except the pre-existing `README.md missing '## Workflow Map'` failure (out of scope).
- [x] **Step 5: Commit** as one atomic rename commit.

### Task 6: Verify End-to-End
**Depends on:** Task 5
**Review status:** APPROVED *(verification pass done inline by orchestrator — all greps clean, invariants pass)*

- [x] **Step 1: Grep `execution-workflow`** — zero live hits across `skills/`, `agents/`, `hooks/`, `CLAUDE.md`, `README.md`, `AGENTS.md`, `tests/` (excluding `docs/plans/` archive).
- [x] **Step 2: Grep `Stage: merge` and `planning-review`** — zero live hits. The one `planning-review` match is in `tests/structural-invariants.sh:410` as a comment explaining why the stage was dropped; that's the test documenting its own history, not a live pointer.
- [x] **Step 3: Grep emitted Stage values.** Live emissions: `implementation` (implementation-workflow:108), `integration` (integration-workflow:93, 132), `documentation` (integration-workflow:167, 188). All match generic-table rows. Additional prose mentions of `Stage: integration` in `using-superRA:76`, `refactor-and-integrate` skill + merge-quality reference are contextual (describing when semantic-merge rides on integration Stage), not new emissions.
- [x] **Step 4: Run `bash tests/structural-invariants.sh`** — all invariants pass except the pre-existing `README.md missing '## Workflow Map'` failure, confirmed out of scope.
- [x] **Step 5:** No final fixups needed.

---

### Task 7: Consolidate Orchestrator Discipline (DRY)
**Depends on:** Task 6
**Review status:** APPROVED

Content-preservation review of commit 7e0ba6f — verifies the consolidation of orchestrator discipline from `implementation-workflow` into `agent-orchestration` is lossless.

