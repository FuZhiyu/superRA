---
title: "Upgrade Path and Task-Tree Records Match Shipped Behavior"
status: implemented
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

## Reproduction

```yaml
steps:
  - name: upgrade-path-check
    kind: check
    cmd: "uv run --with pytest --with pyyaml python -m pytest skills/task-tree/scripts/test_repro.py skills/task-tree/scripts/test_repro_runner.py -k 'tier or retired' -q -p no:cacheprovider"
    deps:
      - skills/task-tree/scripts/_apply_patch.py
      - skills/task-tree/scripts/_artifacts.py
      - skills/task-tree/scripts/_comments.py
      - skills/task-tree/scripts/_repro.py
      - skills/task-tree/scripts/_repro_acceptance.py
      - skills/task-tree/scripts/_repro_builds.py
      - skills/task-tree/scripts/_repro_provenance.py
      - skills/task-tree/scripts/_repro_scope.py
      - skills/task-tree/scripts/_repro_signals.py
      - skills/task-tree/scripts/_repro_state.py
      - skills/task-tree/scripts/_step_links.py
      - skills/task-tree/scripts/_task_dependencies.py
      - skills/task-tree/scripts/_task_io.py
      - skills/task-tree/scripts/_task_snapshot.py
      - skills/task-tree/scripts/_task_validate.py
      - skills/task-tree/scripts/_worktree_discovery.py
      - skills/task-tree/scripts/cli.py
      - skills/task-tree/scripts/dashboard_artifact_workflow.py
      - skills/task-tree/scripts/repro_run.py
      - skills/task-tree/scripts/task_query.py
      - skills/task-tree/scripts/task_read.py
      - skills/task-tree/scripts/conftest.py
      - skills/task-tree/scripts/test_repro.py
      - skills/task-tree/scripts/test_repro_runner.py
```

## Results

