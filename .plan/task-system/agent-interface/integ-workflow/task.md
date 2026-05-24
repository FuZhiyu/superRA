---
title: ".plan/-Native Integration"
status: approved
review_status: approved
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

Updated `skills/integration-workflow/SKILL.md` for `.plan/`-native operation across all five phases:

- **Frontmatter description:** removed RESULTS.md/PLAN.md references; updated triggers
- **Protect:** key-result extraction walks `.plan/` tree via `task_query.py --tree`; drift tests reference task paths (e.g., `data-preparation/merge`); workflow status flipped in root task.md
- **Sync:** `## Sync Map` lives in root task.md (`.plan/task.md`); task-local sync impact in affected task's `## Sync Impact` body section; decision logging in root task.md `## Decisions`
- **Integrate:** `integration_status:` frontmatter field (lowercase enum values); integration reviewer edits frontmatter directly; review notes in task's `## Review Notes`; refactor commits code + task.md atomically; closeout removes temporary `## Sync Map` and `## Sync Impact` sections
- **Document:** rewritten from RESULTS.md maturation + PLAN.md disposition to in-place maturation of task.md `## Results` sections (Stage 2 per `task-system/references/planning.md` §Results Shape); no file relocation or disposition step
- **Finish:** `.plan/` committed as-is; workflow status in root task.md; removed conditional "if PLAN.md still exists" logic
- **Red Flags / When to Lighten:** updated references from `PLAN.md ## Sync Map` to `root task.md ## Sync Map`, from `Integration status: APPROVED` to `integration_status: approved`

