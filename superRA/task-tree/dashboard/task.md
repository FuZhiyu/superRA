---
title: "HTML Dashboard"
status: in-progress
depends_on:
  - core-data-layer
  - cli-scripts
---

## Objective

Provide a human-friendly dashboard over the `superRA/` task tree: recursive tree navigation with progressive disclosure, DAG (Mermaid) and kanban views, distinctive typography, a professional palette, and dark/light mode — and keep it hardened: task content escaped at one trust boundary, no blocking work on the event loop, no legacy module-global render state, dead rendering paths removed, and assets served locally.

### Context — hardening subtree (2026-07-19)

A full design review (backend `plan_dashboard.py` read line-by-line; frontend `base.html` + partials reviewed by a dispatched agent) produced the hardening work now folded into this task's `## Results`. Researcher decisions that governed it:

- **Scope:** all review findings are in scope — the six priority fixes plus the medium/minor items.
- **Escaping:** titles/section previews render HTML as literal text; markdown bodies keep HTML via DOMPurify.
- **Dead code:** the `/tree` + `/task/{path}` giant-tree subsystem is removed outright.
- **Assets:** all JS/CSS libraries served locally (vendor htmx/sse.js); Google Fonts stay CDN with system-font fallback.

Shared conventions for the subtree: the test-suite invocation and `uv run --script` conventions are in repo `CLAUDE.md` §Local Task-Tree CLI Development (standing context — run both the dashboard and full script suites before reporting); `vendor/` is hand-managed and re-fetched per `vendor/README.md`, never generated; no generated-from-spec artifacts are in scope for these tasks.

Dispatch note: the sibling `nonloopback-host-serve` task (still in flight on its own branch) touches the background-supervisor region of `plan_dashboard.py` — avoid running it in parallel with other work touching that file in one worktree, and coordinate ordering at dispatch time.

## Results

The dashboard is a **FastAPI live server** that renders `skills/task-tree/scripts/templates/base.html` plus htmx-swapped partials in a master-detail workspace, with a **standalone-mode render** of the same template for static export. `base.html` now carries page structure and a small Jinja config block only; its ~1,760 CSS and ~3,000 JS lines live in `dashboard.css`/`dashboard.js`, which the live server serves cacheably (`GET /static/{name}`, SHA-256 ETag + 304) and the standalone export inlines. The server-side machinery (routes, SSE broadcast, watcher lifecycle, idle monitor, Jinja render helpers, standalone build, CLI, background supervisor) lives in `skills/task-tree/scripts/plan_dashboard.py`; the standalone render threads its tree/index/project-root state explicitly through the per-worktree `WorktreeState` seam, with no module-global render state left.

What shipped, past the original single-file static HTML the objective first scoped:

- **View navigation** — the master-detail workspace, sidebar tree, breadcrumb, DAG (Mermaid) and kanban surfaces, and client routing, with exactly one row-rendering path (`nav_node.html`) after the dead pre-master-detail giant-tree subsystem (`GET /tree`, `GET /task/{path}`, and the `task_node.html`/`task_children.html` templates) was removed. The children dependency panel is built from a structured `GET /api/children-graph` JSON payload (nodes + edges taken straight off `Task` data), not regex-parsed mermaid source — so the status→color mapping lives in exactly one place and a task title carrying a literal ` --> ` can no longer corrupt the panel.
- **Unified static export** — one template (`base.html`) drives both the live server and the static export via a `window.STANDALONE` branch, replacing the separate static generator.
- **Self-contained, offline export** — the static export base64-embeds figures and inlines every render library (markdown-it, KaTeX, highlight.js, DOMPurify, texmath, htmx, sse.js) alongside the extracted `dashboard.css`/`dashboard.js`, so a downloaded file renders fully offline; the only network reference is Google Fonts (system-font fallback).
- **Offline-functional live mode** — live mode also loads every render library from the server's own `/static/…` route out of the hand-managed `vendor/` bundle rather than a CDN (htmx and sse.js were vendored to close the last two gaps); a blocked network degrades only typography, never rendering or SSE.
- **Multi-worktree serving** — one server/port per repo resolves any worktree per request via `?wt=<wt_id>`; switching is client navigation, not a server-wide swap.
- **Serve lifecycle** — background-by-default launch with idempotent reuse, idle self-exit, `stop`, and a loopback-default `--host` bind.

Task content is escaped at a single server-side trust boundary: Jinja autoescape is on, titles and section previews render HTML as literal text, and markdown bodies keep full HTML through the client DOMPurify gate. The kanban card wires clicks through a delegated `data-path` handler instead of an interpolated inline `onclick`, and comment-anchor selectors use `CSS.escape` so a `"` in a `##` header no longer aborts comment loading. Client DOM writes continue to go through `textContent`/`escapeHtml` helpers and controlled markdown-it rewrites.

Preserved throughout: distinctive typography (Source Serif 4 + IBM Plex Mono via Google Fonts CDN), the warm parchment/ink palette with muted status tints, dark/light mode, progressive disclosure, and the DAG/kanban views.

### Server robustness

Blocking route work runs off the event loop: `/export`, `/api/worktrees`, `/api/comments/summary`, and the worktree cache-miss path of `resolve_worktree` hand their git-subprocess, tree-walk, render, and base64-encoding cores to `asyncio.to_thread`, while every mutation of shared server state (`_worktree_cache`, client sets, watcher maps) stays on the loop thread — so SSE heartbeats and cheap requests stay responsive during a slow export ([plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py)).

