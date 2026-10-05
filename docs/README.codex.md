# superRA for Codex

Guide for using superRA with OpenAI Codex.

Everything ships in one piece: the **plugin skills and hooks** from `.codex-plugin/plugin.json`. Dispatched agents are Codex's default agent; the dispatch prompt tells them which superRA role skill to load, so there are no named custom agents to install.

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

Use this path when you want the plugin to track a local clone directly.

## Why There Are No Named Agents

Codex plugins package skills, hooks, apps, and MCP configuration, and Codex discovers custom named agents separately from `.codex/agents/` or `~/.codex/agents/`. superRA used that second surface until v0.4 and no longer does: role behavior is a skill (`implement-task`, `review-task`), so the plugin's skill bundle carries it and every dispatch spawns Codex's default agent with a prompt that names the skill to load.

That keeps the workflow single-sourced — canonical skills stay in `skills/`, and Codex-specific surfaces are limited to adapters, symlinks, and install metadata.

If you installed superRA before v0.4, a session that finds the stale generated agents flags them and deletes them with your confirmation; to remove them yourself:

```bash
rm -f ~/.codex/agents/superra_implementer.toml ~/.codex/agents/superra_reviewer.toml
```

## Verification

Run `/hooks` in Codex after installing the plugin. When plugin hooks
are enabled, Codex should list superRA hooks from `hooks/hooks-codex.json`.
The Codex hook list should include `autoload-superra`, `agent-model-guard`,
`guard-task-approval`, `guard-foreign-checkout`, `ensure-communicate`,
`merge-guard`, task-tree `PostToolUse` hooks, and `codex-plan-stop`.

## Hook Coverage

What each hook does, and which run on Codex, is on the [hooks page](site/05-hooks/task.md). Codex uses its own events (`hooks/hooks-codex.json`), with these limits:

- **Skill gates** (`ensure-companion`) are not installed: Codex does not expose skill loads as a `PreToolUse` surface.
- **`agent-model-guard`** cannot enforce on Codex CLI 0.147.0, which starts `spawn_agent` without emitting `PreToolUse`; manifest tests still cover the hook contract.
- **Shell interception is incomplete**, so the `Bash` side of `guard-foreign-checkout`, `merge-guard`, and the task-tree hook is best-effort.
- **`guard-foreign-checkout`** falls through to allow on a runtime that does not honor `ask`.
- **`codex-plan-stop`** replaces Claude Code's `ExitPlanMode` hook with a continuation prompt at the end of a plan-mode turn.
