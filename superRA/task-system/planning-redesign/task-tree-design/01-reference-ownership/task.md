---
title: "Split Tree Design from Task-File Contract"
status: not-started
depends_on:  []
tags: []
created: 2026-06-09
---

## Objective

Separate workflow judgment from task-file mechanics.

Create the ownership split that the rest of the redesign will build on:

- Move planner-owned tree-design policy out of `skills/task-system/references/planning.md` into a new `skills/superplan/references/task-tree-design.md` reference.
- Keep the new superplan reference focused on decisions an agent makes while designing or changing a task tree: objective/guidance writing, splitting, placement, durable homes, scope expansion, update-task lifecycle, context distillation, and retroactive task-tree creation.
- Rename `skills/task-system/references/planning.md` to a task-file contract name such as `skills/task-system/references/task-file-contract.md`.
- Keep the renamed task-system reference focused on mechanics and file contract: task anatomy, frontmatter fields, status semantics, sibling dependency mechanics, context inheritance mechanics as rendered by `superra task read`, stale-content rules, results shape, section ownership, and figure embedding.
- Update active ownership surfaces so the new boundary is explicit: `AGENTS.md`, `CLAUDE.md` if present as the same contributor alias, `README.md`, `skills/CATEGORIES.md`, `skills/task-system/SKILL.md`, `skills/superplan/SKILL.md`, and any active domain/utility references that cite the old file.

### Context

Use `skill-creator` before editing skill files. Apply the AGENTS.md DRY/Necessity gate line by line. Prefer pointers to the new owner over paraphrases on secondary surfaces.

### Validation

- `rg "task-system/references/planning.md|§Placing Work|§Splitting Tasks|§Writing Objectives|§Retroactive Plan Creation" skills agents README.md AGENTS.md` shows active references now point to the correct owner.
- The renamed task-system reference still gives implementers/reviewers enough task-file contract to read and edit task files without loading superplan.
- Historical task records may keep old citations unless they are active instructions; document any intentionally retained historical references in `## Results`.

## Results
