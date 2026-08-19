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
`merge-guard`, task-tree `PostToolUse` hooks, and `codex-plan-stop`.

## Hook Coverage

Codex does not expose the same hook events as Claude Code, so the Codex hook set
uses Codex-native events. Runtime-specific coverage limits are documented per hook:

| Hook | Codex event | Notes |
|------|-------------|-------|
| `autoload-superra` | `UserPromptSubmit` | Injects a reminder to load `superRA:using-superra` on superRA prompts. |
| `agent-model-guard` | `PreToolUse` on `Agent` | Rejects generic dispatches unless their raw call explicitly sets both `model` and `reasoning_effort`. Codex CLI 0.147.0 starts `spawn_agent` without emitting this event, so that runtime cannot enforce the gate; deterministic manifest tests still protect the documented hook contract. |
| `merge-guard` | `PreToolUse` on `Bash` | Reminds agents to use `superRA:semantic-merge` before bare merge/rebase/cherry-pick commands. Codex shell interception is incomplete, so this is advisory coverage. |
| `task-tree` | `PostToolUse` on `Edit\|Write` and `Bash` | Reconciles `.plan/` or `superRA/` task trees after supported direct task edits and structural shell changes. Direct task edits are covered through `apply_patch`; structural task-tree shell changes are covered through `Bash`. Codex shell interception remains incomplete, so this is best-effort reconcile coverage rather than a complete enforcement boundary. |
| `codex-plan-stop` | `Stop` in plan mode | Replaces Claude Code's `ExitPlanMode` hook with a continuation prompt. |

Claude-only `Skill` gates are not installed in Codex because Codex does not
document skill loads as a `PreToolUse` surface.
