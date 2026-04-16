# superRA Design Coherence Refactor — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-16 (pre-Task-1)
**Status:** In Progress

**Domain vertical:** Plugin-development (skills/hooks/docs refactor). Not a data-analysis task — no row-counts, no figures, no regression outputs. "Key Findings" captures edits made, orphan-reference grep results, and any skill-description triggering check outcomes.

---

## Task 1: Consolidate Stage names + remove dispatch re-statements

**Status:** IMPLEMENTED

### Key Findings

**Canonical Stage set after the refactor** (matches `using-superRA` §Skill-Load Manifest 1:1): `implementation`, `refactoring`, `drift-test`, `integration-review`, `merge`, `documentation`, `planning-review`. One new manifest row added — `integration-review` — because integration review's reference set differs from `refactoring` (it runs the same loads today, but the two are semantically distinct stages and Tasks 3 / 6 will refine them independently). The `Fallback rule` that silently mapped unknown `Stage:` values to `implementation` defaults is replaced by an explicit halt-and-report policy — drift through guessed fallbacks is no longer a failure mode.

**Dispatch templates collapsed to canonical shape.** Every dispatch across `integration-workflow`, `merge-workflow`, `semantic-merge`, and `refactor-and-integrate` now emits only `Stage:` + `Task:` (+ `Git range:` for reviewers) + the "Follow the standard stage-relevant workflow" prefix + `Additionally:` steering. The redundant `Skills:` / `Domain reference(s):` / free-form context fields (`Key results to protect:`, `Tests under review:`, `Merge context:`, etc.) are gone — the manifest specifies the loads and the agent reads task content from `PLAN.md` / `RESULTS.md` directly. Dispatch-line count dropped sharply across the four skills.

**Three per-workflow Agent-Types tables deleted.** `integration-workflow` (the 8-row domain-reference table), `semantic-merge` (`## Agent Types and Domain References`), and `execution-workflow` (`## Agent Types`) all had tables enumerating what each Stage loads — those tables duplicated the manifest and were drift sources. Each is replaced with a 2-3-line `## Agent Loads` section pointing at `superRA:using-superRA` §Skill-Load Manifest and naming which manifest rows the workflow runs.

**Agent files stop loading dispatch-named references.** `agents/implementer.md` and `agents/reviewer.md` previously step-3-loaded "additional skills specified in your dispatch prompt" and step-4-loaded "the domain reference file specified in your dispatch prompt." Both steps assumed dispatches named references — they no longer do. Step 3 is rewritten to "load any additional skill the dispatch's `Additionally:` line names (rare — overrides only)." Step 4 is deleted; remaining steps renumber; the in-paragraph cross-reference updates from "step 7 below" to "step 6 below." Both agents' stage-loading paragraph is also updated: the old fallback-to-`implementation` for unknown Stages is replaced with halt-and-report.

**One description frontmatter change, one writing-skills triggering check.** Per override #3, only `skills/refactor-and-integrate/SKILL.md`'s `description:` field was modified — its old trailing enumeration listed deprecated Stage names (`drift test creation`, `drift test review`, `integration review`, `merge proposer`, `merge review`) that no longer exist anywhere in the plugin. Updated to name the canonical manifest rows (`drift-test`, `refactoring`, `integration-review`, `merge`). Triggering check: the description still fires on its original triggers — "creating drift tests", "refactoring analysis code", "writing clean merge integration commits" — so no discovery surface is lost; the change only synchronizes the enumeration with the new manifest, an inline correctness fix.

**Task 1 preserved the coupled-chain precondition.** Per override #5, the `integration-review` manifest row carries the same reference load as `refactoring` (domain §Refactor integrity; `codebase-integration.md`; `integration.md`; `integrate-drift-tests.md` if drift tests exist). Tasks 3 and 6 will refine that row later — Task 1's responsibility was only to establish the row with current loads so downstream tasks have a target to refine.

### Validation

Step-7 greps after the refactor:
- `Stage:` across `skills/` + `agents/` — every live emission is canonical: `drift-test`, `integration-review`, `refactoring`, `merge`, `documentation`. (Manifest rows: `implementation`, `refactoring`, `drift-test`, `integration-review`, `merge`, `documentation`, `planning-review`.)
- `Skills:` / `Domain reference(s):` in dispatch blocks — zero. The two remaining `Skills:` hits in the wider grep (`agent-orchestration:77`, `refactor-and-integrate:36`) are meta references describing where override lines *would* go and the fact that dispatches do not restate them; neither is a live dispatch line.
- `Agent Types` tables — zero remaining anywhere.
- Stale Stage names as live `Stage:` field emissions in dispatch blocks across `skills/` + `agents/` — zero (every `Stage:` value matches a manifest row). Stale stage-name *prose* references remain in files outside Task 1's Files-affected list: `README.md` architectural diagram (5 `Stage:` strings in the user-facing flow); role-description enumerations in `skills/agent-orchestration/SKILL.md:127`, `agents/reviewer.md:6,109`, `skills/execution-workflow/SKILL.md` graphviz labels at 69/88/89/91, `skills/report-in-markdown/SKILL.md:33`, `skills/refactor-and-integrate/SKILL.md:17,80,82`, `skills/econ-data-analysis/SKILL.md:327`, `skills/econ-data-analysis/references/integration.md:3,5`; plus the old `drift test creation` row-name in `tests/structural-invariants.sh:431,433,435`. Deferred to Task 16 Step 6 per PLAN.md (line 453 explicitly names these strings for the final sweep). Historical audit enumerations in `PLAN.md` Step 1 and release notes in `RELEASE-NOTES.md` also retain the old names, both legitimate as record.

