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

- [ ] **Plan approved** — researcher signed off on this plan
- [ ] **Execution complete** — all tasks `APPROVED`, invariants green
- [ ] **Drift tests created** — *(n/a for skill-edit work; `structural-invariants.sh` is the standing guard)*
- [ ] **Refactored** — integration pass if relevant
- [ ] **Docs finalized** — README / CATEGORIES / CLAUDE.md references all repointed
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
**Review status:** REVISE

Grep confirms zero live `Stage: merge` emissions. Standalone `semantic-merge` dispatches should carry their Stage on the dispatch side; the manifest stops enumerating it.

- [x] **Step 1: Remove the `merge` row** from the generic Stage table in `skills/using-superRA/SKILL.md`.
- [x] **Step 2: Remove the post-table prose paragraph** that explains the `merge` stage's standalone-`semantic-merge` role. Preserved the sentence about `integration-workflow` Phase B loading `semantic-merge` (still valid and useful).
- [x] **Step 3: Update `tests/structural-invariants.sh`** — dropped `merge` from the Stage-row regex, changed expected count 5 → 4, updated the comment to explain the drop.
- [x] **Step 4: Run `bash tests/structural-invariants.sh`** — manifest row-count invariant passes at 4. Pre-existing `README.md missing '## Workflow Map'` failure is unrelated and out of scope.

> **Review notes (2026-04-20):**
>
> 1. **[BLOCKING] MAJOR — `skills/refactor-and-integrate/SKILL.md` lines 3 and 30 — stale `merge` Stage pointer.** The frontmatter description (line 3) still says dispatched subagents load this skill when their Stage is `"drift-test', 'integration', or 'merge'"`, and the §Three Concurrent Disciplines §3 Merge Quality body (line 30) says `"Stage 'merge' → load 'references/merge-quality.md'"`. Both are live, skill-consumer-facing statements pointing at a manifest row that no longer exists. Any agent reading this skill will see a valid-looking pointer to `Stage: merge` that contradicts the manifest. Fix: update both to remove the `Stage: merge` framing — the merge-quality discipline is still valid and `references/merge-quality.md` still exists (for use by agents inside `integration-workflow` Phase D), but the triggering condition should be reworded to remove the manifest-row claim (e.g., "during merge integration commits within `integration-workflow` Phase D").
>
> 2. **[BLOCKING] MAJOR — `skills/refactor-and-integrate/references/merge-quality.md` line 3 — stale manifest pointer.** Opening sentence says `"Loaded whenever 'Stage:' is 'merge' (per 'superRA:using-superRA' §Skill-Load Manifest)"`. After this commit the manifest no longer has a `merge` row, so this sentence is factually wrong. Fix: reword the opening sentence to reflect how the file is now loaded (by agents doing merge integration inside `integration-workflow` Phase D or standalone `semantic-merge` dispatches, not via a manifest Stage row).
>
> **Verified passing:**
> - `using-superRA/SKILL.md` generic table: 4 rows, no `merge` row present.
> - Post-table prose: the standalone-dispatch paragraph is gone; the Phase B `semantic-merge` sentence (line 76) is preserved.
> - `tests/structural-invariants.sh`: regex and count correct; invariant #20 reports PASS at 4 rows.
> - Zero live `Stage: merge` emissions in `skills/`, `agents/`, `hooks/`.
> - Only FAIL in test run is the pre-existing `README.md missing '## Workflow Map'`, out of scope.

### Task 4: Add "Emitted by" Column to Generic Manifest Table
**Depends on:** Task 3
**Review status:** *(set during execution)*

- [ ] **Step 1: Add a middle column** to the generic Stage table mapping each Stage to the workflow + phase that emits it:
  - `implementation` → `implementation-workflow` (post-Task 5 name; if Task 5 hasn't landed yet, use `execution-workflow` here and let Task 5's rename sweep fix it)
  - `drift-test` → `integration-workflow` Phase A
  - `integration` → `integration-workflow` Phase B
  - `documentation` → `integration-workflow` Phase C
- [ ] **Step 2: Verify each workflow file already names its Stage** in dispatch blocks / self-description. Expected hits:
  - `execution-workflow` ~line 108 + 211 (`Stage: implementation`)
  - `integration-workflow` line 69 (`Stage: drift-test`), 93 + 132–133 (`Stage: integration`), 167 + 188 (`Stage: documentation`)
  If any phase lacks an explicit `Stage: <name>` line, add it.
- [ ] **Step 3: Run invariants, commit.**

### Task 5: Rename `execution-workflow` → `implementation-workflow`
**Depends on:** Task 3 (structural), Task 4 (content)
**Review status:** *(set during execution)*

- [ ] **Step 1: Rename the directory.** `git mv skills/execution-workflow skills/implementation-workflow`.
- [ ] **Step 2: Update the skill frontmatter** in `skills/implementation-workflow/SKILL.md` — `name: implementation-workflow`; refresh self-announce line and any internal `execution-workflow` self-reference.
- [ ] **Step 3: Sweep all references across repo.** Files identified at planning time (grep count):
  - `CLAUDE.md` (2)
  - `README.md`
  - `skills/CATEGORIES.md` (1)
  - `skills/using-superRA/SKILL.md` (1)
  - `skills/using-superRA/references/main-agent.md` (1)
  - `skills/using-superRA/references/codex-tools.md` (1)
  - `skills/using-superRA/references/gemini-tools.md` (1)
  - `skills/planning-workflow/SKILL.md` (5)
  - `skills/integration-workflow/SKILL.md` (3)
  - `skills/handoff-doc/references/plan-anatomy.md` (3)
  - `skills/agent-orchestration/references/agent-teams.md` (1)
  - `skills/econ-data-analysis/SKILL.md` (1)
  - `skills/econ-data-analysis/references/planning.md` (1)
  - `skills/report-in-markdown/SKILL.md` (1)
  - `tests/structural-invariants.sh`
  Re-grep after edits to confirm zero remaining `execution-workflow` occurrences outside `docs/plans/` (historical, untouched).
- [ ] **Step 4: Run `bash tests/structural-invariants.sh`.** If any test references `execution-workflow` by name, update the test.
- [ ] **Step 5: Commit** as one atomic rename commit.

### Task 6: Verify End-to-End
**Depends on:** Task 5
**Review status:** *(set during execution)*

- [ ] **Step 1: Grep `execution-workflow`** across `skills/`, `agents/`, `hooks/`, root-level docs → expect zero hits.
- [ ] **Step 2: Grep `Stage: merge`** and `planning-review` → expect zero hits in live code.
- [ ] **Step 3: Grep emitted Stage values** against manifest rows — every `Stage: <name>` in `skills/` and `agents/` matches a row in the generic table.
- [ ] **Step 4: Run `bash tests/structural-invariants.sh`** — all pass (modulo the pre-existing `## Workflow Map` README failure, which is out of scope).
- [ ] **Step 5: Commit any final fixups.**
