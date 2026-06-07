---
title: "Drift-free, install-free CLI source resolution"
status: not-started
depends_on: 
  - wrappers-and-hooks
  - unified-command-surface

tags: []
created: 2026-06-07
---

## Objective

Resolve the task-system package from the locally installed plugin (Claude/Codex) at runtime so the `superra` CLI never installs anything, never creates a cwd venv, and always matches the installed plugin version; GitHub is a last-resort fallback.

### Problem

Running `uv run superra …` from a research project (not the superRA checkout) makes `uv` discover that project's `pyproject.toml` and try to provision its `.venv`, which fails when a `.venv` already exists (`File exists (os error 17)`) and is wrong in any case — the user's research environment must not be touched to run a task-tree CLI. The repo-local `superRA/superra` wrapper avoids this only because it hardcodes `uv run --project "$REPO_ROOT/skills/task-system"`, which assumes a checkout and so does not exist in a research project's task tree. Pinning the wrapper to a git tag instead would reintroduce drift: when the installed plugin advances, a pinned wrapper silently runs stale CLI against current task files.

The fix is to resolve the task-system package source from whatever plugin is **already installed on disk** and run it with `uvx --from <source>`, which builds an isolated env in uv's cache (no install step, no cwd venv) and always matches the installed version. Both harnesses install the plugin under a versioned cache path:

- Claude: `~/.claude/plugins/cache/<marketplace>/superRA/<version>/skills/task-system`, with `~/.claude/plugins/installed_plugins.json` recording `superRA@superRA.installPath` authoritatively.
- Codex: `~/.codex/plugins/cache/<marketplace>/superra/<version>/skills/task-system` (note lowercase plugin slug; no manifest file).

### Scope

1. **Source resolver.** Implement a fast, bounded resolution chain returning the task-system package directory (the dir containing `pyproject.toml`), in priority order:
   1. **Env var** `CLAUDE_PLUGIN_ROOT` / `PLUGIN_ROOT` (set inside the harness) → `$VAR/skills/task-system`. Explicit harness signal; outranks everything.
   2. **Local checkout** — `$REPO_ROOT/skills/task-system/pyproject.toml` if present. Ordered above the installed caches *on purpose*: a contributor working in a checkout must get live edits, not the stale copied cache snapshot (see precedence rationale below). In a research project there is no checkout, so this branch is skipped and resolution falls through to the caches.
   3. **Claude cache (manifest)** — read `~/.claude/plugins/installed_plugins.json` (shape `{"version", "plugins": {"superRA@superRA": [records]}}`); from the records list pick the one whose `projectPath` matches the current task-tree's project, else the `scope: user` record (`projectPath: null`); append `/skills/task-system` to its `installPath`.
   4. **Codex cache** — bounded glob `~/.codex/plugins/cache/*/*/*/skills/task-system` (exactly three path segments — marketplace/plugin/version), pick the highest semver. Must not casing-assume the plugin slug (Codex uses lowercase `superra`, Claude uses `superRA`).
   5. **GitHub fallback** — `uvx --from "git+https://github.com/FuZhiyu/superRA.git@<tag>#subdirectory=skills/task-system"`. The only place a pin lives; it may lag the installed version and needs network on first build.
   - **Precedence rationale:** installs (Claude and Codex) are *copied* into versioned cache dirs (`…/cache/.../<version>/`), not symlinked to source, even for a local-directory (dev) marketplace — so a cache copy can lag a live working tree between updates. Hence checkout > caches for contributors; for end users (no checkout) the cache copy is the correct installed version.
   - **Speed gate:** no full-disk search. Resolution is env read + one file-exists test + single manifest read + one shallow fixed-depth glob. Cap the glob depth so it cannot walk the tree.
   - All local branches terminate in `uvx --from "<dir>" superra "$@"`.

2. **Wrapper generation.** Make the resolving wrapper the artifact a research project's task tree carries (replacing the checkout-only `uv run --project` assumption). The repo's own `superRA/superra` keeps the local-checkout branch preferred (so dev edits win) but carries the same chain so it is the canonical template.

3. **Agent-facing wrapper command.** Add a `superra` subcommand so agents create/refresh the wrapper without hand-authoring bash (e.g. `superra wrapper init [--root superRA]`). Idempotent; overwrites with the current resolver; sets the executable bit.

4. **Hook-shim alignment.** Extend `hooks/task-hook` to the full chain (it currently does env → checkout only; add Claude manifest, Codex cache, GitHub fallback). Keep the resolution logic single-sourced between the hook shim and the generated wrapper so they cannot drift (shared snippet emitted by the generator, or a sourced resolver the in-plugin shim reads from its own dir — the generated wrapper must stay self-contained since it cannot source from the plugin before resolving it).

5. **`--root` docs cleanup.** `--root` already auto-detects and prefers `superRA` (verified). Drop the redundant `--root superRA` from canonical examples in instructions/docs so the canonical form is `superra task tree` / `superra dashboard`.

6. **Docs.** Rewrite `skills/task-system/references/internals.md §Setup` and the `skills/task-system/SKILL.md` invocation/dashboard rows to make `uvx`-resolved the canonical end-user/agent form; demote `uv tool install` to an optional convenience; add an explicit warning never to run bare `uv run superra` from a research directory. Update `CLAUDE.md`/`AGENTS.md`/`AGENT.md` local-dev guidance only if the canonical contributor form changes (it should remain the `uv run --project skills/task-system` checkout form).

### Validation

- From a non-checkout dir with the plugin installed: the resolved command runs `superra task tree` with no cwd `.venv` created and no `uv tool install`.
- Resolver picks the Claude install when `installed_plugins.json` is present; falls back to the Codex bounded glob when only `~/.codex` has it; falls back to GitHub when neither cache exists.
- Resolution does not perform a full-disk search (assert glob depth bound; time the resolver).
- `superra wrapper init` writes an executable, resolver-carrying `superRA/superra`; re-running it is idempotent.
- `hooks/task-hook` still reconciles via the packaged entry point and now resolves through the same chain.
- No active instruction or doc tells agents to run bare `uv run superra` or to pass `--root superRA` redundantly.

## Planner Guidance

This extends, and stays consistent with, the `wrappers-and-hooks` decision that task trees do not carry brittle *dashboard* launchers: the generated wrapper here is a runtime-**resolving** CLI entry point with no baked generation-time paths, which is what that decision objected to. Keep it that way — no hardcoded plugin/cache/version paths in any committed artifact.

Single-source the bash resolution chain. Duplicated resolver logic between the hook shim and the generated wrapper is the primary drift risk for this task.

Generated role/Codex artifacts are not in scope unless a change touches canonical agent specs; if it does, regenerate via `skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` rather than hand-editing.

## Results