### Notes

The `integration-review` manifest row currently replicates the `refactoring` row verbatim. Tasks 3 and 6 split and refine it. Task 6 also drops `handoff-doc` from most rows (superseded by `using-superRA` §Handoff Doc Discipline) — Task 1 leaves the `handoff-doc` loads intact because Task 6 owns that sweep.

---

## Task 2: Drop Agent Teams "recipe" framing

**Status:** IMPLEMENTED

### Key Findings

**No skill body still claims a per-workflow team recipe exists.** Each of the four workflow skills' "Agent Teams Mode" sections (`execution-workflow:283`, `integration-workflow:417`, `merge-workflow:186`, `semantic-merge:295`) had an "Invoke `superRA:agent-orchestration` for the [X] Team recipe" sentence enumerating teammate counts, role names, and task-graph structure — every one of those is gone. They are replaced with a single pointer at `agent-orchestration` §Integration + `references/agent-teams.md` for spawn mechanics. Composition ("one teammate per stage this workflow runs") is stated once per section; the enumerations live only in the manifest now.

**Opening paragraphs collapsed into one sentence.** The pre-edit sections opened with a "When Agent Teams are available …" paragraph followed by the (now-replaced) "Invoke for the recipe" paragraph — the replacement produced two "When Agent Teams are available" lead-ins per section. Collapsed each into a single opening sentence so the reading flow is clean: "When Agent Teams are available (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`), [workflow-specific purpose] — [direct-iteration rationale]. See `superRA:agent-orchestration` §Integration …"

**`execution-workflow:43` (the early "Agent Team mode" bullet block) also updated.** The bullet "Load `superRA:agent-orchestration` for the Task Team recipe (team composition, task graph, lifecycle)" became "See `superRA:agent-orchestration` §Integration and `references/agent-teams.md` for spawn mechanics; composition is derived from the manifest — one teammate per stage this workflow runs." Same pointer language as the §Agent Teams Mode section further down, so the skill is internally consistent.

**`semantic-merge` §Integration pairs-with line cleaned.** The bullet "**superRA:agent-orchestration** — Semantic Merge Team recipe for Tier 2/3 merges" became "§Integration and `references/agent-teams.md` for team spawn mechanics on Tier 2/3 merges" — no more "recipe" framing in the pairs-with list either.

**`agent-orchestration` §Integration rewritten to runs-stages framing.** The lede was "Skills that use Agent Teams mode (composition derived from the manifest — see `references/agent-teams.md` for spawn mechanics):". Rewrote to explicitly state "There are no per-workflow team 'recipes' — composition is read from the workflow (which stages it runs) and the manifest (what each stage loads)." Each of the four workflow entries now names its runs-stages list:
- `execution-workflow` → stages: implementation.
- `integration-workflow` → stages: drift-test, refactoring, integration-review, documentation.
- `merge-workflow` → stages: merge, refactoring, integration-review.
- `semantic-merge` → stages: merge.

### Validation

Grep for "recipe" across `skills/` returns four hits, all in `agent-orchestration`:
- `SKILL.md:14` — "No per-workflow recipe is needed" (the existing post-Task-1 statement).
- `SKILL.md:173` (approx) — the new "There are no per-workflow team 'recipes'" statement in §Integration.
- `references/agent-teams.md:8` — "No per-workflow team recipe is needed."
- `references/agent-teams.md:50` — "There is no per-workflow recipe beyond this."

Every remaining hit is a denial of the recipe framing, not a claim that a recipe exists. No workflow skill body still contains the "Invoke for the recipe" pattern.

Re-read each workflow's §Agent Teams Mode section end-to-end: the opening paragraph states when teams can be used + the iteration rationale, the second paragraph points at `agent-orchestration` §Integration + `references/agent-teams.md` for spawn mechanics and declares composition is derived from the manifest. No enumeration of teammates or task graph inside any workflow skill — those live only in `agent-teams.md` now.

### Notes on Files-affected list

PLAN.md originally listed `skills/agent-orchestration/references/agent-teams.md` in Task 2's affected files. After the edits, `agent-teams.md` was not modified — Task 1 had already landed the "No per-workflow team recipe is needed" phrasing there (two instances: lines 8 and 50), so there was no corresponding change needed in this task. Dropped from the post-task affected-files list to keep the record accurate.

---

## Task 3: Slim `econ-data-analysis/SKILL.md` + extract disciplines reference

**Status:** IMPLEMENTED

### Key Findings

**Shared-base SKILL.md and role-split operational references.** `econ-data-analysis/SKILL.md` shrank from 473 lines to 276 — the full Describe / Analyze / Validate operational content (195 lines) moved to the new `references/disciplines.md`, which the **implementer loads** and the **reviewer does not**. The shared §Review & Self-Check Discipline stays in SKILL.md's main body so both roles walk the same checklist (one source of truth, two perspectives). Pitfalls, Common Rationalizations, and Red Flags stay in SKILL.md too — the reviewer needs §Pitfalls to verify operation-specific correctness (merges, lags, aggregations, filters, variable construction, missing data).

