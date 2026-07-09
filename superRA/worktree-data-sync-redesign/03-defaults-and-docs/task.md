---
title: "CLI Default and Documentation Sync: --from = Current Worktree"
status: not-started
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
