---
title: "Split Tree Design from Task-File Contract"
status: approved
depends_on:  []
tags: []
created: 2026-06-09
---

## Objective

Separate workflow judgment from task-file mechanics.

Create the ownership split that the rest of the redesign will build on:

- Move planner-owned tree-design policy out of `skills/task-tree/references/planning.md` into a new `skills/superplan/references/task-tree-design.md` reference.
- Keep the new superplan reference focused on decisions an agent makes while designing or changing a task tree: objective/guidance writing, splitting, placement, durable homes, scope expansion, update-task lifecycle, context distillation, and retroactive task-tree creation.
- Rename `skills/task-tree/references/planning.md` to a task-file contract name such as `skills/task-tree/references/task-file-contract.md`.
- Keep the renamed task-tree reference focused on mechanics and file contract: task anatomy, frontmatter fields, status semantics, sibling dependency mechanics, context inheritance mechanics as rendered by `superra task read`, stale-content rules, results shape, section ownership, and figure embedding.
- Update active ownership surfaces so the new boundary is explicit: `AGENTS.md`, `CLAUDE.md` if present as the same contributor alias, `README.md`, `skills/CATEGORIES.md`, `skills/task-tree/SKILL.md`, `skills/superplan/SKILL.md`, and any active domain/utility references that cite the old file.

### Context

Use `skill-creator` before editing skill files. Apply the AGENTS.md DRY/Necessity gate line by line. Prefer pointers to the new owner over paraphrases on secondary surfaces.

### Validation

- `rg "task-tree/references/planning.md|§Placing Work|§Splitting Tasks|§Writing Objectives|§Retroactive Plan Creation" skills agents README.md AGENTS.md` shows active references now point to the correct owner.
- The renamed task-tree reference still gives implementers/reviewers enough task-file contract to read and edit task files without loading superplan.
- Historical task records may keep old citations unless they are active instructions; document any intentionally retained historical references in `## Results`.

## Results

### Key Findings

- Moved tree-design policy into the superplan-owned reference [task-tree-design.md:1](../../../../../skills/superplan/references/task-tree-design.md#L1). It now owns objective/guidance writing, context distillation, splitting, durable-home placement, scope expansion, update-task lifecycle, and retroactive task-tree creation.
- Renamed the old task-tree planning reference to the task-file contract [task-file-contract.md:1](../../../../../skills/task-tree/references/task-file-contract.md#L1). It now owns task anatomy, frontmatter/status/dependency mechanics, inherited context rendering, stale-content cleanup, results shape, section ownership, and figure embedding.
- Updated active ownership surfaces to point at the new owners, including the contributor ownership table [CLAUDE.md:87](../../../../../CLAUDE.md#L87), the task-tree routing table [SKILL.md:81](../../../../../skills/task-tree/SKILL.md#L81), and superplan's planning workflow references [SKILL.md:16](../../../../../skills/superplan/SKILL.md#L16).

### Validation

- `rg "task-tree/references/planning.md|skills/task-tree/references/planning.md|references/planning.md\\)" skills agents README.md AGENTS.md CLAUDE.md` returned no stale active references to the old task-tree planning file.
- `rg "task-tree/references/planning.md|§Placing Work|§Splitting Tasks|§Writing Objectives|§Retroactive Plan Creation" skills agents README.md AGENTS.md` returned only references pointing to the new superplan tree-design owner where those section titles remain active.
- `python3 skills/report-in-markdown/scripts/check_markdown.py skills/superplan/references/task-tree-design.md skills/task-tree/references/task-file-contract.md superRA/task-tree/planning-redesign/task-tree-design/01-reference-ownership/task.md` reported all three markdown files clean.
- `./superRA/superra task read task-tree/planning-redesign/task-tree-design/01-reference-ownership` rendered the updated task with `status: implemented`.
- A full-repo `rg "task-tree/references/planning.md|skills/task-tree/references/planning.md" .` still finds old paths inside `superRA/` task records. I intentionally retained those task-record citations as historical provenance and did not edit other task files.
