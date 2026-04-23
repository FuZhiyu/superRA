# Semantic Sync Integration Redesign Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for PLAN.md / RESULTS.md editing. Treat this as skill creation: load `skill-creator`, preserve RA framing and review gates, and keep instructions concise.

**Objective:** Redesign superRA integration so semantic sync is a standalone utility skill, workflow Sync uses generic agents plus semantic-merge mode references, and downstream task agents receive sync intent through task-local annotations.

**Methodology:** Keep one source of truth per concern: `semantic-merge` owns semantic sync and sync review discipline; `integration-workflow` owns choreography; `refactor-and-integrate` owns post-sync quality and consumes Sync Map / task-impact obligations without loading the full semantic-merge skill.

**Domain Vertical:** Skill design / workflow refactor. No data-analysis vertical applies.

**Data Inventory:** Not applicable.

**Conventions:** Canonical behavior lives in root `skills/` and canonical role specs live in `agents/`. Generated Codex role files and direct-mode references are refreshed only through `skills/codex-superra-setup/scripts/sync_codex_agents.py`. Avoid adding role-specific exceptions to the canonical implementer/reviewer files when a skill-owned reference can carry the behavior.

**Output:** Updated workflow, semantic-merge mode references, handoff anatomy, role docs, generated Codex artifacts, tests, and public/contributor documentation.

**Expected Results / Hypotheses:** The revised workflow dispatches generic sync author and sync reviewer agents that load semantic-merge mode references; `## Sync Map` records branch-level thesis and clusters; affected task blocks carry short `**Sync impact:**` pointers; standalone semantic-merge can complete a full semantic merge with follow-up propagation commits while stopping before broad refactor.

**Sensitivity Analysis:** Verify stale `Stage: sync` / branch-level exception language is removed or intentionally retained only as compatibility text. Verify integration reviewers do not need to load full semantic-merge.

**Pipeline:** Not applicable. Verification commands are listed in Task 5.

---

## Workflow Status

- [x] **Plan approved** - researcher approved the revised generic-agent / mode-reference design in chat.
- [ ] **Execution complete** - revised tasks are pending.
- [ ] **Drift tests created** - not applicable for this skill-design change.
- [ ] **Integrated** - pending after revised implementation and sync/integration review.
- [ ] **Docs finalized** - pending after README/CATEGORIES/role docs/generator outputs are updated.
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

---

### Task 1: Refactor semantic-merge around shared principles and mode references
**Depends on:** *(none)*
**Review status:** IMPLEMENTED
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
  Create or update a reference for direct semantic-merge use outside integration-workflow. It reconstructs current-branch intent when no PLAN.md already carries it, creates a merge-specific record when needed, completes the sync plus follow-up semantic propagation commits, runs relevant checks/drift tests, and stops before broad codebase refactor.

---

### Task 2: Rewrite integration-workflow Sync choreography for generic agents
**Depends on:** Task 1
**Review status:** IMPLEMENTED
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
**Review status:** IMPLEMENTED
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
**Review status:** IMPLEMENTED
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
**Review status:** IMPLEMENTED
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
