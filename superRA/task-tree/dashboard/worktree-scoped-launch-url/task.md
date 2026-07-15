---
title: "Worktree-Scoped Dashboard Launch URLs"
status: implemented
depends_on:  []
---

## Objective

Emit and open dashboard URLs scoped to the invoking worktree so a repo-shared server never falls back to a different launch worktree.

- Use the dashboard's canonical, URL-encoded worktree selector, including basename-collision disambiguation; do not ask agents to reconstruct the selector from a directory basename.
- Cover fresh launch and repo-scoped reuse, with a regression that launches from one worktree and reuses the server from another.
- Update the owning task-tree and main-agent instructions so the emitted scoped URL is the source of truth for task deep links.
- Preserve foreground serving, doc mode, standalone export, collision-safe one-server-per-repo reuse, and the existing direct-open behavior for PDF links. Inline PDF preview is outside this fix.

### Generated-artifact boundary

This task does not change canonical role specs. Do not edit `skills/using-superra/references/direct-mode-implementer.md`, `skills/using-superra/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, or `.codex/agents/superra_reviewer.toml`; if scope expands into `agents/*`, regenerate and check them with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`.

## Planner Guidance

The background supervisor currently prints and opens a bare localhost URL on both spawn and reuse. `_worktree_id_for_plan_root()` already owns canonical selector construction, while `resolve_worktree()` intentionally maps an absent selector to the server's launch worktree. The browser-open tests in `skills/task-tree/scripts/test_dashboard.py` currently encode the bare-URL behavior and exercise only one plan root.

## Results

### Outcome

- Added one live-URL constructor that obtains the canonical selector from `_worktree_id_for_plan_root()` and percent-encodes the complete token, including collision-disambiguating path suffixes ([plan_dashboard.py:169-191](../../../../skills/task-tree/scripts/plan_dashboard.py#L169-L191)).
- Fresh background launches, repo-scoped reuse, and foreground serving now print and open the invoking worktree's scoped URL ([plan_dashboard.py:2236-2245](../../../../skills/task-tree/scripts/plan_dashboard.py#L2236-L2245), [plan_dashboard.py:2305-2313](../../../../skills/task-tree/scripts/plan_dashboard.py#L2305-L2313), [plan_dashboard.py:2600-2620](../../../../skills/task-tree/scripts/plan_dashboard.py#L2600-L2620)). Existing resolver fallback, doc mode, static export, server identity/reuse, and file-link behavior were not changed.
- Added regressions for fresh launch emission/opening, cross-worktree reuse, collision-safe selector encoding, and foreground launch behavior ([test_dashboard.py:4454-4570](../../../../skills/task-tree/scripts/test_dashboard.py#L4454-L4570), [test_dashboard.py:5030-5047](../../../../skills/task-tree/scripts/test_dashboard.py#L5030-L5047)).
- Updated the task-tree, dashboard internals, and main-agent instructions to retain the emitted scoped URL and append only the task hash rather than reconstructing `?wt=` ([SKILL.md:30-38](../../../../skills/task-tree/SKILL.md#L30-L38), [internals.md:232-241](../../../../skills/task-tree/references/internals.md#L232-L241), [main-agent.md:5-9](../../../../skills/using-superra/references/main-agent.md#L5-L9), [main-agent.md:24-28](../../../../skills/using-superra/references/main-agent.md#L24-L28)).

### Verification

- Focused launch/foreground suite: 22 passed.
- Complete dashboard module: 282 passed; two dependency deprecation warnings.
- Complete task-tree script suite: 713 passed; four expected/dependency warnings.
- Live checkout command `uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard --root superRA --no-open` emitted `http://localhost:8995/?wt=dashboard-rendering`.
- Markdown validation reported all three modified instruction files clean.
