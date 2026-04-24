# Semantic Sync Integration Redesign Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for PLAN.md / RESULTS.md editing. Treat this as skill creation: load `skill-creator`, preserve RA framing and review gates, and keep instructions concise.

**Objective:** Redesign superRA integration so semantic sync is a standalone utility skill, workflow Sync uses generic agents plus semantic-merge mode references, and downstream task agents receive sync intent through task-local annotations.

**Methodology:** Keep one source of truth per concern: `semantic-merge` owns semantic sync and sync review discipline; `integration-workflow` owns choreography; `refactor-and-integrate` owns post-sync quality and consumes Sync Map / task-impact obligations without loading the full semantic-merge skill.

**Domain Vertical:** Skill design / workflow refactor. No data-analysis vertical applies.

**Data Inventory:** Not applicable.

**Conventions:** Canonical behavior lives in root `skills/` and canonical role specs live in `agents/`. Generated Codex role files and direct-mode references are refreshed only through `skills/codex-superra-setup/scripts/sync_codex_agents.py`. Avoid adding role-specific exceptions to the canonical implementer/reviewer files when a skill-owned reference can carry the behavior.

**Output:** Updated workflow, semantic-merge mode references, handoff anatomy, role docs, generated Codex artifacts, tests, and public/contributor documentation.

**Expected Results / Hypotheses:** The revised workflow dispatches generic sync author and sync reviewer agents that load semantic-merge mode references; `## Sync Map` records branch-level thesis and clusters; affected task blocks carry short `**Sync impact:**` pointers; both workflow and standalone modes land exactly one minimal merge commit that leaves existing protection passing, with broader propagation deferred to `refactor-and-integrate` (workflow) or the caller (standalone).

**Sensitivity Analysis:** Verify stale `Stage: sync` / branch-level exception language is removed or intentionally retained only as compatibility text. Verify integration reviewers do not need to load full semantic-merge.

**Pipeline:** Not applicable. Verification commands are listed in Task 5.

---

## Workflow Status

- [x] **Plan approved** - researcher approved the revised generic-agent / mode-reference design in chat; Task 6 added to address sync-map-format ownership and procedural symmetry; Task 7 added to reframe both skills as tool skills and split at the semantic-vs-codebase coherence boundary.
- [ ] **Execution complete** - Tasks 1-6 APPROVED; Task 7 pending.
- [ ] **Drift tests created** - not applicable for this skill-design change.
- [ ] **Integrated** - pending after Task 7 approval.
- [ ] **Docs finalized** - pending after Task 7 approval.
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
> **Rationale (if given):** The one-minimal-commit + defer-all design was clean but heavy for simple cases (invoking `refactor-and-integrate` for a two-line doc fix) and artificial for the natural 1+N merge pattern. Carving the skill boundary at *semantic* vs *codebase* coherence gives a principled split: semantic-merge owns everything needed to make the merge's meaning fully represented in the tree; refactor-and-integrate owns everything needed to make the resulting code fit the host project. Each skill carries the techniques its scope requires — no duplication, no forced cross-skill dispatch for small cases. Workflow impact: adds Task 7; previous one-minimal-commit decision becomes superseded.

---

### Task 1: Refactor semantic-merge around shared principles and mode references
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** *(pending)*

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
  Create or update a reference for direct semantic-merge use outside integration-workflow. It reconstructs current-branch intent when no PLAN.md already carries it, creates a merge-specific record when needed, lands exactly one minimal merge commit that leaves existing tests and drift tests passing, and defers broader propagation to the caller (or to `refactor-and-integrate` invoked after the skill returns).

---

### Task 2: Rewrite integration-workflow Sync choreography for generic agents
**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:** *(pending)*

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

### Task 6: Restructure semantic-merge skill for owner-located formats and symmetric procedural richness
**Depends on:** Task 1, Task 2, Task 3, Task 4, Task 5
**Review status:** APPROVED
**Integration status:** *(pending)*