**Three-disciplines framing is now a lean summary with pointers.** The three-paragraph intro in SKILL.md replaces the prior 200-line `## Describe` / `## Analyze` / `## Validate` subsection tree. Each paragraph carries the headline rules (Iron Law for Describe; row-count MANDATORY + one-operation-per-step + sort discipline + join-type discipline for Analyze; four subdisciplines of Validate including escalation-via-AskUserQuestion) and points at `references/disciplines.md §{Describe|Analyze|Validate}` for the operational expansion. The implementer's context is split into two discoverable chunks (the shared discipline + the writing mechanics) rather than the prior 473-line wall; the reviewer's load drops to 276 lines while retaining every verification-critical section.

**§Review & Self-Check Discipline now carries `Why:` rationales on every [GATING] item.** Ten gating items across four sub-sections (Gating / Documentation-and-handoff / Refactor-integrity / Completion-verification) each gain a bulleted `*Why:*` sub-item explaining the failure mode the gate prevents — silent corruption via skipped describe, row-count drift via missing prints, merge bets against unchecked keys, chat-only findings lost at session boundaries, refactors that silently convert transparent analyses into opaque ones, re-expected drift silently changing the headline, uncommitted state that cannot be reproduced. Three `[STANDARD]` items also gained rationales where context mattered (PLAN.md-specifies handoff-doc tie-in, major-vs-minor-decision split, expectations-comparison as forcing-function). `[ADVISORY]` items stay bare. This protects against mechanical checklist-walking by reviewers — the gate tells them *what*, the rationale tells them *why*, so a novel situation can be judged rather than just matched against the line.

**§Writing Discipline absorbed into `notebook-format.md`.** The dissolved §Documentation cross-cutting writing practice section of SKILL.md landed as a new `## Writing Discipline` section in `notebook-format.md`, placed between §Markdown Cells and §Output. The absorbed content carries the markdown-cells / inline-comments / major-vs-minor-decisions / figures-pointer rules, plus a new closing paragraph that makes the major/minor split explicit ("minor decisions inside a cell document *the choice*; major decisions in a markdown cell document *the reasoning that led to the choice*. A reviewer tracing how the analysis got to its current shape reads the markdown cells first, then the code"). The prior §Short checklist per step and §Script categories paragraph from SKILL.md were deleted — the first duplicates §Review & Self-Check Discipline gates, the second is covered by `notebook-format.md`'s §When to Use.

**Manifest and agent files reflect the role split.** The `implementation` row's Stage-scoped-references cell now carries an explicit role split: implementer loads `references/disciplines.md` + `references/notebook-format.md`; reviewer loads SKILL.md only. The lede paragraph above the manifest table was updated — role differentiation now appears on two rows (`implementation` and `documentation`), not just one. Both agent files' Stage → skills paragraph and §Before You Start Step 2 were rewritten to name the exact loads per role.

### Notes on section ordering

PLAN.md Step 3's target ordering places §Review & Self-Check Discipline before §Pitfalls and §Common Rationalizations before §Red Flags. The pre-refactor file had §Review → §Common Rationalizations → §Red Flags → §Verification Checklist → §Pitfalls (in that order). Reordered the tail to match the target: §Pitfalls moved up immediately after §Review, followed by §Common Rationalizations → §Red Flags → §Key References. The §Verification Checklist stub (a one-line "see §Review & Self-Check Discipline above" pointer) was deleted — after the reorder it became a stub pointing backwards to the section right above it, serving no navigation purpose.

### Notes on line-count target

PLAN.md §Architectural design stated ~210 lines as the SKILL.md target. Final is 276 lines. The delta is driven by the `Why:` rationales on Step 4 (~30 lines added as explicit goal), a richer Stage-Scoped References table (new `disciplines.md` row + expanded role-split explanation), and the three-paragraph summary of DAV disciplines (slightly longer than the ~5 lines estimated so each paragraph can stand as a self-sufficient headline summary). The reviewer's total load is still cut roughly in half (from 473 to 276), and the implementer's total is the same as today's monolith but split into three discoverable chunks.

---

## Task 4: Move `script-to-notebook` into `econ-data-analysis` as a reference

**Status:** IMPLEMENTED

### Key Findings

**Skill retired; content relocated under the data-analysis vertical.** The standalone `superRA:script-to-notebook` utility skill is gone — its three files (`SKILL.md` + `references/jupytext-guide.md` + `references/julia-quarto-guide.md`) moved via `git mv` into `skills/econ-data-analysis/references/`, with the old SKILL.md body landing as `notebook-format.md` (frontmatter trimmed to a one-line blockquote; title changed from "Script to Notebook" to "Notebook Format"). The directory `skills/script-to-notebook/` no longer exists. Skill inventory shrinks by one as planned.

**Manifest now carries the notebook-format reference explicitly.** The `implementation` row's Required-skills cell dropped the trailing `+ script-to-notebook` enumeration; the Stage-scoped-references cell gained `econ-data-analysis/references/notebook-format.md` as a data-analysis-specific load. The manifest remains the single source of truth — any agent dispatched at Stage `implementation` sees the notebook-format reference called out on the manifest row itself, not implied by a separate skill load.

**Active sweep — zero residual mentions outside historical records.** Post-refactor grep across `skills/`, `agents/`, `commands/`, `README.md`, `CLAUDE.md`, `CATEGORIES.md` shows no `script-to-notebook` matches. Eight active files updated (five SKILL.md bodies, one agent file, the README, and CATEGORIES); PLAN.md / RESULTS.md / RELEASE-NOTES.md retain the strings as historical record by design. Full file list in PLAN.md Step 5.

