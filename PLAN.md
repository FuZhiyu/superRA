# Worktree Branch Naming Fix Plan

> **For agentic workers:** Use `superRA:handoff-doc` for PLAN.md / RESULTS.md edits. This repo-internal fix follows direct mode: the main agent plays implementer and reviewer in-session.

**Objective:** Replace the parallel-worktree branch naming protocol that creates nested refs under the current branch with a non-conflicting namespace that still contains `/parallel/`.

**Methodology:** Update the owning orchestration instructions and active assertion surfaces only; preserve historical plan/result records as history unless they are active tests or current docs.

**Output:** Updated skill/agent/hook guidance plus regenerated direct-mode artifacts if their source changes.

---

## Workflow Status

- [x] **Plan approved** - researcher requested this direct-mode repo-internal fix.
- [x] **Execution complete** - task implementation approved and targeted verification passed.
- [x] **Merged** - branch pushed and PR opened: https://github.com/FuZhiyu/superRA/pull/23.

---

## Project Conventions

Walked at planning time (2026-04-24). Re-walk on-demand only.

### Repo root
- `AGENTS.md`: contributor discipline for superRA internals; skill edits are skill creation, owning files must be read before editing, generated artifacts stay generated, and the DRY/Necessity tests are blocking gates for `skills/*` and `agents/*` instruction edits.
- `README.md`: user-facing product overview and installation docs; keep contributor/internal protocol details in skill and contributor files rather than duplicating them here.

### Module-level docs walked
- `skills/using-superRA/SKILL.md` and `skills/using-superRA/references/main-agent.md`: direct mode requires role references, self-review, and reviewer discipline.
- `skills/agent-orchestration/SKILL.md`: owns cross-stage dispatch patterns and worktree branch lifecycle protocol.
- `skills/handoff-doc/SKILL.md`: `PLAN.md` / `RESULTS.md` are live committed handoff docs with inline-edit discipline.

### Not walked
- Historical `docs/plans/` records except targeted grep hits; they are not active instruction sources for this fix.

---

### Task 1: Fix parallel worktree branch namespace
**Depends on:** *(none)*
**Review status:** APPROVED

**Input:** Active instruction surfaces matching the old `<branch>/parallel/<slug>` or equivalent pattern.
**Output:** New namespace guidance using `<current-branch>-agent/parallel/<slug>` or an equivalent non-conflicting pattern, with `/parallel/` preserved for `merge-guard`.

- [x] **Step 1: Locate active assertion surfaces.** Searched active skill, agent, hook, test, generated, and top-level doc surfaces. Historical `docs/plans/` records were left untouched.
- [x] **Step 2: Update the owning protocol.** Changed `skills/agent-orchestration/SKILL.md` to create and merge `${current_branch}-agent/parallel/<slug>` branches rather than `${current_branch}/parallel/<slug>`.
- [x] **Step 3: Update active references and source text.** Updated current references, merge-guard comments, implementer source text, generator source string, and regenerated the project-scope Codex implementer artifact.
- [x] **Step 4: Verify behavior.** Ran targeted grep checks, merge-guard regression inputs, generator drift check, and a throwaway Git-ref creation check showing the old pattern fails under an existing leaf ref while the new pattern succeeds.
