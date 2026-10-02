---
title: "Build What This Machine Can Check: Producer Chain by Default, Online-Only Data Reported"
status: in-progress
depends_on: []
---

## Objective

Make `superra repro` act on what the machine running it can verify. `build` and `status` include a selection's producer chain by default, `--only` restricts them to the named steps, and no command ever downloads a file: online-only and absent data are reported, not misread. The dashboard shows each state, where staleness starts, and what is online-only at a glance. At Mature, fold the result into the tasks §At Mature lists.

### Decisions

**Checking files.** A check never downloads. Each file gets one outcome:

| File | Outcome |
|---|---|
| On disk, or in this machine's hash cache at its current size and mtime | its hash: **matches** or **changed** |
| Absent, and a step produces it | **absent** (its producer reads `missing`) |
| Absent, and no step produces it | **unknown** |
| Online-only and not cached: size differs from the lock | **changed** |
| Online-only and not cached: same size; or the read fails | **unknown** |

- **Online-only means** `st_flags & SF_DATALESS` (File Provider: Dropbox, Google Drive, Box, OneDrive, iCloud), or a zero-byte file carrying the `com.dropbox.placeholder` xattr (legacy Dropbox). An mtime difference alone never counts as a change.
- **Size comparison applies only to `SF_DATALESS` files.** `lstat` reports a legacy placeholder's size as 0, so an uncached placeholder is always unknown.
- **The lock records each file's size** beside its hash. A sidecar-tracked out records the size of the out itself; a directory dep records no size, so a directory holding an uncached online-only file is unknown.
- **Every read of a tracked file goes through this check,** including `explain`'s diffs, `accept`'s preview, and sidecar reads.

**Step states.** Each step takes the first state its own evidence supports. The order follows `_classify` today, with `unverified` added just above `fresh`:

| If | State |
|---|---|
| Its last run failed or was interrupted, and it still has work to do | `failed` |
| It has never been built | `missing` |
| An output is **absent** (a check that passed at these inputs on another machine stays `fresh`, as today) | `missing` |
| Its definition or any of its files is **changed** | `stale` |
| Any file is **unknown** | `unverified` |
| Otherwise, or a valid acceptance covers it | `fresh` |

- **`external` is removed as a state.** "External input" stays as the name for a file no step produces.
- **Reported state.** A `fresh` or `unverified` step whose producer is `stale`, `missing`, or `failed` is reported `stale`. The step's own state is kept alongside, and the reason names the **origin**: the step furthest upstream on that path whose own state is `stale`, `missing`, or `failed`.
- **"unverified" names only this state.** The saved-input provenance that `_repro_scope.py` labels "unverified" today is renamed.

**Commands.**

- **Default scope.** `build`, `status`, and `build --dry-run` resolve the targets plus their transitive producers, through one resolver.
- **`--only`** restricts to the named selection; files from producers outside it are used as they sit on disk, as today. Use it when another session is editing a producer in this worktree. **`--upstream`** stays as a hidden no-op alias.
- **`--force`** reruns the named selection only; added producers run only when their state calls for it.
- **What runs.** In dependency order, a build runs `stale`, `missing`, `failed`, and forced steps. `unverified` steps never run, and their outputs are used as they are. A step stale only through upstream reruns only if its inputs changed after its producer ran (existing behavior).
- **Download gate.** Before running anything, if a step that will run reads a file not on disk (online-only, or absent with no producer), the build runs nothing. It lists those files with their sizes (capped), names `--only` as the way to build the rest, and points to [online-only-files.md](../../../skills/reproducibility/references/online-only-files.md) for online-only files. The same check runs again when each step starts, because a step can turn stale after its producers run. No command downloads, and no download flag exists.
- **Build preview.** Before executing, `build` prints the added producers that will run, with their last recorded durations (capped). It does not prompt. `--dry-run` keeps its per-step listing.
- **`accept` and `revoke`** act on the named steps only. `accept` refuses to record a file it cannot hash here, naming it. After recording, it names the non-fresh producers behind the accepted step (capped) and says the step reads stale until they are built or accepted.
- **Default `status` output.**
  - One line per selected step.
  - Producers that are `stale`, `missing`, or `failed` are listed (capped); fresh producers are counted.
  - `unverified` producers collapse to one line with their count, their total online-only size, and the **boundary**: the first `unverified` producer on each path back from the selection.
  - Exit 0 when every assessed step is `fresh` or `unverified`; 1 when a selected step's own state is `stale`, `missing`, or `failed`; 3 when the selection's own states are fine but a producer behind it is `stale`, `missing`, or `failed`.

**Display.** [03-state-display](03-state-display/task.md) owns the dashboard design language for these states.

**Frontier.** `task frontier` and `task read` flag only inputs whose producer is `stale`, `missing`, or `failed`. An `unverified` producer's input is not flagged, because a build never runs it.

**Unchanged.** Content hashing, early cutoff, acceptance validation, and `impact`. `explain` changes only to say "online-only here" where it says "missing here" today.

### Constraints

- [CLAUDE.md](../../../CLAUDE.md) §Bounded Agent-Facing Output governs every new or changed line of CLI and hook output.
- The task-tree core stays stdlib-only. Detection uses `os.lstat` flags and a `ctypes` `getxattr` call; `os.listxattr` does not exist on macOS.

