---
title: "Discovery Precision: Built-in Denylist and Tracked-Symlink Exclusion"
status: implemented
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

Added a module-level `DEFAULT_DENYLIST` tuple and `is_denylisted()` helper (`fnmatch`-based) to [worktree_data_discovery.py:10-41](../../../skills/worktree-data-sync/scripts/worktree_data_discovery.py#L10-L41), covering exactly the initial list from the objective. The ignored-candidates loop in `discover_managed_entries` now skips any gitignored entry whose basename matches the denylist *unless* that same path is an explicit `# data-sync:symlink` annotation root ([worktree_data_discovery.py:276-279](../../../skills/worktree-data-sync/scripts/worktree_data_discovery.py#L276-L279)); a skipped directory root is still recorded in `ignored_dir_roots` so nested candidates under it don't leak through separately. Annotated roots are added unconditionally by the pre-existing final loop over `shared_roots`, which is what gives the "denylisted-name root with annotation is symlink-only" behavior — no special-casing needed there.

For tracked-symlink exclusion, `_tracked_external_symlink_paths` (which actually returns *all* tracked symlinks, not just external ones — the external filter was applied at its one call site) is renamed to `_tracked_symlink_paths` and its result is now computed once and reused: the top-level `iterdir` safety net ([worktree_data_discovery.py:312-320](../../../skills/worktree-data-sync/scripts/worktree_data_discovery.py#L312-L320)) skips any symlink whose name is in that tracked set, so a tracked repo-internal symlink (e.g. `AGENTS.md` -> `CLAUDE.md`) is no longer double-collected via the safety net after already being (correctly) excluded from the dedicated tracked-external-symlink pass.

Extended `test_worktree_data_sync.py` with `TestDiscoveryPrecision` (3 tests): denylisted `.venv`/`__pycache__`/`.DS_Store` excluded while a sibling gitignored `data/` is kept; a `.cache/` root carrying the `data-sync:symlink` annotation comes back `symlink_only: True`; a tracked `AGENTS.md` -> `CLAUDE.md` symlink is excluded while an untracked top-level symlink to an external directory (`notes`) is still discovered.

**Conflict with a pre-existing test, resolved:** `.worktrees` is on the objective's own denylist, but `TestNestedWorktreeSelfReference` (predates this subtree) used a gitignored directory literally named `.worktrees` to test the *destination-containment* self-reference guard, including a `test_no_dest_preserves_legacy_behavior` case asserting `.worktrees` is *kept* when no `dest_worktree` is passed. That assertion is no longer true now that `.worktrees` is unconditionally denylisted. Renamed the fixture's directory to `nested-worktrees` (not on the denylist, chosen only to avoid the new denylist mechanism) throughout that test class, so it keeps testing the self-reference guard in isolation; `TestDiscoveryPrecision`'s denylist tests use generic names (`.venv`, `__pycache__`, `.cache`) rather than re-testing `.worktrees` by name.

**Verification:** `uv run --with pytest python -m pytest skills/worktree-data-sync/scripts/test_worktree_data_sync.py -q` (run outside the sandbox per dispatch note, since uv panics inside it) — `39 passed`. This includes the pre-existing `TestSeedFastPath` suite from sibling task 01, unmodified and still passing.
