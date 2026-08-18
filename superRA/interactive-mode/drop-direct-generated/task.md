---
title: "Drop the generated direct-mode role references and update the generator"
status: approved
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

## Details

These are generated artifacts (`CLAUDE.md` §"Generated artifacts stay generated"): change the generator, don't only hand-delete. Verify the `.toml` generation path is unaffected after removing the direct-mode-ref emission. Depends on `execution-mode-contract` so the contract no longer points to the files before they are removed.

## Results

The two generated direct-mode role references are gone: the generator stopped emitting them, `CLAUDE.md`'s generated-artifact enumeration dropped them, and the live surfaces that hard-referenced them — the harness compatibility script and the `load_contract.json` source paths — were repointed. A whole-repo grep left hits only in the dated `docs/plans/` archives, which record past regenerations accurately and were left alone.

The Codex named-agent TOMLs this task deliberately preserved, and the `codex-superra-setup` generator itself, were retired soon after by [v04-lean-workflow/role-skills](../../v04-lean-workflow/role-skills/task.md). Nothing this task touched survives on the current surface.
