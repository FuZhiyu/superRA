# Installing superRA for Codex

superRA has two Codex install surfaces:

- **Shared skills** via the plugin manifest at `.codex-plugin/plugin.json`
- **Named custom agents** via `codex-superra-setup`, which installs `superra_implementer` and `superra_reviewer` into either project or global Codex scope

For normal use across other repos, install the plugin and then run the setup skill with **global** scope.

## Cross-Repo Setup (Recommended)

1. Clone this repo somewhere durable:
   ```bash
   git clone https://github.com/FuZhiyu/econ-superpowers.git ~/.codex/plugins/superra
   ```
2. Add a personal Codex marketplace entry at `~/.agents/plugins/marketplace.json` that points to that clone. Minimal example:
   ```json
   {
     "name": "personal-superra",
     "interface": {
       "displayName": "Personal superRA Plugins"
     },
     "plugins": [
       {
         "name": "superra",
         "source": {
           "source": "local",
           "path": "./.codex/plugins/superra"
         },
         "policy": {
           "installation": "AVAILABLE",
           "authentication": "ON_INSTALL"
         },
         "category": "Productivity"
       }
     ]
   }
   ```
3. Restart Codex and install the `superra` plugin from that marketplace.
4. In Codex, run `codex-superra-setup`.
5. Choose **global** scope so the named agents install into `~/.codex/agents/`.
6. Restart Codex or start a fresh session if discovery has not refreshed yet.

## Repo-Local Development Setup

When you are developing superRA itself in this repo:

- Repo-scoped skill discovery comes from `.agents/skills/`
- Project-scoped named agents come from `.codex/agents/`

Run:

```bash
python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project
```

This refreshes the generated project-scoped agent files from the canonical role definitions in `agents/`.

## Verification

Check for the named agents in the expected scope:

```bash
ls ~/.codex/agents/superra_implementer.toml ~/.codex/agents/superra_reviewer.toml
```

or, for repo-local setup:

```bash
ls .codex/agents/superra_implementer.toml .codex/agents/superra_reviewer.toml
```

The plugin provides the skills; the setup step provides the named agents.
