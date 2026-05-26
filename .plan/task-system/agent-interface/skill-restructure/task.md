---
title: "Progressive Skill Revelation"
status: approved
depends_on: []
tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Restructure `skills/task-system/SKILL.md` into three tiers. Current SKILL.md mixes consumer, planner, and contributor concerns.

### Tier 1 — SKILL.md body (consumer-facing)

What implementers and reviewers need to work with `.plan/`:

- **Core concepts:** everything is a task, filesystem = hierarchy, sibling-only deps, status rollup, DAG-derived ordering (no numeric prefixes)
- **How to read a task:** `task_read.py --path <path>` with ancestor context injection
- **How to edit:** directly edit task.md with Read/Edit tools. PostToolUse hooks validate frontmatter and rebuild dashboard automatically
- **Flexible sections:** any `## Heading` is valid and becomes foldable in the dashboard. Recommended defaults: `## Objective` (what success looks like), `## Results` (findings), `## Decisions` (user decisions), `## Review Notes` (reviewer feedback)
- **Frontmatter:** edit directly — `status`, `review_status`, `depends_on`, `tags`, `script`, `input`, `output`. Hooks validate enum values
- **Ownership model:** you own the body sections of your assigned task. You don't own: other tasks' content, scope-defining frontmatter (title, depends_on, script, input, output — those are planner-owned)
- **Task file format:** compact reference showing frontmatter fields + body section example
- **Query tools:** `task_query.py --tree`, `--frontier`, `--dag`
- **Creating tasks:** `task_create.py` auto-fills template with dates and frontmatter defaults

### Tier 2 — `references/planning.md` (planner-facing)

What orchestrators and planners need:

- **Objective writing guide:**
  - An objective describes what success looks like, not how to get there
  - Include: goal, relevant conventions (naming, paths, units, variable definitions), constraints (what NOT to do), input/output expectations, validation criteria
  - Include enough context that an implementer with zero project context can work independently after reading the ancestor chain
  - Necessary steps that need tracking → create as subtasks
  - Suggestive approaches → state as suggestions in prose, e.g. "Consider using a left join on fund_id x date"
  - Do NOT prescribe implementation steps — that's the implementer's job
  - DO prescribe validation criteria — what must be true for the task to be complete

- **Task splitting guide:**
  - A task should be worth reviewing independently — if the review would be trivial ("yes you renamed a variable"), it's too small
  - A task should be worth dispatching — spawn cost (skill-load, context hydration) should be justified by the work
  - A task should be goal-oriented — "merge holdings with characteristics" not "run merge script"
  - Split when: different concerns, different data sources, independent work streams, different domain skills
  - Don't split when: trivially sequential, too small to review, artificially decomposing one logical operation
  - When in doubt: can you describe the task's success criteria in one sentence? If yes, it's the right size

- **Root task.md anatomy:** objective, conventions, workflow status, decisions
- **Retroactive plan creation workflow:** how to create `.plan/` from existing work
- **Hierarchy management:** `task_create.py` (auto-fills template), `task_rename.py`, `task_link.py`

### Tier 3 — `references/internals.md` (contributor-facing)

Move from current SKILL.md:
- `_task_io.py` data layer details (Task dataclass, parse/serialize, walk, frontier, rollup, validation functions)
- Hook architecture and configuration (`task_hook.py`, settings.json)
- Migration (`plan_migrate.py`) details
- Dashboard generation details

### Also update

- `skills/CATEGORIES.md` — update task-system description to reflect new role as primary handoff mechanism
- `README.md` skill inventory — same

## Results

Restructured into three tiers:
- **SKILL.md** (Tier 1): consumer-facing — core concepts, how to read/edit tasks, ownership model, task file format, full command surface. Reduced from mixed-audience monolith to focused implementer/reviewer reference.
- **references/planning.md** (Tier 2): planner-facing — objective writing guide, task splitting heuristics, root task anatomy, retroactive plan creation, hierarchy management commands.
- **references/internals.md** (Tier 3): contributor-facing — `_task_io.py` data layer (Task dataclass, all functions), hook architecture and integration points, migration details, dashboard generation, script inventory.

Also updated:
- `skills/CATEGORIES.md` — updated task-system description to reflect role as primary handoff mechanism and reference structure.
- `README.md` — updated task-system entry in utility skills table to describe the three-tier structure.

## Review Notes

No blocking findings. Three-tier split is clean and well-targeted. SKILL.md (Tier 1) covers consumer needs: core concepts, reading, editing, ownership, format, command surface. `references/planning.md` (Tier 2) covers planner discipline. `references/internals.md` (Tier 3) accurately documents the data layer including new functions. CATEGORIES.md and README.md entries updated consistently.
