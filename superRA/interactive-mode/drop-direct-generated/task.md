---
title: "Drop the generated direct-mode role references and update the generator"
status: implemented
depends_on:
  - execution-mode-contract
---

## Objective

Remove the generated direct-mode role references and stop generating them:

- Delete `skills/using-superra/references/direct-mode-implementer.md` and `skills/using-superra/references/direct-mode-reviewer.md`.
- Update the generator `skills/codex-superra-setup/scripts/sync_codex_agents.py` to stop emitting them.
- Update `CLAUDE.md`'s "Currently generated" enumeration to drop the two files.
- Sweep all remaining references to these files (skill/agent prose, adapter references) and remove or repoint them.

Keep the Codex named-agent `.toml` files (`.codex/agents/superra_implementer.toml`, `superra_reviewer.toml`) — they serve subagent-mode dispatch, not direct mode.

Success: the two `direct-mode-*.md` files are gone; `sync_codex_agents.py` runs clean and still produces the `.toml` agents; no dangling reference to the deleted files remains anywhere in the repo.

## Planner Guidance

These are generated artifacts (`CLAUDE.md` §"Generated artifacts stay generated"): change the generator, don't only hand-delete. Verify the `.toml` generation path is unaffected after removing the direct-mode-ref emission. Depends on `execution-mode-contract` so the contract no longer points to the files before they are removed.

## Results

The two generated direct-mode role references are gone, the generator no longer emits them, and the `.toml` named-agents are unaffected.

**Generator ([sync_codex_agents.py](../../../skills/codex-superra-setup/scripts/sync_codex_agents.py)).** Stripped all direct-mode logic: removed the `direct_mode_target` / `direct_mode_title` fields from `RoleSpec`, the `DIRECT_MODE_MANAGED_HEADER` constant, `render_all_direct_mode_refs` / `render_direct_mode_ref` / `split_top_level_sections` / `render_implementer_direct_mode_before_you_start` / `render_reviewer_direct_mode_before_you_start`, and the now-unused `import re`. `main()` and `run_check()` no longer render, write, or check the direct-mode refs; both now operate on the `.toml` agents only. The docstring drops "and direct-mode role references."

**Deleted files.** [direct-mode-implementer.md] and [direct-mode-reviewer.md] removed via `git rm` from `skills/using-superra/references/`.

**Tests ([test_sync_codex_agents.py](../../../skills/codex-superra-setup/scripts/test_sync_codex_agents.py)).** Removed `test_committed_direct_mode_refs_match_generator` and `test_generated_direct_mode_refs_have_managed_headers` (both called the deleted `render_all_direct_mode_refs`), and the now-unused `runpy` import + `SCRIPT_NS`.

**CLAUDE.md.** Three live dangling references removed: the "Currently generated" enumeration now lists only the two `.toml`s; the "Generated artifacts stay generated" bullet drops "Direct-mode role references and"; and the obsolete "Direct mode reads skill-owned role references" architecture bullet (its loading mechanism no longer exists) is deleted.

**Verification.**
- `python3 sync_codex_agents.py --scope project` → clean; `--check` → "All generated agent files are up to date"; `git status` shows the two `.toml`s unmodified (already up to date), confirming the kept named-agents are unaffected.
- Both `.toml` agents present: `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`.
- `python3 test_sync_codex_agents.py` → `Ran 3 tests OK`.
- Repo-wide grep for `direct-mode-implementer` / `direct-mode-reviewer` / `direct_mode` returns zero hits in live skill prose, agent files, or adapter references (`main-agent.md` and `codex-instructions.md` are clean of the deleted-file names).

**Left untouched (out of scope, flagged).**
- `docs/plans/*.md` — dated historical plan/results archives that accurately record past regenerations of these files (one, [2026-05-20-markdown-style-guide-results.md](../../../docs/plans/2026-05-20-markdown-style-guide-results.md), holds actual markdown links to the deleted files). Rewriting an archive to erase accurate history is worse than a dead link in a non-loaded record; the dispatch's sweep scope (skill/agent/adapter prose) excludes these.
- Sibling task files `execution-mode-contract/task.md` and `task-tree/dashboard/worktree-scoped-launch-url/task.md` mention the filenames but belong to other tasks — not edited per the ownership boundary. The latter's "do not edit these generated files" note is now stale and should be cleaned when that task is next touched.

[direct-mode-implementer.md]: ../../../skills/using-superra/references/direct-mode-implementer.md
[direct-mode-reviewer.md]: ../../../skills/using-superra/references/direct-mode-reviewer.md
