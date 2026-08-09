---
title: "Hooks"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

superRA ships lifecycle hooks that run automatically in the background of your harness session.
They act as guards and reminders. Enforcement is handled by the discipline system.
Hook source files live in [hooks/](hooks/); harness-specific wiring is in [hooks/hooks.json](hooks/hooks.json) (Claude Code) and [hooks/hooks-codex.json](hooks/hooks-codex.json) (Codex).

## Hook table

| Hook | Trigger event | Purpose | Claude Code | Codex |
|---|---|---|:---:|:---:|
| **autoload-superra** | `UserPromptSubmit` when the prompt mentions a superRA term | Injects a reminder to load `superRA:using-superra` if the master skill has not loaded this session. | Yes | Yes |
| **merge-guard** | `PreToolUse` on `Bash` commands matching `git merge/rebase/cherry-pick` | Reminds the agent to use `superRA:semantic-merge` instead of a bare merge command. | Yes | Yes |
| **ensure-companion** | `PreToolUse` on `Skill(superRA:superplan|superimplement|superintegrate)` | Hard-denies a workflow-skill call until its companion skills are loaded, listing every missing one in a single deny: all three require `superRA:using-superra`; the two always-dispatching skills (`superimplement`, `superintegrate`) also require `superRA:agent-orchestration`. Paths that only sometimes dispatch — `superplan`, and the default interactive loop when you ask for a review — are ungated on orchestration and instruct the load at their own dispatch point. | Yes | — |
| **ensure-communicate** | `PreToolUse` on `Edit`, `Write`, and `Bash` targeting Markdown | Hard-denies main-thread Markdown writes until `superRA:communicate` is loaded. Subagents are exempt. | Yes | Yes |
| **task-hook** | `PostToolUse` on `Edit`, `Write`, and `Bash` | Reminds the agent to apply Communicate after Markdown edits under the task tree; reconciles direct task edits and structural shell changes by validating status and propagating rollups. Codex shell interception is incomplete, so reconciliation is best effort. | Yes | Yes |
| **exit-plan-mode** | `PostToolUse` on `ExitPlanMode` | Suggests materializing a proposed plan into a `superRA/` task tree when it will guide later work. | Yes | — |
| **codex-plan-stop** | `Stop` while in plan mode (Codex only) | Codex equivalent of the plan-materialization reminder. | — | Yes |

## Coverage notes

Claude Code fires six of the seven hooks: all except `codex-plan-stop`, which is the Codex-side replacement for `exit-plan-mode`.
Codex does not intercept `Skill` calls or plan-mode exit, so the `ensure-companion` gate and `exit-plan-mode` are absent; `codex-plan-stop` covers the plan-materialization reminder instead, and Codex shell interception (`task-hook`) is incomplete, making task-tree reconciliation best-effort there.

## Installing hooks

Hooks are installed automatically when you install the superRA plugin.
For Claude Code:

```bash
claude plugin install superRA@superRA
```

For Codex, enable plugin hooks in your config (`[features].plugin_hooks = true` in `~/.codex/config.toml`) and run `/hooks` to trust the superRA bundle.
See the [Quickstart](#/02-quickstart) for install and setup, and the project [README](README.md) for the full per-harness procedure.
