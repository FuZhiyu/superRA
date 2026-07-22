---
title: "Worktree-Scoped Relative Image Assets"
status: approved
depends_on:  []
---

## Objective

Preserve the active canonical worktree selector when live-dashboard Markdown rendering rewrites relative image sources to /files/ URLs. Add regression coverage proving the rendered URL retains the exact collision-safe selector and that fetching it returns bytes from the selected worktree rather than the launch worktree. Preserve launch-worktree rendering without a selector, standalone exports, absolute/root-relative image sources, and relative-image query strings.

## Planner Guidance

[Issue #47](https://github.com/FuZhiyu/superRA/issues/47) identifies the bypass in [dashboard.js:295](../../../../../skills/task-tree/scripts/templates/dashboard.js#L295): `renderMarkdown()` constructs `/files/` directly instead of routing it through `wtUrl()`. Existing node-backed `renderMarkdown()` tests in [test_dashboard.py:2703-2771](../../../../../skills/task-tree/scripts/test_dashboard.py#L2703-L2771) exercise the rewrite; the two-worktree fixture in [test_dashboard.py:619](../../../../../skills/task-tree/scripts/test_dashboard.py#L619) exercises server-side `WorktreeState` selection. Audit other client-generated `/files/` URLs in the same pass.

## Results

### Outcome

- Live-mode relative Markdown images now route their generated `/files/` URL through `wtUrl()`, preserving `ACTIVE_WT` exactly and reusing its existing percent-encoding and query-string handling ([dashboard.js:291-295](../../../../../skills/task-tree/scripts/templates/dashboard.js#L291-L295)). Standalone rendering and absolute, root-relative, HTTP, and HTTPS image sources remain on their existing branches.
- The cross-worktree regression uses colliding worktree basenames, an encoded selector, distinguishable same-path bytes, and a selected-worktree-only asset. It asserts both the rendered URL and fetched response bytes, while also checking selector-free launch-worktree behavior ([test_dashboard.py:670-752](../../../../../skills/task-tree/scripts/test_dashboard.py#L670-L752)).
- The node-backed `renderMarkdown()` harness now executes `wtUrl()` with the real production functions and covers existing relative-image query strings plus unchanged absolute sources ([test_dashboard.py:2703-2771](../../../../../skills/task-tree/scripts/test_dashboard.py#L2703-L2771)). An audit found no other client-generated `/files/` URLs.

### Protection

- The researcher-confirmed invariant is protected by the cross-worktree regression: the rendered relative-image URL retains the exact encoded collision-disambiguated selector, `/files` returns the selected worktree's distinguishable bytes, a selected-worktree-only asset remains reachable, and an unscoped request returns launch-worktree bytes ([test_dashboard.py:670-753](../../../../../skills/task-tree/scripts/test_dashboard.py#L670-L753)). This is a self-contained end-to-end regression with no numerical tolerance to calibrate; the protection-stage review required no further strengthening beyond the implementation-time image fixtures, selector assertions, and byte checks.
- Fresh red-green verification removed the `wtUrl()` routing call and produced the expected failure at the exact selector assertion; restoring the call made the focused regression pass (`1 passed`).
- The complete task-tree script suite passed with `729 passed, 4 warnings` under `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest -p no:cacheprovider -q skills/task-tree/scripts`. The warnings are two dependency deprecations plus two expected warning-path tests.

**Final diff self-check:** `git diff 2d4c8551629814cab303573322dfde1d26f2a318..HEAD`; the four surviving files/classes are the one-line `wtUrl()` routing fix, byte-distinguishing regression and discoverable test contract, researcher-authorized parent task scope/results record, and this child implementation/protection record. The parent was approved at the base and is retained because issue #47 widened its request-scoping contract; no scope-ambiguous hunk remains. The Project Doc Audit found root [README.md](../../../../../README.md) and [CLAUDE.md](../../../../../CLAUDE.md) current because the fix reuses the existing worktree selector and adds no public interface or contributor protocol.
