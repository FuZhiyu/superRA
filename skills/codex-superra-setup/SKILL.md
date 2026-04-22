---
name: codex-superra-setup
description: Use when installing or refreshing superRA's named Codex agents in project scope (.codex/agents) or global scope (~/.codex/agents).
---

# Codex superRA Setup

Install or refresh superRA's named Codex agents from the canonical role specs in `agents/`. This skill is for the Codex-specific part of the setup: the plugin delivers the shared skills, while the named agents live in `.codex/agents/` or `~/.codex/agents/`.

**Core rule:** use **global** scope for normal cross-repo work; use **project** scope when testing or developing this repo itself.

## When To Use

- Right after installing the superRA Codex plugin
- When `superra_implementer` or `superra_reviewer` are missing
- When `agents/implementer.md` or `agents/reviewer.md` changed and the Codex agent TOMLs need a refresh
- When you want to choose between repo-only setup and cross-repo setup

## Scope Choice

Choose one target:

- **Global scope**: `~/.codex/agents/`
  Use this when you will work in repos other than this one. This is the normal end-user setup.
- **Project scope**: `.codex/agents/`
  Use this when you are developing or testing superRA in this repo and want the named agents available only here.

If the choice has not already been made, ask with the question tool. Suggested prompt:

```text
Install superRA's Codex agents globally in ~/.codex/agents for cross-repo use, or only in this repo's .codex/agents for local testing?
```

## Procedure

1. Confirm the superRA skills are already available in Codex.
   If this repo is open directly in Codex, the `.agents/skills/` symlinks cover repo-scoped discovery.
   If you are using the plugin from another repo, make sure the plugin is installed first.
2. Pick the scope:
   - Global: `global`
   - Project: `project`
3. Resolve the installer script relative to **this skill's directory**, not relative to the current working directory. For normal plugin use, Codex is often running in some other repo, so `skills/codex-superra-setup/...` from the current repo would be wrong. Set your working directory to this skill directory and run:

```bash
python3 scripts/sync_codex_agents.py --scope global
```

or:

```bash
python3 scripts/sync_codex_agents.py --scope project
```

4. If the script reports an unmanaged conflicting file, stop and ask before overwriting it. Only rerun with `--force` after the user explicitly approves:

```bash
python3 scripts/sync_codex_agents.py --scope global --force
```

5. Verify the files landed where expected:
   - Global: `~/.codex/agents/superra_implementer.toml` and `~/.codex/agents/superra_reviewer.toml`
   - Project: `.codex/agents/superra_implementer.toml` and `.codex/agents/superra_reviewer.toml`
6. Restart Codex or start a fresh session if agent discovery has not refreshed yet.

## Verification

The generated agents are:

- `superra_implementer`
- `superra_reviewer`

They expect the superRA skills to be available in the parent session. If the named agents exist but the skills are missing, install or enable the superRA plugin first.

## Notes

- The canonical role instructions still live in `agents/implementer.md` and `agents/reviewer.md`.
- The generated TOMLs are derived from those files; do not hand-edit the generated agent files unless you are intentionally breaking the sync model.
- For contributor verification, from this skill directory run `python3 scripts/sync_codex_agents.py --scope project --check`.
