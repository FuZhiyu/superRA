---
title: "File Checks and Step States Never Download"
status: revise
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
  - A directory is online-only when anything under it is, and has no size.
- **Acceptance.**
  - `accept` refuses a file it cannot hash, naming it: `build-a: cannot record Code/a.sh, which is online-only here`.
  - A valid acceptance whose files cannot be hashed here reads `unverified` with reason `reviewed baseline; <file> is online-only here`, not invalid.
- **Run floor.** In [repro_run.py](../../../../skills/task-tree/scripts/repro_run.py), `build` skips an `unverified` step and counts it `unverified`.
  - `_missing_inputs` no longer reads `external`. It refuses to start any step, dry runs included, whose input is absent, online-only and uncached, or unreadable.
- **Saved-input rename.** The provenance `unverified` is now `no successful build recorded`, and the boundary change `unverified` is now `unbaselined`.
  - A saved input that cannot be hashed here has `digest: null` and says why under `here`. It makes its consumer `unverified`, and `build` no longer refuses it as missing.

### Deviations and decisions

- **Lock version stays `2`.** `sizes` is an optional key that older readers ignore, so a lock written before this change and a lock read by an older superRA both still work. A version bump would have made older checkouts reject the lock.
- **A check that passed elsewhere needs every input checked.** It stays `fresh` when its inputs match, including an online-only input still in this machine's hash cache. An uncached input makes it `unverified`, because "at these inputs" cannot be confirmed.
- **An absent output a step produces keeps its consumer `stale`.** The consumer's dependency reads `missing`, as before. Only an absent file no step produces is `unknown`.
- **A forced `unverified` step still goes through the input check,** so `--force` never reads a file the machine cannot hash. 02 decides the final `--force` scope.
- **A broken link inside a directory dependency now reads `unverified`, not `stale`.** Updated in [test_repro_engine.py](../../../../skills/task-tree/scripts/test_repro_engine.py).
- **`accept` hashes without the persistent cache, as before,** so it refuses any `SF_DATALESS` file, even one cached from an earlier read.
- **A never-built step's file on disk has `outcome: null`.** The status never hashes a never-built step's files.
- **Cache key.** It stays (path, size, mtime_ns). The validation was read-only, so whether size and mtime survive a download and a later eviction was not observed.

### Left for siblings

