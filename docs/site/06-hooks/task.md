---
title: "Hooks"
status: not-started
depends_on:  []
---

## Objective

superRA's hooks run in the background of every agent session: they remind the agent of the right skill, block a few unsafe actions, and keep the task tree consistent after edits. They install with the plugin; you never call them.

## What you may notice

- **An approval prompt** when the agent tries to change a task tree in a different checkout than the one the session started in (`guard-foreign-checkout`). Approve deliberate cross-checkout work; an unattended session stops there.
- **A blocked action the agent retries**, after loading a missing skill or fixing the input (the "Blocks" rows below).
- **Nothing else.** Reminders go to the agent, not to you.

## Hook reference

| Hook | Fires on | Effect | Claude Code | Codex |
|---|---|---|:---:|:---:|
| **autoload-superra** | A prompt mentioning superRA or a phase name | Reminds the agent to load `using-superra`. | Yes | Yes |
| **ensure-companion** | A call to `superplan`, `superimplement`, or `superintegrate` | Blocks until the phase's companion skills are loaded. | Yes | — |
| **ensure-communicate** | A main-agent Markdown write | Blocks until `communicate` is loaded. Subagents are exempt. | Yes | Yes |
| **agent-model-guard** | A generic subagent dispatch | Blocks unless the dispatch names a model (and, on Codex, a reasoning effort). | Yes | Yes |
| **guard-task-approval** | A `task.md` edit | Blocks `status: approved` while the task's review notes still hold a `[BLOCKING]` finding. | Yes | Yes |
| **guard-foreign-checkout** | A `task.md` write or git history command aimed at another checkout | Asks you first. Worktrees of the session's own repository pass. | Yes | Yes |
| **merge-guard** | `git merge`, `rebase`, or `cherry-pick` | Reminds the agent to use [semantic-merge](#/04-utility-skills/02-semantic-merge). | Yes | Yes |
| **task-hook** | Any edit or shell command | Validates edited tasks and updates parent status; reminds the agent to follow `communicate` after Markdown edits under `superRA/`; names the [reproduction steps](#/04-utility-skills/09-reproducibility) an edit makes stale. | Yes | Yes (shell coverage best-effort) |
| **exit-plan-mode** | Leaving Claude Code plan mode | Suggests turning the plan into a `superRA/` task tree. | Yes | — |
| **codex-plan-stop** | The end of a Codex plan-mode turn | Same suggestion, for Codex. | — | Yes |

Sources live in [hooks/](hooks/), wired by [hooks/hooks.json](hooks/hooks.json) (Claude Code) and [hooks/hooks-codex.json](hooks/hooks-codex.json) (Codex).

## Installing

- **Claude Code:** installing the plugin installs the hooks.
- **Codex:** set `[features].plugin_hooks = true` in `~/.codex/config.toml` if your build has plugin hooks off, then run `/hooks` and trust the superRA bundle.

Full setup is in the [Quickstart](#/02-quickstart) and [`docs/README.codex.md`](docs/README.codex.md).
