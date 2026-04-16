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
**Review status:** *(not started)*

**Files affected:** `skills/execution-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/merge-workflow/SKILL.md`, `skills/semantic-merge/SKILL.md`, `skills/agent-orchestration/SKILL.md`, `skills/agent-orchestration/references/agent-teams.md`
**Input:** The four workflow skills' "Agent Teams Mode" sections.
**Output:** No skill claims a per-workflow team "recipe" exists. Spawn instructions live only in `agent-teams.md`; team composition is derived from the manifest.

- [ ] **Step 1: Remove "Invoke for the [X Team] recipe" lines** from each workflow's "Agent Teams Mode" section:
  - `execution-workflow:300` (Task Team recipe)
  - `integration-workflow:448` (Integration Team recipe — including the "6 teammates" enumeration)
  - `merge-workflow:196` (Merge Team recipe — including "4 teammates" + "7-task graph")
  - `semantic-merge:307` (Semantic Merge Team recipe)
  Replace each with one sentence: "When Agent Teams are available, see `agent-orchestration` §Integration and `references/agent-teams.md` for spawn mechanics. Composition is derived from the manifest — one teammate per stage this workflow runs."

- [ ] **Step 2: Update agent-orchestration §Integration** (lines 147–154). Today this lists each workflow with a one-line composition descriptor. Keep the list, but make it clear these are *what stages each workflow runs*, not "recipes." Suggested rewrite for each entry: "**superRA:integration-workflow** — runs stages: drift-test, refactoring, integration-review, documentation."

- [ ] **Step 3: Validate.** Grep for "recipe" across `skills/`. Should return only this PLAN.md and incidental usage. Re-read each workflow's "Agent Teams Mode" section — every section should defer to `agent-orchestration` for mechanics. Atomic commit.

---

### Task 3: Slim `econ-data-analysis/SKILL.md` (shared base) + extract one operational-disciplines reference
**Review status:** *(not started)*

**Files affected:** `skills/econ-data-analysis/SKILL.md`, `skills/econ-data-analysis/references/disciplines.md` (new — combined Describe + Analyze + Validate), `skills/econ-data-analysis/references/notebook-format.md` (Task 4 destination — absorbs writing-discipline content here), `skills/using-superRA/SKILL.md` (manifest), `agents/implementer.md`, `agents/reviewer.md`
**Input:** Current `econ-data-analysis/SKILL.md` (470 lines).
**Output:** Both implementer and reviewer load the same SKILL.md (~210 lines, down from 470) — the shared base with the §Review & Self-Check Discipline both walk, plus Pitfalls (reviewer needs it for operation review) and Red Flags. Implementer additionally loads ONE operational-disciplines reference (`disciplines.md`) carrying the deep DAV content. Reviewer loads SKILL.md only.

**Architectural design.** DAV (Describe / Analyze / Validate) are **concurrent disciplines** applied at every implementation step — splitting them into three reference files is overkill since the implementer always loads all three together. One combined reference is cleaner. The "Documentation — cross-cutting writing practice" section dissolves entirely: its conceptual one-liner moves into the SKILL.md three-disciplines intro; the writing mechanics (markdown cells when, inline comments when, figures pointer) move to `notebook-format.md` per Task 4 (its natural home — script-formatting + writing discipline are one concern); the per-step checklist deletes (it duplicates §Review & Self-Check Discipline gates).

| Section in current SKILL.md | Lines | Goes to | Loaded by |
|---|---|---|---|
| Iron Law | 15 | SKILL.md | both |
| Three Concurrent Disciplines intro (one para each, including "doc is concurrent") | 5 | SKILL.md | both |
| Describe + Analyze + Validate (full operational content) | 195 | `references/disciplines.md` | implementer |
| Documentation cross-cutting writing practice | 25 | (split: 1 line into SKILL.md intro; ~20 lines into `notebook-format.md` per Task 4; ~5 lines deleted as redundant with §Review checklist) | n/a |
| §Review & Self-Check Discipline (with `Why this matters` annotations) | 80 | SKILL.md | both walk it |
| Common Rationalizations | 15 | SKILL.md | both |
| Red Flags - STOP and Start Over | 15 | SKILL.md | both |
| Pitfalls (operation-specific catalog) | 60 | SKILL.md | both — reviewer needs it to verify merges, lags, aggregations, etc. |
| Key References | 5 | SKILL.md | both |