**Stage-Scoped References table in `econ-data-analysis/SKILL.md` is now internally consistent.** The table listed three references pre-refactor (planning, integrate-drift-tests, data-robustness-checklist) despite the file directory carrying `integration.md` (named in the manifest but missing from the table). Added both the missing `integration.md` row and the new `notebook-format.md` row; lede sentence updated from "Two companion reference files..." to "Companion reference files..." to match the now-five-row table. Each table row names its phase + purpose + companion-file relationships (notebook-format's companions `jupytext-guide.md` and `julia-quarto-guide.md` are named in its row).

### Notes on Step 1b (sequencing deviation)

PLAN.md's Step 1b expected Task 3 to have staged a `notebook-format.md.draft` file carrying the dissolved §Documentation cross-cutting writing-discipline content from the SKILL.md body. Task 3 has not run yet in the plan sequence (Tasks 1, 4, 3, 6 are the coupled chain per the Task-sequencing note; Task 4 runs second), so no draft file existed and the dispatch override instructed: proceed with Step 1 content as-is, note the absence. When Task 3 runs, its Step 2 absorbs the writing-discipline content into the now-existing `notebook-format.md` as a new "Writing Discipline" section after the cell-organization section. The `notebook-format.md` file that Task 4 leaves behind is the correct target — Task 3's implementer will find it in place.

### Reviewer note on working-tree reset

During implementation, the coordinator reported that a prior reviewer agent accidentally bundled Task 4's pre-staged file renames into one of its review commits, then soft-reset to unbundle. The result: the three file moves came back as unstaged deletes + untracked new files in the working tree. Git history was not corrupted; only the index was affected. Re-staged before committing.

---

## Task 5: Cache project conventions in PLAN.md header

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 6: Centralize agent-shared discipline in `using-superRA`

**Status:** IMPLEMENTED

### Key Findings

**`using-superRA` is now the agent-runtime design home.** A new `## Handoff Doc Discipline` section sits directly after §Universal Principles and absorbs the everyday-editing essentials from handoff-doc: the four document principles, the inline-edit rule, the 5-bullet stale-content checklist, the User Decisions Log format (including the `ask-user-question-logger` hook reminder), the `## Project Conventions` pointer, the figure-embedding pointer, and a `§When You Need the Full Anatomy` subsection pointing at `handoff-doc/references/plan-anatomy.md` and `results-anatomy.md` for doc-creators. Every subagent loads `using-superRA` via frontmatter; the editing rules are now always available without loading a second skill.

**`handoff-doc` is now a doc-creation skill, 30 lines long.** Shrank from 118 lines. What remains: frontmatter rewritten to point at `using-superRA` §Handoff Doc Discipline for everyday rules; body carries only (a) the two-stage RESULTS.md lifecycle paragraph, (b) §References listing plan-anatomy.md / results-anatomy.md and what each template contains, (c) §How This Skill Is Used describing the three call sites (standalone authors, `planning-workflow` Phase 2, Stage 2 doc-writer in `integration-workflow` Step 3). The top-line rerouting paragraph explicitly states that "every agent already loads `using-superRA`, so the everyday editing rules are always available without loading this one."

**Main-agent-autonomy contract extracted into a reference.** New file `using-superRA/references/main-agent-autonomy.md` generalizes what used to live in `execution-workflow` §Autonomy and Stop Points so the contract applies at every workflow phase (planning, execution, integration, merge, semantic-merge), not just execution. Carries §The Three Pause Classes (hard blocker / decision-beyond-authority / user-defined milestone), §Proceed Without Asking, §Banned Phrasings ("Should I proceed?" etc.), §One Question at a Time, §Log Before You Act. Top-of-file blockquote: "Loaded by the main agent at session start. Subagents inherit autonomy from their dispatch boundary; they do not load this file." The session-bootstrap reference was updated with a new final section `## After Bootstrap: Load the Autonomy Contract` hooking the load into the main agent's session-start sequence.

**Manifest refactored around a new column-header rule.** Added a bold note above the Stage table: "The 'Required skills' column lists what loads *in addition to* `superRA:using-superRA` — the master skill every agent already loads at dispatch time." Dropped `handoff-doc` from five rows (`implementation`, `refactoring`, `drift-test`, `integration-review`, `merge`); kept it on `documentation` and `planning-review` where agents create or mature docs from scratch. Added a closing paragraph below the table confirming the new rule and pointing at §Handoff Doc Discipline for everyday editing.

**Agent files drop the handoff-doc dependency for typical work.** `agents/implementer.md` and `agents/reviewer.md` step 1 rewrote to direct agents at `using-superRA` §Handoff Doc Discipline for the rules and to explicitly state "Load `superRA:handoff-doc` **only** if your task is creating a new `PLAN.md` / `RESULTS.md` from scratch or maturing Stage 1 RESULTS.md into Stage 2 — both rare for [implementer|reviewer] work." The implementer's §Handoff — Unified Across Stages pointer at `superRA:handoff-doc` was also updated to `superRA:using-superRA` §Handoff Doc Discipline.

**Workflow skills carry no principle restatements.** `execution-workflow` §Autonomy and Stop Points shrank from ~23 lines to 8 — the autonomy contract body moved into `main-agent-autonomy.md`; what's left is a 3-bullet list of execution-workflow-specific stop points (Step 4 completion menu / hard blockers from domain signals / methodology-authority boundary decisions) plugged into the autonomy contract's three pause classes. `semantic-merge` and `integration-workflow` pointers at `CLAUDE.md workflow principle #4` (invisible at runtime — CLAUDE.md is contributor-only) were rewritten to `superRA:using-superRA` §Universal Principles (principle #4) + `references/main-agent-autonomy.md` for the full contract. All 11 instances of `per handoff-doc §User Decisions Log` across `execution-workflow`, `integration-workflow`, `merge-workflow`, `semantic-merge`, `agent-orchestration`, `refactor-and-integrate/references/drift-test-quality.md`, and `refactor-and-integrate/references/merge-quality.md` were swept to the new canonical home `per using-superRA §Handoff Doc Discipline §User Decisions Log`. (Task 7 follows up with further collapse of duplicate prose around these pointers — Task 6 just updated the pointer target.)

**Inventory tables reflect the new handoff-doc scoping.** `using-superRA §Skill Inventory`, `skills/CATEGORIES.md` Utility table, and `README.md` Utility table all rewrote the `handoff-doc` row description to reflect the doc-creation scoping and to name the call sites (`planning-workflow` Phase 2, `integration-workflow` Step 3 doc-writer). Each row points at `using-superRA` §Handoff Doc Discipline as the home for everyday editing rules.

### Validation

End-to-end grep checks:
- `handoff-doc. §User Decisions Log` across `skills/` — zero matches.
- `CLAUDE.md workflow principle #4` across `skills/` and `agents/` — zero matches (the pointer moved to `using-superRA` §Universal Principles).
- `Should I proceed|Want me to continue|Ready for the next task` — matches only in `main-agent-autonomy.md` (where they're banned) and in `session-bootstrap.md`'s sample question phrasing (intentional — the bootstrap prompt asks the user explicitly).

End-to-end re-reads:
- `using-superRA/SKILL.md` flows as the central design contract: Universal Principles → Handoff Doc Discipline → Skill Inventory → Composable Design → Skill-Load Manifest → Execution Modes → When to Invoke Which Skill → Semantic Merge → Agent Teams → Reviewer–Orchestrator Dynamic → User Instructions → Instruction Priority.
- `handoff-doc/SKILL.md` reads as a doc-creation skill — the lede reroutes everyday rules to using-superRA; the body is only the two-stage lifecycle, the anatomy references, and the three call sites.
- `agents/implementer.md` / `agents/reviewer.md` step 1 both point at `using-superRA` §Handoff Doc Discipline and explicitly name when `superRA:handoff-doc` should still be loaded (doc creation from scratch / Stage 2 maturation — both rare).
- The manifest's column-header rule makes the new scoping explicit; the `implementation` / `refactoring` / `drift-test` / `integration-review` / `merge` rows no longer list `handoff-doc`.

---

## Task 7: Stop restating User Decisions Log discipline

**Status:** IMPLEMENTED

### Key Findings

**Task 6 left the pointer targets swept; Task 7 collapsed the surrounding prose.** All 11 `per handoff-doc §User Decisions Log` pointers were rewritten to `per using-superRA §Handoff Doc Discipline §User Decisions Log` in Task 6. What remained after Task 6 was the restated *prose around* those pointers — format reminders, location enumerations, and the `ask-user-question-logger` hook-reminder sentence. Eight sites carried restatement:

- `execution-workflow:220` — Step 4 completion menu: hook reminder + the `> **User decision (YYYY-MM-DD):** chose Option N (<name>)` format line were both stripped; the pointer now states where the log lands (`## Decisions`, before executing the choice, first commit of whatever workflow dispatches) without duplicating §User Decisions Log's format template.
- `execution-workflow:247` — "Escalate to the researcher" bullet: the "(task-scoped blockquote or `## Decisions` section per …)" location enumeration stripped.
- `execution-workflow:273/277` — §Autonomy and Stop Points bullet list: the Step 4 bullet lost its trailing "stop and `AskUserQuestion`; log per …" tail because the closing summary line at 277 already covers logging for all three bullets uniformly. Bullets now focus on *what the stop is about*; the summary covers *how to log*.
- `integration-workflow:121, 242, 330` — three pointers, each had a "log it in the top-level `## Decisions` section … per … hook will remind you" three-part restatement. All three are now one-liners with only the workflow-specific context preserved (before dispatching test-creator / doc-writer / disposition).
- `semantic-merge:278` — "Log every answer" paragraph: the hook reminder + format template were stripped; the branch-specific clause "If `PLAN.md` has already been disposed of, record the decision in the merge commit message instead — the commit message is the record of record once the doc is gone" was kept because it is a semantic-merge-only rule, not a restatement of the canonical discipline.
- `agent-orchestration:145` — "If you genuinely cannot tell whether the reviewer is right" point: the hook-reminder trailing sentence was removed; the "inside the relevant task's review-notes area" location context was kept as a parenthetical since the review-notes blockquote is a specific location §User Decisions Log does not enumerate.
- `using-superRA/references/main-agent-autonomy.md:51` — §Log Before You Act paragraph: the hook-reminder sentence was stripped; the paragraph now opens with the canonical pointer and closes with the one-line summary "The doc is the record; the chat message is the pointer."

**Validation grep.** `ask-user-question-logger` across `skills/`: one hit, at `using-superRA/SKILL.md:64` (the canonical sentence). Zero hits elsewhere — the hook-reminder text lives in exactly one place. `User Decisions Log` across `skills/`: every workflow-skill match is a pointer with at most narrow site-specific context; no match inlines the blockquote format template (lives only at `using-superRA/SKILL.md:56-60`).

### Notes on edits NOT made

`merge-workflow:213` (post-merge drift escalation), `integration-workflow:382` (meaningful drift), `integration-workflow:414` (key-result confirmation "Always" bullet), `agent-orchestration:150/151` (orchestrator limits bullets) — these were all already one-line pointers after Task 6 and did not carry restatement prose. Not touched. `integration-workflow:16` (§Autonomy opening paragraph) — the pointer there is a single summary sentence that also names the companion §Universal-Principles reference for autonomy; it is a composite pointer, not a restatement. Not touched.

---

## Task 8: Step 0b — explicit handoff to `planning-workflow`

**Status:** IMPLEMENTED

### Key Findings

**`skills/execution-workflow/SKILL.md` Step 0b** now halts and invokes `superRA:planning-workflow` when the existence check fails, instead of inlining a bootstrap procedure. Old body (3 paragraphs: "Before any task dispatch" / "Step 0 ... Task 0 cannot silently land" / "If the docs exist, are tracked ...") → new body (2 paragraphs: the halt-and-invoke instruction + the revised Step-0 cross-reference that no longer uses "Task 0" framing). The inline "satisfy the domain-specific planning gate (for data analysis: the Data Inventory hard gate ...)" wording is gone — that work happens inside planning-workflow's Phase 1 now, not inline here.

**`skills/planning-workflow/SKILL.md` Overview** gains a second paragraph acknowledging the invocation path from execution-workflow Step 0b: "May be invoked from `execution-workflow` Step 0b when an existing branch lacks committed `PLAN.md` / `RESULTS.md` (or carries uncommitted edits to them). The bootstrap path is identical to a fresh start — run the full Phase 1 / Phase 2 / Self-Review, satisfy any domain-specific planning gate, commit the docs, and hand control back. No shortcut." The wording "no shortcut" closes the design question — there is no lightweight bootstrap mode, just the normal planning flow.

**Validation:** `grep "Task 0\b" skills/execution-workflow/SKILL.md` returns zero matches after the edit. Both skills re-read end-to-end flow cleanly — execution-workflow's failure branch becomes a one-sentence halt, and planning-workflow's overview reads as a natural entry point whether arrived-at fresh or invoked via execution-workflow.

---

## Task 9: Move project doc audit into integration Stage 2

**Status:** IMPLEMENTED

### Key Findings

**New `## Project Doc Audit` section in `skills/refactor-and-integrate/references/codebase-integration.md`** carries the walk-up rules (diff-reachable CLAUDE.md / AGENTS.md / README.md plus always-check repo-root pair), the update-stale-claims / add-new-patterns / no-duplication / missing-pair-creation bullets, the "don't propagate upward" caveat, and a closing sentence naming Stage 2 ownership (refactorer applies; integration reviewer verifies) and carving RESULTS.md out to Step 3.

**`integration-workflow` Stage 2 dispatches updated:**
- Integration-reviewer dispatch `Additionally:` now says "this stage also covers the project doc audit per `codebase-integration.md` §Project Doc Audit (walk-up CLAUDE.md / AGENTS.md / README.md reachable from the diff)".
- Refactorer dispatch carries the same sub-bullet.
- Neither dispatch expands the checklist — the loaded reference carries it.

**`integration-workflow` Step 3 reshaped:**
- Sub-part B entirely removed (the doc audit bullet block, its `git commit -m "update project docs for <analysis>"` block, the "both sub-parts commit" framing).
- Doc-writer dispatch `Task:` trimmed from "Stage 2 RESULTS.md maturation + project doc audit" to "Stage 2 RESULTS.md maturation".
- Doc-writer dispatch `Additionally:` drops the A/B two-sub-part instruction; now reads "this dispatch matures RESULTS.md in place and relocates it to ${RESULTS_DIR} per final-form.md."
- Doc-reviewer dispatch `Task:` trimmed from "review of matured Stage 2 RESULTS.md + audited project docs" to "review of matured Stage 2 RESULTS.md".
- Doc-reviewer scope: 3-item list collapsed to 2 items (fact-check + cross-consistency), with cross-consistency pointing at Stage 2's responsibility for upstream stale-claim catches.
- Process diagram node "B: audit CLAUDE.md / AGENTS.md / README.md" and both of its edges removed; A now flows directly into doc-reviewer.
- Description-frontmatter and Core principle + intro paragraphs rewritten to name Stage 2 as the project-doc audit owner.
- Red Flags "Never" / "Always" bullets rewritten to drop "sub-parts A and B" framing and replace "+ project docs" with "+ project-doc audit" as a Stage 2 qualifier.
- Agent Loads paragraph rewritten to "Step 3 sub-part A is performed by the doc-writer; project-doc audit is covered by Stage 2".
- Agent Teams Mode paragraph trimmed to "sub-part A — the RESULTS.md maturation".

**`results-anatomy.md` §Transition to Stage 2** paragraph: the sentence "The same doc-writer pass also audits project-level docs (`CLAUDE.md` / `AGENTS.md` / `README.md`) for stale claims against the analysis diff." replaced with "Project-level docs (`CLAUDE.md` / `AGENTS.md` / `README.md`) are audited separately during `integration-workflow` Stage 2 refactor + integration review per `refactor-and-integrate/references/codebase-integration.md` §Project Doc Audit."

**Downstream sweep caught three more sites beyond the plan's list:**
- `skills/report-in-markdown/SKILL.md` load-map row `| integration-workflow Step 3 doc-writer subagent (maturing RESULTS.md + project doc audit) | ...` — trimmed to `maturing RESULTS.md`.
- `skills/report-in-markdown/references/final-form.md` §Project documentation accuracy was the doc-reviewer's project-doc checklist (now stale since Stage 2 owns that gate). Replaced with §Cross-consistency with project docs — a tighter checklist that keeps the RESULTS.md-vs-project-docs consistency check and names Stage 2 as the primary project-doc gate, with a stale-claim flag-but-not-block fallback.
- `agents/implementer.md:37` and `agents/reviewer.md:44, 49` — the parenthetical "see `integration-workflow` Step 3 sub-part B" pointers updated to name the new location: "audited before merge in `integration-workflow` Stage 2 per `refactor-and-integrate/references/codebase-integration.md` §Project Doc Audit" (walk-up pointers) and "the Stage 2 project-doc audit (`codebase-integration.md` §Project Doc Audit)" (the reviewer's failure-mode reminder).

**Validation:** grep sweep for "sub-part B" — zero hits in skill bodies or agent files; only PLAN.md-history and RELEASE-NOTES matches remain (expected). Grep for `project doc audit` / `Project Doc Audit` — every remaining hit either is the new §Project Doc Audit section header or a pointer at it. End-to-end re-read of `integration-workflow` Stage 2 + Step 3: the handoff is coherent — refactorer+integration-reviewer audit docs; doc-writer matures RESULTS.md; disposition goes to PLAN.md.

---

## Task 10: Subdivide RESULTS.md maturation into ordered commits

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 11: Skip post-merge integration review on Tier 1 clean merges

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 12: Clarify `semantic-merge` standalone vs delegated

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 13: Distribute `verification-before-completion` + delete the skill

**Status:** IMPLEMENTED

### Key Findings

**Skill folder deleted:** `skills/verification-before-completion/SKILL.md` (143 lines) removed via `git rm -r`.

**Distribution of unique content:**

- **`agents/implementer.md` §Self-Review Before Reporting** — added the 5-step Gate Function (IDENTIFY → RUN → READ → VERIFY → claim) as a new opening subsection, followed by the bottom-line one-liner "Run the command, read the output, then claim the result." Preserved the existing Completeness / Reproducibility / Domain §Review checks beneath it.
- **`agents/implementer.md` §Pre-Commit Self-Check** — appended a red-flag wording block ("should", "probably", "seems to", "Great!", "Done!", "Perfect!") at the end of the checklist, instructing the implementer to stop and verify if any of those words show up without fresh verification evidence.
- **`agents/reviewer.md` §Verify Claims Independently** — prepended a "DO NOT take the implementer's word" paragraph with the new diff-vs-status-return framing ("check the git diff, not just the status return — agents can report 'success' for partial work").
- **`agents/reviewer.md` §Pre-Commit Self-Check** — appended the same red-flag wording block as the implementer, scoped to the reviewer's verdict instead of the commit claim.
- **`skills/refactor-and-integrate/references/drift-test-quality.md`** — added a new `## Red-Green Verification` section between Robustness and Test Format, carrying the Write → Green → Revert → Red → Restore → Green cycle with the rationale "a drift test that passes once is not verified — it might always pass."
- **`skills/execution-workflow/SKILL.md` Step 3 preamble** — inserted a bold one-sentence reminder: "Run every check. Don't trust 'looks committed' — execute `git status` and read the output. The five checks below are the orchestrator's verification gate: evidence before claims, no shortcuts."

**Reference sweep results (grep `verification-before-completion` across `skills/`, `agents/`, `README.md`, `CLAUDE.md`):** zero matches. Also cleaned:
- `skills/using-superRA/SKILL.md` §Skill Inventory — row removed.
- `skills/CATEGORIES.md` Utility table — row removed.
- `README.md` Utility table — row removed.
- `skills/writing-skills/SKILL.md:401` — updated "TDD, verification-before-completion, designing-before-coding" to "TDD, designing-before-coding".

**Intentionally not touched:**
- `PLAN.md` (this refactor plan) and `RESULTS.md` (this dev log) retain references as historical record of the refactor.
- `docs/plans/2025-11-28-skills-improvements-from-user-feedback.md` is an archived prior plan document, not current inventory.

**Note on §Skill Types.** PLAN.md Step 7 anticipated removing the skill from a §Skill Types "Rigid" example list in `using-superRA`. That section does not currently exist in `using-superRA/SKILL.md` (removed in the pre-plan commit `956f6cc` which stripped EXTREMELY-IMPORTANT / Red Flags / Skill Types sections). The `writing-skills` Discipline-Enforcing example list was the only remaining "types-like" enumeration — updated as documented above.

---

## Task 14: Consolidate worktree skills (drop `using-analysis-worktrees`)

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 15: Remove deprecated commands

**Status:** IMPLEMENTED

### Key Findings

**Files deleted (3):**
- `commands/brainstorm.md` — stub pointing at `superpowers:brainstorming`.
- `commands/execute-plan.md` — stub pointing at `superpowers:executing-plans`.
- `commands/write-plan.md` — stub pointing at `superpowers:writing-plans`.

The `commands/` directory is now empty and git treats it as removed (no tracked files remain in it).

**Grep sweep (`execute-plan|write-plan|brainstorm` across `skills/`, `commands/`, `README.md`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `CATEGORIES.md`, `agents/`, `hooks/`):** zero matches after the deletion. No inventory-table rows or skill-body references to clean up — the stubs were referenced only by the plugin runtime's command discovery, not by any skill body or README table.

**Intentionally not touched:**
- `RELEASE-NOTES.md` and `CHANGELOG.md` carry upstream superpowers release history mentioning these commands (lines documenting their introduction, deprecation, and removal in prior upstream versions). These are historical release records, not current inventory, so they stay. superRA's own release-note entry for this refactor lands in Task 16 Step 4.

**Task-1 overlap check:** grep surfaced no references inside any of Task 1's files (`skills/using-superRA/SKILL.md`, the 4 workflow skills, `skills/semantic-merge/SKILL.md`, `skills/refactor-and-integrate/SKILL.md`, `agents/implementer.md`, `agents/reviewer.md`). No deferred edits for Task 1 to absorb.

### Notes
The PLAN's Step 2 mentioned "Remove the 'Deprecated — use superpowers:* instead' rows from any inventory tables (likely in README.md or CHANGELOG)." None existed in superRA's README or anywhere under skill / agent / command files — the stubs self-describe their deprecation in their own frontmatter only. Clean deletion.

---

## Task 16: Final consistency pass

**Status:** *(not started)*

### Key Findings
*(to be populated)*

---

## Task 17: Document agent-reuse vs fresh-dispatch heuristic in agent-orchestration

**Status:** IMPLEMENTED

### Key Findings

**New subsection in `skills/agent-orchestration/SKILL.md`.** `## Agent reuse vs fresh dispatch` placed between `## Decision Framework` and `## Dispatch Templates`. The two sections answer orthogonal questions: Decision Framework picks the dispatch *pattern* (parallel / teams / relay); the new section picks agent *identity* within a chosen pattern (reuse a warm agent via `SendMessage` vs spawn fresh vs bundle several small tasks into one dispatch). No content overlap with the existing parallel/teams/relay table.

**Six labeled paragraphs** (bolded lead-ins, so an orchestrator can skim): Context-reload cost (names the specific loads a fresh dispatch re-pays: `using-superRA`, active domain skill, module-level `CLAUDE.md` / `AGENTS.md` / `README.md` walk-up); Criteria favoring reuse (small scope + same domain context + non-overlapping file set + sequential build-on-previous — all four should hold); Criteria favoring fresh dispatch (any one of: new scope, different domain vertical, file-set overlap with in-flight work, warm agent cannot provide the needed perspective); Bundling as a third option (multi-task brief in a single implementer dispatch, amortizes one context load across several tiny tasks); Reviewer-always-fresh rule; `SendMessage` mechanic pointer.

**Reviewer-always-fresh rule is hard, not soft.** Anchored to `superRA:using-superRA` §Reviewer–Orchestrator Dynamic and the plugin `CLAUDE.md` Workflow principle #1. Rationale in the subsection: the adversarial-review property collapses the moment the reviewer has already committed to a line of thinking about the code — warm-agent review is equivalent to self-review and voids the implementer–reviewer pair. The rule overrides every other reuse criterion; if it is a review pass, dispatch fresh.

**Cross-reference in `skills/execution-workflow/SKILL.md`.** Single line appended to §Per-Task Execution Steps step 1 (the dispatch-implementer step — where the reuse decision actually fires): "See `superRA:agent-orchestration` §Agent reuse vs fresh dispatch for when to reuse a warm implementer via `SendMessage` versus spawning a fresh dispatch." No heuristic content duplicated; pointer only.

### Validation

End-to-end re-read of `agent-orchestration/SKILL.md`: new subsection slots between §Decision Framework (ends with the rule-of-thumb paragraph) and §Dispatch Templates (opens with the canonical-shape intro) without disrupting the existing flow. Covers the orthogonal axis of agent-identity selection that §Decision Framework does not address. No duplication with the parallel/teams/relay table.

End-to-end re-read of `execution-workflow/SKILL.md` §Per-Task Execution Steps: the one-line pointer lands on step 1 (implementer dispatch) and does not step on steps 2–4 (NEEDS_CONTEXT / BLOCKED handling, reviewer dispatch — which by the new hard rule is always fresh, and final APPROVE handoff). The pointer is additive, not conflicting.

No skill-description frontmatter changed — triggering checks not needed for this task.

### Notes

**Concurrency with Task 6.** At dispatch time the orchestrator flagged that another implementer was running Task 6, which edits `skills/execution-workflow/SKILL.md` in multiple places. `git diff` on my target file before commit showed only my single-line addition to step 1 of §Per-Task Execution Steps — no overlap with Task 6's in-flight edits. `skills/agent-orchestration/SKILL.md` was untouched by any other in-flight work.

**Does not subsume the Decision Framework.** The new section does not replace or compete with §Decision Framework; the two compose. An orchestrator first picks the dispatch pattern (parallel / teams / relay / single), then asks the reuse-vs-fresh question within that pattern.
