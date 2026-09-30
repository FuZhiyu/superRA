---
title: "Onboarding: Adopt a Raw Research Project into superRA"
status: in-progress
depends_on: []
---

## Objective

Ship a standalone `superRA:onboarding` skill that brings a project with no superRA — possibly with no git — into the workflow: a retroactive task tree, a reproduction graph, version control, and an optional isolated reproduction run. The skill teaches a researcher new to superRA each concept as it first appears.

### Context

The skill runs six stages, each ending at a stop point where the researcher reviews before the next begins. A stage whose work is already done is skipped, and the skill can be entered at any stage.

1. **Orient.** Explain what superRA is, what the `superRA/` folder holds, what a task is, and the dashboard. State that nothing outside `superRA/` changes until the researcher agrees.
2. **Retroactive task tree.** Actively create the tasks through the existing retroactive capture, scaled from one task to a whole tree: tasks that read like regular tasks, each with an objective stating what the work achieves and which outputs it produces, and `## Results` recording the current results. Existing work superRA has not verified is `implemented` under the existing status rule. Present the tree on the dashboard; the researcher can edit or delete anything in `superRA/`.
3. **Reproduction graph.** Declare `## Reproduction` steps for every task, back to external inputs, and agree the external inputs with the researcher. Present the DAG.
4. **Version control, offered.** After the researcher approves the tree and graph — whether or not a run follows: offer a git repository if none exists, with a `.gitignore` that keeps data and generated outputs out, a data-handling note, and a baseline commit of the untouched project before the `superRA/` commit. The isolated run needs git; a researcher who declines keeps the tree and graph uncommitted.
5. **Isolated reproduction run** (researcher opts in). Explain git worktrees, create one, seed its data by copy-on-write, and build upstream-first in slices the researcher chooses. Code edits are limited to what the code needs to run, committed in the worktree. A task whose rebuild matches its original outputs becomes `approved`; one that fails or diverges goes to `revise`, with the problem in `## Review Notes`. `## Results` keeps presenting the current results.
6. **Merge back.** Explain the branch and its diff (`superRA/` plus minimal fixes), and merge after the researcher agrees. Work that grew beyond minimal fixes goes through `superRA:superintegrate` instead.

A legacy `PLAN.md` project enters the same skill: migration moves out of the session-start actions into an onboarding reference.

### Constraints

- **Stages 1–3 write only inside `superRA/`**: no code edits, no git operations, no files elsewhere in the project.
- **Compose, don't restate.** Retroactive capture lives in `using-superra/references/interactive-mode.md` §The spectrum and `superplan/references/task-tree-design.md` §Retroactive Task-Tree Creation, with tree-shaping in the rest of `task-tree-design.md`; retroactive-graph guidance in `reproducibility/references/adoption.md`; worktree mechanics in `agent-orchestration/references/worktree-harness-fallback.md`; data seeding in `superRA:worktree-data-sync`. The onboarding skill owns the choreography, stop points, concept explanations, git and data setup, and the run protocol, and points to the rest.
- Contributor gates in [CLAUDE.md](../../CLAUDE.md) apply: `skill-creator` loaded before any `SKILL.md` edit, and the three-test instruction gate on every added line.
- **Verification is script-level:** `superra task check`, Markdown and link checks, and `tests/harness-instruction-following/test_contract.py`. The researcher runs the end-to-end harness trial on a raw project after this tree lands.

## Details

### Exploration findings (2026-09-30)

- **The task-tree CLI runs without git** once `superRA/` holds a `task.md`: `wrapper init`, `task tree`, `repro status`, and `dashboard --no-open` all worked in a scratch folder with no repository. `task create` on an empty `superRA/` fails with "could not auto-detect task root" ([06-empty-root-bootstrap](06-empty-root-bootstrap/task.md)).
- **Retroactive capture already exists, sized for one task.** [interactive-mode.md](../../skills/using-superra/references/interactive-mode.md) §The spectrum routes a write-up of finished work through §Retroactive Task-Tree Creation in [task-tree-design.md](../../skills/superplan/references/task-tree-design.md#retroactive-task-tree-creation): five steps covering reading, placement, status, and `## Results`. Its status rule (`approved` only for verified work, `implemented` while approval is open) already gives unverified existing work `implemented`. It says nothing about which sources to read or how to shape a whole tree.
- **Graph adoption is one-task only:** [adoption.md](../../skills/reproducibility/references/adoption.md) says to register one task first; the researcher chose a whole-project graph.
- **Session start bootstraps the wrapper unconditionally** ([main-agent.md](../../skills/using-superra/references/main-agent.md) §Session Start Actions), which creates `superRA/` before any onboarding offer.
- **Seeding already uses copy-on-write:** `worktree-data-sync --mode seed` clones a fresh managed root with `cp -c`. Discovery keys on gitignored paths, so stage 4's `.gitignore` decides what gets seeded.
- **Worktrees carry only committed files**, and a Dropbox-synced project wants a worktree outside the synced folder ([worktree-harness-fallback.md](../../skills/agent-orchestration/references/worktree-harness-fallback.md) §Placement).
