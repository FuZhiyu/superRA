# Codex Instructions

## Delegation Priority in Codex

When the user invokes `superRA`, a `superRA:*workflow` skill, or
`superRA:agent-orchestration`, treat that as an explicit user preference
for the dispatch workflow in Codex; that user choice outranks Codex's
generic default caution about spawning agents.

### Availability routing

| Agent tool | Route | Role surface | Status path |
|---|---|---|---|
| available | `dispatch` | — | — |
| unavailable | `harness-forced-inline` | `implement-task` → `review-task` | `implemented` → `approved` / `revise` |

`harness-forced-inline` is an autonomous fallback only when Codex exposes no agent tool: load and run the two role skills as separate in-session passes and state that the harness forced the fallback. It is not interactive and never applies because a task is trivial or the researcher requested inline work.

- When a workflow step says to dispatch an implementer, a reviewer, or a
  `Stage: sync` author or reviewer, spawn the default agent
  (`spawn_agent(agent_type="default")`) with the dispatch prompt rather
  than staying inline because of the harness-default anti-delegation
  guidance. The prompt's first line names the skill the agent loads.
- Interactive mode (the `direct` alias) is an explicit opt-in by human
  cadence, not the Codex default and not a trivial-task fallback; the
  researcher requests it for closely-steered work
  (`main-agent.md §Execution Modes`).

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

## Codex Tool Map

These skills still mention Claude-oriented tool names in places. In
Codex, interpret them using the concrete Codex tool or action below:

| Skill term | Codex tool / action |
|------------|---------------------|
| `AskUserQuestion` | `request_user_input` when available; plain-text question otherwise |
| `Skill` | load the named skill |
| `TodoWrite` | `update_plan` |
| `Agent(general-purpose)` | `spawn_agent(agent_type="default")` |
| `SendMessage` | `send_input` |
