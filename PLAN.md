# Workflow Frontier Resolver Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. Load `skill-creator` before editing any `skills/*/SKILL.md`. This is a package-design change, not a data-analysis task. Task statuses describe the current workflow frontier; do not mark tasks `APPROVED` until a reviewer has actually approved them.

**Objective:** Redesign the Workflow Frontier Resolver so it teaches a small reusable mechanism for workflow re-entry instead of a lengthy taxonomy of contingency outcomes.

**Methodology:** Keep only the runtime guidance agents are unlikely to infer reliably: the canonical workflow map, the adaptability principle, the durable evidence to inspect, the decision object to return, the affected-task closure rule, owner routing, and safety invariants. Remove contingency-tree prose and duplicated phase-selection logic from workflow skills.

**Data Inventory:** Not applicable. This change edits package documentation and skill references only.

**Conventions:** Preserve one source of truth per concern: `using-superRA` owns cross-stage overview and skill loading; `main-agent.md` owns main-agent autonomy and re-entry mechanism; workflow skills own local phase gates; `handoff-doc` owns document state semantics; `agent-orchestration` owns dispatch and review-loop mechanics.

**Output:** Updated runtime skill/reference docs plus this `PLAN.md` and `RESULTS.md` handoff pair.

**Expected Results / Hypotheses:** Agents should understand the PLAN -> IMPLEMENT -> INTEGRATE cycle, why re-entry is adaptive, and how to compute the next safe frontier without needing an enumerated scenario tree. The resolver's value added should be limited to evidence discipline, affected-frontier calculation, workflow-owner routing, and non-negotiable gates.

**Sensitivity Analysis:** Verify the same mixed-state acceptance case as before: when a completed task changes after implementation or integration, only the changed task plus affected downstream dependents lose local validity, unrelated approved work remains preserved, rollup milestones are unchecked only where false, and global gates still rerun before merge / PR.

**Pipeline:** Not applicable. Verification is static documentation audit plus `git diff --check`.

---

## Workflow Status

- [x] **Plan approved** - researcher requested the material redesign toward mechanisms over contingency prose on 2026-04-23.
- [ ] **Execution complete** - Tasks 1-4 approved and closed, but Tasks 5-9 (over-prescription audit) were added 2026-04-23 and are not yet implemented.
- [ ] **Drift tests created** - not yet reached; documentation/package integration gate remains pending.
- [ ] **Refactored** - not yet reached; integration review remains pending.
- [ ] **Docs finalized** - not yet reached; this RESULTS.md is Stage 1 handoff state.
- [ ] **Merged** - branch has not been merged or opened as a PR by this workflow.

## Project Conventions

Walked at planning time (2026-04-23). Re-walk on-demand only.

### Repo root
- `/AGENTS.md`: contributor-facing entry point. It says superRA internal changes should be evaluated against adaptive/composable workflow design, DRY ownership, lean agents with rich references, and skill-authoring discipline when editing `skills/*/SKILL.md`.
- `/CLAUDE.md`: currently modified in this worktree as part of the broader contributor-guide cleanup. Preserve that outstanding change and do not conflate it with the frontier-resolver task.
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

---

### Task 1: Add Runtime Workflow Overview and Resolver Value Proposition
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** *(not started)*

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
**Integration status:** *(not started)*

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
**Integration status:** *(not started)*

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
**Integration status:** *(not started)*

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
**Integration status:** *(not started)*

**Script:** Not applicable; contributor-doc edit.
**Input:** `CLAUDE.md` (aliased from `AGENTS.md` / `AGENT.md`).
**Output:** New `CLAUDE.md` subsection under `## Internal Design Philosophy` naming the principle, stating the two tests (DRY, necessity), listing anti-patterns, and adding a line-level check to the Design Audit Checklist.

- [x] **Step 1: Add the principle and anti-patterns**

