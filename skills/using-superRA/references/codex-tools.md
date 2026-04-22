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

## Delegation Priority in Codex

When the user invokes `superRA`, a `superRA:*workflow` skill, or
`superRA:agent-orchestration`, treat that as an explicit user preference
for the named-agent workflow in Codex. Under
`superRA:using-superra` §Instruction Priority, that user choice outranks
Codex's generic default caution about spawning agents.

- When a workflow step says to dispatch an implementer or reviewer, spawn
  `superra_implementer` or `superra_reviewer` rather than staying inline
  because of the harness-default anti-delegation guidance.
- Independent review is mandatory. After any implementation step,
  dispatch `superra_reviewer` unless the user explicitly asked for no
  subagents or Codex truly lacks agent support. If agent support is
  unavailable, fall back to in-session reviewer mode and state that the
  fallback was forced by the harness.
- Direct mode remains a fallback, not the Codex default. Use it only
  when the workflow allows it and the user requested it, the task is
  trivial, or agent tools are unavailable.

## Warm Agent Lifecycle in Codex

- Long-running warm agents are normal in Codex. Do not shut down or
  replace an agent just because it has been working for a while.
- When the orchestrator needs to steer a running warm agent, use
  `SendMessage` to pass follow-up context instead of closing the agent
  and spawning a fresh one.
- Shut down a warm agent only when its task is complete, the scope has
  materially changed, or the agent is clearly stuck and no longer useful.

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

See `superRA:agent-orchestration/references/worktree-harness-fallback.md`
for worktree create / enter / remove mechanics (harness tools preferred;
raw `git worktree` fallback) and `superRA:worktree-data-sync` for seeding
non-git data into an existing worktree. Finishing a development branch —
push, PR, or discard — is covered by `superRA:integration-workflow`
Phase D and `superRA:implementation-workflow` Step 4 Option 4.

## Codex App Finishing

When the sandbox blocks branch/push operations (detached HEAD in an
externally managed worktree), the agent commits all work and informs
the user to use the App's native controls:

- **"Create branch"** — names the branch, then commit/push/PR via App UI
- **"Hand off to local"** — transfers work to the user's local checkout

The agent can still run tests, stage files, and output suggested branch
names, commit messages, and PR descriptions for the user to copy.
