---
title: "CLI Default and Documentation Sync: --from = Current Worktree"
status: approved
depends_on: [01-seed-fast-path, 02-discovery-precision]
---

## Objective

Make `--from` default to the worktree containing the caller instead of the repository's main worktree, and bring the three documents that describe the tool in line with the redesigned behavior. Success: an orchestrator running the seeder from its own analysis worktree gets that worktree as the source with no flag, and no document still teaches the workaround for the old default.

**CLI change** (`sync_worktree_data.py` / `worktree_data_discovery.py`): when `--from` is omitted, resolve the source to the worktree whose root contains `Path.cwd()` (it is already in `list_worktrees` output). Error out with a clear message if cwd is not inside any worktree of the repository. Update the `--from` help text and the SKILL.md default note.

**Documentation sync**, each edit passing the root `CLAUDE.md` teach-the-protocol gate:

- `skills/worktree-data-sync/SKILL.md` — describe the final seed behavior (denylist-filtered discovery, preflight, wholesale clone fast path, dataless handling, mostly-dataless annotation suggestion, per-path error report with nonzero exit) at the same level of brevity the file has today; document the denylist and that annotations override it.
- `skills/agent-orchestration/references/parallel-dispatch.md` — delete the bold "**Always pass `--from`**" warning; with the corrected default it documents a trap that no longer exists.
- `skills/agent-orchestration/references/worktree-harness-fallback.md` — update the example invocation: drop the now-redundant `--from "$(pwd)"`, and present `--seed-sync-mode force-symlink` as an option rather than the implied required workaround.

**Validation:** a test that a seed invoked with cwd inside a linked worktree and no `--from` uses that worktree as source (and one for the clear error outside any worktree); a line-by-line pass over the three doc diffs against the DRY + necessity tests.

## Details

`resolve_endpoints` already resolves and validates both endpoints; the change is confined to the default-source branch. For the SKILL.md rewrite, the §Modes/§Managed Path Discovery sections are the ones that drift; §Data Teardown and §See Also should survive untouched.

## Results

`--from` defaults to the worktree containing the caller's cwd, and the three documents describing the tool match the redesigned behavior.

**The CLI change is one branch.** `get_worktree_containing(cwd, known)` in [worktree_data_discovery.py](../../../skills/worktree-data-sync/scripts/worktree_data_discovery.py) returns the worktree root containing `cwd` — deepest match if roots nest — and raises `RuntimeError` when cwd sits outside every known worktree; `resolve_endpoints` calls it in place of `get_main_worktree` when `--from` is omitted, and `main()`'s existing handler turns that error into `Error: …` and exit 1. `get_main_worktree` stays as standalone API surface. The `--from` help text names the new default.

**Documentation sync.**

- [worktree-data-sync/SKILL.md](../../../skills/worktree-data-sync/SKILL.md) — §Command Surface names the new default; §Modes describes the preflight-routed seed and the per-path failure listing with nonzero exit; §Managed Path Discovery lists the denylist inline and states that it filters discovered entries rather than root contents, that an annotation overrides it, and that the safety net skips git-tracked symlinks. §Data Teardown and §See Also were left alone.
- [parallel-dispatch.md](../../../skills/agent-orchestration/references/parallel-dispatch.md) — the "**Always pass `--from`**" warning is deleted rather than reworded: the corrected default needs no narration.
- [worktree-harness-fallback.md](../../../skills/agent-orchestration/references/worktree-harness-fallback.md) — the example drops `--from "$(pwd)"` and presents `--seed-sync-mode force-symlink` as an option, not a required argument.

**Validation.** Four new tests in [test_worktree_data_sync.py](../../../skills/worktree-data-sync/scripts/test_worktree_data_sync.py); 44 pass. `TestEndpointResolution` asserts the cwd worktree is the default, that a main-worktree cwd still resolves to itself, that the helper picks the deepest match, and that an outside-cwd is rejected — reachable only by monkeypatching `list_worktrees`, since a real cwd `git worktree list` can resolve always falls inside one of its own reported roots. `TestCliSurface` runs the full CLI from a linked worktree with no `--from` and asserts the `From:` line and the copied file come from that worktree. A throwaway-repo end-to-end check agreed. The markdown checker is clean on all three documents.
