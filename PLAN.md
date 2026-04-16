# superRA Design Coherence Refactor — Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. This is plugin-development work, not a data-analysis vertical — `superRA:econ-data-analysis` does not apply. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff.

**Objective:** Consolidate superRA's design coherence per the design review. Eliminate stage-name drift, redundant restatements, hollow pointers, and orphaned skills. Tighten workflow boundaries. Slim the skill inventory.

**Methodology:** Per-skill edits to existing files (no new skills, two skills removed). Each task changes one concern and lands in one atomic commit (code + PLAN.md + RESULTS.md). Validation per task is end-to-end re-reading of every touched file plus targeted grep for orphan references. For any skill whose `description:` field is touched, run `superRA:writing-skills` triggering checks.

**Domain vertical:** Not data analysis. The `superRA:planning-workflow` Phase 1 Data Inventory hard gate does not apply — flagged explicitly. The implementer–reviewer pair, handoff-doc discipline, atomic-commit rule, and four workflow principles all carry over unchanged.

**Conventions:**
- One concern per task; one atomic commit per task.
- Use `Edit` (not `Write`) for surgical changes; preserve existing prose tone.
- After every task: re-read each touched file end-to-end; grep for orphan references to moved/removed content.
- Where a skill description changes, walk `superRA:writing-skills` triggering checks — descriptions are load-bearing for skill-discovery.
- Tasks may rewrite earlier-task steps in place if a finding changes the right approach for downstream work (the inline-edit rule).

**Output:** A refactored superRA plugin with:
- Stage names that match the manifest 1:1 (no fallbacks, no dispatch-time re-statements).
- Skill inventory reduced by 2 (`script-to-notebook` folded into `econ-data-analysis` references; `using-analysis-worktrees` folded into a broadened `worktree-data-sync`).
- `verification-before-completion` threaded into implementer/reviewer/orchestrator self-checks.
- Single source of truth for: User Decisions Log discipline, dispatch templates, four principles + autonomy, Stage→loads mapping.
- No restatement of manifest content in dispatch prompts.
- Project docs audit absorbed into the integration Stage 2 refactor/review loop (the doc-writer becomes RESULTS.md-only).

**Expected results:** Smaller, more coherent skill set. Cheaper agent loads (especially reviewer dispatches). Fewer drift surfaces. Same workflow behavior end-to-end.

**Pipeline:** No automated pipeline (this is a doc/skill refactor, not code). Per-task validation is manual: re-read affected files, grep for orphans. The closing Task (Final Consistency Pass) sweeps the whole repo to catch interactions.

**Pre-execution note:** The working directory `.git` is a stale worktree pointer (target path doesn't exist in the parent repo's `worktree list`). Repair before the first commit — either re-add the worktree from `/Users/zhiyufu/Dropbox/package_dev/econ-superpowers` with `git worktree add`, or convert this directory into a fresh clone / branch checkout. Until git works here, no commits land.

**Task sequencing note:** Tasks 1, 3, 4, and 6 are coupled. Sequence: **Task 1 → Task 4 → Task 3 → Task 6.**
- Task 1 establishes canonical Stage names + adds the `integration-review` manifest row (with current load contents preserved).
- Task 4 creates `econ-data-analysis/references/notebook-format.md` from script-to-notebook content.
- Task 3 slims `econ-data-analysis/SKILL.md`, creates `references/disciplines.md`, and absorbs the writing-discipline content into the now-existing `notebook-format.md` (Task 4 Step 1b finalizes the merge).
- Task 6 then sweeps the manifest: drops `handoff-doc` from most rows, applies the role-split for the `implementation` row's references created by Tasks 3 and 4.
Other tasks have no manifest dependency and may run in any order after Task 6.

---

## Decisions

> **User decision (2026-04-16):** Commit the 3 pre-existing uncommitted files as-is before starting Task 1.
> **Question asked:** How to handle 3 files with uncommitted modifications (version bumps in plugin.json/marketplace.json, deletion of EXTREMELY-IMPORTANT/Red Flags/Skill Types sections in using-superRA/SKILL.md) that are unrelated to Tasks 1–16.
> **Rationale:** *(none given — user chose to preserve the prior intentional work as an atomic pre-plan commit)*

> **User decision (2026-04-16):** Add Task 17 to the refactor — document the agent-reuse vs fresh-dispatch heuristic in `agent-orchestration` SKILL.md.
> **Question asked:** *(researcher-initiated, not agent-prompted — raised after observing orchestrator behavior during parallel dispatch of Task 1 + Task 15.)*
> **Rationale:** Each fresh dispatch reloads skills + PLAN.md + module-level guidance; for small sequential follow-ups the context-reload cost outweighs the benefit. The heuristic should be written into the skill so future orchestrators apply it automatically. Reviewer role is a named exception (always fresh — adversarial by design).

---

### Task 1: Consolidate Stage names + remove dispatch re-statements
**Review status:** APPROVED

**Files affected:** `skills/using-superRA/SKILL.md`, `skills/execution-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/merge-workflow/SKILL.md`, `skills/semantic-merge/SKILL.md`, `skills/refactor-and-integrate/SKILL.md`, `agents/implementer.md`, `agents/reviewer.md`
**Input:** Current dispatch sites (grep targets below); current manifest (using-superRA §Skill-Load Manifest).
**Output:** Manifest is the single source of truth for Stage→{skills, references}. Every `Stage:` value in every dispatch matches a manifest row. Per-workflow `Skills:` / `Domain reference:` / "Agent Types and Domain References" tables are deleted.

