# superRA for Codex

Guide for using superRA with OpenAI Codex.

The Codex path has two pieces:

- **plugin skills and hooks** from `.codex-plugin/plugin.json`
- **named custom agents** from `codex-superra-setup`

Use **global agent install** for normal work across other repos.

## Recommended Setup

### Remote marketplace install

1. Add the repo as a marketplace:
   ```bash
   codex plugin marketplace add FuZhiyu/superRA
   ```
2. Restart Codex and install the `superra` plugin.
3. If your Codex build has plugin hooks off, enable them:
   ```toml
   [features]
   plugin_hooks = true
   ```
4. Run `/hooks` and trust the superRA plugin hooks if Codex asks for review.
5. Run `codex-superra-setup`.
6. Choose **global** scope so `superra_implementer` and `superra_reviewer` install into `~/.codex/agents/`.

Codex should cache the installed plugin under `~/.codex/plugins/cache/...`.

### Manual local-clone install

1. Clone this repo to a durable location, for example:
   ```bash
   git clone https://github.com/FuZhiyu/superRA.git ~/.codex/plugins/superra
   ```
2. Add a personal marketplace entry in `~/.agents/plugins/marketplace.json` that points to that clone.
3. Restart Codex and install the `superra` plugin.
4. If your Codex build has plugin hooks off, enable `[features].plugin_hooks = true`.
5. Run `/hooks` and trust the superRA plugin hooks if Codex asks for review.
6. Run `codex-superra-setup`.
7. Choose **global** scope so `superra_implementer` and `superra_reviewer` install into `~/.codex/agents/`.

Use this path when you want the plugin to track a local clone directly.

## Why This Split Exists

Codex plugins package skills, hooks, apps, and MCP configuration. Codex custom named agents are discovered from `.codex/agents/` or `~/.codex/agents/`. superRA follows that documented separation:

- plugin = shared skill and hook bundle
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

For hooks, run `/hooks` in Codex after installing the plugin. When plugin hooks
are enabled, Codex should list superRA hooks from `hooks/hooks-codex.json`.
The Codex hook list should include `autoload-superra`, `merge-guard`, and
`codex-plan-stop`.

If the agents exist but Codex still cannot spawn them, restart Codex or start a fresh session.

## Hook Coverage

Codex does not expose the same hook events as Claude Code, so the Codex hook set
uses reliable Codex-native events:

| Hook | Codex event | Notes |
|------|-------------|-------|
| `autoload-superra` | `UserPromptSubmit` | Injects a reminder to load `superRA:using-superra` on superRA prompts. |
| `merge-guard` | `PreToolUse` on `Bash` | Reminds agents to use `superRA:semantic-merge` before bare merge/rebase/cherry-pick commands. Codex shell interception is incomplete, so this is advisory coverage. |
| `codex-plan-stop` | `Stop` in plan mode | Replaces Claude Code's `ExitPlanMode` hook with a continuation prompt. |

Claude-only `Skill` gates are not installed in Codex because Codex does not
document skill loads as a `PreToolUse` surface. `ask-user-question-logger`
also remains Claude-only in plugin packaging for now; the script accepts Codex
`request_user_input` payloads, but Codex does not currently document that tool
as a `PostToolUse` hook surface.
