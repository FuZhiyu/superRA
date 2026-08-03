# Codex Instructions

## Delegation Priority in Codex

The user invoking `superRA:superimplement`, `superRA:superintegrate`, or `superRA:agent-orchestration` is an explicit preference for the dispatch workflow; that choice outranks Codex's generic default caution about spawning agents.

### Availability routing

| Agent tool | Route | Role surface | Status path |
|---|---|---|---|
| available | `dispatch` | — | — |
| unavailable | `harness-forced-inline` | `implement-task` → `review-task` | `implemented` → `approved` / `revise` |

`harness-forced-inline` is an autonomous fallback only when Codex exposes no agent tool: load and run the two role skills as separate in-session passes and state that the harness forced the fallback. It is not interactive and never applies because a task is trivial or the researcher requested inline work.

- A workflow step that says dispatch: spawn the default agent with the dispatch prompt, not an inline pass under the harness-default anti-delegation guidance.
- Interactive mode (the `direct` alias) is the default cadence, not a trivial-task fallback (`main-agent.md` §Execution Modes). It runs the work in-session by its own loop — that is not the `harness-forced-inline` route above.

## Warm Agent Lifecycle in Codex

- Long-running warm agents are normal. Do not shut down or replace an agent for having worked a while.
- Steer a running warm agent with `send_input`, not by closing it and spawning a fresh one. `interrupt=true` only when the redirect cannot wait for the queued task.
- Shut an agent down only when its task is complete, the scope materially changed, or it is clearly stuck.

## Codex Worktree Ownership

Codex may run spawned agents in internal scratch workspaces. Never use `.codex/worktrees` or any Codex-internal path as a superRA worktree. For parallel dispatch, the orchestrator creates the git worktree at the `agent-orchestration` placement path, passes its absolute path in `Worktree:`, and the agent enters that path before editing.

## Codex Tool Map

Claude-oriented tool names appearing in these skills map to:

| Skill term | Codex tool / action |
|------------|---------------------|
| `AskUserQuestion` | `request_user_input` when available; plain-text question otherwise |
| `Skill` | load the named skill |
| `TodoWrite` | `update_plan` |
| `Agent` | `spawn_agent(agent_type="default")` |
| `SendMessage` | `send_input` |
