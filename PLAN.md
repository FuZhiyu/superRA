# Semantic Sync Integration Redesign Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for PLAN.md / RESULTS.md editing. Treat this as skill creation: load `skill-creator`, preserve RA framing and review gates, and keep instructions concise.
>
> **INTEGRATION-SPECIFIC DISCIPLINE (2026-04-23):** This branch itself redesigns superRA's workflow skills, so the installed plugin copy is out of date relative to what this branch teaches. When following any superRA workflow during this integration, **read the skill files directly from this repo** (`skills/<name>/SKILL.md` and `skills/<name>/references/*.md`) rather than calling the `Skill` tool — the in-repo versions are the authoritative contract for this integration pass. This applies to `integration-workflow`, `semantic-merge`, `agent-orchestration`, `refactor-and-integrate`, `handoff-doc`, and `using-superRA`. Pass explicit in-repo reference paths in every dispatch prompt.
>
> **UPSTREAM INTENT TO HONOR:** Main landed the `improve-design-principle` branch (see `docs/plans/2026-04-23-improve-design-principle-plan.md` after sync) which did two things: (1) redesigned the Workflow Frontier Resolver around a reusable re-entry mechanism, and (2) enshrined **"Teach the Protocol, Don't Prescribe Each Action"** as a gated check in `CLAUDE.md` with a Design Audit Checklist. Implementers must self-apply the gate before committing any edit under `skills/*` or `agents/*`; reviewers must verify it on every pass and **hold this gate tightly** when judging our surviving diff. Surviving hunks that restate what the agent already knows from authoritative sources should be trimmed, not preserved — this is also why every refactor follow-up in this integration must pass the **minimum-net-diff self-check** (`git diff BASE_HEAD_SHA..HEAD`) before each commit.
>
> **GENERATED ARTIFACTS — DO NOT HAND-EDIT.** The following files are generated; update the canonical sources + generator, then regenerate:
> - `skills/using-superRA/references/direct-mode-implementer.md`
> - `skills/using-superRA/references/direct-mode-reviewer.md`
> - `.codex/agents/superra_implementer.toml`
> - `.codex/agents/superra_reviewer.toml`
>
> Canonical sources: `agents/implementer.md`, `agents/reviewer.md`. Generator: `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`. Verification: add `--check` (must report up-to-date) and run `python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py` (6/6 passing). Stage regenerated artifacts in the same commit as the canonical-source edit.

**Objective:** Redesign superRA integration so semantic sync is a standalone utility skill, workflow Sync uses generic agents plus semantic-merge mode references, and downstream task agents receive sync intent through task-local annotations.

**Methodology:** Keep one source of truth per concern: `semantic-merge` owns semantic sync and sync review discipline; `integration-workflow` owns choreography; `refactor-and-integrate` owns post-sync quality and consumes Sync Map / task-impact obligations without loading the full semantic-merge skill.

**Domain Vertical:** Skill design / workflow refactor. No data-analysis vertical applies.

**Data Inventory:** Not applicable.

**Conventions:** Canonical behavior lives in root `skills/` and canonical role specs live in `agents/`. Generated Codex role files and direct-mode references are refreshed only through `skills/codex-superra-setup/scripts/sync_codex_agents.py`. Avoid adding role-specific exceptions to the canonical implementer/reviewer files when a skill-owned reference can carry the behavior.

**Output:** Updated workflow, semantic-merge mode references, handoff anatomy, role docs, generated Codex artifacts, tests, and public/contributor documentation.

**Expected Results / Hypotheses:** The revised workflow dispatches generic sync author and sync reviewer agents that load semantic-merge mode references; `## Sync Map` records branch-level thesis and clusters; affected task blocks carry short `**Sync impact:**` pointers; both workflow and standalone modes land one merge commit plus any propagation commits needed to reach semantic coherence, with broader codebase-coherence work deferred to `refactor-and-integrate` (workflow) or the caller (standalone).

**Sensitivity Analysis:** Verify stale `Stage: sync` / branch-level exception language is removed or intentionally retained only as compatibility text. Verify integration reviewers do not need to load full semantic-merge.

**Pipeline:** Not applicable. Verification commands are listed in Task 5.

---

## Workflow Status

- [x] **Plan approved** - researcher approved the revised generic-agent / mode-reference design in chat. Task 6 originally tracked owner-located formats + procedural symmetry; Task 7 originally tracked the tool-skill reframe at the semantic-vs-codebase coherence boundary. Per the 2026-04-23 consolidation decision below, those two APPROVED tasks were collapsed into a single historical Task 6. A new Task 7 was added for the shared-vs-mode-specific clarity pass.
- [x] **Execution complete** - All 7 tasks APPROVED (Task 7 approved in commit `c73c29e`).
- [x] **Drift tests created** - not applicable for this skill-design change.
- [ ] **Integrated** - in progress against `origin/main` (landed `improve-design-principle`, commit `30d6c91`).
- [ ] **Docs finalized** - pending.
- [ ] **Finished** - not requested in this session.

---

## Project Conventions

