---
title: "Upgrade Path and Task-Tree Records Match Shipped Behavior"
status: not-started
depends_on:
  - 08-workflow-wiring
---

## Objective

A 0.4 project with tier declarations upgrades to 0.5 without losing its frontier, and the release notes and the reproducibility task tree describe the behavior that ships.

- **A leftover `tier:` step key warns instead of blocking.** It is now an `[ERROR]` that stops `task frontier`, while [RELEASE-NOTES.md:15](../../../../RELEASE-NOTES.md#L15) promises a warning. `--tier` and `repro tier` give actionable errors naming the replacement; today `--tier` gets argparse's "unrecognized arguments".
- **The release notes describe 0.5 as shipped** after 01–08, including the decisions they settle. They state that pytask is no longer a dependency, that `repro-lock.json` replaces `pytask.lock` and `repro-builds.json` (both still read; remove them with `git rm` after the first build), and that `.pytask/` can be deleted.
- **Stale task-tree content is rewritten:** tier, canon, and "queued" language in the [root task](../../task.md) (Results and :56–71) and in [07-workflow-integration](../../07-workflow-integration/task.md) (:31–36); pytask as the engine in the root task's Results, the [02-runner](../../02-runner/task.md) title and Results, and [03-task-interface](../../03-task-interface/task.md).
- **Broken links are repaired:** references to the deleted `graph-authoring.md`, `rerun-model.md`, and `pilot-acceptance.md` in [unified-dependency-workflow](../../07-workflow-integration/unified-dependency-workflow/task.md), [12-agent-protocol](../../12-agent-protocol/task.md), and [06-skill](../../06-skill/task.md); `task check --category links` is clean over `superRA/reproducibility/`.

Validation: a fixture tree with `tier:` keys and `--tier` invocations upgrades with warnings and a working frontier.

## Details

Reproduced directly on a scratch tree: a step with `tier: canon` printed `[ERROR] [reproduction] a: ## Reproduction: unknown step key 'tier'`, `task frontier` refused with "effective dependency graph is invalid", and `repro status . --tier canon` printed `superra repro: error: unrecognized arguments: --tier canon`.
