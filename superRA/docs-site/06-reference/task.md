---
title: "Reference Section"
status: not-started
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
