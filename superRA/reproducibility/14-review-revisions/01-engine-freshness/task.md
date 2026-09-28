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

## Review Notes

Planning review, design-review mode: the revised engine design and its fit with the runtime components and siblings 02–09. Claims checked against code at `603dfa60` and pytask 0.6.0 source.

1. **[BLOCKING] Reshaping the lock entry silently invalidates every existing acceptance record and local receipt.** The design renames the in-memory entry (`<step>::spec` moves out of deps into `spec`, `produces` becomes `outs`), but acceptance and receipts compare against the pytask shape.
   - [_repro_acceptance.py:91](../../../../skills/task-tree/scripts/_repro_acceptance.py#L91) `lock_state` returns `{deps: depends_on, products: produces}`; [:106](../../../../skills/task-tree/scripts/_repro_acceptance.py#L106) puts the spec hash inside `deps` under `<step>::spec`; [:190-214](../../../../skills/task-tree/scripts/_repro_acceptance.py#L190-L214) invalidates a record when `baseline.lock` or `state` differs; [:184](../../../../skills/task-tree/scripts/_repro_acceptance.py#L184) classifies spec rows by the `::spec` suffix.
   - Receipts in `.superra-repro/baselines/` are checked the same way ([_repro_scope.py:63](../../../../skills/task-tree/scripts/_repro_scope.py#L63), [:68](../../../../skills/task-tree/scripts/_repro_scope.py#L68)).
   - After conversion, every committed acceptance reads "successful baseline changed". Reviewed steps then rerun, which is the cost the researcher chose to avoid. Sidecar consumers lose their receipt and rerun with "needs a full-byte baseline", and `accept` on a sidecar producer raises "no verified output digest".
   - Fix: state which shape `LockEntry`, `lock_state`, and `current_state` carry. Either keep the internal shape and change only serialization, or normalize legacy records and receipts on read. Settle with [02](../02-portable-records/task.md) who migrates committed acceptance records; 02 now reshapes them after 01, so the interim must still validate. Pin it with the fixture in item 3.

2. **[BLOCKING] "Under the existing mutation lock" gives the per-step writes no protection under `-j`.** `mutation_lock` is one non-blocking `flock` that the build process holds for the whole session ([repro_run.py:381](../../../../skills/task-tree/scripts/repro_run.py#L381), [_repro_acceptance.py:44-56](../../../../skills/task-tree/scripts/_repro_acceptance.py#L44-L56)). Worker threads writing `repro-lock.json` read-modify-write it unguarded, and a lost update drops a completed entry, so that step reruns next time. The build record already needs a thread lock for this reason ([_repro_builds.py:22](../../../../skills/task-tree/scripts/_repro_builds.py#L22), [:84](../../../../skills/task-tree/scripts/_repro_builds.py#L84)). Fix: name an in-process single writer, or a thread lock around each lock write, and have the `-j` test assert that every completed step's entry is present.

3. **[BLOCKING] The Validation list states one false claim and cannot catch the migration regressions.**
   - **"Only the two tests of the needs-pytask message change" is false.** These tests also change:
     - [test_repro_builds.py:19-23](../../../../skills/task-tree/scripts/test_repro_builds.py#L19-L23) asserts `repro-builds.json` and `lock_id`.
     - [test_repro_runner.py:576](../../../../skills/task-tree/scripts/test_repro_runner.py#L576) asserts `build-a::spec` in `depends_on`.
     - [:733](../../../../skills/task-tree/scripts/test_repro_runner.py#L733) asserts pytask's "Would be executed" summary.
     - [:711](../../../../skills/task-tree/scripts/test_repro_runner.py#L711) asserts `.ok` for a scoped status with stale ancestors, which the scoped-status fix contradicts.
     - `test_repro_provenance.py` (:98, :165) and `test_dashboard.py` (:6834–6974) name `pytask.lock`.
   - Fix: list the tests expected to change and why, so any other test edit reads as a regression.
   - **"On this repo, status matches before and after conversion" cannot discriminate.** This repo has no `repro-acceptance.json`. Its check steps depend on the scripts 01 rewrites (`build-record-check` in [pytask.lock](../../../../pytask.lock) depends on `repro_run.py` and `_repro_state.py`), so they go stale for real.
   - Fix: build a fixture with the pytask engine at `7d5fa992` holding an acceptance, a sidecar out with a scoped-build receipt, a check step, and `repro-builds.json`. Under the new code, `status --json` and `explain` must match before and after the first new-engine build.
   - **Missing:** `explain` across the transition, on a history with `pytask.lock` revisions followed by `repro-lock.json` revisions.

4. **[ADVISORY] Unnamed contracts that pytask or the hooks supply today.** Name each so the inline loop keeps it:
   - **Pre-run input check.** pytask raises `NodeNotFoundError` before running a step with a missing dependency (`_pytask/execute.py` ~l.200). Map each `compute_status` state to an action; `external` fails the step without running it.
   - **Frozen selection scope.** The per-step `compute_status` call must evaluate against the whole build selection. The hook's single-step target ([_repro_hooks.py:38](../../../../skills/task-tree/scripts/_repro_hooks.py#L38), [:46](../../../../skills/task-tree/scripts/_repro_hooks.py#L46)) turns in-selection sidecar producers into saved inputs.
   - **Per-step checks.** `check_sources` mid-build declaration guard ([_repro_hooks.py:18](../../../../skills/task-tree/scripts/_repro_hooks.py#L18), [:70](../../../../skills/task-tree/scripts/_repro_hooks.py#L70)); the missing-out-after-run failure from `capture_receipt`.
   - **Dry-run writes nothing**, including no `supersede` ([_repro_hooks.py:30-32](../../../../skills/task-tree/scripts/_repro_hooks.py#L30-L32)).
   - **Output and exits.** Define the build summary and exit codes, and give the value of the new scoped-status exit, which [08](../08-workflow-wiring/task.md) must document.

5. **[ADVISORY] The "every lock reader" list misses readers.**
   - **Status path.** `check_elsewhere_reason` reads `repro-builds.json` and `lock_id` ([_repro_provenance.py:151-163](../../../../skills/task-tree/scripts/_repro_provenance.py#L151-L163)), contradicting "`built_on` feeds explain and nothing else".
   - **Lock-index cache.** `.superra-repro/lock-index/<sha>.json` caches parsed entries by sha ([:212-226](../../../../skills/task-tree/scripts/_repro_provenance.py#L212-L226)), so a shape change needs a cache version.
   - **Both files present.** While both files exist (the build deletes neither), history and the working read must prefer `repro-lock.json`.
   - **Dashboard watcher.** It now fires once per step, and a temp-file-plus-rename write may drop a single-file watch on Linux (*inferred*).

6. **[ADVISORY] Removing the `uv` re-exec also removes the Python 3.10 path.** The re-exec also serves `status`, `explain`, `accept`, and `revoke` without `tomllib` ([repro_run.py:581](../../../../skills/task-tree/scripts/repro_run.py#L581)), while `cli.py` requires Python 3.10 or newer. Reading a legacy `pytask.lock` still needs `tomllib`. State what Python 3.10 does with a legacy lock, and `repro_run.py`'s `requires-python`.

7. **[ADVISORY] Gaps in the `repro-lock.json` shape.**
   - **`built_on.platform` can go stale.** The rewrite-only-when rule omits platform, so `built_on` can name the wrong builder.
   - **`probe_error` has no home.**
   - **Stamp key.** The check-step stamp is keyed by `.superra-repro/stamps/…`, which 02's per-machine-state move would re-key; choose a location-independent key now.
   - **Merge test coverage.** JSON commas and the shared `probes` table can conflict when each branch adds a step or records different probe output; extend the merge test to those cases.
   - **Pruning.** Prune only on an error-free graph (03 may relax build refusal) and never under `--dry-run`.

8. **[ADVISORY] Ownership overlaps with siblings.**
   - **`probes` table.** 02's `env_probe` leak bullet decides whether this table, which 01 creates, keeps probe text. The two share an edit surface, so move that decision into 01.
   - **Registered steps still pull pytask, and no task owns them.** This repo's step `cmd`s still carry `--with 'pytask>=0.6,<0.7' --with pytask-parallel`: [task-scoped-builds](../../11-scoped-verification/task-scoped-builds/task.md) :26/:64, [01-provenance-explain](../../13-staleness-provenance/01-provenance-explain/task.md) :39, [02-build-record](../../13-staleness-provenance/02-build-record/task.md) :30, and [unified-dependency-workflow](../../07-workflow-integration/unified-dependency-workflow/task.md) :86. 09's stale-content list omits them; assign them to 01.
