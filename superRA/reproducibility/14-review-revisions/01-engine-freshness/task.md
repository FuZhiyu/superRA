---
title: "Engine: superRA Runs Builds Itself, With No False Fresh and No Needless Reruns"
status: not-started
depends_on: []
---

## Objective

`superra repro build` runs on superRA's own build loop with no pytask dependency and writes one committed lock, `repro-lock.json`; `status` and `build` then agree with the current bytes in every journey below, each pinned by a test in the `test_repro*.py` suite.

### One engine, one freshness rule

- **`build` decides run or skip through the rule `status` uses.** Each selected step is checked with `_repro_state.compute_status`, counting steps completed earlier in the same run, so a rerun that regenerates identical bytes still stops the cascade. [_repro_hooks.py](../../../../skills/task-tree/scripts/_repro_hooks.py) and the pytask adapter types in [repro_run.py](../../../../skills/task-tree/scripts/repro_run.py) (`FileNode`, `SpecNode`, `StepTask`, the `_pytask` imports) are deleted; their acceptance, saved-input, receipt, and build-record logic runs inline in the loop.
- **Execution semantics carry over unchanged:**
  - Steps run in dependency order; a failed step skips its descendants while unrelated branches continue.
  - `-j N` runs ready steps on a thread pool sharing one hash cache.
  - `--force`, `--upstream`, and `--dry-run` keep their current scope; a crashed or forced attempt still retries through the `running` / `pending` run records.
  - Ctrl-C stops running subprocesses and marks their run records failed.
- **The lock is written per step.** A successful step's entry is written atomically (temp file, then rename) under the existing mutation lock, so an interrupted build keeps every completed entry. A skipped step keeps its entry; a failed step leaves its entry unchanged.
- **No pytask anywhere.** pytask and `pytask-parallel` leave the PEP 723 block of `repro_run.py`, and the `uv` re-exec and "needs pytask" paths go with them. The tests gated by `needs_pytask` run under the standard contributor command in [CLAUDE.md](../../../../CLAUDE.md).

### `repro-lock.json`

- **Shape:** a `version` field; per-step entries keyed and sorted by step name, each with
  - `spec` — the two-half definition hash from `spec_hash`;
  - `deps` and `outs` — logical path to content hash (the sidecar digest for a sidecar-tracked out, the stamp for a check step);
  - `built_on` — `platform` and the `env_probe` digest of the last successful build;
  - a top-level `probes` table mapping digest to probe text.

  One key per line with sorted keys, so two branches that build different steps merge without conflict.
- **Freshness reads only `spec`, `deps`, and `outs`.** `built_on` feeds `explain`'s environment comparison and nothing else.
- **The build record folds into the lock.** `repro-builds.json` and its `lock_id` link are retired. An entry is rewritten only when `spec`, `deps`, `outs`, or the probe digest change; `built_at` and `env.deps` are not carried.
- **Stale entries are pruned.** A build removes entries for steps no longer in the tree (decision below for archived steps).
- **Every lock reader switches together:** `read_lock` and its callers, the per-revision lock index behind `explain` (which reads `repro-lock.json` and, at older revisions, `pytask.lock` with `repro-builds.json`), `explain`'s environment comparison, and the dashboard watcher that emits `repro-updated` ([internals.md:258](../../../../skills/task-tree/references/internals.md#L258)).
- **Older projects read unchanged.** Without `repro-lock.json`, `pytask.lock` and `repro-builds.json` are read and converted in memory (pytask's `<step>::spec` dependency becomes `spec`; its `state` field is dropped). The first build writes `repro-lock.json` and prints that `pytask.lock` and `repro-builds.json` can be removed with `git rm`; it deletes neither. Nothing creates `.pytask/`.

### Freshness fixes, on the new loop

- **Symlinked subdirectories inside a directory dependency are hashed.** [`tree_hash`](../../../../skills/task-tree/scripts/_repro_state.py#L177-L191) walks with `os.walk` without `followlinks` and silently skips unreadable files. Follow links with a cycle guard; a broken link or unreadable file under a declared directory surfaces as an error or `external`, never as a silent omission.
- **A missing lock means never built.** With neither `repro-lock.json` nor `pytask.lock` present, `status` reports every step missing and `build` executes every step; no other local state decides a skip.
- **A targeted build keeps a sidecar-tracked saved input's consumer fresh** when nothing changed: [`check_boundary_receipt`](../../../../skills/task-tree/scripts/_repro_scope.py#L69) records the digest when the bytes match the producer's recorded output or the sidecar matches the lock, instead of rerunning. With one freshness rule this may already hold; the regression test decides.
- **Scoped `status` does not exit 0 while producers behind the selection are stale.** Report the stale upstream count and give it a distinct nonzero exit.

### Mechanics docs

[internals.md](../../../../skills/task-tree/references/internals.md), [commands.md](../../../../skills/task-tree/references/commands.md) §Reproduction, the record sections of [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md), and the engine line of [reproducibility/SKILL.md](../../../../skills/reproducibility/SKILL.md#L11) name the new engine and `repro-lock.json`. Factual edits only; [07-instruction-rewrite](../07-instruction-rewrite/task.md) owns the gate rewrite.

### Validation

- The `needs_pytask` tests pass without pytask installed; only the two tests of the "needs pytask" message change.
- On this repo, `repro status .` reports the same state per step before and after the first new-engine build converts `pytask.lock`.
- New tests: the lock round-trips byte-identically; ordering and failure skips under `-j`; Ctrl-C mid-build; two branches building different steps merge cleanly; `status` and `build` agree with the lock deleted.

### Researcher decisions

- **Lock entries of archived steps.** Recommendation: keep them, so `explain` retains provenance; prune only steps absent from the tree.

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
