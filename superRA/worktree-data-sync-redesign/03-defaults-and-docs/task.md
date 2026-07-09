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

## Planner Guidance

`resolve_endpoints` already resolves and validates both endpoints; the change is confined to the default-source branch. For the SKILL.md rewrite, the §Modes/§Managed Path Discovery sections are the ones that drift; §Data Teardown and §See Also should survive untouched.

## Results

`--from` now defaults to the worktree containing the caller's cwd, not the main worktree, and the three docs that described the old default (or the redesigned seed/discovery behavior from sibling tasks 01/02) are brought current.

### CLI change — [worktree_data_discovery.py](../../../skills/worktree-data-sync/scripts/worktree_data_discovery.py)

- Added `get_worktree_containing(cwd, known)` ([worktree_data_discovery.py:72-80](../../../skills/worktree-data-sync/scripts/worktree_data_discovery.py#L72-L80)): returns the worktree root containing `cwd` (deepest match if more than one nests, though normal worktree layouts never nest), raising `RuntimeError` with a clear message when `cwd` is not inside any known worktree. Reuses the existing `_contains` ancestor check.
- `resolve_endpoints`'s omitted-`--from` branch now calls `get_worktree_containing(cwd, known)` instead of `get_main_worktree(cwd)` ([worktree_data_discovery.py:95-97](../../../skills/worktree-data-sync/scripts/worktree_data_discovery.py#L95-L97)); `get_main_worktree` is now unused and left in place since removing it was not requested and it is still meaningful standalone API surface.
- `--from` help text updated to "Source worktree path (default: worktree containing cwd)" ([sync_worktree_data.py:1159](../../../skills/worktree-data-sync/scripts/sync_worktree_data.py#L1159)).
- `main()` already caught `RuntimeError` from `resolve_endpoints` with a clean `Error: ...` + exit 1 ([sync_worktree_data.py:1217-1219](../../../skills/worktree-data-sync/scripts/sync_worktree_data.py#L1217-L1219)); no change needed there.

### Documentation sync

- [skills/worktree-data-sync/SKILL.md](../../../skills/worktree-data-sync/SKILL.md): §Command Surface's default note now says "the worktree containing the caller's current directory." §Modes' seed subsection rewritten to describe the preflight-routed fast path (fresh clean clone, contaminated-directory recursion with dataless symlinks, mostly-dataless per-file fallback with the annotation suggestion, existing-destination merge) and the per-path failure listing with nonzero exit. §Managed Path Discovery now documents the built-in denylist (listed inline), that it filters discovered entries only (not root contents), that a `# data-sync:symlink` annotation always overrides it, and that the top-level symlink safety net skips symlinks git already tracks. §Data Teardown and §See Also left untouched per planner guidance.
- [skills/agent-orchestration/references/parallel-dispatch.md](../../../skills/agent-orchestration/references/parallel-dispatch.md): deleted the "**Always pass `--from`**" warning — with the corrected default, an orchestrator seeding from its own worktree needs no flag, so the line was dropped rather than replaced with an equivalent reminder (the default is now unsurprising and doesn't need narration).
- [skills/agent-orchestration/references/worktree-harness-fallback.md](../../../skills/agent-orchestration/references/worktree-harness-fallback.md): example invocation drops `--from "$(pwd)"` and presents `--seed-sync-mode force-symlink` as an inline comment option rather than a required argument.

### Validation — [test_worktree_data_sync.py](../../../skills/worktree-data-sync/scripts/test_worktree_data_sync.py)

- `TestEndpointResolution`: renamed/updated `test_defaults_from_to_cwd_worktree_when_omitted` (was asserting main-worktree default, now asserts cwd's own worktree), added `test_defaults_from_to_main_worktree_when_cwd_is_main` (main worktree cwd still defaults to itself), `test_rejects_cwd_outside_any_worktree` (monkeypatches `list_worktrees` to return roots that don't cover cwd — a real cwd anywhere `git worktree list` can resolve is always contained in one of its own reported roots, so the "outside" branch is only reachable this way or via stale worktree metadata), and `test_worktree_containing_returns_deepest_match` (direct unit test of the new helper).
- `TestCliSurface`: added `test_cli_seed_defaults_from_cwd_worktree_without_from_flag` — full subprocess CLI invocation with cwd set to a linked worktree carrying a file not present in the main worktree, no `--from`, asserting the `From:` line names that worktree and its file (not the main worktree's) lands in the destination.
- Full suite: 43 passed (39 pre-existing from sibling tasks 01/02 + 4 new): `uv run --with pytest python -m pytest skills/worktree-data-sync/scripts/test_worktree_data_sync.py -q`.
- Real end-to-end CLI check (throwaway repo, outside the sandbox): seeding/diffing with cwd inside a linked worktree and no `--from` reports `From: <that worktree>`, not the main worktree.
- `uv run --script skills/report-in-markdown/scripts/check_markdown.py` on all three doc files: clean.
- Line-by-line pass of the three doc diffs against the root `CLAUDE.md` teach-the-protocol gate: each added/changed line states a fact the reader would otherwise guess or re-infer (the new default, the denylist contents, the seed routing) rather than narrating process or restating a default the runtime already shows in `--help`.