## Details

### Why

- **Scoped default.** A TreasuryGIV session (transcript `02d0fe7f`, 2026-10-01) ran `status paper-reframing`, saw stale steps across two tasks, and passed all seven `task#step` selectors to `build`. Its own afterword: "Running `compile-deck` alone would've skipped stale upstream steps, so I listed them manually to avoid an unexpectedly long rerun."
- **Online-only data.** The hash cache reads any file it has not hashed at the current size and mtime ([_repro_state.py:202-220](../../../skills/task-tree/scripts/_repro_state.py#L202-L220)). On an online-only file, that read downloads it; when the read fails, the `OSError` becomes `None`, so an existing output reads `missing` and its producer reruns. A legacy Dropbox placeholder reads as an empty file and would hash as one. The producer-chain default widens both problems from the selection to its whole chain.

### Prior art (2026-10-01 surveys)

- **Upstream-by-default is the norm:** DVC, Snakemake, R `targets`, make, doit. The "only" modes are escape hatches that trust disk state: DVC `-s`, `targets` `shortcut = TRUE`.
- **Force scopes are separate** (Snakemake `-f` vs `-F`). **Accepting without running is step-local** (`dvc commit`, `make -t`, Snakemake `--touch`), and in those tools indistinguishable from a run.
- **A failed upstream:** pytask, Snakemake, and DVC skip the downstream step. Only DVC `--ignore-errors` runs it anyway, and it records the downstream step as up to date.
- **A missing raw input** is an error in make, Snakemake, and pytask, and a changed dependency in DVC; no tool has a state for it. DVC `--allow-missing` and Snakemake use existing outputs when the producer has no other change, the same rule as `unverified`.
- **No tool has `unverified`.** make and Snakemake compare mtimes, so they never read files. DVC and pytask hash, so a check downloads or fails. Hashing without implicit downloads leaves the gap `unverified` names.
- Sources: [DVC repro](https://doc.dvc.org/command-reference/repro), [DVC status](https://doc.dvc.org/command-reference/status), [Snakemake CLI](https://snakemake.readthedocs.io/en/stable/executing/cli.html), [tar_make](https://docs.ropensci.org/targets/reference/tar_make.html), [pytask CLI](https://pytask-dev.readthedocs.io/en/stable/tutorials/invoking_pytask.html).

### Online-only facts (checked on OlinStudio, macOS 15.7.3)

- **`lstat` returns the real size and mtime of an online-only File Provider file without downloading it.** Google Drive held 405 such files and Box 29, each with `st_blocks == 0` and `SF_DATALESS` set (mask it: one read `0x40000060`).
- **Directories:** `stat` inside an online-only directory can download that directory's listing ([TN3150](https://developer.apple.com/documentation/technotes/tn3150-getting-ready-for-data-less-files)), so walk a directory dep by checking each directory's flag before descending.
- **Legacy Dropbox:** Olin's `~/Dropbox` is the legacy client. Its online-only placeholders are zero-byte files with the `com.dropbox.placeholder` xattr and no `SF_DATALESS`; one exists at `~/Dropbox/764011267880-1701976534116.pdf`. None of 1,185 zero-byte files under `research_projects/` is one.
- **Downloading.** No reliable shell command exists:
  - `fileproviderctl` has no `materialize` here, and `brctl download` is iCloud-only.
  - A plain read may leave a File Provider file partial, and failed once with `ETIMEDOUT` on Google Drive.
  - Dropbox staff confirm there is no terminal option for legacy placeholders.
  - A coordinated read (`NSFileCoordinator`) requests the whole file; it works from PyObjC (`uv run --with pyobjc-framework-Cocoa`) or Swift.
- **Unverified:** whether size and mtime stay stable across download and eviction. The hash cache depends on it.

### Engine facts the change relies on

- **`accept` already ignores the scope default.** It selects with `include_ancestors=False` and reads `local_status` ([_repro_acceptance.py:438](../../../skills/task-tree/scripts/_repro_acceptance.py#L438), [:483](../../../skills/task-tree/scripts/_repro_acceptance.py#L483)).
- **The upstream cascade never forces a rerun.** It lifts a fresh step to stale in status only ([_repro_acceptance.py:384-385](../../../skills/task-tree/scripts/_repro_acceptance.py#L384-L385)). `build` reclassifies each step against its own target after its producers finish ([repro_run.py:115-120](../../../skills/task-tree/scripts/repro_run.py#L115-L120)).
- **`--force` covers the whole resolved scope today** ([repro_run.py:743](../../../skills/task-tree/scripts/repro_run.py#L743)).
- **The dashboard already assesses upstream** ([plan_dashboard.py:1483](../../../skills/task-tree/scripts/plan_dashboard.py#L1483), [_task_snapshot.py:68](../../../skills/task-tree/scripts/_task_snapshot.py#L68)).
- **Archived-task outputs are already external inputs** in the active graph, so the producer walk stops there.

### At Mature

These task files state the scoped default or the `external` state as current contract; rewrite their lines when folding: [02-runner](../02-runner/task.md), [03-task-interface](../03-task-interface/task.md), [04-dashboard-view](../04-dashboard-view/task.md), [06-skill](../06-skill/task.md), and [07-workflow-integration](../07-workflow-integration/task.md).
