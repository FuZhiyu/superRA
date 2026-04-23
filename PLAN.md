# Semantic Sync Integration Redesign Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for PLAN.md / RESULTS.md editing. Treat this as skill creation: load `skill-creator`, preserve RA framing and review gates, and keep instructions concise.

**Objective:** Redesign superRA integration so semantic sync is a standalone utility step and the integration workflow is easier for agents to follow.

**Methodology:** Keep one source of truth per concern: `semantic-merge` owns semantic sync; `refactor-and-integrate` owns post-sync quality; `integration-workflow` owns choreography.

**Domain Vertical:** Skill design / workflow refactor. No data-analysis vertical applies.

**Data Inventory:** Not applicable.

**Conventions:** Canonical behavior lives in root `skills/` and canonical role specs live in `agents/`. Generated Codex role files and direct-mode references are refreshed only through `skills/codex-superra-setup/scripts/sync_codex_agents.py`.

**Output:** Updated workflow, utility, role, handoff, generated Codex, and public documentation files.

**Expected Results / Hypotheses:** The revised workflow reads as Protect -> Sync -> Integrate -> Document -> Finish; agents dispatch `Stage: sync` for semantic sync and use `BASE_HEAD_SHA..HEAD` for post-sync net-diff review.

**Sensitivity Analysis:** Verify stale terminology is removed or intentionally left only in compatibility pointers.

**Pipeline:** Not applicable. Verification commands are listed in Task 5.

---

## Workflow Status

- [x] **Plan approved** - researcher provided the implementation plan in chat.
- [ ] **Execution complete** - all tasks implemented and verified.
- [ ] **Drift tests created** - not applicable for this skill-design change.
- [ ] **Integrated** - implementation reviewed for stale sync/refactor ownership language.
- [ ] **Docs finalized** - README/CATEGORIES/role docs/generator outputs updated.
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

---

### Task 1: Redesign semantic-merge as standalone semantic sync
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** *(pending)*

**Files:** `skills/semantic-merge/SKILL.md`, `skills/semantic-merge/references/sync-quality.md`, legacy `skills/refactor-and-integrate/references/merge-quality.md`
**Input:** Existing semantic-merge and legacy merge-quality instructions.
**Output:** Semantic-merge owns intent research, conflict resolution, sync commit discipline, Sync Map format, user-decision escalation, and standalone baseline/direction rules.

- [x] **Step 1: Move merge quality ownership**
  Move the actionable legacy merge-quality protocol into a semantic-merge-owned reference. Remove the old refactor-and-integrate reference path unless a compatibility pointer is required.

- [x] **Step 2: Rewrite semantic-merge body**
  Update semantic-merge to frame the workflow as semantic sync: identify the governing baseline/direction, research incoming intent, build a Sync Map, land one sync commit when called from integration-workflow, and return post-sync obligations for later integration.

- [x] **Step 3: Validate scope**
  Search for semantic-merge language that still delegates sync ownership to refactor-and-integrate or references legacy upstream-intent language as the authority.

---

### Task 2: Rewrite integration-workflow choreography
**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:** *(pending)*

**Files:** `skills/integration-workflow/SKILL.md`
**Input:** Existing legacy lettered integration workflow.
**Output:** Clear Protect, Sync, Integrate, Document, Finish workflow.

- [x] **Step 1: Replace phase map and stop points**
  Remove A-D labels from the operational flow. Use named steps: Protect, Sync, Integrate, Document, Finish.

- [x] **Step 2: Add sync anchors**
  Define `PRE_SYNC_BASE_SHA` for incoming intent research and `BASE_HEAD_SHA` for post-sync minimum net diff.

- [x] **Step 3: Split sync from integrate**
  Dispatch one serialized `Stage: sync` implementer for semantic sync, handle research-owned sync decisions through the standard implementer `NEEDS_CONTEXT` / `BLOCKED` statuses, then dispatch integration reviewer over `BASE_HEAD_SHA..HEAD`.

---

### Task 3: Narrow refactor-and-integrate to post-sync quality
**Depends on:** Task 1, Task 2
**Review status:** APPROVED
**Integration status:** *(pending)*

**Files:** `skills/refactor-and-integrate/SKILL.md`, `skills/refactor-and-integrate/references/codebase-integration.md`, `skills/refactor-and-integrate/references/drift-test-quality.md`
**Input:** Existing refactor-and-integrate skill and references.
**Output:** Refactor-and-integrate owns drift-test quality, codebase fit, project doc audit, semantic propagation from Sync Map, and minimum surviving branch delta.

- [x] **Step 1: Remove merge-execution ownership**
  Remove language presenting merge quality as a refactor-and-integrate discipline.

- [x] **Step 2: Update baseline language**
  Replace frozen old-merge-base net-diff language with governing-baseline language, using `BASE_HEAD_SHA..HEAD` for post-sync integration-workflow review.

