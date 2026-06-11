---
title: "Reference Section"
status: implemented
depends_on:
  - 01-information-architecture
tags: []
created: 2026-06-10
---

## Objective

Write the human-facing reference pages per the approved IA:

- **CLI reference:** the `superra` command surface a researcher actually uses (`task tree`, `task frontier`, `task read`, `dashboard`, comments), with the full mutation surface deferred to a link to `skills/task-tree/references/commands.md`.
- **Task-file reference for humans:** frontmatter fields, body section vocabulary, and the status lifecycle as a table — framing and examples here, with `skills/task-tree/references/task-file-contract.md` linked as the authority.
- **Skill and hook inventories:** the tables currently in `README.md`, moved here as their durable home (coordinate with `09-readme-front-door`).
- **Glossary:** the canonical terms — task tree, task, frontier, rollup, stage, domain skill, drift test, semantic merge, direct/subagent mode — each defined once, in the project's own usage.

Constraints: every page names its authoritative source file; where a skill file already serves humans well the page stays a thin framed pointer rather than a paraphrase; one paragraph per line.

Validation: no reference page contradicts its cited authority; glossary terms match usage across the site's other sections.

## Results

All seven reference pages authored under `docs/site/05-reference/`:

- `task.md` (hub) — one-paragraph orientation with hash links to all seven children.
- `01-task-file/task.md` — frontmatter field table (closed field set), body-section ownership table, minimal leaf-task example; links to `task-file-contract.md` as authority.
- `02-cli-commands/task.md` — day-to-day `superra` commands (tree, frontier, dag, read, dashboard, create, move, comment, check) with code blocks; full mutation surface deferred to `commands.md`.
- `03-status-and-frontier/task.md` — status enum table, lifecycle diagram, frontier definition, rollup rules; links to `task-file-contract.md`.
- `04-skills-and-agents/task.md` — workflow/domain/utility skill tables drawn from `README.md`; Stage → skill load manifest summary; implementer/reviewer agent entries; links to `using-superRA/SKILL.md` and `CATEGORIES.md` as authority.
- `05-glossary/task.md` — thirteen terms defined once each (task tree, task, frontier, status rollup, stage, domain skill, drift test, semantic merge, direct mode, subagent mode, implementer, reviewer, APPROVE/REVISE); each links to its owning concept or skill page.
- `06-faq/task.md` — eight questions covering harness choice, phase-skipping, direct mode, public-repo hygiene, resuming a project, plan-mode materialization, merge-guard, and finding authoritative behavior.
- `07-hooks/task.md` — hook table with trigger, purpose, and per-harness coverage columns (Claude Code / Codex / Cursor); coverage notes; install pointer.

Every page names its authoritative source file and stays a thin framed pointer per the IA constraint.
Glossary terms were verified against the authority files (`task-file-contract.md`, `using-superRA/SKILL.md`, `README.md`, hook scripts) — no contradictions found.
