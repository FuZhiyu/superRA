---
title: "Committed Records Stay Portable Across Machines and Branches"
status: not-started
depends_on:
  - 01-engine-freshness
---

## Objective

A project used from several machines, branches, and worktrees shares its reproduction evidence through git without leaking machine details, without merge conflicts from routine work, and without one machine's in-progress state appearing on another.

Reproduction state comes in two kinds:

- **Committed records** travel through git: `repro-lock.json` ([01](../01-engine-freshness/task.md)) and `repro-acceptance.json`, the reviewed decisions that current results stand without a rerun.
- **Local state** lives in the gitignored `.superra-repro/` folder at the checkout root: run records (`running`, `failed`), check stamps, successful-build receipts, logs, the hash cache, and the lock that stops two builds at once.

Both leak today. The acceptance file carries machine data and conflicts on merge, and `.superra-repro/` syncs through Dropbox, which ignores `.gitignore`.

### The acceptance file holds only portable, mergeable facts

- **No absolute paths.** When a `${VAR}` resolves to an absolute root, each record stores the resolved path under `baseline.spec`, so accepting on Olin (`/Users/juliezfu`) and at home (`/Users/zhiyufu`) rewrites the file. The committed record keeps what reuse needs, the reviewed hashes of inputs, specification, and outputs; the copies of the build specification, run record, and receipt stay local.
- **No user name.** `accept` writes `actor` from `getpass.getuser()` ([_repro_acceptance.py](../../../../skills/task-tree/scripts/_repro_acceptance.py)), against [13-staleness-provenance](../../13-staleness-provenance/task.md)'s rule that no host or user name is committed. Git already records who committed.
- **Small records, written only when something changed.** A record is about 3.5 KB per step, against about 560 B per lock entry, and accepting a task rewrites records for steps that were already fresh. A record keeps only the lock entry's freshness fields, never `built_on`, and records written before the reshape still validate.
- **Branches that accept different steps merge cleanly.** Today they conflict on the single JSON file.
- **A bad record disables only itself.** A conflicted or malformed file makes `status`, `build`, and `accept` all exit with an error, because `read_ledger` rejects the whole file. Set the bad record aside with a warning; its step reports as not accepted.

### Local state stays on its machine

- **One machine's state never reaches another.** This checkout's `.superra-repro/` carries Dropbox's sync attribute and no ignore flag, so it travels to every machine. Three effects follow:
  - **Phantom failures.** A build on one machine writes `running` records; another machine reads them as "previous execution was interrupted; rerun required" and reports those steps `failed` for as long as the build runs. An agent there may start the same costly rerun.
  - **Borrowed evidence.** A check stamp from one machine counts as "ran here" on another, erasing the distinction the "passed in lock; not run here" reason exists to keep.
  - **Conflicted copies.** Every `status` rewrites the hash cache, so two machines working at once produce Dropbox conflicted copies. Freshness stays correct, because size and mtime still guard each cache entry.
- **Worktrees keep separate state.** Each worktree has its own checkout root, and today its own `.superra-repro/`. The new location keeps receipts, stamps, and run records per worktree; the hash cache may be shared per machine, since it is keyed by absolute path.
- **Moving local state stales nothing.** Check stamps keep their lock ids, and existing `.superra-repro/` content is migrated or safely ignored.

### Concurrent builds are visible

- **A second build of the same outputs is refused or warned about.** The build lock is `flock` on a file inside `.superra-repro/`, which covers one machine and one worktree only. Two machines building in the same Dropbox checkout, or two worktrees whose `${OUT}` resolves to one shared output folder, can run the same step at once and write the same files. How far this goes depends on the decision below.

### Validation

- Two clones with different absolute roots and user names produce byte-identical committed records for the same build.
- Two branches accepting different steps merge without conflict, and a hand-corrupted record leaves `status`, `build`, and `accept` working for every other step.
- A `running` record written by another host does not make a step `failed` here.
- Records written before the reshape validate, and moving local state stales no step.

### Researcher decisions

- **Where local state lives.**
  - (a) `~/.cache/superra/<id>/`, keyed per worktree.
  - (b) Keep `.superra-repro/`, tag each record with its host, and ignore other hosts' records.
  - (c) Keep `.superra-repro/` and mark it Dropbox-ignored.
  - Recommendation: (a). It works for projects outside Dropbox too, and (c) depends on a per-machine Dropbox setting.
- **How far concurrent-build protection goes.** This depends on whether two machines ever build the same Dropbox checkout at once.
  - (a) A build lease file beside the committed records, naming host, process, steps, and start time; other machines and worktrees warn or refuse while it is live.
  - (b) Document one builder per checkout at a time and rely on the per-machine lock.
  - Recommendation: (a) if two machines ever build the same checkout; otherwise (b).
- **Which acceptance features stay.** The [0.5 design](../../attachments/v05-design.md#reviewed-acceptance-is-evidence-distinct-from-execution) keeps an exact preview-then-apply token, the `upstream` field (producers accepted in the same decision), evidence-file hashing, and per-node review notes.
  - Recommendation: cut the token apply step, since `accept` already rechecks under its lock and `--dry-run` previews; cut `upstream` and evidence hashing, since the required reason can cite evidence. Keep per-node notes.

Owning tasks: [reviewed-acceptance](../../02-runner/reviewed-acceptance/task.md), [02-build-record](../../13-staleness-provenance/02-build-record/task.md).

## Details

### Evidence (engine review, reproduced on scratch projects before 01)

- **Absolute paths.** With `OUT: {env: OUTROOT}` set to an absolute path, build then accept wrote that path five times per step into `repro-acceptance.json`.
- **User name.** `accept` wrote `"actor": "zhiyufu"`.
- **Merge.** Accepting `clean` on branch A and `estimate` on branch B, then merging, gave `CONFLICT (content): Merge conflict in repro-acceptance.json`, while the lock merged cleanly. While conflicted, `status`, `build`, and `accept` all exited with an error.
- **Duplication.** `baseline.lock` copies the lock entry, `baseline.run` the run record, and `baseline.spec` the receipt; `state.outputs` equals `state.products` when no sidecar is declared; `boundary_inputs` is stored twice.
- **Dropbox sync.** `.superra-repro/` in this checkout has the `com.dropbox.attrs` attribute and no `com.dropbox.ignored` flag. The phantom-failure path is `compute_status` in [_repro_state.py](../../../../skills/task-tree/scripts/_repro_state.py), which turns a `running` record into `failed`; the lock is `mutation_lock` in [_repro_acceptance.py](../../../../skills/task-tree/scripts/_repro_acceptance.py).
- **Worktrees.** This repository has worktrees both outside Dropbox (`/private/tmp/superRA-worktrees/`, `~/.cache/superRA-worktrees/`) and inside it (`superRA.worktrees/`). The ones outside start with no hash cache, receipts, or stamps, so their first `status` rehashes all data and their checks report "not run here".
