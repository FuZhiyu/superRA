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
- **Sweep this tree in the same commit.** All 39 task files carrying `## Planner Guidance` — the count at planning time — move to the new heading alongside the contract change, so the tree never reads in two vocabularies.
- **Keep reading the old heading, silently.** Section parsing recognizes `## Planner Guidance` as the same section indefinitely, for trees in other projects and for files this sweep never sees. No warning, no auto-rewrite; agents write `## Additional Information` from here on.
- **`superra task create` gains `--info`**, with `--guidance` kept as a working alias.

Validation: `grep -rn "Planner Guidance"` over `superRA/` returns nothing, and over `skills/` only the parser's alias and the `--guidance` alias; `test_task_tree.py` passes, with coverage for both headings parsing to one section and both flags writing it; a `superra task read` of a task using either heading renders it.

### Context

The section is a `task-tree`-owned part of the task-file contract, so the contract file is the authoritative definition and every other mention points at it. `docs/plans/` holds dated historical records that keep the old name.

## Planner Guidance

- The rename came out of [grilling/02-domain-gates](../../grilling/02-domain-gates/task.md): moving domain surveys into guidance made them invisible to descendants, which exposed that "Planner Guidance" names its author rather than its force. The binding test is what the four domain skills now apply; this task makes it the contract's own rule.
- The dashboard needs no work: it renders body sections generically, so the new heading appears on its own.
