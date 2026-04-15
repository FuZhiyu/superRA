# Superpowers Release Notes

## Unreleased — econ-data-analysis restructured around describe-analyze-validate (DAV); dispatch-prompt protocol standardized; §Review & Self-Check Discipline shared between implementer and reviewer

Three structural refactors land together.

**§Review & Self-Check Discipline integrated into `econ-data-analysis/SKILL.md` main body.** A new `## Review & Self-Check Discipline — shared gating for implementer and reviewer` section sits directly after Validate and before Pitfalls. It is the **single source of truth** that both the implementer (as pre-handoff self-check) and the reviewer (as verification criteria) walk — no parallel checklist lives elsewhere, and no separate `implementation-review.md` / `integration-review.md` reference files exist (the shared-gating decision; logged in `PLAN.md §Decisions` 2026-04-15). Every item carries an inline severity marker: `[GATING]` (load-bearing non-negotiable; failure blocks unconditional APPROVE), `[STANDARD]` (required; missed items become REVISE findings), or `[ADVISORY]` (best-practice; reviewer MAY flag as MINOR). The section is organized into six sub-sections: Gating (Iron Law applied per step), Implementation standards, Validation completeness, Documentation and handoff, Refactor integrity (applies at `refactoring` / `integration review` stages), and Completion verification (applies at `execution-workflow` Step 3). The prior `## Verification Checklist` collapses to a one-line pointer back to the new section.

**CONDITIONAL APPROVE verdict protocol.** The reviewer walks the **entire** §Review section top to bottom even when a `[GATING]` item fails — halting early forces a full re-review on the next pass, and reviewer dispatches are costly (logged rationale in `PLAN.md §Decisions` 2026-04-15). Three verdicts: `APPROVE` (no findings), `REVISE` (only `[STANDARD]` items failed), and `CONDITIONAL APPROVE` (one or more `[GATING]` items failed; reviewer walked the downstream items anyway and they look correct conditional on the gating fix not invalidating them). On a re-dispatch following CONDITIONAL APPROVE, the reviewer's second pass is narrow — verify the gating fix plus the cited downstream items still hold — and promotes to unconditional APPROVE when both pass.

**Dispatch-prompt protocol standardized across all workflow skills.** Every `Agent(subagent_type: "superRA:implementer"|"superRA:reviewer")` dispatch template in `skills/` — across `execution-workflow`, `integration-workflow`, `merge-workflow`, `semantic-merge`, and the illustrative examples in `refactor-and-integrate` — now opens with the canonical prefix "Follow the standard stage-relevant workflow and load relevant skills and documents to proceed. Additionally, …". The prefix tells the dispatched agent that its standard Before-You-Start + stage-reference-auto-load (per `agents/implementer.md` / `agents/reviewer.md`) is in effect; the text after `Additionally,` is task-specific steering only (focus area, prior-round adjudication notes, warnings, non-default skill/reference overrides). Dispatch prompts never re-state the standard protocol, never paraphrase PLAN.md content, and never repeat domain-skill checklist items the agent walks on its own.

