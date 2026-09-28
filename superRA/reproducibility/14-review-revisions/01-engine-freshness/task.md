---
title: "Engine: superRA Runs Builds Itself, With No False Fresh and No Needless Reruns"
status: not-started
depends_on: []
---

## Objective

`superra repro build` runs on superRA's own build loop with no pytask dependency and writes one committed lock, `repro-lock.json`. Every command keeps its current behavior, and `status` and `build` agree with the current bytes in every journey below, each pinned by a test in the `test_repro*.py` suite.

### One engine, one freshness rule

- **`build` decides run or skip through the rule `status` uses.** Each step is checked with `_repro_state.compute_status` over the whole build selection, counting steps completed earlier in the same run, so a producer inside the selection is never treated as a saved input and a rerun that regenerates identical bytes still stops the cascade. [_repro_hooks.py](../../../../skills/task-tree/scripts/_repro_hooks.py) and the pytask adapter types in [repro_run.py](../../../../skills/task-tree/scripts/repro_run.py) (`FileNode`, `SpecNode`, `StepTask`, the `_pytask` imports) are deleted; their logic runs inline in the loop.
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
  - `built_on` — `platform`, and the `env_probe` digest or `probe_error` of the last successful build;
  - a top-level `probes` table mapping digest to probe text.

  One key per line with sorted keys.
- **Freshness reads only `spec`, `deps`, and `outs`.** `built_on` feeds `explain`'s environment comparison and the "checked elsewhere" status reason ([check_elsewhere_reason](../../../../skills/task-tree/scripts/_repro_provenance.py#L151-L163)), never the fresh/stale decision.
- **The build record folds into the lock.** `repro-builds.json` and its `lock_id` link are retired. An entry is rewritten only when `spec`, `deps`, `outs`, `platform`, or the probe result change; `built_at` and `env.deps` are not carried.
- **`env_probe` output cannot leak paths.** Its stdout is committed verbatim today ([_repro_builds.py:88-91](../../../../skills/task-tree/scripts/_repro_builds.py#L88-L91)) and only a docs line guards it (decision below).
- **Stale entries are pruned** only by a real build on an error-free graph: entries for steps no longer in the tree are removed (decision below for archived steps).
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
- **New tests:** the lock round-trips byte-identically; under `-j`, ordering, failure skips, and every completed step's entry present; Ctrl-C mid-build; `--dry-run` writes nothing; `build` exit codes; `status` exits 3 for a fresh selection behind a missing or stale producer and 2 for a usage error; `status` and `build` agree with the lock deleted; merges of branches that build different steps, including adjacent steps and a `probes` table change on both sides, stay conflict-free.

### Researcher decisions

- **Lock entries of archived steps.** Recommendation: keep them, so `explain` retains provenance; prune only steps absent from the tree.
- **Probe text in the lock.** Commit only the digest, or keep the text and refuse probe output that contains an absolute path. Recommendation: keep the text and refuse such output with an error naming the line, since the line-level difference is what `explain` shows a coauthor.

Owning tasks: [02-runner](../../02-runner/task.md), [task-scoped-builds](../../11-scoped-verification/task-scoped-builds/task.md), [02-build-record](../../13-staleness-provenance/02-build-record/task.md).

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
