---
title: "File Checks and Step States Never Download"
status: not-started
depends_on: []
---

## Objective

Implement the parent's §Checking files and §Step states in the freshness engine, so a check never downloads, and an online-only or absent file is never misread as missing or changed.

- **File outcomes.** The hash cache and `path_state` return matches/changed, absent, or unknown, never `None` for an existing file. An online-only file is never opened. A read error on an existing file is unknown.
- **Online-only detection** per the parent's definition, including the directory walk that checks each directory's flag before descending.
- **Lock sizes.** Lock entries record each file's size beside its hash; the reader accepts the current version 2 lock without sizes.
- **States.** Add `unverified`; remove `external` from `STATUSES` and the classification. The cascade lifts `fresh` and `unverified` steps to `stale` only for a `stale`, `missing`, or `failed` producer.
- **Acceptance.** `accept` refuses to record a file it cannot hash here, naming it. An acceptance whose files are online-only and uncached reads `unverified`, not invalid.
- **Mechanics docs.** [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md) (state table, the readiness lines that name `external`, reproduction records) and [internals.md](../../../../skills/task-tree/references/internals.md) §Reproduction records.

### Validation

- Regression tests with `lstat` flags and xattrs monkeypatched:
  - An online-only file is never opened. A cached one keeps its hash; an uncached one reads unknown, or changed when its size differs from the lock.
  - A legacy placeholder never hashes as an empty file.
  - A read `OSError` on an existing output yields `unverified`, never `missing`.
  - An absent file that no step produces makes its consumer `unverified`; an absent output makes its producer `missing`.
  - The cascade over `unverified`, and acceptance refusal and validation.
  - A version 2 lock still reads.
- The full script suite passes.
- Read-only on real files: `status` on a fixture whose dep is Olin's legacy placeholder reports it unknown. On a File Provider machine (home-studio or home-server), it reports a real online-only file without materializing it: `SF_DATALESS` is still set afterwards.

## Details

- **Where the change lands.** `HashCache.file_hash` / `_hashed` / `tree_hash` and `path_state` / `node_state` / `dependency_state` in [_repro_state.py](../../../../skills/task-tree/scripts/_repro_state.py); `_classify` and `STATUSES` there. Also `apply_to_status`, `validate_record`, and `current_state` in [_repro_acceptance.py](../../../../skills/task-tree/scripts/_repro_acceptance.py), and the saved-input checks in [_repro_scope.py](../../../../skills/task-tree/scripts/_repro_scope.py).
- **Cache key.** Keep (path, size, mtime_ns). Whether size and mtime survive a download and a later eviction is unverified; the File Provider validation run should note what it saw.
- **Scope split from [02-upstream-default](../02-upstream-default/task.md).** This task owns how files and steps get their states. 02 owns what commands do with them, including the download gate and all status rendering in `format_status`.