Walked at planning time (2026-04-23). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at `b6e0640`): Contributor guidance for superRA itself. Skill, hook, agent, and internal-doc edits are behavior-shaping skill creation work. Preserve the four workflow principles, RA framing, DRY ownership boundaries, and canonical shared instructions in `skills/` and `agents/`.
- `/AGENTS.md`: Symlink to `/CLAUDE.md`.
- `/README.md` (HEAD at `b6e0640`): User-facing overview of superRA's PLAN -> IMPLEMENT -> INTEGRATE workflow, skill categories, agents, hooks, and installation. Keep public workflow and utility-skill descriptions aligned with runtime skill behavior.

### Module-level docs walked
- `tests/claude-code/README.md` (HEAD at `b6e0640`): Claude Code skill tests are shell-based and focus on skill loading and expected behavior. Fast tests are preferred by default; integration tests are slow and optional.

### Not walked
- No nested module guidance docs under `skills/` or `agents/` beyond the skill files and references read for this plan.

## Decisions

> **User decision (2026-04-23):** Redesign Sync around generic sync author/reviewer agents plus semantic-merge mode references; keep `## Sync Map` branch-level and add task-local or standalone file-local `Sync impact` annotations.
> **Question asked:** How should semantic sync agents, reviewers, and Sync Map / task-impact responsibilities be structured?
> **Rationale (if given):** Avoid confusing `Stage: sync` exceptions in canonical implementer/reviewer contracts, keep semantic-merge standalone via mode references, avoid costly semantic-merge loads for integration reviewers, and ensure task-scoped agents still receive sync intent. Workflow impact: clears `Execution complete`, `Integrated`, `Docs finalized`, and `Finished`; resets task Review/Integration statuses to pending because the prior Stage-sync design is superseded.

> **User decision (2026-04-23, post-Task-5 review):** Restructure the semantic-merge skill so format specs live with their owning mode (not in a shared `sync-map-format.md`) and shared procedural knowledge lives in the SKILL.md body so both modes carry equal richness.
> **Question asked:** Does sync-map-format.md earn its keep given integration agents do not load it, and did the lean SKILL.md body lose procedural knowledge (role classification, regeneration preference, stale-reference sweep, dirty-state handling) the global semantic-merge skill carried?
> **Rationale (if given):** Integration agents consume Sync Map / Sync impact as prose, not as format spec — the format's only real consumers are the sync author (writer) and sync reviewer (verifier), so the author can own it and the reviewer can point at it; the Standalone Merge Record has a single consumer and collapses into standalone-merge.md. Separately, the "write good sync notes" side of semantic-merge is the valuable output: if the sync author does not classify generated outputs, prefer regeneration, or sweep stale references, the Sync Map obligations they write are thinner than the global skill's equivalent. Workflow and standalone should be symmetric on that procedural knowledge. Workflow impact: adds Task 6; holds `Execution complete`, `Integrated`, and `Docs finalized` until Task 6 is APPROVED.

> **User decision (2026-04-23, post-Task-6 clarification):** Collapse the sync commit shape to a single unambiguous rule for both modes — land exactly one minimal merge commit that leaves existing protection passing; defer broader propagation to Integrate (workflow) or to the caller / `refactor-and-integrate` (standalone).
> **Question asked:** What does "exactly one sync commit" mean — does it include semantic propagation or only mechanical conflict resolution — and should workflow vs standalone have different commit-shape rules (1 vs 1+N)?
> **Rationale (if given):** Two different commit-shape patterns across modes (1 vs 1+N) is confusing and blurs the Sync / Integrate boundary. A single rule — "one minimal commit that passes existing protection" — uses the Protection step (drift tests + key-result coverage from `integration-workflow` Phase A, or existing tests / drift tests for standalone) as the unambiguous definition of "not broken." Broader propagation (caller updates for renames, output regeneration, drift-test expectation updates, project-doc audit) defers out of semantic-merge's scope. Workflow impact: refines Task 6's semantic-merge output; no new task block needed. **Superseded by the 2026-04-23 semantic-coherence-vs-codebase-coherence decision below.**

> **User decision (2026-04-23, Task 7 — skill-boundary reframe):** Split `semantic-merge` and `refactor-and-integrate` at the semantic coherence vs codebase coherence boundary. Reframe both skills as tool skills (techniques, not prescribed procedures); semantic-merge carries through to semantic coherence (1 merge commit + N propagation commits as needed); refactor-and-integrate handles codebase coherence (convention fit, utility reuse, Project Doc Audit walk-up, minimum net diff). `sync-quality.md` becomes the gated checklist for semantic coherence.
> **Question asked:** If semantic-merge agents already carry every technique needed for semantic coherence (role classification, stale-reference detection, regeneration preference, intent preservation), should they just carry through the propagation themselves — with `sync-quality.md` as the specialized checklist — rather than defer to `refactor-and-integrate` for work they could do with their own tools?
> **Rationale (if given):** The one-minimal-commit + defer-all design was clean but heavy for simple cases (invoking `refactor-and-integrate` for a two-line doc fix) and artificial for the natural 1+N merge pattern. Carving the skill boundary at *semantic* vs *codebase* coherence gives a principled split: semantic-merge owns everything needed to make the merge's meaning fully represented in the tree; refactor-and-integrate owns everything needed to make the resulting code fit the host project. Each skill carries the techniques its scope requires — no duplication, no forced cross-skill dispatch for small cases. Workflow impact: adds Task 7 (subsequently consolidated into Task 6 per the 2026-04-23 consolidation decision below); previous one-minimal-commit decision becomes superseded.

