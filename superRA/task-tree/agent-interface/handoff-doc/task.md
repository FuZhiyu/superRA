---
title: "Deprecate Handoff-Doc Skill"
status: approved
depends_on:
  - skill-restructure
tags: []
created: 2026-05-24
---

## Objective

Deprecate `skills/handoff-doc/` — its content is now redundant with the task-tree skill and the agent role specs.

### What was handoff-doc

handoff-doc owned: four document principles, inline-edit rule, stale-content checklist, User Decisions Log format, plan-anatomy templates, results-anatomy templates.

### Why it's redundant

With .plan/ as the primary handoff mechanism:
- **Editing discipline** (inline-edit only, latest state, no strikethroughs) → now embedded in `agents/implementer.md` §Editing Etiquette
- **Task anatomy** → now in `skills/task-tree/references/planning.md`
- **Results shape** → now in `skills/task-tree/references/planning.md` or task-tree consumer tier
- **Ownership rules** → now in `skills/task-tree/SKILL.md` (consumer tier) and agent role specs
- **User Decisions Log** → trivial: "put decisions in `## Decisions` section"
- **Stale-content checklist** → embeddable in role specs or task-tree

### What to do

1. **Merge any remaining unique content** from `skills/handoff-doc/references/` into `skills/task-tree/references/`:
   - Plan-anatomy content (root task.md anatomy, task.md anatomy, field-by-field notes) → merge into `task-tree/references/task-file-contract.md` and `superplan/references/task-tree-design.md`
   - Results-anatomy content (per-task results shape, figure embedding, Stage 2 maturation) → add as a section in `task-tree/references/task-file-contract.md`
   - Stale-content checklist → embed in `task-tree/SKILL.md` consumer tier
   - User Decisions Log format → embed in `superplan/references/task-tree-design.md`

2. **Replace SKILL.md body** with a deprecation redirect:
   ```
   This skill is deprecated. Its concerns are now owned by:
   - Editing discipline: agents/implementer.md §Handoff / agents/reviewer.md §Editing Etiquette
   - Task anatomy and creation: skills/task-tree/ (references/task-file-contract.md) + superplan/references/task-tree-design.md
   - Results format: skills/task-tree/references/task-file-contract.md §Results Shape
   - User Decisions Log: superplan/references/task-tree-design.md
   ```

3. **Update Skill-Load Manifest** in `skills/using-superRA/SKILL.md`:
   - Remove handoff-doc from the `Stage: documentation` row
   - Remove the "main agents additionally load handoff-doc" instruction
   - Remove from skill inventory table

4. **Update CATEGORIES.md and README.md** — remove or mark deprecated

5. **Update CLAUDE.md ownership table** — reassign handoff-doc concerns to task-tree

6. **Remove handoff-doc loads** from any workflow skill that references `superRA:handoff-doc`

## Decisions

> **User decision (2026-05-24):** Deprecate handoff-doc entirely — its content is redundant with task-tree + agent role specs in the .plan/ world.
> **Question asked:** Why do we still have handoff-doc if we're replacing PLAN.md/RESULTS.md with .plan/?
> **Rationale:** Task-system skill now owns format/interaction, agent role specs own discipline, planning-workflow owns creation. No unique concern left for handoff-doc.

## Results

### Key Findings
- Merged all unique content from `handoff-doc/references/` into `task-tree/references/` (content now lives in [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md) and [superplan/references/task-tree-design.md](../../../../skills/superplan/references/task-tree-design.md)): field-by-field notes, User Decisions Log, Conventions section discipline, Workflow Status checkboxes, Stale Content Checklist, Results Shape (two-stage lifecycle, per-task template, section ownership, figure embedding).
- Replaced `handoff-doc/SKILL.md` body with 12-line deprecation redirect.
- Replaced both reference files with one-line redirects.
- Removed handoff-doc from `using-superRA/SKILL.md`: inventory table, Stage: documentation row (replaced with `report-in-markdown`), "main agents additionally load" instruction, Skill-Load Manifest explanatory paragraph.
- Updated 14 files across workflow skills, agent files, utility skills, and domain references to point at `task-tree/references/planning.md` instead of `handoff-doc`.
- Updated CLAUDE.md ownership table, CATEGORIES.md, and README.md.

### Notes
- Historical plan files in `docs/plans/` were NOT updated — they are archival records of past work and their references to handoff-doc are accurate for the time they were written.
- The `implementation-workflow/SKILL.md` "Step 0b: Handoff-Doc Existence Check" heading was not renamed — it still checks for plan file existence and the heading is descriptive of its legacy purpose.
