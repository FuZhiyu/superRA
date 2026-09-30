---
title: "The `superra repro` Runner: Engine, Records, Acceptance, and Diagnosis"
status: approved
depends_on:
  - 01-section-contract
---

## Objective

Own `superra repro`, which builds the steps of the graph from [01-section-contract](../01-section-contract/task.md), records what each build and review established, and explains why a step is not fresh. Command semantics are documented in [commands.md §Reproduction](../../../skills/task-tree/references/commands.md#reproduction); records in [internals.md §Reproduction records](../../../skills/task-tree/references/internals.md#reproduction-records).

- **Commands:** `build`, `status`, `explain`, `impact`, `accept`, `revoke`, `dag`. `build` and `status` require task or `task#step` targets (`.` for every registered step) and run only that selection against saved inputs; `--upstream` adds the producer chain and `--force` reruns the resulting scope.
- **One freshness rule** for `status` and `build`: SHA-256 content hashes with no size cap, looked up through a size-and-mtime cache, and early cutoff when a rerun regenerates identical bytes. `status`, `explain`, and `impact` run no build and need no engine.
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
- **Build loop.** Steps run as subprocesses in dependency order, `-j N` on threads. A missing input fails the step before its command runs; a failed step skips its descendants. Ctrl-C, SIGTERM, or SIGHUP kills each running step's process group and records it failed; queued steps keep their records and acceptance.
- **Freshness fixes found by the 2026-09-28 design review**, each with a regression test in [test_repro_engine.py](../../../skills/task-tree/scripts/test_repro_engine.py):
  - A directory dep follows symlinks with a cycle guard; a symlinked data folder had read `fresh` after its contents changed.
  - A sidecar-tracked saved input counts as verified when its bytes match the producer's record or the digest its sidecar names; it had forced needless reruns on a fresh clone.
  - A scoped `status` exits 3 and names the non-fresh producers behind a fresh selection, instead of exiting 0.

### Records

- **A step's definition is its own node.** The spec hash records the declared half (`cmd` as written, `params`, logical deps and outs) and the resolved command as `declared:resolved`, so a definition edit invalidates only that step and `explain` can say which half moved.
- **The lock holds one line per step** (version 2), so a git merge takes each entry whole from one side and cannot mix two builds into a false `fresh`. A conflicted lock still reads, dropping the entries the sides disagree on so their steps read `missing`. Entries record `built_on` (OS and architecture) for `explain`; no timestamp, so an identical rebuild leaves the lock byte-identical. Lock entries of archived steps are kept for provenance.
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
- **A check that passed at these inputs elsewhere reads `fresh`**, with the lock revision and platform in its reason; a local failure still wins.
- **`impact <path>`** lists affected steps with their last durations, including every step a `superRA/config.yaml` change reaches through runner templates, variables, or `env_deps`. `build --dry-run` prices a rebuild the same way, as an upper bound. `status` counts the outside readers of each step's outs as a fact, never a task-local verdict.

### Selection and upgrade

- **Task targets replaced reproduction tiers.** A bare `build` or `status` fails naming the `.` target; `--tier` and `repro tier` exit 2 naming task targets; a leftover `tier:` key warns. Scope and force compose: `--force` reruns exactly the selection, `--upstream --force` the producer chain, which fixed the [TreasuryGIV pilot's](../08-pilot-treasurygiv/task.md) unintended 40-minute upstream rebuild.
- **Concurrent work does not abort a build.** Guards cover the selected declarations, resolved paths, artifact ownership, and input bytes; unrelated task creation, status changes, prose, and unused config edits pass ([internals.md §Build guards](../../../skills/task-tree/references/internals.md#build-guards)).
- **A pre-release project upgrades without rebuilding:** `pytask.lock`, `repro-builds.json`, and `repro-acceptance.json` are read until the first build or accept rewrites them. [RELEASE-NOTES.md](../../../RELEASE-NOTES.md) gives the order coauthors follow.

### Known limit

- Batch acceptance is atomic per step, not per call: an I/O failure partway can leave the earlier steps' records written.

Tests: [test_repro_engine.py](../../../skills/task-tree/scripts/test_repro_engine.py), [test_repro_runner.py](../../../skills/task-tree/scripts/test_repro_runner.py), [test_repro_scope.py](../../../skills/task-tree/scripts/test_repro_scope.py), [test_repro_acceptance.py](../../../skills/task-tree/scripts/test_repro_acceptance.py), [test_repro_provenance.py](../../../skills/task-tree/scripts/test_repro_provenance.py), and [test_repro_builds.py](../../../skills/task-tree/scripts/test_repro_builds.py).
