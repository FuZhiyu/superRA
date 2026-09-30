---
title: "Route New and Legacy Projects to Onboarding"
status: not-started
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
