---
title: "Build the `superra repro` Runner on pytask"
status: implemented
depends_on: [01-section-contract]
---

## Objective

Ship `superra repro`, the command that rebuilds stale steps of the graph from [01-section-contract](../01-section-contract/task.md) and reports why.

- **Commands:** `build [targets] [--tier canon|local|all] [-j N] [--force] [--dry-run]`, `status [--json] [--tier]`, `explain <step>`, `dag [--mermaid]`, `tier <task-path> canon|local`. A target is a step name or a task path (all its steps); building a target includes its ancestors. Default tier for `build` and `status` is `canon`.
- **Engine bridge:** generate one pytask task per step in memory and run `pytask.build(tasks=…)`; never write `task_*.py` into the project. Each step depends on a hashed `PythonNode` of its resolved spec (cmd, params, resolved deps and outs) so editing one step invalidates only that step. File and directory nodes are runner-owned `PNode` classes whose id is the logical (variable-form) path and whose hashing uses the resolved path, so the lock never embeds an author or branch. The pytask root is the project root; `pytask.lock` is committed there; the per-machine hash cache, per-step logs, and check-step stamps live in one gitignored directory that `repro` creates and adds to `.gitignore` on first run.
- **Hash cache:** file state is the content hash, looked up in a persistent cache keyed on size and mtime_ns (no inode). A cache hit costs one `stat`; a miss rehashes. Sidecar-tracked outs hash the sidecar.
- **Execution:** each step runs from the project root with the resolved `cmd`, stdout and stderr to `<logs>/<step>.log`, duration recorded; `-j` uses `pytask-parallel`. `check` steps rerun when their deps change and record a stamp on success. A failing step stops its descendants, reports the log path, and exits non-zero.
- **Status and explain:** per step, one of `fresh` / `stale` / `missing` / `failed` / `external` with the triggering reason (which dep or out changed, or "never built"), owner task, tier, last duration. `--json` is the contract the dashboard and `task read` consume.
- **Entry script:** a PEP 723 script under `skills/task-tree/scripts/` pinning `pytask>=0.6,<0.7`, `pytask-parallel`, and `pyyaml`; `cli.py` dispatches `repro` to it so the `./superRA/superra` wrapper needs no change. Every other `superra` command keeps working without pytask installed.
- **Validation criteria:** pytest suite (pytask available via `uv run --with`) on a fixture tree with shell-script steps: first build runs all; second is a no-op; `touch` with identical bytes is a no-op; a dep edit reruns exactly the affected chain; a step edit that regenerates identical bytes does not cascade; deleting an out reports `missing` and rebuilds it; `-k`-style target selection pulls stale ancestors; `--json` matches the documented shape; the cache file is used (second `status` performs no full-file reads, asserted through a counter or a large fixture timing).

## Details

- pytask facts checked in the installed 0.6.0 source: the lock path is `config["root"] / "pytask.lock"`; portable ids are `os.path.relpath` from that root; symlinks are not resolved on non-Windows; `pytask lock accept|reset|clean` exists and covers a later seed-from-canonical adoption without new code. Task state is the hash of the task module file, so all generated tasks share it; the per-step `PythonNode` supplies the missing granularity.
- Custom node: implement a `PNode`-compatible class whose `state()` consults the cache; pytask hashes `PathNode` content on every invocation otherwise. Keep the cache format simple (JSON, path → size, mtime_ns, sha256).
- Check steps need a product for pytask to skip them when unchanged; a stamp file in the state directory is the intended product.
- Machine-specific files are excluded from env deps by the contract; the runner adds nothing on its own.
- Survey evidence for the design: pytask handled the Julia subprocess pattern, `--dry-run --explain` named the changed helper file, and `DirectoryNode` hashed files inside directories in the 2026-09-02 tool survey.

## Results

`superra repro` ships with five subcommands — `build`, `status`, `explain`, `dag`, `tier` — over the graph [01-section-contract](../01-section-contract/task.md) built. Only `build` needs pytask.

### What later tasks call

- **[repro_run.py](../../../skills/task-tree/scripts/repro_run.py)** — the PEP 723 entry pinning `pytask>=0.6,<0.7`, `pytask-parallel`, and `pyyaml`. [cli.py](../../../skills/task-tree/scripts/cli.py) hands it every `repro` argument before argparse runs, so the flag surface has one owner and the `./superRA/superra` wrapper needed no change. When the running interpreter is short of what a subcommand needs, `main` re-execs the script under `uv run --script`, which provisions that block; `SUPERRA_REPRO_REEXEC` stops a loop.
- **[_repro_state.py](../../../skills/task-tree/scripts/_repro_state.py)** — stdlib runner state. `compute_status(graph, paths, tier=…)` returns a `StatusReport` whose `to_dict()` is the `--json` contract [03-task-interface](../03-task-interface/task.md) and [04-dashboard-view](../04-dashboard-view/task.md) consume; `select_steps`, `render_dag`, `set_tier`, and `HashCache` are separately callable.

`status`, `explain`, `dag`, and `tier` never import pytask, so the task CLI and the dashboard can show reproduction state on a machine that has never built.

### The three decisions the engine bridge turned on

