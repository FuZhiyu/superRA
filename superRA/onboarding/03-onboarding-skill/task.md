---
title: "Author the Onboarding Skill Spine and Setup References"
status: approved
depends_on:
  - 02-retroactive-graph
---

## Objective

Create `skills/onboarding/SKILL.md` carrying the six-stage choreography from the parent objective, and the references for version-control setup and legacy `PLAN.md` migration. Stage 2 reuses the existing retroactive capture.

- **SKILL.md:** each stage's action and its stop point, the writes-only-in-`superRA/` rule for stages 1–3, pointers to the owning skills, and a routing table to its references. Frontmatter description names the triggers: a project without `superRA/`, a legacy `PLAN.md`, or a researcher asking to adopt superRA.
- **Stage 2 points to existing retroactive capture** and adds only the whole-tree lines it lacks, placed in [task-tree-design.md](../../../skills/superplan/references/task-tree-design.md#retroactive-task-tree-creation) §Retroactive Task-Tree Creation so standalone retroactive documentation gets them too:
  - which sources to read: code, generated outputs, the paper or draft, project documents;
  - decompose the whole body of work with the same file's §Splitting Tasks and §Writing Objectives and Details, each objective naming what the work achieves and the outputs it produces;
  - an umbrella `superRA/task.md` when the paper's question spans every top-level task.

  The status rule and the rest of the section stay as they are.
- **Concept explanations** for a new user, each given where the concept first appears: `superRA/` and tasks (stage 1–2, including that the researcher may delete anything there), the dashboard (stage 2), the reproduction graph (stage 3), worktrees and merging (stages 5–6, owned by [04-isolated-run](../04-isolated-run/task.md)).
- **Stage 3 validates without `repro status` or `build`,** which write a `.superra-repro/` cache and a `.gitignore` line at the project root ([02-retroactive-graph](../02-retroactive-graph/task.md) §Validated without git).
- **`references/project-setup.md`** (stage 4): offer git when absent, explaining what it gives the researcher; a `.gitignore` excluding data, generated outputs, and caches, settled with the researcher for ambiguous large files; a data-handling note in the project's `CLAUDE.md` / `AGENTS.md` (created if absent) saying where data lives and that it is never committed; a baseline commit of the untouched project, then the `superRA/` commit. A project already in git: check `.gitignore` coverage and commit `superRA/` on a topic branch.
- **`references/legacy-plan-migration.md`:** the `PLAN.md` migration offer and `superra task migrate from-plan`, moved from [main-agent.md](../../../skills/using-superra/references/main-agent.md) §Session Start Actions.

## Results

[skills/onboarding/](../../../skills/onboarding/SKILL.md) carries the six stages, each ending at a stop point, with the writes-only-in-`superRA/` rule for stages 1–3 and a plain-words explanation where each concept first appears. Stages 5–6 route to [isolated-run.md](../../../skills/onboarding/references/isolated-run.md) from [04-isolated-run](../04-isolated-run/task.md).

- **Stage 2 reuses retroactive capture.** [task-tree-design.md §Retroactive Task-Tree Creation](../../../skills/superplan/references/task-tree-design.md#retroactive-task-tree-creation) gained three things: the sources to read (code, outputs, paper or draft, documents), whole-project decomposition by §Splitting Tasks with the umbrella decision left to `build-and-review.md`, and a pointer to §Writing Objectives and Details for objectives. The status rule is unchanged; the skill adds one line that unverified existing work stays `implemented`.
- **Stage 3** declares per [adoption.md](../../../skills/reproducibility/references/adoption.md). `repro status` and `build` write at the project root, so the skill holds both until stage 5, including the `repro status` the graph-review step asks for after a comment.
- **[project-setup.md](../../../skills/onboarding/references/project-setup.md)** (stage 4) offers git and, for a project without it: a researcher-settled `.gitignore` that also covers `.superra-repro/` and the dashboard's run files, a data-handling note in `CLAUDE.md` / `AGENTS.md`, a dashboard stop before `git init` (which moves the dashboard's run files out of `superRA/`), a baseline commit checked for data and files over 50 MB, then a separate `superRA/` commit. A project already in git gets a coverage check — tracked data, files over 50 MB, and a missing `.superra-repro/` line, which would otherwise land as an uncommitted `.gitignore` edit during the run — and a topic-branch commit.
- **[legacy-plan-migration.md](../../../skills/onboarding/references/legacy-plan-migration.md)** carries the upgrade message, docs link, and migrate command formerly in the session-start actions. The command was run in a scratch legacy project with the wrapper present, which needed the [06-empty-root-bootstrap](../06-empty-root-bootstrap/task.md) migration fix.
- **Checks:** Markdown checks clean; `task check --category links` passes. Skill evals were not run; the researcher runs the end-to-end trial.