> **User decision (2026-04-23, post-Task-7 consolidation + shared-vs-mode-specific clarity):** Consolidate the APPROVED Task 6 and Task 7 into a single historical Task 6 block; add a new Task 7 that tightens the shared-vs-mode-specific split in `semantic-merge`. In the new Task 7: `SKILL.md` should teach only shared principles — core intent rule, techniques, coherence checklist, and the parallel-worktree exception — while mode references carry the mode boundary, inputs, mode-specific process, format, and report/status. The `Workflow Boundary` and `Standalone Boundary` sections currently in `SKILL.md` move into `workflow-sync-author.md` and `standalone-merge.md` respectively. `sync-quality.md` is absorbed into `SKILL.md` as §Semantic Coherence Checklist and deleted as a separate reference.
> **Question asked:** Does the current semantic-merge skill cleanly separate shared principles from mode-specific details? Where should `## Workflow Boundary` / `## Standalone Boundary` live? Does a separate `sync-quality.md` earn its keep when every call path loads it?
> **Rationale (if given):** After Task 6 the mode differences reduce to inputs (dispatch-supplied vs inferred), artifact format (Sync Map + task-impact vs `SEMANTIC_MERGE.md`), and communication target (orchestrator status vs caller report); the boundary sections are mode scope statements that belong with their mode, not in the shared body. `sync-quality.md` is a must-load on every call path (sync author dispatch, sync reviewer dispatch, standalone), and `SKILL.md` is always loaded when the skill is used — folding the checklist into `SKILL.md` removes a file without reducing availability and preserves the shared-flow-checklist invariant (implementer and reviewer walk the same section). Workflow impact: clears `Execution complete`, `Integrated`, `Docs finalized`, and `Finished`; resets new Task 7 to pending.

> **User decision (2026-04-23, integration kickoff):** Enter `integration-workflow` Sync + Integrate against `origin/main` (commit `30d6c91`, merged `improve-design-principle`). Anchors: `PRE_SYNC_BASE_SHA=b6e0640`, `BASE_HEAD_SHA=30d6c91`.
> **Question asked:** Which base does this branch integrate against, and what upstream intent from main must this integration honor?
> **Rationale (if given):** Main landed the `improve-design-principle` branch on 2026-04-23, which (a) redesigned the Workflow Frontier Resolver and (b) enshrined "Teach the Protocol, Don't Prescribe Each Action" as a gated check in `CLAUDE.md` with a Design Audit Checklist. The integration must adopt both upstream changes and honor the anti-over-prescription gate on our surviving diff — reviewers hold it tightly, implementers run the minimum-net-diff self-check before each commit.

> **User decision (2026-04-23, integration discipline — authoritative skill source):** During this integration, dispatched agents MUST read the in-repo skill files under `skills/<name>/SKILL.md` and `skills/<name>/references/*.md` directly rather than invoking the `Skill` tool. The installed plugin copy is behind this branch's redesign, so invoking `Skill` would load stale contracts. Each dispatch prompt explicitly lists the in-repo reference paths the agent must open.
> **Question asked:** How should agents access superRA skills when this branch is the superior / authoritative version relative to the installed plugin?
> **Rationale (if given):** The whole point of this branch is to tighten integration-rule skills beyond the installed version; loading those same skills via the `Skill` tool would defeat the purpose. Following the in-repo files keeps the workflow dog-fooding its own current design.

> **User decision (2026-04-23, workflow Sync Map current-intent field):** Workflow-mode Sync Maps should not restate current-branch intent; `PLAN.md` / `RESULTS.md` already carry it. The Sync Map records incoming intent and the resolution thesis.
> **Question asked:** Should workflow Sync Map `### Branch Summary` include a `Current branch intent` field?
> **Rationale (if given):** Repeating current branch intent inside the Sync Map duplicates the authoritative plan record and creates another stale-content surface.

## Sync Map

**Base branch:** `origin/main`
**Pre-sync merge base:** `b6e0640efce48e9dbf2ca9cec9ac1e310aaf82b3`
**Synced base head:** `30d6c911c9a2fb62582ad948fd4de82b0b2bf150`
**Incoming range:** `b6e0640..30d6c91`
**Sync commits:** `865339c` (merge commit of `origin/main` at `30d6c91` into `tighten-integration-rules`), `e7acf40` (Sync Map SHA propagation), `ff082f4` (generator follow-through)
**Sync review status:** APPROVED

### Branch Summary

