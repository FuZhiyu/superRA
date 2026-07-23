---
title: "Drop the generated direct-mode role references and update the generator"
status: revise
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

## Review Notes

1. **CRITICAL** — [tests/check-harness-compatibility.sh:71-72](../../../tests/check-harness-compatibility.sh#L71-L72) is a live harness-compatibility test that asserts the two deleted files exist (`test -f skills/using-superra/references/direct-mode-implementer.md` / `direct-mode-reviewer.md`). The script runs under `set -euo pipefail`, so with the files deleted it now aborts at the "Codex adapter references" section — I ran it and it exits 1. This is a functional test breakage introduced directly by this task, so the Objective's success criterion ("no dangling reference to the deleted files remains anywhere in the repo"; repo "runs clean") is not met. Fix: remove the two `test -f` lines for the deleted files (keep the `codex-instructions.md` assertion on line 70) and re-run the script to confirm it passes.

2. **MAJOR** — [tests/harness-instruction-following/load_contract.json](../../../tests/harness-instruction-following/load_contract.json) still lists the deleted files in `source_paths` for LC005 ([L144-L145](../../../tests/harness-instruction-following/load_contract.json#L144-L145)) and LC006 ([L177-L178](../../../tests/harness-instruction-following/load_contract.json#L177-L178)), and LC006's `expected_evidence` ([L185](../../../tests/harness-instruction-following/load_contract.json#L185)) still claims the drift check "regenerates direct-mode references and .codex agent TOML". `test_contract.py` does not existence-check `source_paths`, so its 10 tests still pass, but these are stale dangling references in a live (non-archive) fixture that now misdescribe the coverage. Fix: drop the two `direct-mode-*` entries from LC005 and LC006 `source_paths`, and reword LC006's `expected_evidence` to reference only the `.toml` agents.

3. **MAJOR** — The [Results §Verification](#) grep claim ("Repo-wide grep … returns zero hits in live skill prose, agent files, or adapter references") is scoped too narrowly: it excludes `tests/`, which is live (not a `docs/plans/*.md` archive). A truly repo-wide grep surfaces the findings in items 1 and 2. Update the sweep and the Results account once those are fixed so "no dangling reference … anywhere in the repo" is accurate. The `docs/plans/*.md` and sibling-task-file exclusions already flagged are correctly judged; the `tests/` omission was not flagged at all.

Note: the generator, deletions, generator/test runs, `.toml`-unchanged verification, and CLAUDE.md edits (items in the Objective other than the sweep) all verified correct on my pass — `sync_codex_agents.py --scope project --check` passes, `test_sync_codex_agents.py` runs 3 OK, both `.toml`s unchanged (identical md5), and the CLAUDE.md enumeration/bullets are complete.
