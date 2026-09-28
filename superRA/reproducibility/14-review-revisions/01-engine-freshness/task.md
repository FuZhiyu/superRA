---
title: "Engine: No False Fresh and No Needless Reruns"
status: not-started
depends_on: []
---

## Objective

`status` and `build` agree with the current bytes in every journey below, each pinned by a test in the `test_repro*.py` suite.

- **Symlinked subdirectories inside a directory dependency are hashed.** [`tree_hash`](../../../../skills/task-tree/scripts/_repro_state.py#L177-L191) walks with `os.walk` without `followlinks` and silently skips unreadable files. Follow links with a cycle guard; a broken link or unreadable file under a declared directory surfaces as an error or `external`, never as a silent omission.
- **pytask's SQLite state never decides a skip.** A step the lock does not list executes, and `status` and `build` agree after `pytask.lock` is deleted or a commit without a lock is checked out.
- **A targeted build keeps a sidecar-tracked saved input's consumer fresh** when nothing changed: [`check_boundary_receipt`](../../../../skills/task-tree/scripts/_repro_scope.py#L69) records the digest when the bytes match the producer's recorded output or the sidecar matches the lock, instead of rerunning.
- **Scoped `status` does not exit 0 while producers behind the selection are stale.** Report the stale upstream count and give it a distinct nonzero exit.
- **`pytask-parallel` is pinned** beside `pytask>=0.6,<0.7` in [repro_run.py:4](../../../../skills/task-tree/scripts/repro_run.py#L4).

### Researcher decisions

- **Keep pytask or replace it with an in-house topological runner.** Recommendation: keep pytask for 0.5 with the fixes above and revisit after real-project use.

Owning tasks: [02-runner](../../02-runner/task.md), [task-scoped-builds](../../11-scoped-verification/task-scoped-builds/task.md).

## Details

### Evidence (engine review, reproduced on a scratch project at `7d5fa992`; repo suite 275 passed)

- **Symlink false fresh.** Step `agg` read `Data/panel/`, with `Data/panel/y2020 -> extdata/y2020`. After editing `extdata/y2020/p.csv`, `status agg` printed `✓ agg fresh … up to date` and `build agg` skipped it; `output/agg.csv` kept the old value. A directory holding only such a link hashes to `dir:e3b0c442…`, the hash of nothing. No test covers symlinks; worktree-data-sync creates them.
- **SQLite override.** With `pytask.lock` deleted and `.pytask/` kept, `status .` reported "5 missing / never built" and `build .` reported "5 Skipped because unchanged" and silently rewrote the lock. pytask 0.6 falls back to `.pytask/pytask.sqlite3` when no lock exists (`use_lockfile_for_skip=False` in `_pytask/lockfile.py`).
- **Sidecar rerun.** After `build .`, `build 03-report` reran `report` with the message `saved input ${OUT}/big.bin needs a full-byte baseline`. On a fresh clone `status .` showed `report` fresh, yet `build 03-report` reran it.
- **Scoped status.** After editing `Data/raw.csv`, `status 02-est 03-report` printed "3 fresh" and exited 0; the only hint was the footer "upstream freshness not verified". The "(selected steps only)" label also appears for `.`.

### pytask coupling (for the decision)

superRA already decides freshness, forcing, acceptance skips, and saved inputs, and writes receipts itself. pytask adds ordering, threads, and lock writing at the cost of four private imports (`_pytask.pluginmanager.storage`, `_pytask.build.normalize_programmatic_config`, `_pytask.cli.DEFAULTS_FROM_CLI`, `_pytask.outcomes`), a `tryfirst` hook raising `SkippedUnchanged` so pytask never rewrites the lock entry, a workaround because pytask-parallel bypasses `execute`, and direct TOML reads of pytask's lock format.

### Minor findings to settle or document

- `build --dry-run` lists every downstream step as "would execute", so its cost total is an upper bound; label it.
- `status .` exits 1 on every fresh clone until check steps run locally.
- An acceptance that no longer validates lingers with a "clear it with revoke" message while the lock still matches.
- Lock entries for renamed or archived steps are never pruned (*inferred*).
- Python imports are not tracked; only the Julia `include` closure is (*inferred*).
