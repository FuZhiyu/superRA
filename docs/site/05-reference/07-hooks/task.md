---
title: "Hooks"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

superRA ships lifecycle hooks that run automatically in the background of your harness session.
They are guards and reminders, not enforcement boundaries — the discipline system handles enforcement.
Hook source files live in [hooks/](hooks/); harness-specific wiring is in [hooks/hooks.json](hooks/hooks.json) (Claude Code), [hooks/hooks-codex.json](hooks/hooks-codex.json) (Codex), and [hooks/hooks-cursor.json](hooks/hooks-cursor.json) (Cursor).

## Hook table

| Hook | Trigger event | Purpose | Claude Code | Codex | Cursor |
|---|---|---|:---:|:---:|:---:|
| **autoload-superra** | `UserPromptSubmit` when the prompt mentions a superRA term | Injects a reminder to load `superRA:using-superRA` if the master skill has not loaded this session. | Yes | Yes | Yes |
| **merge-guard** | `PreToolUse` on `Bash` commands matching `git merge/rebase/cherry-pick` | Reminds the agent to use `superRA:semantic-merge` instead of a bare merge command. | Yes | Yes | Yes |
| **ensure-using-superra** | `PreToolUse` on `Skill(superRA:superplan|superimplement|superintegrate)` | Hard-denies the workflow-skill call when `superRA:using-superRA` is not yet loaded; directs the agent to load it and retry. | Yes | — | Yes |
| **ensure-agent-orchestration** | `PreToolUse` on `Skill(superRA:superplan|superimplement|superintegrate)` | Same pattern as above, gating on `superRA:agent-orchestration`. | Yes | — | Yes |
| **task-hook** | `PostToolUse` on `Edit`, `Write`, and `Bash` | Reconciles the task tree after direct task edits or structural shell changes — validates status, propagates rollups. Codex shell interception is incomplete, so this is best-effort validation rather than a complete enforcement boundary. | Yes | Yes | — |
| **exit-plan-mode** | `PostToolUse` on `ExitPlanMode` | Suggests materializing a proposed plan into a `superRA/` task tree when it will guide later work. | Yes | — | Yes |
| **codex-plan-stop** | `Stop` while in plan mode (Codex only) | Codex equivalent of the plan-materialization reminder. | — | Yes | — |

## Coverage notes

Claude Code has the richest hook surface: six of the seven hooks fire — all except `codex-plan-stop`, which is the Codex-side replacement for `exit-plan-mode`.
Codex does not intercept `Skill` calls or plan-mode exit, so the two `ensure-*` gates and `exit-plan-mode` are absent; `codex-plan-stop` covers the plan-materialization reminder instead, and Codex shell interception (`task-hook`) is incomplete, making task-tree reconciliation best-effort there.
Cursor wires `autoload-superra`, `merge-guard`, both `ensure-*` gates, and `exit-plan-mode`, but carries no `task-hook`, so task-tree reconciliation does not run on Cursor.

## Installing hooks

Hooks are installed automatically when you install the superRA plugin.
For Claude Code:

```bash
claude plugin install superRA@superRA
```

For Codex, enable plugin hooks in your config (`[features].plugin_hooks = true` in `~/.codex/config.toml`) and run `/hooks` to trust the superRA bundle.
See [How-to: Install and Set Up](#/04-how-to/01-install-and-set-up) for the full per-harness procedure.