- **02-upstream-default.**
  - The download gate must also catch an online-only input that is in the hash cache: `_missing_inputs` passes it because it can be hashed.
  - `report.ok` still counts `unverified` as not ok, so `status` exits 1 for it.
  - The frontier `CURRENT` set still flags inputs from `unverified` producers.
  - The "(stale, missing, failed, or external)" exit-code line at [commands.md:114](../../../../skills/task-tree/references/commands.md#L114).
- **03-state-display.** `dashboard.js` has no `unverified` entry in `REPRO_STATES` and still lists `external`.
- **04-discipline.** The `external` state appears in [reproducibility/SKILL.md:35](../../../../skills/reproducibility/SKILL.md#L35) and [rerun-or-accept.md:9](../../../../skills/reproducibility/references/rerun-or-accept.md#L9).

### Verification

- **Regression tests.** [test_repro_online.py](../../../../skills/task-tree/scripts/test_repro_online.py) has 16 tests covering every Validation bullet, with `file_flags`, `has_placeholder_xattr`, `Path.open`, `open`, and `os.scandir` monkeypatched.
  - Removing any of the four read guards (`explain` diff, `accept` baseline diff, sidecar read, directory listing) fails its test.
- **Full suite.** `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`: 1082 passed, 10 skipped.
- **OlinStudio, read-only.** A disposable fixture outside the repo used real files as dependencies:
  - The legacy placeholder `~/Dropbox/Fit3D_Measurements_History.csv`.
  - The `SF_DATALESS` Box file `~/Library/CloudStorage/Box-Box/ois_historical_data_extended.xlsx` (5,123,878 bytes).
  - The fixture's lock entries recorded a placeholder hash for each, and the Box file's true size.
  - Results:
    - `status` reported both dependencies `unknown` with `online_only: true`.
    - `build` skipped both steps as `unverified`.
    - `accept --dry-run` refused the Box file.
  - Afterwards the Box file still had `SF_DATALESS` set and the same size and mtime, and the placeholder was still zero bytes with its `com.dropbox.placeholder` xattr.

## Review Notes

Tier: thorough. Focus: correctness, test quality.

1. **[BLOCKING] A build still runs a step whose input is online-only but cached, and the run then records the step `failed`.**
   - **Problem.** `_missing_inputs` hashes inputs through the persistent `build.cache`, so a cached online-only input passes ([repro_run.py:132](../../../../skills/task-tree/scripts/repro_run.py#L132)). The step's command then reads the file, which downloads it.
     - Before and after the run, `current_state` builds a new `HashCache()` with no persistent entries ([repro_run.py:179](../../../../skills/task-tree/scripts/repro_run.py#L179), [_repro_acceptance.py:272](../../../../skills/task-tree/scripts/_repro_acceptance.py#L272)). It records the input as `Unread` before the run.
     - After the run, the input is either still `Unread`, which raises "cannot be hashed here after execution" ([_repro_acceptance.py:279](../../../../skills/task-tree/scripts/_repro_acceptance.py#L279)), or, once downloaded, a hash that differs from the `Unread` value, which raises "dependencies changed during execution".
     - Before this commit, the same build downloaded the file and succeeded. It now downloads the file and records a failure.
   - **Reproduction.** In a probe on `CHAIN`: build; edit `Code/b.sh`; evict `output/a.txt` while it is still cached; then `build 02-b#build-b`. The command exits 0, and the run record is `failed` with `${OUT}/a.txt cannot be hashed here after execution (online-only here)`.
   - **Fix.** In `_missing_inputs`, refuse an input that is online-only by metadata (`cache.probe(...)[0]` or `is_online_only`), whether it is cached or not. This is the per-step half of the parent's download gate, and it matches the run floor's purpose. Add a test that builds a stale step whose input is cached and evicted. "Left for siblings" then no longer needs the first 02 bullet.
2. **[BLOCKING] The edit-detection hook opens online-only reproduction dependencies on every session.**
   - **Problem.** `_repro_watch` watches every literal-path dep and every declared directory dep of every registered step ([task_hook.py:912](../../../../skills/task-tree/scripts/task_hook.py#L912)). `detect` hashes each watched file that is missing from the session baseline with a plain `open` ([_edit_detect.py:263-279](../../../../skills/task-tree/scripts/_edit_detect.py#L263-L279), [:177-184](../../../../skills/task-tree/scripts/_edit_detect.py#L177-L184)).
     - The hashing covers files of up to 4 MB, and up to 64 MB per call.
     - The hook seeds this baseline on every `UserPromptSubmit`, so each session opens, and downloads, every small online-only dep and lists every directory dep.
     - A probe confirms it: with `Code/a.sh` evicted, `_edit_detect.detect(plan_root, …, _repro_watch(plan_root))` trips the `Offline` open guard.
   - **Scope.** The parent's §Checking files says "Every read of a tracked file goes through this check", and this task's Objective bullet says "No tracked read bypasses the check". The hook was missing from the Objective's list of read sites, so the orchestrator may route this fix to another task instead.
   - **Fix.** In `visit`, keep an online-only file in the baseline with no digest and without opening it. In `_scan_dir`, check each directory's `SF_DATALESS` flag before descending into it. Add an `Offline` test over `detect`.
3. **[ADVISORY] The forced-`unverified` deviation has no test.** A probe confirms that `build 01-a#build-a --force` with `Code/a.sh` evicted and uncached exits 1 with "cannot start: input Code/a.sh is online-only here" and runs nothing. No test in [test_repro_online.py](../../../../skills/task-tree/scripts/test_repro_online.py) covers this case. Add the probe as a test.
4. **[ADVISORY] `probe` walks whole directories that status otherwise skips.** For a directory without a recorded walk, `probe` calls `_holds_online_only`, which runs `stat` on every file under it ([_repro_state.py:354-372](../../../../skills/task-tree/scripts/_repro_state.py#L354-L372), [:389](../../../../skills/task-tree/scripts/_repro_state.py#L389)).
   - `_file_rows` calls `probe` on every status ([_repro_state.py:1252](../../../../skills/task-tree/scripts/_repro_state.py#L1252)). For a sidecar-tracked directory out, the sidecar is hashed instead of the directory, so each status and each dashboard refresh walks the very large intermediate that the sidecar exists to avoid.
   - `node_sizes` walks every directory node after each build and then discards the result, because `probe` returns no size for a directory ([_repro_state.py:629](../../../../skills/task-tree/scripts/_repro_state.py#L629)).
   - **Fix.** Skip directories in `node_sizes`. Answer a sidecar directory's `online_only` from its sidecar and the directory's own flag, without walking it.
5. **[ADVISORY] A dead line in a precedence test.** In [test_repro_online.py:226](../../../../skills/task-tree/scripts/test_repro_online.py#L226), the first `entry = project.status(...)` is overwritten at line 229 before it is used. Delete it.
