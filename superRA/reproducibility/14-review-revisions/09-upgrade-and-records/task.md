---
title: "Upgrade Path and Task-Tree Records Match Shipped Behavior"
status: not-started
depends_on:
  - 08-workflow-wiring
---

## Objective

A project from 0.4 upgrades to 0.5 without losing its frontier, and the release notes and this task tree describe what 0.5 actually ships.

### 0.4 projects keep working

- **A leftover `tier:` key warns instead of blocking.** Today it is an error that stops `task frontier`, while [RELEASE-NOTES.md:15](../../../../RELEASE-NOTES.md#L15) promises a warning.
- **Retired flags name their replacement.** `repro status . --tier canon` prints argparse's "unrecognized arguments: --tier canon". `--tier` and `repro tier` should point to task targets instead.

### The release notes describe 0.5 as shipped

- They cover the result of 01–08, including the decisions those tasks settle.
- From 01: pytask is no longer a dependency; `repro-lock.json` replaces `pytask.lock` and `repro-builds.json`, which are still read and can be removed with `git rm` after the first build; `.pytask/` can be deleted; the `env_probe` config key is gone.
- From 02: acceptance records move to one file per step under `repro-acceptance/`; the first `accept` converts and deletes `repro-acceptance.json`. Coauthors must upgrade before that commit lands, since an older superRA reads no records from the new layout and every accepted step reads stale for them.

### The task tree matches the code

- **Tier, canon, and "queued" language:** the [root task](../../task.md) (Results and lines 56–71) and [07-workflow-integration](../../07-workflow-integration/task.md) (lines 31–36).
- **pytask as the engine:** the root task's Results, the [02-runner](../../02-runner/task.md) title and Results, and [03-task-interface](../../03-task-interface/task.md).
- **`env_probe` and `repro-builds.json`:** [02-build-record](../../13-staleness-provenance/02-build-record/task.md).
- **Links to deleted references** (`graph-authoring.md`, `rerun-model.md`, `pilot-acceptance.md`): [unified-dependency-workflow](../../07-workflow-integration/unified-dependency-workflow/task.md), [12-agent-protocol](../../12-agent-protocol/task.md), and [06-skill](../../06-skill/task.md).

### Validation

- A fixture tree with `tier:` keys and `--tier` invocations upgrades with warnings and a working frontier.
- `task check --category links` is clean over `superRA/reproducibility/`.

## Details

Reproduced directly on a scratch tree before 01: a step with `tier: canon` printed `[ERROR] [reproduction] a: ## Reproduction: unknown step key 'tier'`, `task frontier` refused with "effective dependency graph is invalid", and `repro status . --tier canon` printed `superra repro: error: unrecognized arguments: --tier canon`.
