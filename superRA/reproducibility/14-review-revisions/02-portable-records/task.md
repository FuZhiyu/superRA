---
title: "Committed Records Stay Portable Across Machines and Branches"
status: approved
depends_on:
  - 01-engine-freshness
---

## Objective

A project used from several machines, branches, and worktrees shares its reproduction evidence through git without leaking machine details, without merge conflicts from routine work, and without one machine's in-progress state appearing on another.

Reproduction state comes in two kinds:

- **Committed records** travel through git: `repro-lock.json` ([01](../01-engine-freshness/task.md)) and `repro-acceptance.json`, the reviewed decisions that current results stand without a rerun.
- **Local state** lives in the gitignored `.superra-repro/` folder at the checkout root: run records (`running`, `failed`), check stamps, successful-build receipts, logs, the hash cache, and the lock that stops two builds at once.

Both leak today. The acceptance file carries machine data and conflicts on merge, and `.superra-repro/` syncs through Dropbox, which ignores `.gitignore`. [01](../01-engine-freshness/task.md) removed the other two leaks the review found, `env_probe` text and `repro-builds.json` churn. It kept the acceptance record's shape ([_repro_acceptance.py:371-418](../../../../skills/task-tree/scripts/_repro_acceptance.py#L371-L418) still copies the receipt's resolved spec and writes `actor`) and left local state in `.superra-repro/`.

**Out of scope:** two builds of the same folder at once, whether from two machines on one Dropbox checkout or from worktrees sharing `${OUT}`.

### The acceptance file holds only portable, mergeable facts

- **No absolute paths.** When a `${VAR}` resolves to an absolute root, each record stores the resolved path under `baseline.spec`, so accepting on Olin (`/Users/juliezfu`) and at home (`/Users/zhiyufu`) rewrites the file. The committed record keeps what reuse needs, the reviewed hashes of inputs, specification, and outputs; the copies of the build specification, run record, and receipt stay local.
- **No user name.** `accept` writes `actor` from `getpass.getuser()` ([_repro_acceptance.py](../../../../skills/task-tree/scripts/_repro_acceptance.py)), against [13-staleness-provenance](../../13-staleness-provenance/task.md)'s rule that no host or user name is committed. Git already records who committed.
- **Small records, written only when something changed.** A record is about 3.5 KB per step, against about 560 B per lock entry, and accepting a task rewrites records for steps that were already fresh. A record keeps only the lock entry's freshness fields, never `built_on`, and records written before the reshape still validate.
- **Branches that accept different steps merge cleanly.** Today they conflict on the single JSON file.
- **A bad record disables only itself.** A conflicted or malformed file makes `status`, `build`, and `accept` all exit with an error, because `read_ledger` rejects the whole file. Set the bad record aside with a warning; its step reports as not accepted.

### Local state stays on its machine

`.superra-repro/` stays at the checkout root, one per worktree. superRA sets Dropbox's ignore attribute on it (`com.dropbox.ignored`) whenever it creates or opens the folder, so each machine keeps its own copy; outside Dropbox the attribute has no effect.

- **One machine's state never reaches another.** This checkout's `.superra-repro/` carries Dropbox's sync attribute and no ignore flag, so it travels to every machine. Three effects follow:
  - **Phantom failures.** A build on one machine writes `running` records; another machine reads them as "previous execution was interrupted; rerun required" and reports those steps `failed` for as long as the build runs. An agent there may start the same costly rerun.
  - **Borrowed evidence.** A check stamp from one machine counts as "ran here" on another, erasing the distinction the "passed in lock; not run here" reason exists to keep.
  - **Conflicted copies.** Every `status` rewrites the hash cache, so two machines working at once produce Dropbox conflicted copies. Freshness stays correct, because size and mtime still guard each cache entry.
- **Ignoring an already-synced folder stales nothing.** Dropbox then removes the folder from the other machines once; losing it there costs at most a rehash, with no step turning stale or failed.

### Validation

- Two clones with different absolute roots and user names produce byte-identical committed records for the same build.
- Two branches accepting different steps merge without conflict, and a hand-corrupted record leaves `status`, `build`, and `accept` working for every other step.
- A `running` record written by another host does not make a step `failed` here.
- Records written before the reshape validate, and deleting a machine's `.superra-repro/` stales no step.

### Acceptance keeps only what reuse needs

