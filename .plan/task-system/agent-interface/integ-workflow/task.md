---
title: ".plan/-Native Integration"
status: not-started
review_status: ~
integration_status: ~
depends_on: 
  - agent-protocols
  - handoff-doc

tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Update `skills/integration-workflow/SKILL.md` for `.plan/`.

### Key changes by phase

- **Protect:** drift tests reference task paths (e.g., `data-preparation/merge`) instead of task numbers. Key-result selection walks `.plan/` tree
- **Sync:** `## Sync Map` section in root task.md (same lifecycle — temporary, removed at Integrate closeout). Task-local sync impact in affected task's `## Sync Impact` section
- **Integrate:** `integration_status:` in frontmatter (already supported by task system). Integration reviewer edits frontmatter directly. Post-sync refactor commits code + task.md
- **Document:** results maturation happens in task.md `## Results` sections, not a separate RESULTS.md. Stage 2 maturation = restructuring/polishing results within each task.md for reader-facing clarity, potentially reorganizing body sections
- **Finish:** `.plan/` is committed as-is. PLAN.md is a manual communication index (no generation step)


## Results