Add a subsection titled "Teach the Protocol, Don't Prescribe Each Action" after `### Minimal, Targeted Instructions`. State the governing test (without this line, would the agent's behavior be unstable?), the two ordered sub-tests (DRY, then necessity), and concrete anti-patterns drawn from the current repo: wrapper instructions around authoritative content (e.g., `Worktree:` steering), "here is what you will receive" descriptions of the dispatch prompt, reminders of runtime defaults, and restatements of the Skill-Load Manifest inside dispatch or role bodies. Contrast with behavior-shaping instructions that must be kept.

- [x] **Step 2: Extend the Design Audit Checklist**

Add a single-line check to `## Design Audit Checklist`: for every added line, does removing it change what the agent would *do*, or only what it would *understand*? If only understand, delete it.

### Task 6: Audit Agent Role Specs and `using-superRA` Surfaces
**Depends on:** Task 5
**Review status:** *(not started)*
**Integration status:** *(not started)*

**Script:** Line-by-line instruction audit against the Task 5 principle; edits applied inline.
**Input:** `agents/implementer.md`, `agents/reviewer.md`, `skills/using-superRA/SKILL.md` and all files under `skills/using-superRA/references/` (including `main-agent.md`, `codex-instructions.md`, `claude-tools.md`, and any generated `direct-mode-*.md` — edit source specs and regenerate rather than editing generated files directly).
**Output:** Trimmed role specs / runtime surfaces, a findings note in `RESULTS.md` summarizing what was cut, replaced with a pointer, or kept with rationale. Verify generated direct-mode reference files are regenerated from their canonical agent specs.

- [ ] **Step 1: Survey each file line by line**

For every paragraph, bullet, and sentence, apply the two tests from `CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action`: (a) is this already carried by another authoritative source the agent reads? (b) without this line, would agent behavior be unstable? Classify each line as KEEP / POINTER / DELETE and record the rationale in `RESULTS.md` Task 6 findings.

- [ ] **Step 2: Apply the edits and regenerate**

Trim DELETE lines; replace POINTER lines with a one-line reference to the authoritative source. When editing anything that feeds generated direct-mode role references, update the canonical source spec and regenerate per `CLAUDE.md §Architectural Patterns`.

- [ ] **Step 3: Verify no behavior was lost**

Cross-check each DELETE / POINTER decision against the authoritative source it points at — the source must actually carry the deleted content. Note any gap where a deleted line exposed a real missing instruction elsewhere and fix by adding the line to its correct owner.

### Task 7: Audit Workflow Skills and `agent-orchestration`
**Depends on:** Task 5
**Review status:** APPROVED
**Integration status:** *(not started)*

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
**Review status:** *(not started)*
**Integration status:** *(not started)*

**Script:** Line-by-line instruction audit against the Task 5 principle; edits applied inline.
**Input:** `skills/handoff-doc/`, `skills/refactor-and-integrate/`, `skills/report-in-markdown/`, `skills/semantic-merge/`, `skills/worktree-data-sync/`, `skills/econ-data-analysis/`, `skills/codex-superra-setup/` — each skill's `SKILL.md` plus all files under its `references/`.
**Output:** Trimmed utility / domain / meta skills, a findings note in `RESULTS.md` summarizing per-file cuts / pointers / kept lines, and confirmation that domain and utility skills remain standalone-usable (per `CLAUDE.md §Adaptive, Composable Workflows`).

- [ ] **Step 1: Survey each file line by line**

Apply the two tests to each line. For utility / domain / meta skills, additionally check: does this line still make sense when the skill is loaded standalone (without a surrounding workflow)? Classify KEEP / POINTER / DELETE in `RESULTS.md` Task 8 findings.

- [ ] **Step 2: Apply the edits**

Trim DELETEs, replace POINTERs with single-line references. Preserve the standalone-usability guarantee — a utility skill should still work when invoked outside the superRA workflow.

- [ ] **Step 3: Verify standalone usability**

For each domain and utility skill, confirm its `SKILL.md` still reads coherently on its own. Note any follow-up needed in `RESULTS.md` Task 8.

### Task 9: Cross-Audit Consistency Sweep
**Depends on:** Task 6, Task 7, Task 8
**Review status:** *(not started)*
**Integration status:** *(not started)*

**Script:** Whole-repo verification that the audit edits compose cleanly.
**Input:** The full diff produced by Tasks 6-8.
**Output:** A consolidated audit summary in `RESULTS.md` Task 9 listing any residual duplication, pointer targets that do not actually carry the referenced content, and any newly-introduced gaps where a deleted line's content is not recoverable from an authoritative source.

- [ ] **Step 1: Pointer integrity check**

For every POINTER introduced in Tasks 6-8, confirm the cited source actually contains the referenced content at the expected location.

- [ ] **Step 2: Residual-duplication search**

Grep for repeated phrases across `skills/`, `agents/`, and `CLAUDE.md` for behavior-shaping instructions (not just resolver taxonomy) and confirm each concern has a single owner.

- [ ] **Step 3: Anti-pattern regression check**

Re-run the CLAUDE.md anti-pattern tests against the post-audit tree: (a) wrapper instructions around authoritative content, (b) "here is what you will receive" descriptions, (c) reminders of runtime defaults, (d) restatements of the Skill-Load Manifest inside dispatch or role bodies. Any surviving instance must be justified in `RESULTS.md` Task 9 as behavior-shaping.
