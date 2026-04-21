# superRA for Codex

Guide for using superRA with OpenAI Codex.

The Codex path has two pieces:

- **plugin skills** from `.codex-plugin/plugin.json`
- **named custom agents** from `codex-superra-setup`

Use **global agent install** for normal work across other repos.

## Recommended Setup

1. Clone this repo to a durable location, for example:
   ```bash
   git clone https://github.com/FuZhiyu/superRA.git ~/.codex/plugins/superra
   ```
2. Add a personal marketplace entry in `~/.agents/plugins/marketplace.json` that points to that clone.
3. Restart Codex and install the `superra` plugin.
4. Run `codex-superra-setup`.
5. Choose **global** scope so `superra_implementer` and `superra_reviewer` install into `~/.codex/agents/`.

## Why This Split Exists

Codex plugins package skills, apps, and MCP configuration. Codex custom named agents are discovered from `.codex/agents/` or `~/.codex/agents/`. superRA follows that documented separation:

- plugin = shared skill bundle
- `codex-superra-setup` = named agent installer

That keeps the workflow single-sourced:

- canonical skills stay in `skills/`
- canonical role specs stay in `agents/`
- Codex-specific surfaces are generated adapters, symlinks, and install metadata

## Verification

For cross-repo use:

```bash
ls ~/.codex/agents/superra_implementer.toml ~/.codex/agents/superra_reviewer.toml
```

If the agents exist but Codex still cannot spawn them, restart Codex or start a fresh session.
