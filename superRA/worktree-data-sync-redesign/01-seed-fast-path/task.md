---
title: "Seed Fast Path: Subtree Cloning with Dataless Preflight and Loud Errors"
status: approved
depends_on: []
---

## Objective

Replace per-file subprocess copying in `--mode seed` (`skills/worktree-data-sync/scripts/sync_worktree_data.py`) with per-root routing chosen by a stat-only preflight, and make seed failures loud. Success: seeding a fresh worktree issues subprocess calls proportional to the number of contaminated directories, not the number of files, and any failure is visible per-path with a nonzero exit.

**Routing (per copy-managed root):**

1. **Preflight** — one stat-only walk of the source root collecting file count, total size, and the set of dataless files (`st_flags & SF_DATALESS`; no content reads, so no materialization). Mark every ancestor directory of a dataless file *contaminated*.
2. **Fast path** — destination root absent and no dataless files → one `cp -c -R -p <src> <dst>` for the whole root; on failure fall back to a full copy that still avoids per-file subprocesses (`shutil.copytree` with symlinks preserved).
3. **Contaminated directory** — `mkdir` the destination dir, then per child: clean subdirectory → its own single `cp -c -R -p`; contaminated subdirectory → recurse; dataless file → symlink to the resolved source path; remaining regular files → batched `cp -c f1 f2 … <destdir>/` calls (many files per invocation, never one subprocess per file).
4. **Mostly-dataless root** (more than half of its files dataless) — seed per-file (symlink dataless, batch-copy the rest) and print a suggestion to annotate the root `# data-sync:symlink` in `.gitignore`; do not change behavior automatically.
5. **Destination root already exists** — the existing per-file merge walk with its never-overwrite semantics, unchanged in behavior (batch the copies where straightforward).

`--seed-sync-mode force-cow` routes through the same fast path; `force-symlink` and symlink-only annotated roots are unaffected (still one top-level symlink each).

**Error reporting (all seed paths):** record every failed path with its reason; print failures to stderr at the end (cap the listing, e.g. first 20 plus a total count); exit nonzero when any error occurred. The current behavior — exceptions swallowed into a bare `errors=N` counter with exit 0 — must be gone.

**Preserved invariants:**

- Never overwrite an existing destination file, in every path.
- Nested symlinks inside cloned trees arrive as symlinks with verbatim targets (cp's `-R`-implies-`-P` behavior matches the current walk; see parent `### Context`).
- Graceful degradation off APFS/macOS per parent `### Constraints`.

**Validation (extend `test_worktree_data_sync.py`):**

- Fresh destination + clean root seeds via a single clone invocation (assert by spying on/monkeypatching the subprocess layer).
- A root with a dataless file nested two levels deep (monkeypatched dataless check) yields real directories along the contaminated path, a symlink for the dataless file, whole-subtree clones for clean siblings, and batched copies for loose files.
- A mostly-dataless root produces the annotation suggestion on stderr and per-file seeding.
- An injected copy failure produces the per-path error listing and a nonzero exit.
- Existing never-overwrite and seed-mode tests still pass.

## Details

One `os.walk` can serve as the preflight; the contaminated set is the union of ancestor chains of dataless paths. Deriving per-directory cleanliness bottom-up avoids a second walk. Keep `run_seed`'s signature and `SeedSummary` usable from tests — extend the summary with the failure list rather than replacing it. `_progress` per-root messages can stay; consider adding the preflight's per-root size/file-count to the progress line so long copies are explainable.

## Results

Seed (`--mode seed`) routes each copy-managed root through a stat-only preflight to the cheapest materialization path, and every failure is named. The work is confined to [sync_worktree_data.py](../../../skills/worktree-data-sync/scripts/sync_worktree_data.py) and its test file; the user-facing description belongs to task [03](../03-defaults-and-docs/task.md).

**The preflight is one `os.walk` with no content reads.** It collects file count, total size, the dataless-file set, and the contaminated set — the union of every dataless file's ancestor chain — plus per-subtree counts so a wholesale clone can still attribute its summary. `seed_copy_root` then picks the path: an existing destination takes the unchanged never-overwrite merge walk; a clean fresh root is one `cp -c -R -p`; a root more than half dataless seeds per file and suggests the `# data-sync:symlink` annotation; anything else recurses through contaminated directories, symlinking placeholders and handing loose files to batched `cp` calls of 200. Off APFS the clone falls back to `shutil.copytree(symlinks=True)`, and a failed batch retries per file to isolate the exact failing path.

Subprocess calls now scale with contaminated directories rather than files — the parent's measurement is 0.3s against 15.5s on 2,000 files. Never-overwrite is free in the three fresh-destination paths, since the destination subtree does not exist yet.

**Failures reach the caller.** `SeedSummary` gained a `failures` list and a `record_failure` method that every former `summary.errors += 1` site now calls, so `errors == len(failures)`. `emit_seed_failures` prints the first 20 `path: reason` lines with an `… and K more` tail to stderr, and `main` exits 1 whenever the list is non-empty.

**Verification.** 43 tests pass — `uv run --with pytest python -m pytest skills/worktree-data-sync/scripts/test_worktree_data_sync.py`. `TestSeedFastPath` covers each routing case with a subprocess spy, including a regression guard that a directory symlink inside a mostly-dataless root is recreated verbatim rather than followed into or dropped. An end-to-end CLI seed into a fresh worktree cloned a three-file root wholesale, symlinked the annotated root, and exited 0.

### Notes

- The preflight calls module-level `is_dataless(path)` per file rather than reading `st_flags` off its own stat. That keeps the check monkeypatchable — the simulation method the parent `### Constraints` requires — and preserves the `AttributeError`-on-`st_flags` fallback for Linux. The cost this task targets is per-file subprocess spawning, not per-file stats.
- Wholesale-clone summary counts come from the preflight, so they are accurate for regular files and symlinks but do not count empty directories. Neither did the walk they replaced.
