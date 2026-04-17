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

> **User decision (2026-04-16):** Drop Task 16 (final consistency pass) from the plan; proceed directly to INTEGRATE.
> **Question asked:** Why do we need Task 16? It duplicates what integration-workflow Stage 2 already covers.
> **Rationale:** Task 16's six steps (inventory sync, principle consistency, end-to-end re-read, CHANGELOG/RELEASE-NOTES update, triggering checks, grep sweep) all map onto integration-workflow Stage 2's refactor + integration review + project-doc-audit that Task 9 just relocated there. Executing Task 16 in the IMPLEMENT phase would perform the work twice.

> **User decision (2026-04-16):** Run integration-workflow only — do not proceed to merge-workflow afterward.
> **Question asked:** Merge locally vs open a PR (standard execution-workflow Step 4 4-option menu)?
> **Rationale:** Researcher chose a third path — run the integration-prep (drift tests skipped for plugin-dev, refactor + integration review, doc finalization) but stop before merge. Merge decision deferred.

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
**Review status:** APPROVED

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
**Review status:** APPROVED

**Files affected:** `skills/handoff-doc/references/plan-anatomy.md`, `skills/planning-workflow/SKILL.md`, `skills/planning-workflow/references/plan-template.md`, `skills/execution-workflow/SKILL.md`, `agents/implementer.md`, `agents/reviewer.md`
**Input:** Current "Before You Start" walk-up step in `agents/implementer.md` step 6 and `agents/reviewer.md` step 6; `execution-workflow` Step 1.3.
**Output:** Project conventions discovered by orchestrator walk-up land in a `## Project Conventions` section of `PLAN.md` (read-only for subagents). Subagents read this section first; on-demand re-walk is allowed but not required.

- [x] **Step 1: Add `## Project Conventions` to plan anatomy.** Added a new top-level `## Project Conventions` section in `plan-anatomy.md` placed between the `## Header` section and the `## Task Block Anatomy` section (it is a PLAN.md top-level section, not an inline header field — matching the `## Decisions` section pattern). Content: intro paragraph naming when it is populated (`planning-workflow` Phase 3 / refreshed at `execution-workflow` Step 1) and who edits it (orchestrator; subagents read-only); a markdown code block showing the section layout (Walk date stamp + "### Repo root" + "### Module-level docs walked" + "### Not walked" subheadings, each with file:path + SHA + one-paragraph summary examples); and a §Discipline sub-block listing the four rules (populated by orchestrator, one-paragraph-per-doc summaries not excerpts, stamp the walk date, list the not-walked paths too). Task 6's §Project Conventions pointer in `using-superRA` already cross-references this file; no edit needed there.

- [x] **Step 2: Update `planning-workflow` SKILL.md Phase 3.** Appended a new paragraph to Phase 3 after the existing "Follow existing project conventions for directory structure" bullet. Paragraph names the walk-up requirement ("walk up from every directory the plan will touch and `Read` every `CLAUDE.md` / `AGENTS.md` / `README.md` you encounter along the path; also read the repo-root `CLAUDE.md` and every `README.md` in a data directory the plan will load from") and the output target ("populate the `## Project Conventions` section of `PLAN.md` with one-paragraph summaries per doc, stamped with the walk date"). Points at `handoff-doc/references/plan-anatomy.md` §Project Conventions for the anatomy and makes the on-demand re-walk behavior explicit for subagents.

- [x] **Step 3: Update `planning-workflow/references/plan-template.md`.** Added a worked example of the `## Project Conventions` section between the header's closing `---` and the §Task Block Structure heading. The worked example carries three subsections (Repo root / Module-level docs walked / Not walked), each populated with 2-3 example entries matching the anatomy in `plan-anatomy.md`. Intro paragraph points at `plan-anatomy.md` §Project Conventions for the full anatomy and explains the read-instead-of-walk subagent behavior + on-demand re-walk flag-the-omission rule.

- [x] **Step 4: Update `execution-workflow` Step 1 walk-up step (item 3).** Rewrote from "Read the project's guidance docs" walk-up paragraph to "Read PLAN.md's `## Project Conventions` section" — the orchestrator reads the populated section first and skims if fresh; only walks and populates if the section is missing, empty, or stale. Preserves the critical framing that these conventions are load-bearing for adjudicating reviewer findings and editing upcoming tasks inline. Notes explicitly that subagents read the populated section instead of re-walking per dispatch and the orchestrator updates when a subagent flags an omission.

