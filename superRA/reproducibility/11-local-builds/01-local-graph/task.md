---
title: "File Checks and Step States Never Download"
status: not-started
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
