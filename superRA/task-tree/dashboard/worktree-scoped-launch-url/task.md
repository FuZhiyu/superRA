---
title: "Worktree-Scoped Dashboard Requests"
status: implemented
depends_on: []
---

## Objective

Keep a repo-shared dashboard scoped to the invoking worktree across launch and subsequent worktree-dependent requests so it never falls back to a different launch worktree.

- Use the dashboard's canonical, URL-encoded worktree selector, including basename-collision disambiguation; do not ask agents to reconstruct the selector from a directory basename.
- Cover fresh launch and repo-scoped reuse, with a regression that launches from one worktree and reuses the server from another.
- Preserve the emitted selector when client-rendered task assets request worktree-dependent server routes.
- Update the owning task-tree and main-agent instructions so the emitted scoped URL is the source of truth for task deep links.
- Preserve foreground serving, doc mode, standalone export, collision-safe one-server-per-repo reuse, and the existing direct-open behavior for PDF links. Inline PDF preview is outside this fix.

### Generated-artifact boundary

This task does not change canonical role specs. Do not edit `skills/using-superra/references/direct-mode-implementer.md`, `skills/using-superra/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, or `.codex/agents/superra_reviewer.toml`; if scope expands into `agents/*`, regenerate and check them with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`.

## Results

### Outcome

- Added one live-URL constructor that obtains the canonical selector from `_worktree_id_for_plan_root()` and percent-encodes the complete token, including collision-disambiguating path suffixes ([plan_dashboard.py:169-191](../../../../skills/task-tree/scripts/plan_dashboard.py#L169-L191)).
- Fresh background launches, repo-scoped reuse, and foreground serving now print and open the invoking worktree's scoped URL ([plan_dashboard.py:2310-2319](../../../../skills/task-tree/scripts/plan_dashboard.py#L2310-L2319), [plan_dashboard.py:2379-2387](../../../../skills/task-tree/scripts/plan_dashboard.py#L2379-L2387), [plan_dashboard.py:2679-2694](../../../../skills/task-tree/scripts/plan_dashboard.py#L2679-L2694)). Existing resolver fallback, doc mode, static export, server identity/reuse, and file-link behavior were not changed.
- Added regressions for fresh launch emission/opening, cross-worktree reuse, collision-safe selector encoding, and foreground launch behavior ([test_dashboard.py:5285-5401](../../../../skills/task-tree/scripts/test_dashboard.py#L5285-L5401), [test_dashboard.py:5861-5878](../../../../skills/task-tree/scripts/test_dashboard.py#L5861-L5878)).
- Updated the task-tree, dashboard internals, and main-agent instructions to retain the emitted scoped URL and append only the task hash rather than reconstructing `?wt=` ([SKILL.md:30-38](../../../../skills/task-tree/SKILL.md#L30-L38), [internals.md:232-241](../../../../skills/task-tree/references/internals.md#L232-L241), [main-agent.md:5-9](../../../../skills/using-superra/references/main-agent.md#L5-L9), [main-agent.md:24-28](../../../../skills/using-superra/references/main-agent.md#L24-L28)).

### Result Protection

- Protected the composed scoped-URL invariant with a dedicated regression: the canonical URL generated for worktree B includes a percent-encoded collision-disambiguating selector, is accepted directly by the request router, and renders B rather than launch worktree A ([test_dashboard.py:670-726](../../../../skills/task-tree/scripts/test_dashboard.py#L670-L726)).
- Red-green verification passed: the test first passed against the protected implementation, failed when `_dashboard_url()` was deliberately perturbed to omit `?wt=`, and passed again after restoration.

### Relative Image Assets

Relative Markdown images now preserve the active canonical worktree selector when rendered into `/files` requests ([dashboard.js:291-295](../../../../skills/task-tree/scripts/templates/dashboard.js#L291-L295)). The protected regression uses a collision-disambiguated selector and same-path assets with distinct contents to verify the exact encoded image URL and prove that `/files` returns bytes from the selected worktree, while an unscoped request continues to return launch-worktree bytes ([test_dashboard.py:670-753](../../../../skills/task-tree/scripts/test_dashboard.py#L670-L753)).

### Verification

- Focused scoped-launch and relative-image protection suite: 14 passed.
- Complete dashboard module: 306 passed; two dependency deprecation warnings.
- Complete task-tree script suite: 729 passed; four expected/dependency warnings.
- Live checkout command `uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard --root superRA --no-open` emitted `http://localhost:8995/?wt=dashboard-rendering`.
- Markdown validation reported all three modified instruction files clean.
