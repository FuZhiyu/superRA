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
**Review status:** IMPLEMENTED
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

> **Review notes:**
> 1. MAJOR [BLOCKING] — `skills/semantic-merge/references/sync-quality.md:44`: the Sync Map format hard-codes `origin/main` as the base branch and incoming range endpoint even though the workflow supports researcher-confirmed release, sibling, or other base refs. This would write wrong handoff evidence for non-main syncs. Replace the hard-coded ref with a placeholder for the confirmed base ref and make the incoming range use the same ref/anchor consistently, e.g. `<PRE_SYNC_BASE_SHA>..<BASE_HEAD_SHA>` or `<PRE_SYNC_BASE_SHA>..<base-ref>`.
>    → implemented: replaced hard-coded `origin/main` with `<base-ref>` and `<PRE_SYNC_BASE_SHA>..<BASE_HEAD_SHA>` in the Sync Map format (`skills/semantic-merge/references/sync-quality.md:44`).

---

### Task 2: Rewrite integration-workflow choreography
**Depends on:** Task 1
**Review status:** IMPLEMENTED
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

> **Review notes:**
> 1. MAJOR [BLOCKING] — `skills/integration-workflow/SKILL.md:75`: the target-base resolution step uses `git merge-base HEAD origin/main ...`, which returns a commit SHA, but the rest of Sync needs a base ref for `git fetch origin <base-branch>`, `git rev-parse origin/<base-branch>`, dispatch, and Sync Map evidence. As written, an agent can log/pass a merge-base SHA as `<resolved-base>` or leave `<base-branch>` undefined. Resolve and record the branch/ref name first, then compute `PRE_SYNC_BASE_SHA` and `BASE_HEAD_SHA` from that confirmed ref.
>    → implemented: `BASE_REF` is now resolved and logged as a branch/ref before fetch, `PRE_SYNC_BASE_SHA`, `BASE_HEAD_SHA`, dispatch context, and final freshness checks use that ref (`skills/integration-workflow/SKILL.md:75`).

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
**Review status:** APPROVED
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