A project on the reproduction pre-release now upgrades with warnings instead of errors, and the release notes, README, docs-site task-tree pages, and task tree describe what 0.5 ships. [upgrade-path-check](#reproduction) is fresh; its eight tests fail without the code changes and pass here.

### 0.4 projects keep working

- **A leftover `tier:` key warns and is ignored**, in a section or in a step ([_repro.py](../../../../skills/task-tree/scripts/_repro.py), `RETIRED_KEYS`). The step still registers and builds; tier never entered the spec hash, so a built lock stays byte-identical and nothing reruns ([test](../../../../skills/task-tree/scripts/test_repro_runner.py)).
  - **Already fixed by 03:** `task frontier` no longer refused. The key was still an error, which dropped the step and made `repro build` exit 1.
- **`--tier`, `--tier=…`, and `repro tier` exit 2** with `reproduction tiers are retired; name task or task#step targets instead ('.' selects every registered step)`, also after `--root` / `--plan-root` ([repro_run.py](../../../../skills/task-tree/scripts/repro_run.py), `main`).
- **Scratch fixture** (a section and a step with `tier: canon`, a dependent task): `task frontier` lists the dependent, `task check` reports two warnings and no error, `repro build a` executes, and five `--tier` and `repro tier` invocations print the message above.
- **Leftover `env_probe` and `code_roots` under `reproduction:` also warn and are ignored** (`RETIRED_CONFIG_KEYS`). As errors they blocked every build, since a project-wide config error touches all steps. A built lock stays byte-identical when they are added ([test](../../../../skills/task-tree/scripts/test_repro_runner.py)). Researcher decision via the orchestrator: 0.5 upgrades warn, never block.

### The release notes describe 0.5 as shipped

[RELEASE-NOTES.md](../../../../RELEASE-NOTES.md#050---unreleased) is rewritten from 01–08 and 10's `## Results`:

- **An upgrade section comes first**, ordered: every coauthor upgrades before the first 0.5 build or accept commit lands, since an older superRA reads neither `repro-lock.json` nor `repro-acceptance/`. Then `task check` (`tier`, `env_probe`, and `code_roots` warn and can be deleted), a build that writes the lock and prints the `git rm` for `pytask.lock` and `repro-builds.json`, deleting `.pytask/`, and the first `accept`, which converts `repro-acceptance.json`.
- **Changed** is grouped into builds and freshness, readiness and dependencies, reviewed acceptance and diagnosis, agent workflow, and dashboard. It covers the own engine, lock version 2 with one line per step and conflicted-lock reading, checks passed elsewhere, readiness from `depends_on` only, errors blocking only the builds they touch, per-step portable acceptance records, the Dropbox-ignored `.superra-repro/`, `explain` and `impact`, the skill's routing and claim gate, the manifest row, the completion gate that asks before costly reruns, external inputs at Protect, the edit hook, and the dashboard fixes.
- **Removed** lists pytask, `pytask-parallel`, `_repro_hooks.py`, and the `env_probe` and `code_roots` keys, which now warn.
- **Corrected claims:** the combined-graph cycle rule, parent-owned frontier rows, "optional evidence", and a completion gate that "names its deliverable tasks" are gone.
- [README.md](../../../../README.md#upgrading) §Upgrading and its banner now carry the upgrade order and the current readiness and acceptance behavior instead of the cycle audit.
- [task-file-contract.md §Validation](../../../../skills/task-tree/references/task-file-contract.md#validation) lists the retired keys under `[WARNING]` and no longer lists cyclic task-group ordering, which 03 removed, as an error.
- **Docs site.** The [task-tree pages](../../../../docs/site/04-utility-skills/01-task-tree/task.md) and their children now describe readiness from `depends_on` with not-fresh inputs beside each frontier task, a `task move` that refuses only a broken `depends_on`, acceptance with a required reason in `repro-acceptance/`, and the DAG's dashed `depends_on` arrows, red error outline, and marked cycles. The dead **Focus subtree** mention is gone.

This resolves [wiring.md](../attachments/wiring.md) M6.

### The task tree matches the code

- **Tier, canon, and "queued":** the [root task](../../task.md) Results now reads as the implemented state, and its Context drops `env_probe` and the named completion targets. [07-workflow-integration](../../07-workflow-integration/task.md) describes the call sites 08 left. [task-targets-and-lifecycle](../../11-scoped-verification/task-targets-and-lifecycle/task.md) and [01-cli-decision-support](../../12-agent-protocol/01-cli-decision-support/task.md) note what 07, 08, and this task later changed.
- **pytask as the engine:** [02-runner](../../02-runner/task.md) is retitled and its Results describe the current runner, keeping the decisions that outlived pytask; [03-task-interface](../../03-task-interface/task.md) drops the tier badge and the pytask gate.
- **`env_probe` and `repro-builds.json`:** [02-build-record](../../13-staleness-provenance/02-build-record/task.md) Results describe `built_on` in the lock.
- **Links:** every file link in a `task.md` under `superRA/reproducibility/` resolves, and every heading anchor into a skill reference exists.
  - Deleted references in [unified-dependency-workflow](../../07-workflow-integration/unified-dependency-workflow/task.md) and [06-skill](../../06-skill/task.md) point to their current homes. [12-agent-protocol](../../12-agent-protocol/task.md)'s dated diagnosis names the old files as code spans and says what replaced them.
  - The same class, fixed beyond the Objective's list: [reviewed-acceptance](../../02-runner/reviewed-acceptance/task.md), [11-scoped-verification](../../11-scoped-verification/task.md) and two of its children, [scalable-navigation](../../04-dashboard-view/scalable-navigation/task.md), [03-diagnosis-guidance](../../13-staleness-provenance/03-diagnosis-guidance/task.md), [03-skill-redesign](../../12-agent-protocol/03-skill-redesign/task.md), and 01, 02, and 10 of this group (10's link to `diagnosing.md` missed `skills/`).
- **Objectives are unchanged.** Where an approved task's Objective names retired mechanics (02-runner, 03-task-interface, 02-build-record, 06-skill), its Results says what replaced them.

### Verification

- `task check --category links` is clean. That category checks only `#step` references, so file links and anchors were checked with a scratch script over every `.md` under `superRA/reproducibility/`.
- Task-tree and harness suites, without `test_dag_workspace_browser.py`: 1,431 passed, 9 skipped.
- The eleven non-browser checks these edits made `missing` were rebuilt and pass.

### Left open

- **Browser and artifact steps stay stale or missing:** `dashboard-dag-design-browser`, `dashboard-dag-design-interaction-check`, `dashboard-graph-review`, `dashboard-graph-review-check`, `dashboard-navigation-heterogeneity`, and `task-scoped-builds-pilot`. They rewrite committed browser artifacts or timings, and a parallel fix owns the browser test file.
- **Attachments keep dead links**, as dated records: the TreasuryGIV pilot feedback, task-scoped-builds' design, and this group's gate audit.
