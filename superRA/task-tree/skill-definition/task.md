---
title: "Skill Definition + Inventory"
status: approved
depends_on:
  - core-data-layer
  - cli-scripts
  - dashboard
---

## Objective

Own the task-tree skill's definition surface: `SKILL.md`, the task-file contract, and the skill inventory.

- **`SKILL.md`** carries core concepts (everything is a task, `## Objective` planner-owned, `## Results` implementer-owned and recursive, filesystem hierarchy, sibling-only deps, status rollup), directory structure, the command surface with examples, the task-file template, and migration docs.
- **The task-file contract names the body sections and the test that sorts them.** Binding content — what a reviewer rejects work against — goes in `## Objective`; everything else is information and goes in `## Details`. A task read injects an ancestor's objective and nothing else, so the same test decides what a subtree inherits, and each skill classifies its own artifacts against it.
- **Trees written under the old vocabulary keep working.** The retired `## Planner Guidance` heading parses as `## Details` indefinitely — no warning, no file rewrite — and `superra task create` takes `--details` with `--guidance` as an alias.
- **Inventory:** `CATEGORIES.md` and the `README.md` skill list stay current.

## Results

[`skills/task-tree/SKILL.md`](../../../skills/task-tree/SKILL.md) is a routing layer over three references — [commands.md](../../../skills/task-tree/references/commands.md), [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md), [internals.md](../../../skills/task-tree/references/internals.md) — with migration reached by a pointer to `internals.md §Migration`. `commands.md` gained a `superra task check` row and a §Diagnostics section; `CATEGORIES.md` and `README.md` carry discovery-level skill descriptions.

**The binding test lives in [task-file-contract.md §Task Anatomy](../../../skills/task-tree/references/task-file-contract.md).** `task-tree-design.md` sorts objective lines *by* that test rather than restating it, under §Writing Objectives and Details. The rename reached every live surface — the superplan spine and its references, both role skills, `main-agent.md`, the four domain planning references, `commands.md`, and the CLI scripts and tests — plus all 46 task files under `superRA/` and the two [showcase fixtures](../../../docs/showcase-fixtures/), so the tree never read in two vocabularies. `docs/plans/` keeps the old name as dated history.

**Legacy compatibility is a parse-time alias, not a migration.** `_SECTION_ALIASES` in [_task_io.py](../../../skills/task-tree/scripts/_task_io.py) maps the old heading to `Details`, verified on a scratch tree outside this repo: `task read` of a legacy-heading task prints `## Details`. `--details` and `--guidance` share one argparse dest; the Python kwarg is `details=`.