The server fails loudly and keeps its connection bookkeeping truthful. A `task.md` that fails to re-parse during a watcher rebuild logs to stderr and stamps a `parse_error` state — a `badge-error` badge plus a `data-parse-error` attribute on the node ([nav_node.html](../../../skills/task-tree/scripts/templates/nav_node.html)) — instead of silently serving the last-good parse. A slow SSE client whose queue overflows receives a `_QUEUE_CLOSE` sentinel that ends its stream through the normal disconnect path, restoring the invariant the idle monitor depends on: registered queues == open connections. The root-or-children snippet that was duplicated inline is now one shared precompiled `Template`, and the nav-node render helper uses a precompiled template instead of a per-call `env.from_string`.

### Shutdown lifecycle protection

Watcher teardown is bounded under repeated caller cancellation: it gets a cooperative grace period, then a bounded forced-cancellation phase, and finally a process watchdog for a cancellation-suppressing watcher. The watchdog is restricted to a standalone `plan_dashboard.py` process running as `__main__` on its main thread, and late watcher completion disarms it ([plan_dashboard.py:557-672](../../../skills/task-tree/scripts/plan_dashboard.py#L557-L672)).

Permanent regressions cover both the focused cancellation bounds and two real detached-process cycles with eight concurrent abrupt SSE resets; each process cycle verifies the native watcher returns, the child exits, and its port closes before relaunch ([test_dashboard.py:1162-1518](../../../skills/task-tree/scripts/test_dashboard.py#L1162-L1518), [test_dashboard.py:4850](../../../skills/task-tree/scripts/test_dashboard.py#L4850)).

### Reconnect freshness

When a worktree watcher starts after an interval with no connected client, the
server rebuilds that worktree's cached task state before watching for new
changes, then sends a worktree-scoped `full-reload` to the reconnecting SSE
client. Because the client queue is registered before watcher startup, edits
made while the watcher was stopped are visible immediately on reconnect; an
ensure call against an already-live watcher emits no duplicate refresh
([plan_dashboard.py:505-546](../../../skills/task-tree/scripts/plan_dashboard.py#L505-L546)).

Permanent regressions cover the offline edit, refreshed cache, reconnect-stream
notification, duplicate suppression, and cross-worktree broadcast isolation
([test_dashboard.py:1177-1193](../../../skills/task-tree/scripts/test_dashboard.py#L1177-L1193),
[test_dashboard.py:1240-1327](../../../skills/task-tree/scripts/test_dashboard.py#L1240-L1327)).

### Release 0.3.3

The dashboard hardening and worktree image/reconnect fixes are documented in
the dated [0.3.3 release notes](../../../RELEASE-NOTES.md#L5). All maintained
Claude, marketplace, and Codex manifests agree at `0.3.3`, and the release
workflow runs `scripts/bump-version.sh --check` before reading or using the
release version. It also requires exactly one non-empty `0.3.3` section directly
below `Unreleased`, and its release job runs only on `refs/heads/main`. The
workflow therefore remains the sole owner of idempotent `v0.3.3` tag and release
creation after merge
([release.yml:32](../../../.github/workflows/release.yml#L32),
[release.yml:23](../../../.github/workflows/release.yml#L23),
[release.yml:45](../../../.github/workflows/release.yml#L45)).

**Design debt (recorded for a future extraction pass):** `skills/task-tree/scripts/plan_dashboard.py` is ~2,740 lines mixing several concerns. The legacy module-global render state and the `/export` snapshot/restore dance are gone — the standalone render owns its state via `WorktreeState` — and the ~1,760 CSS / ~3,000 JS lines that used to inflate `base.html` now live in separate cacheable files. What remains: the background supervisor (~300 lines of PID/daemon logic) and the standalone build (~340 lines) are FastAPI-decoupled, clean extraction candidates following the `skills/task-tree/scripts/dashboard_artifact_workflow.py` precedent.

**Verification.** The dashboard module passes 308 tests with two dependency warnings, and the full task-tree script suite passes 731 tests with four expected/dependency warnings (`uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`). The consolidated tree and dashboard DAG render correctly, `task check` reports no issues, the durable task passes the Markdown checker, and `git diff --check` is clean. Release verification also confirms synchronized `0.3.3` manifests, a clean version audit, valid workflow YAML and main-ref gating, and exactly one non-empty `0.3.3` notes section directly below `Unreleased`. Each hardening child's merged diff traced cleanly to its objective with no scope-ambiguous hunks, no `skills/*`/`agents/*` instruction edits, and `vendor/` left hand-managed per its `README.md`; per-task red/green and byte-identical-export checks are recorded in this task's git history.

## Review Notes

1. **MAJOR** — The matured release subsection records that the manifests currently agree, but it drops the Protect-selected permanent manifest-consistency guard: the workflow runs `scripts/bump-version.sh --check` before it reads the version ([release.yml:32-33](../../../.github/workflows/release.yml#L32-L33)). Amend [the release subsection](task.md#L70-L79) to state that pre-release guard explicitly and cite it, alongside the retained section-order/uniqueness and main-only tag guards. Protect-selected key results cannot be reduced to a one-time verification fact during maturation.
   → implemented: retained the permanent pre-release manifest check and its
   ordering before version use in the durable release subsection
   ([release.yml:32](../../../.github/workflows/release.yml#L32)).