**Files:** `skills/semantic-merge/SKILL.md`, `skills/semantic-merge/references/workflow-sync-author.md`, `skills/semantic-merge/references/workflow-sync-reviewer.md`, `skills/semantic-merge/references/standalone-merge.md`, `skills/semantic-merge/references/sync-quality.md`, `skills/semantic-merge/references/sync-map-format.md` (to be deleted), `skills/handoff-doc/references/plan-anatomy.md`, `skills/refactor-and-integrate/references/codebase-integration.md`, `skills/integration-workflow/SKILL.md`, and any other file pointing at `sync-map-format.md`.
**Input:** Current semantic-merge skill (after Task 3 DRY consolidation), the post-review decision above, and the global `semantic-merge-integration` skill as the procedural reference point.
**Output:** Format specs live with their owning mode (workflow Sync Map + task-local Sync impact in `workflow-sync-author.md`; Standalone Merge Record in `standalone-merge.md`); `sync-map-format.md` is deleted; shared procedural knowledge (intent classification by role, regeneration preference, stale-reference sweep, mid-operation / dirty-state handling, synthesis preference) lives in `SKILL.md` so both modes carry equal richness; mode references shrink to mode-specific process + format + status return.

- [x] **Step 1: Expand SKILL.md body with shared procedural flow**
  Added a canonical "Shared Procedure" section in `skills/semantic-merge/SKILL.md` covering repo-state grounding (branch / worktree / mid-operation / merge base / incoming range / touched files), reversible-stash dirty-state handling, intent research with role classification (behavior/API, data/schema, docs/narrative, generated outputs, tests, config/build), synthesis-then-regeneration preference, research-meaningful escalation, resolve-and-land, and a stale-reference sweep at verification. RA framing preserved: agent classifies and executes within each role; research-meaningful calls inside data, tests, and analysis outputs go to the researcher.

- [x] **Step 2: Move Workflow Sync Map and task-local Sync impact format into `workflow-sync-author.md`**
  Inlined the full `## Sync Map` template and the task-local `**Sync impact:**` anatomy into `workflow-sync-author.md` next to the process steps that write them. Preserved the parenthetical-inside-bold form `> **Sync review notes (present only while REVISE is active):**`. `workflow-sync-reviewer.md` now points at `workflow-sync-author.md §Workflow Sync Map Format` / `§Task-Local Sync Impact Format` for shape recognition.

- [x] **Step 3: Move Standalone Merge Record format into `standalone-merge.md`**
  Inlined the `SEMANTIC_MERGE.md` merge-record template (headers + File / Script Impact Map) into `standalone-merge.md` next to the step that writes it.

- [x] **Step 4: Delete `sync-map-format.md` and rewire pointers**
  `git rm skills/semantic-merge/references/sync-map-format.md`. Rewired pointers in `skills/semantic-merge/SKILL.md` §Choose a Mode, `skills/semantic-merge/references/workflow-sync-author.md`, `skills/semantic-merge/references/workflow-sync-reviewer.md`, `skills/semantic-merge/references/standalone-merge.md`, `skills/semantic-merge/references/sync-quality.md`, `skills/handoff-doc/references/plan-anatomy.md` (§Sync Map format pointer + §Task-local Sync impact format pointer — now point at `workflow-sync-author.md`), and `skills/integration-workflow/SKILL.md` dispatch templates (dropped `sync-map-format.md` from both sync-author and sync-reviewer reference lists). `skills/refactor-and-integrate/references/codebase-integration.md` did not point at `sync-map-format.md`. Verified: `rg -n "sync-map-format" skills agents README.md CLAUDE.md .codex tests` returns zero matches.

