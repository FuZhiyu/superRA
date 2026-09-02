---
title: "Build the `superra repro` Runner on pytask"
status: not-started
depends_on: [01-section-contract]
---

## Objective

Ship `superra repro`, the command that rebuilds stale steps of the graph from [01-section-contract](../01-section-contract/task.md) and reports why.

- **Commands:** `build [targets] [--tier canon|local|all] [-j N] [--force] [--dry-run]`, `status [--json] [--tier]`, `explain <step>`, `dag [--mermaid]`, `tier <task-path> canon|local`. A target is a step name or a task path (all its steps); building a target includes its stale ancestors. Default tier for `build` and `status` is `canon`.
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