- **Nodes are runner-owned and deliberately not `PPathNode`.** pytask derives a path node's lock id from its resolved path (`_pytask/lockfile.py`, `build_portable_node_id`), which would embed whatever `${OUT}` expanded to. `FileNode` keeps the logical path in `name` — the id pytask falls back to for a plain `PNode` — and hashes `resolved`, so the committed lock reads the same on every checkout. pytask creates a product's parent directory only for a `PPathNode`, so the step function does it instead.
- **The task state is the constant `"1"`.** `TaskWithoutPath` hashes its function's source, and every generated step shares one function: that hash gives no granularity and would invalidate a whole project's graph on any runner-source edit. `SpecNode` supplies the granularity — the declared half (`cmd` as written, `params`, the logical dep and out lists) and the resolved command, hashed separately and recorded as one `declared:resolved` state — so a step-definition edit invalidates that step alone, a `${VAR}` that reaches only `cmd` still moves the step's state, and `status` can say which of the two moved. Node *ids* stay logical throughout; states have always tracked what the invocation resolved to.
- **Status recomputes freshness from the committed lock, not from pytask.** pytask itself skips from the lock whenever one exists (`_pytask/state.py`, `has_node_changed`), so reading the same record applies the same rule without the engine — the reason `status --json` costs no pytask install. `pytask.build(tasks=…, paths=[])` with the cwd at the project root roots pytask there while collecting nothing from disk; the runner warns if pytask still roots elsewhere.

### Behavior worth knowing

- **Step states.** `fresh`, `stale`, `missing` (never built, or an out is gone), `failed`, and `external` — a dep no step produces is not on disk, so the step cannot run. A fresh step downstream of a non-fresh one becomes `stale` with an upstream reason. `failed` applies only while the step still has work to do: once its inputs are restored and disk matches the lock again, `status` reports `fresh`, which is what `build` does too. A `failed` step's `reason` leads with whatever moved since that run and ends at the log, so an edit made after the failure is still the trigger a rerun answers to. `status` exits 1 unless every reported step is fresh, which is what the IMPLEMENT gate in [07-workflow-integration](../07-workflow-integration/task.md) can read.
- **The state directory is `.superra-repro/`** at the project root — hash cache, per-step logs, per-step run records, check stamps — created and appended to `.gitignore` on the first command against a tree that declares steps, so a project with no graph stays untouched. One run record per step rather than one shared file keeps `-j` runs race-free.
- **`-j N` runs the threads backend.** Steps are subprocesses, so the GIL is free while they run and no closure or cache has to survive pickling.
- **A sidecar is hashed wherever its out appears** — as the producer's product and as any consumer's dep — so both sides agree on one state for one lock id and the large file is never read. It stands in for hashing, never for existence: a `Node` triple carries the out's own path, so a deleted out reports `missing` and rebuilds on one extra `stat`. The runner writes the sidecar after a successful run unless the step rewrote it during that run.
- **A dep below a directory out gets that directory as a node.** The graph infers the edge by prefix, but per-path nodes alone would leave the engine free to run the consumer first, so `make_tasks` adds the covering directory to the consumer's deps.
- **`--dry-run` turns on pytask's `--explain`**, so it names what changed rather than only listing what would run.
- **`--tier` (default `canon`) picks the default build and scopes `status`; an explicit target overrides it**, and any selection pulls the ancestors it needs whatever tier they carry — pytask itself skips the fresh ones.
- **`--force` applies to the whole selection, ancestors included.** pytask takes it as a session flag, so `repro build <step> --force` reruns every ancestor pulled in with the target even when all of them are fresh — in [08-pilot-treasurygiv](../08-pilot-treasurygiv/task.md) forcing one figure step reran five upstream estimation steps and cost a 40-minute rebuild. Scoping the flag to the named targets needs per-task invalidation rather than the session flag, and is not implemented.

### Validation

52 tests in [test_repro_runner.py](../../../skills/task-tree/scripts/test_repro_runner.py) — 22 stdlib, 30 gated on pytask. The suite is 997 with pytask; on the pytask-free baseline command it is 967 passed and 30 skipped.

Coverage follows the objective's list, plus: an out deleted by hand, a `params` edit invalidating one step, a failing step's log and its blocked descendants, `--force`, `--dry-run` writing nothing, `-j 2`, a sidecar-tracked out staying fresh after the out is hand-edited, tier-scoped reporting, `tier` inserting the key when absent, a tree with no steps leaving no state behind, and `cli.py` routing. The review round added red-green cover for each of its findings: a directory out ordering its consumer at `-j 1` and `-j 2` (plus two deterministic structural tests), a deleted sidecar-tracked out, a `${VAR}` that reaches only `cmd`, a restored input clearing a `failed` step, a failure message carrying no Python frames, and the re-exec message naming what is missing. Each of the six fails with its fix reverted. The advisory round added two more: a dep edited after a cleared failure naming that dep rather than only the log, and a declaration edit still reading as a declaration edit once the spec state is split in two — the first reddens with its fix reverted, the second guards the split against misclassifying.

Command surface in [commands.md](../../../skills/task-tree/references/commands.md) §Reproduction, scripts in [internals.md](../../../skills/task-tree/references/internals.md) §Script Inventory, and a routing row in [SKILL.md](../../../skills/task-tree/SKILL.md).

## Review Notes

Quick pass; focuses: correctness. Covered: the one bullet this range added and the `--force` wiring behind it. Not covered: the rest of the runner, approved earlier and unchanged.

1. **[ADVISORY]** [task.md:11](task.md#L11) and [task.md:52](task.md#L52) both say a selection pulls its *stale* ancestors. [select_steps](../../../skills/task-tree/scripts/_repro_state.py#L749-L759) walks the full upstream closure and pytask skips the fresh ones, which is exactly why the new `--force` bullet reads as a surprise. Drop "stale" from both.
   → implemented: dropped "stale" at [task.md:11](task.md#L11) and [task.md:52](task.md#L52); the latter now says pytask skips the fresh ancestors, which is what makes the `--force` bullet a surprise.
