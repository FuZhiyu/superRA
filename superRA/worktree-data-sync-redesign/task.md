---
title: "Worktree Data Sync Redesign: Fast Seeding, Precise Discovery, Loud Failures"
status: approved
depends_on: []
---

## Objective

Redesign the `worktree-data-sync` skill's seed path and managed-path discovery so that seeding a fresh worktree is fast (no per-file subprocess spawning), discovery stops collecting non-data junk (venvs, caches, harness-local state), failures are reported per-path with a nonzero exit, and the `--from` default matches how the tool is actually invoked. Scope: `skills/worktree-data-sync/` (both scripts, tests, SKILL.md) plus the two agent-orchestration references that document the old `--from` trap.

### Context

Design settled with the researcher in-session (2026-07-08); the decisions below are binding, not open questions:

- **Measured baseline:** per-file `cp -c` subprocess costs ~8ms/file — 2,000 files take 15.5s as a per-file loop vs 0.3s as one `cp -cR` (50×). Slow seeds are also the likely cause of observed "errors": harness Bash calls time out at 120s and kill the seed mid-run.
- **Verified `cp` semantics (macOS):** `cp -c` preserves mtime; with `-R`, BSD cp defaults to `-P` — nested symlinks (relative, absolute, looping) are recreated verbatim and never followed, identical to the current Python walk's behavior.
- **Keep zero-config inference.** Discovery stays stateless and gitignore-driven; precision comes from a built-in denylist, not a per-project allowlist/manifest.
- **Copy stays the default; symlink stays annotation-declared.** CoW clones are cheap and give the agent an isolated snapshot. Directory symlinks share a live writable namespace (new writes land in the source worktree, parallel agents collide, harvest/diff inverts), so the tool never auto-creates a directory symlink — that semantic is opt-in via `# data-sync:symlink` only.
- **Dataless (cloud-placeholder) handling:** a folder full of dataless files is still materialized as a real directory with per-file symlinks — mkdir + recurse, never an automatic dir-symlink. A *mostly*-dataless root seeds per-file and prints a suggestion to annotate it `# data-sync:symlink`; suggest, never auto-switch.
- **Never-overwrite is vacuous on a fresh destination.** The merge semantics ("copy only missing") only need per-file checks when the destination root already exists; the absent-destination case takes the wholesale-clone fast path.

### Constraints

- The two scripts stay stdlib-only and runnable as plain `python3` — they execute inside arbitrary target projects and must never trigger uv/venv provisioning (no PEP 723 blocks).
- macOS-specific facilities (`cp -c`/clonefile, `SF_DATALESS` via `st_flags`) stay behind graceful fallbacks so the scripts still work on non-APFS filesystems and Linux (`cp -cR` failure → `shutil` fallback; missing `st_flags` → not dataless).
- Tests simulate dataless files by monkeypatching the dataless check — never rely on real cloud-placeholder files. Run the suite with `uv run --with pytest python -m pytest skills/worktree-data-sync/scripts/test_worktree_data_sync.py` (dev convenience only; the scripts themselves stay uv-free).
- None of the files this subtree touches are generated artifacts — do not run `sync_codex_agents.py`. Prose edits to `SKILL.md` and the agent-orchestration references must pass the root `CLAUDE.md` teach-the-protocol gate (DRY + necessity, line by line).

## Details

`01-seed-fast-path` and `02-discovery-precision` touch different scripts but share `test_worktree_data_sync.py`; dispatch them serially in this worktree (or give each its own worktree) to avoid colliding edits to the shared test file.

## Results

Seeding a fresh worktree is now one clone per clean root instead of one subprocess per file, discovery returns only genuine data roots, and every failure is named and exits nonzero. The behavior is documented in [worktree-data-sync/SKILL.md](../../skills/worktree-data-sync/SKILL.md); 43 tests cover it in [test_worktree_data_sync.py](../../skills/worktree-data-sync/scripts/test_worktree_data_sync.py).

- **Seed routes each managed root by a stat-only preflight** ([01-seed-fast-path](01-seed-fast-path/task.md)). A clean fresh root is one `cp -c -R -p` — the measured 0.3s against 15.5s for the old per-file loop on 2,000 files. Directories holding cloud placeholders are rebuilt with per-file symlinks and batched copies; a mostly-placeholder root seeds per file and suggests annotating it `# data-sync:symlink` rather than switching behavior. Never-overwrite holds in every path, and off APFS the clone falls back to `shutil.copytree` before recording a failure.
- **Failures are loud.** Each failed path is recorded with its reason, listed on stderr, and exits 1 — replacing a swallowed `errors=N` counter that exited 0.
- **Discovery stops collecting junk** ([02-discovery-precision](02-discovery-precision/task.md)). A built-in denylist filters discovered entries by basename — venvs, caches, build directories, harness-local state — while an explicit `# data-sync:symlink` annotation always overrides it, and root *contents* are never filtered. The top-level symlink safety net skips symlinks git already tracks, so a repo-internal alias like `AGENTS.md` → `CLAUDE.md` is no longer double-collected.
- **`--from` defaults to the caller's own worktree** ([03-defaults-and-docs](03-defaults-and-docs/task.md)), not the repository's main worktree, and errors clearly when cwd sits outside every worktree. The "always pass `--from`" warning is deleted from [parallel-dispatch.md](../../skills/agent-orchestration/references/parallel-dispatch.md) and the `--from "$(pwd)"` workaround from [worktree-harness-fallback.md](../../skills/agent-orchestration/references/worktree-harness-fallback.md).

Both scripts stay stdlib-only and PEP 723-free so they never provision a venv inside a target project.