Result: SKILL.md ~210 lines. Reviewer load ~210. Implementer load ~210 + ~200 (`disciplines.md`) + `notebook-format.md` (also loaded per Task 4) ≈ same total as today's monolith, but split into two discoverable chunks (the discipline + the writing mechanics) instead of one 470-line wall.

- [ ] **Step 1: Create `references/disciplines.md`.** Combine the Describe, Analyze, and Validate sections from current SKILL.md into one reference file. Open with a 2-paragraph intro re-anchoring the reader in the Iron Law and the concurrent-disciplines framing (so the file reads coherently standalone). Preserve the `## Describe` / `## Analyze` / `## Validate` section structure and every existing subsection inside each (Describe's after-loading / before-merge / outliers / after-transformation / visualization; Analyze's row-count rule, sort discipline, join discipline; Validate's sanity / multi-source / missing-data / sensitivity).

- [ ] **Step 2: Dissolve the Documentation cross-cutting section.** From SKILL.md's "Documentation — cross-cutting writing practice" section:
  - Keep the one-line conceptual statement ("Documentation runs continuously alongside Describe, Analyze, and Validate") — fold into the new SKILL.md three-disciplines intro.
  - Move the §Writing discipline subsection (markdown cells / inline comments / figures pointer / major-vs-minor-decision rule) into `notebook-format.md` per Task 4. **Task 4 must absorb this content; sequencing note added in PLAN.md preamble.** Until Task 4 lands, stage the content as a draft block at the end of `notebook-format.md` if it's already created, or in a `notebook-format.md.draft` file if not.
  - Delete the §Short checklist per step — it duplicates the §Review & Self-Check Discipline gates (Markdown cell stating what / Row-count log / Decision justifications). Adding it once in the §Review checklist is enough.
  - Delete the §Script categories paragraph (analysis vs runner) — already covered by `notebook-format.md` per Task 4.

- [ ] **Step 3: Rewrite the slim SKILL.md.** New structure: Header + Stage-Scoped References (updated for the new layout) → Iron Law → Three Disciplines intro (one paragraph each — Describe / Analyze / Validate; the documentation concept folded into either the Analyze paragraph or a closing sentence; both end with "for the full operational discipline see `references/disciplines.md`; for writing mechanics see `references/notebook-format.md`") → §Review & Self-Check Discipline → Pitfalls → Common Rationalizations → Red Flags → Key References.

- [ ] **Step 4: Add `Why this matters` annotations** to §Review & Self-Check Discipline. Every `[GATING]` item gets a one-sentence rationale (e.g., for "Every input described before the first transformation": "Why: violations are silent corruption — the most common analytical error is transforming data you don't understand. See `references/disciplines.md` §Describe."). `[STANDARD]` items get rationale only where the item could be misapplied without context. `[ADVISORY]` items are bare. This is what protects against mechanical checklist-walking by reviewers — they understand *why* each gate exists.

- [ ] **Step 5: Update the manifest** (`using-superRA` §Skill-Load Manifest). For the `implementation` row, split the `Stage-scoped references` cell by role:
  - **Implementer:** `references/disciplines.md` + `references/notebook-format.md` (the latter from Task 4).
  - **Reviewer:** none beyond SKILL.md. Pitfalls is in SKILL.md; the dispatcher may name a Pitfalls subsection in `Additionally:` for review focus on a specific operation, but no extra file load.

- [ ] **Step 6: Update agent files.**
  - `agents/implementer.md` step 2: "Load `econ-data-analysis/SKILL.md` plus `references/disciplines.md` and `references/notebook-format.md` per the manifest's `implementation` row for implementer."
  - `agents/reviewer.md` step 2: "Load `econ-data-analysis/SKILL.md` only. The §Review & Self-Check Discipline you walk lives in SKILL.md; Pitfalls for any operation under review is in SKILL.md. If your dispatch's `Additionally:` line names a specific Pitfalls focus, jump to it."

- [ ] **Step 7: Validate.** Re-read SKILL.md end-to-end — should read as a complete shared discipline (no cliffhangers; the §Review checklist annotations point at `disciplines.md` but the checklist itself is self-sufficient). Re-read `disciplines.md` end-to-end — should read as a coherent operational guide; the three sections flow naturally together (the concurrent-disciplines framing makes this intuitive, not jarring). Re-read `notebook-format.md` end-to-end — the absorbed writing-discipline content should sit naturally next to the script-format mechanics. Atomic commit.

---

### Task 4: Move `script-to-notebook` into `econ-data-analysis` as a reference
**Review status:** *(not started)*

**Files affected:** `skills/script-to-notebook/SKILL.md` (delete), `skills/script-to-notebook/references/*.md` (move), `skills/econ-data-analysis/references/notebook-format.md` (new), `skills/econ-data-analysis/references/jupytext-guide.md` (move), `skills/econ-data-analysis/references/julia-quarto-guide.md` (move), `skills/econ-data-analysis/SKILL.md`, `skills/using-superRA/SKILL.md`, `skills/CATEGORIES.md`, `README.md`, `agents/implementer.md`, `agents/reviewer.md`, all skills that mention `superRA:script-to-notebook`
**Input:** Current `script-to-notebook` skill + its two references.
**Output:** Notebook-formatting content lives under the data-analysis vertical. Standalone skill is removed. Skill inventory shrinks by one.

- [ ] **Step 1: Move content.** Move `skills/script-to-notebook/SKILL.md` → `skills/econ-data-analysis/references/notebook-format.md` (keep the body; trim the frontmatter to a one-line description). Move `skills/script-to-notebook/references/jupytext-guide.md` and `julia-quarto-guide.md` to `skills/econ-data-analysis/references/`.

- [ ] **Step 1b: Absorb the writing-discipline content from Task 3 Step 2.** The dissolved §Documentation cross-cutting writing practice section (markdown cells when, inline comments when, figures discipline, major-vs-minor-decision rule) lands in `notebook-format.md` here — script-formatting and writing discipline are one concern. Place it as a new "Writing Discipline" section after the cell-organization section in `notebook-format.md`. If Task 3 staged the content as `notebook-format.md.draft`, merge it in and delete the draft file.

- [ ] **Step 2: Delete the skill folder.** `git rm -r skills/script-to-notebook/`.

- [ ] **Step 3: Update `econ-data-analysis/SKILL.md`** §Stage-Scoped References table to add the new `notebook-format.md` entry. Update §Documentation cross-cutting to point at `references/notebook-format.md` (replace the `superRA:script-to-notebook` mentions). Note: Task 3 has already removed most of this section; this step finalizes the references-table entries.

- [ ] **Step 4: Update the manifest** (`using-superRA` §Skill-Load Manifest). The `implementation` row's reference cell currently mentions `superRA:script-to-notebook` parenthetically. Replace with `econ-data-analysis/references/notebook-format.md` (data-analysis vertical only).

- [ ] **Step 5: Sweep all references.**
  ```bash
  grep -rn "script-to-notebook\|superRA:script-to-notebook" skills/ agents/ commands/ README.md CLAUDE.md CATEGORIES.md
  ```
  Update every match to point at `econ-data-analysis/references/notebook-format.md` (or delete if the mention is now obsolete).

- [ ] **Step 6: Update inventory tables.** Remove `script-to-notebook` row from `using-superRA` §Skill Inventory and `skills/CATEGORIES.md` Utility table and `README.md` skill table.

- [ ] **Step 7: Validate.** Grep again for `script-to-notebook` — only this PLAN.md and incidental references should remain. Re-read `econ-data-analysis/SKILL.md` end-to-end. Atomic commit.

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
**Review status:** *(not started)*

**Files affected:** `skills/using-superRA/SKILL.md`, `skills/using-superRA/references/main-agent-autonomy.md` (new), `skills/using-superRA/references/session-bootstrap.md`, `skills/handoff-doc/SKILL.md` (trimmed), `agents/implementer.md`, `agents/reviewer.md`, `skills/execution-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/merge-workflow/SKILL.md`, `skills/semantic-merge/SKILL.md`, `skills/using-superRA/SKILL.md` (manifest)
**Input:** Today, agents load BOTH `using-superRA` (for principles) AND `handoff-doc` (for doc discipline). Workflow skills restate the four principles inline. Autonomy / stop-points / banned-phrasings live only in `execution-workflow`. Result: implementer/reviewer dispatch loads ~120 lines of `handoff-doc` they could read once at the design-contract level.
**Output:** Implementer/reviewer load only `using-superRA` for cross-cutting design + handoff-doc agent essentials. `handoff-doc` becomes a doc-*creation* skill (loaded by `planning-workflow` and the Stage 2 doc-writer only). Workflow skills carry no principle restatements. Autonomy lives in a main-agent-only reference.

**Architectural principle (per researcher):** `using-superRA` is the design home — every agent reads it. Anything an implementer or reviewer needs to know that crosses skill boundaries (the four principles, the handoff-doc editing rules, the User Decisions Log format, the autonomy contract) lives in `using-superRA` directly or in its `references/`. Specialized skills become loaders for callers that need the *full* discipline (creating docs from scratch, orchestrating). Subagent dependencies shrink.

- [ ] **Step 1: Add §Handoff Doc Discipline to `using-superRA/SKILL.md`** (~35 lines, new section after §Universal Principles). Absorb from `handoff-doc/SKILL.md` the agent-runtime essentials:
  - The four document principles (latest-state-only, live-and-committed, task-block-structure, doc-is-the-record). §Universal Principles #2 ("Handoff docs are the auditable record …") already states the headline; this new section spells out the operational rules.
  - The inline-edit rule (one paragraph).
  - The stale-content checklist (5 bullets — what counts as stale, remove not strike-through).
  - The §User Decisions Log format (where: task-scoped vs `## Decisions`; format: 3-line blockquote with date / question / rationale; the "log before you act" rule).
  - Figure embedding pointer (one sentence: figures go in `results_attachments/`; full mechanics in `report-in-markdown/references/rich-content.md`).
  - Pointer to the `## Project Conventions` section (introduced by Task 5).
  - Pointer to `handoff-doc/references/plan-anatomy.md` and `results-anatomy.md` for full templates (only doc-creators need them).

- [ ] **Step 2: Trim `handoff-doc/SKILL.md`** to a doc-creation skill. What remains: the two-stage RESULTS.md lifecycle paragraph, the §Standalone use vs Multi-agent workflows note, pointers to anatomy references, and a top-line rerouting note: "Cross-cutting agent-runtime essentials (the four principles, inline-edit rule, User Decisions Log, figure embedding pointer) live in `using-superRA` §Handoff Doc Discipline. This skill is for doc *creation*: invoked by `planning-workflow` for new docs and by the Stage 2 doc-writer for RESULTS.md maturation." Target: shrink from 118 lines to ~50.

- [ ] **Step 3: Create `using-superRA/references/main-agent-autonomy.md`.** Move the body of `execution-workflow` §Autonomy and Stop Points (lines 267–289) into it. Generalize so it applies to every workflow phase, not just execution. Include: "proceed without asking" patterns, "stop and ask" classes (the three pause classes from §Universal Principles #4), banned phrasings ("Should I proceed?", "Want me to continue?", etc.). Top of file: "Loaded by the main agent at session start. Subagents inherit autonomy from their dispatch boundary; they do not load this."

- [ ] **Step 4: Hook the new reference into session-start.** Update `using-superRA/references/session-bootstrap.md` to instruct the main agent to load `main-agent-autonomy.md` after the cross-session detection checks.

- [ ] **Step 5: Update agent files (drop handoff-doc dependency for typical work).**
  - In `agents/implementer.md` step 1: replace "Load `superRA:handoff-doc` before reading or editing PLAN.md or RESULTS.md" with: "You already loaded `superRA:using-superRA` per your frontmatter — its §Handoff Doc Discipline carries the rules you need for editing PLAN.md / RESULTS.md (four principles, inline-edit rule, stale-content checklist, User Decisions Log format, figure embedding pointer). Load `superRA:handoff-doc` only if your task creates a new PLAN.md or RESULTS.md from scratch (rare for implementer)."
  - Same in `agents/reviewer.md` step 1.

- [ ] **Step 6: Update the manifest.** Drop `handoff-doc` from the `implementation`, `refactoring`, `drift-test`, `merge`, and `integration-review` rows' "Required skills" cells. Keep it in the `documentation` row (doc-writer creates the matured RESULTS.md and needs the full discipline) and in `planning-review` (planning agents need plan-anatomy). Add a column-header note: "Skills listed here are loaded *in addition to* `using-superRA`, which carries the cross-cutting agent essentials."

- [ ] **Step 7: Strip principle and User-Decisions restatements from workflow skills.** In each of `execution-workflow`, `integration-workflow`, `merge-workflow`, `semantic-merge`:
  - Replace any restatement of the four principles with: "See `using-superRA` §Universal Principles."
  - Strip the §Autonomy and Stop Points body from `execution-workflow` (now in main-agent-autonomy.md). Replace with: "Workflow stop points are listed below. The autonomy contract (proceed-without-asking patterns, stop-and-ask classes, banned phrasings) is in `using-superRA/references/main-agent-autonomy.md` — main-agent only." Then list only the workflow-specific stop points (no rationale).
  - Replace each "log per `handoff-doc` §User Decisions Log" pointer with "log per `using-superRA` §Handoff Doc Discipline §User Decisions Log." (Task 7 will sweep the remaining duplicate text around these pointers.)

- [ ] **Step 8: Validate.** Re-read `using-superRA/SKILL.md` end-to-end — it should now feel like the central design contract every agent shares (principles + handoff-doc discipline + role-cross-cutting rules). Re-read `handoff-doc/SKILL.md` — should feel like a doc-creation skill, not an everyday agent skill. Re-read `agents/implementer.md` and `agents/reviewer.md` — neither should require loading handoff-doc for typical work; both should point at using-superRA's new section for doc-editing rules. Grep "four principles" / "load-bearing principle" — restatements should appear only in `using-superRA` and `main-agent-autonomy.md`. Atomic commit.

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
**Review status:** IMPLEMENTED

> **Review notes:**
> 1. [STANDARD] Wrong commit SHA cited in Step 7's note and in `RESULTS.md` Task 13 §"Note on §Skill Types". Both say the `§Skill Types` section was "removed in pre-plan commit `e5c8b58`". That SHA is the `plan for consolidate the workflow` commit — the PLAN.md creation commit, not a `using-superRA` edit. The commit that actually removed EXTREMELY-IMPORTANT / Red Flags / Skill Types from `skills/using-superRA/SKILL.md` is `956f6cc` ("chore: pre-plan cleanup — bump version to 0.0.4 and trim using-superRA"). Verified by `git log -S 'Rigid' -- skills/using-superRA/SKILL.md` and by reading `956f6cc`'s commit message, which explicitly names the three removed sections. Fix: replace both citations of `e5c8b58` with `956f6cc`. Minor factual correction, but the dev-log is the record — future agents following the pointer will land on the wrong commit and get confused about the provenance of the §Skill Types removal.
>    → implemented: replaced `e5c8b58` with `956f6cc` in both citations (`PLAN.md:376` Step 7 note and `RESULTS.md:176` §"Note on §Skill Types"); verified `956f6cc` is the commit that actually trimmed using-superRA via `git show --stat 956f6cc` (commit message names EXTREMELY-IMPORTANT / Red Flags / Skill Types removal).
 `skills/verification-before-completion/` (delete), `agents/implementer.md`, `agents/reviewer.md`, `skills/refactor-and-integrate/references/drift-test-quality.md`, `skills/execution-workflow/SKILL.md`, `skills/using-superRA/SKILL.md` (inventory + types), `skills/CATEGORIES.md`, `README.md`, `skills/writing-skills/SKILL.md` (one mention)
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
**Review status:** *(not started)*

**Files affected:** `skills/agent-orchestration/SKILL.md`, `skills/execution-workflow/SKILL.md` (one-line cross-reference).
**Input:** Current `agent-orchestration` Decision Framework section (the parallel-dispatch / Agent Teams / orchestrator-relay table) and its §Integration section. Current `execution-workflow` Per-Task Execution Steps + §Dispatch Templates pointer.
**Output:** `agent-orchestration` SKILL.md carries explicit orchestrator guidance on when to reuse a warm agent via `SendMessage` versus when to spawn a fresh dispatch. `execution-workflow` carries a one-line pointer at that guidance. The heuristic prevents reflexive fresh-dispatch of small follow-up tasks while preserving the adversarial-review property of the implementer–reviewer pair.

- [ ] **Step 1: Draft the new subsection in `agent-orchestration` SKILL.md.** Place it immediately after the Decision Framework section (so the two sit together as the orchestrator's dispatch-choice toolkit). Suggested section title: **"Agent reuse vs fresh dispatch."** Cover:
  - **Context-reload cost framing.** Each fresh dispatch pays to reload `superRA:using-superRA`, the active domain skill (where applicable), `superRA:handoff-doc`, and the module-level `CLAUDE.md` / `AGENTS.md` / `README.md` walk-up for every directory the task touches. For small follow-ups in the same context, that cost is disproportionate.
  - **Criteria favoring reuse (via `SendMessage` to the warm agent's name/id).** Small scope, same domain context, non-overlapping file set, sequential task where the next task benefits from what the agent already knows. Good example: a grep-sweep follow-up after a prior grep-sweep task.
  - **Criteria favoring fresh dispatch.** Large new task, different domain vertical, meaningful file-set overlap with in-flight work, task requires a perspective the warm agent cannot provide (see reviewer exception below).
  - **Bundling as a third option.** For several tiny tasks that share context up front, a single implementer dispatch can carry a multi-task brief — list each task pointer in `Task:` and spell out the sequence and boundaries in `Additionally:`.
  - **Reviewer-always-fresh rule (named exception).** Reviewers are adversarial by design (see §Reviewer–Orchestrator Dynamic in `using-superRA` and CLAUDE.md Workflow principle #1). Review passes always spawn a fresh reviewer agent; never send a review task to the implementer that just produced the work. Make this a hard rule in the new subsection, not a soft preference.
  - **`SendMessage` mechanic pointer.** One sentence: the `to:` field takes the agent's id (or name, for teammates); the recipient resumes with its full session context and the new message is queued for it. No code example needed — the tool description carries the details.

- [ ] **Step 2: Add the `execution-workflow` cross-reference.** In `execution-workflow` §Per-Task Execution Steps (near step 1 of the per-task loop, which is where the reuse decision actually fires), add a one-line pointer: "See `agent-orchestration` §Agent reuse vs fresh dispatch for when to reuse a warm implementer via `SendMessage` versus spawning a fresh dispatch." Do not duplicate the heuristic's content.

- [ ] **Step 3: Validate.** Re-read `agent-orchestration` end-to-end — the new subsection should sit naturally between the Decision Framework and the Dispatch Templates section; no duplication with the existing parallel/teams/relay table. Re-read `execution-workflow` to confirm the pointer lands cleanly without stepping on adjacent prose. Atomic commit.

**Dependency note:** Task 17 may run at any time after Task 1 lands (Task 1 touches `agent-orchestration`-adjacent files but not `agent-orchestration/SKILL.md` itself; still, running Task 17 after Task 1 avoids any chance of interaction). Task 16's final consistency pass must include Task 17's touched files in its end-to-end re-read.

---

## Out of scope (deferred)

These items came up in the design review but were explicitly deferred:

- **D6 (failure-recovery sections in workflow skills)** — deferred. Will be revisited if real failure modes accumulate.
- **D7 (analysis-testing skill for non-drift tests)** — deferred. Open question whether to add a new skill or fold into `econ-data-analysis`.
- **README user-facing content (B6)** — left as-is; intentionally duplicates principles for the user-facing entry point.
- **The `six principles` discrepancy in the installed plugin (A4)** — repo is correct ("four"); will resolve on next plugin install/release.
