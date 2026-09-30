---
title: "Onboarding: Adopt a Raw Research Project into superRA"
status: approved
depends_on: []
---

## Objective

The standalone `superRA:onboarding` skill brings a project with no superRA — possibly with no git — into the workflow: a retroactive task tree, a reproduction graph, version control, and an optional isolated reproduction run. The skill teaches a researcher new to superRA each concept as it first appears.

### Context

The skill runs six stages, each ending at a stop point where the researcher reviews before the next begins. A stage whose work is already done is skipped, and the skill can be entered at any stage.

1. **Orient.** Explain what superRA is, what the `superRA/` folder holds, what a task is, and the dashboard. State that nothing outside `superRA/` changes until the researcher agrees.
2. **Retroactive task tree.** Actively create the tasks through the existing retroactive capture, scaled from one task to a whole tree: tasks that read like regular tasks, each with an objective stating what the work achieves and which outputs it produces, and `## Results` recording the current results. Existing work superRA has not verified is `implemented` under the existing status rule. Present the tree on the dashboard; the researcher can edit or delete anything in `superRA/`.
3. **Reproduction graph.** Declare `## Reproduction` steps for every task, back to external inputs, and agree the external inputs with the researcher. Present the DAG.
4. **Version control, offered.** After the researcher approves the tree and graph — whether or not a run follows: offer a git repository if none exists, with a `.gitignore` that keeps data and generated outputs out, a data-handling note, and a baseline commit of the untouched project before the `superRA/` commit. The isolated run needs git; a researcher who declines keeps the tree and graph uncommitted.
5. **Isolated reproduction run** (researcher opts in). Explain git worktrees, create one, seed its data by copy-on-write, and build upstream-first in slices the researcher chooses. Code edits are limited to what the code needs to run, committed in the worktree. A task whose rebuild matches its original outputs becomes `approved`; one that fails or diverges goes to `revise`, with the problem in `## Review Notes`. `## Results` keeps presenting the current results.
6. **Merge back.** Explain the branch and its diff (`superRA/` plus minimal fixes), and merge after the researcher agrees. Work that grew beyond minimal fixes goes through `superRA:superintegrate` instead.

A legacy `PLAN.md` project enters the same skill, whose migration reference replaces the session-start migration offer.

### Constraints

- **Stages 1–3 write only inside `superRA/`**: no code edits, no git operations, no files elsewhere in the project.
- **Compose, don't restate.** Retroactive capture lives in `using-superra/references/interactive-mode.md` §The spectrum and `superplan/references/task-tree-design.md` §Retroactive Task-Tree Creation, with tree-shaping in the rest of `task-tree-design.md`; retroactive-graph guidance in `reproducibility/references/adoption.md`; worktree mechanics in `agent-orchestration/references/worktree-harness-fallback.md`; data seeding in `superRA:worktree-data-sync`. The onboarding skill owns the choreography, stop points, concept explanations, git and data setup, and the run protocol, and points to the rest.
- Contributor gates in [CLAUDE.md](../../CLAUDE.md) apply: `skill-creator` loaded before any `SKILL.md` edit, and the three-test instruction gate on every added line.

## Results

[skills/onboarding/](../../skills/onboarding/SKILL.md) runs the six stages, each ending at a stop point, and explains each concept where it first appears. Independent review approved it after one revise round, which made unwritten outputs count as divergences and removed four gate restatements.

- **Skill files.** [SKILL.md](../../skills/onboarding/SKILL.md) carries the stages and the writes-only-in-`superRA/` rule for stages 1–3.
  - [project-setup.md](../../skills/onboarding/references/project-setup.md), stage 4: offers git; settles a `.gitignore` that also covers `.superra-repro/` and the dashboard's run files; writes a data-handling note in `CLAUDE.md` / `AGENTS.md`; makes a baseline commit checked for data and files over 50 MB, then a separate `superRA/` commit. A project already in git gets a coverage check and a topic-branch commit.
  - [isolated-run.md](../../skills/onboarding/references/isolated-run.md), stages 5–6: creates and seeds a worktree outside the system temp directory, deletes each slice's seeded outs so every compared output is one the build wrote, and compares by bytes, then by values within a stated tolerance. A match sets `approved`; a failure or divergence sets `revise` with `## Review Notes`. After the merge, differing outputs are copied back with consent or rebuilt in place.
  - [legacy-plan-migration.md](../../skills/onboarding/references/legacy-plan-migration.md): the `PLAN.md` offer and `superra task migrate from-plan`, moved out of session start.
- **Shared steps live in their owning skills,** which onboarding extended:
  - [task-tree-design.md §Retroactive Task-Tree Creation](../../skills/superplan/references/task-tree-design.md#retroactive-task-tree-creation) names the sources to read and decomposes a whole project, so standalone retroactive documentation gets the same lines.
  - [adoption.md](../../skills/reproducibility/references/adoption.md) declares a whole existing project from its scripts as they are, then builds upstream-first in slices the researcher picks; the one-task trial remains the other scope.
- **Entry points.** [main-agent.md §Session Start Actions](../../skills/using-superra/references/main-agent.md) offers onboarding before the wrapper bootstrap writes anything; [superplan §Entry Assessment](../../skills/superplan/SKILL.md) routes existing work without a tree there. Inventories: [CATEGORIES.md](../../skills/CATEGORIES.md), [README.md](../../README.md), the [CLAUDE.md](../../CLAUDE.md) ownership and load-surface rows, and the `.agents/skills/onboarding` symlink.
- **CLI fixes for a wrapper-only `superRA/`.** `task create` falls back to the nearest `superRA/` holding the `superra` wrapper, preferring it over a farther tree ([cli.py](../../skills/task-tree/scripts/cli.py) `_wrapper_only_root`; [test_cli.py](../../skills/task-tree/scripts/test_cli.py)). `task migrate from-plan` ignores the wrapper when checking that the output is empty ([plan_migrate.py](../../skills/task-tree/scripts/plan_migrate.py); [test_task_tree.py](../../skills/task-tree/scripts/test_task_tree.py)).

### Notes

- **`repro status` and `build` write at the project root**: a `.superra-repro/` cache and a `.gitignore` line. The skill therefore validates stage 3 with `task check` and the dashboard, and holds `status` and `build` until stage 5. `task check`, `repro dag`, and the dashboard work without git.
- **Not exercised end to end.** No worktree run was performed and no skill eval ran; the researcher's trial on a raw project covers both.
