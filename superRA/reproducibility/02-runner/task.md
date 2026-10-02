---
title: "The `superra repro` Runner: Engine, Records, Acceptance, and Diagnosis"
status: approved
depends_on:
  - 01-section-contract
---

## Objective

Own `superra repro`, which builds the steps of the graph from [01-section-contract](../01-section-contract/task.md), records what each build and review established, and explains why a step is not fresh. Command semantics are documented in [commands.md §Reproduction](../../../skills/task-tree/references/commands.md#reproduction); records in [internals.md §Reproduction records](../../../skills/task-tree/references/internals.md#reproduction-records).

- **Commands:** `build`, `status`, `explain`, `impact`, `accept`, `revoke`, `dag`. `build` and `status` require task or `task#step` targets (`.` for every registered step) and take in the targets' producer chain; `--only` restricts them to the targets against saved inputs, and `--force` reruns the targets only. `accept` and `revoke` act on the named steps.
- **One freshness rule** for `status` and `build`: SHA-256 content hashes with no size cap, looked up through a size-and-mtime cache, and early cutoff when a rerun regenerates identical bytes. `status`, `explain`, and `impact` run no build and need no engine.
- **No command downloads a file.** A file this machine cannot check without downloading it makes its step `unverified`; `build` never runs that step, and a build that would read a file not on disk runs nothing and lists it.
- **Committed records are portable and mergeable:** `repro-lock.json` keyed by logical `${VAR}` paths, one line per step; one acceptance record per step under `repro-acceptance/`. Nothing committed names a host, user, or time; git answers who and when. Local state stays in the gitignored, Dropbox-ignored `.superra-repro/`.
- **Reviewed acceptance is a second route to `fresh`**, distinct from execution: it never fabricates a lock entry, receipt, or check stamp, and forced execution bypasses it.
- **`explain` reports facts, not verdicts:** for each changed node, where the recorded and current bytes came from, one of three causes, and a tool pointer. The build-or-accept judgment stays in the [reproducibility skill](../../../skills/reproducibility/references/rerun-or-accept.md).

## Results

`superra repro` runs builds on superRA's own loop in [repro_run.py](../../../skills/task-tree/scripts/repro_run.py), with state in [_repro_state.py](../../../skills/task-tree/scripts/_repro_state.py), acceptance and impact in [_repro_acceptance.py](../../../skills/task-tree/scripts/_repro_acceptance.py), selection evidence in [_repro_scope.py](../../../skills/task-tree/scripts/_repro_scope.py), and provenance in [_repro_provenance.py](../../../skills/task-tree/scripts/_repro_provenance.py). The entry script pins only `pyyaml`.

### superRA owns the engine

The runner first generated pytask 0.6 tasks in memory; superRA now schedules steps itself, and pytask is no longer a dependency.

- **Why.** superRA already decided freshness, forcing, acceptance skips, and saved inputs. pytask added ordering, threads, and lock writing at the cost of four private imports, a hook raising `SkippedUnchanged`, and direct reads of its lock format.
  - Letting pytask own freshness was rejected: `task read`, `task frontier`, and the dashboard need step state on every call, and `status` ran in ~0.15 s against ~0.8 s for a pytask dry run. `pytask lock accept` also overwrites the lock, erasing the line between accepted and executed.
  - The migration fixture, a project built by the pytask engine, read identical step states under both engines, and its first build executed nothing.
- **Build loop.** Steps run as subprocesses in dependency order, `-j N` on threads. A step whose input is absent or not on this machine is refused before its command runs and writes no run record; a failed step skips its descendants. Ctrl-C, SIGTERM, or SIGHUP kills each running step's process group and records it failed; queued steps keep their records and acceptance.
- **Freshness fixes found by the 2026-09-28 design review**, each with a regression test in [test_repro_engine.py](../../../skills/task-tree/scripts/test_repro_engine.py):
  - A directory dep follows symlinks with a cycle guard; a symlinked data folder had read `fresh` after its contents changed.
  - A sidecar-tracked saved input counts as verified when its bytes match the producer's record or the digest its sidecar names; it had forced needless reruns on a fresh clone.

### Records

- **A step's definition is its own node.** The spec hash records the declared half (`cmd` as written, `params`, logical deps and outs) and the resolved command as `declared:resolved`, so a definition edit invalidates only that step and `explain` can say which half moved.
- **The lock holds one line per step** (version 2), so a git merge takes each entry whole from one side and cannot mix two builds into a false `fresh`. A conflicted lock still reads, dropping the entries the sides disagree on so their steps read `missing`. Entries record `built_on` (OS and architecture) for `explain` and an optional `sizes` map; no timestamp, so an identical rebuild leaves the lock byte-identical. Lock entries of archived steps are kept for provenance.
- **Acceptance records are one small file per step,** so branches that accept different steps merge cleanly, and two clones with different data roots and user names write byte-identical records. A record that does not parse or whose `id` does not match disables only its own step. On ElasticityBound (35 accepted steps), converting the legacy ledger preserved every step's status and reason, and records fell from 8.0 KB to 2.2 KB on average.
- **`.superra-repro/` carries Dropbox's ignore flag**, set by the runner and the edit hook. A live check between two machines confirmed a flagged folder never syncs, so another machine's in-progress run cannot mark a step failed here. Deleting the folder stales no step.

### Reviewed acceptance

`accept <targets> --reason '…'` previews, revalidates, and writes in one call under one lock; `--dry-run` previews. It covers first registration, harmless edits, and outputs from direct runs; never-run checks, missing files, invalid graphs, and failed runs stay blocked.

- A step whose own `status` already reads fresh is skipped and its record never rewritten.
- A consumer's record pins its producer's output bytes, so re-accepting or revoking the producer leaves the consumer's record valid; full-chain status reports the consumer stale while the producer is not fresh.
- An acceptance that no longer validates does not override a step whose bytes match its successful build: the step stays `fresh` and the reason names the `revoke` that clears the record.

### Diagnosis

The motivating case: six stale steps on IntermediaryDemand took about 20 tool calls to diagnose by hand, and none held a result-affecting change ([report](../../../docs/plans/2026-09-23-repro-staleness-explanations-report.md)). One `explain` call on that project now covers all of its non-fresh steps.

- **`explain <target>`** takes a task, a step, or a path and resolves each changed hash against the local receipt, the acceptance records, the lock history on local and remote-tracking branches, tracked-file blob history, and Dropbox conflicted copies. Every lock or git source states its relation to HEAD. Causes are `input-changed`, `other-build`, and `unknown-output`; `status` ends with the `explain` command to run when a step is not fresh and spawns no git.
- **Cost is bounded per call:** one history pass, a 64 MiB blob budget, a cache keyed on HEAD and branch tips, one row per changed file, and diff excerpts in a task view only with `--diff`. On ElasticityBound (4,262 commits, 173 branches, 74 stale steps) `explain .` fell from 3.9 s and 153 lines to 1.6 s and 32 lines; a synthetic 200,000-commit history from 10.9 s to 1.4 s.
- **A check that passed at these inputs elsewhere reads `fresh`**, with the lock revision and platform in its reason, once every input is checked here; a local failure still wins.
- **`impact <path>`** lists affected steps with their last durations, including every step a `superRA/config.yaml` change reaches through runner templates, variables, or `env_deps`. `build --dry-run` prices a rebuild the same way, as an upper bound. `status` counts the outside readers of each step's outs as a fact, never a task-local verdict.

### Selection: the producer chain by default

A TreasuryGIV session (transcript `02d0fe7f`, 2026-10-01) passed seven `task#step` selectors to `build` so that a scoped build would not skip stale upstream steps. Builds now take in the producer chain, as DVC, Snakemake, R `targets`, make, and doit do; `--only` is the escape hatch that trusts disk state, like DVC `-s` and `targets` `shortcut = TRUE`. Command semantics: [commands.md §Reproduction](../../../skills/task-tree/references/commands.md#reproduction).

- **Task targets replaced reproduction tiers.** A bare `build` or `status` fails naming the `.` target; `--tier` and `repro tier` exit 2 naming task targets; a leftover `tier:` key warns.
- **One resolver, flipped at the CLI.** `select_steps(..., include_ancestors=not args.only)` serves `build`, `status`, and `build --dry-run`. `--upstream` is a hidden alias for the default; combined with `--only` it is a usage error.
- **`--force` reruns the targets only;** an added producer runs only when its state calls for it. This keeps the fix for the [TreasuryGIV pilot's](../08-pilot-treasurygiv/task.md) unintended 40-minute upstream rebuild.
- **`build` previews** the added producers that will run, with their last durations, and prints a line only for steps that execute or fail.
- **`status` keeps the selection apart from its producers.** JSON lists `steps` and `producers` separately. It exits 0 when every assessed step is `fresh` or `unverified`, 1 when a selected step's own state is `stale`, `missing`, or `failed`, and 3 when only a producer's is. `status X --upstream` therefore exits 3 where it exited 1.
- **`accept` stays step-local.** After recording, it names the non-fresh producers behind the accepted steps and says those steps read stale until the producers are built or accepted.
- **Every elided list names its command.** Default text lists at most `OUTPUT_CAP` (10) items per list, then a count and the `--json` command.
- **Concurrent work does not abort a build.** Guards cover the selected declarations, resolved paths, artifact ownership, and input bytes; unrelated task creation, status changes, prose, and unused config edits pass ([internals.md §Build guards](../../../skills/task-tree/references/internals.md#build-guards)).
- **A pre-release project upgrades without rebuilding:** `pytask.lock`, `repro-builds.json`, and `repro-acceptance.json` are read until the first build or accept rewrites them. [RELEASE-NOTES.md](../../../RELEASE-NOTES.md) gives the order coauthors follow.

### No command downloads a file

Reading an online-only file downloads it, and the hash cache used to read any file it had not hashed at the current size and mtime. A failed read became a missing output, so its producer reran, and a legacy Dropbox placeholder hashed as an empty file. Now each file reads `matches`, `changed`, `absent`, or `unknown`, and a step with an `unknown` file is `unverified` (state table: [commands.md §Reproduction](../../../skills/task-tree/references/commands.md#reproduction)).

- **Online-only** means `st_flags & SF_DATALESS` (File Provider: Dropbox, Google Drive, Box, OneDrive, iCloud), or a zero-byte file carrying the `com.dropbox.placeholder` xattr, read through `ctypes` `getxattr`. `lstat` gives an `SF_DATALESS` file's real size and mtime without downloading it; a directory dep's walk checks each directory's flag before listing it.
- **`unverified` replaced the `external` state.** Precedence is `failed` > `missing` > `stale` > `unverified` > `fresh`. A `fresh` or `unverified` step behind a `stale`, `missing`, or `failed` producer reads `stale`, keeps its own state as `local_status`, and names the furthest-upstream such step as `origin`. No other build tool has this state: make and Snakemake compare mtimes, while DVC and pytask hash and so download or fail.
- **The lock records sizes** in an optional `sizes` map, so an uncached `SF_DATALESS` file whose size differs reads `changed`. The lock stays version 2, since older readers ignore the key and a bump would make older checkouts reject the lock; `sizes` takes no part in an acceptance's `lock` digest.
- **Every tracked read goes through the check:** the hash cache, `explain`'s diffs, `accept`'s baseline and receipts, sidecar reads, the Julia include scan, and the edit-detection hook. A test fails if any of them opens a simulated online-only file.
- **The download gate.** Before scheduling, a build whose running steps read a file not on disk (online-only, even when cached, or absent with no producer) runs nothing and lists the files with their sizes. It names `--only` as the way to build the rest and points to [online-only-files.md](../../../skills/reproducibility/references/online-only-files.md). The same check runs at each step's start, because a step can turn stale after its producers run. One formatter, `unread_file_lines`, writes the gate, the step-start refusal, `accept`'s refusal, and the `status` file list.
- **Acceptance.** `accept` refuses a file it cannot hash here, naming it. A valid acceptance whose files are online-only here reads `unverified`, not invalid.
- **Checked read-only on OlinStudio** against a legacy Dropbox placeholder and the 5,123,878-byte `SF_DATALESS` Box file `ois_historical_data_extended.xlsx`. Both read `unknown`, their steps `unverified`; `build` and `build --force` ran neither, the gate stopped a build that needed the Box file, and `accept --dry-run` refused it. Afterwards neither file had materialized.

### Known limits

- Batch acceptance is atomic per step, not per call: an I/O failure partway can leave the earlier steps' records written.
- **Size and mtime across download and eviction are unverified.** The hash cache key (path, size, `mtime_ns`) assumes both survive; every online-only check so far was read-only.
- **`OUTPUT_CAP` is a local copy** in `_repro_state.py`. Import it from `_task_validate` once that constant is committed.

Tests: [test_repro_engine.py](../../../skills/task-tree/scripts/test_repro_engine.py), [test_repro_runner.py](../../../skills/task-tree/scripts/test_repro_runner.py), [test_repro_scope.py](../../../skills/task-tree/scripts/test_repro_scope.py), [test_repro_acceptance.py](../../../skills/task-tree/scripts/test_repro_acceptance.py), [test_repro_provenance.py](../../../skills/task-tree/scripts/test_repro_provenance.py), [test_repro_builds.py](../../../skills/task-tree/scripts/test_repro_builds.py), [test_repro_online.py](../../../skills/task-tree/scripts/test_repro_online.py) (file checks that never download), and [test_repro_upstream.py](../../../skills/task-tree/scripts/test_repro_upstream.py) (the producer-chain default, `--only`, `--force`, and the gate).

## Review Notes

Tier: thorough. Focuses: correctness, results-writing (maturation of 11-local-builds into this task).

1. [ADVISORY] [§Selection:69](#L69) says every elided list ends with "the `--json` command". The build preview's count line names `build --dry-run` ([repro_run.py:438](../../../skills/task-tree/scripts/repro_run.py#L438)). Fix: "then a count and the command that lists them".
2. [ADVISORY] The fold dropped the fact that `status --only` still exits 3 when a producer behind the selection is not fresh ([repro_run.py:893](../../../skills/task-tree/scripts/repro_run.py#L893), [:910](../../../skills/task-tree/scripts/repro_run.py#L910)); [§Selection:67](#L67) gives the default's exit codes only. Fix: add the `--only` case to that bullet.