- [x] **Step 5: Trim mode references so they stop repeating the SKILL.md body**
  `workflow-sync-author.md` and `standalone-merge.md` now carry only mode-specific content: inputs, mode-specific process (commit shape, format writes, mode boundary), the format spec, status return. Each reference opens with a pointer to `SKILL.md §Shared Procedure` for the shared flow. `sync-quality.md` was trimmed to the gated checklist plus a one-paragraph pointer that the canonical procedure lives in `SKILL.md §Shared Procedure` and format specs live in the owning mode references; added checklist items for role classification and stale-reference sweep so the reviewer walks what the procedure teaches.

- [x] **Step 6: Verify**
  Ran:
  ```bash
  rg -n "sync-map-format" skills agents README.md CLAUDE.md .codex tests
  python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check
  python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py
  git diff --check
  ```
  First command returned zero matches. Generator check reported all files up to date. Test suite passed 6/6. `git diff --check` clean.

---

### Task 7: Reframe semantic-merge and refactor-and-integrate as tool skills; split at semantic vs codebase coherence
**Depends on:** Task 1, Task 2, Task 3, Task 4, Task 5, Task 6
**Review status:** IMPLEMENTED
**Integration status:** *(pending)*

> **Review notes (2026-04-23):**
>
> 1. [MAJOR] `skills/semantic-merge/references/sync-quality.md:45` — The Verification item says "Generated outputs needing regeneration are listed as post-sync obligations ... regeneration itself is deferred." This contradicts the new Task 7 design. Scope boundary line 21 of the same file says "Generated outputs made stale by the merged sources **are regenerated**, or — when regeneration would change a meaningful result — escalated ... and recorded as a follow-up obligation." SKILL.md §Techniques also names regeneration (not deferral) as the preferred handling for stale generated outputs within the merge's semantic reach. This Verification bullet is stale language carried over from the prior one-minimal-commit design. Fix: rewrite the bullet so it reflects the new rule — generated outputs within semantic reach are regenerated or escalated; only outputs whose regeneration would change a meaningful result (and the codebase-coherence-bounded work) are deferred and listed as post-sync obligations.
>    → implemented: rewrote the Verification bullet at `skills/semantic-merge/references/sync-quality.md:45` — regenerated-within-chain is now the default; regeneration-that-would-change-a-meaningful-result is escalated per `SKILL.md §Techniques` step 4 and recorded as a follow-up obligation; regeneration within semantic reach is not deferred.
>
> 2. [MAJOR] `skills/semantic-merge/references/workflow-sync-reviewer.md:27` — Process Step 8 says "Confirm the sync author did not perform broad refactor, generated-output refresh, drift-test expectation update, or project-doc audit." Under the new Task 7 design, generated-output regeneration *within the merge's semantic reach* is part of semantic coherence and is an expected action for the sync author, not grounds for rejection. As worded, the reviewer is told to penalize the author for doing exactly what SKILL.md §Techniques step 2 and sync-quality.md §Scope boundary line 21 ask them to do. Fix: remove "generated-output refresh" from this item (or qualify it to "broad / out-of-reach generated-output refresh that belongs to codebase coherence") so the reviewer only flags scope creep, not regeneration within semantic reach.
>    → implemented: rewrote Step 8 at `skills/semantic-merge/references/workflow-sync-reviewer.md:27` — now verifies scope boundary at the semantic-vs-codebase-coherence line: generated outputs within semantic reach must be regenerated (or escalated + recorded); codebase-coherence work must be deferred as Sync Map post-sync obligations. Reviewer flags scope creep across that line, not regeneration within semantic reach.
>
> 3. [MINOR] `skills/semantic-merge/references/workflow-sync-reviewer.md:15` — Inputs list "sync commit SHA" (singular) but `skills/integration-workflow/SKILL.md:165` now dispatches the reviewer with plural `Sync commits: <MERGE_COMMIT_SHA>[, <PROPAGATION_SHAS>...]`. Align the reviewer inputs to accept the merge commit SHA plus zero or more propagation commit SHAs, for consistency with the 1+N design.
>    → implemented: pluralized at `skills/semantic-merge/references/workflow-sync-reviewer.md:15` — now `Sync commits (merge commit SHA plus any propagation-commit SHAs)`. Also pluralized lines 3, 7, and 23 where the file described the author landing / the reviewer inspecting a single sync commit, for consistency.
>
> 4. [MINOR] `skills/semantic-merge/references/workflow-sync-author.md:34` — The Workflow Sync Map format header still has a single-SHA `**Sync commit:** <SYNC_COMMIT_SHA>` anchor, while the standalone merge record was correctly broadened to `**Merge commit:**` + `**Propagation commits:**`. Under the 1+N design, the workflow Sync Map should also record the merge commit SHA plus propagation-commit SHAs so the sync reviewer and downstream Integrate can trace the full set. Consider broadening this header (e.g., `**Merge commit:** <sha>` / `**Propagation commits:** <sha1>, <sha2>, ...` or `None`) to match standalone — the existing `Sync review status:` field can stay as-is. Flagged as MINOR because the singular field is not wrong per se (the merge commit is the anchor), just asymmetric and lossy relative to standalone; the orchestrator may accept as-is if they prefer a single anchor SHA in workflow mode.
>    → implemented: broadened the Sync Map header at `skills/semantic-merge/references/workflow-sync-author.md:34` to `**Sync commits:** <MERGE_COMMIT_SHA>[, <PROPAGATION_SHA>...]` (single-line, comma-separated per orchestrator guidance). Also pluralized incidental singular phrasings at lines 47, 73, and 78 of the same file (`Sync resolution`, `DONE` status-return description, and Report bullet) for consistency.

