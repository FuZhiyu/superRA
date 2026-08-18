---
title: "Discovery Precision: Built-in Denylist and Tracked-Symlink Exclusion"
status: approved
depends_on: []
---

## Objective

Stop managed-path discovery (`skills/worktree-data-sync/scripts/worktree_data_discovery.py`) from collecting gitignored paths that are not research data, and stop the top-level symlink safety net from collecting symlinks git already tracks. Success: on a repo with a venv, caches, and tracked alias symlinks, `discover_managed_entries` returns only genuine data roots.

**Built-in denylist.** A module-level constant of well-known non-data names; a discovered gitignored entry whose path basename matches (exact name or glob) is excluded from managed entries. Initial list:

`.venv`, `venv`, `.direnv`, `node_modules`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.tox`, `.nox`, `.cache`, `.ipynb_checkpoints`, `.quarto`, `dist`, `build`, `*.egg-info`, `.DS_Store`, `.env`, `.envrc`, `.worktrees`, `.claude`, `.codex`

Scope rules:

- The denylist filters *discovered entries* only; contents of a managed data root are copied verbatim (no exclusion inside a root — `cp -cR` cannot exclude, and a data root's contents are the user's business).
- An explicit `.gitignore` annotation (`# data-sync:symlink`, legacy `# worktree:symlink`) wins over the denylist — a deliberately annotated root is always managed. Copying a venv is also a *correctness* bug, not just waste (`pyvenv.cfg` and script shebangs pin absolute paths), which is why the venv names lead the list.

**Tracked-symlink exclusion.** The top-level symlink safety net (the `iterdir` pass) skips symlinks that are tracked in git: tracked repo-internal symlinks (e.g. `AGENT.md` → `CLAUDE.md`) are checked out by git in the destination already, and tracked external symlinks are handled by the dedicated tracked-symlink pass.

**Validation (extend `test_worktree_data_sync.py`):**

- Gitignored `.venv/`, `__pycache__/`, `.DS_Store` are absent from discovered entries; a gitignored data directory alongside them is still discovered.
- A denylisted-name root carrying a `# data-sync:symlink` annotation is discovered as symlink-only.
- A tracked repo-internal symlink is not collected; an untracked top-level symlink to an external directory still is.

## Details

Regression fixture idea: this very repo's observed over-collection — `.DS_Store`, `.claude`, and the tracked `AGENT.md`/`AGENTS.md` aliases all came back as managed entries. `fnmatch` against the basename covers the `*.egg-info` glob; keep the constant a tuple/frozenset so callers can reference it in the SKILL.md doc task.

## Results

Discovery returns only genuine data roots. Both changes live in [worktree_data_discovery.py](../../../skills/worktree-data-sync/scripts/worktree_data_discovery.py).

**`DEFAULT_DENYLIST` filters discovered entries by basename**, matched with `fnmatch` so `*.egg-info` works, and covers exactly the list the objective names. A skipped directory root is still recorded in `ignored_dir_roots`, so nested candidates under it cannot leak through separately. An explicit `# data-sync:symlink` root is exempt, and the pre-existing final loop over `shared_roots` adds annotated roots unconditionally — which is what makes a denylisted-name root with an annotation come back `symlink_only`, with no special case anywhere.

**The top-level symlink safety net skips symlinks git already tracks.** `_tracked_external_symlink_paths` returned all tracked symlinks despite its name (the external filter lived at its one call site), so it is renamed `_tracked_symlink_paths` and computed once. A tracked repo-internal alias such as `AGENTS.md` → `CLAUDE.md` is no longer re-collected by the safety net after the dedicated tracked-symlink pass has already excluded it.

**`TestDiscoveryPrecision`** adds three tests: denylisted `.venv`, `__pycache__`, and `.DS_Store` excluded while a sibling gitignored `data/` survives; an annotated `.cache/` root returning `symlink_only: True`; a tracked `AGENTS.md` symlink excluded while an untracked top-level symlink to an external directory is still discovered. 43 tests pass overall.

**One pre-existing test moved off a denylisted name.** `TestNestedWorktreeSelfReference` used a gitignored directory literally named `.worktrees` to exercise the destination-containment guard, including a case asserting it is *kept* when no `dest_worktree` is passed — no longer true once `.worktrees` is denylisted. Its fixture directory is renamed `nested-worktrees` so it keeps testing the self-reference guard in isolation.
