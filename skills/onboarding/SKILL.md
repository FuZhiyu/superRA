---
name: onboarding
description: Bring an existing research project into superRA — a retroactive task tree, a reproduction graph, version control, and an optional isolated reproduction run — while teaching a researcher new to superRA each concept. Use whenever a project has code, data, or results but no superRA/ task tree, even without git; when it still carries a legacy PLAN.md; or when a researcher asks to adopt, set up, or start using superRA on existing work.
---

# Onboarding

Bring existing work into superRA in six stages.

- **End every stage at its stop point:** present what changed, then wait for the researcher.
- **Enter at the stage the project needs;** skip a stage whose work is already done.
- **Stages 1–3 write only inside `superRA/`:** no code edits, no git commands, no other files. `superra repro status` and `repro build` write a cache and a `.gitignore` line at the project root, so both wait for stage 5, including the `repro status` after a graph comment.
- **Explain each concept in plain words where it first appears,** for a researcher who has never used superRA or git.

## 1. Orient

Explain: superRA keeps the project's research as a tree of tasks in one `superRA/` folder. Each task is a `task.md` stating what the work must achieve (its objective) and what it found (its results); a dashboard shows the tree in the browser. Until the researcher agrees, nothing outside `superRA/` changes, and they may edit or delete anything inside it.

Legacy `PLAN.md` without `superRA/`: [references/legacy-plan-migration.md](references/legacy-plan-migration.md), then continue at stage 2's presentation.

**Stop:** the researcher agrees to start.

## 2. Retroactive task tree

Create the wrapper per `superRA:task-tree` §CLI Setup, then build the tree per `superplan/references/task-tree-design.md` §Retroactive Task-Tree Creation. Existing work superRA has not verified stays `implemented`.

Serve the dashboard (`./superRA/superra dashboard --no-open`), give the researcher its link, and walk them through it: the tree, one task's objective and results, and what `implemented` means here — done, not yet verified.

**Stop:** the researcher approves the tree, editing, commenting on the dashboard, or deleting tasks as they like.

## 3. Reproduction graph

Explain: each task lists the commands that produce its outputs and the files each command reads and writes, so superRA can rerun exactly what a change affects and show which results are out of date.

Declare the whole project per `reproducibility/references/adoption.md`, and present the graph in the dashboard's Graph view.

**Stop:** the researcher approves the graph and its external inputs.

## 4. Version control

Offer git per [references/project-setup.md](references/project-setup.md), whether or not a run follows.

**Stop:** the setup is committed, or the researcher declines; declining leaves the tree and graph uncommitted and rules out stage 5.

## 5–6. Isolated reproduction run and merge back

Ask whether to rerun the project to verify it. Yes: [references/isolated-run.md](references/isolated-run.md).

## Close

Point to everyday use: new work starts with `superRA:superplan`, and the dashboard stays the view of the tree.