**Files:** `skills/semantic-merge/SKILL.md`, `skills/semantic-merge/references/sync-quality.md`, `skills/semantic-merge/references/workflow-sync-author.md`, `skills/semantic-merge/references/workflow-sync-reviewer.md`, `skills/semantic-merge/references/standalone-merge.md`, `skills/refactor-and-integrate/SKILL.md`, `skills/refactor-and-integrate/references/codebase-integration.md`, `skills/integration-workflow/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`, `skills/using-superRA/SKILL.md`, `CLAUDE.md`, `README.md`, `skills/CATEGORIES.md`.
**Input:** Current semantic-merge + refactor-and-integrate skills (post-Task-6, one-minimal-commit design); the superseding decision in `## Decisions` (semantic-coherence-vs-codebase-coherence reframe).
**Output:** `semantic-merge` is a tool skill teaching techniques for reaching semantic coherence (1 merge commit + N propagation commits as needed within that scope); `refactor-and-integrate` is a tool skill teaching techniques for codebase coherence. `sync-quality.md` is the gated checklist for semantic coherence. The two skills point at each other with one-line pair-relationship notes. Integration-workflow sequences both. No duplicated procedural content.

- [x] **Step 1: Reframe semantic-merge SKILL.md around techniques, not prescribed procedure**
  Rename `## Shared Procedure` -> `## Techniques`. State that the skill is a tool skill: it teaches techniques; integration-workflow sequences them at the macro level; within a single merge operation techniques follow a natural micro-order (investigate before resolving, resolve before landing, record obligations before returning). Keep the six numbered technique blocks (ground in repo state, investigate intent + role classification, build resolution plan, escalate intent-changing choices, resolve and land, detect stale references). Update content only where the new commit-shape rule requires — see Steps 2 and 4.

- [x] **Step 2: Rewrite the stopping rule around semantic coherence**
  Update Technique 5 (Resolve and land): semantic-merge lands 1 merge commit + N propagation commits as needed to reach semantic coherence. Every commit must leave existing protection (drift tests + key-result coverage in workflow mode; existing tests + drift tests in standalone mode) passing — protection-pass is the per-commit lower bound, not the whole-mode stopping rule. Stop when `sync-quality.md §Scope boundary` passes. Broader *codebase* work — naming conventions, utility reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff against host — is out of scope and defers to `refactor-and-integrate`.

