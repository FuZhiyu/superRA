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

This task does not change canonical role specs. Do not edit `skills/using-superra/references/direct-mode-implementer.md`, `skills/using-superra/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, or `.codex/agents/superra_reviewer.toml`; if scope expands into `agents/*`, regenerate and check them with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`.

## Planner Guidance

The background supervisor currently prints and opens a bare localhost URL on both spawn and reuse. `_worktree_id_for_plan_root()` already owns canonical selector construction, while `resolve_worktree()` intentionally maps an absent selector to the server's launch worktree. The browser-open tests in `skills/task-tree/scripts/test_dashboard.py` currently encode the bare-URL behavior and exercise only one plan root.

## Revision Notes

[Issue #47](https://github.com/FuZhiyu/superRA/issues/47) widens the scoped-launch invariant to relative Markdown image requests. The approved launch-URL implementation remains valid; the new child task owns the asset-request regression and fix.

## Results

### Outcome

- Added one live-URL constructor that obtains the canonical selector from `_worktree_id_for_plan_root()` and percent-encodes the complete token, including collision-disambiguating path suffixes ([plan_dashboard.py:169-191](../../../../skills/task-tree/scripts/plan_dashboard.py#L169-L191)).
- Fresh background launches, repo-scoped reuse, and foreground serving now print and open the invoking worktree's scoped URL ([plan_dashboard.py:2236-2245](../../../../skills/task-tree/scripts/plan_dashboard.py#L2236-L2245), [plan_dashboard.py:2305-2313](../../../../skills/task-tree/scripts/plan_dashboard.py#L2305-L2313), [plan_dashboard.py:2600-2620](../../../../skills/task-tree/scripts/plan_dashboard.py#L2600-L2620)). Existing resolver fallback, doc mode, static export, server identity/reuse, and file-link behavior were not changed.
- Added regressions for fresh launch emission/opening, cross-worktree reuse, collision-safe selector encoding, and foreground launch behavior ([test_dashboard.py:4500-4616](../../../../skills/task-tree/scripts/test_dashboard.py#L4500-L4616), [test_dashboard.py:5076-5093](../../../../skills/task-tree/scripts/test_dashboard.py#L5076-L5093)).
- Updated the task-tree, dashboard internals, and main-agent instructions to retain the emitted scoped URL and append only the task hash rather than reconstructing `?wt=` ([SKILL.md:30-38](../../../../skills/task-tree/SKILL.md#L30-L38), [internals.md:232-241](../../../../skills/task-tree/references/internals.md#L232-L241), [main-agent.md:5-9](../../../../skills/using-superra/references/main-agent.md#L5-L9), [main-agent.md:24-28](../../../../skills/using-superra/references/main-agent.md#L24-L28)).

### Result Protection

- Protected the composed scoped-URL invariant with a dedicated regression: the canonical URL generated for worktree B includes a percent-encoded collision-disambiguating selector, is accepted directly by the request router, and renders B rather than launch worktree A ([test_dashboard.py:582-626](../../../../skills/task-tree/scripts/test_dashboard.py#L582-L626)).
- Red-green verification passed: the test first passed against the protected implementation, failed when `_dashboard_url()` was deliberately perturbed to omit `?wt=`, and passed again after restoration.

### Verification

- Focused launch/foreground suite: 22 passed.
- Complete dashboard module: 283 passed; two dependency deprecation warnings.
- Complete task-tree script suite: 714 passed; four expected/dependency warnings.
- Live checkout command `uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard --root superRA --no-open` emitted `http://localhost:8995/?wt=dashboard-rendering`.
- Markdown validation reported all three modified instruction files clean.

### Integration

The 10 focused scoped-URL and shutdown-lifecycle protection tests passed, followed by the complete task-tree script suite at 714 passed with four expected/dependency warnings.

**Final diff self-check:** `git diff 35fab8110f13eb1b3dab920a1e2c9b0b52dd1e30..HEAD`; surviving change classes are the previously approved bounded shutdown/watchdog lifecycle and release metadata, scoped launch-URL construction and routing regressions, task-tree/main-agent instruction currency, and durable task records. Suspicious hunks were the instruction edits under `skills/*`, retained because the scoped-URL objective requires agents to preserve the emitted canonical selector and each line passes the contributor DRY/Necessity gate; the approved dashboard and postponed docs-site task edits are prior maturation results. No scope-ambiguous hunk remains.