- [x] **Step 5: Update agent files step 5 (the walk-up step).** Both `agents/implementer.md` and `agents/reviewer.md` had their step-5 walk-up rewritten to "Read PLAN.md's `## Project Conventions` section" — both start from the populated section as the canonical source, only walk on-demand when something is missing, and flag the omission in status return. The "MAJOR integration-review finding if code ignores module-level conventions" framing in `reviewer.md` is preserved. (Corrected the step number in PLAN's Step 5 spec — the walk-up is step 5, not step 6; step 6 is the "Ask questions" step Task 1 renumbered to. Step 6 is untouched.)

- [x] **Step 6: Validate.** Re-read `agents/implementer.md` step 5: opens with "Read PLAN.md's `## Project Conventions` section"; the walk-on-demand fallback is explicit; the "do not dump docs into your status report" and "if a doc contradicts the dispatch prompt, raise the conflict before starting" framings from the prior version are preserved. Re-read `agents/reviewer.md` step 5: parallel structure; preserves the "MAJOR integration-review finding" framing and the pointer at `codebase-integration.md` §Project Doc Audit as the Stage-2 safety net. Re-read `plan-anatomy.md` §Project Conventions end-to-end: the code block shows the three subsections with worked examples; the Discipline sub-block lists the four rules. Re-read `plan-template.md` §Project Conventions: the template shows the same three subsections with example content; the explanatory paragraph above it names Phase 3 as the populate-step and points at `plan-anatomy.md` for the full anatomy. Re-read `execution-workflow` Step 1 (item 3): the "read first, walk only if stale" framing reads cleanly; the orchestrator-updates-when-subagent-flags loop closes the on-demand path. Atomic commit staged: `task 5: cache project conventions in PLAN.md header`.

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
**Review status:** APPROVED

**Files affected:** `skills/execution-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/semantic-merge/SKILL.md`, `skills/agent-orchestration/SKILL.md`, `skills/using-superRA/references/main-agent-autonomy.md`
**Input:** Current restatements scattered across `execution-workflow`, `integration-workflow`, `merge-workflow`, `semantic-merge`, `agent-orchestration` (each repeats some variant of "log per `handoff-doc` §User Decisions Log; the `ask-user-question-logger` hook will remind you"). After Task 6, the canonical home is `using-superRA` §Handoff Doc Discipline §User Decisions Log.
**Output:** Workflow skills carry only a one-line pointer. The hook-reminder text appears once.

- [x] **Step 1: Audit.** Task 6 had already swept all 11 pointer targets to `using-superRA` §Handoff Doc Discipline §User Decisions Log. Restatements of format + hook reminder still surrounded several of those pointers in the workflow skills — Task 7's work is collapsing that surrounding prose. Eight restatement sites identified: `execution-workflow:220` (Step 4 menu hook + format reminder), `execution-workflow:247` (Escalate bullet location reminder), `execution-workflow:273/277` (Step 4 completion-menu bullet + closing summary), `integration-workflow:121` (drift-test candidate location reminder + hook reminder), `integration-workflow:242` (RESULTS_DIR location reminder + hook reminder), `integration-workflow:330` (PLAN.md disposition location reminder), `semantic-merge:278` (full format restatement + hook reminder), `agent-orchestration:145` (hook reminder), and `using-superRA/references/main-agent-autonomy.md:51` (hook reminder — the file Task 6 created).

- [x] **Step 2: Move the hook-reminder text into `using-superRA` §Handoff Doc Discipline §User Decisions Log.** Task 6 already did this — the canonical sentence "The `ask-user-question-logger` PostToolUse hook reminds you to log after each `AskUserQuestion` call; if your harness doesn't expose the hook, set a TodoWrite reminder" lives at `using-superRA/SKILL.md:64` inside §User Decisions Log. No edit needed here.

- [x] **Step 3: Replace each restatement.** Collapsed each of the eight sites to a clean "Log per `using-superRA` §Handoff Doc Discipline §User Decisions Log" pointer, preserving only the site-specific context (which commit the log lands in, which PLAN.md section if useful for that workflow's pause class, what to do if the doc has been disposed of). Stripped the hook-reminder sentence everywhere except the canonical home. `execution-workflow:273` (Step 4 bullet) lost its trailing "stop and `AskUserQuestion`; log per …" tail — the closing summary line at 277 now covers logging for all three bullets uniformly so the individual bullets stay focused on *what the stop is about*. Semantic-merge:278 kept its branch-specific context ("If PLAN.md has already been disposed of, record the decision in the merge commit message instead") because that's a semantic-merge-only rule, not a restatement of the discipline.

- [x] **Step 4: Validate.** Re-grep for `ask-user-question-logger` across `skills/`: one match, at `using-superRA/SKILL.md:64` (the canonical sentence). Zero elsewhere. Re-grep for `User Decisions Log`: every workflow-skill hit is either a one-line pointer or a pointer with narrow site-specific context; no hit repeats the hook-reminder text, and no hit inlines the blockquote format template (that lives only at `using-superRA/SKILL.md:56-60`). Atomic commit staged: `task 7: collapse duplicate prose around User Decisions Log pointers`.

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
**Review status:** APPROVED

**Files affected:** `skills/integration-workflow/SKILL.md`, `skills/refactor-and-integrate/references/codebase-integration.md`, `skills/handoff-doc/references/results-anatomy.md`, `skills/report-in-markdown/SKILL.md` (load-map row), `skills/report-in-markdown/references/final-form.md` (project-docs section), `agents/implementer.md`, `agents/reviewer.md` (two cross-references each).
**Input:** `integration-workflow` Step 3 sub-part B — currently bundled into the doc-writer dispatch.
**Output:** Project doc audit (walk-up CLAUDE.md / AGENTS.md / README.md, update stale claims, create missing pairs) becomes a checklist item for the Stage 2 refactorer and a verification item for the Stage 2 integration reviewer. Step 3 doc-writer is RESULTS.md-only.

- [x] **Step 1: Move the audit checklist** into `refactor-and-integrate/references/codebase-integration.md` as a new "Project Doc Audit" section. The walk-up rules, what-to-update, what-to-leave-alone, and CLAUDE.md+AGENTS.md symlink rule are now a §Project Doc Audit section in that file. The closing sentence names the Stage 2 ownership split (refactorer applies; integration reviewer verifies) and carves RESULTS.md out to Step 3.

- [x] **Step 2: Update `integration-workflow` Stage 2 dispatches.** Both refactorer dispatch (Stage 2 step 4a) and integration-reviewer dispatch (Stage 2 step 2) carry the sub-bullet "this stage also covers the project doc audit per `codebase-integration.md` §Project Doc Audit (walk-up CLAUDE.md / AGENTS.md / README.md reachable from the diff)". The dispatch prompts do not expand the checklist — the loaded reference carries it.

- [x] **Step 3: Update `integration-workflow` Step 3.** Sub-part B is deleted. Step 3 now has sub-part A (RESULTS.md maturation) and sub-part C (PLAN.md disposition). Doc-writer dispatch `Task:` is now `Stage 2 RESULTS.md maturation` (no "+ project doc audit"); its `Additionally:` drops the audit sub-bullet. Doc-reviewer dispatch `Task:` is `review of matured Stage 2 RESULTS.md` (no "+ audited project docs"); its scope list drops the separate "Project docs" bullet, replaced with a tighter Cross-consistency bullet that points at Stage 2's responsibility for upstream stale-claim catches.

- [x] **Step 4: Update `integration-workflow` Step 3 process diagram and red flags.** Process diagram: node "B: audit CLAUDE.md / AGENTS.md / README.md" and its edges removed; A now flows directly into doc-reviewer dispatch. Description-frontmatter and Core principle + intro paragraphs rewritten to name Stage 2 as the project-doc audit owner. Red Flags "Never" / "Always" bullets rewritten to drop "sub-parts A and B" framing; Agent Loads paragraph rewritten the same way. Agent Teams Mode paragraph trimmed to "sub-part A — the RESULTS.md maturation".

- [x] **Step 5: Update `results-anatomy.md` §Transition to Stage 2** to move the project-doc audit sentence out of the doc-writer pass and into a separate sentence naming Stage 2 + `codebase-integration.md` §Project Doc Audit as the owner.

- [x] **Step 6: Validate + downstream sweep.** Grep `sub-part B` and `project doc audit` across the repo:
  - `sub-part B` — zero hits in skill bodies and agent files; only PLAN.md history (lines 60, 270, 277, 283, 287, 442 in this file) and RELEASE-NOTES remain, which is fine.
  - `project doc audit` / `Project Doc Audit` — appears in `codebase-integration.md` (the new section), in `integration-workflow/SKILL.md` (as pointers into Stage 2), in `results-anatomy.md` (the new Stage 2 pointer), in `final-form.md` (the new cross-consistency paragraph), and in `agents/{implementer,reviewer}.md` (the two walk-up pointers now point at Stage 2's §Project Doc Audit, not Step 3 sub-part B).
  
  Also caught during sweep: `report-in-markdown/SKILL.md` load-map row still read "maturing `RESULTS.md` + project doc audit" — trimmed to "maturing `RESULTS.md`". `final-form.md` §Project documentation accuracy was the doc-reviewer's project-doc checklist (now stale since Stage 2 owns that gate) — rewritten into a tighter §Cross-consistency with project docs that keeps the RESULTS.md-vs-project-docs consistency check and names Stage 2 as the primary project-doc gate. Atomic commit.

---

### Task 10: Subdivide RESULTS.md maturation into ordered, recoverable commits
**Review status:** APPROVED

**Files affected:** `skills/integration-workflow/SKILL.md` (Step 3 sub-part A), `skills/report-in-markdown/references/final-form.md`, `agents/implementer.md` (Report Format — multi-commit status return).
**Input:** `integration-workflow` Step 3 sub-part A — the pass currently bundles fact-check + restructure + figure materialization + relocation into one commit.
**Output:** Sub-part A is four ordered commits: (1) fact-check in place, (2) restructure in place, (3) materialize figures, (4) `git mv` to `RESULTS_DIR` + attachments. Each commit is independently recoverable.

- [x] **Step 1: Update `final-form.md`** with the four-step ordering. §The consolidation pass — what changes was renamed to §The consolidation pass — four ordered commits, with one subsection per commit. Each subsection names the commit message, scope, `git` commands, and a pre-commit validation gate ("every cited number matches its source", "no `## Task N` headings remain / frontmatter present", "every figure renders / every figure is PNG / `results_attachments/` still at root", "git log --follow shows history back to Stage 1 / every embed path resolves at the new location").

- [x] **Step 2: Update `integration-workflow` Step 3 sub-part A** to dispatch the doc-writer with the four-step sequence. Doc-writer dispatch `Additionally:` now says "matures RESULTS.md per `final-form.md` §The consolidation pass — four ordered commits. Land each of the four commits separately (in order: fact-check → restructure → materialize figures → relocate) so a session interruption is recoverable. In your status return, list which of the four sub-commits landed." Sub-part A body rewritten as a four-step commit sequence listing each commit message and scope; closing sentence names "Each commit has its own validation gate — see `final-form.md`" + "Do NOT bundle these into one commit." Added a Recovery-on-re-dispatch paragraph instructing the re-dispatch `Additionally:` line to name which commits still need landing; the doc-writer reads `git log --oneline` to resume.

- [x] **Step 3: Update the doc-writer's report format.** Added a "Multi-commit stages" paragraph to `agents/implementer.md` §Report Format carrying a new "Sub-commits landed" field. Example: `Sub-commits landed: 1 (fact-check), 2 (restructure). Did not reach 3 (materialize figures) or 4 (relocate) — blocked on PDF→PNG conversion.` Omit for single-commit dispatches. Keeps the agent file generic; the documentation Stage's four-commit expectation is named via example only.

- [x] **Step 4: Validate.** Re-read Sub-part A and `final-form.md` §The consolidation pass — four ordered commits end-to-end:
  - A session crash after Commit 1 leaves the tree with a fact-checked dev-log at the worktree root — re-dispatch resumes at Commit 2.
  - A crash after Commit 2 leaves the tree with a restructured file at worktree root pointing at `results_attachments/...` — re-dispatch resumes at Commit 3.
  - A crash after Commit 3 leaves the tree with the restructured file at worktree root pointing at `attachments/...` AND the materialized folder at `${RESULTS_ATTACHMENTS_DIR}` — re-dispatch just runs the `git mv` in Commit 4.
  - A crash after Commit 4 is complete state.
  
  Each state is git-coherent (tests still pass if they existed; git log reads cleanly; nothing is half-staged on disk without being committed). `final-form.md` and `integration-workflow` agree on the commit sequence and the commit messages. Atomic commit.

---

### Task 11: Skip post-merge integration review on Tier 1 clean merges
**Review status:** APPROVED

**Files affected:** `skills/merge-workflow/SKILL.md`, `skills/semantic-merge/SKILL.md`
**Input:** `merge-workflow` Step 2 (post-merge verification) currently runs both drift tests AND a fresh integration reviewer unconditionally.
**Output:** When `semantic-merge` Step 1 returned Tier 1 (clean merge, no conflicts, no analysis-path changes in the incoming diff), `merge-workflow` Step 2b is skipped. The skip is documented in the merge commit (Option 1) or PR body (Option 2).

- [x] **Step 1: Update `semantic-merge`'s return contract.** §What to Report split into Standalone mode (existing content) and Delegated mode (new). Delegated mode names the required fields: tier classification, incoming-impact line (paths touched, analysis-path yes/no), integration + user decisions (one-paragraph summaries), drift tests / pipeline / verification all stamped `deferred to caller`. Tier + incoming-impact marked load-bearing — `merge-workflow` Step 2 reads them for skip eligibility.

- [x] **Step 2: Update `merge-workflow` Step 2.** Added sub-step 2.0 (read tier + incoming-impact, decide skip) ahead of 2a. Reworded 2b to "Skip this sub-step only if 2.0 said so." Skip condition: Tier 1 AND no analysis-path changes. Otherwise (Tier 2, Tier 3, or Tier 1 with analysis-path changes) run 2a AND 2b. Added an "Analysis paths" definition and a "when in doubt, do not skip" nudge. Step 1's invocation example updated to delegated-mode form per Task 12.

- [x] **Step 3: Document the skip.** Added sub-step 2c: when 2b is skipped, merge commit message gets the trailer `"Post-merge integration review skipped: Tier 1 clean merge, no analysis-path changes incoming."` For Option 2 (PR), the same sentence goes under "Pre-Merge Quality" in the PR body — PR body template's Integration review line offers the skip-wording alternative. Step 4 Option 1 block got a trailer-append instruction.

- [x] **Step 4: Update `merge-workflow` §Why Both Drift Tests AND Integration Review Post-Merge.** Renamed to "§Why Both Drift Tests AND Integration Review Post-Merge — and when one is redundant". Two-signal rationale preserved verbatim for the default case. New second paragraph names the provable-redundancy condition and explains *why* drift tests alone cover both signals when Tier 1 AND no analysis-path changes (no surface for convention drift on your code). Closing paragraph reconnects to Step 3's refactor-review loop.

- [x] **Step 5: Validate.** Re-read `merge-workflow` Step 2 end-to-end: 2.0 → 2a (always) → either 2b or 2c depending on 2.0 → refactor-review loop if anything fails. Process diagram updated: new diamond "Step 2b skippable?" gating either 2b dispatch or 2c skip-documentation; both converge on existing pass/fail diamond. Red Flags rewritten: "Never push without running BOTH signals" becomes "Never push without running 2a" + "Never skip 2b outside the 2.0 condition"; "Always run both" becomes "Always run 2a; run 2b unless 2.0's skip condition is met; document the skip per 2c when skipped"; semantic-merge invocation is now "never invoke in default standalone mode" because delegated mode is load-bearing for the skip contract. Atomic commit.

---

### Task 12: Clarify `semantic-merge` standalone vs delegated (mode-aware verification)
**Review status:** APPROVED

**Files affected:** `skills/semantic-merge/SKILL.md`, `skills/merge-workflow/SKILL.md`
**Input:** `semantic-merge` §Invocation Pattern previously said "process is identical, only the caller differs." Post-merge verification (drift tests, pipeline, stale-reference check) ran inside every Tier in both modes, duplicating what `merge-workflow` Step 2 then re-ran.
**Output:** Two explicit modes with a mode-aware-verification table. Standalone owns all post-merge verification (drift tests, pipeline, stale-reference check). Delegated does tier classification + conflict resolution only; caller runs the rest.

- [x] **Step 1: Rewrite §Invocation Pattern** to spell out the mode split. New "Mode-aware verification" subsection is a 6-row table showing which post-merge checks each mode runs — Tier classification and conflict resolution in both; drift tests, pipeline run, stale-reference check standalone-only; return tier+impact delegated-only. The invocation pattern is now split so the two bullets carry mode-specific behavior, not a "process is identical" disclaimer.

- [x] **Step 2: Parameterize the invocation contract.** Delegated-mode invocation task string spelled out: `"merge <base> into <analysis> — delegated mode: skip post-merge drift tests and pipeline run; the caller will verify"`. Documented this in `merge-workflow` Step 1 alongside the existing invocation example — Step 1 now opens with "in delegated mode" and the code fence shows the full task string.

- [x] **Step 3: Update Tier 1 / Tier 2 / Tier 3 sections** to gate post-merge verification by mode. Each of the three tiers' post-merge steps (Tier 1 steps 2-5; Tier 2 step 5; Tier 3 steps 8-9) is annotated `[standalone-only]` and followed by an explicit "Delegated: skip — the caller runs …" sentence that names the caller's step (merge-workflow Step 2a for drift tests, Step 4 for pipeline). The Working Principles "drift tests are the safety net" bullet is reworded to carry both modes ("In standalone mode, always … In delegated mode, you do NOT … — `merge-workflow` Step 2a does"). Red Flags §Always is also split by mode. Agent Teams Mode closing sentence updated: drift-test verification is lead-handled in standalone, caller-handled in delegated.

- [x] **Step 4: Validate.** Re-read `semantic-merge` end-to-end in both modes:
  - Standalone Tier 1: merge → drift tests → pipeline → done. Standalone Tier 2: propose → review → drift tests → done. Standalone Tier 3: propose → present → merge → review → drift tests → pipeline → done. Behavior preserved.
  - Delegated Tier 1: merge → return tier+impact. Delegated Tier 2: propose → review → return tier+impact. Delegated Tier 3: propose → present → merge → review → return tier+impact. Drift tests / pipeline never re-run inside semantic-merge — the caller owns them.
  
  Re-read `merge-workflow` Step 1: invocation is delegated-mode, return contract documented, Step 2 reads tier+impact for skip eligibility. No redundancy across the boundary: Step 2a always runs (the caller's drift-test pass), Step 4 always runs (the caller's pipeline), semantic-merge never runs either in delegated mode. Atomic commit (coupled with Task 11 since they share files).

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
**Review status:** APPROVED

**Files affected:** `skills/using-analysis-worktrees/SKILL.md` (deleted), `skills/worktree-data-sync/SKILL.md` (broadened), `skills/planning-workflow/SKILL.md`, `skills/merge-workflow/SKILL.md`, `skills/execution-workflow/SKILL.md`, `skills/agent-orchestration/references/agent-teams.md`, `skills/using-superRA/SKILL.md`, `skills/CATEGORIES.md`, `README.md`
**Input:** `using-analysis-worktrees` was mostly judgment ("when to use") + git mechanics (every harness knows). The data-sync content was genuinely valuable; cleanup was duplicated in `merge-workflow` and `execution-workflow`.
**Output:** One worktree skill (`worktree-data-sync`, broadened) covering: (a) when to use a worktree (one-paragraph judgment), (b) data sync (existing content), (c) cleanup ritual. Skill inventory shrinks by one.

- [x] **Step 1: Broaden `worktree-data-sync` scope.** Added two new top-level sections: `## When to Use a Worktree` (relocated from `using-analysis-worktrees` §When to Use Worktrees — Decision Table, preserved verbatim with the 6-row scenario/recommendation table) and `## Cleanup` (placed after §Examples, carrying the canonical `git worktree remove` ritual, the Option-4 discard teardown for execution-workflow, a note that `git worktree remove` also removes seeded data when the worktree was created through this skill, and the `--force` safety warning). Also merged the §Creating a Worktree content from `using-analysis-worktrees` (directory selection, safety verification, environment setup, seed, verify, report) into this skill as a single section — the new SKILL.md flows When-to-use → When-to-use (data-sync CLI only) → Creating → Data-sync CLI surface / modes / discovery / examples → Cleanup. Kept the existing §Command Surface / §Modes / §Managed Path Discovery / §Examples content intact. Updated the frontmatter `description:` to reflect the broadened scope: it now lists worktree-creation triggers, the original sync triggers, and the new cleanup trigger, preserving the "Optional for simple single-session analyses — a feature branch without a worktree is sufficient" opt-out. Triggering-check walkthrough: the description still fires on its original sync triggers (the core CLI content is unchanged), and now fires on worktree-setup + cleanup triggers that used to route to `using-analysis-worktrees`; nothing that previously fired is lost.

- [x] **Step 2: Delete `using-analysis-worktrees`.** `git rm -r skills/using-analysis-worktrees/` executed — removed `SKILL.md` (only file in the folder).

- [x] **Step 3: Move "when to use" judgment from `planning-workflow`.** The §Before you create directories paragraph in `planning-workflow/SKILL.md` (line 26) rewrote from "consider loading `superRA:using-analysis-worktrees` before any file creation" to "consider loading `superRA:worktree-data-sync` for the worktree setup". Added a trailing pointer "(See `worktree-data-sync` §When to Use a Worktree for the full decision table.)" so the planning-workflow summary sentence points at the detailed table in the consolidated skill.

- [x] **Step 4: Replace cleanup duplications.** `merge-workflow` Step 5 Cleanup Worktree: replaced the inline `git worktree remove <worktree-path>` block with "invoke `superRA:worktree-data-sync` §Cleanup for the teardown ritual." Preserved the "If the analysis was done on a feature branch without a worktree, skip this step" and "Report what was merged/pushed and what was cleaned up" lines. `execution-workflow` Step 4 Option 4 (Discard): replaced the inline `git checkout <base-branch> && git branch -D <analysis-branch> && git worktree remove <worktree-path>` block with "invoke `superRA:worktree-data-sync` §Cleanup — its Option-4 ritual covers the branch deletion and the optional `git worktree remove`." The typed-`discard` confirmation and "Stop after the branch and worktree are removed. Report what was deleted." lines are preserved.

- [x] **Step 5: Sweep references.** Grep for `using-analysis-worktrees` across `skills/`, `agents/`, `commands/`, `README.md`, `CLAUDE.md` returned zero matches in active content after the sweep. Active files updated: `skills/planning-workflow/SKILL.md` (Step 3 above), `skills/merge-workflow/SKILL.md` (§Integration pairs-with bullet rewrote from "Cleans up the worktree created by that skill" to "§Cleanup ritual for the worktree created by that skill at planning time"), `skills/execution-workflow/SKILL.md` (§Integration pairs-with bullet rewrote likewise, pointing at §When to Use a Worktree), `skills/agent-orchestration/references/agent-teams.md:95` (rewrote from "load `superRA:using-analysis-worktrees` first to set up the workspaces, and `superRA:worktree-data-sync` for copying managed data" to "load `superRA:worktree-data-sync` for both the workspace setup (§Creating a Worktree) and the managed-data copy"). Intentionally not touched: `PLAN.md`, `RESULTS.md`, `RELEASE-NOTES.md` retain the string as historical record.

- [x] **Step 6: Update inventory tables.** `using-superRA/SKILL.md` §Skill Inventory: removed the `using-analysis-worktrees` row; rewrote the `worktree-data-sync` row's purpose to "Isolated git worktrees, non-git data sync between them, and cleanup ritual." `skills/CATEGORIES.md` Utility table: same change. `README.md` Utility table: same change.

- [x] **Step 7: Validate.** Re-read `worktree-data-sync/SKILL.md` end-to-end: flows from when-to-use → data-sync-only use cases → creating the worktree (directory selection, safety, environment, seed, verify, report) → the data-sync CLI (command surface, modes, discovery, examples) → cleanup. Self-contained — no references to a separate worktree skill. Post-sweep grep confirms zero matches for `using-analysis-worktrees` in active content (`skills/`, `agents/`, `commands/`, `README.md`, `CLAUDE.md`). The three inventory tables now enumerate the same post-refactor utility set: `handoff-doc`, `refactor-and-integrate`, `report-in-markdown`, `semantic-merge`, `worktree-data-sync`. Atomic commit staged: `task 14: consolidate worktree skills into worktree-data-sync`.

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

---

### Integration Review (Stage 2, post-refactor sweep)
**Review status:** IMPLEMENTED

**Scope:** Cross-skill coherence across the 17-task refactor. Branch `refactor/workflow-domain-split`; git range `917e5f5..1b04980`. Plugin-dev vertical — data-analysis integration reference does not apply; `refactor-and-integrate/references/codebase-integration.md` (generic code-quality + §Project Doc Audit) is the operative reference.

> **Review notes:**
> 1. [MAJOR — README stage-name drift] `README.md:57,60,65,68,71,74` — the Workflow Map Mermaid diagram still emits **old non-canonical Stage names** that contradict Task 1's canonicalization: line 60 `Stage: implementation review` (should be `Stage: implementation` + note that `subagent_type` carries the split per Task 1 Step 3); line 65 `Stage: drift test creation / drift test review` (should be `Stage: drift-test`); line 68 `Stage: refactoring / integration review` (should be `Stage: refactoring / integration-review` hyphenated); line 71 `Stage: doc writer / doc reviewer` (should be `Stage: documentation`); line 74 `Stage: merge proposer / merge review` (should be `Stage: merge`). Line 57 also references `notebook-format.md` — correct. Fix: rewrite the five node labels to use canonical Stage names, matching the manifest. The README is the user-facing entry point; shipping it with stale names misroutes anyone who learns the plugin from this doc.
>    → implemented: rewrote all five Mermaid node labels to canonical Stage names — VAL now emits `Stage: implementation (subagent_type encodes role)`, INT1 `Stage: drift-test`, INT2 `Stage: refactoring / integration-review`, INT3 `Stage: documentation` (with "project-doc audit runs in Stage 2" note), MERGE `Stage: merge` (`README.md:60,65,68,71,74`).
> 2. [MAJOR — manifest enumeration] `README.md:187` — enumerates canonical Stage values as "`implementation`, `refactoring`, `drift-test`, `merge`, `documentation`, `planning-review`" (6 values), **missing `integration-review`** (the 7th row Task 1 Step 2 added). `README.md:169` correspondingly says "**six-row** Skill-Load Manifest" — the manifest is now **7 rows**. Fix: both lines need the 7th stage added.
>    → implemented: added `integration-review` to the Stage enumeration in the Key Design Decisions bullet (`README.md:187`) and updated "six-row Skill-Load Manifest" → "seven-row Skill-Load Manifest" in the using-superRA inventory row (`README.md:169`).
> 3. [MAJOR — broken structural invariants] `tests/structural-invariants.sh` has 5 FAILs and 1 silently-stale PASS after the refactor — the test suite that guards plugin structure is not reflecting Task 3 / Task 6 / Task 1 changes:
>    - **Block 3 (line 61-67):** asserts `econ-data-analysis/SKILL.md` main body contains `## Describe` / `## Analyze` / `## Validate` section headings. Task 3 extracted the full DAV content to `references/disciplines.md`; main body now uses bold inline paragraphs (`**Describe.**` / `**Analyze.**` / `**Validate.**`), not top-level section headings. Test must be updated to reflect the new location (check `references/disciplines.md` for the sections) or relaxed.
>    - **Block 3b (line 71-75):** asserts Validate section has `### Sensitivity analysis` sub-section. Same issue — content moved to `references/disciplines.md`.
>    - **Block 24 (line 496-501):** asserts `handoff-doc/SKILL.md` has exactly 4 numbered principles. Task 6 moved the 4 principles to `using-superRA` §Handoff Doc Discipline and slimmed handoff-doc to a doc-creation skill — the count is now 0 there. Test must be retargeted to `using-superRA/SKILL.md` (which now carries them under §The Four Document Principles).
>    - **Block 20 (line 390-396):** SILENTLY STALE — asserts "exactly 6 Stage rows" using regex `^\| \`(implementation|refactoring|drift-test|merge|documentation|planning-review)\`` which excludes `integration-review`. The test PASSES but is not counting the 7th row Task 1 added. Regex must add `integration-review` and the expected count must become 7.
>    
>    Plugin-dev's structural invariants are the analogue of drift tests for this vertical. Stage-2 integration review is exactly where these need to be updated. Leaving the suite broken defeats the safety net the branch is supposed to deliver.
>    → implemented: updated `tests/structural-invariants.sh` across all four blocks. Block 3 (line 55-82): retargeted `## Describe` / `## Analyze` / `## Validate` section checks to `references/disciplines.md`; kept Pitfalls + Red Flags checks in SKILL.md main body. Block 3b (line 84-90): retargeted `### Sensitivity analysis` check to `references/disciplines.md`. Block 20 (line 412-426): regex expanded to include `integration-review`; expected count changed from 6 to 7; handoff-doc mention floor lowered from ≥6 to ≥3 (Task 6 dropped handoff-doc from 5 manifest rows). Block 24 (line 497-530): handoff-doc principle count check replaced with assertion that `using-superRA` carries `### The Four Document Principles` with exactly 4 numbered principles under that heading — canonical home moved in Task 6. Full suite run: all PASS, 2 known upstream WARN, 0 FAIL.
> 4. [MAJOR — stale downstream pointer in merge-workflow] `skills/merge-workflow/SKILL.md:24` — reads "project-level docs (CLAUDE.md / AGENTS.md / README.md) have been audited, both via the doc-writer + doc-reviewer pair (**integration-workflow Step 3 sub-parts A + B**)". Task 9 deleted sub-part B entirely; project-doc audit moved to Stage 2 (refactorer + integration-reviewer). The correct pointer is "audited during Stage 2 via `codebase-integration.md` §Project Doc Audit; RESULTS.md matured via Step 3 sub-part A". This is the canonical "ownership moved; downstream doc still thinks the old owner runs it" drift that §Project Doc Audit is built to catch.
>    → implemented: rewrote the precondition bullet to split the two claims — RESULTS.md maturation via Step 3 sub-part A (doc-writer + doc-reviewer pair); project-doc audit via Stage 2 per `codebase-integration.md` §Project Doc Audit (`skills/merge-workflow/SKILL.md:24`).
> 5. [MAJOR — contributor-only CLAUDE.md referenced at runtime] Two skill files point runtime agents at the root `CLAUDE.md`, which `using-superRA/SKILL.md:6` explicitly states is "contributor-only and is NOT visible to agents running the plugin in a user's repo":
>    - `skills/integration-workflow/SKILL.md:405` — "see the foundational RA framing in `CLAUDE.md`"
>    - `skills/semantic-merge/SKILL.md:337` — "see the foundational RA framing in `CLAUDE.md`"
>    
>    Task 6 Step 7 fixed the two instances at `semantic-merge:278` and `integration-workflow:16` by retargeting to `using-superRA §Universal Principles`; these two Red-Flags-section references were missed. Fix: retarget both to `superRA:using-superRA §Universal Principles`. The runtime agent cannot read the repo-root `CLAUDE.md`, so these pointers resolve to nothing.
>    → implemented: retargeted both "see the foundational RA framing in `CLAUDE.md`" lines to `superRA:using-superRA §Universal Principles` (`skills/integration-workflow/SKILL.md:405`, `skills/semantic-merge/SKILL.md:337`).
> 6. [MAJOR — planning-workflow stale prose] `skills/planning-workflow/SKILL.md:91` — the "Living Plan and Results Docs" section says "load `superRA:handoff-doc`. That skill is the single source of truth for document mechanics and is loaded by implementer and reviewer subagents, so the rules stay consistent across roles." This contradicts Task 6's refactor on three points: (a) `handoff-doc` is NOT loaded by implementer/reviewer subagents per the new manifest (dropped from `implementation`, `refactoring`, `drift-test`, `integration-review`, `merge` rows); (b) the four principles / inline-edit rule / stale-content checklist live in `using-superRA §Handoff Doc Discipline`, not in `handoff-doc`; (c) `handoff-doc` is now a doc-creation skill, not "the single source of truth for document mechanics". Fix: rewrite to point planning-authors at `using-superRA §Handoff Doc Discipline` for the everyday discipline and at `handoff-doc/references/plan-anatomy.md` + `results-anatomy.md` for the anatomy templates (which planning-workflow Phase 2 does load as a doc-creator).
>    → implemented: split the pointer into two paragraphs — everyday editing discipline (four principles / inline-edit / stale-content / User Decisions Log / figure-embedding / Project Conventions) points at `superRA:using-superRA` §Handoff Doc Discipline; full anatomy templates (section layouts, code-block examples, two-stage lifecycle) points at `superRA:handoff-doc` (`plan-anatomy.md` + `results-anatomy.md`) which planning-workflow Phase 2 loads as a doc-creator (`skills/planning-workflow/SKILL.md:91-93`).
> 7. [MAJOR — missing RELEASE-NOTES entry] `RELEASE-NOTES.md` carries no entry for this 17-task refactor. The existing `## Unreleased` entry at the top describes the PRIOR rounds (1-3) of the workflow-domain-split branch; the current 17-task consolidation (Tasks 1-17 summarized in PLAN.md) does not appear. CLAUDE.md §General and Project Doc Audit require RELEASE-NOTES.md to reflect merge-ready state; shipping this without a new entry violates the doc-currency gate. Fix: add a new unreleased entry (or extend the current one) summarizing Tasks 1, 3, 4, 6, 9, 13, 14, 15 as the user-observable changes (canonical Stage names + manifest single-source-of-truth + handoff-doc slimmed + script-to-notebook folded + using-analysis-worktrees folded + verification-before-completion distributed + deprecated command stubs removed + project-doc audit relocated).
>    → implemented: extended the existing `## Unreleased` entry by renaming it to carry "design-coherence refactor" scope, updating the lede paragraph to describe a four-round restructure (adding Round 4 for this 17-task refactor), and appending eight dedicated Round 4 paragraphs covering Tasks 1, 3, 4, 6, 9, 13, 14, 15 as user-observable changes, plus a closing paragraph naming the branch `refactor/workflow-domain-split` and the `917e5f5..HEAD` commit range with a pointer at `PLAN.md` for the task-by-task record (`RELEASE-NOTES.md:3-14`).
> 8. [MINOR — inline-edit rule pointer drift] Several files still point at `superRA:handoff-doc` for inline-edit / four-principles content that Task 6 moved to `using-superRA §Handoff Doc Discipline`:
>    - `skills/econ-data-analysis/SKILL.md:124` — `§Review > Documentation and handoff` [GATING] item: "`RESULTS.md` updated in place for this task's section per `superRA:handoff-doc`" → should be `per superRA:using-superRA §Handoff Doc Discipline`.
>    - `skills/econ-data-analysis/SKILL.md:155` — `§Review > Completion verification` [STANDARD] item: "per the inline-edit rule in `superRA:handoff-doc`" → same retarget.
>    - `skills/using-superRA/SKILL.md:131` — §Execution Modes direct-mode bullet: "Update `PLAN.md` / `RESULTS.md` inline per `superRA:handoff-doc`" → since this file IS `using-superRA`, should be `per §Handoff Doc Discipline above`.
>    - `skills/planning-workflow/references/results-template.md:5` — "The canonical anatomy and inline-edit rules live in `superRA:handoff-doc`" — the anatomy DOES live there, but inline-edit rules do not. Split: "The canonical anatomy lives in `superRA:handoff-doc`; the inline-edit rule lives in `superRA:using-superRA` §Handoff Doc Discipline."
>    
>    These are not strictly wrong (handoff-doc still exists and doc-creators will find the rules via the pointer chain), but they violate the DRY principle Task 6 established — the everyday editing rules have exactly one authoritative home now, and that's `using-superRA`.
>    → implemented: retargeted all four pointers. `econ-data-analysis/SKILL.md:124` now reads `per superRA:using-superRA §Handoff Doc Discipline`; `:155` now reads `per the inline-edit rule in superRA:using-superRA §Handoff Doc Discipline`; `using-superRA/SKILL.md:131` now reads `per §Handoff Doc Discipline above` (self-reference, since this file is using-superRA); `planning-workflow/references/results-template.md:5` now splits into "canonical anatomy lives in `superRA:handoff-doc`" + "everyday editing discipline lives in `superRA:using-superRA` §Handoff Doc Discipline".
> 9. [MINOR — README principle count mismatch] `README.md:101` says "**Four workflow principles** are baked into every skill" but then lists **five** items (principles 1-4 + "DRY, composability, extensibility" as item 5). CLAUDE.md treats DRY/composability as a subsection under §Design Principles, not as a 5th workflow principle. Fix either (a) change "Four" to "Five" and restructure CLAUDE.md to match, or (b) re-label item 5 as "Architectural pattern" / "DRY discipline" below the four principles, separated out so the count stays 4. The researcher's intent (per CLAUDE.md) appears to be (b).
>    → implemented: option (b) per dispatch guidance — extracted the old numbered item 5 ("DRY, composability, extensibility") into a new `### Architectural discipline` subsection below the four numbered principles, with a one-line intro ("Below the four workflow principles sits one load-bearing architectural rule...") and the full DRY paragraph preserved verbatim. The four-principle count is now consistent with CLAUDE.md (`README.md:101-115`).
> 10. [MINOR — stale skill refs in codex-tools / gemini-tools] `skills/using-superRA/references/codex-tools.md:86` references `using-git-worktrees` and `finishing-a-development-branch` — both deleted in prior refactors; neither exists under `skills/`. `skills/using-superRA/references/gemini-tools.md:21` references `subagent-driven-development` — also deleted. These are runtime-reachable via the master skill loading the platform-specific tools reference at main-agent start. Fix: retarget the codex-tools pointers to `worktree-data-sync` (which absorbed `using-git-worktrees` per Task 14) and drop the `finishing-a-development-branch` reference (concern is covered by `merge-workflow` / `execution-workflow` Option 4); retarget gemini-tools' `subagent-driven-development` to `agent-orchestration` (the current home of subagent-dispatch mechanics).
>    → implemented: `codex-tools.md:86` rewritten to point at `superRA:worktree-data-sync` §Creating a Worktree for worktree + data-sync + cleanup, and at `superRA:merge-workflow` + `superRA:execution-workflow` Step 4 Option 4 for finishing-a-development-branch concerns. `codex-tools.md:25` also caught in the sweep — `agent-orchestration` / `subagent-driven-development` pair trimmed to just `superRA:agent-orchestration`. `gemini-tools.md:21` rewritten to point at `superRA:agent-orchestration` only.
> 11. [MINOR — execution-workflow diagram prose] `skills/execution-workflow/SKILL.md:69,88,89,91` — the Process flowchart nodes `"Dispatch reviewer (implementation review)"` use the retired "implementation review" label in a parenthetical. Task 1 Step 3 specified both roles use `Stage: implementation` with `subagent_type` carrying the split; the diagram label "(implementation review)" reads as a hint that the old `Stage: implementation review` value still applies. Fix: either drop the parenthetical or retarget to "(reviewer subagent)" so the prose matches the canonical name. Low severity because it's a diagram label, not a Stage emission — but it's a legibility trap for readers learning the dispatch model from the diagram.
>    → implemented: replaced all four `"Dispatch reviewer (implementation review)"` occurrences with `"Dispatch reviewer subagent"` — dropping the stale Stage-name parenthetical and aligning the diagram with the canonical `Stage: implementation` (role encoded by `subagent_type`) (`skills/execution-workflow/SKILL.md:69,88,89,91`).
> 
> **Doc edits needed (by file):**
> - `README.md` — items 1, 2, 9.
> - `tests/structural-invariants.sh` — item 3.
> - `skills/merge-workflow/SKILL.md:24` — item 4.
> - `skills/integration-workflow/SKILL.md:405`, `skills/semantic-merge/SKILL.md:337` — item 5.
> - `skills/planning-workflow/SKILL.md:91` — item 6.
> - `skills/planning-workflow/references/results-template.md:5` — item 8.
> - `RELEASE-NOTES.md` — item 7.
> - `skills/econ-data-analysis/SKILL.md:124,155`, `skills/using-superRA/SKILL.md:131` — item 8.
> - `skills/using-superRA/references/codex-tools.md:86`, `skills/using-superRA/references/gemini-tools.md:21` — item 10.
> - `skills/execution-workflow/SKILL.md:69,88,89,91` — item 11.
> 
> **Clean sweeps (already passing):**
> - `script-to-notebook`, `using-analysis-worktrees`, `verification-before-completion`, `execute-plan`, `write-plan`, `brainstorm` — zero hits in active content (skills/, agents/, commands/ [deleted], root README.md, root CLAUDE.md); PLAN.md + RESULTS.md + RELEASE-NOTES.md retain these as intentional history.
> - `sub-part B` — zero hits in skill bodies or agent files.
> - Canonical `Stage:` emissions in dispatch templates across all workflow skills and agent files — all 7 canonical values, no stray old names.
> - Four-principles consistency in CLAUDE.md — exactly 4 numbered workflow principles (lines 30, 34, 36, 38), no stray "six".
> - Skill inventory tables (using-superRA §Skill Inventory, CATEGORIES.md, README.md Utility/Workflow/Domain/Meta) all match the 13-skill set on disk (5 workflow + 1 domain + 5 utility + 2 meta).
