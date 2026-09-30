---
title: "Build the `superra repro` Runner"
status: approved
depends_on:
  - 01-section-contract
---

## Objective

Ship `superra repro`, the command that rebuilds stale steps of the graph from [01-section-contract](../01-section-contract/task.md) and reports why.

- **Commands:** preserve build/status/explain/dag and the [scoped verification contract](../11-scoped-verification/task.md). Build/status require task or `task#step` targets (`.` for every registered step) and run only that selection against saved inputs; `--upstream` adds producers and `--force` reruns the resulting scope. The 0.5 child adds impact/accept/revoke.
- **Engine bridge:** generate one pytask task per step in memory and run `pytask.build(tasks=…)`; never write `task_*.py` into the project. Each step depends on a hashed `PythonNode` of its resolved spec (cmd, params, resolved deps and outs) so editing one step invalidates only that step. File and directory nodes are runner-owned `PNode` classes whose id is the logical (variable-form) path and whose hashing uses the resolved path, so the lock never embeds an author or branch. The pytask root is the project root; `pytask.lock` is committed there; the per-machine hash cache, per-step logs, and check-step stamps live in one gitignored directory that `repro` creates and adds to `.gitignore` on first run.
- **Hash cache:** file state is the content hash, looked up in a persistent cache keyed on size and mtime_ns (no inode). A cache hit costs one `stat`; a miss rehashes. Sidecar-tracked outs hash the sidecar.
- **Execution:** each step runs from the project root with the resolved `cmd`, stdout and stderr to `<logs>/<step>.log`, duration recorded; `-j` uses `pytask-parallel`. `check` steps rerun when their deps change and record a stamp on success. A failing step stops its descendants, reports the log path, and exits non-zero.
- **Status and explain:** per step, one of `fresh` / `stale` / `missing` / `failed` / `external` with the triggering reason (which dep or out changed, or "never built"), owner task, last duration. `--json` is the contract the dashboard and `task read` consume.
- **Entry script:** a PEP 723 script under `skills/task-tree/scripts/` pinning `pytask>=0.6,<0.7`, `pytask-parallel`, and `pyyaml`; `cli.py` dispatches `repro` to it so the `./superRA/superra` wrapper needs no change. Every other `superra` command keeps working without pytask installed.
- **Validation criteria:** pytest suite (pytask available via `uv run --with`) on a fixture tree with shell-script steps: first build runs all; second is a no-op; `touch` with identical bytes is a no-op; a dep edit reruns exactly the affected chain; a step edit that regenerates identical bytes does not cascade; deleting an out reports `missing` and rebuilds it; `-k`-style target selection pulls stale ancestors; `--json` matches the documented shape; the cache file is used (second `status` performs no full-file reads, asserted through a counter or a large fixture timing).

- **0.5 reuse:** implement [impact and reviewed acceptance](reviewed-acceptance/task.md) while preserving successful-run evidence and the existing status vocabulary.

## Details

- pytask facts checked in the installed 0.6.0 source: the lock path is `config["root"] / "pytask.lock"`; portable ids are `os.path.relpath` from that root; symlinks are not resolved on non-Windows; `pytask lock accept|reset|clean` exists and covers a later seed-from-canonical adoption without new code. Task state is the hash of the task module file, so all generated tasks share it; the per-step `PythonNode` supplies the missing granularity.
- Custom node: implement a `PNode`-compatible class whose `state()` consults the cache; pytask hashes `PathNode` content on every invocation otherwise. Keep the cache format simple (JSON, path → size, mtime_ns, sha256).
- Check steps need a product for pytask to skip them when unchanged; a stamp file in the state directory is the intended product.
- Machine-specific files are excluded from env deps by the contract; the runner adds nothing on its own.
- Survey evidence for the design: pytask handled the Julia subprocess pattern, `--dry-run --explain` named the changed helper file, and `DirectoryNode` hashed files inside directories in the 2026-09-02 tool survey.

## Results

`superra repro` ships with seven subcommands — `build`, `status`, `explain`, `impact`, `accept`, `revoke`, `dag` — over the graph [01-section-contract](../01-section-contract/task.md) builds. This task first built the runner on pytask 0.6; [01-engine-freshness](../14-review-revisions/01-engine-freshness/task.md) replaced pytask with superRA's own build loop and `pytask.lock` with `repro-lock.json`, so the Objective's engine-bridge and pinning items no longer describe the code.

