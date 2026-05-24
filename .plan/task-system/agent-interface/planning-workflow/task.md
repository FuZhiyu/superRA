---
title: ".plan/-Native Planning"
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

Update `skills/planning-workflow/SKILL.md` to output `.plan/` hierarchy.

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
- Reference the objective writing guide and task splitting guide from `task-system/references/planning.md` (defined in skill-restructure task)

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

