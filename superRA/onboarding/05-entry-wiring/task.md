---
title: "Route New and Legacy Projects to Onboarding"
status: implemented
depends_on:
  - 03-onboarding-skill
  - 04-isolated-run
---

## Objective

Make onboarding the entry for any project without a task tree, and list the skill in the inventories.

- **Session start** ([main-agent.md](../../../skills/using-superra/references/main-agent.md) §Session Start Actions): a project with code or results but no `superRA/` gets an onboarding offer before the wrapper bootstrap writes anything; the `PLAN.md` line collapses into that offer.
- **`superplan` §Entry Assessment:** existing work with no tree routes to onboarding; `PLAN.md` migration points there.
- **Inventories:** `skills/CATEGORIES.md` (Workflow), `README.md` skill table and the upgrade paragraph that mentions `PLAN.md` migration, and the `task-tree` description and §Migration pointer.
- `tests/harness-instruction-following/test_contract.py` passes, updated where it pins the moved lines.

## Results

A project without a task tree now reaches onboarding from both entry points, and the skill is listed wherever skills are inventoried.

- **Session start** ([main-agent.md](../../../skills/using-superra/references/main-agent.md) §Session Start Actions): a project holding code, data, results, or a legacy `PLAN.md` but no `superRA/` gets the onboarding offer first, and the wrapper bootstrap, `task tree`, `repro status`, and dashboard wait until onboarding creates the tree. The `PLAN.md` bullet is gone; its content lives in onboarding's legacy reference.
- **Planning:** [superplan §Entry Assessment](../../../skills/superplan/SKILL.md) routes existing work or a legacy `PLAN.md` with no tree to onboarding.
- **Inventories:** a Workflow row in [CATEGORIES.md](../../../skills/CATEGORIES.md); an onboarding paragraph in [README.md](../../../README.md) §How it works and the upgrade paragraph's migration sentence; an Ownership Boundaries row and a main-agent load-surface row in [CLAUDE.md](../../../CLAUDE.md); the `.agents/skills/onboarding` symlink the Codex packaging check requires.
- **Left as is:** the `task-tree` description and its §Migration row still name `PLAN.md` migration, because the migrate command's mechanics stay there; onboarding only owns the offer. README has no skill table, so nothing was added there.
- **Checks:** `test_contract.py` 15 passed; `check-harness-compatibility.sh` passes after adding the symlink; Markdown and link checks clean.