### What later tasks call

- **[repro_run.py](../../../skills/task-tree/scripts/repro_run.py)** — the PEP 723 entry, pinning only `pyyaml`. [cli.py](../../../skills/task-tree/scripts/cli.py) hands it every `repro` argument before argparse runs, so the flag surface has one owner and the `./superRA/superra` wrapper needed no change. Every subcommand runs on Python 3.10 except a read of a legacy `pytask.lock`, which needs `tomllib`: `main` then re-execs the script under `uv run --script`, and `SUPERRA_REPRO_REEXEC` stops a loop.
- **[_repro_state.py](../../../skills/task-tree/scripts/_repro_state.py)** — stdlib runner state. `compute_status(graph, paths, …)` returns a `StatusReport` whose `to_dict()` is the `--json` contract [03-task-interface](../03-task-interface/task.md) and [04-dashboard-view](../04-dashboard-view/task.md) consume; `select_steps`, `render_dag`, and `HashCache` are separately callable.

### Decisions that outlived the engine switch

- **Lock ids are logical paths.** Each node is keyed by its variable-form path and hashed at the resolved path, so the committed lock reads the same on every checkout.
- **A step's definition is its own node.** `spec_hashes` hashes the declared half (`cmd` as written, `params`, the logical dep and out lists) and the resolved command separately, recorded as one `declared:resolved` state: a step-definition edit invalidates that step alone, a `${VAR}` that reaches only `cmd` still moves the step, and `status` can say which half moved.
- **`status` and `build` share one freshness rule.** `status` reads the committed lock without running anything, so the task CLI and the dashboard show reproduction state on a machine that has never built.

### Behavior worth knowing

- **Step states.** `fresh`, `stale`, `missing` (never built, or an out is gone), `failed`, and `external` — a dep no step produces is not on disk, so the step cannot run. A fresh step downstream of a non-fresh one becomes `stale` with an upstream reason. Restoring inputs can clear an ordinary failure when disk matches the lock again; a forced failure requires a successful retry. A `failed` step's `reason` leads with whatever moved since that run and ends at the log.
- **The state directory is `.superra-repro/`** at the project root — hash cache, per-step logs, per-step run records, check stamps — created and appended to `.gitignore` on the first command against a tree that declares steps, and flagged for Dropbox to ignore ([02-portable-records](../14-review-revisions/02-portable-records/task.md)). One run record per step keeps `-j` runs race-free.
- **`-j N` runs steps on threads.** Steps are subprocesses, so the GIL is free while they run.
- **A sidecar is hashed wherever its out appears** — as the producer's product and as any consumer's dep — so both sides agree on one state and the large file is never read. It stands in for hashing, never for existence: a deleted out reports `missing`. The runner writes the sidecar after a successful run unless the step rewrote it during that run.
- **A dep below a directory out waits for that directory's producer.** The graph infers the edge by prefix, and the scheduler orders the consumer after it.
- **`--dry-run` lists each step it would execute with its last recorded duration**; `explain` names what changed.
- **Forced rerun scope is explicit.** [11-scoped-verification](../11-scoped-verification/task.md) limits `--force` to the selected scope; `--upstream --force` reruns the producer chain. This addresses the [pilot's](../08-pilot-treasurygiv/task.md) unintended 40-minute upstream rebuild.

### Validation

[test_repro_runner.py](../../../skills/task-tree/scripts/test_repro_runner.py) covers the objective's list — first build runs all, a second is a no-op, identical-byte `touch` and regenerated identical outputs do not cascade, a dep edit reruns exactly the affected chain, a deleted out rebuilds, target selection, the `--json` shape, and cache use — plus the review rounds' red-green cases. The engine itself is covered in [test_repro_engine.py](../../../skills/task-tree/scripts/test_repro_engine.py). Neither needs pytask.

Command surface in [commands.md](../../../skills/task-tree/references/commands.md#reproduction), scripts in [internals.md](../../../skills/task-tree/references/internals.md) §Script Inventory, and a routing row in [SKILL.md](../../../skills/task-tree/SKILL.md).