- [x] **Step 1: Audit Stage names actually emitted.** Grep returned eleven distinct non-canonical values across `skills/` and `agents/`: `implementation`, `implementation review`, `drift test creation`, `drift test`, `integration review`, `refactoring`, `documentation finalization (Stage 2 RESULTS.md + project doc audit)` (emitted twice), `merge`, `merge proposer`, `merge proposer (Tier 3)`, and `integration` (from refactor-and-integrate's dispatch example). Matches the expected list.

- [x] **Step 2: Decide canonical names + update manifest.** Added the new `integration-review` row to `using-superRA/SKILL.md` §Skill-Load Manifest (same reference load as `refactoring`, preserved verbatim — Tasks 3 and 6 will refine later per the Task-sequencing note). Replaced the `Fallback rule` paragraph with: "**Unknown Stage values are a dispatch error.** If the dispatch prompt carries a `Stage:` that does not match a row above, halt and report the mismatch in your status return — do not guess." Canonical name for integration review is `integration-review` (hyphenated, matching the `drift-test` convention, per override #8).

- [x] **Step 3: Sweep all dispatch sites.** Rewrote every non-canonical `Stage:` value to its canonical name:
  - `integration-workflow`: `drift test creation` → `drift-test`; `drift test` → `drift-test`; `integration review` → `integration-review`; `documentation finalization (...)` → `documentation` (sub-part A/B context moved into `Additionally:`).
  - `merge-workflow`: `integration review` → `integration-review`.
  - `semantic-merge`: `merge proposer` → `merge`; `merge proposer (Tier 3)` → `merge` (Tier 2 / Tier 3 context moved into `Additionally:`).
  - `refactor-and-integrate`: the two dispatch examples (`drift test creation` / `integration`) replaced with a one-line pointer at `agent-orchestration` §Dispatch Templates per Step 4.
  - `execution-workflow`: the `Agent Types` section's reviewer line referenced `Stage: implementation review` — rewrote to state both roles use `Stage: implementation` and `subagent_type` carries the split. The §Dispatch Templates pointer paragraph that named `Stage: implementation review` was likewise updated.

- [x] **Step 4: Delete redundant `Skills:` / `Domain reference(s):` lines from every dispatch template.** Every Stage-line dispatch block across `integration-workflow`, `merge-workflow`, `semantic-merge`, and `refactor-and-integrate` has been reduced to the canonical shape (`Stage:` + `Task:` + `Git range:` (reviewers only) + `Additionally:`). Large free-form context fields (`Key results to protect:`, `Tests under review:`, `Code under review:`, `Codebase conventions:`, `Merge context:`, `Incoming changes:`, etc.) were also dropped — the dispatched agent reads these from `PLAN.md` / `RESULTS.md` directly. The `refactor-and-integrate` §Dispatch Convention examples were replaced with a single paragraph pointing at `agent-orchestration` §Dispatch Templates and naming which manifest rows load this skill.

- [x] **Step 5: Delete per-workflow Agent-Types tables.** Removed `## Agent Types and Domain References` from `integration-workflow/SKILL.md` and `semantic-merge/SKILL.md`, and the `## Agent Types` section from `execution-workflow/SKILL.md`. Each replaced with a short `## Agent Loads` section that points at `superRA:using-superRA` §Skill-Load Manifest and names the manifest rows the workflow runs.

- [x] **Step 6: Update agents/{implementer,reviewer}.md "Before You Start" steps 3 and 4.** Rewrote step 3 in both files to: "Load any additional skill the dispatch's `Additionally:` line names (rare — overrides only; the manifest is the default)." Deleted step 4 entirely. Renumbered the remaining steps (5→4, 6→5, 7→6) and updated the in-paragraph cross-reference ("see step 7 below" → "see step 6 below"). Also updated both agent files' §Stage → skills and references paragraph: the old fallback to `implementation` defaults is replaced with a halt-and-report instruction, matching the manifest's new no-fallback policy.

- [x] **Step 7: Validate.** Re-grepped `Stage:` across `skills/` and `agents/`: every emitted value is now `implementation`, `drift-test`, `refactoring`, `integration-review`, `merge`, or `documentation` — all manifest rows. Re-grepped `Skills:` / `Domain reference` in dispatch sections: zero hits in dispatch blocks; two meta-level matches remain (`agent-orchestration:77` describing the canonical template's optional override fields, and `refactor-and-integrate:36` stating dispatches do not restate these lines) — both legitimate. Re-read every touched workflow skill end-to-end: dispatch templates match the canonical shape (`Stage:` + `Task:` + optional `Git range:` + `Additionally:`). Also fixed two stale `integration review` references in `integration-workflow` Red Flags / Always lists to `integration-review`. Refactor-and-integrate's `description:` frontmatter was edited to enumerate the new canonical Stage names; `superRA:writing-skills` triggering-check: the description still fires on its original triggers (drift tests, refactor, merge integration commits) and the change only synchronizes the enumeration of Stage names with the new manifest — no trigger surface change.

---

### Task 2: Drop Agent Teams "recipe" framing
**Review status:** IMPLEMENTED

**Files affected:** `skills/execution-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/merge-workflow/SKILL.md`, `skills/semantic-merge/SKILL.md`, `skills/agent-orchestration/SKILL.md`
**Input:** The four workflow skills' "Agent Teams Mode" sections.
**Output:** No skill claims a per-workflow team "recipe" exists. Spawn instructions live only in `agent-teams.md`; team composition is derived from the manifest.

- [x] **Step 1: Remove "Invoke for the [X Team] recipe" lines** from each workflow's "Agent Teams Mode" section. All four "Invoke `superRA:agent-orchestration` for the [X] Team recipe" sentences replaced with the pointer "See `superRA:agent-orchestration` §Integration and `references/agent-teams.md` for spawn mechanics. Composition is derived from the manifest — one teammate per stage this workflow runs." The enumerations ("6 teammates: test-creator, test-reviewer, …", "4 teammates …", "7-task graph", "2 teammates") are gone; spawn details live only in `agent-teams.md`. Also updated `execution-workflow` line 43 (the bullet inside the Agent Team mode block mentioning "Load `superRA:agent-orchestration` for the Task Team recipe") to the same pointer language, and cleaned the `semantic-merge` §Integration pairs-with line ("Semantic Merge Team recipe for Tier 2/3 merges" → "§Integration and `references/agent-teams.md` for team spawn mechanics on Tier 2/3 merges"). Collapsed the redundant "When Agent Teams are available" lead-in that resulted from the replacement into a single opening sentence per section.

- [x] **Step 2: Update agent-orchestration §Integration.** Rewrote the lede from "Skills that use Agent Teams mode (composition derived from the manifest…)" to explicitly state "There are no per-workflow team 'recipes' — composition is read from the workflow (which stages it runs) and the manifest (what each stage loads)." Each workflow entry now names its runs-stages list rather than team-type: `execution-workflow` → stages: implementation; `integration-workflow` → drift-test, refactoring, integration-review, documentation; `merge-workflow` → merge, refactoring, integration-review; `semantic-merge` → merge. Pointer at `references/agent-teams.md` for spawn mechanics preserved in the same paragraph.

- [x] **Step 3: Validate.** Grep for "recipe" across `skills/` returns four hits — three in `agent-orchestration` (SKILL.md:14 + references/agent-teams.md:8,50) and each is a "no per-workflow recipe is needed" statement (the desired state), plus the new "There are no per-workflow team 'recipes'" line in §Integration. No skill body still claims a per-workflow team recipe exists. Re-read each workflow's "Agent Teams Mode" section end-to-end: every section now defers to `agent-orchestration` for spawn mechanics and derives composition from the manifest. Atomic commit staged: `task 2: drop Agent Teams recipe framing`.

---

### Task 3: Slim `econ-data-analysis/SKILL.md` (shared base) + extract one operational-disciplines reference
**Review status:** APPROVED

**Files affected:** `skills/econ-data-analysis/SKILL.md`, `skills/econ-data-analysis/references/disciplines.md` (new — combined Describe + Analyze + Validate), `skills/econ-data-analysis/references/notebook-format.md` (absorbed Writing Discipline section), `skills/using-superRA/SKILL.md` (manifest), `agents/implementer.md`, `agents/reviewer.md`
**Input:** Current `econ-data-analysis/SKILL.md` (473 lines pre-refactor).
**Output:** Both implementer and reviewer load SKILL.md (276 lines, down from 473) — the shared base with the §Review & Self-Check Discipline both walk (now with `Why:` rationales on every [GATING] item and selected [STANDARD] items), plus Pitfalls (reviewer needs it for operation review), Common Rationalizations, and Red Flags. Implementer additionally loads `references/disciplines.md` (195 lines — full DAV operational content) and `references/notebook-format.md` (cell organization + the absorbed writing-discipline section + rendering). Reviewer loads SKILL.md only.

**Architectural design.** DAV (Describe / Analyze / Validate) are **concurrent disciplines** applied at every implementation step — splitting them into three reference files is overkill since the implementer always loads all three together. One combined reference is cleaner. The "Documentation — cross-cutting writing practice" section dissolves entirely: its conceptual one-liner moves into the SKILL.md three-disciplines intro; the writing mechanics (markdown cells when, inline comments when, figures pointer, major-vs-minor-decision rule) move to `notebook-format.md` (its natural home — script-formatting + writing discipline are one concern); the per-step checklist deletes (it duplicates §Review & Self-Check Discipline gates).

| Section in current SKILL.md | Lines | Goes to | Loaded by |
|---|---|---|---|
| Iron Law | 15 | SKILL.md | both |
| Three Concurrent Disciplines intro (one para each, including "doc is concurrent") | 5 | SKILL.md | both |
| Describe + Analyze + Validate (full operational content) | 195 | `references/disciplines.md` | implementer |
| Documentation cross-cutting writing practice | 25 | (split: 1 line into SKILL.md intro; ~20 lines into `notebook-format.md` §Writing Discipline; ~5 lines deleted as redundant with §Review checklist) | n/a |
| §Review & Self-Check Discipline (with `Why this matters` annotations) | 80 | SKILL.md | both walk it |
| Common Rationalizations | 15 | SKILL.md | both |
| Red Flags - STOP and Start Over | 15 | SKILL.md | both |
| Pitfalls (operation-specific catalog) | 60 | SKILL.md | both — reviewer needs it to verify merges, lags, aggregations, etc. |
| Key References | 5 | SKILL.md | both |

Result: SKILL.md 276 lines (slightly over the ~210 target — the `Why:` rationales on every [GATING] item and several [STANDARD] items added ~30 lines, which is the explicit Step 4 goal). Reviewer load 276. Implementer load 276 + 195 (`disciplines.md`) + 110 (`notebook-format.md` post-absorption) ≈ 581 total — split into three discoverable chunks instead of one 473-line wall, and the shared checklist now carries explicit reasoning that protects against mechanical checklist-walking.

- [x] **Step 1: Create `references/disciplines.md`.** File created with a 2-paragraph `## How to read this file` intro re-anchoring the Iron Law and the concurrent-disciplines framing. Preserves the `## Describe` / `## Analyze` / `## Validate` section structure verbatim from the pre-refactor SKILL.md, including every existing subsection (Describe's after-loading / before-merge / outliers / after-transformation / visualization; Analyze's row-count rule, sort discipline, join discipline; Validate's sanity / multi-source / missing-data / sensitivity). References to §Pitfalls within the file point at `SKILL.md §Pitfalls` since Pitfalls stays in SKILL.md (reviewer needs it). Final line count: 195.

- [x] **Step 2: Dissolve the Documentation cross-cutting section.** From SKILL.md's "Documentation — cross-cutting writing practice" section:
  - Kept the one-line conceptual statement — folded into the new SKILL.md three-disciplines intro ("Documentation runs continuously alongside them as a cross-cutting writing practice, not a fourth phase").
  - Moved the §Writing discipline subsection (markdown cells when, inline comments when, figures pointer, major-vs-minor-decision rule) into `notebook-format.md` as a new `## Writing Discipline` section placed after §Markdown Cells. Added a closing paragraph making the major/minor split explicit ("minor decisions inside a cell document *the choice*; major decisions in a markdown cell document *the reasoning that led to the choice*"). Task 4 had already landed `notebook-format.md` as the real file, so the content lands directly — no draft staging needed. (Task 4's Step 1b RESULTS note flagged this handoff.)
  - Deleted the §Short checklist per step — duplicates §Review & Self-Check Discipline gates.
  - Deleted the §Script categories paragraph — already covered by `notebook-format.md`'s §When to Use section.

- [x] **Step 3: Rewrite the slim SKILL.md.** New structure in place: Header + Stage-Scoped References → Iron Law → Three Disciplines intro (three paragraphs — Describe / Analyze / Validate; each ending with a pointer to `references/disciplines.md` §{Describe|Analyze|Validate}; a closing sentence points at `references/notebook-format.md` for writing mechanics) → §Review & Self-Check Discipline → Pitfalls → Common Rationalizations → Red Flags → Key References. The prior §Verification Checklist placeholder ("For pre-handoff self-check and reviewer verification, see §Review & Self-Check Discipline above") is deleted entirely — it was a stub pointing at the section immediately above it, serving no navigation purpose after the reorder. Stage-Scoped References table gained a new row for `disciplines.md` (IMPLEMENT + VALIDATE phase; implementer-only load); the `notebook-format.md` row was updated to name the writing-discipline content explicitly.

- [x] **Step 4: Add `Why this matters` annotations** to §Review & Self-Check Discipline. Every `[GATING]` item now carries a bulleted `*Why:*` sub-item (10 items total — 3 under Gating, 1 under Documentation and handoff, 4 under Refactor integrity, 3 under Completion verification). Selected `[STANDARD]` items carry rationales where the item could be misapplied without context: "PLAN.md-specifies" / "Major vs minor decisions" under Implementation standards, and "PLAN.md expectations comparison" under Validation completeness. `[ADVISORY]` items remain bare. The annotations frame verification as principled (why this gate exists) rather than mechanical (is the box ticked), per Step 4's anti-mechanical-walking rationale.

- [x] **Step 5: Update the manifest** (`using-superRA` §Skill-Load Manifest). The `implementation` row's Stage-scoped-references cell now reads: "domain §Review & Self-Check Discipline. For data analysis: **implementer** additionally loads `econ-data-analysis/references/disciplines.md` + `references/notebook-format.md`; **reviewer** loads SKILL.md only (its §Review & Self-Check Discipline is self-sufficient for verification; §Pitfalls is in SKILL.md — if the dispatcher wants a specific Pitfalls subsection highlighted for review, it names it in `Additionally:`)." The lede paragraph above the manifest table was updated to acknowledge role differentiation now appears on two rows (`implementation` and `documentation`), not just one.

- [x] **Step 6: Update agent files.**
  - `agents/implementer.md` step 2 rewrote to enumerate the exact loads for the `implementation` row in data analysis: `SKILL.md` (shared base) + `references/disciplines.md` (operational content) + `references/notebook-format.md` (writing + rendering). The "shared §Review & Self-Check Discipline, two perspectives" framing is preserved.
  - `agents/reviewer.md` §Stage → skills and references lede now reads: "You walk the same §Review & Self-Check Discipline from the active domain skill that the implementer walks as pre-handoff self-check — one source of truth, two perspectives. On the `implementation` row the implementer loads additional operational references (for data analysis: `references/disciplines.md` + `references/notebook-format.md`); you do NOT load those — SKILL.md is self-sufficient for verification." Step 2 rewrote to name the load boundary ("load `superRA:econ-data-analysis/SKILL.md` only") and to note that an `Additionally:` Pitfalls-focus line is the hook if a specific operation needs highlighted review.

- [x] **Step 7: Validate.** Re-read `SKILL.md` end-to-end — the three-disciplines intro reads as a self-sufficient summary that points at the deep content; the §Review & Self-Check Discipline section now carries explicit reasoning on every gating item; §Pitfalls sits between the checklist and the rationalizations, followed by Red Flags and Key References (the target ordering). Re-read `disciplines.md` end-to-end — the 2-paragraph intro re-anchors Iron Law + concurrent-disciplines framing so the file reads standalone; the three sections flow together naturally (the concurrent framing makes this intuitive). Re-read `notebook-format.md` — the absorbed §Writing Discipline section sits naturally between §Markdown Cells and §Output; the major-vs-minor-decision rule is now explicit in its own closing paragraph. Section-header grep confirms the final SKILL.md section order (Iron Law → Three Disciplines → Review & Self-Check → Pitfalls → Common Rationalizations → Red Flags → Key References). Atomic commit staged: `task 3: slim econ-data-analysis/SKILL.md + extract disciplines.md reference`.

---

### Task 4: Move `script-to-notebook` into `econ-data-analysis` as a reference
**Review status:** APPROVED

**Files affected:** `skills/script-to-notebook/SKILL.md` (delete), `skills/script-to-notebook/references/*.md` (move), `skills/econ-data-analysis/references/notebook-format.md` (new), `skills/econ-data-analysis/references/jupytext-guide.md` (move), `skills/econ-data-analysis/references/julia-quarto-guide.md` (move), `skills/econ-data-analysis/SKILL.md`, `skills/using-superRA/SKILL.md`, `skills/CATEGORIES.md`, `README.md`, `agents/reviewer.md`, `skills/refactor-and-integrate/SKILL.md`, `skills/planning-workflow/SKILL.md`, `skills/execution-workflow/SKILL.md`
**Input:** Current `script-to-notebook` skill + its two references.
**Output:** Notebook-formatting content lives under the data-analysis vertical. Standalone skill is removed. Skill inventory shrinks by one.

- [x] **Step 1: Move content.** `skills/script-to-notebook/SKILL.md` → `skills/econ-data-analysis/references/notebook-format.md`; `jupytext-guide.md` and `julia-quarto-guide.md` moved from `skills/script-to-notebook/references/` to `skills/econ-data-analysis/references/` (via `git mv` — history preserved). Frontmatter trimmed from the old skill-style block (name / description / user-invocable) to a single one-line blockquote placed under the new `# Notebook Format` heading. Title changed from `# Script to Notebook` to `# Notebook Format`.

- [x] **Step 1b: Absorb the writing-discipline content from Task 3 Step 2.** Task 3 has not yet run, so no `notebook-format.md.draft` existed at implementation time. Per dispatch override, proceeded with Step 1 content as-is. When Task 3 runs, its Step 2 will absorb the dissolved §Documentation cross-cutting writing practice section into `notebook-format.md` as a new "Writing Discipline" section after the cell-organization section (per Task 3's spec).

- [x] **Step 2: Delete the skill folder.** `skills/script-to-notebook/` no longer exists in the working tree — the three files were moved via `git mv` in Step 1, leaving the directory empty, and git has already removed it.

- [x] **Step 3: Update `econ-data-analysis/SKILL.md`** §Stage-Scoped References table — added a new `references/notebook-format.md` entry (IMPLEMENT + VALIDATE phase; companion guides `jupytext-guide.md`, `julia-quarto-guide.md`). Also added a `references/integration.md` row that was missing from the table (it is named in the manifest but was not listed in this SKILL.md). Lede sentence updated from "Two companion reference files ..." to "Companion reference files ..." since the table now carries five entries. All four inline `superRA:script-to-notebook` mentions in the body (Describe §Visualization rendering pointer; Documentation §Script categories; Documentation §Figures; §Review & Self-Check Discipline §Implementation standards) rewrote to `references/notebook-format.md`. §Key References likewise rewrote `superRA:script-to-notebook` → `references/notebook-format.md`.

- [x] **Step 4: Update the manifest** (`using-superRA` §Skill-Load Manifest). The `implementation` row's Required-skills cell previously read "`handoff-doc`; active domain skill (for data analysis: `econ-data-analysis` + `script-to-notebook`)". Rewrote to "`handoff-doc`; active domain skill (for data analysis: `econ-data-analysis`)" and appended "for data analysis also `econ-data-analysis/references/notebook-format.md`" to the Stage-scoped references cell so the load is explicit on the manifest (the single source of truth).

- [x] **Step 5: Sweep all references.** Grep across `skills/`, `agents/`, `commands/`, `README.md`, `CLAUDE.md`, `CATEGORIES.md` shows zero `script-to-notebook` matches in active content after the sweep. Active updates made:
  - `README.md` Workflow Map Mermaid node IMPL: `script-to-notebook` → `econ-data-analysis/references/notebook-format.md`.
  - `README.md` Domain — Data Analysis table: `econ-data-analysis` row's stage-scoped-references enumeration extended with `notebook-format.md` (and its jupytext/julia-quarto companion guides).
  - `skills/CATEGORIES.md` Domain table: `econ-data-analysis` row's Stage-scoped references enumeration extended with `notebook-format.md` (and companion guides).
  - `agents/reviewer.md` §Verify Claims Independently active-check line: `per script-to-notebook` → `per econ-data-analysis/references/notebook-format.md`.
  - `skills/refactor-and-integrate/SKILL.md` §Auto-loaded alongside: dropped the `superRA:script-to-notebook` bullet; merged the note into the `superRA:econ-data-analysis` bullet (the `implementation` manifest row now carries notebook-format.md as a stage reference).
  - `skills/planning-workflow/SKILL.md` Phase 3 File Structure: `per superRA:script-to-notebook` → `per econ-data-analysis/references/notebook-format.md`.
  - `skills/execution-workflow/SKILL.md` Step 1.2: `superRA:econ-data-analysis + superRA:script-to-notebook` → `superRA:econ-data-analysis (plus references/notebook-format.md when analysis scripts are being written or reviewed)`.
  
  Intentionally not touched: `PLAN.md` / `RESULTS.md` / `RELEASE-NOTES.md` retain their `script-to-notebook` strings as historical record of this refactor and of prior upstream releases.

- [x] **Step 6: Update inventory tables.** Removed the `script-to-notebook` row from `using-superRA/SKILL.md` §Skill Inventory, `skills/CATEGORIES.md` Utility table, and `README.md` Utility table. All three tables now enumerate the same post-refactor utility set (handoff-doc, refactor-and-integrate, report-in-markdown, semantic-merge, using-analysis-worktrees, worktree-data-sync).

- [x] **Step 7: Validate.** Post-sweep grep confirms zero `script-to-notebook` mentions in active content (only PLAN.md, RESULTS.md, and RELEASE-NOTES.md retain the strings by design). Re-read `econ-data-analysis/SKILL.md` end-to-end — the Stage-Scoped References table is internally consistent (five rows matching the five reference files in the directory), Describe §Visualization / Documentation §Script categories / Documentation §Figures / §Review & Self-Check Discipline §Implementation standards / §Key References all point at the new path, and the §Documentation cross-cutting section still reads coherently pending Task 3's further restructuring. Atomic commit staged: `task 4: move script-to-notebook into econ-data-analysis as a reference`.

---

### Task 5: Cache project conventions in PLAN.md header
**Review status:** *(not started)*

**Files affected:** `skills/handoff-doc/references/plan-anatomy.md`, `skills/planning-workflow/SKILL.md`, `skills/planning-workflow/references/plan-template.md`, `skills/execution-workflow/SKILL.md`, `agents/implementer.md`, `agents/reviewer.md`
**Input:** Current "Before You Start" walk-up step in `agents/implementer.md` step 6 and `agents/reviewer.md` step 6; `execution-workflow` Step 1.3.
**Output:** Project conventions discovered by orchestrator walk-up land in a `## Project Conventions` section of `PLAN.md` (read-only for subagents). Subagents read this section first; on-demand re-walk is allowed but not required.

- [ ] **Step 1: Add `## Project Conventions` to plan anatomy.** In `plan-anatomy.md` §Header, insert a new top-level section between `Conventions:` and `Output:` (or extend the existing `Conventions:` field). Spec: "Populated by the orchestrator at planning-workflow Phase 3 and at execution-workflow Step 1.3. Lists each module-level `CLAUDE.md` / `AGENTS.md` / `README.md` walked, with a one-paragraph summary of the conventions extracted. Subagents read this section instead of re-walking; if a section is missing, they may walk on-demand and report the omission."

- [ ] **Step 2: Update `planning-workflow` SKILL.md Phase 3** ("File Structure"). Add a sub-step: "Walk the directories the plan will touch. Populate `## Project Conventions` in PLAN.md with the extracted conventions before drafting tasks."

- [ ] **Step 3: Update `planning-workflow/references/plan-template.md`** with the new section, including a worked example for a module with a CLAUDE.md.

- [ ] **Step 4: Update `execution-workflow` Step 1.3** to read: "If `## Project Conventions` is empty or stale, walk and populate it now. If populated, skim and proceed."

- [ ] **Step 5: Update `agents/implementer.md` step 6 and `agents/reviewer.md` step 6.** Replace the mandatory walk-up with: "Read the `## Project Conventions` section of PLAN.md. The orchestrator already walked. If you need conventions not covered there (a directory the orchestrator missed, or a `README.md` in a data dir the orchestrator didn't open), walk on-demand and flag the omission in your status return so the orchestrator can update PLAN.md."

- [ ] **Step 6: Validate.** Re-read both agent files end-to-end. Re-read `plan-anatomy.md` and `plan-template.md`. Atomic commit.

---

### Task 6: Centralize agent-shared discipline in `using-superRA` (absorb handoff-doc essentials)
**Review status:** APPROVED

**Files affected:** `skills/using-superRA/SKILL.md`, `skills/using-superRA/references/main-agent-autonomy.md` (new), `skills/using-superRA/references/session-bootstrap.md`, `skills/handoff-doc/SKILL.md` (trimmed from 118 lines to 30), `agents/implementer.md`, `agents/reviewer.md`, `skills/execution-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/merge-workflow/SKILL.md`, `skills/semantic-merge/SKILL.md`, `skills/agent-orchestration/SKILL.md`, `skills/refactor-and-integrate/references/drift-test-quality.md`, `skills/refactor-and-integrate/references/merge-quality.md`, `skills/CATEGORIES.md`, `README.md`
**Input:** Today, agents load BOTH `using-superRA` (for principles) AND `handoff-doc` (for doc discipline). Workflow skills restate the four principles inline. Autonomy / stop-points / banned-phrasings live only in `execution-workflow`. Result: implementer/reviewer dispatch loads ~120 lines of `handoff-doc` they could read once at the design-contract level.
**Output:** Implementer/reviewer load only `using-superRA` for cross-cutting design + handoff-doc agent essentials. `handoff-doc` becomes a doc-*creation* skill (loaded by `planning-workflow` and the Stage 2 doc-writer only). Workflow skills carry no principle restatements. Autonomy lives in a main-agent-only reference.

**Architectural principle (per researcher):** `using-superRA` is the design home — every agent reads it. Anything an implementer or reviewer needs to know that crosses skill boundaries (the four principles, the handoff-doc editing rules, the User Decisions Log format, the autonomy contract) lives in `using-superRA` directly or in its `references/`. Specialized skills become loaders for callers that need the *full* discipline (creating docs from scratch, orchestrating). Subagent dependencies shrink.

- [x] **Step 1: Add §Handoff Doc Discipline to `using-superRA/SKILL.md`** (~55 lines in final form, new section after §Universal Principles). Absorbed from `handoff-doc/SKILL.md` the agent-runtime essentials: the four document principles (latest-state-only, live-and-committed, task-block-structure, doc-is-the-record) with operational rules; the inline-edit rule; the stale-content 5-bullet checklist; the §User Decisions Log format with the 3-line blockquote template and the "log before you act" rule plus the `ask-user-question-logger` hook reminder; figure-embedding pointer to `results_attachments/` and `report-in-markdown/references/rich-content.md`; the `## Project Conventions` section pointer (introduced by Task 5); and a `§When You Need the Full Anatomy` subsection pointing at `handoff-doc/references/plan-anatomy.md` and `results-anatomy.md` for doc-creators.

- [x] **Step 2: Trim `handoff-doc/SKILL.md`** to a doc-creation skill. Final size: 30 lines (below the ~50 target). Rewrote the top-line rerouting note to point at `using-superRA` §Handoff Doc Discipline as the canonical home for the editing rules and frame this skill as invoked by `planning-workflow` Phase 2 and the Stage 2 doc-writer only. Kept the two-stage RESULTS.md lifecycle paragraph, the §References listing (`plan-anatomy.md` + `results-anatomy.md`), and the §How This Skill Is Used section describing the three call sites (standalone, planning-workflow, doc-writer). The frontmatter description was rewritten to reflect the doc-creation scoping and to point readers at `using-superRA` §Handoff Doc Discipline for everyday editing.

- [x] **Step 3: Create `using-superRA/references/main-agent-autonomy.md`.** New file; generalized from `execution-workflow` §Autonomy and Stop Points so it applies to every workflow phase (planning, execution, integration, merge, semantic-merge). Top-of-file blockquote states: "Loaded by the main agent at session start. Subagents inherit autonomy from their dispatch boundary; they do not load this file." Carries three top-level sections: §The Three Pause Classes (hard blocker, decision-beyond-authority, user-defined milestone — each with concrete examples), §Proceed Without Asking (load-bearing patterns like "task just moved to APPROVED → immediately dispatch the next not-started task"), and §Banned Phrasings (the "Should I proceed?" / "Want me to continue?" / "Ready for the next task?" list). Closes with §One Question at a Time and §Log Before You Act pointing at §Handoff Doc Discipline §User Decisions Log.

- [x] **Step 4: Hook the new reference into session-start.** `session-bootstrap.md` gained a new final section `## After Bootstrap: Load the Autonomy Contract` instructing the main agent to load `main-agent-autonomy.md` after the cross-session detection checks. Emphasizes that subagents do NOT load this reference — they inherit autonomy from their dispatch boundary.

- [x] **Step 5: Update agent files (drop handoff-doc dependency for typical work).**
  - `agents/implementer.md` step 1: rewrote to "Handoff-doc editing rules. You already loaded `superRA:using-superRA` per your frontmatter — its §Handoff Doc Discipline carries everything you need to edit `PLAN.md` / `RESULTS.md` ... Load `superRA:handoff-doc` **only** if your task is creating a new `PLAN.md` / `RESULTS.md` from scratch or maturing Stage 1 RESULTS.md into Stage 2 — both rare for implementer work." The implementer-specific role ownership and review-loop annotation protocol pointer is preserved.
  - `agents/reviewer.md` step 1: parallel rewrite — same structure, scoped to reviewer work ("creating a new `PLAN.md` / `RESULTS.md` from scratch or reviewing a Stage 2 RESULTS.md maturation — both rare for reviewer work"). The reviewer-specific role ownership and review-loop protocol pointer is preserved.
  - `agents/implementer.md` §Handoff — Unified Across Stages: the pointer at `superRA:handoff-doc` updated to `superRA:using-superRA` §Handoff Doc Discipline (the discipline is there now, not in handoff-doc).

- [x] **Step 6: Update the manifest.** Dropped `handoff-doc` from the `implementation`, `refactoring`, `drift-test`, `integration-review`, and `merge` rows' "Required skills" cells. Kept it on `documentation` and `planning-review` rows (doc-creators need the full anatomy templates). Added a bold column-header note above the table: "The 'Required skills' column lists what loads *in addition to* `superRA:using-superRA` — the master skill every agent already loads at dispatch time ... That content is always available without needing to list it below." Added a closing paragraph below the table confirming the new rule: "`handoff-doc` remains a required load only on the `documentation` and `planning-review` rows — those stages create or mature docs from scratch and need the full anatomy templates (`plan-anatomy.md`, `results-anatomy.md`). Everyday implementer / reviewer stages get handoff-doc editing rules from `using-superRA` §Handoff Doc Discipline and do not need to load `handoff-doc` separately."

- [x] **Step 7: Strip principle and User-Decisions restatements from workflow skills.**
  - `execution-workflow` §Autonomy and Stop Points body replaced with a short pointer at `main-agent-autonomy.md` plus a 3-bullet list of execution-workflow-specific stop points (Step 4 completion menu / hard blockers from domain signals / methodology-authority boundary decisions) plugged into the autonomy contract's three pause classes. The §Proceed-without-asking and §Banned-phrasings bodies are now exclusively in `main-agent-autonomy.md`.
  - `semantic-merge §When to Ask the User`: `per CLAUDE.md workflow principle #4` rewrote to `per superRA:using-superRA §Universal Principles (principle #4)` — CLAUDE.md is contributor-only and not visible at runtime.
  - `integration-workflow §Autonomy` line 16: pointer at CLAUDE.md workflow principle #4 rewrote to `superRA:using-superRA` §Universal Principles (principle #4) + `references/main-agent-autonomy.md` for the full contract.
  - All 11 instances of `per handoff-doc §User Decisions Log` across `execution-workflow`, `integration-workflow`, `merge-workflow`, `semantic-merge`, `agent-orchestration`, `refactor-and-integrate/references/drift-test-quality.md`, and `refactor-and-integrate/references/merge-quality.md` swept to `per using-superRA §Handoff Doc Discipline §User Decisions Log`. (Task 7 will further collapse duplicate prose around these pointers; this task just updates the pointer target.)

- [x] **Step 8: Validate.** Re-read `using-superRA/SKILL.md` end-to-end — now reads as the central design contract every agent shares: Universal Principles → Handoff Doc Discipline (five subsections: The Four Document Principles, Inline-Edit Rule, What Counts as Stale, User Decisions Log, Project Conventions, Figure Embedding, When You Need the Full Anatomy) → Skill Inventory → Composable Design → Skill-Load Manifest → Execution Modes → When to Invoke Which Skill → Semantic Merge → Agent Teams → Reviewer–Orchestrator Dynamic → User Instructions → Instruction Priority. Re-read `handoff-doc/SKILL.md` — reads as a doc-creation skill: lede says "This skill is for doc *creation*"; §Two-Stage RESULTS.md Lifecycle + §References (plan-anatomy.md, results-anatomy.md) + §How This Skill Is Used (standalone, planning-workflow, doc-writer). Re-read `agents/implementer.md` and `agents/reviewer.md` step 1 — neither requires loading handoff-doc for typical work; both point at using-superRA §Handoff Doc Discipline. Grep `handoff-doc. §User Decisions Log` across skills/ returns zero matches. Grep `CLAUDE.md workflow principle #4` returns zero matches. The manifest's `implementation` / `refactoring` / `drift-test` / `integration-review` / `merge` rows no longer list `handoff-doc`; only `documentation` and `planning-review` do. Atomic commit staged: `task 6: centralize agent-shared discipline in using-superRA`.

---

### Task 7: Stop restating User Decisions Log discipline
**Review status:** *(not started)*

**Files affected:** every workflow skill + `agent-orchestration` + `semantic-merge` + `agents/{implementer,reviewer}.md`
**Input:** Current restatements scattered across `execution-workflow`, `integration-workflow`, `merge-workflow`, `semantic-merge`, `agent-orchestration` (each repeats some variant of "log per `handoff-doc` §User Decisions Log; the `ask-user-question-logger` hook will remind you"). After Task 6, the canonical home is `using-superRA` §Handoff Doc Discipline §User Decisions Log.
**Output:** Workflow skills carry only a one-line pointer. The hook-reminder text appears once.

- [ ] **Step 1: Audit.**
  ```bash
  grep -rn "User Decisions Log\|ask-user-question-logger" skills/ agents/
  ```
  Catalog every restatement.

- [ ] **Step 2: Move the hook-reminder text into `using-superRA` §Handoff Doc Discipline §User Decisions Log** (the section created in Task 6). One sentence: "The `ask-user-question-logger` PostToolUse hook reminds you to log after each `AskUserQuestion` call; if your harness doesn't expose the hook, set a TodoWrite reminder."

- [ ] **Step 3: Replace each restatement** in workflow skills with: "Log per `using-superRA` §Handoff Doc Discipline §User Decisions Log."

- [ ] **Step 4: Validate.** Re-grep. Only `using-superRA` should carry the discipline; everywhere else is a one-line pointer. Atomic commit.

---

### Task 8: Step 0b — explicit handoff to `planning-workflow` (no inline degradation)
**Review status:** APPROVED

**Files affected:** `skills/execution-workflow/SKILL.md`, `skills/planning-workflow/SKILL.md`
**Input:** `execution-workflow` Step 0b (lines 122–141) — currently inlines "load planning-workflow + handoff-doc, create or finish-editing PLAN.md/RESULTS.md, satisfy domain-specific planning gate."
**Output:** When PLAN.md/RESULTS.md are missing or dirty, execution-workflow halts and explicitly invokes `planning-workflow` (which then runs its full Phase 1 / Phase 2 / Self-Review). No inline planning-workflow degradation.

- [x] **Step 1: Rewrite Step 0b.** Replaced the old "Before any task dispatch: load planning-workflow and handoff-doc, create or finish-editing PLAN.md…" paragraph with the halt-and-invoke instruction: "If the check fails, halt execution-workflow and invoke `superRA:planning-workflow` to bootstrap the docs. Do not inline planning-workflow content here — the docs are created through planning-workflow's full Phase 1 / Phase 2 / Self-Review (with any applicable domain-specific planning gate satisfied there, not here). Resume execution-workflow at Step 1 after planning-workflow completes; its own self-review and execution-handoff will return control here." Also updated the adjacent Step 0 cross-reference from "Task 0 cannot silently land on main / master" to "planning-workflow's bootstrap commits cannot silently land on main / master," so the surrounding paragraph stays consistent with the no-inline-degradation framing (no stray "Task 0" references left).

- [x] **Step 2: Update `planning-workflow` overview** with the invoked-from-execution note: "May be invoked from `execution-workflow` Step 0b when an existing branch lacks committed `PLAN.md` / `RESULTS.md` (or carries uncommitted edits to them). The bootstrap path is identical to a fresh start — run the full Phase 1 / Phase 2 / Self-Review, satisfy any domain-specific planning gate, commit the docs, and hand control back. No shortcut." Placed as a second paragraph after the existing overview opening so it reads as context for readers who arrived through the execution-workflow halt.

- [x] **Step 3: Validate.** Re-read `execution-workflow` Step 0b end-to-end: the check paragraph remains; the failure paragraph is now an explicit invocation of `planning-workflow`, no Task-0 framing, no inline "satisfy the domain-specific planning gate" wording. Re-read `planning-workflow` Overview: the new paragraph sits between the "Owns procedural shape" sentence and the "domain-agnostic" paragraph, reads as a legitimate entry point. `grep "Task 0\b" skills/execution-workflow/SKILL.md` returns zero matches. Atomic commit staged: `task 8: explicit planning-workflow handoff from execution Step 0b`.

---

### Task 9: Move project doc audit into integration Stage 2 (refactor + integration-review)
**Review status:** *(not started)*

**Files affected:** `skills/integration-workflow/SKILL.md`, `skills/refactor-and-integrate/references/codebase-integration.md`, `skills/refactor-and-integrate/SKILL.md`, `skills/handoff-doc/references/results-anatomy.md` (the §Transition to Stage 2 paragraph)
**Input:** `integration-workflow` Step 3 sub-part B (lines 300–311) — currently bundled into the doc-writer dispatch.
**Output:** Project doc audit (walk-up CLAUDE.md / AGENTS.md / README.md, update stale claims, create missing pairs) becomes a checklist item for the Stage 2 refactorer and a verification item for the Stage 2 integration reviewer. Step 3 doc-writer is RESULTS.md-only.

- [ ] **Step 1: Move the audit checklist** (the bullet list at `integration-workflow:304–311` describing what to update, what to leave alone, the CLAUDE.md+AGENTS.md symlink rule) into `refactor-and-integrate/references/codebase-integration.md` as a new "Project Doc Audit" section. This becomes part of the refactorer's discipline.

- [ ] **Step 2: Update `integration-workflow` Stage 2 dispatches.** Both refactorer dispatch (Stage 2 step 4a) and integration-reviewer dispatch (Stage 2 step 2) get a sub-bullet: "this stage also covers project doc audit per `codebase-integration.md` §Project Doc Audit." (The dispatch template doesn't expand the checklist — the agent loads `codebase-integration.md` per the manifest.)

- [ ] **Step 3: Update `integration-workflow` Step 3.** Remove sub-part B entirely. Step 3 becomes:
  - Sub-part A (RESULTS.md maturation by doc-writer; subdivided per Task 10).
  - Sub-part C (PLAN.md disposition by orchestrator) — unchanged.
  
  Update the doc-writer dispatch (Step 3 sub-part A) to drop "Audit project docs reachable from the diff…" from its sub-parts list.

- [ ] **Step 4: Update `integration-workflow` Step 3 process diagram and red flags.** Remove every reference to "sub-part B," "project doc audit," and the "doc-writer subagent does the doc audit" framing.

- [ ] **Step 5: Update `results-anatomy.md` §Transition to Stage 2** to remove the "The same doc-writer pass also audits project-level docs" sentence.

- [ ] **Step 6: Validate.** Grep for "sub-part B" and "project doc audit" — should appear only in `codebase-integration.md`. Re-read integration-workflow end-to-end: the workflow should now have Stage 2 (which absorbed B) and Step 3 (now smaller — just RESULTS.md + PLAN.md disposition). Atomic commit.

---

### Task 10: Subdivide RESULTS.md maturation into ordered, recoverable commits
**Review status:** *(not started)*

**Files affected:** `skills/integration-workflow/SKILL.md` (Step 3 sub-part A), `skills/report-in-markdown/references/final-form.md`
**Input:** `integration-workflow:282–298` — sub-part A currently bundles fact-check + restructure + figure materialization + relocation into one commit.
**Output:** Sub-part A is four ordered commits: (1) fact-check in place, (2) restructure in place, (3) materialize figures, (4) `git mv` to `RESULTS_DIR` + attachments. Each commit is independently recoverable.

- [ ] **Step 1: Update `final-form.md`** with the four-step ordering. Each step gets its own validation criterion (e.g., step 1: every cited number matches its source; step 2: no task numbering remains; step 3: every figure rendered as PNG and embedded with relative path; step 4: file relocated, attachments folder relocated, history preserved).

- [ ] **Step 2: Update `integration-workflow` Step 3 sub-part A** to dispatch the doc-writer with the four-step sequence and explicit "commit each separately" instruction. Suggested commit messages: `"results: fact-check Stage 2 RESULTS.md"`, `"results: restructure Stage 2 RESULTS.md to reader-facing"`, `"results: materialize figures into ${RESULTS_DIR}/attachments"`, `"results: relocate RESULTS.md to ${RESULTS_DIR}"`.

- [ ] **Step 3: Update the doc-writer's report format.** Status return should list which of the four sub-commits landed (so a session interruption mid-A is recoverable: the next dispatch starts at the first un-landed step).

- [ ] **Step 4: Validate.** Re-read sub-part A and `final-form.md`. Confirm a session-crash mid-A produces a partially-relocated tree that is still git-coherent. Atomic commit.

---

### Task 11: Skip post-merge integration review on Tier 1 clean merges
**Review status:** *(not started)*

**Files affected:** `skills/merge-workflow/SKILL.md`, `skills/semantic-merge/SKILL.md`
**Input:** `merge-workflow` Step 2 (post-merge verification) currently runs both drift tests AND a fresh integration reviewer unconditionally.
**Output:** When `semantic-merge` Step 1 returned Tier 1 (clean merge, no conflicts, drift tests passed inside semantic-merge), `merge-workflow` Step 2b is skipped. The skip is documented in the merge commit.

- [ ] **Step 1: Update `semantic-merge`'s return contract.** When invoked from `merge-workflow`, semantic-merge returns its tier classification + a one-line "did main introduce non-trivial code changes?" verdict. Add this to `semantic-merge` §Invocation Pattern (delegated mode) and §What to Report.

- [ ] **Step 2: Update `merge-workflow` Step 2.** Add a sub-step 2.0: "Read semantic-merge's tier classification. If Tier 1 (clean, no conflicts) AND the incoming diff did not touch any file in your analysis paths: skip Step 2b. Run Step 2a (drift tests on merged state) only."

- [ ] **Step 3: Document the skip.** When 2b is skipped, the merge commit message gets a trailer: `"Post-merge integration review skipped: Tier 1 clean merge, no analysis-path changes incoming."` This makes the saving auditable.

- [ ] **Step 4: Update `merge-workflow` §Why Both Drift Tests AND Integration Review Post-Merge.** Replace "always run both" with the conditional rule. Preserve the rationale for the non-Tier-1 case.

- [ ] **Step 5: Validate.** Re-read `merge-workflow` Step 2 end-to-end. The skip path should be obvious; the not-skip path should be unchanged. Atomic commit.

---

### Task 12: Clarify `semantic-merge` standalone vs delegated (mode-aware verification)
**Review status:** *(not started)*

**Files affected:** `skills/semantic-merge/SKILL.md`
**Input:** `semantic-merge` §Invocation Pattern (lines 24–31) currently says "process is identical, only the caller differs." Today this means semantic-merge does its own drift-test re-run inside Tier 1/2/3 even when `merge-workflow` will then re-run them in Step 2a.
**Output:** Two explicit modes documented. Standalone owns all post-merge verification (drift tests, pipeline, stale-reference check). Delegated trims duplicates: it does what tier classification requires (e.g., Tier 2/3 propose+review), and leaves drift-test re-run + integration review to the caller.

- [ ] **Step 1: Rewrite §Invocation Pattern** to spell out the difference. Add a "Mode-aware verification" subsection enumerating which post-merge checks each mode runs. (Standalone: tier classification, conflict resolution, drift tests, pipeline, stale-reference check, report. Delegated: tier classification, conflict resolution, return tier + caller-relevant context. The caller — `merge-workflow` — runs drift tests + integration review on the merged state in its Step 2.)

- [ ] **Step 2: Add a parameter to the invocation contract.** When the caller is `merge-workflow`, the Skill invocation is `superRA:semantic-merge` with task: `"merge <base> into <analysis> — delegated mode: skip post-merge drift tests and pipeline run; the caller will verify"`. Document this in `merge-workflow` Step 1 alongside the existing invocation example.

- [ ] **Step 3: Update Tier 1 / Tier 2 / Tier 3 sections** to gate the post-merge drift-test step ("If standalone: run drift tests. If delegated: skip — caller will run."). Same for pipeline and stale-reference checks.

- [ ] **Step 4: Validate.** Re-read `semantic-merge` end-to-end in both modes. Re-read `merge-workflow` Step 1. The two skills should now be redundancy-free across the boundary. Atomic commit.

---

### Task 13: Distribute `verification-before-completion` content + delete the skill
**Review status:** APPROVED

**Files affected:** `skills/verification-before-completion/` (delete), `agents/implementer.md`, `agents/reviewer.md`, `skills/refactor-and-integrate/references/drift-test-quality.md`, `skills/execution-workflow/SKILL.md`, `skills/using-superRA/SKILL.md` (inventory + types), `skills/CATEGORIES.md`, `README.md`, `skills/writing-skills/SKILL.md` (one mention)
**Input:** `verification-before-completion/SKILL.md` (143 lines). Per the content audit: ~30 lines of unique content; ~110 lines of duplication with `econ-data-analysis` Red Flags + Common Rationalizations, `agents/reviewer.md` "DO NOT take the implementer's word", and `execution-workflow` Step 3 §Completion verification.
**Output:** Unique content distributed to four call sites (implementer self-check, reviewer claim-verification, drift-test creation, execution-workflow Step 3). Skill deleted. ~110 duplicated lines disappear; ~30 lines land where they're actually used.

- [x] **Step 1: Move the 5-step Gate Function** (IDENTIFY → RUN → READ → VERIFY → claim) into `agents/implementer.md` §Self-Review Before Reporting. Added as a new "Evidence before claims" opening subsection with the 5-step gate and the bottom-line one-liner "Run the command, read the output, then claim the result." Preserved the existing Completeness / Reproducibility / Domain §Review blocks beneath it.

- [x] **Step 2: Move the red-flag *wording* list** ("should", "probably", "seems to", "Great!", "Done!", "Perfect!") into both `agents/implementer.md` §Pre-Commit Self-Check and `agents/reviewer.md` §Pre-Commit Self-Check. Appended as a bold 3-line block at the end of each checklist, scoped to the commit claim / the review verdict respectively.

- [x] **Step 3: Move the Red-Green TDD pattern for regression / drift tests** into `skills/refactor-and-integrate/references/drift-test-quality.md` as a new `## Red-Green Verification` section between Robustness and Test Format. Carries the Write → Green → Revert → Red → Restore → Green cycle plus the rationale ("a drift test that passes once is not verified — it might always pass").

- [x] **Step 4: Sharpen `agents/reviewer.md` §Verify Claims Independently.** Prepended "DO NOT take the implementer's word" paragraph with the new diff-vs-status framing: "Check the git diff, not just the status return — agents can report 'success' for partial work, missing edits, or claims that do not match the committed state."

- [x] **Step 5: Add one sentence to `execution-workflow` Step 3 preamble.** Inserted bold line after the existing skeleton paragraph: "Run every check. Don't trust 'looks committed' — execute `git status` and read the output. The five checks below are the orchestrator's verification gate: evidence before claims, no shortcuts."

- [x] **Step 6: Delete the skill.** `git rm -r skills/verification-before-completion/` — removed `SKILL.md` (only file in the folder).

- [x] **Step 7: Sweep references.** `grep -rn "verification-before-completion" skills/ agents/ README.md CLAUDE.md` returned zero matches after the sweep. Cleanup performed: row removed from `using-superRA/SKILL.md` §Skill Inventory; row removed from `CATEGORIES.md` Utility table; row removed from `README.md` Utility table; `writing-skills/SKILL.md:401` example list trimmed from "TDD, verification-before-completion, designing-before-coding" to "TDD, designing-before-coding". Note: the §Skill Types "Rigid" example list the step anticipated does not currently exist in `using-superRA/SKILL.md` (removed in pre-plan commit `956f6cc`), so no row to strip there; `writing-skills` was the only remaining example list.

- [x] **Step 8: Validate.** Final sweep confirms zero matches across active content; surviving mentions are limited to `PLAN.md` / `RESULTS.md` (this refactor's own record) and `docs/plans/2025-11-28-skills-improvements-from-user-feedback.md` (archived prior plan). Re-read `agents/implementer.md` end-to-end: the §Self-Review block now opens with the gate function, making verification the first discipline the implementer sees, not a tail-end checklist. Re-read `agents/reviewer.md`: §Verify Claims Independently now leads with the diff-vs-status framing, and §Pre-Commit Self-Check carries the red-flag wording stop. Re-read `drift-test-quality.md`: Red-Green Verification sits between Robustness and Test Format — it reads as part of the test-writing discipline, not as an imported discipline. Re-read `execution-workflow` Step 3: the orchestrator's role as the verification gate is now explicit in the preamble. Atomic commit staged: `task 13: distribute verification-before-completion content + delete skill`.

---

### Task 14: Consolidate worktree skills (drop `using-analysis-worktrees`)
**Review status:** *(not started)*

**Files affected:** `skills/using-analysis-worktrees/SKILL.md` (delete), `skills/worktree-data-sync/SKILL.md` (broaden scope), `skills/planning-workflow/SKILL.md` (move "when to use" judgment), `skills/merge-workflow/SKILL.md` (point cleanup at consolidated skill), `skills/execution-workflow/SKILL.md` (Option 4 cleanup), `skills/using-superRA/SKILL.md` (inventory), `skills/CATEGORIES.md`, `README.md`, all references to `using-analysis-worktrees`
**Input:** `using-analysis-worktrees` is mostly judgment ("when to use") + git mechanics (every harness knows). The data-sync content is genuinely valuable; cleanup is duplicated in `merge-workflow` and `execution-workflow`.
**Output:** One worktree skill (`worktree-data-sync`, broadened) covering: (a) when to use a worktree (one-paragraph judgment), (b) data sync (existing content), (c) cleanup ritual. Skill inventory shrinks by one.

- [ ] **Step 1: Broaden `worktree-data-sync` scope.** Add two sections to its SKILL.md:
  - "When to use a worktree" — one paragraph, relocated from `using-analysis-worktrees` (kept tight: judgment, not how-to).
  - "Cleanup" — the canonical `git worktree remove` ritual + the case where the worktree was created by data-sync (cleanup also removes seeded data).
  
  Update the skill description to reflect the broader scope. Run `superRA:writing-skills` triggering checks since description changed.

- [ ] **Step 2: Delete `using-analysis-worktrees`.** `git rm -r skills/using-analysis-worktrees/`.

- [ ] **Step 3: Move "when to use" judgment from `planning-workflow`** (§Before you create directories) to point at `worktree-data-sync` §When to use. Keep the planning-workflow's one-sentence reminder.

- [ ] **Step 4: Replace cleanup duplications.** In `merge-workflow` Step 5 and `execution-workflow` Step 4 Option 4 (Discard), replace the inline `git worktree remove` block with: "Invoke `superRA:worktree-data-sync` §Cleanup."

- [ ] **Step 5: Sweep references.**
  ```bash
  grep -rn "using-analysis-worktrees\|superRA:using-analysis-worktrees" skills/ agents/ commands/ README.md CLAUDE.md
  ```
  Update every match to point at `worktree-data-sync` (often the surrounding context determines which sub-section).

- [ ] **Step 6: Update inventory tables.** Remove `using-analysis-worktrees` row from `using-superRA` §Skill Inventory, `CATEGORIES.md`, `README.md`.

- [ ] **Step 7: Validate.** Grep again. Re-read `worktree-data-sync` end-to-end — it should now be self-contained. Atomic commit.

---

### Task 15: Remove deprecated commands
**Review status:** APPROVED

**Files affected:** `commands/execute-plan.md`, `commands/write-plan.md`, `commands/brainstorm.md`, `using-superRA` (skill inventory references), `README.md`
**Input:** Three stub commands point at `superpowers:*` skills that are not part of this plugin. If the user doesn't have `obra/superpowers` installed, the commands silently fail.
**Output:** The three deprecated command stubs are removed. No silent failures.

- [x] **Step 1: Delete the stubs.**
  ```bash
  git rm commands/execute-plan.md commands/write-plan.md commands/brainstorm.md
  ```

- [x] **Step 2: Sweep references.** `grep -rn "execute-plan\|write-plan\|brainstorm" skills/ commands/ README.md CLAUDE.md` returned zero matches in any of those paths — no inventory-table rows to remove. Upstream-history mentions in `RELEASE-NOTES.md` and `CHANGELOG.md` are intentionally preserved (they are release history for the upstream superpowers project, not superRA inventory); superRA's own release entry for this refactor lands in Task 16 Step 4.

- [x] **Step 3: Validate.** Atomic commit.

---

### Task 16: Final consistency pass
**Review status:** *(not started)*

**Files affected:** `skills/CATEGORIES.md`, `README.md`, `CHANGELOG.md`, `RELEASE-NOTES.md`, every skill touched in Tasks 1–15
**Input:** Cumulative diff of Tasks 1–15.
**Output:** All inventory tables match the post-refactor skill set. CHANGELOG/RELEASE-NOTES have an entry. The "four principles" claim is consistent across files. End-to-end re-read confirms no drift.

- [ ] **Step 1: Sync inventory tables.** Update `skills/CATEGORIES.md` (Workflow / Domain / Utility / Meta tables), `README.md` skill tables, and `using-superRA` §Skill Inventory to reflect:
  - Removed: `script-to-notebook`, `using-analysis-worktrees`
  - Broadened: `worktree-data-sync`
  - Added rows for `references/main-agent-autonomy.md` and `references/review-checklist.md` if those tables enumerate references.

- [ ] **Step 2: Verify "four principles" consistency.**
  ```bash
  grep -rn "four \(load-bearing\|workflow\|discipline\) principles\|six \(discipline\) principles" skills/ agents/ CLAUDE.md README.md
  ```
  Confirm "four" everywhere (no stray "six"). The installed plugin description (visible at session start) may show "six" — that's a deployment-cache issue, not a repo issue, and resolves on next install.

- [ ] **Step 3: End-to-end re-read.** Walk every workflow skill (`planning-workflow`, `execution-workflow`, `integration-workflow`, `merge-workflow`, `semantic-merge`, `agent-orchestration`) plus `using-superRA`, `handoff-doc`, `econ-data-analysis`, `refactor-and-integrate`, `report-in-markdown`, `verification-before-completion`, `worktree-data-sync`, both agent files. Catch any orphan reference, broken pointer, contradictory line, or stale Stage name introduced by interactions between Tasks 1–15.

- [ ] **Step 4: Update CHANGELOG and RELEASE-NOTES** with a single entry summarizing the refactor: stage consolidation, two skills folded, project-doc-audit relocated, verification-before-completion connected, worktree skills consolidated. Cite this PLAN.md by branch/SHA so the design rationale is auditable.

- [ ] **Step 5: Run `superRA:writing-skills` triggering checks** for every skill whose description was modified across the refactor (at minimum: `worktree-data-sync` after Task 14, `econ-data-analysis` if its description was touched in Task 3, and `using-superRA` if Task 1 / Task 6 modified its description). Confirm each still triggers on its intended cues and doesn't trigger on cues meant for sibling skills.

- [ ] **Step 6: Validate.** Final grep sweep for the strings: `script-to-notebook`, `using-analysis-worktrees`, `execute-plan`, `write-plan`, `brainstorm`, `Stage: implementation review`, `Stage: drift test creation`, `Stage: integration review`, `Stage: merge proposer`, `sub-part B`, `recipe`. None should appear in skill bodies (only in PLAN.md / CHANGELOG history, which is fine). Atomic commit.

---

### Task 17: Document agent-reuse vs fresh-dispatch heuristic in agent-orchestration
**Review status:** APPROVED

**Files affected:** `skills/agent-orchestration/SKILL.md`, `skills/execution-workflow/SKILL.md` (one-line cross-reference).
**Input:** Current `agent-orchestration` Decision Framework section (the parallel-dispatch / Agent Teams / orchestrator-relay table) and its §Integration section. Current `execution-workflow` Per-Task Execution Steps + §Dispatch Templates pointer.
**Output:** `agent-orchestration` SKILL.md carries explicit orchestrator guidance on when to reuse a warm agent via `SendMessage` versus when to spawn a fresh dispatch. `execution-workflow` carries a one-line pointer at that guidance. The heuristic prevents reflexive fresh-dispatch of small follow-up tasks while preserving the adversarial-review property of the implementer–reviewer pair.

- [x] **Step 1: Draft the new subsection in `agent-orchestration` SKILL.md.** Placed as `## Agent reuse vs fresh dispatch` immediately after the Decision Framework section and before Dispatch Templates. Subsection covers:
  - **Context-reload cost framing** — fresh dispatch reloads `superRA:using-superRA`, the active domain skill, and the module-level `CLAUDE.md` / `AGENTS.md` / `README.md` walk-up for every directory touched.
  - **Criteria favoring reuse** — small scope, same domain context, non-overlapping file set with in-flight work, sequential build-on-previous-task pattern.
  - **Criteria favoring fresh dispatch** — large/new scope, different domain vertical, file-set overlap with in-flight work, perspective the warm agent cannot provide.
  - **Bundling as a third option** — multi-task brief in one implementer dispatch, task pointers in `Task:`, sequence + boundaries in `Additionally:`.
  - **Reviewer-always-fresh rule** — hard rule, named exception: review passes always spawn fresh; warm-agent review voids the implementer–reviewer pair.
  - **`SendMessage` mechanic** — one-sentence pointer: `to:` field takes agent id (or teammate name in a team); recipient resumes with full session context.

- [x] **Step 2: Add the `execution-workflow` cross-reference.** Appended a one-line pointer to `§Per-Task Execution Steps` step 1 at `skills/execution-workflow/SKILL.md:161`: "See `superRA:agent-orchestration` §Agent reuse vs fresh dispatch for when to reuse a warm implementer via `SendMessage` versus spawning a fresh dispatch." No content duplication.

- [x] **Step 3: Validate.** End-to-end re-read of `agent-orchestration/SKILL.md`: the new subsection sits naturally between Decision Framework (pattern selection: parallel / teams / relay) and Dispatch Templates (dispatch shape), covering the orthogonal axis of agent-identity selection. No overlap with the existing parallel/teams/relay table. End-to-end re-read of `execution-workflow/SKILL.md`: pointer lands cleanly on step 1 of the per-task loop without stepping on adjacent prose (step 2 NEEDS_CONTEXT/BLOCKED, step 3 reviewer dispatch both unaffected).

**Dependency note:** Task 17 may run at any time after Task 1 lands (Task 1 touches `agent-orchestration`-adjacent files but not `agent-orchestration/SKILL.md` itself; still, running Task 17 after Task 1 avoids any chance of interaction). Task 16's final consistency pass must include Task 17's touched files in its end-to-end re-read.

---

## Out of scope (deferred)

These items came up in the design review but were explicitly deferred:

- **D6 (failure-recovery sections in workflow skills)** — deferred. Will be revisited if real failure modes accumulate.
- **D7 (analysis-testing skill for non-drift tests)** — deferred. Open question whether to add a new skill or fold into `econ-data-analysis`.
- **README user-facing content (B6)** — left as-is; intentionally duplicates principles for the user-facing entry point.
- **The `six principles` discrepancy in the installed plugin (A4)** — repo is correct ("four"); will resolve on next plugin install/release.
