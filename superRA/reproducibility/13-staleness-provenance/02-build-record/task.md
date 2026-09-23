---
title: "Commit a Per-Step Build Record: Time, Platform, Environment"
status: implemented
depends_on:
  - 01-provenance-explain
---

## Objective

Record, at each successful build, what git cannot know about who produced the locked bytes, and show it in `explain` when it differs from this machine.

- **Record.** Committed project-root `repro-builds.json`: `{step: {lock_id, built_at, platform, env}}`. `lock_id` hashes the step's lock entry so a record that no longer matches the lock is detectable. `platform` is OS and CPU architecture. `env` holds the hashes of configured `env_deps` plus the stdout of an optional project-level `env_probe` command (e.g. `python -c 'import numpy; numpy.show_config()'`). No host or user name.
- **History without history.** The file keeps only the current entry per step; for a lock match at revision X, `explain` reads `git show X:repro-builds.json`.
- **Written with the successful receipt** in build teardown; merge conflicts are per-step keys, no worse than `pytask.lock`.
- **`explain` shows environment only on mismatch** (`env: differs — <field>`) or `env: same as lock builder`; the check-stamp reason from [01](../01-provenance-explain/task.md) names the builder's environment when known.
- **Validation:** fixtures cover record write on success and not on failure, `lock_id` mismatch detection, lookup at an older lock revision, `env_probe` capture and mismatch display; the suite passes; the record and `env_probe` are documented in [task-file contract §Acceptance and successful baseline records](../../../../skills/task-tree/references/task-file-contract.md#acceptance-and-successful-baseline-records), [§Project config](../../../../skills/task-tree/references/task-file-contract.md#project-config), and [commands.md §Reproduction](../../../../skills/task-tree/references/commands.md#reproduction).

## Details

- Receipt capture: [capture_receipt](../../../../skills/task-tree/scripts/_repro_acceptance.py#L137), called from build teardown in [repro_run.py](../../../../skills/task-tree/scripts/repro_run.py) after engine product verification. Run records written at [repro_run.py:215-236](../../../../skills/task-tree/scripts/repro_run.py#L215-L236).
- `env_deps` already exist as a config key ([_repro.py CONFIG_KEYS](../../../../skills/task-tree/scripts/_repro.py#L40)); `env_probe` joins them under `reproduction:` in `superRA/config.yaml`.
- The motivating drift: identical code and data produced different pickle bytes under OpenBLAS and Accelerate NumPy wheels; only a probe inside the project's own environment can see that.

## Reproduction

```yaml
steps:
  - name: build-record-check
    kind: check
    cmd: "uv run --with pytest --with 'pytask>=0.6,<0.7' --with pytask-parallel --with pyyaml python -m pytest skills/task-tree/scripts/test_repro_builds.py -q -p no:cacheprovider"
    deps:
      - skills/task-tree/scripts/_apply_patch.py
      - skills/task-tree/scripts/_artifacts.py
      - skills/task-tree/scripts/_comments.py
      - skills/task-tree/scripts/_repro.py
      - skills/task-tree/scripts/_repro_acceptance.py
      - skills/task-tree/scripts/_repro_builds.py
      - skills/task-tree/scripts/_repro_hooks.py
      - skills/task-tree/scripts/_repro_provenance.py
      - skills/task-tree/scripts/_repro_scope.py
      - skills/task-tree/scripts/_repro_state.py
      - skills/task-tree/scripts/_step_links.py
      - skills/task-tree/scripts/_task_dependencies.py
      - skills/task-tree/scripts/_task_io.py
      - skills/task-tree/scripts/_task_snapshot.py
      - skills/task-tree/scripts/_task_validate.py
      - skills/task-tree/scripts/_worktree_discovery.py
      - skills/task-tree/scripts/cli.py
      - skills/task-tree/scripts/dashboard_artifact_workflow.py
      - skills/task-tree/scripts/plan_dashboard.py
      - skills/task-tree/scripts/plan_migrate.py
      - skills/task-tree/scripts/repro_run.py
      - skills/task-tree/scripts/task_add_result.py
      - skills/task-tree/scripts/task_check.py
      - skills/task-tree/scripts/task_comment.py
      - skills/task-tree/scripts/task_create.py
      - skills/task-tree/scripts/task_hook.py
      - skills/task-tree/scripts/task_link.py
      - skills/task-tree/scripts/task_query.py
      - skills/task-tree/scripts/task_read.py
      - skills/task-tree/scripts/task_rename.py
      - skills/task-tree/scripts/task_update.py
      - skills/task-tree/scripts/wrapper_resolver.py
      - skills/task-tree/scripts/conftest.py
      - skills/task-tree/scripts/test_repro_runner.py
      - skills/task-tree/scripts/test_repro_provenance.py
      - skills/task-tree/scripts/test_repro_builds.py
```

## Results

A successful build now writes the step's entry in the committed project-root `repro-builds.json`. `explain` reads the builder's entry at the lock revision a row already names and adds one `env:` fact to that row.

### The record

- **Shape:** `{step: {lock_id, built_at, platform, env: {deps, probe | probe_error}}}` ([record_build](../../../../skills/task-tree/scripts/_repro_builds.py#L65-L77)).
  - `lock_id` is the first 16 hex characters of the SHA-256 of the step's `depends_on` and `produces`, taken from the verified receipt. It equals the lock entry pytask writes (`test_record_is_written_on_success_only`).
  - `platform` is `platform.system()` plus `platform.machine()`, e.g. `Darwin arm64`. No host or user name is recorded.
  - `env.deps` holds the configured `env_deps` hashes; `env.probe` holds the stdout of `env_probe`, a new optional `reproduction:` key run once per build from the project root.
- **Written** in the teardown hook right after the receipt, under a thread lock for `-j` builds ([_repro_hooks.py:80-81](../../../../skills/task-tree/scripts/_repro_hooks.py#L80-L81)). A failed run leaves the entry unchanged.

### In `explain`

[_env](../../../../skills/task-tree/scripts/_repro_provenance.py#L481-L508) runs for rows whose bytes came from a build: an output row, or an input that another step produces.
- **Builder:** the row's step for an output; the producer for a produced input.
- **Record lookup:** the first `lock` or `working-lock` source on the row, recorded side first. A lock source at revision X reads `git show X:repro-builds.json`, memoized per revision ([builds_at](../../../../skills/task-tree/scripts/_repro_provenance.py#L251-L257)); the working lock reads the file on disk.
- **Row fact**, appended to the evidence:
  - `env: same as lock builder`;
  - `env: differs — <field>`, where a field is `platform (<there> there, <here> here)`, an `env_deps` path, or `env_probe line N: '<there>' there, '<here> here'`;
  - `env: lock X has a build record for <step> that does not match its lock entry` when `lock_id` disagrees;
  - nothing when X holds no record for the builder, e.g. history from before this change.
- **Cost:** the probe runs only when a matched record carries one, once per `explain` call. JSON carries `env` with `status`, `where`, `builder`, `record`, and `differences`.
- **Check-stamp reason** ([check_elsewhere_reason](../../../../skills/task-tree/scripts/_repro_provenance.py#L151-L164)): `passed at these inputs in lock <rev> on <platform>; not run here` when the on-disk record's `lock_id` matches the check's lock entry. It reads only the file, so `status` still spawns no git once the lock commit is cached.

### Deviations from Details

- **`env` shows beside the source facts, not as its own line**, which keeps the one-line-per-node budget.
- **The probe is not part of any step's state.** A differing probe never makes a step stale; it only appears in `explain`.

### Validation

- [test_repro_builds.py](../../../../skills/task-tree/scripts/test_repro_builds.py), registered as `build-record-check`:
  - the record is written on success, matches the lock entry, carries no host or user name, and is unchanged by a failed run;
  - two clones with different `env_probe` output. A rebuilds `est` under `openblas`, then force-rebuilds it with identical bytes under `mkl`, so HEAD's record says `mkl`. B's row names the rebuild revision and reports `env_probe line 1: 'blas: openblas' there, 'blas: accelerate' here`, which proves the lookup reads the named revision, not HEAD. Matching probes give `env: same as lock builder`;
  - a committed `panel` record with a wrong `lock_id` is reported as not matching;
  - a source-file input row carries no `env`;
  - the check-stamp reason names the builder's platform.
- Full task-tree suite: 1277 passed.
- **IntermediaryDemand (read-only):** there is no `repro-builds.json` there yet, so `explain .` prints no `env:` and is otherwise unchanged (0.4 s).
- **This repo:** building `build-record-check` and `provenance-explain-check` wrote its first `repro-builds.json`, committed here with `pytask.lock`.

### For review

- `provenance-explain-check` in [01-provenance-explain](../01-provenance-explain/task.md) does not declare `_repro_builds.py`, which `_repro_provenance.py` and its tests now import. Its planner should add the dep.
