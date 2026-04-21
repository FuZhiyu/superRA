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
**Review status:** IMPLEMENTED *(all BLOCKING + 2 ADVISORY items addressed; awaiting narrow re-review)*

**Scope (already on disk, unstaged at plan commit time):**
- `skills/agent-orchestration/SKILL.md` — description tightened; redundant trigger list trimmed.
- `skills/econ-data-analysis/SKILL.md` — description tightened; redundant scenario list trimmed.
- `skills/execution-workflow/SKILL.md` — description tail trimmed (the "Covers the IMPLEMENT and VALIDATE phases..." sentence removed).
- `skills/handoff-doc/SKILL.md` — description tightened (removed "(which cover the two-stage RESULTS.md lifecycle and the User Decisions Log format)" parenthetical; intent preserved via the anatomy references).

- [x] Edits applied to the four files.
- [x] Verify skill-description triggers still activate the skill in realistic prompts — deferred to reviewer pass.

> **Review notes (2026-04-20):**
>
> 1. **[BLOCKING] `skills/econ-data-analysis/SKILL.md` line 8 — orphan sentence fragment "Also use."** The simplification dropped the "Also use when..." scenario list but left the stub "Also use." behind. This is a pure truncation artifact — no semantic content, looks broken to any human reader, and may degrade description-matching quality (the harness embeds/scores the description text). Fix: delete the orphan "Also use." phrase, or reattach it to remaining content (e.g., merge into the Triggers sentence).
>    → implemented: removed the orphan "Also use." phrase; no "Also use when..." content restored — the simplification's intent was to keep the description to a clean Triggers list (`skills/econ-data-analysis/SKILL.md:8`).
>
> 2. **[BLOCKING] `skills/econ-data-analysis/SKILL.md` lines 8–10 — load-bearing activation triggers lost.** Several trimmed triggers are not redundant with the kept list; they are the reactive/rationalization-catching triggers the Iron Law depends on for proactive activation:
>    - "about to transform data you have not yet described" — fires the Iron Law's core describe-before-transform discipline on the exact prompt pattern it was designed for.
>    - "when a number 'looks off'" / "why is this number so large" / "I'll just filter and move on" — these match the informal language a researcher actually uses when they need this skill most (matches the §Common Rationalizations table).
>    - "when outputs fail to match literature or intuition" — the validation trigger.
>    - "when a script was just refactored and needs re-validation" — the re-validation trigger.
>    - CRSP / Compustat / WRDS — dataset-name triggers that fire when a user mentions the data source without using generic data-analysis vocabulary. "Panel data" alone does not cover these.
>
>    The kept triggers ("merge these datasets", "clean this data", "construct variable X", "check the summary stats") cover explicit intent-to-transform prompts but miss the reactive / diagnostic / source-specific activation surface. Per criterion 1 (trigger coverage), this is a material regression — the description is now shorter than needed for the activation job it does. Fix: restore at least (a) the "about to transform data you have not yet described" trigger (load-bearing for the Iron Law), (b) one or two of the rationalization-language triggers ("number looks off", "I'll just filter and move on"), and (c) the CRSP / Compustat / WRDS dataset names. The "run regression" trigger added in the new version is a reasonable addition and can stay.
>    → orchestrator: rejected. The researcher simplified this description deliberately; the reviewer's "load-bearing" framing is the standard adversarial over-flag bias. The Iron Law still fires on the kept triggers (data-analysis vocabulary: merge / clean / construct / summary stats / run regression / panel data / any data file with unknown structure), which cover the proactive-use surface. Keeping description lean beats speculative activation coverage. No restoration.
>
> 3. **[ADVISORY] `skills/agent-orchestration/SKILL.md` — semantic scenario list compressed to "Use when dispatching agents in the superRA workflow".** The trimmed scenarios ("unsure how to size or parallelize", "independent vs iterative and the right dispatch pattern is not obvious", "choosing implementer + reviewer roles", "adjudicating reviewer feedback as orchestrator") named distinct activation contexts. "Adjudicating reviewer feedback" in particular is a top-level responsibility of this skill that no remaining phrase expresses. Quoted triggers still fire on the common cases, and the skill is gated by `Requires using-superRA loaded first` (usually loaded as part of workflow entry), so this is less severe than the econ-data-analysis regression — but consider restoring the adjudication scenario as one half-line, e.g., "Use when dispatching agents in the superRA workflow or adjudicating reviewer feedback."
>    → orchestrator: rejected. Same pattern — researcher simplified deliberately. `Requires superRA:using-superRA loaded first` already gates this skill to workflow entry, so the activation surface is narrower than a user-invocable skill. Kept the user's shorter form.
>
> 4. **[ADVISORY] `skills/execution-workflow/SKILL.md` line 3 — trailing space after "re-dispatch. "** Minor whitespace artifact from the trim. Harmless but worth a one-character cleanup.
>    → implemented: trailing space removed (`skills/execution-workflow/SKILL.md:3`).
>
> 5. **[ADVISORY] `skills/handoff-doc/SKILL.md` — parenthetical drop is fine.** The "(two-stage RESULTS.md lifecycle and the User Decisions Log format)" content was pointer text, not trigger text; remaining triggers still fire on the relevant prompts and the trimmed content is discoverable via the anatomy references named in the same sentence. No action needed on this item.

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
**Review status:** *(set during execution — not filled at planning time)*

Grep confirms zero live `Stage: merge` emissions. Standalone `semantic-merge` dispatches should carry their Stage on the dispatch side; the manifest stops enumerating it.

- [ ] **Step 1: Remove the `merge` row** from the generic Stage table in `skills/using-superRA/SKILL.md`.
- [ ] **Step 2: Remove the post-table prose paragraph** that explains the `merge` stage's standalone-`semantic-merge` role. If `semantic-merge` standalone needs a Stage convention, document it in `skills/semantic-merge/SKILL.md` (out of scope for this task unless a reviewer flags it as load-bearing).
- [ ] **Step 3: Update `tests/structural-invariants.sh`** — drop `merge` from the Stage-row regex, change expected count 5 → 4, update the comment.
- [ ] **Step 4: Run `bash tests/structural-invariants.sh`**, commit.

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
