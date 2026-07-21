---
title: "HTML Dashboard"
status: in-progress
depends_on:
  - core-data-layer
  - cli-scripts
---

## Objective

Provide a human-friendly dashboard over the `superRA/` task tree: recursive tree navigation with progressive disclosure, DAG (Mermaid) and kanban views, distinctive typography, a professional palette, and dark/light mode.

## Results

The dashboard is a **FastAPI live server** that renders `skills/task-tree/scripts/templates/base.html` plus htmx-swapped partials in a master-detail workspace, with a **standalone-mode render** of the same template for static export. The server-side machinery (routes, SSE broadcast, watcher lifecycle, idle monitor, Jinja render helpers, standalone build, CLI, background supervisor) lives in `skills/task-tree/scripts/plan_dashboard.py`.

What shipped, past the original single-file static HTML the objective first scoped:

- **View navigation** — the master-detail workspace, sidebar tree, breadcrumb, DAG (Mermaid) and kanban surfaces, and client routing.
- **Unified static export** — one template (`base.html`) drives both the live server and the static export via a `window.STANDALONE` branch, replacing the separate static generator.
- **Self-contained export** — the static export base64-embeds figures so a downloaded file is figure-portable offline.
- **Multi-worktree serving** — one server/port per repo resolves any worktree per request via `?wt=<wt_id>`; switching is client navigation, not a server-wide swap.
- **Serve lifecycle** — background-by-default launch with idempotent reuse, idle self-exit, `stop`, and a loopback-default `--host` bind.

Preserved throughout: distinctive typography (Source Serif 4 + IBM Plex Mono via Google Fonts CDN), the warm parchment/ink palette with muted status tints, dark/light mode, progressive disclosure, the DAG/kanban views, and the XSS posture (JSON escaping, `textContent` for DOM writes, controlled markdown-it rewrites).

### Shutdown lifecycle protection

Watcher teardown is bounded under repeated caller cancellation: it gets a cooperative grace period, then a bounded forced-cancellation phase, and finally a process watchdog for a cancellation-suppressing watcher. The watchdog is restricted to a standalone `plan_dashboard.py` process running as `__main__` on its main thread, and late watcher completion disarms it ([plan_dashboard.py:109-111](../../../skills/task-tree/scripts/plan_dashboard.py#L109-L111), [plan_dashboard.py:541-671](../../../skills/task-tree/scripts/plan_dashboard.py#L541-L671)).

Permanent regressions cover both the focused cancellation bounds and two real detached-process cycles with eight concurrent abrupt SSE resets. Each process cycle verifies that the native watcher returns, the child exits, and its port closes before relaunch ([test_dashboard.py:1063-1234](../../../skills/task-tree/scripts/test_dashboard.py#L1063-L1234), [test_dashboard.py:4177-4310](../../../skills/task-tree/scripts/test_dashboard.py#L4177-L4310)). Integration verification passed all five focused lifecycle tests, the 279-test dashboard suite twice, and the 710-test task-tree script suite twice; final bounded closeout shards recorded 708 passes, two unrelated Playwright skips, and no failures or errors.

**Design debt (recorded for a future extraction pass):** `skills/task-tree/scripts/plan_dashboard.py` has grown to ~2,665 lines mixing seven concerns. The background supervisor (~300 lines of PID/daemon logic) and the standalone build (~340 lines) have no FastAPI coupling and are clean extraction candidates, following the precedent of `skills/task-tree/scripts/dashboard_artifact_workflow.py`.

**Integration verification:** the 10 focused scoped-URL and shutdown-lifecycle protection tests passed, followed by the complete task-tree script suite at 714 passed with four expected/dependency warnings.

**Final diff self-check:** `git diff 35fab8110f13eb1b3dab920a1e2c9b0b52dd1e30..HEAD`; surviving change classes are the previously approved bounded shutdown/watchdog lifecycle and release metadata, scoped launch-URL construction and routing regressions, task-tree/main-agent instruction currency, and durable task records. Suspicious hunks were the instruction edits under `skills/*`, retained because the scoped-URL objective requires agents to preserve the emitted canonical selector and each line passes the contributor DRY/Necessity gate; the approved dashboard and postponed docs-site task edits are prior maturation results. No scope-ambiguous hunk remains.
