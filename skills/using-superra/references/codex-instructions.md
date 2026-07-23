# Codex Instructions

## Delegation Priority in Codex

When the user invokes `superRA`, a `superRA:*workflow` skill, or
`superRA:agent-orchestration`, treat that as an explicit user preference
for the named-agent workflow in Codex; that user choice outranks
Codex's generic default caution about spawning agents.

- When a workflow step says to dispatch an implementer or reviewer, spawn
  `superra_implementer` or `superra_reviewer` rather than staying inline
  because of the harness-default anti-delegation guidance.
- `superintegrate` Sync uses `Stage: sync` with generic sync author /
  sync reviewer agents. For those two branch-level dispatches, spawn the
  default/generic agent and pass the mode reference list from
  `superintegrate`.
- Independent review is mandatory. After any implementation step,
  dispatch `superra_reviewer` unless the user explicitly asked for no
  subagents or Codex truly lacks agent support. If agent support is
  unavailable, fall back to in-session reviewer mode and state that the
  fallback was forced by the harness.
- Interactive mode (the `direct` alias) is an explicit opt-in by human
  cadence, not the Codex default and not a trivial-task fallback; the
  researcher requests it for closely-steered work
  (`main-agent.md §Execution Modes`). Falling back to in-session
  execution because agent tools are unavailable is a separate,
  harness-forced case — state that it was forced.

## Warm Agent Lifecycle in Codex

- Long-running warm agents are normal in Codex. Do not shut down or
  replace an agent just because it has been working for a while.
- When the orchestrator needs to steer a running warm agent, use
  `send_input` to pass follow-up context instead of closing the agent
  and spawning a fresh one. Set `interrupt=true` only when the redirect
  cannot wait for the queued task to finish.
- Shut down a warm agent only when its task is complete, the scope has
  materially changed, or the agent is clearly stuck and no longer useful.

## Codex Worktree Ownership

Codex may run spawned agents in internal scratch workspaces. Do not use
`.codex/worktrees` or any Codex-internal path as a superRA worktree.
For parallel dispatch, the orchestrator creates the git worktree at the
`agent-orchestration` placement path, passes its absolute path in
`Worktree:`, and the agent enters that path before editing.

## Named Agent Setup

Codex supports custom named agents through `.codex/agents/` and `~/.codex/agents/`. superRA uses that documented path rather than prompt-wrapping built-in workers.

If `superra_implementer` or `superra_reviewer` are missing:

1. Run `superRA:codex-superra-setup`.
2. Choose **global** scope for normal cross-repo use, or **project** scope for testing this repo itself.
3. Restart Codex or start a fresh session if discovery has not refreshed yet.

The plugin installs the skills. The setup skill installs the named custom agents.

## Codex Tool Map

These skills still mention Claude-oriented tool names in places. In
Codex, interpret them using the concrete Codex tool or action below:

| Skill term | Codex tool / action |
|------------|---------------------|
| `AskUserQuestion` | `request_user_input` when available; plain-text question otherwise |
| `Skill` | load the named skill |
| `TodoWrite` | `update_plan` |
| `Agent(subagent_type: "superRA:implementer")` | `spawn_agent(agent_type="superra_implementer")` |
| `Agent(subagent_type: "superRA:reviewer")` | `spawn_agent(agent_type="superra_reviewer")` |
| `Agent(generic)` for `Stage: sync` author / reviewer | `spawn_agent(agent_type="default")` |
| `SendMessage` | `send_input` |

## Related Codex Skill

- `codex-superra-setup`: Generate and install the named
  `superra_implementer` / `superra_reviewer` Codex custom agents into
  `~/.codex/agents/` (global) or `.codex/agents/` (project).