- [x] **Step 3: Add Sync Map consumption**
  State that post-sync integration review and refactor propagate obligations recorded in `## Sync Map`.

---

### Task 4: Update manifests, role docs, and handoff anatomy
**Depends on:** Task 1, Task 2, Task 3
**Review status:** IMPLEMENTED
**Integration status:** *(pending)*

**Files:** `skills/using-superRA/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`, `agents/implementer.md`, `agents/reviewer.md`, generated direct-mode and Codex agent files.
**Input:** Current manifest, role docs, handoff anatomy, and generated artifacts.
**Output:** `Stage: sync` manifest row; `## Sync Map` ownership and lifecycle; generated artifacts refreshed from canonical role specs.

- [x] **Step 1: Add manifest stage**
  Add `sync` as the integration-workflow Sync step stage that loads `semantic-merge`.

- [x] **Step 2: Replace legacy intent anatomy**
  Replace active legacy upstream-intent handoff guidance with `## Sync Map` guidance owned by the sync agent and consumed by integration review.

- [x] **Step 3: Update role docs and regenerate**
  Update canonical role specs, then run the Codex agent sync script instead of editing generated files by hand.

> **Review notes:**
> 1. [MAJOR] The canonical implementer role still makes every implementer update an assigned task block and set `Review status: IMPLEMENTED`, and its pre-commit check still says every PLAN.md edit must stay inside the assigned task block (`agents/implementer.md:151`, `agents/implementer.md:165`). That contradicts the new branch-level `Stage: sync` path, where there may be no task block and the sync implementer is explicitly allowed to edit header-level `## Sync Map`. Fix the Update Docs / Commit and Pre-Commit Self-Check sections so `Stage: sync` records the Sync Map / sync commit handoff without inventing a task block or failing its own self-check, then regenerate Codex/direct-mode artifacts.
>    → implemented: Update Docs / Commit and pre-commit checks now split task-scoped handoff from `Stage: sync` Sync Map / commit-body handoff, then generated artifacts were refreshed (`agents/implementer.md:151`).
> 2. [MAJOR] The generated direct-mode role references still tell agents that task context/review scope comes from a PLAN.md task block (`skills/using-superRA/references/direct-mode-implementer.md:27`, `skills/using-superRA/references/direct-mode-reviewer.md:33`). Main-agent direct mode loads these generated references instead of raw `agents/*.md`, so direct-mode `Stage: sync` misses the branch-level context added to the canonical roles: PLAN header, `## Decisions`, existing `## Sync Map`, RESULTS.md, and base/ref/current branch state. Update the generator/direct-mode rendering to include the branch-level sync exception for implementer and reviewer direct mode, then regenerate.
>    → implemented: direct-mode rendering now includes `Stage: sync` / branch-level sync context and the generated direct-mode references were refreshed from the generator (`skills/codex-superra-setup/scripts/sync_codex_agents.py:307`).
> 3. [MAJOR] The handoff anatomy gives conflicting placement instructions for `## Sync Map`: the Decisions placement says the header order is `Workflow Status` -> `Decisions` -> `Sync Map` -> `---` -> task blocks, while Project Conventions says it sits between the header separator and the first task block and directly above Decisions when present, and the Sync Map section says it goes after Decisions before the first task block (`skills/handoff-doc/references/plan-anatomy.md:69`, `skills/handoff-doc/references/plan-anatomy.md:73`, `skills/handoff-doc/references/plan-anatomy.md:163`). Spell out one complete top-level order that includes Project Conventions, Decisions, Sync Map, separators, and task blocks, matching where a sync agent should actually insert the temporary section.
>    → implemented: plan anatomy now gives one top-level order with Project Conventions before optional Decisions / Sync Map and the task-block separator after them (`skills/handoff-doc/references/plan-anatomy.md:67`).

---

### Task 5: Update public docs and verify
**Depends on:** Task 1, Task 2, Task 3, Task 4
**Review status:** APPROVED
**Integration status:** *(pending)*

**Files:** `README.md`, `skills/CATEGORIES.md`, `CLAUDE.md`, generated artifacts as needed.
**Input:** Updated skills and role docs.
**Output:** Public and contributor docs aligned with semantic sync design; verification completed.

- [x] **Step 1: Refresh public docs**
  Update README and CATEGORIES to describe Protect -> Sync -> Integrate -> Document -> Finish and the standalone semantic-merge utility.

- [x] **Step 2: Refresh contributor ownership notes**
  Update CLAUDE.md ownership language so `semantic-merge` owns semantic sync and refactor-and-integrate owns post-sync quality.

- [x] **Step 3: Verify**
  Run:
  ```bash
  python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check
  rg -n "Phase A|Phase B|Phase C|Phase D|Stage: merge|Upstream Intent|merge-quality" skills agents README.md CLAUDE.md .codex
  python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py
  ```
