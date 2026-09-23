---
title: "Commit a Per-Step Build Record: Time, Platform, Environment"
status: not-started
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