- [x] **Step 3: Convert Technique 6 from detection-only to detect-and-resolve**
  The stale-reference sweep enumerates stale references that the merge may have left behind. In the new design, resolving stale references that live within the merge's semantic reach is part of semantic coherence and belongs to semantic-merge. Update the technique text to "detect and resolve" with the scope caveat that broader codebase-fit work defers.

- [x] **Step 4: Rewrite §Workflow Boundary and §Standalone Boundary around the new coherence boundary**
  Workflow Boundary: Sync lands a minimal merge commit plus any propagation commits needed to reach semantic coherence; downstream Integrate handles codebase coherence. Standalone Boundary: semantic-merge carries the merge through to semantic coherence using its own techniques with `sync-quality.md` as the gated checklist; when codebase coherence is also wanted, the caller invokes `refactor-and-integrate` (or handles it manually).

- [x] **Step 5: Rewrite sync-quality.md §Scope boundary to encode semantic coherence**
  Replace the current "exactly one minimal merge commit; broader propagation deferred" items with items that define semantic coherence: stale references resolved within the merge's reach; generated outputs regenerated or escalated; docs describing the merged code updated; no conflict markers; protection passes on every commit; broader codebase-fit work deferred. Keep Intent preservation, Intent integrity, Handoff docs, and Verification sections intact.

- [x] **Step 6: Update workflow-sync-author.md and standalone-merge.md process steps**
  workflow-sync-author.md: Step 4 allows multiple commits within semantic coherence scope; Step 5 records codebase-coherence obligations as Sync Map post-sync obligations. standalone-merge.md: collapse to "land merge commit + propagation commits to semantic coherence; `sync-quality.md` is the checklist; codebase work defers to `refactor-and-integrate` at the caller's discretion." `SEMANTIC_MERGE.md` record format restores a propagation-commit list (1 merge + N propagation SHAs) since standalone now lands multiple commits.

- [x] **Step 7: Update refactor-and-integrate/SKILL.md opening**
  Add a one-line pair-relationship note: "Paired with `semantic-merge`: run `semantic-merge` first to reach semantic coherence; this skill picks up to reach codebase coherence." Frame the skill as tool-shaped (three techniques: drift-test creation, codebase-fit refactor, Sync impact propagation); no prescribed order. Update the Disciplines / references section only if wording drifts from the new framing.

- [x] **Step 8: Rewire cross-references**
  Update `skills/semantic-merge/references/workflow-sync-reviewer.md` any `§Shared Procedure` pointer -> `§Techniques`; same for `workflow-sync-author.md`, `standalone-merge.md`, and `sync-quality.md` opening paragraph. `skills/handoff-doc/references/plan-anatomy.md §Sync Map` and `§Task-local Sync impact` ownership / format pointers still land on `workflow-sync-author.md` — no change needed there. `skills/integration-workflow/SKILL.md` Sync dispatch templates reference `semantic-merge/references/workflow-sync-author.md` + `sync-quality.md` (sync-author) and `workflow-sync-reviewer.md` + `sync-quality.md` (sync-reviewer) — verify still correct.

- [x] **Step 9: Update public / contributor docs**
  `CLAUDE.md §DRY ownership`: describe `semantic-merge` as tools for semantic coherence and `refactor-and-integrate` as tools for codebase coherence. `README.md` and `skills/CATEGORIES.md` utility-skill rows: update one-line summaries to reflect the semantic-vs-codebase split. `skills/using-superRA/SKILL.md` skill-inventory one-liner for semantic-merge: same update.

- [x] **Step 10: Verify**
  Ran:
  ```bash
  rg -n "Shared Procedure" skills agents README.md CLAUDE.md .codex tests
  rg -n "exactly one minimal merge commit|one minimal commit|one sync commit" skills agents README.md CLAUDE.md
  python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check
  python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py
  git diff --check
  ```
  First two rg commands returned zero matches. Generator reported all files up to date. Test suite passed 6/6. `git diff --check` clean. RESULTS.md Task 7 section updated with file-by-file change summary.
