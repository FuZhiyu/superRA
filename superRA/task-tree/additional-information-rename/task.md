---
title: "Rename Planner Guidance to Additional Information and state the binding test"
status: not-started
depends_on: []
---

## Objective

Rename the `## Planner Guidance` body section to `## Additional Information`, and make the binding-versus-information test the explicit rule for what goes where.

- **The test belongs in the task-file contract.** Binding content — what a reviewer rejects work against — goes in `## Objective`. Everything else is information and goes in `## Additional Information`. A task read injects an ancestor's objective and nothing else, so the test also decides what descendants inherit.
- **Each skill classifies its own content.** The contract states the test; the domain and workflow skills decide which of their artifacts are binding. econ-data-analysis's data inventory is not binding; theory-modeling's solution concept and assumption map are.
- **Rename every live surface**: [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md), [task-tree-design.md](../../../skills/superplan/references/task-tree-design.md), the `superplan` spine and its references, `implement-task`, `review-task`, [main-agent.md](../../../skills/using-superra/references/main-agent.md), the domain planning references, [commands.md](../../../skills/task-tree/references/commands.md), and the scripts and tests that name the section — [cli.py](../../../skills/task-tree/scripts/cli.py), [task_create.py](../../../skills/task-tree/scripts/task_create.py), [test_task_tree.py](../../../skills/task-tree/scripts/test_task_tree.py). 33 occurrences across 16 files at planning time.
- **Existing task files** carrying `## Planner Guidance` — 39 in this tree at planning time — are migrated by the decision recorded below, not left to drift.
- Section-name recognition stays a single source: whatever parses body sections accepts the new name, and the old name's handling follows the migration decision.

Validation: `grep -rn "Planner Guidance"` over `skills/`, `hooks/`, `tests/`, and `superRA/` returns only what the migration decision deliberately leaves; `test_task_tree.py` passes; a `superra task read` of a task with the renamed section renders it.

### Context

The section is a `task-tree`-owned part of the task-file contract, so the contract file is the authoritative definition and every other mention points at it. `docs/plans/` holds dated historical records that keep the old name.

## Planner Guidance

- The rename came out of [grilling/02-domain-gates](../../grilling/02-domain-gates/task.md): moving domain surveys into guidance made them invisible to descendants, which exposed that "Planner Guidance" names its author rather than its force. The binding test is what the four domain skills now apply; this task makes it the contract's own rule.
- Three open decisions for the researcher, unsettled at planning time: whether the parser keeps accepting `## Planner Guidance` as an alias or hard-fails on it; whether the 39 existing task files migrate in one sweep or on next touch; and whether the dashboard label changes with the section name.
