# Codex Tool Reference

These skills still mention Claude-oriented tool names in places. In Codex, read them as the corresponding Codex action:

| Skill term | Codex action |
|------------|--------------|
| `AskUserQuestion` | use the question tool; fall back to plain text only if the tool is unavailable |
| `Skill` | invoke the named skill |
| `TodoWrite` | use the plan or todo tool the harness exposes |
| `Agent(subagent_type: "superRA:implementer")` | spawn the named Codex agent `superra_implementer` |
| `Agent(subagent_type: "superRA:reviewer")` | spawn the named Codex agent `superra_reviewer` |
| `SendMessage` | send input to the existing warm agent |
| parallel agent dispatch | use Codex parallel-agent tools when available; otherwise fall back to ordinary agent fan-out |

## Named Agent Setup

Codex supports custom named agents through `.codex/agents/` and `~/.codex/agents/`. superRA uses that documented path rather than prompt-wrapping built-in workers.

If `superra_implementer` or `superra_reviewer` are missing:

1. Run `superRA:codex-superra-setup`.
2. Choose **global** scope for normal cross-repo use, or **project** scope for testing this repo itself.
3. Restart Codex or start a fresh session if discovery has not refreshed yet.

The plugin installs the skills. The setup skill installs the named custom agents.

## Repo vs Plugin Discovery

- **Open this repo directly in Codex:** repo-scoped skill discovery comes from `.agents/skills/`, and project-scoped custom agents can live in `.codex/agents/`.
- **Use superRA while working in another repo:** install the plugin, then run `superRA:codex-superra-setup` with **global** scope so the named agents land in `~/.codex/agents/`.

This split is deliberate: skills are bundled and installed by the plugin, while named custom agents use Codex's documented custom-agent scan paths.

## Environment Detection

Skills that create worktrees or finish branches should detect their environment with read-only git commands before proceeding:

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

- `GIT_DIR != GIT_COMMON` → already in a linked worktree
- `BRANCH` empty → detached HEAD

See `superRA:worktree-data-sync` for worktree creation + data sync + cleanup, and `superRA:merge-workflow` / `superRA:execution-workflow` for branch completion flows.
