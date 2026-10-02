---
title: "File Checks and Step States Never Download"
status: approved
depends_on: []
---

## Objective

Implement the parent's §Checking files and §Step states in the freshness engine, so a check never downloads, and an online-only or absent file is never misread as missing or changed.

- **File outcomes.** The hash cache and `path_state` return matches/changed, absent, or unknown, never `None` for an existing file. A read error on an existing file is unknown.
- **No tracked read bypasses the check.** An online-only file is never opened by the hash cache, `explain`'s diffs ([_repro_provenance.py:597](../../../../skills/task-tree/scripts/_repro_provenance.py#L597)), `accept`'s preview ([_repro_acceptance.py:424](../../../../skills/task-tree/scripts/_repro_acceptance.py#L424)), or sidecar reads ([_repro_scope.py:74](../../../../skills/task-tree/scripts/_repro_scope.py#L74)). `explain` says "online-only here" where it says "missing here" today ([_repro_provenance.py:916](../../../../skills/task-tree/scripts/_repro_provenance.py#L916)).
- **Online-only detection** per the parent's definition, including the directory walk that checks each directory's flag before descending.
- **Lock sizes** per the parent's rules; the reader accepts the current version 2 lock without sizes.
- **States.**
  - The parent's precedence: add `unverified`, and remove `external` from `STATUSES`, the classification, and `format_status`'s marks ([_repro_state.py:1125](../../../../skills/task-tree/scripts/_repro_state.py#L1125)).
  - The cascade lifts `fresh` and `unverified` steps to `stale` only for a `stale`, `missing`, or `failed` producer, and records the origin step.
  - Rename the saved-input provenance "unverified" ([_repro_scope.py:47](../../../../skills/task-tree/scripts/_repro_scope.py#L47), [:102](../../../../skills/task-tree/scripts/_repro_scope.py#L102)).
- **The run rule's floor.** `build` never runs an `unverified` step, and the "cannot start" check no longer reads `external` ([repro_run.py:124-148](../../../../skills/task-tree/scripts/repro_run.py#L124-L148)). That way no commit between this task and 02 runs a step on data it cannot check.
- **Per-file evidence.** Each step's status entry and JSON carry, per dep and out, its outcome, whether it is online-only, and its size. The gate, `status`, and the dashboard panel read these.
- **Acceptance.** `accept` refuses to record a file it cannot hash here, naming it. An acceptance whose files are online-only and uncached reads `unverified`, not invalid.
- **Mechanics docs.**
  - [commands.md](../../../../skills/task-tree/references/commands.md): the state table only.
  - [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md): reproduction records.
  - [internals.md](../../../../skills/task-tree/references/internals.md) §Reproduction records.

### Validation

- Regression tests with `lstat` flags and xattrs monkeypatched:
  - An online-only file is never opened, by the hash cache, `explain`, `accept`'s preview, or a sidecar read. A cached one keeps its hash; an uncached `SF_DATALESS` one reads unknown, or changed when its size differs from the lock.
  - A legacy placeholder never hashes as an empty file, and never reads changed for its zero size.
  - Precedence: a failed or interrupted step with an online-only input reads `failed`; a never-built one reads `missing`; a check that passed elsewhere at these inputs stays `fresh`.
  - The cascade reason names the origin step two levels up, not the immediate producer.
  - A read `OSError` on an existing output yields `unverified`, never `missing`.
  - An absent file that no step produces makes its consumer `unverified`; an absent output makes its producer `missing`.
  - The cascade over `unverified`, and acceptance refusal and validation.
  - A version 2 lock still reads.
- The full script suite passes.
- Read-only on real files, on OlinStudio: `status` on fixtures whose dep is Olin's legacy placeholder, and one whose dep is a real online-only Google Drive or Box file. It reports both unknown without materializing either: `SF_DATALESS` stays set, and the placeholder keeps its xattr.

## Details

- **Where the change lands.** `HashCache.file_hash` / `_hashed` / `tree_hash` and `path_state` / `node_state` / `dependency_state` in [_repro_state.py](../../../../skills/task-tree/scripts/_repro_state.py); `_classify` and `STATUSES` there. Also `apply_to_status`, `validate_record`, and `current_state` in [_repro_acceptance.py](../../../../skills/task-tree/scripts/_repro_acceptance.py), and the saved-input checks in [_repro_scope.py](../../../../skills/task-tree/scripts/_repro_scope.py).
- **Cache key.** Keep (path, size, mtime_ns). Whether size and mtime survive a download and a later eviction is unverified; the File Provider validation run should note what it saw.
- **Scope split from [02-upstream-default](../02-upstream-default/task.md).** This task owns how files and steps get their states, plus the floor that keeps `unverified` steps from running. 02 owns what commands do with the states: scope, the gate, and status rendering beyond the marks.

## Results

The freshness engine now checks files without ever downloading one, and steps take the parent's precedence with `unverified` in place of `external`. On OlinStudio, `status`, `build`, `explain`, and `accept --dry-run` ran over a legacy Dropbox placeholder and an `SF_DATALESS` Box file: both read `unknown`, the steps read `unverified`, and neither file materialized.

### File checks never open an online-only file

- **Outcomes.** [_repro_state.py](../../../../skills/task-tree/scripts/_repro_state.py) gives each file `matches`, `changed`, `absent`, or `unknown` through `outcome()`.
  - `HashCache.path_state` / `file_hash` return a hash, `None` (absent), or an `Unread` value (`online-only` or `unreadable`).
  - A read or `stat` error on an existing path is `Unread("unreadable")`, never absent.
- **Detection.** `is_online_only` checks `st_flags & SF_DATALESS`, or a zero-byte file with the `com.dropbox.placeholder` xattr (`ctypes` `getxattr`).
  - A placeholder is checked before the hash cache, so it never hashes as an empty file.
  - `tree_hash` checks each directory's flag before listing it. An uncached online-only file, a dataless subdirectory, or a broken link makes the whole directory `Unread`.
- **Guarded reads outside the cache.** Each one checks the file first, and a test fails if any of them opens a simulated online-only file:
  - `explain`'s snapshot diff, and its `git diff` against the working tree.
  - `accept`'s baseline diff (`inspect_baseline`) and receipt snapshots.
  - The sidecar read in `_bytes_verified`.
  - The Julia include scan in [_repro.py](../../../../skills/task-tree/scripts/_repro.py), which warns instead of reading.
  - The edit-detection hook in [_edit_detect.py](../../../../skills/task-tree/scripts/_edit_detect.py): an online-only file stays in the session baseline with no digest and is compared by `stat` alone, and `_scan_dir` never lists an online-only directory.
  - `explain <path>` prints "online-only here" (or "unreadable here") where it printed "missing here"; its JSON adds `here`.
- **Lock sizes.** A build records an optional `sizes` map beside the hashes: the out's own size for a sidecar, and none for a directory.
  - An uncached `SF_DATALESS` file whose size differs from the recorded one reads `changed`.
  - `LockEntry.sizes` takes no part in equality or in an acceptance's `lock` digest, so existing acceptances stay valid.

### States, cascade, and the run floor

- **Precedence.** `_classify` gives `failed` > `missing` > `stale` > `unverified` > `fresh`. `STATUSES` and the `status` marks drop `external` and add `unverified` (`○`).
- **Cascade.** `apply_to_status` lifts `fresh` and `unverified` steps to `stale` only for a `stale`, `missing`, or `failed` producer.
  - It sets `origin` to the furthest-upstream blocking step, and the reason names it: `upstream step 'build-a' is stale`.
  - The status JSON carries `origin`.
- **Per-file evidence.** Each status entry and its JSON carry `files`: one row per dep and out, with `node`, `role`, `outcome`, `online_only`, and `size`.
  - A directory has no size. It is online-only when its own flag says so or its hash walk found online-only content. `status` never walks a directory just to answer this; a sidecar-tracked out is judged from its sidecar and its own flag.
- **Acceptance.**
  - `accept` refuses a file it cannot hash, naming it: `build-a: cannot record Code/a.sh, which is online-only here`.
  - A valid acceptance whose files cannot be hashed here reads `unverified` with reason `reviewed baseline; <file> is online-only here`, not invalid.
- **Run floor.** In [repro_run.py](../../../../skills/task-tree/scripts/repro_run.py), `build` skips an `unverified` step and counts it `unverified`.
  - `_missing_inputs` no longer reads `external`. It refuses to start any step, dry runs included, whose input is absent, unreadable, or online-only by metadata. That covers a cached online-only input too, since reading it would download it.
  - A refused step writes no run record, so its last successful run stands.
- **Saved-input rename.** The provenance `unverified` is now `no successful build recorded`, and the boundary change `unverified` is now `unbaselined`.
  - A saved input that cannot be hashed here has `digest: null` and says why under `here`. It makes its consumer `unverified`, and `build` no longer refuses it as missing.

### Deviations and decisions

- **Lock version stays `2`.** `sizes` is an optional key that older readers ignore, so a lock written before this change and a lock read by an older superRA both still work. A version bump would have made older checkouts reject the lock.
- **A check that passed elsewhere needs every input checked.** It stays `fresh` when its inputs match, including an online-only input still in this machine's hash cache. An uncached input makes it `unverified`, because "at these inputs" cannot be confirmed.
- **An absent output a step produces keeps its consumer `stale`.** The consumer's dependency reads `missing`, as before. Only an absent file no step produces is `unknown`.
- **A forced `unverified` step still goes through the input check,** so `--force` never reads an online-only or unreadable file: it refuses and runs nothing. 02 decides the final `--force` scope.
- **A broken link inside a directory dependency now reads `unverified`, not `stale`.** Updated in [test_repro_engine.py](../../../../skills/task-tree/scripts/test_repro_engine.py).
- **`accept` hashes without the persistent cache, as before,** so it refuses any `SF_DATALESS` file, even one cached from an earlier read.
- **A never-built step's file on disk has `outcome: null`.** The status never hashes a never-built step's files.
- **Cache key.** It stays (path, size, mtime_ns). The validation was read-only, so whether size and mtime survive a download and a later eviction was not observed.

### Left for siblings

- **02-upstream-default.**
  - The pre-scheduling download gate and its message. The per-step refusal in `_missing_inputs` is the floor it builds on.
  - `report.ok` still counts `unverified` as not ok, so `status` exits 1 for it.
  - The frontier `CURRENT` set still flags inputs from `unverified` producers.
  - The "(stale, missing, failed, or external)" exit-code line at [commands.md:114](../../../../skills/task-tree/references/commands.md#L114).
- **03-state-display.** `dashboard.js` has no `unverified` entry in `REPRO_STATES` and still lists `external`.
- **04-discipline.** The `external` state appears in [reproducibility/SKILL.md:35](../../../../skills/reproducibility/SKILL.md#L35) and [rerun-or-accept.md:9](../../../../skills/reproducibility/references/rerun-or-accept.md#L9).

### Verification

- **Regression tests.** [test_repro_online.py](../../../../skills/task-tree/scripts/test_repro_online.py) has 19 tests covering every Validation bullet, with `file_flags`, `has_placeholder_xattr`, `Path.open`, `open`, and `os.scandir` monkeypatched.
  - They include a stale step whose cached input is evicted, a forced `unverified` step, and edit detection over an evicted file and directory.
  - Removing any of the six guards fails its test: `explain` diff, `accept` baseline diff, sidecar read, directory listing, the metadata check at step start, and edit detection.
- **Full suite.** `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`: 1085 passed, 10 skipped.
- **OlinStudio, read-only.** A disposable fixture outside the repo used real files as dependencies:
  - The legacy placeholder `~/Dropbox/Fit3D_Measurements_History.csv`.
  - The `SF_DATALESS` Box file `~/Library/CloudStorage/Box-Box/ois_historical_data_extended.xlsx` (5,123,878 bytes).
  - The fixture's lock entries recorded a placeholder hash for each, and the Box file's true size.
  - Results:
    - `status` reported both dependencies `unknown` with `online_only: true`.
    - `build` skipped both steps as `unverified`.
    - `accept --dry-run` refused the Box file.
    - `build --force` refused both steps before starting them.
    - Edit detection kept both files in its baseline with no digest.
  - Afterwards the Box file still had `SF_DATALESS` set and the same size and mtime, and the placeholder was still zero bytes with its `com.dropbox.placeholder` xattr.
