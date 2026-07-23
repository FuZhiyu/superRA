---
title: "Drop the generated direct-mode role references and update the generator"
status: not-started
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
