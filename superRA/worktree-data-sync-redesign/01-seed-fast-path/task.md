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

## Planner Guidance

One `os.walk` can serve as the preflight; the contaminated set is the union of ancestor chains of dataless paths. Deriving per-directory cleanliness bottom-up avoids a second walk. Keep `run_seed`'s signature and `SeedSummary` usable from tests — extend the summary with the failure list rather than replacing it. `_progress` per-root messages can stay; consider adding the preflight's per-root size/file-count to the progress line so long copies are explainable.

## Results

Seed (`--mode seed`) now routes each copy-managed root through a stat-only preflight to the cheapest materialization path, and seed failures are loud (per-path stderr listing + nonzero exit). All work is in the two files below; no SKILL.md/doc changes (seed internals are not user-facing — the `--from` default and doc sync are task `03`).

### What changed — [sync_worktree_data.py](../../../skills/worktree-data-sync/scripts/sync_worktree_data.py)

- **`SeedSummary` extended, not replaced** ([sync_worktree_data.py:44-55](../../../skills/worktree-data-sync/scripts/sync_worktree_data.py#L44-L55)): added `failures: list[tuple[str, str]]` and a `record_failure(path, reason)` method that also bumps `errors`, so `errors` now always equals `len(failures)`. `run_seed`'s signature is unchanged; all former `summary.errors += 1` sites now call `record_failure`.
- **`preflight_root`** ([sync_worktree_data.py:141-190](../../../skills/worktree-data-sync/scripts/sync_worktree_data.py#L141-L190)): one `os.walk` (stat only, no content reads) collecting file count, total size, the dataless-file set, the contaminated-dir set (union of ancestor chains of every dataless file up to the root), and per-subtree file/symlink counts for accurate summary attribution during wholesale clones.
- **Router `seed_copy_root`** ([sync_worktree_data.py:374-408](../../../skills/worktree-data-sync/scripts/sync_worktree_data.py#L374-L408)): destination exists → merge walk (case 5); else no dataless → single-clone fast path (case 2); else `2·|dataless| > count` → per-file + `# data-sync:symlink` suggestion (case 4); else contaminated recursion (case 3).
- **`_clone_tree`** ([sync_worktree_data.py:265-295](../../../skills/worktree-data-sync/scripts/sync_worktree_data.py#L265-L295)): one `cp -c -R -p src dst` per clean (sub)tree, falling back to `shutil.copytree(symlinks=True)` off APFS/macOS, then to a recorded failure.
- **`_seed_contaminated`** / **`_seed_per_file`** ([sync_worktree_data.py:298-371](../../../skills/worktree-data-sync/scripts/sync_worktree_data.py#L298-L371)): mkdir + per-child routing; loose regular files are collected and handed to `_batch_copy`.
- **`_batch_copy`** ([sync_worktree_data.py:233-262](../../../skills/worktree-data-sync/scripts/sync_worktree_data.py#L233-L262)): chunks of 200 loose files per `cp -c … <destdir>` invocation; on a batch error it falls back per-file (via `cow_copy_file`) to isolate and record the exact failing path.
- **`copy_missing_tree`** (case 5, existing-destination merge, [sync_worktree_data.py:411-454](../../../skills/worktree-data-sync/scripts/sync_worktree_data.py#L411-L454)) preserved its never-overwrite semantics and now batches the missing loose copies and routes errors through `record_failure`.
- **Loud failures** ([emit_seed_failures](../../../skills/worktree-data-sync/scripts/sync_worktree_data.py#L1131-L1140), [main exit](../../../skills/worktree-data-sync/scripts/sync_worktree_data.py#L1241-L1244)): `emit_seed_failures` prints `Seed encountered N error(s):` plus the first 20 `path: reason` lines and an `… and K more` tail to stderr; `main` calls `sys.exit(1)` whenever `summary.failures` is non-empty.

Subprocess-call count is now proportional to contaminated directories, not files: a clean fresh root is one `cp -R`; the parent `### Context` measured this at ~0.3s vs ~15.5s for the old per-file loop on 2,000 files. Never-overwrite is automatically satisfied in the fresh-destination paths (cases 2-4) since the destination subtree does not yet exist; only case 5 needs per-file existence checks.

### Verification

- Full suite green — 36 passed (30 pre-existing + 6 new): `uv run --with pytest python -m pytest skills/worktree-data-sync/scripts/test_worktree_data_sync.py`.
- New tests in `TestSeedFastPath` ([test_worktree_data_sync.py:404-557](../../../skills/worktree-data-sync/scripts/test_worktree_data_sync.py#L404-L557)) cover every validation bullet: single-clone fast path (subprocess spy asserts exactly one `cp -R`), nested-two-levels dataless → real dirs + placeholder symlink + clean-sibling clone + batched loose files, mostly-dataless → stderr suggestion + per-file seeding, injected copy failure → per-path `record_failure`, capped 20+tail listing, and CLI `sys.exit(1)` on failure.
- Real end-to-end CLI seed into a fresh worktree: `output/` (3 files incl. a subdir) cloned wholesale, annotated `data/` symlinked, `Seed summary: copied=3, symlinked=1, skipped_existing=0, errors=0`, exit 0.
- Scripts stay stdlib-only and PEP 723-free (only new import is `dataclasses.field`); `python3 -c "import ast; ast.parse(...)"` parses clean.

### Notes for the reviewer

- The preflight calls the module-level `is_dataless(path)` per file (a second `os.stat` beyond the size stat) rather than reading `st_flags` off the single stat. This is deliberate: it keeps the dataless check monkeypatchable by tests (the constraint's required simulation method) and preserves the `AttributeError`-on-`st_flags` graceful fallback for Linux. A second `os.stat` is microseconds; the measured cost the task targets was per-file *subprocess* spawning, not per-file stats.
- Summary attribution for wholesale clones is derived from the preflight's per-subtree counts rather than counting actual copied entries; it is accurate for regular files and symlinks but does not separately account for empty directories (never counted in the old walk either).
