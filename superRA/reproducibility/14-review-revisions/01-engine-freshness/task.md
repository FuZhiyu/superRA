---
title: "Engine: superRA Runs Builds Itself, With No False Fresh and No Needless Reruns"
status: approved
depends_on: []
---

## Objective

`superra repro build` runs on superRA's own build loop with no pytask dependency and writes one committed lock, `repro-lock.json`. Every command keeps its current behavior, and `status` and `build` agree with the current bytes in every journey below, each pinned by a test in the `test_repro*.py` suite.

### One engine, one freshness rule

- **`build` decides run or skip through the rule `status` uses.** Each step is checked with `_repro_state.compute_status` over the whole build selection, counting steps completed earlier in the same run, so a producer inside the selection is never treated as a saved input and a rerun that regenerates identical bytes still stops the cascade. `_repro_hooks.py` and the pytask adapter types in [repro_run.py](../../../../skills/task-tree/scripts/repro_run.py) (`FileNode`, `SpecNode`, `StepTask`, the `_pytask` imports) are deleted; their logic runs inline in the loop.
- **The CLI is unchanged:** the same subcommands, flags, and `--json` shapes. `build` exits 0 on success and 1 when a step fails or the build cannot start. Only `build`'s progress lines and summary, and the lock file names, change.
- **Execution semantics carry over:**
  - Steps run in dependency order; a failed step skips its descendants while unrelated branches continue.
  - A step with a missing input fails before its command runs; an `external` input is reported the way `status` reports it.
  - After each run the step's declarations are rechecked, and a declared out the command did not write fails the step.
  - Acceptance skips, saved-input receipts, successful baselines, and supersede-on-attempt behave as the hooks do today.
  - `-j N` runs ready steps on a thread pool sharing one hash cache.
  - `--force` and `--upstream` keep their scope; a crashed or forced attempt still retries through the `running` / `pending` run records.
  - `--dry-run` writes nothing: no lock, run record, receipt, or acceptance change.
  - Ctrl-C stops running subprocesses and marks their run records failed.
- **The lock is written per step by one writer.** A successful step's entry is written atomically (temp file, then rename) through a single in-process writer or under a thread lock, so no `-j` worker overwrites another's entry and an interrupted build keeps every completed entry. The same writer serializes the other read-modify-writes worker threads now reach, including `supersede` on `repro-acceptance.json`. A skipped step keeps its entry; a failed step leaves its entry unchanged.
- **No pytask anywhere.** pytask and `pytask-parallel` leave the PEP 723 block of `repro_run.py`. The tests gated by `needs_pytask` run under the standard contributor command in [CLAUDE.md](../../../../CLAUDE.md). Registered step commands that install pytask drop it: [task-scoped-builds](../../11-scoped-verification/task-scoped-builds/task.md) (two steps), [01-provenance-explain](../../13-staleness-provenance/01-provenance-explain/task.md), [02-build-record](../../13-staleness-provenance/02-build-record/task.md), and the command in [unified-dependency-workflow](../../07-workflow-integration/unified-dependency-workflow/task.md).
- **Python 3.10 runs every command.** The `uv` re-exec remains only for reading a legacy `pytask.lock`, which needs `tomllib`.

### `repro-lock.json`

- **Only the file format changes.** `LockEntry` and everything compared against it — `lock_state`, `current_state`, acceptance `baseline.lock`, and the receipts under `.superra-repro/baselines/` — keep today's in-memory shape, the step spec included as the `<step>::spec` dependency. Existing acceptance records and receipts therefore validate unchanged; [02](../02-portable-records/task.md) owns reshaping the committed acceptance record.
- **File shape:** a `version` field; per-step entries keyed and sorted by step name, each with
  - `spec` — the two-half definition hash from `spec_hash`;
  - `deps` and `outs` — logical path to content hash (the sidecar digest for a sidecar-tracked out, the stamp for a check step);
  - `built_on` — the `platform` of the last successful build.

  One key per line with sorted keys.