**Incoming intent:** Main landed the `improve-design-principle` branch (PR #21), which (1) redesigned the Workflow Frontier Resolver around a reusable re-entry mechanism owned by `using-superRA/references/main-agent.md`, and (2) enshrined the **"Teach the Protocol, Don't Prescribe Each Action"** principle as a gated check in `CLAUDE.md` with a Design Audit Checklist. Every edit under `skills/*` and `agents/*` must now pass the DRY + Necessity tests. Main's diff applied these tests across role specs, workflow skills, and utility/domain skills, producing trimmed instruction surfaces.

**Resolution thesis:** Honor both intents without contradiction. Adopt main's clean `CLAUDE.md` wholesale as the new contributor-facing contract — it subsumes our branch's principle-list framing and adds the Ownership Boundaries table we need, plus the gated Teach-the-Protocol check. Extend main's Ownership Boundaries table to reflect the approved `semantic-merge` (semantic coherence) / `refactor-and-integrate` (codebase coherence) split from this branch's Task 6. For every role spec, workflow skill, and utility file where main trimmed lines and this branch kept rich structure, apply main's trim on top of our structure. Preserve our redesigned workflow vocabulary (`Protect` / `Sync` / `Integrate` / `Document` / `Finish`; `semantic coherence` stopping rule; `## Sync Map` + `**Sync impact:**`) because the redesign is the whole point of the branch.

### Sync Clusters

> **Sync cluster `S1-teach-the-protocol-clean-rewrite` (2026-04-23):** commits in `b6e0640..30d6c91`; paths `CLAUDE.md`; affects no tasks directly (branch-level contract). **Incoming intent:** Main rewrote `CLAUDE.md` into a leaner contributor guide — renamed sections (`Internal Design Philosophy`, `Ownership Boundaries` table, `Architectural Patterns`, `Design Audit Checklist`), added the "Teach the Protocol, Don't Prescribe Each Action" gate, and dropped the prose-heavy Design Principles block. **Sync resolution:** Adopted main's new `CLAUDE.md` wholesale. Updated the Ownership Boundaries table so `semantic-merge` owns semantic-coherence techniques + Sync Map/impact formats + workflow/standalone sync modes, and `refactor-and-integrate` owns codebase-coherence techniques + drift tests + Sync impact propagation (replacing main's single `refactor-and-integrate` "drift-test/refactor/integration/merge-quality" row). **Post-sync obligations:** Integration reviewer must hold the Teach-the-Protocol gate tightly when judging the surviving diff on `30d6c91..HEAD`; `git diff --check` was clean at merge commit. **User decision:** None — resolution followed the kickoff decision.

> **Sync cluster `S2-role-spec-trim-overlap` (2026-04-23):** commits in `b6e0640..30d6c91`; paths `agents/implementer.md`, `agents/reviewer.md`, `skills/using-superRA/references/direct-mode-implementer.md`, `skills/using-superRA/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`, `skills/codex-superra-setup/scripts/sync_codex_agents.py`; affects no tasks directly (branch-level role contract). **Incoming intent:** Main's Task 6 applied the Teach-the-Protocol gate to `agents/implementer.md` and `agents/reviewer.md`, trimming wrapper instructions (§Stage → skills, §What the dispatch carries, §Worktree field steering, §Editing Etiquette duplication of `handoff-doc`), and regenerated the direct-mode refs + Codex TOMLs via `sync_codex_agents.py`. **Sync resolution:** Took main's trim for §Before You Start and §Editing Etiquette on both roles. Rewrote the `cleanup_reviewer_handoff` hook in the generator to be a no-op (main's version targeted an obsolete `## Upstream Intent` paragraph this branch's redesign replaced with Sync Map / Sync impact). Regenerated all four artifacts; `test_sync_codex_agents.py` 6/6 passes and `sync_codex_agents.py --scope project --check` is clean (idempotent regeneration). **Post-sync obligations:** Integration reviewer should re-verify the trimmed `agents/*.md` bodies still carry every behavior-shaping instruction (commit hygiene, `→ implemented:` protocol, `→ orchestrator:` annotations, CRITICAL escalation, `Integration status` flip mechanics) — main's trim was wholesale over-prescription removal, not behavior loss. **User decision:** None.

