---
title: "Author the Onboarding Skill Spine and Setup References"
status: implemented
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

## Review Notes

Tier: quick. Focuses: the CLAUDE.md §Teach the Protocol instruction gate on added skill lines, cross-reference consistency with the owners.

1. **[BLOCKING] Objective line paraphrases its owner (gate test 1, DRY).** [task-tree-design.md:119](../../../skills/superplan/references/task-tree-design.md#L119) points to §Writing Objectives and Details, then restates its goal bullet ("what the task must produce or verify, naming the artifacts that define its scope", [task-tree-design.md:10](../../../skills/superplan/references/task-tree-design.md#L10)) as ": what the unit achieves and the outputs it produces." Fix: cut the paraphrase — "Write each objective as for planned work, per §Writing Objectives and Details."
   → implemented: [task-tree-design.md:119](../../../skills/superplan/references/task-tree-design.md#L119) now points to §Writing Objectives and Details without the paraphrase.
2. **[BLOCKING] Same-file restatement of the status rule (gate test 2).** [SKILL.md:47](../../../skills/onboarding/SKILL.md#L47) "No: tasks stay `implemented`." is already fixed by stage 2's "Existing work superRA has not verified stays `implemented`." ([SKILL.md:25](../../../skills/onboarding/SKILL.md#L25)). Fix: drop the clause; "Yes: …isolated-run.md" alone keeps the branch.
   → implemented: dropped "No: tasks stay `implemented`" from [SKILL.md:47](../../../skills/onboarding/SKILL.md#L47).
3. **[ADVISORY] Third copy of the `task check` validation.** [SKILL.md:12](../../../skills/onboarding/SKILL.md#L12) "validate with `superra task check` and the dashboard" repeats [designing-the-graph.md:50](../../../skills/reproducibility/references/designing-the-graph.md#L50) (and adoption.md:11, see 02-retroactive-graph). The clause's real job is overriding [designing-the-graph.md:62](../../../skills/reproducibility/references/designing-the-graph.md#L62), which says to "rerun `superra repro status <task>`" after a graph comment; "so they wait for stage 5, including after a graph comment" would carry that without the restatement.
   → implemented: [SKILL.md:12](../../../skills/onboarding/SKILL.md#L12) drops the `task check` copy and states the override: both commands wait for stage 5, including the `repro status` after a graph comment.
4. **[ADVISORY] Umbrella task reads as mandatory.** [task-tree-design.md:118](../../../skills/superplan/references/task-tree-design.md#L118) "with an umbrella task per build-and-review.md §Create" can be read as always creating one; the owner makes it conditional ("Otherwise skip it", [build-and-review.md:43](../../../skills/superplan/references/build-and-review.md#L43)). "…and decide the umbrella task per …" keeps the condition with the owner.
   → implemented: [task-tree-design.md:118](../../../skills/superplan/references/task-tree-design.md#L118) now says "decide the umbrella task per" the owner.
5. **[ADVISORY] Already-in-git path leaves `.superra-repro/` out of `.gitignore`.** [project-setup.md:15](../../../skills/onboarding/references/project-setup.md#L15) checks only data and large files. The first `repro build` in the worktree then appends `.superra-repro/` to the tracked `.gitignore` ([_repro_state.py:149-156](../../../skills/task-tree/scripts/_repro_state.py#L149-L156)); that edit is outside isolated-run's commit step and blocks `git worktree remove` without `--force`. Add `.superra-repro/` to the coverage check, as the no-git path already does.
   → implemented: [project-setup.md:15](../../../skills/onboarding/references/project-setup.md#L15) checks for `.superra-repro/` and adds the line in the `superRA/` commit.
