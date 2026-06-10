---
title: ".plan/-Native Planning"
status: approved
depends_on:
  - agent-protocols
  - handoff-doc
tags: []
created: 2026-05-24
---

## Objective

Update `skills/superplan/SKILL.md` (formerly `skills/planning-workflow/SKILL.md`) to output the `superRA/` task-tree hierarchy.

### Phases unchanged

- **Phase 1 (Domain Vertical Setup):** domain skill loading is format-independent — no changes needed
- **Phase 2 (Scope Check):** unchanged

### Phase 3 (File Structure) changes

- Walk project docs → populate root task.md `## Conventions` (not PLAN.md `## Project Conventions`)
- Pipeline file guidance unchanged
- Create `.plan/` directory with root task.md containing project-level sections

### Phase 4 (Task Decomposition) — major rewrite

Replace step-based decomposition with subtask-based:
- Tasks are created via `task_create.py` (auto-fills template) or mkdir + write task.md directly
- No checkboxes — tracked steps become subtasks, suggestive steps stay as prose in objective
- Dependencies via `depends_on:` in frontmatter (sibling-only)
- Reference the objective writing guide and task splitting guide from `task-tree/references/planning.md` (defined in skill-restructure task)

### Section rewrites

- **"PLAN.md Is the Task Tracker" → ".plan/ Is the Task Tracker":** same discipline (persistent, committed, authoritative), adapted for filesystem hierarchy. `TodoWrite` is still a transient view, not a record. If losing a task at session end would lose work the researcher cares about, it belongs in `.plan/`
- **"User Feedback and Changing Plans":** adapted for `.plan/` — edit task.md files in place, add/remove subtask directories. Same protocol: confirm intent → log decision in task's `## Decisions` → update in place → sweep for stale content → commit atomically
- **"Living Plan and Results Docs":** results live in task.md body, not separate file. Same inline-edit discipline applies

### Retroactive Plan Creation (new section)

When documenting existing exploratory work into `.plan/`:
1. Survey existing code, outputs, and notebooks
2. Create `.plan/` structure with `task_create.py` — one task per logical unit of work done, with `--status implemented`
3. Edit each task.md to fill body sections with what was done (objective: what was the goal) and found (results: what was discovered)
4. Hooks validate + rebuild dashboard. The plan is now a retroactive record that can drive review, integration, and future work

### Other

- **§Self-Review:** adapted for `.plan/` structure (check subtask coverage, dependency graph sanity, etc.)
- **§Execution Handoff:** creates `.plan/`, commits, hands off to implementation-workflow
- **Remove:** "Save plan to PLAN.md", "Create RESULTS.md alongside" — replaced by .plan/ creation

## Results

### Key Findings

Updated `skills/planning-workflow/SKILL.md` for `.plan/`-native output:

- **Frontmatter description:** Updated triggers from "no PLAN.md" to "no .plan/", "executable plan document" to "executable task tree", "existing PLAN.md rewritten from scratch" to "existing .plan/ rewritten from scratch"
- **Overview:** Output is now `.plan/` task tree, not `PLAN.md` + `RESULTS.md`. Removed "Save plan to PLAN.md" and "Create RESULTS.md alongside" directives.
- **Phase 1-2:** Unchanged (format-independent)
- **Phase 3:** "Walk project docs and cache in root task.md `## Conventions`" replaces "populate PLAN.md `## Project Conventions`". Added step to create `.plan/` directory with root task.md.
- **Phase 4:** Complete rewrite — step-based decomposition replaced with subtask-based. References `task-tree/references/planning.md` §Writing Objectives and §Splitting Tasks. Uses `task_create.py`. No checkboxes. Dependencies via `depends_on:` frontmatter.
- **Retroactive Plan Creation:** New section — survey existing work, create `.plan/` with `--status implemented`, fill body sections.
- **Living Plan and Results:** "PLAN.md Is the Task Tracker" became ".plan/ Is the Task Tracker" — same discipline adapted for filesystem hierarchy. Results live in task.md `## Results` sections.
- **User Feedback and Changing Plans:** Adapted for `.plan/` — edit task.md files in place, add/remove task directories. Decision logging points to task.md `## Decisions` sections.
- **Self-Review:** Added §8 Subtask Coverage check. Adapted existing checks for task tree structure instead of PLAN.md blocks.
- **Execution Handoff:** Commits `.plan/` directory, hands off to implementation-workflow. Removed "check Plan approved box" (no checkboxes in `.plan/`).
- **Removed:** "Plan Document Header and Task Structure" section (now just a pointer to planning.md), "Step Granularity" section (replaced by task-oriented guidance), all `- [ ]` / `- [x]` references.
