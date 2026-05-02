# Workflow Frontier Resolver Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. Load `skill-creator` before editing any `skills/*/SKILL.md`. This is a package-design change, not a data-analysis task. Task statuses describe the current workflow frontier; do not mark tasks `APPROVED` until a reviewer has actually approved them.

**Objective:** Make superRA's runtime instruction surface adaptive and composable by doing two things together on one branch: (1) redesign the Workflow Frontier Resolver so it teaches a small reusable re-entry mechanism instead of a long taxonomy of contingency outcomes (Tasks 1-4); and (2) remove over-prescription across every instruction surface the workflow loads — role specs, workflow skills, orchestration, utility/domain/meta skills, generated direct-mode refs, and Codex TOMLs — by applying the "Teach the Protocol, Don't Prescribe Each Action" principle that was extracted from the first redesign and promoted to a gated check (Tasks 5-11).

**Methodology:** For (1): keep only the runtime guidance agents are unlikely to infer reliably — the canonical workflow map, the adaptability principle, the durable evidence to inspect, the decision object to return, the affected-task closure rule, owner routing, and safety invariants. Remove contingency-tree prose and duplicated phase-selection logic from workflow skills. For (2): for every instruction line, apply two ordered tests — **DRY** (if the content is already carried by another skill, reference, dispatch field, or handoff doc the agent reads, point or delete; do not paraphrase) and **Necessity** (without this line, would the agent's behavior be unstable? if not, delete). Keep behavior-shaping lines — safety invariants, ordering constraints, non-default constraints, explicit authority rules. Many deletions across this branch are the audit intentionally trimming wrappers, meta-narration, runtime-default reminders, and Skill-Load Manifest restatements; they are the expected output of the approved methodology, not scope creep. The full principle + anti-patterns + "Keep" carve-out live in `CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action`.

**Data Inventory:** Not applicable. This change edits package documentation, skill references, role specs, and generator-owned files only.

**Conventions:** Preserve one source of truth per concern per `CLAUDE.md §Ownership Boundaries`: `using-superRA` owns cross-stage overview + Skill-Load Manifest + Execution Modes; `main-agent.md` owns main-agent autonomy + re-entry mechanism; workflow skills own local phase gates; `agent-orchestration` owns dispatch-prompt shape + reviewer-feedback adjudication + relay protocol; `handoff-doc` owns document state semantics + anatomy templates + User Decisions Log; `refactor-and-integrate` owns generic drift-test + refactor + integration + merge-quality discipline; `econ-data-analysis` owns data-analysis domain discipline including the drift-test tolerance rubric (relocated from `refactor-and-integrate` in Task 10 because calibration is econ-specific). One-way pointer flow: domain → cross-cutting, not the reverse.

**Output:** Trimmed runtime skill/reference docs, condensed role specs (`agents/*.md`), regenerated direct-mode references (`skills/using-superRA/references/direct-mode-*.md`) and Codex TOMLs (`.codex/agents/*.toml`) produced from the updated sources via `sync_codex_agents.py`, expanded `CLAUDE.md` (teach-the-protocol principle + gate + Design Audit Checklist line), relocated drift-test tolerance rubric, and this `PLAN.md` / `RESULTS.md` pair.

**Expected Results / Hypotheses:** (1) Agents reading the runtime surface should understand the PLAN → IMPLEMENT → INTEGRATE cycle, why re-entry is adaptive, and how to compute the next safe frontier without needing an enumerated scenario tree; the resolver's value added is limited to evidence discipline, affected-frontier calculation, workflow-owner routing, and non-negotiable gates. (2) Every remaining instruction line in `skills/*` and `agents/*` passes the DRY + Necessity tests — the remaining surface is behavior-shaping, not hortatory or redundant. (3) No behavior agents depend on was lost: deleted content is either generally inferrable or recoverable from an authoritative owner via a surviving pointer. (4) Generator regeneration is deterministic and the direct-mode refs carry no dispatch-only wording.

**Sensitivity Analysis:** (a) Mixed-state re-entry: when a completed task changes after implementation or integration, only the changed task plus affected downstream dependents lose local validity; unrelated approved work remains preserved; rollup milestones are unchecked only where false; global gates still rerun before merge/PR. (b) Audit-refactor safety: the existing `test_sync_codex_agents.py` suite (5 tests, determinism + direct-mode-leak guards via `ValueError` on source drift) remains the drift-test coverage — any future source-text reflow that would silently leak dispatch-only wording into direct-mode refs raises in generation rather than in production.

**Pipeline:** Not applicable. Verification is static documentation audit + `uv run pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py` + `git diff --check` + leak-grep on regenerated direct-mode refs.

---

## Workflow Status

- [x] **Plan approved** - researcher requested the material redesign toward mechanisms over contingency prose on 2026-04-23.
- [x] **Execution complete** - All 11 tasks reviewer-approved; principle gate enshrined; inverted cross-references in `codebase-integration.md` fully removed (decision tree + gated-checklist item).
- [x] **Drift tests created** - existing `skills/codex-superra-setup/scripts/test_sync_codex_agents.py` (5 tests, all passing) is the Phase A coverage per §Decisions 2026-04-23. No new drift tests authored.
- [x] **Refactored** - Phase B integration review approved all 11 tasks (commit `5479838`); surviving diff justified against approved task objectives; one MINOR polish deferred to RESULTS.md §Known Follow-Ups.
- [x] **Docs finalized** - PLAN.md + RESULTS.md relocated to `docs/plans/2026-04-23-improve-design-principle-{plan,results}.md` per user decision; no doc-writer/doc-reviewer maturation (contributor-docs change, not an analysis report).
- [x] **Merged** - branch pushed to `origin/improve-design-principle` and PR opened against `origin/main` on 2026-04-23 (Phase D Option 2: push + PR).

## Project Conventions

Walked at planning time (2026-04-23). Re-walk on-demand only.

### Repo root
- `/AGENTS.md`: contributor-facing entry point (aliased to `/CLAUDE.md`). It says superRA internal changes should be evaluated against adaptive/composable workflow design, DRY ownership, lean agents with rich references, and skill-authoring discipline when editing `skills/*/SKILL.md`. Now also carries the gated **Teach the Protocol, Don't Prescribe Each Action** principle added in Tasks 5 and 11.
- `/CLAUDE.md`: the canonical contributor guide. Carries the `## Internal Design Philosophy` (Adaptive/Composable + Minimal/Targeted + **Teach-the-Protocol gate**), `## Ownership Boundaries` table, `## Architectural Patterns`, `## Skill Authoring Guidelines`, and `## Design Audit Checklist`. Every implementer/reviewer editing `skills/*` or `agents/*` self-applies the gate before commit and the reviewer verifies it on every pass.
- `/README.md`: user-facing project design belongs there. Runtime skills may carry a concise operational overview only where agents actually load it.

### Relevant skill/reference files
- `skills/using-superRA/SKILL.md`: owns the runtime skill inventory, Skill-Load Manifest, and should carry the compact canonical workflow/adaptability overview loaded by all superRA agents.
- `skills/using-superRA/references/main-agent.md`: owns main-agent session start, autonomy, direct mode, and the re-entry mechanism.
- `skills/planning-workflow/SKILL.md`: owns plan creation and the material plan-change protocol, including which task-local statuses and rollup milestones are invalidated.
- `skills/implementation-workflow/SKILL.md`: owns implementation, review, and reproducibility mechanics after the resolver selects an implementation/review frontier.
- `skills/integration-workflow/SKILL.md`: owns Phase A-D integration mechanics after the resolver selects an integration/documentation/finalization frontier.
- `skills/agent-orchestration/SKILL.md`: owns dispatch, reviewer-feedback adjudication, and status-return mechanics inside a selected frontier.
- `skills/handoff-doc/references/plan-anatomy.md`: owns task-block and workflow-status semantics for handoff docs.

### Not walked
- `tests/`, `hooks/`, `scripts/`, and package metadata are not in the planned diff unless verification shows they are needed.

## Decisions

> **User decision (2026-04-23):** Implement the "Workflow Frontier Resolver Handoff" plan using a frontier model, not a single global state model.
> **Question asked:** Which design should govern mixed-state workflow re-entry?
> **Rationale (if given):** The hard problem is safe workflow re-entry from any repo state, while preserving unrelated completed work and avoiding rigid contingency rules.

> **User decision (2026-04-23):** Keep domain-neutral cleanup out of scope for this change.
> **Question asked:** Should domain-neutral design issues be handled in this task?
> **Rationale (if given):** Domain-neutral cleanup will be addressed separately; this change focuses only on workflow design flexibility.

> **User decision (2026-04-23):** Create `PLAN.md` and `RESULTS.md` retroactively after direct implementation.
> **Question asked:** Should the already-implemented change be recorded in superRA handoff docs?
> **Rationale (if given):** The package should dogfood its own workflow state discipline.

> **User decision (2026-04-23):** Redesign the resolver around mechanisms over contingency plans.
> **Question asked:** Should the lengthy resolver be narrowed to guidance agents cannot reliably infer themselves?
> **Rationale (if given):** The current resolver reads like a condition-by-condition scenario tree. This affects Tasks 1-4, clears their implementation/review validity, and unchecks `Execution complete`; the implementation must now add the missing runtime workflow/adaptability overview and keep only evidence discipline, affected-frontier calculation, owner routing, and safety gates.

> **User decision (2026-04-23):** Improve the resolver prose for clarity without changing the design.
> **Question asked:** Should the current resolver wording be tightened and reviewed by reviewer agents?
> **Rationale (if given):** The mechanism is accepted, but the current writing is too verbose and unclear. This affects Task 2 and Task 4 only; Task 1 and Task 3 remain approved.

> **User decision (2026-04-23):** Extend the plan with an over-prescription audit across package instruction surfaces.
> **Question asked:** Should additional tasks be added to audit instructions for lines that restate what agents already know or can read from authoritative sources?
> **Rationale (if given):** Current instructions in several places (e.g., the implementer's `Worktree:` wrapper, the "what the dispatch prompt carries" narration) tell agents what they would already do with the content they receive. The design principle to apply: keep a line only if, without it, agent behavior would be unstable — otherwise delete or replace with a pointer. The principle is documented in `CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action` (Task 5). Tasks 6-9 audit role specs, workflow skills + orchestration, and utility/domain skills against the principle and apply the edits. This adds Tasks 5-9 and unchecks `Execution complete`; Tasks 1-4 remain APPROVED (the principle tightens future edits rather than overturning the resolver redesign).

> **User decision (2026-04-23):** Refine the post-audit output — relocate the drift-test tolerance rubric, remove an inverted cross-reference, condense role-spec prose.
> **Question asked:** Two design questions surfaced in the post-audit review: (1) should the drift-test tolerance rubric live in the cross-cutting `refactor-and-integrate/drift-test-quality.md` or in the domain-specific `econ-data-analysis/references/integrate-drift-tests.md`? (2) Should the cross-cutting `codebase-integration.md` carry a "Data-analysis work:" cross-reference back into a domain file?
> **Rationale (if given):** (1) Tolerance calibration is econ-specific (t-stat crossing 1.96, percent-of-estimate scales, economic-reasoning thresholds) — it belongs in the domain skill so the cross-cutting file stays domain-agnostic and new verticals can carry their own rubric. (2) A cross-cutting file pointing back at a domain file is an inverted dependency; pointers flow domain → cross-cutting only. Alongside these, the researcher condensed `agents/implementer.md` and `agents/reviewer.md` by hand (WIP commit `93fda71`) and the refinement needs formalization into a Task 10 so the plan and RESULTS reflect what actually happened. This adds Task 10; Tasks 6-9 remain APPROVED (their approved outputs are being polished, not overturned).

> **User decision (2026-04-23):** Proceed with integration at the Step 4 completion menu.
> **Question asked:** Work complete and verified — what disposition for the branch (integrate / change plan / keep as-is / discard)?
> **Rationale (if given):** *(none given — direct selection at the 4-option menu)*

> **User decision (2026-04-23):** Skip programmatic anti-pattern / leak / pointer drift-test authoring at Phase A; rely on the existing `test_sync_codex_agents.py` (generator determinism) as the drift-test coverage for this branch.
> **Question asked:** Which Phase A drift tests should be authored — anti-pattern regression, direct-mode leak guard, pointer integrity, or none new?
> **Rationale (if given):** Researcher is skeptical that programmatic guards against anti-patterns are meaningful — the patterns are subjective and false-positive-prone. Existing generator-determinism tests catch the one silent-error class that bit us (the Task 6 cleanup-helper regression) because any future source-text drift makes the cleanup helpers raise `ValueError` and the test suite fails. The `Drift tests created` milestone flips against that existing coverage rather than a new suite.

> **User decision (2026-04-23):** Integrate against `origin/main` — Phase B integration base confirmation.
> **Question asked:** Which base branch should Phase B integrate against?
> **Rationale (if given):** Branch was cut from `origin/main` (merge-base `b6e0640`); main has no new commits since then, so Phase B collapses to a trivial fast-forward path after integration review.

> **User decision (2026-04-23):** Enshrine the "Teach the Protocol, Don't Prescribe Each Action" principle as a gate in `CLAUDE.md` — applies to every future implementer and reviewer editing any file under `skills/*` or `agents/*`.
> **Question asked:** Should the principle be promoted from design-philosophy prose to a gated check that implementers self-apply before commit and reviewers verify on every pass?
> **Rationale (if given):** The principle has proved load-bearing across Tasks 5-10 — catching it at the edit site is cheaper than the next audit round. Adds Task 11 and unchecks `Execution complete`; Tasks 1-10 remain APPROVED (the gate tightens future edits, does not overturn prior work). After Task 11 APPROVE, resume `integration-workflow` Phase B Step 1 (integration reviewer dispatch) — the base-branch confirmation above does not need re-asking.

> **User decision (2026-04-23):** Phase C shape — skip the doc-writer / doc-reviewer maturation pass; move `PLAN.md` and `RESULTS.md` into `docs/plans/` (matching the existing `YYYY-MM-DD-<slug>-plan.md` / `-results.md` convention) and flip `Docs finalized` against the current state.
> **Question asked:** Which Phase C shape — lightweight in-place tighten, full maturation with relocation, or skip-and-flip?
> **Rationale (if given):** This is a contributor-docs change, not an analysis producing an external report; the dev-log RESULTS.md is already the decision record. `docs/plans/` is the existing convention for superRA's package-design plan + results pairs. Fastest path to Phase D merge consistent with the branch's purpose.

---

### Task 1: Add Runtime Workflow Overview and Resolver Value Proposition
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** Not applicable; documentation/reference edit.
**Input:** `README.md`, `AGENTS.md`, `skills/using-superRA/SKILL.md`, `skills/using-superRA/references/main-agent.md`.
**Output:** Concise runtime overview plus a clear statement of what the resolver adds.

- [x] **Step 1: Add the loaded overview**

Add a compact PLAN -> IMPLEMENT -> INTEGRATE overview and adaptability statement to the runtime surface agents actually read, preferably `skills/using-superRA/SKILL.md`. Keep it procedural and avoid duplicating README-owned product explanation.

- [x] **Step 2: Define the resolver's value added**

State that the resolver exists to make agents do four things consistently: inspect durable evidence, compute the affected task frontier while preserving unrelated approved work, route to the workflow that owns the earliest invalid layer, and enforce non-negotiable gates before advancement.

- [x] **Step 3: Separate mechanism from examples**

Keep the resolver's mechanism in `main-agent.md`; avoid named state taxonomies or long scenario examples unless a specific guard is otherwise unpredictable.

### Task 2: Replace Contingency Taxonomy with a Frontier Mechanism
**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** Not applicable; documentation/reference edit.
**Input:** `skills/using-superRA/references/main-agent.md`.
**Output:** Shorter resolver that returns a decision object and selects the next owner by walking the canonical workflow order.

- [x] **Step 1: Keep the evidence contract**

Retain the durable facts agents must read: git status/log, PLAN/RESULTS presence and consistency, workflow rollups, decisions, task dependencies, task-local statuses, review notes, upstream intent, and current results.

- [x] **Step 2: Keep the decision object**

Return the same practical decision shape: affected tasks, preserved-approved tasks, invalidated milestones, next workflow owner/entry layer, and any required researcher stop point.

- [x] **Step 3: Replace state labels with ordered reasoning**

Replace the `needs ...` taxonomy with a canonical-order procedure: repair/log plan changes first; compute the changed-task closure; preserve unaffected local statuses; choose the earliest invalid layer across planning, implementation/review, validation/completion, integration, documentation, and final merge/PR.

- [x] **Step 4: Keep only safety invariants**

Retain explicit guards where unpredictable behavior is likely: no unlogged material user decision, no new global `Current state` field, no clearing unrelated task statuses, no integration before implementation validation and logged disposition, and no merge/PR before integration, documentation, and freshness gates.

- [x] **Step 5: Tighten resolver prose for clarity**

Rewrite the resolver section so the distinction between diagnosis, routing, plan-change handling, and workflow-owned actions is clear. Avoid abstract phrases such as "boxes whose guarantee is false"; use direct language about workflow milestones, task-level status, and the owning workflow.

### Task 3: Simplify Workflow Call Sites Around the Mechanism
**Depends on:** Task 2
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** Not applicable; documentation/reference edit.
**Input:** `skills/planning-workflow/SKILL.md`, `skills/implementation-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/agent-orchestration/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`.
**Output:** Workflow docs that point to the resolver for cross-workflow re-entry while preserving local gates.

- [x] **Step 1: Keep local ownership boundaries**

Ensure planning owns plan edits/status invalidation, implementation owns review/reproducibility/completion, integration owns drift/refactor/docs/merge gates, orchestration owns dispatch mechanics, and handoff-doc owns status semantics.

- [x] **Step 2: Remove duplicated entry-selection prose**

Search for resume/re-entry/frontier/skip/status wording that restates the resolver. Replace duplicated phase-selection prose with pointers to the mechanism, while keeping local phase gate instructions.

- [x] **Step 3: Preserve standalone utility semantics**

Make sure `handoff-doc` and other utility/domain skills remain usable directly and do not depend on a main-agent scenario tree.

### Task 4: Audit Against Adaptive-Composable Design
**Depends on:** Task 1, Task 2, Task 3
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** Static documentation audit.
**Input:** Modified skill/reference files and contributor design checklist.
**Output:** Verified diff and audit notes in `RESULTS.md`.

- [x] **Step 1: Run design-text search**

Search modified files for contingency-heavy phrases and old taxonomy labels: `needs plan repair`, `needs implementation`, `awaiting review`, `needs validation`, `if .* then`, `under .* condition`, `Current state`, `state machine`, `skip`, `resume`, `re-entry`, and similar wording.

- [x] **Step 2: Verify overview placement**

Confirm the canonical workflow overview and adaptability principle are present in a loaded runtime surface, not only in README or AGENTS.

- [x] **Step 3: Verify mechanism-only resolver**

Check the resolver against the value-added list: durable evidence, affected frontier/preserved work, owner routing, and safety gates. Remove anything that is just a scenario agents can infer from the canonical map.

- [x] **Step 4: Verify ownership boundaries**

Confirm the diff respects the AGENTS.md ownership table and does not put workflow choreography, dispatch mechanics, handoff-doc mechanics, or README-owned explanation in the wrong owner.

- [x] **Step 5: Run diff hygiene check**

Run `git diff --check`.

- [x] **Step 6: Review clarity with parallel reviewers**

Spawn reviewer agents after the prose edit. One reviewer should focus on plain-language clarity and ambiguity; another should focus on consistency with workflow ownership and the change-plan protocol.

### Task 5: Document "Teach the Protocol, Don't Prescribe Each Action" Principle
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** Not applicable; contributor-doc edit.
**Input:** `CLAUDE.md` (aliased from `AGENTS.md` / `AGENT.md`).
**Output:** New `CLAUDE.md` subsection under `## Internal Design Philosophy` naming the principle, stating the two tests (DRY, necessity), listing anti-patterns, and adding a line-level check to the Design Audit Checklist.

- [x] **Step 1: Add the principle and anti-patterns**

Add a subsection titled "Teach the Protocol, Don't Prescribe Each Action" after `### Minimal, Targeted Instructions`. State the governing test (without this line, would the agent's behavior be unstable?), the two ordered sub-tests (DRY, then necessity), and concrete anti-patterns drawn from the current repo: wrapper instructions around authoritative content (e.g., `Worktree:` steering), "here is what you will receive" descriptions of the dispatch prompt, reminders of runtime defaults, and restatements of the Skill-Load Manifest inside dispatch or role bodies. Contrast with behavior-shaping instructions that must be kept.

- [x] **Step 2: Extend the Design Audit Checklist**

Add a single-line check to `## Design Audit Checklist`: for every added line, does removing it change what the agent would *do*, or only what it would *understand*? If only understand, delete it.

### Task 6: Audit Agent Role Specs and `using-superRA` Surfaces
**Depends on:** Task 5
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** Line-by-line instruction audit against the Task 5 principle; edits applied inline.
**Input:** `agents/implementer.md`, `agents/reviewer.md`, `skills/using-superRA/SKILL.md` and all files under `skills/using-superRA/references/` (including `main-agent.md`, `codex-instructions.md`, `claude-tools.md`, and any generated `direct-mode-*.md` — edit source specs and regenerate rather than editing generated files directly).
**Output:** Trimmed role specs / runtime surfaces, a findings note in `RESULTS.md` summarizing what was cut, replaced with a pointer, or kept with rationale. Verify generated direct-mode reference files are regenerated from their canonical agent specs.

- [x] **Step 1: Survey each file line by line**

Walked `agents/implementer.md`, `agents/reviewer.md`, `skills/using-superRA/SKILL.md`, and every file under `skills/using-superRA/references/` against the CLAUDE.md §Teach the Protocol principle. KEEP / POINTER / DELETE classifications recorded in `RESULTS.md` Task 6 findings; the heaviest over-prescription was in `agents/implementer.md` (§Stage → skills / §What the dispatch carries wrappers, §Data-First Discipline duplication of `econ-data-analysis`, full §Editing Etiquette duplication of `handoff-doc`), `agents/reviewer.md` (mirror of the same), and `main-agent.md` §Execution Modes (near-duplicate of `codex-instructions.md` §Delegation Priority with a typo and a dangling fragment).

- [x] **Step 2: Apply the edits and regenerate**

Trimmed DELETEs and converted POINTERs in `agents/implementer.md`, `agents/reviewer.md`, `skills/using-superRA/SKILL.md`, and `main-agent.md` §Execution Modes (now one subagent-default sentence plus a direct-mode protocol block plus a single-line Codex pointer at `references/codex-instructions.md`). Updated `skills/codex-superra-setup/scripts/sync_codex_agents.py` to match the new source shape (removed the `## Stage → skills and references` section lookup now that source was trimmed; collapsed the two cleanup_* functions whose pattern-match targets no longer exist; trimmed the direct-mode `## Before You Start` prose in-place). Regenerated `skills/using-superRA/references/direct-mode-{implementer,reviewer}.md` and `.codex/agents/superra_{implementer,reviewer}.toml`; `sync_codex_agents.py --scope project --check` and `test_sync_codex_agents.py` both pass.

- [x] **Step 3: Verify no behavior was lost**

Cross-checked every DELETE/POINTER target: `handoff-doc` carries the full editing discipline the implementer/reviewer bodies now link to; `econ-data-analysis` owns Data-First Discipline; `codex-instructions.md` §Delegation Priority carries the Codex subagent rule that main-agent.md used to restate. No deleted content exposed a missing instruction elsewhere — every POINTER target actually carries the referenced content.

### Task 7: Audit Workflow Skills and `agent-orchestration`
**Depends on:** Task 5
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** Line-by-line instruction audit against the Task 5 principle; edits applied inline.
**Input:** `skills/planning-workflow/SKILL.md`, `skills/implementation-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/agent-orchestration/SKILL.md`, and every reference file under those four skills' `references/` directories.
**Output:** Trimmed workflow skills, a findings note in `RESULTS.md` summarizing cuts / pointers / kept lines per file, and confirmation that ownership boundaries from `CLAUDE.md §Ownership Boundaries` are preserved.

- [x] **Step 1: Survey each file line by line**

Applied the two tests to each line across the four SKILL.md files and the two `agent-orchestration/references/` files. Findings recorded in `RESULTS.md` Task 7.

- [x] **Step 2: Apply the edits**

Applied trims and pointer replacements. Preserved all local gate instructions, stop points, status transitions, and review-verdict discipline.

- [x] **Step 3: Verify ownership boundaries are intact**

Re-checked `CLAUDE.md §Ownership Boundaries`. After trimming, each concern still has exactly one authoritative owner. Findings in `RESULTS.md` Task 7.

### Task 8: Audit Utility, Domain, and Meta Skills
**Depends on:** Task 5
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** Line-by-line instruction audit against the Task 5 principle; edits applied inline.
**Input:** `skills/handoff-doc/`, `skills/refactor-and-integrate/`, `skills/report-in-markdown/`, `skills/semantic-merge/`, `skills/worktree-data-sync/`, `skills/econ-data-analysis/`, `skills/codex-superra-setup/` — each skill's `SKILL.md` plus all files under its `references/`.
**Output:** Trimmed utility / domain / meta skills, a findings note in `RESULTS.md` summarizing per-file cuts / pointers / kept lines, and confirmation that domain and utility skills remain standalone-usable (per `CLAUDE.md §Adaptive, Composable Workflows`).

- [x] **Step 1: Survey each file line by line**

Applied the two tests (DRY, necessity) plus the standalone-usability check to each line across all 22 in-scope files. Full per-file KEEP / POINTER / DELETE summary lives in `RESULTS.md` Task 8 findings.

- [x] **Step 2: Apply the edits**

Trimmed DELETE lines; replaced POINTER lines with single-line references to the authoritative owner. 19 of 22 files received edits (the 3 `SKILL.md` files under `refactor-and-integrate`, `handoff-doc` root SKILL, and two fully-functional CLI/rendering guides already met the bar in most sections; the edits in scope reflect where the principle surfaced violations). No gated checklist item removed; no `SKILL.md` frontmatter changed.

- [x] **Step 3: Verify standalone usability**

Re-read each skill's post-edit SKILL.md as if loaded outside the superRA workflow — `handoff-doc`, `refactor-and-integrate`, `report-in-markdown`, `semantic-merge`, `worktree-data-sync`, `econ-data-analysis`, `codex-superra-setup` all read coherently without orchestration context. Where an instruction needed a workflow callsite (e.g., `integration-workflow` Phase B), it now reads as an example caller rather than a prerequisite. Details in `RESULTS.md` Task 8 §Standalone-usability check.

### Task 9: Cross-Audit Consistency Sweep
**Depends on:** Task 6, Task 7, Task 8
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** Whole-repo verification that the audit edits compose cleanly.
**Input:** The full diff produced by Tasks 6-8.
**Output:** A consolidated audit summary in `RESULTS.md` Task 9 listing any residual duplication, pointer targets that do not actually carry the referenced content, and any newly-introduced gaps where a deleted line's content is not recoverable from an authoritative source.

- [x] **Step 1: Pointer integrity check**

Verified every POINTER introduced in Tasks 7 and 8 against the cited source (Task 6 pointers were already verified by that task's reviewer). All resolve at the named anchor. Findings in `RESULTS.md` Task 9 §Pointer Integrity.

- [x] **Step 2: Residual-duplication search**

Grepped `skills/`, `agents/`, and `CLAUDE.md` for behavior-shaping phrases (Data-First discipline, Iron Law, editing etiquette bullets, Execution Modes, Skill-Load Manifest, User Decisions Log). Each concern has one authoritative owner; every other mention is a pointer or role-scoped compact. Findings in `RESULTS.md` Task 9 §Residual Duplication.

- [x] **Step 3: Anti-pattern regression check**

Re-ran the four CLAUDE.md anti-pattern categories against the post-audit tree. No surviving unjustified instance of (a) wrapper-around-authoritative, (c) runtime-default reminder, or (d) Manifest restatement. One borderline (b) "Here is what you will receive" shape survives in `agents/implementer.md §Dispatch Inputs` and `agents/reviewer.md §Dispatch Inputs`; flagged in `RESULTS.md` Task 9 §Anti-Pattern Regression as behavior-shaping (the second sentence requires a baseline of what "more than this" means) — orchestrator adjudication left open.

### Task 10: Formalize Post-Audit Refinements
**Depends on:** Task 6, Task 7, Task 8, Task 9
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** Documentation refinement + generator regeneration.
**Input:** Files touched by Tasks 6-8; the researcher's WIP commit `93fda71`.
**Output:** Relocated tolerance rubric, removed inverted cross-reference, propagated role-spec condensation into the regenerated direct-mode refs and Codex TOMLs, fixed typo, and consistent state across all skill/agent surfaces.

- [x] **Step 1: Relocate the drift-test tolerance rubric**

Moved the full tolerance rubric (point estimates, standard errors, counts, signs/significance, document-every-choice example) from `skills/refactor-and-integrate/references/drift-test-quality.md §Tolerance calibration — worked examples` to `skills/econ-data-analysis/references/integrate-drift-tests.md §Tolerance Conventions for Econ Results`. Replaced the source section in `drift-test-quality.md` with a short header noting that tolerance calibration is domain-specific and pointing at the econ reference. Updated the gated-checklist parenthetical so the cross-cutting reference names the domain location rather than its own former section.

- [x] **Step 2: Remove inverted cross-reference in `codebase-integration.md`**

Deleted the `> **Data-analysis work:** also load econ-data-analysis/references/integration.md` blockquote and its HTML comment from `skills/refactor-and-integrate/references/codebase-integration.md`. The reverse pointer (domain → cross-cutting) already lives in `econ-data-analysis/references/integration.md`, which is the correct direction. Also fixed one surviving in-file reference on the decision-tree bullet that still pointed "to the blockquote above"; it now names `econ-data-analysis/references/integration.md` directly.

- [x] **Step 3: Propagate role-spec condensation**

Accepted the researcher's manual condensation of `agents/implementer.md` and `agents/reviewer.md` (WIP commit `93fda71`): shorter §Dispatch Inputs opening, clearer `PLAN.md`-authoritative rule, unified handoff-doc compact etiquette (including the new "Remove superseded content, don't stack it" bullet already authoritative in `handoff-doc §The Four Principles`). Fixed the typo `authorative → authoritative` in `agents/implementer.md` Before-You-Start bullet 3. Additional rough-edge fixes on the re-dispatch pass: restored the missing period in `agents/implementer.md` frontmatter description (`agent Used` → `agent. Used`, matching `reviewer.md`); collapsed the inconsistent blank line inside the compact-etiquette list that separated the fourth bullet ("Doc before report") from the first three in both role files into a single continuous 4-item list. Regenerated `skills/using-superRA/references/direct-mode-{implementer,reviewer}.md` and `.codex/agents/superra_{implementer,reviewer}.toml` via `sync_codex_agents.py --scope project`; `sync_codex_agents.py --scope project --check` is clean, `test_sync_codex_agents.py` 5/5 pass.

### Task 11: Enshrine the Teach-the-Protocol Principle as a Gate
**Depends on:** Task 5
**Review status:** APPROVED
**Integration status:** APPROVED

**Script:** Contributor-doc edit.
**Input:** `CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action` (authored in Task 5).
**Output:** The section now leads with a **"This is a gate."** statement making the principle a blocking check for every future implementer editing files under `skills/*` or `agents/*` (self-apply before commit) and every reviewer (verify on every pass). Because `CLAUDE.md` is auto-loaded for any edit in this repo, the gate propagates without role-spec changes.

- [x] **Step 1: Promote the principle to an explicit gate**

Prepended a `**This is a gate.**` paragraph to the section stating scope (files under `skills/*` and `agents/*`), actor (implementer self-check before commit; reviewer verification on every pass), and severity (a failing line is `[BLOCKING]`, not stylistic). Kept the existing two tests, anti-pattern list, and "Keep" carve-out intact — the gate statement is additive.
