---
title: "Deprecate Handoff-Doc Skill"
status: implemented
review_status: revise
integration_status: ~
depends_on: 
  - skill-restructure

tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Deprecate `skills/handoff-doc/` — its content is now redundant with the task-system skill and the agent role specs.

### What was handoff-doc

handoff-doc owned: four document principles, inline-edit rule, stale-content checklist, User Decisions Log format, plan-anatomy templates, results-anatomy templates.

### Why it's redundant

With .plan/ as the primary handoff mechanism:
- **Editing discipline** (inline-edit only, latest state, no strikethroughs) → now embedded in `agents/implementer.md` §Editing Etiquette
- **Task anatomy** → now in `skills/task-system/references/planning.md`
- **Results shape** → now in `skills/task-system/references/planning.md` or task-system consumer tier
- **Ownership rules** → now in `skills/task-system/SKILL.md` (consumer tier) and agent role specs
- **User Decisions Log** → trivial: "put decisions in `## Decisions` section"
- **Stale-content checklist** → embeddable in role specs or task-system

### What to do

1. **Merge any remaining unique content** from `skills/handoff-doc/references/` into `skills/task-system/references/`:
   - Plan-anatomy content (root task.md anatomy, task.md anatomy, field-by-field notes) → merge into `task-system/references/planning.md`
   - Results-anatomy content (per-task results shape, figure embedding, Stage 2 maturation) → add as a section in `task-system/references/planning.md` or a new `task-system/references/results-guide.md`
   - Stale-content checklist → embed in `task-system/SKILL.md` consumer tier
   - User Decisions Log format (3-line blockquote) → embed in `task-system/references/planning.md`

2. **Replace SKILL.md body** with a deprecation redirect:
   ```
   This skill is deprecated. Its concerns are now owned by:
   - Editing discipline: agents/implementer.md §Editing Etiquette
   - Task anatomy and creation: skills/task-system/ (references/planning.md)
   - Results format: skills/task-system/ (references/planning.md §Results)
   - User Decisions Log: skills/task-system/ (references/planning.md §Decisions)
   ```

3. **Update Skill-Load Manifest** in `skills/using-superRA/SKILL.md`:
   - Remove handoff-doc from the `Stage: documentation` row
   - Remove the "main agents additionally load handoff-doc" instruction
   - Remove from skill inventory table

4. **Update CATEGORIES.md and README.md** — remove or mark deprecated

5. **Update CLAUDE.md ownership table** — reassign handoff-doc concerns to task-system

6. **Remove handoff-doc loads** from any workflow skill that references `superRA:handoff-doc`

## Decisions

> **User decision (2026-05-24):** Deprecate handoff-doc entirely — its content is redundant with task-system + agent role specs in the .plan/ world.
> **Question asked:** Why do we still have handoff-doc if we're replacing PLAN.md/RESULTS.md with .plan/?
> **Rationale:** Task-system skill now owns format/interaction, agent role specs own discipline, planning-workflow owns creation. No unique concern left for handoff-doc.

## Results

### Key Findings
- Merged all unique content from `handoff-doc/references/` into `task-system/references/planning.md`: field-by-field notes, User Decisions Log, Conventions section discipline, Workflow Status checkboxes, Stale Content Checklist, Results Shape (two-stage lifecycle, per-task template, section ownership, figure embedding).
- Replaced `handoff-doc/SKILL.md` body with 12-line deprecation redirect.
- Replaced both reference files with one-line redirects.
- Removed handoff-doc from `using-superRA/SKILL.md`: inventory table, Stage: documentation row (replaced with `report-in-markdown`), "main agents additionally load" instruction, Skill-Load Manifest explanatory paragraph.
- Updated 14 files across workflow skills, agent files, utility skills, and domain references to point at `task-system/references/planning.md` instead of `handoff-doc`.
- Updated CLAUDE.md ownership table, CATEGORIES.md, and README.md.

### Notes
- Historical plan files in `docs/plans/` were NOT updated — they are archival records of past work and their references to handoff-doc are accurate for the time they were written.
- The `implementation-workflow/SKILL.md` "Step 0b: Handoff-Doc Existence Check" heading was not renamed — it still checks for plan file existence and the heading is descriptive of its legacy purpose.

## Review Notes

> 1. [MAJOR] Codex generator script and generated agents not updated. [`skills/codex-superra-setup/scripts/sync_codex_agents.py:311`](skills/codex-superra-setup/scripts/sync_codex_agents.py#L311) and [`:324`](skills/codex-superra-setup/scripts/sync_codex_agents.py#L324) contain hard-coded references to `handoff-doc`. The generated `.codex/agents/superra_implementer.toml` (3 occurrences) and `.codex/agents/superra_reviewer.toml` (3 occurrences) still direct agents to load the deprecated skill. Per `CLAUDE.md` §Codex and Harness Design, update the generator script text and regenerate the toml files.
> 2. [MINOR] Corrupted section symbol. [`skills/using-superRA/SKILL.md:43`](skills/using-superRA/SKILL.md#L43) and [`skills/handoff-doc/SKILL.md:10`](skills/handoff-doc/SKILL.md#L10) have two U+FFFD replacement characters where a `§` should be (before "Editing Etiquette" for `agents/implementer.md`). Replace with the correct `§` character.