As part of the same sweep, legacy over-specification is removed from every dispatch template: `Work from:` lines are dropped (subagents run in the orchestrator's cwd by default), and `Counterpart:` lines are dropped outside the explicit Agent Teams subsections (teammate pairing is set at team-spawn time via `agent-orchestration` team recipes, not inside the per-task dispatch). The previous `Note:` free-form fields in `merge-workflow` and `semantic-merge` Tier 3 are folded into the `Additionally:` tail so all steering flows through one channel.

`tests/structural-invariants.sh` now adds four new assertions for the §Review integration on top of the two dispatch-prefix assertions: `## Review & Self-Check Discipline` heading exists in `econ-data-analysis/SKILL.md`; `[GATING]` marker count ≥ 8; `CONDITIONAL APPROVE` verdict string present; no `implementation-review.md` / `integration-review.md` reference file exists under `skills/econ-data-analysis/references/` (shared-gating decision sanity check). Existing prefix-coverage and no-`Work from:`/`Counterpart:` assertions continue to pass. All assertions green on this commit.

**econ-data-analysis restructured around describe-analyze-validate (DAV).** Replaces the two competing organizers in `econ-data-analysis/SKILL.md` (the "Three Concurrent Principles" section and the "Describe-Analyze-Doc" cycle) with a single three-concurrent-disciplines structure: **Describe**, **Analyze**, **Validate**. The old DAD framing was misleading because its "DOC" phase bundled three unrelated activities — re-describing the post-transformation output, validating against priors, and writing documentation. Under DAV, post-transformation describe is explicitly the second application of the same Describe discipline (fed into Validate §Sanity checks), validation is a first-class discipline in its own right, and documentation is called out as a **cross-cutting writing practice** that runs continuously, not a fourth phase.

**Validate is elevated.** It now carries four sub-sections: Sanity checks (row count vs. expectation, distribution shift, economic sense, PLAN.md expectations), Multi-source validation (scale / property / relationship / reference — Principle 3's content), Missing-data as signal (interpretation of systematic missingness; operational how-to stays in Pitfalls), and **Sensitivity analysis** — a new first-class execution-side discipline covering how to run a sensitivity check, what counts as "robust enough" (economic reasoning, not mechanical pass/fail), and when to escalate divergence to the researcher via `AskUserQuestion`. Planning-side sensitivity design still lives in `references/planning.md`; the menu in `references/data-robustness-checklist.md`.

**Row-count tracking is now stated once** as a MANDATORY rule under Analyze, with pointers elsewhere. Panel-structure and variable-diagnostics content appears once under Describe. The Iron Law, Common Rationalizations, Red Flags, and the operation-specific Pitfalls checklists are preserved. Verification Checklist renamed DESCRIBE/ANALYZE/DOC → DESCRIBE/ANALYZE/VALIDATE.

**Propagation.** `agents/implementer.md`, `agents/reviewer.md`, `skills/CATEGORIES.md`, `skills/semantic-merge/SKILL.md`, `skills/refactor-and-integrate/references/codebase-integration.md`, `skills/execution-workflow/SKILL.md`, `skills/using-superRA/SKILL.md`, `skills/econ-data-analysis/references/planning.md`, `skills/econ-data-analysis/references/integrate-drift-tests.md`, `skills/planning-workflow/SKILL.md`, `skills/planning-workflow/references/plan-template.md`, `skills/handoff-doc/references/plan-anatomy.md`, and `README.md` all updated. `planning-workflow` step-granularity example collapses from four steps (describe/analyze/validate/doc) to three (describe/analyze/validate), with document-and-commit bundled into the Validate step. `plan-template.md` Step 3 retitled from "Doc — verify, update handoff docs, and commit" to "Validate — verify the result, document, and commit".

**Drift tests updated.** `tests/structural-invariants.sh` swaps the old Principle 1 assertion for `## Describe` / `## Analyze` / `## Validate` section checks, adds a `### Sensitivity analysis` sub-section assertion, and adds a grep guard that fails if DAD / describe-analyze-doc creeps back into the SKILL.md body.

## Workflow principles elevated over data-analysis framing; skills categorized; plan-mode integration (2026-04-14)

Refactor that repositions superRA as a domain-agnostic workflow plugin with data analysis as the flagship vertical — opening the architecture to future verticals (theory, literature review, simulation, writing) without reshaping the workflow skills. Four phased commits.

**Skill categorization.** New `skills/CATEGORIES.md` groups the skills into **Workflow** (procedural, domain-agnostic), **Domain** (vertical-specific; today only `econ-data-analysis`), **Utility** (reusable, domain-neutral tools), and **Meta** (session bootstrap, skill authoring). The flat `skills/<name>/SKILL.md` layout is preserved — nesting would break harness skill loaders. `README.md` Skills section is re-sorted to match the grouping.

**planning-workflow is now domain-agnostic.** The Phase 1 Data Inventory hard gate and Sensitivity Analysis Design moved into a new `econ-data-analysis/references/planning.md`; `planning-workflow` now has a generic Phase 1 "Domain Vertical Setup" that routes to the active domain skill's planning reference. Living-plan and RESULTS.md mechanics deduplicate against `handoff-doc` via pointers instead of restating the rules. Sections that were "data analysis" are now "data analysis example" callouts in `plan-template.md`, so future verticals can swap the vertical-specific header sections cleanly.

**econ-data-analysis gains two stage-scoped references** while the main body stays thorough. The guiding rule: cross-cutting content (Iron Law, Principles 1–3, describe-analyze-doc, pitfalls, Red Flags, rationalization list) stays in the main `SKILL.md` body so the agent has it at every dispatch. Only stage-scoped content moves to references: `references/planning.md` (Data Inventory gate + sensitivity design, planning-only) and `references/integrate-drift-tests.md` (what to protect, econ-specific tolerance conventions, data-analysis failure modes — integrate-only). The integrate reference points at `refactor-and-integrate/references/drift-test-quality.md` for the quality checklist rather than duplicating it.

**CLAUDE.md / AGENTS.md rewritten.** The four Workflow Principles are now the primary Design Principles section, labeled "(load-bearing across all domains)". RA framing stays as a cross-cutting one-liner. Iron Law is demoted into a new **Domain verticals** subsection that frames data analysis as the flagship vertical with Iron Law as its load-bearing domain rule. A new **Roadmap: Extending Beyond Data Analysis** section lists the four planned verticals and the checklist to add one.

**README.md reframed.** "Why superRA?" leads with the four workflow principles; Iron Law moves to a data-analysis-vertical aside. "How It Works" diagram is domain-agnostic with inline "(data analysis: ...)" glosses. Philosophy is split into workflow discipline + data-analysis vertical + cross-vertical. New Roadmap section mirrors CLAUDE.md.

**using-superRA gains a Workflow Principles section.** The orchestrator now internalizes all four principles at session start instead of waiting for a workflow skill to surface them. A companion "Domain Verticals" section routes data-analysis tasks to `econ-data-analysis` with the stage-scoped references listed.

**Plan-mode integration.** New `execution-workflow` **Step 0b** checks that `PLAN.md` and `RESULTS.md` exist and are committed before any task dispatch — if not, it bootstraps them as Task 0 (using `planning-workflow` and `handoff-doc`) before proceeding. A new PostToolUse hook **`exit-plan-mode`** fires after `ExitPlanMode` and reminds the agent that the plan still needs to be materialized into committed `PLAN.md` + `RESULTS.md` before any implementation, closing the gap between CLI plan-mode and the superRA handoff-doc discipline. Hook is registered in both `hooks.json` (Claude Code) and `hooks-cursor.json` (Cursor).

**Agent stage-aware references.** `agents/implementer.md` and `agents/reviewer.md` now name the specific stage-scoped reference each role should load on top of the main `econ-data-analysis` SKILL.md body — planning stage loads `references/planning.md`, integrate stage (drift tests) loads `references/integrate-drift-tests.md`, and analysis-task / data-integrity / implementation reviewers rely on the main body. "Do not load every reference at every dispatch" is the new discipline.

**Files touched.** New files: `skills/CATEGORIES.md`, `skills/econ-data-analysis/references/planning.md`, `skills/econ-data-analysis/references/integrate-drift-tests.md`, `hooks/exit-plan-mode`, `tests/structural-invariants.sh` (plugin-level drift-test analogue). Modified: `skills/planning-workflow/SKILL.md` (stripped), `skills/planning-workflow/references/plan-template.md` (domain-agnostic callouts), `skills/econ-data-analysis/SKILL.md` (load-map header), `skills/execution-workflow/SKILL.md` (Step 0b), `skills/integration-workflow/SKILL.md` (Stage 1 dispatches name both drift-test references), `skills/using-superRA/SKILL.md` (workflow principles + verticals section; Skill Types example updated), `agents/implementer.md` / `agents/reviewer.md` (stage-aware refs), `hooks/hooks.json` / `hooks/hooks-cursor.json` (register exit-plan-mode), `CLAUDE.md` (new structure; `AGENTS.md` is a symlink), `README.md` (re-sorted + new Roadmap + hook rows; deduplicated Meta table).

**No behavior change for existing data-analysis workflows.** The Data Inventory hard gate still runs — it's just reached through a different path (domain skill reference instead of inlined in `planning-workflow`). All existing `superRA:<name>` invocations continue to resolve.

## integration-workflow Step 3 consolidation: one doc-writer + doc-reviewer pair (2026-04-11)

Merges the previous Step 3 (mature RESULTS.md) and Step 4 (dispose of PLAN.md) into a single **Step 3: Documentation Finalization** and moves the consolidation work off the orchestrator onto a dispatched **doc-writer subagent** gated by a **doc-reviewer subagent**. Previously Step 3 was orchestrator-performed with only a reviewer dispatch — a reviewer-only gate, not a full implementer-reviewer pair. Workflow principle P1 (enforced implementer-reviewer pair at every step) now holds literally at Step 3.

**The consolidated step has three sub-parts:**

- **Sub-part A (doc-writer):** mature `RESULTS.md` in place per `superRA:report-in-markdown` full mode (all three references — `baseline-io.md` + `rich-content.md` + `final-form.md`), relocate to `RESULTS_DIR`.
- **Sub-part B (doc-writer, same dispatch):** audit project-level docs. Walk up from every file in the analysis diff to each `CLAUDE.md` / `AGENTS.md` / `README.md` (plus the repo root `README.md` and root `CLAUDE.md` unconditionally). Update stale claims, add new patterns/modules, create missing `CLAUDE.md` + `AGENTS.md` symlink pairs for new module directories. This closes the long-standing gap that the macro workflow never had a project-docs update step — it's now baked into the doc-writer pass, not bolted on.
- **Sub-part C (orchestrator, after doc-reviewer APPROVE):** PLAN.md disposition via `AskUserQuestion`, logged in `PLAN.md` `## Decisions`. Stays with the orchestrator because it is a user-facing decision, not an RA-implementable task.

**One reviewer dispatch** gates both A and B together, which lets it catch cross-consistency issues (matured RESULTS.md vs. any README/CLAUDE.md that mentions the analysis). The reviewer loads `superRA:report-in-markdown` + `final-form.md` only, per the skill's load-map for the doc-reviewer role.

**The orchestrator preamble** still owns the RESULTS_DIR resolution — reads project guidance first, asks via `AskUserQuestion` only if guidance is missing. This runs before the doc-writer dispatch so the subagent receives `RESULTS_DIR` as a parameter rather than having to decide it.

**Files touched.** `skills/integration-workflow/SKILL.md` — rewrite of Step 3 (replaces previous Step 3 + Step 4), new process-diagram cluster, updated Agent Types table (two new rows: doc-writer and doc-reviewer; drop the "orchestrator performs the consolidation" note), updated Agent Teams Mode (Step 3 can join the team as a two-teammate sub-graph), updated Red Flags (new "do not orchestrator-perform sub-parts A and B" rule and new "do not delegate sub-part C to the doc-writer" rule), description picks up "update project docs" trigger. `skills/handoff-doc/references/results-anatomy.md` — "Transition to Stage 2" paragraph updated to state the doc-writer subagent performs the consolidation. `skills/report-in-markdown/SKILL.md` — load-map rows renamed to "Step 3 doc-writer subagent" and "Step 3 doc-reviewer subagent". `skills/report-in-markdown/references/final-form.md` — header and severity-section language updated to name the doc-writer / doc-reviewer roles explicitly. `README.md` — integration-workflow row rewritten to describe the doc-writer + doc-reviewer pair; design principle #3 picks up "documentation finalization" instead of "work-journal report"; `report-in-markdown` row updated to name the two Step 3 callers.

This commit closes the follow-up gap flagged at the bottom of the previous entry ("Out of this rollout") — the external work-journal plugin dependency is now fully gone, and the P1 gap at Step 3 that the previous entry left open is now closed.

## RESULTS.md two-stage lifecycle + report-in-markdown utility skill (2026-04-11)

`RESULTS_UPDATE.md` is renamed to `RESULTS.md` everywhere, and is now treated as a single-identity artifact that **matures across two stages** rather than a disposable scaffold paired with a separately-generated work-journal entry. The `_UPDATE` suffix was misleading: `handoff-doc` already enforced "latest state only, no history" on the file, so the suffix implied append semantics that the discipline forbade.

**The two-stage lifecycle.** Stage 1 is the worktree-root dev log written during IMPLEMENT — task-indexed, mirrors `PLAN.md`, agent-facing, terse. Stage 2 is the permanent record produced at `integration-workflow` Step 3 — the same file is consolidated in place (fact-checked against committed code/output, restructured for reader flow, figures materialized into a new `attachments/` folder, frontmatter added), then relocated from the worktree root to the analysis's permanent code folder per project guidance, and committed as part of the integration commit. Same file name, same identity across stages. The matured `RESULTS.md` **is** the work journal — there is no longer a separate work-journal entry to generate.

**New utility skill: `report-in-markdown`.** A new format-discipline skill at `skills/report-in-markdown/` carries the markdown-report rules that the rename creates a need for. The design principle is **lean SKILL.md body, rich references**: every caller pays the context cost of the body, so the body stays under 80 lines with a load-map table that points each caller (implementer, integration reviewer, integration consolidator, standalone) at exactly the references they need. The references are `baseline-io.md` (frontmatter, paths, git metadata; loaded only for permanent artifacts), `rich-content.md` (figures, LaTeX math, tables, file references; loaded by any caller with embedded content), and `final-form.md` (Stage 2 consolidation discipline including the fact-check checklist ported from the external `work-journal` plugin's `report-checker` role; loaded only by the consolidator and the integration reviewer). Stage 1 implementers writing text-only task sections load nothing beyond the lean body; Stage 1 reviewers (data integrity, implementation correctness) load nothing beyond the body either, because their job is data correctness, not presentation polish.

**Files touched in this rollout.** `feat(report-in-markdown)`: new skill (4 files, 319 lines). `refactor(handoff-doc)`: rename `references/results-update-anatomy.md` → `results-anatomy.md`, rewrite to describe the two-stage lifecycle, delegate figure/math/table rules to `rich-content.md`, point at `final-form.md` for Stage 2 consolidation. Update `SKILL.md` to reflect the new file name and lifecycle. `refactor(downstream rename)`: propagate `RESULTS_UPDATE.md` → `RESULTS.md` across `planning-workflow`, `execution-workflow`, `merge-workflow`, `semantic-merge`, `agent-orchestration`, `using-superRA`, `agents/implementer.md`, `agents/reviewer.md`, and the `results-update-template.md` → `results-template.md` rename. The implementer protocol picks up a one-line note directing it to load `report-in-markdown` + `rich-content.md` only when the task section embeds figures, math, or tables. `docs`: skill count goes from 17 to 18 in `README.md`, `report-in-markdown` joins the INTEGRATE-phase skill table, and `CLAUDE.md` principle #2 picks up the rename in passing.

**Out of this rollout.** `integration-workflow` Step 3 currently inlines the work-journal report spec (frontmatter, figure handling, fact-check). Replacing that inline spec with an explicit `report-in-markdown` invocation is the largest single rewrite of the rollout and lands in a follow-up commit alongside the disposition-step updates that say "the matured `RESULTS.md` is committed and stays in place" rather than "PLAN.md and RESULTS_UPDATE.md are disposed of via `git mv`/`git rm`." After that lands, superRA's integration flow no longer depends on the external `work-journal` plugin; the consolidation is owned end-to-end by `report-in-markdown`'s `final-form.md` reference.

**Project-side note.** The rule that Stage 2 `RESULTS.md` lands "in the analysis's relevant code folder" is deliberately project-specific and lives in each project's `CLAUDE.md`/`AGENTS.md`, not in any superRA skill. superRA reads project guidance for the destination; it does not impose a default. Projects without explicit guidance fall back to a reasonable per-skill default (`./scratch/` for standalone reports, the analysis script's containing folder for `RESULTS.md`).

## Fourth design principle: autonomous with human in the loop (2026-04-11)

A fourth workflow principle now joins the three codified in the earlier skills fix pass. It governs when the agent should drive forward on its own versus stop and consult the researcher, and closes the gap where user decisions made in chat never made it back into `PLAN.md`.

**Principle:** the agent proceeds autonomously between legitimate stop points — no "should I continue?" check-ins on an approved plan, no re-confirmation after an `APPROVED` task, no reassurance-seeking between workflow steps. It stops for exactly three classes of pause: hard blockers, decisions beyond the RA's authority (methodology, research intent, scope, sample/variable definition, any tradeoff that depends on the research question), and user-defined workflow milestones (e.g., execution-workflow's completion menu). At every stop point it uses the `AskUserQuestion` tool when the harness exposes it, plain text otherwise. Every user decision produced at a stop point is written into `PLAN.md` (or `RESULTS_UPDATE.md` when relevant) **before** the agent acts on it, and committed atomically with the work it unblocks — so the handoff doc remains the record of record and the researcher's judgment calls survive into every future session.

This commit only adds the principle statement to `CLAUDE.md` (§Workflow principles, now four items) and `README.md` (§Design Principles). Follow-up commits will integrate the principle into `handoff-doc` (new "User Decisions Log" format), `execution-workflow` (restructured "Autonomy and Stop Points" section), `integration-workflow` / `merge-workflow` / `semantic-merge` (AskUserQuestion migration at existing stop points), a new `PostToolUse` hook that reminds the agent to log decisions into `PLAN.md` after each `AskUserQuestion` call, and a grep-sweep cleanup of remaining "escalate to human partner" phrasing across `skills/` and `agents/`.

## superRA skills fix pass (2026-04-11)

Post-audit fix pass addressing findings from a four-reviewer panel that evaluated the 17 skills against the `writing-skills` rubric. Thirteen focused commits; skill count unchanged (still 17). No new skills, no deletions — this pass tightens behavior that was already in place.

**CSO description rewrites (9 skills):** the frontmatter descriptions on `planning-workflow`, `execution-workflow`, `integration-workflow`, `merge-workflow`, `semantic-merge`, `agent-orchestration`, `implementer-protocol`, `reviewer-protocol`, and `econ-data-analysis` previously summarized each skill's internal workflow ("dispatches subagent per task", "classifies conflicts via tier classification", "creates drift tests"). That is the anti-pattern `writing-skills` warns about: when a description summarizes workflow, future Claude shortcuts to the description and skips the skill body. Descriptions are now rich with concrete triggering conditions — symptoms, keywords, phrasings, state signals like "branch with APPROVED plan but no code yet" — and carry no process-summary verbs. `writing-skills`'s own description is deliberately left alone for now.

**`execution-workflow` preserve-and-annotate orchestrator discipline:** the "Known gap" flagged in the 2026-04-11 handoff-doc entry below (which landed earlier the same day) is now closed. `execution-workflow/SKILL.md:128` and `:286` previously told the orchestrator to "clear the review notes" before re-dispatching the implementer, which wiped the blockquote the implementer was supposed to annotate with `→ implemented: ...` markers. The orchestrator now adjudicates in place by appending `→ orchestrator: rejected <reason>` / `→ orchestrator: <second opinion requested> <reason>` annotations and rewriting task steps in place for accepted items. The implementer then annotates with `→ implemented: ...`, and the reviewer deletes confirmed-fixed items on re-review. `integration-workflow`, `merge-workflow`, and `semantic-merge` inherit the new discipline by cross-reference.

**Protocol skills now do explicit `Read` instead of Glob-hunt:** `implementer-protocol/SKILL.md` and `reviewer-protocol/SKILL.md` bodies used to tell the caller to find the agent file via `Glob`. They now say `Read agents/<role>.md at the plugin base directory` (which the runtime announces when the skill loads), resolving deterministically with no hunt. The descriptions are also rewritten to triggering-conditions form.

**`handoff-doc` ownership matrix removed; new Principle 6 added:** the "Ownership at a Glance" table in `handoff-doc/SKILL.md` duplicated role-ownership content whose authoritative home is `agents/implementer.md` and `agents/reviewer.md`. It is gone. Principle 4 now explicitly points at the agent files for role ownership. In its place, a new Principle 6 ("The doc is the record. Status reports are pointers, not substitutes.") codifies that all material findings must be written into PLAN.md / RESULTS_UPDATE.md before being reported in chat — with matching pre-commit self-check bullets added to both agent files. handoff-doc is now "six principles"; all downstream references (README, agent files, planning-workflow, results-update-template) were updated.

**`planning-workflow` Red Flags:** the Phase 1 data-inventory hard gate was enforced by prose but had no rationalization-blocking table like the other workflow skills. A new "Red Flags — Hard Gate Protection" section now closes the loopholes of speculative drafts, verbal inventories, parallel Phase 1/Phase 2 work, and "TBD sources" task steps.

**`econ-data-analysis` post-merge re-validation Red Flag:** added two bullets to the Red Flags list covering "assume a merge/rebase/refactor preserves analysis results without re-running describe" and "accept merged code without comparing pre- and post-change row counts and summary statistics."

**Drift-test integrity anchored in one place:** the "don't silently update test expectations", "don't proceed past failing tests", "don't remove tests during refactoring" rules previously appeared in three workflow skills in slightly-drifting wording. They are now stated canonically in `skills/refactor-and-integrate/references/drift-test-quality.md` under "Drift Test Integrity — Cross-Cutting Red Flags", and `integration-workflow`, `merge-workflow`, and `semantic-merge` point at the canonical section.

**`semantic-merge` ↔ `merge-workflow` invocation contract clarified:** the relationship was previously ambiguous — merge-workflow said "internally invokes semantic-merge" in one place and "Invoke superRA:semantic-merge" in another, which read as either automatic or explicit. The contract is now explicit on both sides: merge-workflow Step 1 delegates to `superRA:semantic-merge` via a real Skill invocation, and semantic-merge carries an "Invocation Pattern" section describing both standalone and delegated call sites.

**"Preserve" terminology dropped from `codebase-integration.md`:** the refactoring checklist previously said "describe steps preserved", "row count logging preserved", "validation checks preserved". "Preserve" is ambiguous — an agent can read it as either "don't delete these artifacts" or "these artifacts are fine as-is, no re-run needed". The checklist is rewritten in precise action verbs: "re-run", "re-execute", "present AND re-validated". The section is retitled "Data Discipline Through Refactoring."

**Infrastructure-skill discoverability:** `using-analysis-worktrees` and `worktree-data-sync` were only cross-referenced from `execution-workflow`. They now have discovery pointers from `planning-workflow` (at plan-creation time, when the worktree decision is cheapest), `execution-workflow` (worktree-data-sync added to required-skills), and `agent-orchestration` (new "Infrastructure for Parallel Work" subsection). `using-analysis-worktrees` also carries a new decision table spelling out optional vs recommended vs mandatory for various setup scenarios.

**Three workflow design principles added to `CLAUDE.md` + `README.md`:** the plugin's tested philosophy is now stated explicitly and is the criterion against which future changes are evaluated:
1. **Enforced implementer–reviewer pair at every step** — no result accepted without reviewer sign-off.
2. **Handoff docs are the auditable record AND the continuation point** — all material findings land in committed PLAN.md / RESULTS_UPDATE.md before any status report; any fresh agent can resume from docs + git state alone.
3. **Fast early, strict before merge. Semantic merges always** — analysis code is written for speed during IMPLEMENT; refactor/integration happen only at INTEGRATE; every merge into main runs through semantic-merge.

`CLAUDE.md` carries the full version plus the foundational discipline (RA framing, Iron Law) and the architectural pattern (lean agents, rich references), and states explicitly that every proposed change must be evaluated against the principles. `README.md` carries a shorter public-facing summary.

## superRA handoff-doc discipline (2026-04-11)

Extracted the document-level discipline for `PLAN.md`, `RESULTS_UPDATE.md`, and any other task-block-structured handoff document into a new utility skill, and consolidated the role-specific review-loop protocol into the two agent prototype files.

Skill count: **16 → 17**.

**New utility skill:**
- `handoff-doc` — canonical source for the five handoff-doc principles (latest-state-only no history, live-and-committed inline-edit, task-block structure, ownership by role, what-changed deltas in both directions), the ownership matrix at a glance, the inline-edit rule, the stale-content checklist, and the figure embedding rule. *(Since updated in the fix pass above: a sixth principle "doc is the record" was added, and the ownership matrix was removed in favor of pointers to `agents/implementer.md` and `agents/reviewer.md`.)* Progressive-reveal references: `references/plan-anatomy.md` (full PLAN.md template with header and task blocks) and `references/results-update-anatomy.md` (full findings template). Loaded by implementer and reviewer subagents; referenced by `planning-workflow`. Also usable standalone by a single author writing handoff docs without subagents — the ownership matrix collapses and the author plays all roles.

**Review-loop mechanics moved into the agent files:**
- `agents/implementer.md` now carries a "Handoff — Unified Across Stages" section with an explicit "What You Own, What You Don't" ownership block and a "How You Fix Review Items on a REVISE Round" protocol that codifies the `→ implemented: <file:line + fix>` annotation pattern. The implementer may append annotations but never deletes review items, never rewrites reviewer prose, never touches `→ orchestrator: ...` notes, and never edits task objectives/I/O or other tasks.
- `agents/reviewer.md` adds a parallel "What You Own, What You Don't" block and restructures the handoff into "How You Write a Review" with explicit first-review and re-review sub-protocols. On re-review, confirmed-fixed items are deleted directly from the blockquote (no "resolved" markers, no strikethroughs); the blockquote is removed entirely when empty, and `**Review status:** APPROVED` is set.
- Delete authority: reviewer and orchestrator both hold it, implementer never does. CRITICAL-severity items cannot be silently overridden.

**What-changed deltas in both directions:**
- Because handoff docs show latest state only, readers cannot infer what changed by reading the doc alone. The skill codifies that dispatch prompts carry a one-line "what changed since last dispatch" delta and that subagent status returns carry a `**Doc edits:**` line describing the specific sections/fields modified. Status returns are navigation aids pointing at the doc, not content dumps.

**Planning-workflow updates:**
- `skills/planning-workflow/SKILL.md` Living Plan section shortened to a brief pointer at `superRA:handoff-doc` as the canonical discipline source. No behavioral change — the rules already lived there implicitly.
- `skills/planning-workflow/references/results-update-template.md` trimmed to a minimal starter scaffold with a pointer at the full anatomy in `handoff-doc/references/results-update-anatomy.md`. Figures must now be embedded with markdown image syntax `![caption](results_attachments/fig_name.png)` — consistent with handoff-doc's figure embedding rule.

**Progressive reveal:**
- `handoff-doc/SKILL.md` is concise (~100 lines): principles, ownership at a glance, inline-edit rule, stale checklist, figure rule. Deeper material lives in `references/`. Subagent-specific execution protocol (annotation rules, status-line format, pre-commit self-checks) lives in the agent files, not in the skill — the skill defines document-level discipline usable standalone, while each agent file carries its own view of the review loop.

**Workflow skills unchanged in this commit.** `execution-workflow`, `integration-workflow`, and `merge-workflow` were deliberately left untouched. The handoff-doc skill and the agent prototype files are additive: agents load `superRA:handoff-doc` via `Skill` before touching PLAN.md or RESULTS_UPDATE.md, so the new document-level discipline is in force for every dispatched subagent without any workflow skill needing to intermediate.

**Known gap (resolved in the follow-up fix pass, same date):** when this entry originally landed, `execution-workflow/SKILL.md` still prescribed the old orchestrator behavior of clearing review notes from PLAN.md before re-dispatch, which contradicted the new preserve-and-annotate protocol defined here. That gap was closed in the subsequent "skills fix pass" entry below — execution-workflow now preserves the blockquote across rounds and adjudicates in place with `→ orchestrator:` annotations.

## superRA workflow/utility restructure (2026-04-10)

Major structural refactor of the superRA skill namespace. Skills now split into two clear categories: **workflow skills** (dispatcher-facing, suffix `-workflow`) and **utility skills** (agent-facing, standalone-invokable). Eliminates invocation collisions, removes content duplication between skills and their references files, and makes domain knowledge (drift test standards, codebase integration checklists, merge quality rules) reusable outside the workflows that originally carried them.

Skill count: **18 → 16**.

**New workflow skills (4):**
- `planning-workflow` — PLAN phase. Phase 1 data inventory hard gate + Phase 2 plan creation. Replaces `analysis-planning` + `data-exploration`.
- `execution-workflow` — IMPLEMENT + VALIDATE phases. Per-task dispatch with two-stage review, orchestrator-discipline filter on reviewer feedback, end-of-workflow reproducibility verification, and the 4-option completion menu. Replaces `executing-analysis`, absorbs reproducibility checks and option menu from `finishing-analysis`.
- `integration-workflow` — INTEGRATE step 1 of 2. Drift test creation, refactor-review loop, work-journal report generation, and PLAN.md / RESULTS_UPDATE.md disposition. Replaces `pre-merge-gate` workflow part and absorbs Steps 4b/4c of `finishing-analysis`.
- `merge-workflow` — INTEGRATE step 2 of 2. Main update via semantic-merge, **post-merge verification running BOTH drift tests AND a fresh integration review**, refactor-review loop on either failure, local merge or PR push, worktree cleanup. Replaces `finishing-analysis` Steps 4d + 5.

**New utility skill:**
- `refactor-and-integrate` — Standalone-invokable utility bundling the three integration-phase domain references (`drift-test-quality.md`, `codebase-integration.md`, `merge-quality.md`). Loaded by dispatched `implementer`/`reviewer` agents for drift test creation, drift test review, refactoring, integration review, merge proposing, and merge review. Reference files moved from `pre-merge-gate/references/` and `semantic-merge/references/`.

**Deleted skills (7):**
- `analysis-planning` → renamed to `planning-workflow`
- `data-exploration` → folded into `planning-workflow` as Phase 1 with the existing `<HARD-GATE>` enforcement
- `executing-analysis` → renamed to `execution-workflow`
- `pre-merge-gate` → split into `integration-workflow` (workflow) + `refactor-and-integrate` (references)
- `finishing-analysis` → split three ways: reproducibility + option menu into `execution-workflow`, drift tests + refactor + report + dev doc handling into `integration-workflow`, main update + merge/PR + cleanup into `merge-workflow`
- `requesting-analysis-review` → redundant with `execution-workflow`'s built-in two-stage review plus ad-hoc `Agent(reviewer)` invocation
- `receiving-code-review` → general SWE discipline that doesn't belong in a research plugin. The useful core (verify before forwarding, push back with reasoning, override with documented rationale) is now codified in `execution-workflow`'s **Handling Reviewer Feedback (Orchestrator Discipline)** section, applied to subagent reviewers where it is load-bearing.

**Agent definition consolidation:**
- `agents/implementer.md` and `agents/reviewer.md` now own the report format, default handoff, stage-specific handoff matrix, document-update discipline (scope rule + inline-edit rule), and conditional skill auto-load. Dispatch templates pass only `Stage:`, task pointer, `Skills:`, domain reference basename, and git SHA range — no more duplicated handoff instructions in every dispatch prompt.

**New: pointer-based dispatch convention:**
- Dispatch templates name a parent skill in the `Skills:` line and the domain reference by basename. The agent loads the parent skill via the Skill tool, reads the runtime-announced base directory, and resolves `<base_dir>/references/<basename>`. No more inline absolute paths or repo-relative paths in dispatch prompts.

**New: orchestrator discipline for reviewer feedback:**
- `execution-workflow` adds a "Handling Reviewer Feedback" section that codifies the SWE filter for dispatched reviewers. The orchestrator (main agent) reads each cited issue, classifies as real bug / pedantic / wrong / methodology disagreement, can override with documented reasoning, must escalate CRITICAL to the human partner, and cannot silently ignore feedback. The same discipline is referenced by `integration-workflow` and `merge-workflow`.

**Breaking changes for users:**
- Invocations of `superRA:analysis-planning`, `superRA:executing-analysis`, `superRA:data-exploration`, `superRA:pre-merge-gate`, `superRA:finishing-analysis`, `superRA:requesting-analysis-review`, `superRA:receiving-code-review` will no longer resolve. Update to the new workflow skill names above.
- PLAN.md templates at `skills/analysis-planning/references/` moved to `skills/planning-workflow/references/`.
- Agent dispatch prompts using the old-style inline handoff instructions will still work (the agents ignore redundant fields), but the pointer-based convention is recommended for new code.

## v5.0.7 (2026-03-31)

### GitHub Copilot CLI Support

- **SessionStart context injection** — Copilot CLI v1.0.11 added support for `additionalContext` in sessionStart hook output. The session-start hook now detects the `COPILOT_CLI` environment variable and emits the SDK-standard `{ "additionalContext": "..." }` format, giving Copilot CLI users the full superpowers bootstrap at session start. (Original fix by @culinablaz in PR #910)
- **Tool mapping** — added `references/copilot-tools.md` with the full Claude Code to Copilot CLI tool equivalence table
- **Skill and README updates** — added Copilot CLI to the `using-superpowers` skill's platform instructions and README installation section

### OpenCode Fixes

- **Skills path consistency** — the bootstrap text no longer advertises a misleading `configDir/skills/superpowers/` path that didn't match the runtime path. The agent should use the native `skill` tool, not navigate to files by path. Tests now use consistent paths derived from a single source of truth. (#847, #916)
- **Bootstrap as user message** — moved bootstrap injection from `experimental.chat.system.transform` to `experimental.chat.messages.transform`, prepending to the first user message instead of adding a system message. Avoids token bloat from system messages repeated every turn (#750) and fixes compatibility with Qwen and other models that break on multiple system messages (#894).

## v5.0.6 (2026-03-24)

### Inline Self-Review Replaces Subagent Review Loops

The subagent review loop (dispatching a fresh agent to review plans/specs) doubled execution time (~25 min overhead) without measurably improving plan quality. Regression testing across 5 versions with 5 trials each showed identical quality scores regardless of whether the review loop ran.

- **brainstorming** — replaced Spec Review Loop (subagent dispatch + 3-iteration cap) with inline Spec Self-Review checklist: placeholder scan, internal consistency, scope check, ambiguity check
- **writing-plans** — replaced Plan Review Loop (subagent dispatch + 3-iteration cap) with inline Self-Review checklist: spec coverage, placeholder scan, type consistency
- **writing-plans** — added explicit "No Placeholders" section defining plan failures (TBD, vague descriptions, undefined references, "similar to Task N")
- Self-review catches 3-5 real bugs per run in ~30s instead of ~25 min, with comparable defect rates to the subagent approach

### Brainstorm Server

- **Session directory restructured** — the brainstorm server session directory now contains two peer subdirectories: `content/` (HTML files served to the browser) and `state/` (events, server-info, pid, log). Previously, server state and user interaction data were stored alongside served content, making them accessible over HTTP. The `screen_dir` and `state_dir` paths are both included in the server-started JSON. (Reported by 吉田仁)

### Bug Fixes

- **Owner-PID lifecycle fixes** — the brainstorm server's owner-PID monitoring had two bugs causing false shutdowns within 60 seconds: (1) EPERM from cross-user PIDs (Tailscale SSH, etc.) was treated as "process dead", and (2) on WSL the grandparent PID resolves to a short-lived subprocess that exits before the first lifecycle check. Fixed by treating EPERM as "alive" and validating the owner PID at startup — if it's already dead, monitoring is disabled and the server relies on the 30-minute idle timeout. This also removes the Windows/MSYS2-specific carve-out from `start-server.sh` since the server now handles it generically. (#879)
- **writing-skills** — corrected false claim that SKILL.md frontmatter supports "only two fields"; now says "two required fields" and links to the agentskills.io specification for all supported fields (PR #882 by @arittr)

### Codex App Compatibility

- **codex-tools** — added named agent dispatch mapping documenting how to translate Claude Code's named agent types to Codex's `spawn_agent` with worker roles (PR #647 by @arittr)
- **codex-tools** — added environment detection and Codex App finishing sections for worktree-aware skills (by @arittr)
- **Design spec** — added Codex App compatibility design spec (PRI-823) covering read-only environment detection, worktree-safe skill behavior, and sandbox fallback patterns (by @arittr)

## v5.0.5 (2026-03-17)

### Bug Fixes

- **Brainstorm server ESM fix** — renamed `server.js` → `server.cjs` so the brainstorming server starts correctly on Node.js 22+ where the root `package.json` `"type": "module"` caused `require()` to fail. (PR #784 by @sarbojitrana, fixes #774, #780, #783)
- **Brainstorm owner-PID on Windows** — skip PID lifecycle monitoring on Windows/MSYS2 where the PID namespace is invisible to Node.js, preventing the server from self-terminating after 60 seconds. (#770, docs from PR #768 by @lucasyhzlu-debug)
- **stop-server.sh reliability** — verify the server process actually died before reporting success. SIGTERM + 2s wait + SIGKILL fallback. (#723)

### Changed

- **Execution handoff** — restore user choice between subagent-driven and inline execution after plan writing. Subagent-driven is recommended but no longer mandatory.

## v5.0.4 (2026-03-16)

### Review Loop Refinements

Dramatically reduces token usage and speeds up spec and plan reviews by eliminating unnecessary review passes and tightening reviewer focus.

- **Single whole-plan review** — plan reviewer now reviews the complete plan in one pass instead of chunk-by-chunk. Removed all chunk-related concepts (`## Chunk N:` headings, 1000-line chunk limits, per-chunk dispatch).
- **Raised the bar for blocking issues** — both spec and plan reviewer prompts now include a "Calibration" section: only flag issues that would cause real problems during implementation. Minor wording, stylistic preferences, and formatting quibbles should not block approval.
- **Reduced max review iterations** — from 5 to 3 for both spec and plan review loops. If the reviewer is calibrated correctly, 3 rounds is plenty.
- **Streamlined reviewer checklists** — spec reviewer trimmed from 7 categories to 5; plan reviewer from 7 to 4. Removed formatting-focused checks (task syntax, chunk size) in favor of substance (buildability, spec alignment).

### OpenCode

- **One-line plugin install** — OpenCode plugin now auto-registers the skills directory via a `config` hook. No symlinks or `skills.paths` config needed. Install is just adding one line to `opencode.json`. (PR #753)
- **Added `package.json`** so OpenCode can install superpowers as an npm package from git.

### Bug Fixes

- **Verify server actually stopped** — `stop-server.sh` now confirms the process is dead before reporting success. SIGTERM + 2s wait + SIGKILL fallback. Reports failure if the process survives. (PR #751)
- **Generic agent language** — brainstorm companion waiting page now says "the agent" instead of "Claude".

## v5.0.3 (2026-03-15)

### Cursor Support

- **Cursor hooks** — added `hooks/hooks-cursor.json` with Cursor's camelCase format (`sessionStart`, `version: 1`) and updated `.cursor-plugin/plugin.json` to reference it. Fixed platform detection in `session-start` to check `CURSOR_PLUGIN_ROOT` first (Cursor may also set `CLAUDE_PLUGIN_ROOT`). (Based on PR #709)

### Bug Fixes

- **Stop firing SessionStart hook on `--resume`** — the startup hook was re-injecting context on resumed sessions, which already have the context in their conversation history. The hook now fires only on `startup`, `clear`, and `compact`.
- **Bash 5.3+ hook hang** — replaced heredoc (`cat <<EOF`) with `printf` in `hooks/session-start`. Fixes indefinite hang on macOS with Homebrew bash 5.3+ caused by a bash regression with large variable expansion in heredocs. (#572, #571)
- **POSIX-safe hook script** — replaced `${BASH_SOURCE[0]:-$0}` with `$0` in `hooks/session-start`. Fixes "Bad substitution" error on Ubuntu/Debian where `/bin/sh` is dash. (#553)
- **Portable shebangs** — replaced `#!/bin/bash` with `#!/usr/bin/env bash` in all shell scripts. Fixes execution on NixOS, FreeBSD, and macOS with Homebrew bash where `/bin/bash` is outdated or missing. (#700)
- **Brainstorm server on Windows** — auto-detect Windows/Git Bash (`OSTYPE=msys*`, `MSYSTEM`) and switch to foreground mode, fixing silent server failure caused by `nohup`/`disown` process reaping. (#737)
- **Codex docs fix** — replaced deprecated `collab` flag with `multi_agent` in Codex documentation. (PR #749)

## v5.0.2 (2026-03-11)

### Zero-Dependency Brainstorm Server

**Removed all vendored node_modules — server.js is now fully self-contained**

- Replaced Express/Chokidar/WebSocket dependencies with zero-dependency Node.js server using built-in `http`, `fs`, and `crypto` modules
- Removed ~1,200 lines of vendored `node_modules/`, `package.json`, and `package-lock.json`
- Custom WebSocket protocol implementation (RFC 6455 framing, ping/pong, proper close handshake)
- Native `fs.watch()` file watching replaces Chokidar
- Full test suite: HTTP serving, WebSocket protocol, file watching, and integration tests

### Brainstorm Server Reliability

- **Auto-exit after 30 minutes idle** — server shuts down when no clients are connected, preventing orphaned processes
- **Owner process tracking** — server monitors the parent harness PID and exits when the owning session dies
- **Liveness check** — skill verifies server is responsive before reusing an existing instance
- **Encoding fix** — proper `<meta charset="utf-8">` on served HTML pages

### Subagent Context Isolation

- All delegation skills (brainstorming, dispatching-parallel-agents, requesting-code-review, subagent-driven-development, writing-plans) now include context isolation principle
- Subagents receive only the context they need, preventing context window pollution

## v5.0.1 (2026-03-10)

### Agentskills Compliance

**Brainstorm-server moved into skill directory**

- Moved `lib/brainstorm-server/` → `skills/brainstorming/scripts/` per the [agentskills.io](https://agentskills.io) specification
- All `${CLAUDE_PLUGIN_ROOT}/lib/brainstorm-server/` references replaced with relative `scripts/` paths
- Skills are now fully portable across platforms — no platform-specific env vars needed to locate scripts
- `lib/` directory removed (was the last remaining content)

### New Features

**Gemini CLI extension**

- Native Gemini CLI extension support via `gemini-extension.json` and `GEMINI.md` at repo root
- `GEMINI.md` @imports `using-superpowers` skill and tool mapping table at session start
- Gemini CLI tool mapping reference (`skills/using-superpowers/references/gemini-tools.md`) — translates Claude Code tool names (Read, Write, Edit, Bash, etc.) to Gemini CLI equivalents (read_file, write_file, replace, etc.)
- Documents Gemini CLI limitations: no subagent support, skills fall back to `executing-plans`
- Extension root at repo root for cross-platform compatibility (avoids Windows symlink issues)
- Install instructions added to README

### Improvements

**Multi-platform brainstorm server launch**

- Per-platform launch instructions in visual-companion.md: Claude Code (default mode), Codex (auto-foreground via `CODEX_CI`), Gemini CLI (`--foreground` with `is_background`), and fallback for other environments
- Server now writes startup JSON to `$SCREEN_DIR/.server-info` so agents can find the URL and port even when stdout is hidden by background execution

**Brainstorm server dependencies bundled**

- `node_modules` vendored into the repo so the brainstorm server works immediately on fresh plugin installs without requiring `npm` at runtime
- Removed `fsevents` from bundled deps (macOS-only native binary; chokidar falls back gracefully without it)
- Fallback auto-install via `npm install` if `node_modules` is missing

**OpenCode tool mapping fix**

- `TodoWrite` → `todowrite` (was incorrectly mapped to `update_plan`); verified against OpenCode source

### Bug Fixes

**Windows/Linux: single quotes break SessionStart hook** (#577, #529, #644, PR #585)

- Single quotes around `${CLAUDE_PLUGIN_ROOT}` in hooks.json fail on Windows (cmd.exe doesn't recognize single quotes as path delimiters) and on Linux (single quotes prevent variable expansion)
- Fix: replaced single quotes with escaped double quotes — works across macOS bash, Windows cmd.exe, Windows Git Bash, and Linux, with and without spaces in paths
- Verified on Windows 11 (NT 10.0.26200.0) with Claude Code 2.1.72 and Git for Windows

**Brainstorming spec review loop skipped** (#677)

- The spec review loop (dispatch spec-document-reviewer subagent, iterate until approved) existed in the prose "After the Design" section but was missing from the checklist and process flow diagram
- Since agents follow the diagram and checklist more reliably than prose, the spec review step was being skipped entirely
- Added step 7 (spec review loop) to the checklist and corresponding nodes to the dot graph
- Tested with `claude --plugin-dir` and `claude-session-driver`: worker now correctly dispatches the reviewer

**Cursor install command** (PR #676)

- Fixed Cursor install command in README: `/plugin-add` → `/add-plugin` (confirmed via Cursor 2.5 release announcement)

**User review gate in brainstorming** (#565)

- Added explicit user review step between spec completion and writing-plans handoff
- User must approve the spec before implementation planning begins
- Checklist, process flow, and prose updated with the new gate

**Session-start hook emits context only once per platform**

- Hook now detects whether it's running in Claude Code or another platform
- Emits `hookSpecificOutput` for Claude Code, `additional_context` for others — prevents double context injection

**Linting fix in token analysis script**

- `except:` → `except Exception:` in `tests/claude-code/analyze-token-usage.py`

### Maintenance

**Removed dead code**

- Deleted `lib/skills-core.js` and its test (`tests/opencode/test-skills-core.js`) — unused since February 2026
- Removed skills-core existence check from `tests/opencode/test-plugin-loading.sh`

### Community

- @karuturi — Claude Code official marketplace install instructions (PR #610)
- @mvanhorn — session-start hook dual-emit fix, OpenCode tool mapping fix
- @daniel-graham — linting fix for bare except
- PR #585 author — Windows/Linux hooks quoting fix

---

## v5.0.0 (2026-03-09)

### Breaking Changes

**Specs and plans directory restructured**

- Specs (brainstorming output) now save to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- Plans (writing-plans output) now save to `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- User preferences for spec/plan locations override these defaults
- All internal skill references, test files, and example paths updated to match
- Migration: move existing files from `docs/plans/` to new locations if desired

**Subagent-driven development mandatory on capable harnesses**

Writing-plans no longer offers a choice between subagent-driven and executing-plans. On harnesses with subagent support (Claude Code, Codex), subagent-driven-development is required. Executing-plans is reserved for harnesses without subagent capability, and now tells the user that Superpowers works better on a subagent-capable platform.

**Executing-plans no longer batches**

Removed the "execute 3 tasks then stop for review" pattern. Plans now execute continuously, stopping only for blockers.

**Slash commands deprecated**

`/brainstorm`, `/write-plan`, and `/execute-plan` now show deprecation notices pointing users to the corresponding skills. Commands will be removed in the next major release.

### New Features

**Visual brainstorming companion**

Optional browser-based companion for brainstorming sessions. When a topic would benefit from visuals, the brainstorming skill offers to show mockups, diagrams, comparisons, and other content in a browser window alongside terminal conversation.

- `lib/brainstorm-server/` — WebSocket server with browser helper library, session management scripts, and dark/light themed frame template ("Superpowers Brainstorming" with GitHub link)
- `skills/brainstorming/visual-companion.md` — Progressive disclosure guide for server workflow, screen authoring, and feedback collection
- Brainstorming skill adds a visual companion decision point to its process flow: after exploring project context, the skill evaluates whether upcoming questions involve visual content and offers the companion in its own message
- Per-question decision: even after accepting, each question is evaluated for whether browser or terminal is more appropriate
- Integration tests in `tests/brainstorm-server/`

**Document review system**

Automated review loops for spec and plan documents using subagent dispatch:

- `skills/brainstorming/spec-document-reviewer-prompt.md` — Reviewer checks completeness, consistency, architecture, and YAGNI
- `skills/writing-plans/plan-document-reviewer-prompt.md` — Reviewer checks spec alignment, task decomposition, file structure, and file size
- Brainstorming dispatches spec reviewer after writing the design doc
- Writing-plans includes chunk-based plan review loop after each section
- Review loops repeat until approved or escalate after 5 iterations
- End-to-end tests in `tests/claude-code/test-document-review-system.sh`
- Design spec and implementation plan in `docs/superpowers/`

**Architecture guidance across the skill pipeline**

Design-for-isolation and file-size-awareness guidance added to brainstorming, writing-plans, and subagent-driven-development:

- **Brainstorming** — New sections: "Design for isolation and clarity" (clear boundaries, well-defined interfaces, independently testable units) and "Working in existing codebases" (follow existing patterns, targeted improvements only)
- **Writing-plans** — New "File Structure" section: map out files and responsibilities before defining tasks. New "Scope Check" backstop: catch multi-subsystem specs that should have been decomposed during brainstorming
- **SDD implementer** — New "Code Organization" section (follow plan's file structure, report concerns about growing files) and "When You're in Over Your Head" escalation guidance
- **SDD code quality reviewer** — Now checks architecture, unit decomposition, plan conformance, and file growth
- **Spec/plan reviewers** — Architecture and file size added to review criteria
- **Scope assessment** — Brainstorming now assesses whether a project is too large for a single spec. Multi-subsystem requests are flagged early and decomposed into sub-projects, each with its own spec → plan → implementation cycle

**Subagent-driven development improvements**

- **Model selection** — Guidance for choosing model capability by task type: cheap models for mechanical implementation, standard for integration, capable for architecture and review
- **Implementer status protocol** — Subagents now report DONE, DONE_WITH_CONCERNS, BLOCKED, or NEEDS_CONTEXT. Controller handles each status appropriately: re-dispatching with more context, upgrading model capability, breaking tasks apart, or escalating to human

### Improvements

**Instruction priority hierarchy**

Added explicit priority ordering to using-superpowers:

1. User's explicit instructions (CLAUDE.md, AGENTS.md, direct requests) — highest priority
2. Superpowers skills — override default system behavior
3. Default system prompt — lowest priority

If CLAUDE.md or AGENTS.md says "don't use TDD" and a skill says "always use TDD," the user's instructions win.

**SUBAGENT-STOP gate**

Added `<SUBAGENT-STOP>` block to using-superpowers. Subagents dispatched for specific tasks now skip the skill instead of activating the 1% rule and invoking full skill workflows.

**Multi-platform improvements**

- Codex tool mapping moved to progressive disclosure reference file (`references/codex-tools.md`)
- Platform Adaptation pointer added so non-Claude-Code platforms can find tool equivalents
- Plan headers now address "agentic workers" instead of "Claude" specifically
- Collab feature requirement documented in `docs/README.codex.md`

**Writing-plans template updates**

- Plan steps now use checkbox syntax (`- [ ] **Step N:**`) for progress tracking
- Plan header references both subagent-driven-development and executing-plans with platform-aware routing

---

## v4.3.1 (2026-02-21)

### Added

**Cursor support**

Superpowers now works with Cursor's plugin system. Includes a `.cursor-plugin/plugin.json` manifest and Cursor-specific installation instructions in the README. The SessionStart hook output now includes an `additional_context` field alongside the existing `hookSpecificOutput.additionalContext` for Cursor hook compatibility.

### Fixed

**Windows: Restored polyglot wrapper for reliable hook execution (#518, #504, #491, #487, #466, #440)**

Claude Code's `.sh` auto-detection on Windows was prepending `bash` to the hook command, breaking execution. The fix:

- Renamed `session-start.sh` to `session-start` (extensionless) so auto-detection doesn't interfere
- Restored `run-hook.cmd` polyglot wrapper with multi-location bash discovery (standard Git for Windows paths, then PATH fallback)
- Exits silently if no bash is found rather than erroring
- On Unix, the wrapper runs the script directly via `exec bash`
- Uses POSIX-safe `dirname "$0"` path resolution (works on dash/sh, not just bash)

This fixes SessionStart failures on Windows with spaces in paths, missing WSL, `set -euo pipefail` fragility on MSYS, and backslash mangling.

## v4.3.0 (2026-02-12)

This fix should dramatically improve superpowers skills compliance and should reduce the chances of Claude entering its native plan mode unintentionally.

### Changed

**Brainstorming skill now enforces its workflow instead of describing it**

Models were skipping the design phase and jumping straight to implementation skills like frontend-design, or collapsing the entire brainstorming process into a single text block. The skill now uses hard gates, a mandatory checklist, and a graphviz process flow to enforce compliance:

- `<HARD-GATE>`: no implementation skills, code, or scaffolding until design is presented and user approves
- Explicit checklist (6 items) that must be created as tasks and completed in order
- Graphviz process flow with `writing-plans` as the only valid terminal state
- Anti-pattern callout for "this is too simple to need a design" — the exact rationalization models use to skip the process
- Design section sizing based on section complexity, not project complexity

**Using-superpowers workflow graph intercepts EnterPlanMode**

Added an `EnterPlanMode` intercept to the skill flow graph. When the model is about to enter Claude's native plan mode, it checks whether brainstorming has happened and routes through the brainstorming skill instead. Plan mode is never entered.

### Fixed

**SessionStart hook now runs synchronously**

Changed `async: true` to `async: false` in hooks.json. When async, the hook could fail to complete before the model's first turn, meaning using-superpowers instructions weren't in context for the first message.

## v4.2.0 (2026-02-05)

### Breaking Changes

**Codex: Replaced bootstrap CLI with native skill discovery**

The `superpowers-codex` bootstrap CLI, Windows `.cmd` wrapper, and related bootstrap content file have been removed. Codex now uses native skill discovery via `~/.agents/skills/superpowers/` symlink, so the old `use_skill`/`find_skills` CLI tools are no longer needed.

Installation is now just clone + symlink (documented in INSTALL.md). No Node.js dependency required. The old `~/.codex/skills/` path is deprecated.

### Fixes

**Windows: Fixed Claude Code 2.1.x hook execution (#331)**

Claude Code 2.1.x changed how hooks execute on Windows: it now auto-detects `.sh` files in commands and prepends `bash`. This broke the polyglot wrapper pattern because `bash "run-hook.cmd" session-start.sh` tries to execute the `.cmd` file as a bash script.

Fix: hooks.json now calls session-start.sh directly. Claude Code 2.1.x handles the bash invocation automatically. Also added .gitattributes to enforce LF line endings for shell scripts (fixes CRLF issues on Windows checkout).

**Windows: SessionStart hook runs async to prevent terminal freeze (#404, #413, #414, #419)**

The synchronous SessionStart hook blocked the TUI from entering raw mode on Windows, freezing all keyboard input. Running the hook async prevents the freeze while still injecting superpowers context.

**Windows: Fixed O(n^2) `escape_for_json` performance**

The character-by-character loop using `${input:$i:1}` was O(n^2) in bash due to substring copy overhead. On Windows Git Bash this took 60+ seconds. Replaced with bash parameter substitution (`${s//old/new}`) which runs each pattern as a single C-level pass — 7x faster on macOS, dramatically faster on Windows.

**Codex: Fixed Windows/PowerShell invocation (#285, #243)**

- Windows doesn't respect shebangs, so directly invoking the extensionless `superpowers-codex` script triggered an "Open with" dialog. All invocations now prefixed with `node`.
- Fixed `~/` path expansion on Windows — PowerShell doesn't expand `~` when passed as an argument to `node`. Changed to `$HOME` which expands correctly in both bash and PowerShell.

**Codex: Fixed path resolution in installer**

Used `fileURLToPath()` instead of manual URL pathname parsing to correctly handle paths with spaces and special characters on all platforms.

**Codex: Fixed stale skills path in writing-skills**

Updated `~/.codex/skills/` reference (deprecated) to `~/.agents/skills/` for native discovery.

### Improvements

**Worktree isolation now required before implementation**

Added `using-git-worktrees` as a required skill for both `subagent-driven-development` and `executing-plans`. Implementation workflows now explicitly require setting up an isolated worktree before starting work, preventing accidental work directly on main.

**Main branch protection softened to require explicit consent**

Instead of prohibiting main branch work entirely, the skills now allow it with explicit user consent. More flexible while still ensuring users are aware of the implications.

**Simplified installation verification**

Removed `/help` command check and specific slash command list from verification steps. Skills are primarily invoked by describing what you want to do, not by running specific commands.

**Codex: Clarified subagent tool mapping in bootstrap**

Improved documentation of how Codex tools map to Claude Code equivalents for subagent workflows.

### Tests

- Added worktree requirement test for subagent-driven-development
- Added main branch red flag warning test
- Fixed case sensitivity in skill recognition test assertions

---

## v4.1.1 (2026-01-23)

### Fixes

**OpenCode: Standardized on `plugins/` directory per official docs (#343)**

OpenCode's official documentation uses `~/.config/opencode/plugins/` (plural). Our docs previously used `plugin/` (singular). While OpenCode accepts both forms, we've standardized on the official convention to avoid confusion.

Changes:
- Renamed `.opencode/plugin/` to `.opencode/plugins/` in repo structure
- Updated all installation docs (INSTALL.md, README.opencode.md) across all platforms
- Updated test scripts to match

**OpenCode: Fixed symlink instructions (#339, #342)**

- Added explicit `rm` before `ln -s` (fixes "file already exists" errors on reinstall)
- Added missing skills symlink step that was absent from INSTALL.md
- Updated from deprecated `use_skill`/`find_skills` to native `skill` tool references

---

## v4.1.0 (2026-01-23)

### Breaking Changes

**OpenCode: Switched to native skills system**

Superpowers for OpenCode now uses OpenCode's native `skill` tool instead of custom `use_skill`/`find_skills` tools. This is a cleaner integration that works with OpenCode's built-in skill discovery.

**Migration required:** Skills must be symlinked to `~/.config/opencode/skills/superpowers/` (see updated installation docs).

### Fixes

**OpenCode: Fixed agent reset on session start (#226)**

The previous bootstrap injection method using `session.prompt({ noReply: true })` caused OpenCode to reset the selected agent to "build" on first message. Now uses `experimental.chat.system.transform` hook which modifies the system prompt directly without side effects.

**OpenCode: Fixed Windows installation (#232)**

- Removed dependency on `skills-core.js` (eliminates broken relative imports when file is copied instead of symlinked)
- Added comprehensive Windows installation docs for cmd.exe, PowerShell, and Git Bash
- Documented proper symlink vs junction usage for each platform

**Claude Code: Fixed Windows hook execution for Claude Code 2.1.x**

Claude Code 2.1.x changed how hooks execute on Windows: it now auto-detects `.sh` files in commands and prepends `bash `. This broke the polyglot wrapper pattern because `bash "run-hook.cmd" session-start.sh` tries to execute the .cmd file as a bash script.

Fix: hooks.json now calls session-start.sh directly. Claude Code 2.1.x handles the bash invocation automatically. Also added .gitattributes to enforce LF line endings for shell scripts (fixes CRLF issues on Windows checkout).

---

## v4.0.3 (2025-12-26)

### Improvements

**Strengthened using-superpowers skill for explicit skill requests**

Addressed a failure mode where Claude would skip invoking a skill even when the user explicitly requested it by name (e.g., "subagent-driven-development, please"). Claude would think "I know what that means" and start working directly instead of loading the skill.

Changes:
- Updated "The Rule" to say "Invoke relevant or requested skills" instead of "Check for skills" - emphasizing active invocation over passive checking
- Added "BEFORE any response or action" - the original wording only mentioned "response" but Claude would sometimes take action without responding first
- Added reassurance that invoking a wrong skill is okay - reduces hesitation
- Added new red flag: "I know what that means" → Knowing the concept ≠ using the skill

**Added explicit skill request tests**

New test suite in `tests/explicit-skill-requests/` that verifies Claude correctly invokes skills when users request them by name. Includes single-turn and multi-turn test scenarios.

## v4.0.2 (2025-12-23)

### Fixes

**Slash commands now user-only**

Added `disable-model-invocation: true` to all three slash commands (`/brainstorm`, `/execute-plan`, `/write-plan`). Claude can no longer invoke these commands via the Skill tool—they're restricted to manual user invocation only.

The underlying skills (`superpowers:brainstorming`, `superpowers:executing-plans`, `superpowers:writing-plans`) remain available for Claude to invoke autonomously. This change prevents confusion when Claude would invoke a command that just redirects to a skill anyway.

## v4.0.1 (2025-12-23)

### Fixes

**Clarified how to access skills in Claude Code**

Fixed a confusing pattern where Claude would invoke a skill via the Skill tool, then try to Read the skill file separately. The `using-superpowers` skill now explicitly states that the Skill tool loads skill content directly—no need to read files.

- Added "How to Access Skills" section to `using-superpowers`
- Changed "read the skill" → "invoke the skill" in instructions
- Updated slash commands to use fully qualified skill names (e.g., `superpowers:brainstorming`)

**Added GitHub thread reply guidance to receiving-code-review** (h/t @ralphbean)

Added a note about replying to inline review comments in the original thread rather than as top-level PR comments.

**Added automation-over-documentation guidance to writing-skills** (h/t @EthanJStark)

Added guidance that mechanical constraints should be automated, not documented—save skills for judgment calls.

## v4.0.0 (2025-12-17)

### New Features

**Two-stage code review in subagent-driven-development**

Subagent workflows now use two separate review stages after each task:

1. **Spec compliance review** - Skeptical reviewer verifies implementation matches spec exactly. Catches missing requirements AND over-building. Won't trust implementer's report—reads actual code.

2. **Code quality review** - Only runs after spec compliance passes. Reviews for clean code, test coverage, maintainability.

This catches the common failure mode where code is well-written but doesn't match what was requested. Reviews are loops, not one-shot: if reviewer finds issues, implementer fixes them, then reviewer checks again.

Other subagent workflow improvements:
- Controller provides full task text to workers (not file references)
- Workers can ask clarifying questions before AND during work
- Self-review checklist before reporting completion
- Plan read once at start, extracted to TodoWrite

New prompt templates in `skills/subagent-driven-development/`:
- `implementer-prompt.md` - Includes self-review checklist, encourages questions
- `spec-reviewer-prompt.md` - Skeptical verification against requirements
- `code-quality-reviewer-prompt.md` - Standard code review

**Debugging techniques consolidated with tools**

`systematic-debugging` now bundles supporting techniques and tools:
- `root-cause-tracing.md` - Trace bugs backward through call stack
- `defense-in-depth.md` - Add validation at multiple layers
- `condition-based-waiting.md` - Replace arbitrary timeouts with condition polling
- `find-polluter.sh` - Bisection script to find which test creates pollution
- `condition-based-waiting-example.ts` - Complete implementation from real debugging session

**Testing anti-patterns reference**

`test-driven-development` now includes `testing-anti-patterns.md` covering:
- Testing mock behavior instead of real behavior
- Adding test-only methods to production classes
- Mocking without understanding dependencies
- Incomplete mocks that hide structural assumptions

**Skill test infrastructure**

Three new test frameworks for validating skill behavior:

`tests/skill-triggering/` - Validates skills trigger from naive prompts without explicit naming. Tests 6 skills to ensure descriptions alone are sufficient.

`tests/claude-code/` - Integration tests using `claude -p` for headless testing. Verifies skill usage via session transcript (JSONL) analysis. Includes `analyze-token-usage.py` for cost tracking.

`tests/subagent-driven-dev/` - End-to-end workflow validation with two complete test projects:
- `go-fractals/` - CLI tool with Sierpinski/Mandelbrot (10 tasks)
- `svelte-todo/` - CRUD app with localStorage and Playwright (12 tasks)

### Major Changes

**DOT flowcharts as executable specifications**

Rewrote key skills using DOT/GraphViz flowcharts as the authoritative process definition. Prose becomes supporting content.

**The Description Trap** (documented in `writing-skills`): Discovered that skill descriptions override flowchart content when descriptions contain workflow summaries. Claude follows the short description instead of reading the detailed flowchart. Fix: descriptions must be trigger-only ("Use when X") with no process details.

**Skill priority in using-superpowers**

When multiple skills apply, process skills (brainstorming, debugging) now explicitly come before implementation skills. "Build X" triggers brainstorming first, then domain skills.

**brainstorming trigger strengthened**

Description changed to imperative: "You MUST use this before any creative work—creating features, building components, adding functionality, or modifying behavior."

### Breaking Changes

**Skill consolidation** - Six standalone skills merged:
- `root-cause-tracing`, `defense-in-depth`, `condition-based-waiting` → bundled in `systematic-debugging/`
- `testing-skills-with-subagents` → bundled in `writing-skills/`
- `testing-anti-patterns` → bundled in `test-driven-development/`
- `sharing-skills` removed (obsolete)

### Other Improvements

- **render-graphs.js** - Tool to extract DOT diagrams from skills and render to SVG
- **Rationalizations table** in using-superpowers - Scannable format including new entries: "I need more context first", "Let me explore first", "This feels productive"
- **docs/testing.md** - Guide to testing skills with Claude Code integration tests

---

## v3.6.2 (2025-12-03)

### Fixed

- **Linux Compatibility**: Fixed polyglot hook wrapper (`run-hook.cmd`) to use POSIX-compliant syntax
  - Replaced bash-specific `${BASH_SOURCE[0]:-$0}` with standard `$0` on line 16
  - Resolves "Bad substitution" error on Ubuntu/Debian systems where `/bin/sh` is dash
  - Fixes #141

---

## v3.5.1 (2025-11-24)

### Changed

- **OpenCode Bootstrap Refactor**: Switched from `chat.message` hook to `session.created` event for bootstrap injection
  - Bootstrap now injects at session creation via `session.prompt()` with `noReply: true`
  - Explicitly tells the model that using-superpowers is already loaded to prevent redundant skill loading
  - Consolidated bootstrap content generation into shared `getBootstrapContent()` helper
  - Cleaner single-implementation approach (removed fallback pattern)

---

## v3.5.0 (2025-11-23)

### Added

- **OpenCode Support**: Native JavaScript plugin for OpenCode.ai
  - Custom tools: `use_skill` and `find_skills`
  - Message insertion pattern for skill persistence across context compaction
  - Automatic context injection via chat.message hook
  - Auto re-injection on session.compacted events
  - Three-tier skill priority: project > personal > superpowers
  - Project-local skills support (`.opencode/skills/`)
  - Shared core module (`lib/skills-core.js`) for code reuse with Codex
  - Automated test suite with proper isolation (`tests/opencode/`)
  - Platform-specific documentation (`docs/README.opencode.md`, `docs/README.codex.md`)

### Changed

- **Refactored Codex Implementation**: Now uses shared `lib/skills-core.js` ES module
  - Eliminates code duplication between Codex and OpenCode
  - Single source of truth for skill discovery and parsing
  - Codex successfully loads ES modules via Node.js interop

- **Improved Documentation**: Rewrote README to explain problem/solution clearly
  - Removed duplicate sections and conflicting information
  - Added complete workflow description (brainstorm → plan → execute → finish)
  - Simplified platform installation instructions
  - Emphasized skill-checking protocol over automatic activation claims

---

## v3.4.1 (2025-10-31)

### Improvements

- Optimized superpowers bootstrap to eliminate redundant skill execution. The `using-superpowers` skill content is now provided directly in session context, with clear guidance to use the Skill tool only for other skills. This reduces overhead and prevents the confusing loop where agents would execute `using-superpowers` manually despite already having the content from session start.

## v3.4.0 (2025-10-30)

### Improvements

- Simplified `brainstorming` skill to return to original conversational vision. Removed heavyweight 6-phase process with formal checklists in favor of natural dialogue: ask questions one at a time, then present design in 200-300 word sections with validation. Keeps documentation and implementation handoff features.

## v3.3.1 (2025-10-28)

### Improvements

- Updated `brainstorming` skill to require autonomous recon before questioning, encourage recommendation-driven decisions, and prevent agents from delegating prioritization back to humans.
- Applied writing clarity improvements to `brainstorming` skill following Strunk's "Elements of Style" principles (omitted needless words, converted negative to positive form, improved parallel construction).

### Bug Fixes

- Clarified `writing-skills` guidance so it points to the correct agent-specific personal skill directories (`~/.claude/skills` for Claude Code, `~/.codex/skills` for Codex).

## v3.3.0 (2025-10-28)

### New Features

**Experimental Codex Support**
- Added unified `superpowers-codex` script with bootstrap/use-skill/find-skills commands
- Cross-platform Node.js implementation (works on Windows, macOS, Linux)
- Namespaced skills: `superpowers:skill-name` for superpowers skills, `skill-name` for personal
- Personal skills override superpowers skills when names match
- Clean skill display: shows name/description without raw frontmatter
- Helpful context: shows supporting files directory for each skill
- Tool mapping for Codex: TodoWrite→update_plan, subagents→manual fallback, etc.
- Bootstrap integration with minimal AGENTS.md for automatic startup
- Complete installation guide and bootstrap instructions specific to Codex

**Key differences from Claude Code integration:**
- Single unified script instead of separate tools
- Tool substitution system for Codex-specific equivalents
- Simplified subagent handling (manual work instead of delegation)
- Updated terminology: "Superpowers skills" instead of "Core skills"

### Files Added
- `.codex/INSTALL.md` - Installation guide for Codex users
- `.codex/superpowers-bootstrap.md` - Bootstrap instructions with Codex adaptations
- `.codex/superpowers-codex` - Unified Node.js executable with all functionality

**Note:** Codex support is experimental. The integration provides core superpowers functionality but may require refinement based on user feedback.

## v3.2.3 (2025-10-23)

### Improvements

**Updated using-superpowers skill to use Skill tool instead of Read tool**
- Changed skill invocation instructions from Read tool to Skill tool
- Updated description: "using Read tool" → "using Skill tool"
- Updated step 3: "Use the Read tool" → "Use the Skill tool to read and run"
- Updated rationalization list: "Read the current version" → "Run the current version"

The Skill tool is the proper mechanism for invoking skills in Claude Code. This update corrects the bootstrap instructions to guide agents toward the correct tool.

### Files Changed
- Updated: `skills/using-superpowers/SKILL.md` - Changed tool references from Read to Skill

## v3.2.2 (2025-10-21)

### Improvements

**Strengthened using-superpowers skill against agent rationalization**
- Added EXTREMELY-IMPORTANT block with absolute language about mandatory skill checking
  - "If even 1% chance a skill applies, you MUST read it"
  - "You do not have a choice. You cannot rationalize your way out."
- Added MANDATORY FIRST RESPONSE PROTOCOL checklist
  - 5-step process agents must complete before any response
  - Explicit "responding without this = failure" consequence
- Added Common Rationalizations section with 8 specific evasion patterns
  - "This is just a simple question" → WRONG
  - "I can check files quickly" → WRONG
  - "Let me gather information first" → WRONG
  - Plus 5 more common patterns observed in agent behavior

These changes address observed agent behavior where they rationalize around skill usage despite clear instructions. The forceful language and pre-emptive counter-arguments aim to make non-compliance harder.

### Files Changed
- Updated: `skills/using-superpowers/SKILL.md` - Added three layers of enforcement to prevent skill-skipping rationalization

## v3.2.1 (2025-10-20)

### New Features

**Code reviewer agent now included in plugin**
- Added `superpowers:code-reviewer` agent to plugin's `agents/` directory
- Agent provides systematic code review against plans and coding standards
- Previously required users to have personal agent configuration
- All skill references updated to use namespaced `superpowers:code-reviewer`
- Fixes #55

### Files Changed
- New: `agents/code-reviewer.md` - Agent definition with review checklist and output format
- Updated: `skills/requesting-code-review/SKILL.md` - References to `superpowers:code-reviewer`
- Updated: `skills/subagent-driven-development/SKILL.md` - References to `superpowers:code-reviewer`

## v3.2.0 (2025-10-18)

### New Features

**Design documentation in brainstorming workflow**
- Added Phase 4: Design Documentation to brainstorming skill
- Design documents now written to `docs/plans/YYYY-MM-DD-<topic>-design.md` before implementation
- Restores functionality from original brainstorming command that was lost during skill conversion
- Documents written before worktree setup and implementation planning
- Tested with subagent to verify compliance under time pressure

### Breaking Changes

**Skill reference namespace standardization**
- All internal skill references now use `superpowers:` namespace prefix
- Updated format: `superpowers:test-driven-development` (previously just `test-driven-development`)
- Affects all REQUIRED SUB-SKILL, RECOMMENDED SUB-SKILL, and REQUIRED BACKGROUND references
- Aligns with how skills are invoked using the Skill tool
- Files updated: brainstorming, executing-plans, subagent-driven-development, systematic-debugging, testing-skills-with-subagents, writing-plans, writing-skills

### Improvements

**Design vs implementation plan naming**
- Design documents use `-design.md` suffix to prevent filename collisions
- Implementation plans continue using existing `YYYY-MM-DD-<feature-name>.md` format
- Both stored in `docs/plans/` directory with clear naming distinction

## v3.1.1 (2025-10-17)

### Bug Fixes

- **Fixed command syntax in README** (#44) - Updated all command references to use correct namespaced syntax (`/superpowers:brainstorm` instead of `/brainstorm`). Plugin-provided commands are automatically namespaced by Claude Code to avoid conflicts between plugins.

## v3.1.0 (2025-10-17)

### Breaking Changes

**Skill names standardized to lowercase**
- All skill frontmatter `name:` fields now use lowercase kebab-case matching directory names
- Examples: `brainstorming`, `test-driven-development`, `using-git-worktrees`
- All skill announcements and cross-references updated to lowercase format
- This ensures consistent naming across directory names, frontmatter, and documentation

### New Features

**Enhanced brainstorming skill**
- Added Quick Reference table showing phases, activities, and tool usage
- Added copyable workflow checklist for tracking progress
- Added decision flowchart for when to revisit earlier phases
- Added comprehensive AskUserQuestion tool guidance with concrete examples
- Added "Question Patterns" section explaining when to use structured vs open-ended questions
- Restructured Key Principles as scannable table

**Anthropic best practices integration**
- Added `skills/writing-skills/anthropic-best-practices.md` - Official Anthropic skill authoring guide
- Referenced in writing-skills SKILL.md for comprehensive guidance
- Provides patterns for progressive disclosure, workflows, and evaluation

### Improvements

**Skill cross-reference clarity**
- All skill references now use explicit requirement markers:
  - `**REQUIRED BACKGROUND:**` - Prerequisites you must understand
  - `**REQUIRED SUB-SKILL:**` - Skills that must be used in workflow
  - `**Complementary skills:**` - Optional but helpful related skills
- Removed old path format (`skills/collaboration/X` → just `X`)
- Updated Integration sections with categorized relationships (Required vs Complementary)
- Updated cross-reference documentation with best practices

**Alignment with Anthropic best practices**
- Fixed description grammar and voice (fully third-person)
- Added Quick Reference tables for scanning
- Added workflow checklists Claude can copy and track
- Appropriate use of flowcharts for non-obvious decision points
- Improved scannable table formats
- All skills well under 500-line recommendation

### Bug Fixes

- **Re-added missing command redirects** - Restored `commands/brainstorm.md` and `commands/write-plan.md` that were accidentally removed in v3.0 migration
- Fixed `defense-in-depth` name mismatch (was `Defense-in-Depth-Validation`)
- Fixed `receiving-code-review` name mismatch (was `Code-Review-Reception`)
- Fixed `commands/brainstorm.md` reference to correct skill name
- Removed references to non-existent related skills

### Documentation

**writing-skills improvements**
- Updated cross-referencing guidance with explicit requirement markers
- Added reference to Anthropic's official best practices
- Improved examples showing proper skill reference format

## v3.0.1 (2025-10-16)

### Changes

We now use Anthropic's first-party skills system!

## v2.0.2 (2025-10-12)

### Bug Fixes

- **Fixed false warning when local skills repo is ahead of upstream** - The initialization script was incorrectly warning "New skills available from upstream" when the local repository had commits ahead of upstream. The logic now correctly distinguishes between three git states: local behind (should update), local ahead (no warning), and diverged (should warn).

## v2.0.1 (2025-10-12)

### Bug Fixes

- **Fixed session-start hook execution in plugin context** (#8, PR #9) - The hook was failing silently with "Plugin hook error" preventing skills context from loading. Fixed by:
  - Using `${BASH_SOURCE[0]:-$0}` fallback when BASH_SOURCE is unbound in Claude Code's execution context
  - Adding `|| true` to handle empty grep results gracefully when filtering status flags

---

# Superpowers v2.0.0 Release Notes

## Overview

Superpowers v2.0 makes skills more accessible, maintainable, and community-driven through a major architectural shift.

The headline change is **skills repository separation**: all skills, scripts, and documentation have moved from the plugin into a dedicated repository ([obra/superpowers-skills](https://github.com/obra/superpowers-skills)). This transforms superpowers from a monolithic plugin into a lightweight shim that manages a local clone of the skills repository. Skills auto-update on session start. Users fork and contribute improvements via standard git workflows. The skills library versions independently from the plugin.

Beyond infrastructure, this release adds nine new skills focused on problem-solving, research, and architecture. We rewrote the core **using-skills** documentation with imperative tone and clearer structure, making it easier for Claude to understand when and how to use skills. **find-skills** now outputs paths you can paste directly into the Read tool, eliminating friction in the skills discovery workflow.

Users experience seamless operation: the plugin handles cloning, forking, and updating automatically. Contributors find the new architecture makes improving and sharing skills trivial. This release lays the foundation for skills to evolve rapidly as a community resource.

## Breaking Changes

### Skills Repository Separation

**The biggest change:** Skills no longer live in the plugin. They've been moved to a separate repository at [obra/superpowers-skills](https://github.com/obra/superpowers-skills).

**What this means for you:**

- **First install:** Plugin automatically clones skills to `~/.config/superpowers/skills/`
- **Forking:** During setup, you'll be offered the option to fork the skills repo (if `gh` is installed)
- **Updates:** Skills auto-update on session start (fast-forward when possible)
- **Contributing:** Work on branches, commit locally, submit PRs to upstream
- **No more shadowing:** Old two-tier system (personal/core) replaced with single-repo branch workflow

**Migration:**

If you have an existing installation:
1. Your old `~/.config/superpowers/.git` will be backed up to `~/.config/superpowers/.git.bak`
2. Old skills will be backed up to `~/.config/superpowers/skills.bak`
3. Fresh clone of obra/superpowers-skills will be created at `~/.config/superpowers/skills/`

### Removed Features

- **Personal superpowers overlay system** - Replaced with git branch workflow
- **setup-personal-superpowers hook** - Replaced by initialize-skills.sh

## New Features

### Skills Repository Infrastructure

**Automatic Clone & Setup** (`lib/initialize-skills.sh`)
- Clones obra/superpowers-skills on first run
- Offers fork creation if GitHub CLI is installed
- Sets up upstream/origin remotes correctly
- Handles migration from old installation

**Auto-Update**
- Fetches from tracking remote on every session start
- Auto-merges with fast-forward when possible
- Notifies when manual sync needed (branch diverged)
- Uses pulling-updates-from-skills-repository skill for manual sync

### New Skills

**Problem-Solving Skills** (`skills/problem-solving/`)
- **collision-zone-thinking** - Force unrelated concepts together for emergent insights
- **inversion-exercise** - Flip assumptions to reveal hidden constraints
- **meta-pattern-recognition** - Spot universal principles across domains
- **scale-game** - Test at extremes to expose fundamental truths
- **simplification-cascades** - Find insights that eliminate multiple components
- **when-stuck** - Dispatch to right problem-solving technique

**Research Skills** (`skills/research/`)
- **tracing-knowledge-lineages** - Understand how ideas evolved over time

**Architecture Skills** (`skills/architecture/`)
- **preserving-productive-tensions** - Keep multiple valid approaches instead of forcing premature resolution

### Skills Improvements

**using-skills (formerly getting-started)**
- Renamed from getting-started to using-skills
- Complete rewrite with imperative tone (v4.0.0)
- Front-loaded critical rules
- Added "Why" explanations for all workflows
- Always includes /SKILL.md suffix in references
- Clearer distinction between rigid rules and flexible patterns

**writing-skills**
- Cross-referencing guidance moved from using-skills
- Added token efficiency section (word count targets)
- Improved CSO (Claude Search Optimization) guidance

**sharing-skills**
- Updated for new branch-and-PR workflow (v2.0.0)
- Removed personal/core split references

**pulling-updates-from-skills-repository** (new)
- Complete workflow for syncing with upstream
- Replaces old "updating-skills" skill

### Tools Improvements

**find-skills**
- Now outputs full paths with /SKILL.md suffix
- Makes paths directly usable with Read tool
- Updated help text

**skill-run**
- Moved from scripts/ to skills/using-skills/
- Improved documentation

### Plugin Infrastructure

**Session Start Hook**
- Now loads from skills repository location
- Shows full skills list at session start
- Prints skills location info
- Shows update status (updated successfully / behind upstream)
- Moved "skills behind" warning to end of output

**Environment Variables**
- `SUPERPOWERS_SKILLS_ROOT` set to `~/.config/superpowers/skills`
- Used consistently throughout all paths

## Bug Fixes

- Fixed duplicate upstream remote addition when forking
- Fixed find-skills double "skills/" prefix in output
- Removed obsolete setup-personal-superpowers call from session-start
- Fixed path references throughout hooks and commands

## Documentation

### README
- Updated for new skills repository architecture
- Prominent link to superpowers-skills repo
- Updated auto-update description
- Fixed skill names and references
- Updated Meta skills list

### Testing Documentation
- Added comprehensive testing checklist (`docs/TESTING-CHECKLIST.md`)
- Created local marketplace config for testing
- Documented manual testing scenarios

## Technical Details

### File Changes

**Added:**
- `lib/initialize-skills.sh` - Skills repo initialization and auto-update
- `docs/TESTING-CHECKLIST.md` - Manual testing scenarios
- `.claude-plugin/marketplace.json` - Local testing config

**Removed:**
- `skills/` directory (82 files) - Now in obra/superpowers-skills
- `scripts/` directory - Now in obra/superpowers-skills/skills/using-skills/
- `hooks/setup-personal-superpowers.sh` - Obsolete

**Modified:**
- `hooks/session-start.sh` - Use skills from ~/.config/superpowers/skills
- `commands/brainstorm.md` - Updated paths to SUPERPOWERS_SKILLS_ROOT
- `commands/write-plan.md` - Updated paths to SUPERPOWERS_SKILLS_ROOT
- `commands/execute-plan.md` - Updated paths to SUPERPOWERS_SKILLS_ROOT
- `README.md` - Complete rewrite for new architecture

### Commit History

This release includes:
- 20+ commits for skills repository separation
- PR #1: Amplifier-inspired problem-solving and research skills
- PR #2: Personal superpowers overlay system (later replaced)
- Multiple skill refinements and documentation improvements

## Upgrade Instructions

### Fresh Install

```bash
# In Claude Code
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

The plugin handles everything automatically.

### Upgrading from v1.x

1. **Backup your personal skills** (if you have any):
   ```bash
   cp -r ~/.config/superpowers/skills ~/superpowers-skills-backup
   ```

2. **Update the plugin:**
   ```bash
   /plugin update superpowers
   ```

3. **On next session start:**
   - Old installation will be backed up automatically
   - Fresh skills repo will be cloned
   - If you have GitHub CLI, you'll be offered the option to fork

4. **Migrate personal skills** (if you had any):
   - Create a branch in your local skills repo
   - Copy your personal skills from backup
   - Commit and push to your fork
   - Consider contributing back via PR

## What's Next

### For Users

- Explore the new problem-solving skills
- Try the branch-based workflow for skill improvements
- Contribute skills back to the community

### For Contributors

- Skills repository is now at https://github.com/obra/superpowers-skills
- Fork → Branch → PR workflow
- See skills/meta/writing-skills/SKILL.md for TDD approach to documentation

## Known Issues

None at this time.

## Credits

- Problem-solving skills inspired by Amplifier patterns
- Community contributions and feedback
- Extensive testing and iteration on skill effectiveness

---

**Full Changelog:** https://github.com/obra/superpowers/compare/dd013f6...main
**Skills Repository:** https://github.com/obra/superpowers-skills
**Issues:** https://github.com/obra/superpowers/issues
