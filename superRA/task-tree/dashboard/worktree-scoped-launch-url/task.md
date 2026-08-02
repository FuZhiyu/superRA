---
title: "Worktree-Scoped Dashboard Requests"
status: approved
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

This task does not change canonical role specs. Do not edit `.codex/agents/superra_implementer.toml` or `.codex/agents/superra_reviewer.toml`; if scope expands into `agents/*`, regenerate and check them with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`.

## Results

### Outcome

- Added one live-URL constructor that obtains the canonical selector from `_worktree_id_for_plan_root()` and percent-encodes the complete token, including collision-disambiguating path suffixes ([plan_dashboard.py:203-206](../../../../skills/task-tree/scripts/plan_dashboard.py#L203-L206)).
- Fresh background launches, repo-scoped reuse, and foreground serving now print and open the invoking worktree's scoped URL ([plan_dashboard.py:2814-2817](../../../../skills/task-tree/scripts/plan_dashboard.py#L2814-L2817), [plan_dashboard.py:2741-2746](../../../../skills/task-tree/scripts/plan_dashboard.py#L2741-L2746), [plan_dashboard.py:3110-3124](../../../../skills/task-tree/scripts/plan_dashboard.py#L3110-L3124)). Existing resolver fallback, doc mode, static export, server identity/reuse, and file-link behavior were not changed.
- Added regressions for fresh launch emission/opening, cross-worktree reuse, collision-safe selector encoding, and foreground launch behavior ([test_dashboard.py:5828-5897](../../../../skills/task-tree/scripts/test_dashboard.py#L5828-L5897), [test_dashboard.py:6357-6373](../../../../skills/task-tree/scripts/test_dashboard.py#L6357-L6373)).
- Updated the task-tree, dashboard internals, and main-agent instructions to retain the emitted scoped URL and append only the task hash rather than reconstructing `?wt=` ([SKILL.md:31-39](../../../../skills/task-tree/SKILL.md#L31-L39), [internals.md:236-243](../../../../skills/task-tree/references/internals.md#L236-L243), [main-agent.md:5-9](../../../../skills/using-superra/references/main-agent.md#L5-L9), [main-agent.md:24-28](../../../../skills/using-superra/references/main-agent.md#L24-L28)).

### Result Protection

- Protected the scoped-URL invariant with a Node-independent routing regression: the canonical URL generated for worktree B includes a percent-encoded collision-disambiguating selector, is accepted directly by the request router, and renders B rather than launch worktree A ([test_dashboard.py:708-722](../../../../skills/task-tree/scripts/test_dashboard.py#L708-L722)).
- Red-green verification passed: the test first passed against the protected implementation, failed when `_dashboard_url()` was deliberately perturbed to omit `?wt=`, and passed again after restoration.

### Relative Image Assets

Relative Markdown images now preserve the active canonical worktree selector when rendered into `/files` requests ([dashboard.js:375-379](../../../../skills/task-tree/scripts/templates/dashboard.js#L375-L379)). A separately Node-marked regression uses the shared collision-worktree fixture, a disambiguated selector, and same-path assets with distinct contents to verify the exact encoded image URL and prove that `/files` returns bytes from the selected worktree, while an unscoped request continues to return launch-worktree bytes ([test_dashboard.py:724-752](../../../../skills/task-tree/scripts/test_dashboard.py#L724-L752)).

### Verification

- Focused integration regressions (collision-safe launch, scoped image bytes,
  watcher reconnect, and duplicate suppression): 4 passed.
- Complete dashboard module: 308 passed; two dependency deprecation warnings.
- Complete task-tree script suite: 731 passed; four expected/dependency warnings.
- Live checkout command `uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard --root superRA --no-open` emitted `http://localhost:8995/?wt=dashboard-rendering`.
- Markdown validation reported both in-scope task records clean.

### Integration

- Split the collision-safe launch and relative-image assertions over a shared
  fixture so the Python routing guard remains active when Node is unavailable,
  while the image rewrite reports its Node dependency explicitly
  ([test_dashboard.py:657-752](../../../../skills/task-tree/scripts/test_dashboard.py#L657-L752)).
- Project-doc audit covered root [README.md](../../../../README.md) and
  [CLAUDE.md](../../../../CLAUDE.md); both remain current, and no nearer module
  README or contributor guide exists for the changed files.

**Final diff self-check:** `git diff 2d4c8551629814cab303573322dfde1d26f2a318..HEAD`; surviving change classes are canonical scoped-image request routing, collision-safe launch/image regressions with shared test setup, and the durable task record. The approved task-record and `skills/*` code/test hunks are retained because they directly implement and protect the scoped-request objective; no scope-ambiguous or unjustified hunk remains.
