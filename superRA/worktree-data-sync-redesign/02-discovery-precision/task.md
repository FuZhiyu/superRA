---
title: "Discovery Precision: Built-in Denylist and Tracked-Symlink Exclusion"
status: not-started
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

## Planner Guidance

Regression fixture idea: this very repo's observed over-collection — `.DS_Store`, `.claude`, and the tracked `AGENT.md`/`AGENTS.md` aliases all came back as managed entries. `fnmatch` against the basename covers the `*.egg-info` glob; keep the constant a tuple/frozenset so callers can reference it in the SKILL.md doc task.

## Results
