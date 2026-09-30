---
title: "Author the Onboarding Skill Spine and Setup References"
status: not-started
depends_on:
  - 01-retroactive-tree
  - 02-retroactive-graph
---

## Objective

Create `skills/onboarding/SKILL.md` carrying the six-stage choreography from the parent objective, and the references for version-control setup and legacy `PLAN.md` migration.

- **SKILL.md:** each stage's action and its stop point, the writes-only-in-`superRA/` rule for stages 1–3, pointers to the owning skills, and a routing table to its references. Frontmatter description names the triggers: a project without `superRA/`, a legacy `PLAN.md`, or a researcher asking to adopt superRA.
- **Concept explanations** for a new user, each given where the concept first appears: `superRA/` and tasks (stage 1–2, including that the researcher may delete anything there), the dashboard (stage 2), the reproduction graph (stage 3), worktrees and merging (stages 5–6, owned by [04-isolated-run](../04-isolated-run/task.md)).
- **`references/project-setup.md`** (stage 4): create git when absent; a `.gitignore` excluding data, generated outputs, and caches, settled with the researcher for ambiguous large files; a data-handling note in the project's `CLAUDE.md` / `AGENTS.md` (created if absent) saying where data lives and that it is never committed; a baseline commit of the untouched project, then the `superRA/` commit. A project already in git: check `.gitignore` coverage and commit `superRA/` on a topic branch.
- **`references/legacy-plan-migration.md`:** the `PLAN.md` migration offer and `superra task migrate from-plan`, moved from [main-agent.md](../../../skills/using-superra/references/main-agent.md) §Session Start Actions.