- **Freshness reads only `spec`, `deps`, and `outs`.** `built_on` feeds `explain`'s environment comparison and the "checked elsewhere" status reason ([check_elsewhere_reason](../../../../skills/task-tree/scripts/_repro_provenance.py#L151-L163)), never the fresh/stale decision.
- **The build record folds into the lock.** `repro-builds.json` and its `lock_id` link are retired. An entry is rewritten only when `spec`, `deps`, `outs`, or `platform` change; `built_at` and `env.deps` are not carried.
- **`env_probe` is removed.** Its only use was one `explain` hint, while its committed text risked leaking paths and made the lock conflict in merges. `built_on.platform` and the `env_deps` hashes remain `explain`'s environment comparison; a config still setting `env_probe` gets `task check`'s unknown-key error.
- **Stale entries are pruned** only by a real build on an error-free graph: entries for steps no longer in the tree are removed (decision below).
- **Every lock reader switches together, preferring `repro-lock.json` when both files exist:**
  - `read_lock` and its callers, including acceptance and scope;
  - the per-revision lock index behind `explain`, which reads `repro-lock.json` and, at older revisions, `pytask.lock` with `repro-builds.json`; its `lock-index/<sha>.json` cache gets a version bump;
  - `check_elsewhere_reason` and `explain`'s environment comparison;
  - the dashboard watcher that emits `repro-updated` ([internals.md:258](../../../../skills/task-tree/references/internals.md#L258)), which follows the file across rename-based writes.
- **Older projects read unchanged.** Without `repro-lock.json`, `pytask.lock` and `repro-builds.json` are read and converted in memory; pytask's `state` field is dropped. The first build writes `repro-lock.json` and prints that `pytask.lock` and `repro-builds.json` can be removed with `git rm`; it deletes neither. Nothing creates `.pytask/`.

### Freshness fixes, on the new loop

- **Symlinked subdirectories inside a directory dependency are hashed.** [`tree_hash`](../../../../skills/task-tree/scripts/_repro_state.py#L177-L191) walks with `os.walk` without `followlinks` and silently skips unreadable files. Follow links with a cycle guard; a broken link or unreadable file under a declared directory surfaces as an error or `external`, never as a silent omission.
- **A missing lock means never built.** With neither `repro-lock.json` nor `pytask.lock` present, `status` reports every step missing and `build` executes every step; no other local state decides a skip.
- **A targeted build keeps a sidecar-tracked saved input's consumer fresh** when nothing changed: [`check_boundary_receipt`](../../../../skills/task-tree/scripts/_repro_scope.py#L69) records the digest when the bytes match the producer's recorded output or the sidecar matches the lock, instead of rerunning. With one freshness rule this may already hold; the regression test decides.
- **Scoped `status` does not exit 0 while producers behind the selection are stale.** It reports the count of producers behind the selection that are not fresh (stale, missing, failed, or external). `status` exits 0 when everything assessed is fresh, 1 when a selected step is not fresh, and 3 when the selection is fresh but a producer behind it is not; exit 2 stays argparse's usage error. `StatusReport.ok` keeps meaning every reported step is fresh; the exit code takes the upstream count separately.

### Mechanics docs

[internals.md](../../../../skills/task-tree/references/internals.md), [commands.md](../../../../skills/task-tree/references/commands.md) §Reproduction, the record sections of [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md), and the engine line of [reproducibility/SKILL.md](../../../../skills/reproducibility/SKILL.md#L11) name the new engine, `repro-lock.json`, and the `status` exit codes. Factual edits only; [07-instruction-rewrite](../07-instruction-rewrite/task.md) owns the gate rewrite.

### Validation

- **Migration fixture.** Build a scratch project with the pytask engine at `7d5fa992`: a chain with a sidecar-tracked out and its receipt, a check step, an accepted step, and a build record. Record `status --json` and `explain` output, run the first new-engine build, and require the same per-step state, acceptance validity, and receipts, with no step executed that the old engine would have skipped.
- **History across the switch.** `explain` names the right lock revision in a git history whose older commits hold `pytask.lock` and newer ones `repro-lock.json`.
- **Existing tests.** The `needs_pytask` tests pass without pytask. The tests expected to change, and why:
  - the two tests of the "needs pytask" message — the message is gone;
  - [test_repro_builds.py:19-23](../../../../skills/task-tree/scripts/test_repro_builds.py#L19-L23) — `repro-builds.json` and `lock_id` are retired;
  - [test_repro_runner.py:733](../../../../skills/task-tree/scripts/test_repro_runner.py#L733) — pytask's "Would be executed" summary is gone;
  - lock file names in `test_repro_provenance.py` and `test_dashboard.py`.

  Any other test edit is a regression.
- **New tests:** the lock round-trips byte-identically; under `-j`, ordering, failure skips, and every completed step's entry present; Ctrl-C mid-build; `--dry-run` writes nothing; `build` exit codes; `status` exits 3 for a fresh selection behind a missing or stale producer and 2 for a usage error; `status` and `build` agree with the lock deleted; merges of branches that build different steps, including adjacent steps, stay conflict-free.

### Decisions

- **Lock entries of archived steps are kept,** so `explain` retains provenance; pruning drops only steps absent from the tree.

Owning tasks: [02-runner](../../02-runner/task.md), [task-scoped-builds](../../11-scoped-verification/task-scoped-builds/task.md), [02-build-record](../../13-staleness-provenance/02-build-record/task.md).

## Results

`superra repro build` now runs on superRA's own loop in [repro_run.py](../../../../skills/task-tree/scripts/repro_run.py) and writes `repro-lock.json`; pytask, `_repro_hooks.py`, and the adapter types are gone. The whole task-tree suite passes without pytask, and a project built by the pytask engine migrates with identical step states and nothing rerun. `env_probe` is removed.

### Verification

- **Suite.** The standard contributor command in [CLAUDE.md](../../../../CLAUDE.md), with no pytask: 1,269 passed; the 10 skips need playwright, which the command does not install.
- **Python 3.10.** The six `test_repro*` modules pass (200 tests); the two in-process legacy-lock tests skip there, since the CLI re-execs under `uv` for a legacy `pytask.lock`.
- **Migration fixture.** A scratch project was built by the pytask engine at `7d5fa992`: a chain with a sidecar-tracked out, a check step, an accepted step, and a build record.
  - The new engine's `status . --json` matched the old one step for step (status, reason, local status, acceptance id), both before and after its first build.
  - That first build executed nothing, wrote `repro-lock.json` with every entry's `built_on`, printed the `git rm` hint, and deleted neither legacy file.
  - `explain` output was identical except the footer now reads "the lock at N revision(s)".
  - A targeted `build 02-est 03-report` over the sidecar-tracked saved input reran nothing.
- **This repo.** The new engine rebuilt the eleven check steps these edits staled, under `-j 4`; the committed [repro-lock.json](../../../../repro-lock.json) is its output. `dashboard-dag-design-interaction-check` failed once under that load (a toolbar control's bounding box read as none) and passed on a solo rerun. Commit 4adac714 removed `pytask.lock` and `repro-builds.json`.
  - Left stale: the three build steps (`dashboard-dag-design-browser`, `dashboard-navigation-heterogeneity`, `task-scoped-builds-pilot`), since rerunning them rewrites committed browser artifacts and timing measurements.
- **Speed on this repo (14 steps).** `status .` takes 0.16–0.20 s, and `build . --dry-run` 0.40 s, against ~0.8 s under pytask. The [pilot's](../../11-scoped-verification/task-scoped-builds/attachments/pilot-results.json) warm no-op build median fell from 0.394 s to 0.074 s.

### What changed

- **Build loop.** Each step is decided by `compute_status` over the whole selection; `compute_status` gained a `scope` argument, so a producer anywhere in the selection is never a saved input. Steps run in dependency order on a thread pool, and a failed step skips its descendants.
  - A missing input fails the step before its command runs.
  - Ctrl-C, SIGTERM, or SIGHUP kills each running step's process group and records the step failed; `build` exits 1. A step still queued is cancelled and recorded `skipped`, so its run record and acceptance stay as they were.
  - The run and skip semantics of the hooks carry over, including supersede on attempt and sticky `forced` retries.
- **Lock.** Lock writing lives in [_repro_state.py](../../../../skills/task-tree/scripts/_repro_state.py): `write_lock_entry` and `prune_lock` run under `RECORD_LOCK`, which also serializes `supersede`. `read_lock` falls back to the legacy pair, converted in memory once per process. `LockEntry` gained `built_on`, excluded from equality, so acceptance records and receipts validate unchanged. Records are written with mode `0666 & ~umask`, not `mkstemp`'s 0600.
- **Build record.** `explain` reads `built_on` from the lock at the row's revision ([_repro_builds.py](../../../../skills/task-tree/scripts/_repro_builds.py)).
  - `env_deps` hashes come from the entry's `deps`, so `explain` still shows them.
  - The "record does not match its lock entry" case is gone with `lock_id`.
- **Lock history.** The index behind `explain` reads both lock files per revision; its `lock-index/<sha>.json` cache is now version 3. A legacy revision that Python 3.10 cannot parse is not cached.
- **Dashboard.** The watcher re-arms after a lock change, so it follows the file across rename writes. The reopened watch ticks once and compares the lock with what the last refresh read, so a write that lands while it reopens is not lost.
- **Freshness fixes.**
  - `tree_hash` follows symlinks with a cycle guard; a broken link or an unreadable file makes the directory unreadable (reported as `missing`).
  - A sidecar saved input counts as verified when its bytes match the producer's recorded output or the digest its sidecar names. A skip records those digests into the consumer's receipt.
  - A scoped `status` exits 3 and names the producers behind the selection that are not fresh; `--json` carries them as `behind`. `status .` drops the "(selected steps only)" label.
  - A check that passed elsewhere but failed here reads "forced rerun required" only when the failed run was forced; otherwise "rerun required".
- **`env_probe` removed** from the config keys, the lock, and `explain`; legacy probe fields are ignored on read.
- **Tests.** [test_repro_engine.py](../../../../skills/task-tree/scripts/test_repro_engine.py) (19 test functions) covers every "New tests" item plus the fixes, the legacy read, `explain` across the switch, and interruption by SIGINT, SIGTERM, and SIGHUP with queued steps; `engine-freshness-check` below runs it. The lock-write race of the dashboard watcher is pinned in [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py).
- **Docs and steps.**
  - The mechanics docs name the new engine, the lock, and the exit codes; commands.md labels the dry-run total an upper bound.
  - Every registered step command and companion that installed pytask or depended on `_repro_hooks.py` no longer does, including `reviewed-baseline-regression-check` and `diagnosis-scenario-check`.

### Deviations

- **Test edits beyond the expected list.**
  - Removing the pytask gates: the `needs_pytask` markers, and two runtime `find_spec("pytask")` gates in `test_task_dependencies.py`.
  - Tests that patched deleted engine internals now patch equivalent seams:
    - `test_the_generated_task_carries_the_directory_edge` now checks the scheduler's parent map.
    - `test_revalidates_between_task_creation_and_engine_setup` patches `_schedule`, and `test_precommand_forced_failure_preserves_truth_and_invalidates_cache` patches `current_state`. Their assertions are unchanged.
  - `test_legacy_alias_lock_requires_only_affected_consumer_rebuild` edits the JSON lock instead of TOML.
  - Four scoped-`status` assertions in `test_repro_scope.py` move from 0 to 3, the new exit code, because each selection is fresh with a never-built or stale producer behind it.
  - Two check-elsewhere reasons in `test_repro_provenance.py` now include `on <platform>`, because every lock entry carries `built_on`.
  - `test_repro_builds.py` follows the folded record beyond lines 19-23: the probe tests and the `lock_id` mismatch case are gone, the `explain` environment test compares platforms, and an identical-rebuild check is new.
- **Deferred advisories.** `_run_step` supersedes a step's acceptance only under `running_lock` after the stop check, so a step an interrupt reaches before it starts keeps its acceptance ([test](../../../../skills/task-tree/scripts/test_repro_engine.py)). The dashboard's re-armed lock watch ticks on timeout once, then reopens event-driven ([test](../../../../skills/task-tree/scripts/test_dashboard.py)).
- **Minor findings.** The dry-run upper bound is now documented. The rest are untouched: exit 1 on a fresh clone until checks run, the lingering invalid acceptance, and untracked Python imports.

## Details

### Why superRA owns the engine

superRA already decided freshness, forcing, acceptance skips, and saved inputs, and wrote receipts itself. pytask supplied ordering, threads, and lock writing at the cost of four private imports (`_pytask.pluginmanager.storage`, `_pytask.build.normalize_programmatic_config`, `_pytask.cli.DEFAULTS_FROM_CLI`, `_pytask.outcomes`), a `tryfirst` hook raising `SkippedUnchanged`, a workaround because `pytask-parallel` bypasses `execute`, and direct TOML reads of pytask's lock format.

- **Letting pytask own freshness instead was rejected.** `task frontier`, `task read`, and the dashboard need step state on every call. On this repo (13 steps) `repro status .` takes ~0.15 s against ~0.8 s for `build . --dry-run`; per-node change reasons live in private `_pytask.state` and `_pytask.explain`; `pytask lock accept` overwrites the lock, erasing the line between accepted and executed; and pytask writes `.pytask/file_hashes.json` at the end of every session, including read-only ones.
- **pytask's lock machinery buys nothing this engine needs.** Its journal exists because pytask batches lock writes to the end of a session of many small tasks; per-step atomic writes cover the same crash case for a few slow steps. Sorted output and a version check carry over. Its SQLite fallback for a missing lock is the source of the override below.
- **Parallelism is unchanged.** The runner already used `pytask-parallel`'s thread backend; its process, loky, dask, and coiled backends were never used and add nothing when every step is a subprocess.

### Evidence (engine review, reproduced on a scratch project at `7d5fa992`; repo suite 275 passed)

- **Symlink false fresh.** Step `agg` read `Data/panel/`, with `Data/panel/y2020 -> extdata/y2020`. After editing `extdata/y2020/p.csv`, `status agg` printed `✓ agg fresh … up to date` and `build agg` skipped it; `output/agg.csv` kept the old value. A directory holding only such a link hashes to `dir:e3b0c442…`, the hash of nothing. No test covers symlinks; worktree-data-sync creates them.
- **SQLite override.** With `pytask.lock` deleted and `.pytask/` kept, `status .` reported "5 missing / never built" and `build .` reported "5 Skipped because unchanged" and silently rewrote the lock. pytask 0.6 falls back to `.pytask/pytask.sqlite3` when no lock exists (`use_lockfile_for_skip=False` in `_pytask/lockfile.py`).
- **Sidecar rerun.** After `build .`, `build 03-report` reran `report` with the message `saved input ${OUT}/big.bin needs a full-byte baseline`. On a fresh clone `status .` showed `report` fresh, yet `build 03-report` reran it.
- **Scoped status.** After editing `Data/raw.csv`, `status 02-est 03-report` printed "3 fresh" and exited 0; the only hint was the footer "upstream freshness not verified". The "(selected steps only)" label also appears for `.`.
- **Build-record churn.** A rebuild that left `pytask.lock` identical still rewrote `repro-builds.json`; only `built_at` changed.

### Minor findings to settle or document

- `build --dry-run` lists every downstream step as "would execute", so its cost total is an upper bound; label it.
- `status .` exits 1 on every fresh clone until check steps run locally.
- An acceptance that no longer validates lingers with a "clear it with revoke" message while the lock still matches.
- Python imports are not tracked; only the Julia `include` closure is (*inferred*).
