---
title: "Install and Set Up"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

You want superRA running in your harness so you can start a project.
This guide covers installation on Claude Code, Codex, and other harnesses.

## Install on Claude Code

Claude Code (v2.1+) supports plugin installation directly from GitHub.
Run two commands and restart:

```bash
claude plugin marketplace add FuZhiyu/superRA
claude plugin install superRA@superRA
```

After restarting, the skills, agents, and hooks are available in every session.

To update later:

```bash
claude plugin marketplace update superRA
claude plugin update superRA
```

**For development or forking:** clone the repo and install from the local clone instead.
Full instructions are in the [README installation section](README.md#installation).

## Install on Codex

Codex installation has two pieces that must both be done: the plugin (skills and hooks) and the named agents (`superra_implementer`, `superra_reviewer`).
The split is deliberate — Codex plugins carry shared skill and hook bundles, while named agents are discovered separately from `~/.codex/agents/`.

### Remote marketplace install (recommended)

1. Add the marketplace:

   ```bash
   codex plugin marketplace add FuZhiyu/superRA
   ```

2. Restart Codex and install the `superra` plugin from the Plugins UI (or `/plugins`).
3. If Codex reports plugin hooks disabled, enable them by adding to `~/.codex/config.toml`:

   ```toml
   [features]
   plugin_hooks = true
   ```

4. Run `/hooks` and trust the superRA plugin hooks if Codex prompts for review.
5. Run `codex-superra-setup` and choose **global** scope.
   This installs `superra_implementer` and `superra_reviewer` into `~/.codex/agents/`.
6. Restart Codex or start a fresh session if agent discovery has not refreshed.

**Verify:** check that `~/.codex/agents/superra_implementer.toml` and `~/.codex/agents/superra_reviewer.toml` exist, and that `/hooks` lists the superRA hooks.

For the manual local-clone path, hook coverage details, and troubleshooting, see [`docs/README.codex.md`](docs/README.codex.md).

## Install on Other Harnesses

superRA ships entry files for several other harnesses:

- **Copilot CLI and any `AGENTS.md`-aware tool** — point the tool at [`AGENTS.md`](AGENTS.md) at the repo root.
- **Gemini CLI** — point at [`GEMINI.md`](GEMINI.md) and [`gemini-extension.json`](gemini-extension.json).

Harness-specific install flows vary.
For patterns that apply to any Superpowers-compatible harness, see the [upstream Superpowers docs](https://github.com/obra/superpowers) and substitute this repo's URL.

## What Gets Installed

A complete install gives you:

- **Skills** — `superplan`, `superimplement`, `superintegrate`, domain skills, and utility skills, all loadable by name in your harness.
- **Named agents** — `superra_implementer` and `superra_reviewer`, pre-loaded with the right role protocols.
- **Hooks** — lifecycle automation: merge-guard (warns on bare `git merge`), task-tree reconciliation on task edits, plan-materialization prompt on exit from plan mode, and session startup reminder to load the master skill.

The full hook list and per-harness coverage is in [Reference › Hooks](#/05-reference/07-hooks).