> **Sync cluster `S3-workflow-vocabulary-overlap` (2026-04-23):** commits in `b6e0640..30d6c91`; paths `skills/planning-workflow/SKILL.md`, `skills/implementation-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`, `skills/handoff-doc/SKILL.md`, `skills/report-in-markdown/SKILL.md`, `skills/report-in-markdown/references/final-form.md`, `skills/econ-data-analysis/SKILL.md`, `skills/econ-data-analysis/references/integrate-drift-tests.md`, `skills/refactor-and-integrate/SKILL.md`, `skills/refactor-and-integrate/references/codebase-integration.md`, `skills/refactor-and-integrate/references/drift-test-quality.md`, `skills/semantic-merge/SKILL.md`; affects Tasks 1, 2, 7. **Incoming intent:** Main's Task 7 trimmed workflow skills around a new `using-superRA/references/main-agent.md §Workflow Frontier Resolver` that owns cross-phase re-entry; Task 8 trimmed utility/domain skills. Main also kept its `Phase A/B/C/D` vocabulary and `Upstream Intent` scaffolding where ours used `Protect/Sync/Integrate/Document/Finish` + `Sync Map / Sync impact`. **Sync resolution:** Honored main's trims for per-row contextualization in the stage-scoped references table (`econ-data-analysis/SKILL.md`), figure-directory narration in `report-in-markdown/SKILL.md`, `final-form.md` caller description, and Step 7 of `planning-workflow §User Feedback` (now points at the Workflow Frontier Resolver rather than restating drift-test re-run logic; kept the full-drift-test-suite invariant as a one-liner because it is behavior-shaping). Preserved our redesigned vocabulary wherever it conflicted: Step 4 of `implementation-workflow` keeps "Protect, Sync, Integrate, Document, Finish"; `integration-workflow/SKILL.md` keeps Steps 3/4/§When to Lighten/Red Flags as redesigned; `refactor-and-integrate/SKILL.md` keeps the three-techniques framing and drops the merge-quality reference (deleted by us); `semantic-merge/SKILL.md` keeps our redesigned Shared Steps + Semantic Coherence Checklist (dropped main's inline advisory about caller verification and the floating parallel-worktree note — already covered by §Exception). In `codebase-integration.md`, removed the inverted `econ-data-analysis/integration.md` blockquote per main's Task 10 decision (domain → cross-cutting pointers only) and kept our tighter "same governing diff" phrasing (main's version referenced obsolete `<frozen-merge-base>`). In `plan-anatomy.md §Field-by-Field Notes`, synthesized main's trimmed Review/Integration-status notes with our `**Sync impact:**` bullet. **Post-sync obligations:** Integration reviewer should grep for any residual `Phase A/B/C/D`, `Upstream Intent`, or `frozen-merge-base` references outside `docs/plans/`; the surviving Sync-Map-vocabulary surface is what refactor-and-integrate obligations will propagate. Affects Tasks 1 (semantic-merge), 2 (integration-workflow Sync choreography), and 7 (shared-vs-mode-specific split). **User decision:** None.

**Note on advancing base:** `origin/main` advanced to `61588d9` during the sync (commits `a40613b`, `c337e96`, `61588d9` — merge of PR #22 `header-adaption`, refining `planning-workflow` Phase 3 header-field handling). The dispatch anchors this Sync to `30d6c91` per the kickoff decision; a re-sync against the new `origin/main` HEAD will be needed before Finish (Sync Step 1 freshness check in `integration-workflow`). That re-sync is out of scope for this Sync round.

**Note on generated artifacts:** `skills/using-superRA/references/direct-mode-implementer.md`, `skills/using-superRA/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, and `.codex/agents/superra_reviewer.toml` are generated from `agents/implementer.md`, `agents/reviewer.md`, and the generator script `skills/codex-superra-setup/scripts/sync_codex_agents.py` — never hand-edit. This Sync resolved the canonical sources + the generator first, then ran `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` to regenerate all four artifacts; regeneration was idempotent on the second pass (`--check` clean, `test_sync_codex_agents.py` 6/6). If Integrate or later Sync rounds touch the canonical sources, regenerate through the script and stage the artifacts in the same commit.

---

### Task 1: Refactor semantic-merge around shared principles and mode references
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** *(pending)*
**Sync impact:** Cluster `S3-workflow-vocabulary-overlap` trimmed `semantic-merge/SKILL.md` via the teach-the-protocol gate; surviving `## Choose a Mode` + `## Shared Steps` + `## Semantic Coherence Checklist` must stay free of runtime-default reminders and wrapper narration when Integrate audits the governing diff. Source: `PLAN.md ## Sync Map`.

**Files:** `skills/semantic-merge/SKILL.md`, `skills/semantic-merge/references/sync-quality.md`, `skills/semantic-merge/references/workflow-sync-author.md`, `skills/semantic-merge/references/workflow-sync-reviewer.md`, `skills/semantic-merge/references/standalone-merge.md`, `skills/semantic-merge/references/sync-map-format.md`.
**Input:** Current semantic-merge skill, Sync Map reference, and the revised generic-agent design decision.
**Output:** A lean semantic-merge body that teaches shared ideas and directs agents to mode-specific references for workflow sync authoring, workflow sync review, standalone full merge, and sync-map / impact formats.

- [x] **Step 1: Keep only shared semantic sync ideas in the skill body**
  State the core intent-before-lines principle, research-owned escalation rule, branch/ref anchoring rule, and separation between semantic sync/propagation and broad codebase refactor. Move mode-specific workflow detail into references.

- [x] **Step 2: Add workflow sync author mode**
  Create or update a reference for a generic sync author agent called by integration-workflow. It reads existing `PLAN.md` / `RESULTS.md`, resolves incoming/current intent, lands the workflow sync commit, writes branch-level `## Sync Map`, and adds task-local `**Sync impact:**` pointers for affected tasks without performing broad refactor.

- [x] **Step 3: Add workflow sync reviewer mode**
  Create or update a reference for a generic sync reviewer agent. It verifies anchors, incoming intent, conflict resolution, user-decision logging, Sync Map completeness, task-local Sync impact coverage, and scope boundary before Integrate begins.

- [x] **Step 4: Add standalone full merge mode**
  Create or update a reference for direct semantic-merge use outside integration-workflow. It reconstructs current-branch intent when no PLAN.md already carries it, creates a merge-specific record when needed, lands one merge commit plus propagation commits needed to reach semantic coherence, and defers broader codebase-coherence work to the caller or `refactor-and-integrate`.

---

### Task 2: Rewrite integration-workflow Sync choreography for generic agents
**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:** *(pending)*
**Sync impact:** Cluster `S3-workflow-vocabulary-overlap` kept our Protect/Sync/Integrate/Document/Finish step structure and §When to Lighten while absorbing main's trim elsewhere; Integrate must grep for any residual `Phase A/B/C/D`, `Upstream Intent`, or `frozen-merge-base` language outside `docs/plans/` and remove it. Source: `PLAN.md ## Sync Map`.

**Files:** `skills/integration-workflow/SKILL.md`, `skills/agent-orchestration/SKILL.md` if dispatch-shape ownership needs a pointer.
**Input:** Current Protect -> Sync -> Integrate workflow and semantic-merge mode references from Task 1.
**Output:** Sync dispatch uses generic agents that load semantic-merge mode references; a sync reviewer gates the transition into Integrate.

- [x] **Step 1: Keep base/ref anchoring in the workflow**
  Preserve target-base confirmation, fetch, `PRE_SYNC_BASE_SHA`, and `BASE_HEAD_SHA` computation in integration-workflow because choreography and stop points remain workflow-owned.

- [x] **Step 2: Dispatch a generic sync author**
  Replace specialized `Stage: sync` implementer dispatch with a generic-agent dispatch that explicitly loads `semantic-merge` and its workflow-sync-author reference. The dispatch passes `BASE_REF`, `PRE_SYNC_BASE_SHA`, `BASE_HEAD_SHA`, and incoming range.

- [x] **Step 3: Add sync review before Integrate**
  Dispatch a generic reviewer-style agent that loads `semantic-merge` and its workflow-sync-reviewer reference. Integrate starts only after sync review approves the sync commit, Sync Map, and task-local Sync impact annotations.

- [x] **Step 4: Define revise / blocked routing**
  Keep the orchestrator as arbitrator: sync review findings are adjudicated before re-dispatch; research-owned conflicts are logged in `## Decisions` before the sync author resumes; repeated or CRITICAL disagreements go to the researcher.

---

### Task 3: Define Sync Map, task-local Sync impact, and standalone file-impact anatomy
**Depends on:** Task 1, Task 2
**Review status:** APPROVED
**Integration status:** *(pending)*

**Files:** `skills/handoff-doc/references/plan-anatomy.md`, `skills/semantic-merge/references/sync-map-format.md`, semantic-merge mode references, `skills/refactor-and-integrate/references/codebase-integration.md`.
**Input:** Existing `## Sync Map` anatomy and the decision to keep branch-level and task-local sync state distinct.
**Output:** A single authoritative branch-level Sync Map plus short task-local pointers that make sync intent visible to task-scoped integration agents.

- [x] **Step 1: Narrow `## Sync Map` to branch-level thesis**
  Define `## Sync Map` as the high-level merge thesis: base/ref anchors, incoming/current intent summary, sync clusters, resolution summary, affected tasks/files, user decisions, and post-sync obligations.

- [x] **Step 2: Add task-local `Sync impact` annotation**
  Define a compact task-block field for affected tasks. It points to the relevant Sync Map cluster and states the task-specific integration obligation. It is not a second authoritative copy of the full Sync Map.

- [x] **Step 3: Add standalone file/script impact map**
  For standalone semantic-merge mode, define a merge record format that includes branch summary plus file/script impact rows when no PLAN.md task structure exists.

- [x] **Step 4: Specify ownership and lifecycle**
  Sync author writes Sync Map and task/file impact annotations; sync reviewer verifies them and records sync-review status / notes in the Sync Map; integration implementers/reviewers consume them; the orchestrator removes temporary Sync Map scaffolding only after obligations are satisfied and task-local statuses reflect the integrated state.

---

### Task 4: Simplify canonical role docs and post-sync integration consumption
**Depends on:** Task 1, Task 2, Task 3
**Review status:** APPROVED
**Integration status:** *(pending)*

**Files:** `agents/implementer.md`, `agents/reviewer.md`, `skills/using-superRA/SKILL.md`, `skills/refactor-and-integrate/SKILL.md`, `skills/refactor-and-integrate/references/codebase-integration.md`, generated direct-mode and Codex agent files.
**Input:** Current role docs with branch-level `Stage: sync` exceptions and the revised semantic-merge mode design.
**Output:** Canonical implementer/reviewer contracts stay task-oriented; Sync-specific behavior lives in semantic-merge references; integration agents consume Sync impact through refactor-and-integrate without loading semantic-merge.

- [x] **Step 1: Remove sync-specific role exceptions**
  Delete or replace canonical implementer/reviewer language that says branch-level `Stage: sync` changes their normal ownership model. Keep only the generic task/review contract and point sync dispatches at semantic-merge references instead.

- [x] **Step 2: Update the skill-load manifest**
  Remove `sync` as a normal superRA task stage if it is no longer dispatched through named implementer/reviewer agents, or retain only a backward-compatibility note that generic Sync dispatches load semantic-merge directly through their prompt.

- [x] **Step 3: Teach integration agents to consume Sync impact**
  Move the lightweight consumption protocol into refactor-and-integrate: read task-local `Sync impact`, follow the referenced Sync Map cluster, verify obligations against `BASE_HEAD_SHA..HEAD`, and avoid reconstructing incoming intent from git history.

- [x] **Step 4: Regenerate generated role artifacts**
  Run the Codex agent sync script after canonical role edits. Do not hand-edit generated direct-mode references or `.codex/agents` files.

---

### Task 5: Update public docs and verify the revised design
**Depends on:** Task 1, Task 2, Task 3, Task 4
**Review status:** APPROVED
**Integration status:** *(pending)*

**Files:** `README.md`, `skills/CATEGORIES.md`, `CLAUDE.md`, generated artifacts as needed, tests under `skills/codex-superra-setup/scripts/` or `tests/claude-code/` as needed.
**Input:** Updated skills, references, workflow choreography, role docs, and generated artifacts.
**Output:** Public and contributor docs aligned with generic Sync dispatch, standalone semantic-merge mode behavior, sync review, and task-local Sync impact annotations.

- [x] **Step 1: Refresh public and contributor docs**
  Update README, CATEGORIES, and CLAUDE.md so they describe semantic-merge as a standalone utility with mode references, Sync as a generic-agent workflow step with a dedicated sync review, and refactor-and-integrate as the consumer of task-local Sync impact.

- [x] **Step 2: Add or update verification coverage**
  Update tests or generator checks that assume `Stage: sync` is a canonical named-agent stage. Add coverage for generated direct-mode references if their sync content is removed or replaced.

- [x] **Step 3: Verify**
  Run:
  ```bash
  python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check
  python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py
  git diff --check
  rg -n "Stage: sync|At sync stage|branch-level sync review|sync implementer|sync reviewer agent uses|Upstream Intent|merge-quality|NEEDS_USER_DECISION" skills agents README.md CLAUDE.md .codex tests -g '*.md' -g '*.toml' -g '*.py'
  ```
  Inspect the search results rather than requiring zero matches; the goal is to confirm remaining legacy sync terms are intentional.

---

### Task 6: Restructure semantic-merge as a tool skill at the semantic-vs-codebase coherence boundary
**Depends on:** Task 1, Task 2, Task 3, Task 4, Task 5
**Review status:** APPROVED
**Integration status:** *(pending)*

**Files:** `skills/semantic-merge/SKILL.md`, all four `skills/semantic-merge/references/*.md` (with `sync-map-format.md` deleted), `skills/refactor-and-integrate/SKILL.md`, `skills/refactor-and-integrate/references/codebase-integration.md`, `skills/integration-workflow/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`, `skills/using-superRA/SKILL.md`, `CLAUDE.md`, `README.md`, `skills/CATEGORIES.md`.
**Input:** Post-Task-5 semantic-merge (lean SKILL.md body; separate `sync-map-format.md`; one-minimal-commit rule with all propagation deferred). See the two post-Task-5 decisions in `## Decisions` for the design rationale (owner-located formats + symmetric procedural richness; tool-skill reframe at the semantic-vs-codebase coherence boundary).

**Output:**
- Format specs owned by their mode: Workflow Sync Map + task-local Sync impact in `workflow-sync-author.md`; Standalone Merge Record in `standalone-merge.md`. `sync-map-format.md` deleted.
- `SKILL.md` body carries shared techniques (repo-state grounding with reversible-stash dirty-state handling; intent investigation with role classification across behavior/API, data/schema, docs/narrative, generated outputs, tests, config/build; resolution plan with synthesis + regeneration preference; intent-changing escalation with `handoff-doc §User Decisions Log` pointer; resolve-and-land; detect-and-resolve stale references). Framed as tool-skill techniques, not prescribed procedure.
- Commit-shape rule reset: 1 merge commit + N propagation commits as needed to reach **semantic coherence**; per-commit protection-pass is the lower bound; `sync-quality.md §Scope boundary` is the whole-mode stopping rule. Codebase-coherence work (convention fit, utility reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff) defers to `refactor-and-integrate`.
- `refactor-and-integrate` reframed as a paired tool skill: opens with "Paired with `semantic-merge`: run `semantic-merge` first to reach semantic coherence; this skill picks up to reach codebase coherence." Three techniques (drift-test creation, codebase-fit refactor, Sync impact propagation), no prescribed order.
- Public/contributor docs (CLAUDE.md §DRY ownership, README.md, CATEGORIES.md, using-superRA Skill Inventory) updated to the semantic-vs-codebase-coherence framing.

**Verification:** `rg` scans for `sync-map-format`, `Shared Procedure`, and legacy one-commit phrasings all return zero matches. Codex generator + tests pass. `git diff --check` clean. (Task ran in two APPROVED passes recorded in git history — owner-located formats + procedural symmetry, then the tool-skill reframe — consolidated here per the 2026-04-23 consolidation decision.)

---

### Task 7: Clarify shared-vs-mode-specific content in semantic-merge
**Depends on:** Task 6
**Review status:** APPROVED
**Integration status:** *(pending)*
**Sync impact:** Cluster `S3-workflow-vocabulary-overlap` — main's teach-the-protocol trim touched `semantic-merge/SKILL.md §Choose a Mode` with a parallel-worktree advisory that we already own in §Exception, and added a caller-verification note the Semantic Coherence Checklist's §Scope boundary already carries. Integrate verifies the absorbed checklist and §Exception still cover those points without re-introduced duplication. Source: `PLAN.md ## Sync Map`.

**Files:** `skills/semantic-merge/SKILL.md`, `skills/semantic-merge/references/workflow-sync-author.md`, `skills/semantic-merge/references/workflow-sync-reviewer.md`, `skills/semantic-merge/references/standalone-merge.md`, `skills/semantic-merge/references/sync-quality.md` (to be deleted), `skills/integration-workflow/SKILL.md`, `CLAUDE.md`.

**Input:** Post-Task-6 semantic-merge plus the researcher's in-flight uncommitted hand-edits (2026-04-23) that rename `## Techniques` back to `## Shared Steps` with a simple opener and drop Process Step 5 (codebase-coherence obligation recording) from `workflow-sync-author.md`. `SKILL.md` still carries mode-specific `## Workflow Boundary` and `## Standalone Boundary` sections. `sync-quality.md` is a separate must-load reference loaded on every call path (sync-author dispatch, sync-reviewer dispatch, standalone).

**Output:**
- `SKILL.md` carries only shared content: core principle, mode selection, §Shared Steps (renamed from §Techniques per researcher edit, with the terse "The following steps are shared by all modes." opener), §Semantic Coherence Checklist (absorbed from `sync-quality.md`), and the parallel-worktree Exception. No mode-specific boundary sections remain.
- Mode references each carry: §Boundary + §Inputs + §Mode-Specific Process + §Format + §Status/Report. The main differences between modes reduce to their essential axis — inputs (dispatch-supplied vs inferred), artifact format (Sync Map + task-impact vs `SEMANTIC_MERGE.md`), and communication target (orchestrator status vs caller report).
- `workflow-sync-author.md` process is 4 steps (not 5); codebase-coherence obligations are recorded in §Boundary + Sync Map post-sync obligations, not as a separate process step. Status Return reports the full sync commit chain.
- `sync-quality.md` is deleted; its gated checklist lives as a `##` section of `SKILL.md` since the skill body is always loaded when any mode is used. Shared-flow-checklist invariant preserved: implementer and reviewer walk the same section.
- All pointers rewired to `SKILL.md §Semantic Coherence Checklist` (or its sub-section `§Scope boundary`). Integration-workflow dispatch templates drop `sync-quality.md` from reference lists. CLAUDE.md §DRY ownership updated.

- [x] **Step 1: Adopt researcher's in-flight edits as the starting baseline.**
  Keep the `## Shared Steps` rename (from `## Techniques`) and the terse opener "The following steps are shared by all modes." Keep `workflow-sync-author.md` process at 4 steps (no codebase-obligation step 5) and make the Status Return report the full sync commit chain.

- [x] **Step 2: Move `## Workflow Boundary` into `workflow-sync-author.md` as §Boundary at the top.**
  Carry forward the semantic-coherence stopping rule and the deferral of codebase-coherence work to `refactor-and-integrate` via Integrate. The reviewer reference inherits the same boundary by reviewing the same work; point the reviewer's opener at the author's §Boundary rather than restating it.

- [x] **Step 3: Move `## Standalone Boundary` into `standalone-merge.md` as §Boundary at the top.**
  Carry forward the semantic-coherence stopping rule and the caller-level deferral of codebase-coherence work to `refactor-and-integrate` or manual handling.

- [x] **Step 4: Absorb `sync-quality.md` into `SKILL.md` as §Semantic Coherence Checklist.**
  Keep the `[BLOCKING]` / `[ADVISORY]` structure and sub-headings (Intent preservation, Scope boundary, Intent integrity, Handoff docs, Verification). Preserve the shared-flow-checklist invariant: implementer and reviewer walk the same section.

- [x] **Step 5: Rewire all pointers.**
  - Mode references: drop "Also load `sync-quality.md`" lines; point at `SKILL.md §Semantic Coherence Checklist` for the checklist walk.
  - `SKILL.md §Shared Steps` step 5 (Resolve and land): `sync-quality.md §Scope boundary` → `§Semantic Coherence Checklist §Scope boundary`.
  - `integration-workflow/SKILL.md` sync-author and sync-reviewer dispatch bodies: drop `semantic-merge/references/sync-quality.md` from reference lists; update `sync-quality.md §Scope boundary` narration to the SKILL.md section.
  - `CLAUDE.md §DRY ownership`: `sync-quality.md §Scope boundary` → `SKILL.md §Semantic Coherence Checklist §Scope boundary`.
  - Delete `skills/semantic-merge/references/sync-quality.md` via `git rm`.

- [x] **Step 6: Verify.**
  Run:
  ```bash
  rg -n "sync-quality" skills agents README.md CLAUDE.md .codex tests
  rg -n "Workflow Boundary|Standalone Boundary" skills/semantic-merge/SKILL.md
  python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check
  python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py
  git diff --check
  ```
  First two rg commands should return zero matches; generator check should report up-to-date; test suite 6/6; `git diff --check` clean.