The [0.5 design](../../attachments/v05-design.md#reviewed-acceptance-is-evidence-distinct-from-execution) keeps an exact preview-then-apply token, the `upstream` field (producers accepted in the same decision), evidence-file hashing, and per-node review notes. Cut the token apply step, since `accept` already rechecks under its lock and `--dry-run` previews; cut `upstream` and evidence hashing, since the required reason can cite evidence. Keep per-node notes. Update the 0.5 design in the same commit.

Owning tasks: [reviewed-acceptance](../../02-runner/reviewed-acceptance/task.md), [02-build-record](../../13-staleness-provenance/02-build-record/task.md).

## Results

Committed acceptance records are now portable, small, and mergeable, and `.superra-repro/` stays on its machine. Every Validation item holds: each has a regression test that failed before the change, except the remote `running` record, which only a live Dropbox check covers (below). [portable-records-check](#reproduction) is fresh, and after merging 01's fix round and 03 the full task-tree suite passes (1,281 passed, 10 playwright-only skips).

### Acceptance records: one portable file per step

- **Branches that accept different steps merge cleanly.** Records live in `repro-acceptance/<step>.json` instead of one `repro-acceptance.json` ([write_record](../../../../skills/task-tree/scripts/_repro_acceptance.py#L177)). A real `git merge` of two branches accepting `build-a` and `build-x` is clean ([test](../../../../skills/task-tree/scripts/test_repro_acceptance.py#L784)).
  - **Deviation from the Objective's file name.** One JSON file conflicts whenever two branches add neighbouring keys, so the records became a directory. The name `repro-acceptance/` is a proposal.
- **A record keeps only what reuse needs** ([portable_record](../../../../skills/task-tree/scripts/_repro_acceptance.py#L112)): `id`, `basis`, `lock` (SHA-256 of the preceding lock entry's `deps` and `products`, never `built_on`), `state` (`deps`, `products`, and `outputs` only when it differs, as with a sidecar), `boundary_inputs` (logical path, producer, digest), `reason`, `reviews`.
  - Dropped: the `baseline` copies of the spec, run record, receipt, and outputs; `actor`; `recorded_at`; `evidence`; `upstream`. `recorded_at` had to go for byte-identical records; git records who committed and when.
  - Two clones with different absolute `${OUT}` roots and user names write byte-identical `repro-lock.json` and records ([test](../../../../skills/task-tree/scripts/test_repro_acceptance.py#L749)). A `cmd` that embeds a resolved root still changes the spec hash, as 01 designed.
  - Size: 0.9 KB for a fixture step; the real project's 35 records average 2.2 KB (maximum 3.9 KB), against 8.0 KB before. The reason text is now most of each record.
- **Records are written only when something changed.** `accept` skips a selected step only when that step's own `status` reads fresh, by the same rule `status` uses ([preview](../../../../skills/task-tree/scripts/_repro_acceptance.py#L451)), and never rewrites equal content ([test](../../../../skills/task-tree/scripts/test_repro_acceptance.py#L862)). Its output names skipped steps "already fresh".
  - A saved input that `status` reports unverified counts as a change and is recorded: a sidecar producer's output edited without its sidecar, read on a checkout without `.superra-repro/`, is accepted and then reads fresh ([test](../../../../skills/task-tree/scripts/test_repro_acceptance.py#L825)).
- **A bad record disables only itself** ([read_ledger](../../../../skills/task-tree/scripts/_repro_acceptance.py#L143)). A record that does not parse or whose `id` does not match is set aside with a warning naming its step, which then reads as not accepted. After a conflicted merge of the same step accepted on two branches, `status`, `build`, and `accept` work, and re-accepting the step fixes it ([test](../../../../skills/task-tree/scripts/test_repro_acceptance.py#L798)). An unreadable legacy file warns and is ignored.
- **Records written before the reshape validate.** The legacy `repro-acceptance.json` is still read; the first record write converts it into per-step files and deletes it ([_convert_legacy](../../../../skills/task-tree/scripts/_repro_acceptance.py#L162), [test](../../../../skills/task-tree/scripts/test_repro_acceptance.py#L838)). A malformed legacy record is dropped at conversion; it was already ignored.
  - **Real-project check** (ElasticityBound-Local, 111 steps, 35 accepted, read through a scratch copy that symlinks its data): per-step `status` and `local_status` with their reasons are identical under the old code, under the new code reading the legacy file, and after conversion. Converted records hold no absolute path or user name.
- **Acceptance cuts, as specified.** `--apply <token>`, `--evidence`, and `upstream` are gone; `--dry-run` previews; `accept` still rechecks declarations and hashes under its lock before writing ([accept](../../../../skills/task-tree/scripts/_repro_acceptance.py#L467)); `--review` notes stay. The [0.5 design](../../attachments/v05-design.md#reviewed-acceptance-is-evidence-distinct-from-execution) is updated.
  - **Behavior change: revoking a producer leaves a downstream record valid.** The consumer's reviewed saved-input bytes still pin the producer's output, so its local status stays fresh; full-chain status reports it stale while the producer is not fresh.
  - **Batch acceptance is atomic per step, not per call.** An I/O failure partway through can leave the earlier steps' records written.
  - Status JSON `acceptance` drops `evidence`, `recorded_at`, and `actor`; `explain` names the source "reviewed acceptance" without a time; the dashboard no longer lists evidence files.

### Local state stays on its machine

- **`.superra-repro/` carries Dropbox's ignore flag.** [dropbox_ignore](../../../../skills/task-tree/scripts/_repro_state.py#L121) sets `com.dropbox.ignored` (Linux: `user.com.dropbox.ignored`) whenever `repro` opens the folder, and the edit hook sets it when it creates the folder first ([_edit_detect.py:210](../../../../skills/task-tree/scripts/_edit_detect.py#L210)). Tests: [runner](../../../../skills/task-tree/scripts/test_repro_acceptance.py#L906), [hook](../../../../skills/task-tree/scripts/test_edit_detect.py).
  - **Live Dropbox check, on a scratch folder synced between `home-studio` and `julies-homeserver`:** a newly flagged folder never reached the home server, and flagging an already-synced folder removed it there while keeping the local copy. The scratch folder is deleted.
- **A remote `running` record cannot make a step `failed` here, because it never arrives.** The Dropbox flag is the only mechanism. pytest cannot simulate Dropbox sync, so the live check above is this item's only evidence.
- **Deleting `.superra-repro/` stales no step**, with a sidecar step, a check, and an accepted step in the tree ([test](../../../../skills/task-tree/scripts/test_repro_acceptance.py#L875)).

### Open items

- **Other checks over the changed files are not rebuilt here.** `reviewed-baseline-regression-check`, `provenance-explain-check`, `edit-detection-check`, `engine-freshness-check`, and the other steps that list these modules are stale or missing in this worktree; their commands pass in the full-suite run.
- Contributor and agent docs updated: [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md#records), [commands.md](../../../../skills/task-tree/references/commands.md#reviewed-acceptance), [internals.md](../../../../skills/task-tree/references/internals.md), [rerun-or-accept.md](../../../../skills/reproducibility/references/rerun-or-accept.md#accept).

## Details

### Evidence (engine review, reproduced on scratch projects before 01)

- **Absolute paths.** With `OUT: {env: OUTROOT}` set to an absolute path, build then accept wrote that path five times per step into `repro-acceptance.json`.
- **User name.** `accept` wrote `"actor": "zhiyufu"`.
- **Merge.** Accepting `clean` on branch A and `estimate` on branch B, then merging, gave `CONFLICT (content): Merge conflict in repro-acceptance.json`, while the lock merged cleanly. While conflicted, `status`, `build`, and `accept` all exited with an error.
- **Duplication.** `baseline.lock` copies the lock entry, `baseline.run` the run record, and `baseline.spec` the receipt; `state.outputs` equals `state.products` when no sidecar is declared; `boundary_inputs` is stored twice.
- **Dropbox sync.** `.superra-repro/` in this checkout has the `com.dropbox.attrs` attribute and no `com.dropbox.ignored` flag. The phantom-failure path is `compute_status` in [_repro_state.py](../../../../skills/task-tree/scripts/_repro_state.py), which turns a `running` record into `failed`; the lock is `mutation_lock` in [_repro_acceptance.py](../../../../skills/task-tree/scripts/_repro_acceptance.py).
- **Worktrees.** This repository has worktrees both outside Dropbox (`/private/tmp/superRA-worktrees/`, `~/.cache/superRA-worktrees/`) and inside it (`superRA.worktrees/`). The ones outside start with no hash cache, receipts, or stamps, so their first `status` rehashes all data and their checks report "not run here".

## Reproduction

```yaml
steps:
  - name: portable-records-check
    kind: check
    cmd: "uv run --with pytest --with pyyaml python -m pytest skills/task-tree/scripts/test_repro_acceptance.py skills/task-tree/scripts/test_edit_detect.py -q -p no:cacheprovider"
    deps:
      - skills/task-tree/scripts/_apply_patch.py
      - skills/task-tree/scripts/_artifacts.py
      - skills/task-tree/scripts/_checkout_scope.py
      - skills/task-tree/scripts/_comments.py
      - skills/task-tree/scripts/_edit_detect.py
      - skills/task-tree/scripts/_repro.py
      - skills/task-tree/scripts/_repro_acceptance.py
      - skills/task-tree/scripts/_repro_builds.py
      - skills/task-tree/scripts/_repro_provenance.py
      - skills/task-tree/scripts/_repro_scope.py
      - skills/task-tree/scripts/_repro_signals.py
      - skills/task-tree/scripts/_repro_state.py
      - skills/task-tree/scripts/_step_links.py
      - skills/task-tree/scripts/_task_dependencies.py
      - skills/task-tree/scripts/_task_io.py
      - skills/task-tree/scripts/_task_snapshot.py
      - skills/task-tree/scripts/_task_validate.py
      - skills/task-tree/scripts/_worktree_discovery.py
      - skills/task-tree/scripts/cli.py
      - skills/task-tree/scripts/repro_run.py
      - skills/task-tree/scripts/task_hook.py
      - skills/task-tree/scripts/task_read.py
      - skills/task-tree/scripts/conftest.py
      - skills/task-tree/scripts/test_edit_detect.py
      - skills/task-tree/scripts/test_repro_acceptance.py
      - skills/task-tree/scripts/test_repro_provenance.py
      - skills/task-tree/scripts/test_repro_runner.py
```
