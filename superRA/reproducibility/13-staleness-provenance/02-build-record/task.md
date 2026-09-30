---
title: "Commit a Per-Step Build Record: Time, Platform, Environment"
status: approved
depends_on:
  - 01-provenance-explain
---

## Objective

Record, at each successful build, what git cannot know about who produced the locked bytes, and show it in `explain` when it differs from this machine.

- **Record.** Committed project-root `repro-builds.json`: `{step: {lock_id, built_at, platform, env}}`. `lock_id` hashes the step's lock entry so a record that no longer matches the lock is detectable. `platform` is OS and CPU architecture. `env` holds the hashes of configured `env_deps` plus the stdout of an optional project-level `env_probe` command (e.g. `python -c 'import numpy; numpy.show_config()'`). No host or user name.
- **History without history.** The file keeps only the current entry per step; for a lock match at revision X, `explain` reads `git show X:repro-builds.json`.
- **Written with the successful receipt** in build teardown; merge conflicts are per-step keys, no worse than `pytask.lock`.
- **`explain` shows environment only on mismatch** (`env: differs — <field>`) or `env: same as lock builder`; the check-stamp reason from [01](../01-provenance-explain/task.md) names the builder's environment when known.
- **Validation:** fixtures cover record write on success and not on failure, `lock_id` mismatch detection, lookup at an older lock revision, `env_probe` capture and mismatch display; the suite passes; the record and `env_probe` are documented in [task-file contract §Acceptance and successful baseline records](../../../../skills/task-tree/references/task-file-contract.md#records), [§Project config](../../../../skills/task-tree/references/task-file-contract.md#project-config), and [commands.md §Reproduction](../../../../skills/task-tree/references/commands.md#reproduction).

## Details

- Receipt capture: [capture_receipt](../../../../skills/task-tree/scripts/_repro_acceptance.py#L137), called from build teardown in [repro_run.py](../../../../skills/task-tree/scripts/repro_run.py) after engine product verification. Run records written at [repro_run.py:215-236](../../../../skills/task-tree/scripts/repro_run.py#L215-L236).
- `env_deps` already exist as a config key ([_repro.py CONFIG_KEYS](../../../../skills/task-tree/scripts/_repro.py#L40)); `env_probe` joins them under `reproduction:` in `superRA/config.yaml`.
- The motivating drift: identical code and data produced different pickle bytes under OpenBLAS and Accelerate NumPy wheels; only a probe inside the project's own environment can see that.

## Results

Each step's entry in the committed `repro-lock.json` records the platform it was built on, and `explain` compares that platform and the builder's `env_deps` hashes with this machine. This task first wrote a separate `repro-builds.json` with a build time and an `env_probe` digest; [01-engine-freshness](../../14-review-revisions/01-engine-freshness/task.md) folded the record into the lock and removed `env_probe`, so the Objective's record shape, `lock_id`, and probe items no longer describe the code.

### The record

- **Shape:** `built_on: {platform}` on each lock entry, e.g. `Darwin arm64` from `platform.system()` plus `platform.machine()` ([_repro_builds.py](../../../../skills/task-tree/scripts/_repro_builds.py)). No host or user name, and no timestamp, so an identical rebuild leaves the lock byte-identical.
- **Environment:** the builder's `env_deps` hashes come from the entry's own `deps`; no separate field stores them.
- **Written** with the lock entry after a successful run. A failed run leaves the entry unchanged. `built_on` is excluded from entry equality, so it never decides freshness.
- **Legacy:** a `repro-builds.json` is still read, converted in memory, until the first build writes `repro-lock.json`; its probe fields are ignored.

### In `explain`

`_env` in [_repro_provenance.py](../../../../skills/task-tree/scripts/_repro_provenance.py) runs for rows whose bytes came from a build: an output row, or an input that another step produces.

- **Builder:** the row's step for an output; the producer for a produced input.
- **Record lookup:** the builder's lock entry at the lock revision the row names, or the working lock.
- **Row fact**, appended to the evidence:
  - `env: same as lock builder`;
  - `env: differs — <field>`, where a field is `platform (<there> there, <here> here)` or an `env_deps` path;
  - nothing when the entry has no `built_on`, e.g. history from before the record.
- **JSON** carries `env` with `status`, `where`, `builder`, `record`, and `differences`.
- **Check reason** ([check_elsewhere_reason](../../../../skills/task-tree/scripts/_repro_provenance.py#L156)): `passed at these inputs in lock <rev> on <platform>; not run here`. Since [10-checks-passed-elsewhere](../../14-review-revisions/10-checks-passed-elsewhere/task.md) that check reads `fresh`.

### Deviations from Details

- **`env` shows beside the source facts, not as its own line**, which keeps the one-line-per-node budget.

### Validation

- [test_repro_builds.py](../../../../skills/task-tree/scripts/test_repro_builds.py), registered as `build-record-check`:
  - the lock entry carries `built_on` on success, names no host or user, is byte-identical after an identical rebuild, and is unchanged by a failed run;
  - across two clones, the row names the rebuild revision and reports `env: same as lock builder`, then `env: differs — platform (…)` when this machine's platform differs;
  - a source-file input row carries no `env`;
  - the check reason names the builder's platform.
- **IntermediaryDemand (read-only), before the fold:** `explain .` printed no `env:` for a project with no record, and was otherwise unchanged (0.4 s).

## Review Notes
Tier: quick. Focus: correctness (write on success only, binding to the lock entry, lookup at the row's lock revision, mismatch display), host/user leakage, cost, and agent usability of `env:` facts. All advisory.

1. **[ADVISORY] Probe output is committed verbatim.** The record itself names no host or user. [record_build](../../../../skills/task-tree/scripts/_repro_builds.py#L65-L77), however, commits whatever `env_probe` prints. `numpy.show_config()` prints only paths from the wheel's build machine, but probes such as `julia -e 'versioninfo()'` or `which python` print home-directory paths. Add one clause to the `env_probe` row in [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md#project-config): its stdout is committed, so keep it free of paths.
   → implemented: the `env_probe` row in [task-file-contract.md §Project config](../../../../skills/task-tree/references/task-file-contract.md#project-config) states that its stdout is committed and must print no paths or user-identifying text.
2. **[ADVISORY] The full probe stdout repeats in every step's entry.** `numpy.show_config()` is about 60 lines, so `repro-builds.json` grows by that much per step, and each rebuild rewrites it in the diff. Consider storing the stdout once, or a hash plus the stdout.
   → implemented: each step entry carries a 16-hex probe digest, and the text is stored once under the top-level `_probes` key, pruned to referenced digests ([record_build](../../../../skills/task-tree/scripts/_repro_builds.py#L74-L94)). [differences](../../../../skills/task-tree/scripts/_repro_builds.py#L110-L129) looks the text up in the same file revision, so `env: differs` still names the first differing line (`test_probe_runs_once_per_build_and_its_text_is_stored_once`).
3. **[ADVISORY] Parallel builds can run the probe twice.** [probe_once](../../../../skills/task-tree/scripts/_repro_builds.py#L43-L48) is not guarded by `_write_lock`, so two `-j` teardowns can both run it. The result is the same; only the time is duplicated.
   → implemented: [probe_once](../../../../skills/task-tree/scripts/_repro_builds.py#L52-L58) runs under its own lock; a `-j 3` build runs the probe once (same test).
4. **[ADVISORY] 01's registered check is missing a dependency.** `provenance-explain-check` in [01-provenance-explain](../01-provenance-explain/task.md) does not declare `skills/task-tree/scripts/_repro_builds.py`, which `_repro_provenance.py` now imports. This is for the planner, as the implementer noted.
