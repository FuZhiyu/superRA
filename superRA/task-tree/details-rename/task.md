---
title: "Rename the planner-guidance section to Details and state the binding test"
status: implemented
depends_on: []
---

## Objective

Rename the old planner-guidance body section to `## Details`, and make the binding-versus-information test the explicit rule for what goes where.

- **The test belongs in the task-file contract.** Binding content — what a reviewer rejects work against — goes in `## Objective`. Everything else is information and goes in `## Details`. A task read injects an ancestor's objective and nothing else, so the test also decides what descendants inherit.
- **Each skill classifies its own content.** The contract states the test; the domain and workflow skills decide which of their artifacts are binding. econ-data-analysis's data inventory is not binding; theory-modeling's solution concept and assumption map are.
- **Rename every live surface**: [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md), [task-tree-design.md](../../../skills/superplan/references/task-tree-design.md), the `superplan` spine and its references, `implement-task`, `review-task`, [main-agent.md](../../../skills/using-superra/references/main-agent.md), the domain planning references, [commands.md](../../../skills/task-tree/references/commands.md), and the scripts and tests that name the section — [cli.py](../../../skills/task-tree/scripts/cli.py), [task_create.py](../../../skills/task-tree/scripts/task_create.py), [test_task_tree.py](../../../skills/task-tree/scripts/test_task_tree.py). 33 occurrences across 16 files at planning time.
- **Sweep this tree in the same commit.** All 39 task files carrying the old heading — the count at planning time — move to the new heading alongside the contract change, so the tree never reads in two vocabularies.
- **Keep reading the old heading, silently.** Section parsing recognizes the old heading as the same section indefinitely, for trees in other projects and for files this sweep never sees. No warning, no auto-rewrite; agents write `## Details` from here on.
- **`superra task create` gains `--details`**, with `--guidance` kept as a working alias.

Validation: the old heading name appears nowhere under `superRA/`, and under `skills/` only in the parser's alias table and the `--guidance` flag alias; `test_task_tree.py` passes, with coverage for both headings parsing to one section and both flags writing it; a `superra task read` of a task using either heading renders it.

### Context

The section is a `task-tree`-owned part of the task-file contract, so the contract file is the authoritative definition and every other mention points at it. `docs/plans/` holds dated historical records that keep the old name.

## Details

- The rename came out of [grilling/02-domain-gates](../../grilling/02-domain-gates/task.md): moving domain surveys into guidance made them invisible to descendants, which exposed that the old name named its author rather than its force. The binding test is what the four domain skills now apply; this task makes it the contract's own rule.
- The dashboard needs no work: it renders body sections generically, so the new heading appears on its own.

## Results

`## Details` is the section's name everywhere; the old heading survives only as a silent parser alias and the `--guidance` flag.

- **The binding test is stated in the contract**, at [task-file-contract.md §Task Anatomy](../../../skills/task-tree/references/task-file-contract.md) — binding content to `## Objective`, everything else to `## Details`, with inheritance as the consequence and each skill classifying its own artifacts. [task-tree-design.md](../../../skills/superplan/references/task-tree-design.md) now sorts objective lines *by* that test instead of restating it; its section is §Writing Objectives and Details.
- **Legacy files read unchanged.** `_SECTION_ALIASES` in [_task_io.py](../../../skills/task-tree/scripts/_task_io.py) maps the old heading to `Details` at parse time, so a file written under the old vocabulary renders and JSON-serializes as one `Details` section, with no warning and no rewrite of the file. Verified on a scratch tree outside this repo: `task read` of a legacy-heading task prints `## Details`.
- **`task create` takes `--details`**, with `--guidance` as an argparse alias on the same dest; both flags write `## Details`. The Python kwarg is `details=`.
- **Sweep.** 46 task files under `superRA/` plus the two [showcase fixtures](../../../docs/showcase-fixtures/) moved to the new heading; inline prose mentions in the tree — including this task's own objective — were reworded so the old name appears nowhere under `superRA/`. `docs/plans/` was untouched and carries no mention.
- **Untracked stale export.** `superRA/dashboard.html` is a local dashboard export, not tracked; it is not part of the sweep.

Full suite green: 809 passed (`skills/task-tree/scripts`), with the parse test parametrized over both headings and a new flag-alias test.
