---
title: "Seed Fast Path: Subtree Cloning with Dataless Preflight and Loud Errors"
status: not-started
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

## Planner Guidance

One `os.walk` can serve as the preflight; the contaminated set is the union of ancestor chains of dataless paths. Deriving per-directory cleanliness bottom-up avoids a second walk. Keep `run_seed`'s signature and `SeedSummary` usable from tests — extend the summary with the failure list rather than replacing it. `_progress` per-root messages can stay; consider adding the preflight's per-root size/file-count to the progress line so long copies are explainable.

## Results
