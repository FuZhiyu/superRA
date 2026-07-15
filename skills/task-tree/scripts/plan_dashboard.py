#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["fastapi", "uvicorn[standard]", "jinja2", "watchfiles", "pyyaml"]
# ///
"""Live-updating task dashboard server with backward-compatible static generation.

Usage:
    uv run plan_dashboard.py serve [--root superRA/] [--port 8080] [--no-open] [--foreground]
    uv run plan_dashboard.py stop [--root superRA/]
    uv run plan_dashboard.py generate --plan-root PATH [--output PATH]

This is the low-level interface. The user-facing `dashboard` argument delegates
here via cli.py; `generate` is the deprecated alias of `dashboard export`.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import importlib.resources as resources
import json
import os
import re
import signal
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from contextlib import asynccontextmanager
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import AsyncGenerator
from urllib.parse import quote

# ---------------------------------------------------------------------------
# Ensure sibling modules are importable
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))

from _task_io import TASK_ROOT_DIRNAME, Task, _walk_children, collect_all_tasks, parse_task, walk_plan
from _worktree_discovery import (
    _parse_plan_title,
    discover_worktrees,
    filter_worktrees,
    get_git_common_dir,
    sort_worktrees,
)
from task_query import tree_to_json

# ---------------------------------------------------------------------------
# Optional comment module (created by another agent)
# ---------------------------------------------------------------------------
try:
    from _comments import (
        add_comment,
        delete_comment,
        edit_comment,
        load_comments,
        resolve_comment,
    )

    _COMMENTS_AVAILABLE = True
except ImportError:
    _COMMENTS_AVAILABLE = False

# ---------------------------------------------------------------------------
# Module-level state (configured before uvicorn.run)
# ---------------------------------------------------------------------------
PLAN_ROOT: Path = Path(TASK_ROOT_DIRNAME)

# Doc-mode: when True, the live page renders as a documentation site (task-workflow
# chrome suppressed).  Strictly opt-in via `serve --doc-mode`; default off so the
# served dashboard is unchanged.  Read by the index route at render time.
DOC_MODE: bool = False

# Repo identity: a stable hash of the repo's git common dir (or plan root when
# there is no git), reported by /healthz so the launcher's reuse probe can tell
# *our* repo's dashboard from a different repo whose port happens to collide on
# the same hash.  Set from the launcher-supplied ``--repo-id`` (falling back to a
# fresh derivation) before serving; empty until then.
REPO_ID: str = ""

# Default idle timeout: exit after this many continuous seconds with zero open
# SSE connections.  Tests inject a sub-second value either by passing ``timeout``
# straight to ``_idle_monitor`` or by setting ``IDLE_TIMEOUT`` before launch (it is
# read by ``lifespan`` when it creates the monitor task).
IDLE_TIMEOUT: float = 300.0  # 5 minutes

# Heartbeat interval for periodic SSE keep-alive messages.  Must be well under
# IDLE_TIMEOUT so dead connections are pruned before they hold the server open.
HEARTBEAT_INTERVAL: float = 20.0  # seconds

# Cooperative watchfiles shutdown normally completes promptly after its stop
# event is set.  Bound that grace period so a stuck native watcher cannot hold
# Uvicorn's ASGI response/lifespan shutdown open forever; after this interval
# _stop_watcher falls back to task cancellation.
WATCHER_STOP_TIMEOUT: float = 2.0
WATCHER_CANCEL_TIMEOUT: float = 0.5
WATCHER_PROCESS_EXIT_TIMEOUT: float = 0.5

# Handle to the running uvicorn.Server instance so the idle monitor can request
# shutdown by setting server.should_exit = True.  Set in serve().
_server: "uvicorn.Server | None" = None  # type: ignore[name-defined]

# Immutable process ownership: executing this entry script owns the auxiliary
# dashboard process; importing it into pytest or another ASGI host does not.
_standalone_process_owner = __name__ == "__main__"

# In-memory task tree and flat index.  These are a compatibility view over the
# *default* (launch) worktree's WorktreeState — read by /export's snapshot path
# and the standalone renderer.  Per-request handlers resolve a WorktreeState
# instead of reading these.
_root_task: Task | None = None
_task_index: dict[str, Task] = {}
_project_root: str = ""

# Per-worktree SSE delivery and watcher lifecycle (task 02).
#
# Live-reload is scoped per worktree: a client viewing worktree A registers its
# queue under A and a watcher for A runs only while A has at least one client.
# ``_worktree_clients`` maps worktree id -> the queues of clients viewing it;
# ``_worktree_watchers`` maps worktree id -> the awatch task feeding that set;
# ``_worktree_stop_events`` maps worktree id -> the cooperative-stop Event handed
# to that task's ``awatch``; setting it lets watchfiles close its native
# fsevents thread/fd on its own terms instead of leaking it past a hard cancel;
# ``_worktree_locks`` serializes each worktree's spawn/teardown so a connect and
# a disconnect cannot race the watcher in or out from under each other.  These
# locks are separate from task 01's per-state build lock.
_worktree_clients: dict[str, set[asyncio.Queue[str]]] = {}
_worktree_watchers: dict[str, asyncio.Task] = {}
_worktree_stop_events: dict[str, asyncio.Event] = {}
_worktree_locks: dict[str, asyncio.Lock] = {}


# ---------------------------------------------------------------------------
# Per-worktree state model
# ---------------------------------------------------------------------------
# The dashboard serves any discovered worktree on demand.  Each worktree's
# render state (its task tree, flat index, project root, and plan root) lives in
# a WorktreeState; a request resolves to one via its ``?wt=<name>`` query param,
# defaulting to the launch worktree.  ``_worktree_cache`` is keyed by worktree id
# (the canonical selector token returned by ``_worktree_id_for_plan_root``).


@dataclass
class WorktreeState:
    """Per-worktree render state, replacing the former module singletons."""

    wt_id: str
    plan_root: Path
    project_root: str
    root_task: Task | None = None
    task_index: dict[str, Task] = field(default_factory=dict)


# worktree id -> WorktreeState, built lazily on first request for a worktree.
_worktree_cache: dict[str, WorktreeState] = {}

# The launch worktree id: the worktree the server started in, used as the
# default when a request carries no ``?wt=``.
_launch_wt_id: str = ""


def _worktree_id_for_plan_root(plan_root: Path) -> str:
    """Canonical worktree id for a plan root = the id the selector addresses it by.

    The worktree dir is the plan root's parent (the plan root is ``<wt>/superRA``),
    so the id is normally that directory's basename.  But when two discovered
    worktrees share a basename, ``_discovered_worktree_map()`` registers each under
    a disambiguated longest-unique-suffix key instead of the bare basename.  To
    keep the launch worktree's cache key, its ``?wt=`` selector token, and the
    resolver's default-short-circuit all in agreement, return the same key the map
    uses for this plan root when discovery knows it; fall back to the bare basename
    when discovery has no entry (no git repo / standalone).
    """
    resolved = plan_root.resolve()
    for wt_id, mapped in _discovered_worktree_map().items():
        if mapped.resolve() == resolved:
            return wt_id
    return resolved.parent.name


def _dashboard_url(port: int, plan_root: Path) -> str:
    """Return the live URL scoped to *plan_root*'s canonical selector token."""
    wt_id = quote(_worktree_id_for_plan_root(plan_root), safe="")
    return f"http://localhost:{port}/?wt={wt_id}"


def _build_worktree_state(wt_id: str, plan_root: Path) -> WorktreeState:
    """Walk *plan_root* and return a fully populated WorktreeState."""
    state = WorktreeState(
        wt_id=wt_id,
        plan_root=plan_root,
        project_root=str(plan_root.resolve().parent),
    )
    state.root_task = walk_plan(plan_root)
    _build_index(state.root_task, state.task_index)
    return state


def _sync_default_globals() -> None:
    """Mirror the launch worktree's state into the legacy module globals.

    ``/export`` snapshots these globals around a standalone render, and the
    standalone renderer drives them directly; the test suite also reads them.
    Keeping them as a view over the default WorktreeState preserves that path.
    """
    state = _worktree_cache.get(_launch_wt_id)
    if state is not None:
        _set_module_state(state.root_task, state.task_index, state.project_root)


# ---------------------------------------------------------------------------
# Data layer
# ---------------------------------------------------------------------------


def _build_index(task: Task, index: dict[str, Task]) -> None:
    """Recursively populate a flat path -> Task index."""
    index[task.path] = task
    for child in task.children:
        _build_index(child, index)


def rebuild_tree() -> None:
    """Full re-walk of the launch plan directory; (re)seed the default worktree.

    Rebuilds the launch worktree's WorktreeState from ``PLAN_ROOT`` and mirrors
    it into the legacy globals.  Tests and the CLI seed the cache through here.
    """
    global _launch_wt_id
    _launch_wt_id = _worktree_id_for_plan_root(PLAN_ROOT)
    _worktree_cache[_launch_wt_id] = _build_worktree_state(_launch_wt_id, PLAN_ROOT)
    _sync_default_globals()


def rebuild_state_task(state: WorktreeState, task_path: str) -> tuple[Task | None, bool]:
    """Re-parse a single task.md within *state* and update its index.

    Returns ``(updated_task, children_changed)``.  *updated_task* is ``None``
    when the file no longer exists.  *children_changed* is ``True`` when child
    directories were added or removed since the last index snapshot, signalling
    the caller to broadcast a full-reload instead of a single-task fragment.
    """
    task_dir = state.plan_root / task_path if task_path else state.plan_root
    task_md = task_dir / "task.md"
    if not task_md.exists():
        state.task_index.pop(task_path, None)
        return None, False
    try:
        updated = parse_task(task_md, state.plan_root)
    except Exception:
        return state.task_index.get(task_path), False

    # --- Re-discover children from the filesystem ---
    existing = state.task_index.get(task_path)
    old_child_paths: set[str] = set()
    if existing is not None:
        old_child_paths = {c.path for c in existing.children}

    # Walk current child subdirectories that contain a task.md
    new_children = _walk_children(task_dir, state.plan_root)
    new_child_paths = {c.path for c in new_children}

    children_changed = new_child_paths != old_child_paths

    updated.children = new_children

    # Update the flat index: register the task itself and all discovered
    # children; remove entries for children that no longer exist.
    state.task_index[task_path] = updated
    for gone_path in old_child_paths - new_child_paths:
        _remove_from_index(state.task_index, gone_path)
    for child in new_children:
        _build_index(child, state.task_index)

    # Patch the node inside the tree so the parent's reference stays valid
    _replace_node_in_tree(state.root_task, task_path, updated)
    return updated, children_changed


def rebuild_task(task_path: str) -> tuple[Task | None, bool]:
    """Re-parse a single task.md in the launch worktree (legacy-globals view)."""
    state = _worktree_cache.get(_launch_wt_id)
    if state is None:
        return None, False
    result = rebuild_state_task(state, task_path)
    _sync_default_globals()
    return result


def _remove_from_index(index: dict[str, Task], task_path: str) -> None:
    """Remove a task and all its descendants from a flat index."""
    task = index.pop(task_path, None)
    if task is not None:
        for child in task.children:
            _remove_from_index(index, child.path)


def _replace_node_in_tree(node: Task | None, target_path: str, replacement: Task) -> bool:
    """Walk the tree and swap out the node whose path matches *target_path*."""
    if node is None:
        return False
    for i, child in enumerate(node.children):
        if child.path == target_path:
            node.children[i] = replacement
            return True
        if _replace_node_in_tree(child, target_path, replacement):
            return True
    return False


def _find_task(state: WorktreeState, path: str) -> Task | None:
    """O(1) task lookup by path within a worktree state."""
    return state.task_index.get(path)


# ---------------------------------------------------------------------------
# SSE helpers
# ---------------------------------------------------------------------------


async def _broadcast(event: str, data: str, wt: str) -> None:
    """Send an SSE-formatted message to every client viewing worktree *wt*.

    Multi-line data is handled per SSE spec: each line gets a ``data:`` prefix.
    Scoped to *wt*'s client set: a broadcast for one worktree never reaches a
    client viewing another.  A broadcast for a worktree with no current clients
    (e.g. the last client left between the watcher firing and this call) is a
    safe no-op via ``dict.get(wt, set())``.
    """
    data_lines = "".join(f"data: {line}\n" for line in data.split("\n"))
    message = f"event: {event}\n{data_lines}\n"
    clients = _worktree_clients.get(wt, set())
    dead: list[asyncio.Queue[str]] = []
    for q in clients:
        try:
            q.put_nowait(message)
        except asyncio.QueueFull:
            dead.append(q)
    for q in dead:
        clients.discard(q)


# ---------------------------------------------------------------------------
# Watcher rebuild-and-render-fragment hook (per-worktree)
# ---------------------------------------------------------------------------
# The watcher rebuilds/evicts a worktree's WorktreeState and renders the
# broadcast fragments from that state, not from module globals.  Task 02 owns
# the per-worktree watcher lifecycle and delivery; it reuses this body and just
# parameterizes which worktree it operates on.


async def _rebuild_and_broadcast(state: WorktreeState, changes) -> None:
    """Apply a batch of filesystem *changes* to *state* and broadcast fragments.

    *changes* is a ``watchfiles`` change set scoped to ``state.plan_root``.
    Renders the ``full-reload`` / ``summary-updated`` / ``task:<path>`` fragments
    from *state* so the rebuild-and-render path is worktree-scoped throughout.
    """
    import watchfiles

    # Paths of tasks whose parent needs re-rendering (structural changes)
    structural_parent_paths: set[str] = set()
    changed_paths: set[str] = set()

    for change_type, file_path_str in changes:
        fp = Path(file_path_str)
        name = fp.name

        if name not in ("task.md", "comments.yaml"):
            continue

        task_dir = fp.parent
        try:
            rel = task_dir.relative_to(state.plan_root)
            task_path = str(rel) if str(rel) != "." else ""
        except ValueError:
            continue

        if change_type == watchfiles.Change.added:
            if name == "task.md":
                # Parent of the new task needs re-rendering
                parent_path = str(Path(task_path).parent) if task_path else ""
                if parent_path == ".":
                    parent_path = ""
                structural_parent_paths.add(parent_path)
        elif change_type == watchfiles.Change.deleted:
            if name == "task.md":
                parent_path = str(Path(task_path).parent) if task_path else ""
                if parent_path == ".":
                    parent_path = ""
                structural_parent_paths.add(parent_path)
        else:
            changed_paths.add(task_path)

    if structural_parent_paths:
        # A task dir was added or deleted: the tree shape changed. The
        # master-detail client rebuilds its whole sidebar and restores
        # activePath on full-reload, so a single full-reload is both the
        # correct and the simplest signal here — no per-parent fragment
        # juggling, no descendant fold/highlight to preserve by hand.
        rebuild_worktree_state(state.wt_id)
        await _broadcast("full-reload", "{}", state.wt_id)
        if state.root_task is not None:
            summary_html = _render_summary(state.root_task)
            await _broadcast("summary-updated", summary_html, state.wt_id)

    # Process content-only changes (skip paths already covered by the
    # structural full-reload above).
    content_paths = changed_paths - structural_parent_paths
    if content_paths:
        any_children_changed = False

        for task_path in content_paths:
            updated, children_changed = rebuild_state_task(state, task_path)
            if children_changed:
                # A task.md edit that changes this task's own child set is
                # structural too — let the client rebuild the sidebar.
                any_children_changed = True
            elif updated is not None and state.root_task is not None:
                # Pure content edit: swap the body-free sidebar row. The
                # client's active-card / children-DAG refresh keys off the
                # event name, not this fragment, so a nav (no-body) row is
                # the cheap, correct payload for the declarative sse-swap.
                fragment = _render_nav_node(updated)
                await _broadcast(f"task:{task_path}", fragment, state.wt_id)

        if any_children_changed:
            rebuild_worktree_state(state.wt_id)
            await _broadcast("full-reload", "{}", state.wt_id)

        if content_paths and state.root_task is not None:
            summary_html = _render_summary(state.root_task)
            await _broadcast("summary-updated", summary_html, state.wt_id)


def rebuild_worktree_state(wt_id: str) -> WorktreeState | None:
    """Rebuild (or evict) the cached WorktreeState for *wt_id*.

    Re-walks the worktree's plan root and refreshes its cached state in place so
    handlers and the watcher see the new tree.  Returns the refreshed state, or
    ``None`` when the worktree is no longer cached.  Mirrors the launch worktree
    into the legacy globals so ``/export`` and the standalone renderer stay
    consistent.  This is the cache-invalidation hook task 02's watcher calls.
    """
    existing = _worktree_cache.get(wt_id)
    if existing is None:
        return None
    refreshed = _build_worktree_state(wt_id, existing.plan_root)
    # Refresh in place so any handler/watcher holding the same object sees it.
    existing.root_task = refreshed.root_task
    existing.task_index = refreshed.task_index
    existing.project_root = refreshed.project_root
    if wt_id == _launch_wt_id:
        _sync_default_globals()
    return existing


# ---------------------------------------------------------------------------
# Filesystem watcher (watchfiles + debounce)
# ---------------------------------------------------------------------------


async def _watch_worktree(wt: str, stop_event: asyncio.Event) -> None:
    """Background coroutine: watch worktree *wt* for task.md changes.

    Watches that worktree's ``plan_root`` and routes each change batch through
    the worktree-scoped ``_rebuild_and_broadcast`` hook, which rebuilds *wt*'s
    WorktreeState and broadcasts the fragments to *wt*'s clients only.  The
    change-detection logic itself lives in ``_rebuild_and_broadcast``; this
    coroutine only parameterizes which worktree's root it watches.

    ``stop_event`` is handed straight to ``awatch`` so teardown is cooperative:
    setting it lets the watch loop reach its clean ``return``, which runs
    watchfiles' ``RustNotify.__exit__`` and closes the native fsevents
    thread/fd.  A hard ``task.cancel()`` instead unwinds the Python generator
    without that exit, orphaning the native thread; the orphaned fsevents source
    keeps the event loop's kqueue perpetually readable and spins the loop at
    full CPU after every disconnect.
    """
    import watchfiles

    state = _worktree_cache.get(wt)
    if state is None:
        return

    async for changes in watchfiles.awatch(state.plan_root, stop_event=stop_event):
        # watchfiles already debounces (default 1600ms); the sleep adds a
        # short extra window so rapid back-to-back writes coalesce.
        await asyncio.sleep(0.2)
        await _rebuild_and_broadcast(state, changes)


# ---------------------------------------------------------------------------
# Per-worktree watcher lifecycle
# ---------------------------------------------------------------------------
# A watcher for a worktree runs only while that worktree has at least one
# connected client.  ``_ensure_watcher`` is called by ``/events`` after the new
# client's queue is registered (so no early change event is lost to a
# watcher-init race); ``_stop_watcher`` is called when the last client leaves.
# Both run under that worktree's ``_worktree_locks`` entry so a concurrent
# connect and disconnect cannot spawn a duplicate watcher or tear a live one
# down.


def _worktree_lock(wt: str) -> asyncio.Lock:
    """Return (creating on first use) the spawn/teardown lock for *wt*."""
    lock = _worktree_locks.get(wt)
    if lock is None:
        lock = asyncio.Lock()
        _worktree_locks[wt] = lock
    return lock


async def _ensure_watcher(wt: str) -> None:
    """Start the watcher for *wt* if one is not already running.

    A present-but-``done()`` task (a watcher that finished or crashed) is treated
    as absent and respawned, so a dead watcher is never silently reused.
    """
    async with _worktree_lock(wt):
        existing = _worktree_watchers.get(wt)
        if existing is not None and not existing.done():
            return
        # Fresh stop event per spawn: a respawn after a crashed/finished watcher
        # must start with an unset event so the new watch loop is not torn down
        # by a stale signal from the prior generation.
        stop_event = asyncio.Event()
        _worktree_stop_events[wt] = stop_event
        _worktree_watchers[wt] = asyncio.create_task(_watch_worktree(wt, stop_event))


def _is_benign_awatch_teardown_race(exc: BaseException) -> bool:
    """True for watchfiles' benign ``awatch`` teardown-race artifact only.

    When ``awatch`` is torn down by its ``stop_event`` while the awaiting
    context is itself unwinding, watchfiles' own ``anyio`` task group can exit
    with ``UnboundLocalError: ... 'raw_changes'`` (the loop's ``raw_changes`` is
    unbound when the task group's ``__aexit__`` raises).  By the time this
    surfaces the native fd is already closed, so it is safe to swallow — but
    *only* this exact leaf, never a genuine watcher fault.
    """
    return isinstance(exc, UnboundLocalError) and "raw_changes" in str(exc)


def _schedule_forced_process_exit(delay: float) -> threading.Timer | None:
    """Guarantee exit when a cancellation-suppressing watcher cannot unwind.

    The dashboard is an auxiliary, non-persistent process.  Once both bounded
    watcher teardown phases fail, a daemon watchdog is safer than allowing an
    orphaned CPU-spinning process to survive indefinitely.  The delay lets the
    current ASGI response and lifespan make their normal exit attempt first.
    Only the foreground CLI context owns its process. Direct ``serve()`` calls,
    embedded ASGI hosts, and servers running outside the main thread must not arm
    a process-level exit.
    """
    if (
        not _standalone_process_owner
        or threading.current_thread() is not threading.main_thread()
    ):
        return None

    timer = threading.Timer(delay, os._exit, args=(0,))
    timer.daemon = True
    timer.start()
    return timer


async def _stop_watcher(wt: str) -> None:
    """Cooperatively stop and remove the watcher for *wt* (last client left).

    Sets the worktree's ``awatch`` stop event instead of cancelling the task, so
    the watch loop reaches its clean ``return`` and watchfiles closes the native
    fsevents thread/fd.  Cancelling instead orphaned that native thread and left
    the event loop spinning on a perpetually-readable kqueue (see
    ``_watch_worktree``).

    The stop event gets a bounded grace period to release native resources. If
    the watcher does not finish, task cancellation gets a second bounded wait so
    neither the disconnecting response nor lifespan shutdown can wait forever.
    A cancellation-suppressing task triggers a delayed process-exit watchdog.
    Genuine watcher crashes still propagate when they finish within those
    bounds; a later failure is reported through the loop's exception handler.
    The one thing swallowed is watchfiles' own *benign* teardown race: when this
    runs from inside the disconnecting SSE generator's ``finally`` (the common
    case), ``awatch`` raises
    ``UnboundLocalError: ... 'raw_changes'`` from its ``anyio`` task group as it
    exits (either bare or wrapped in a ``BaseExceptionGroup``).  By then the
    watcher is gone and its native fd is closed, so that specific leaf is not
    actionable; swallow only it (so it does not propagate into the ASGI response
    teardown as a noisy 500-style traceback on every disconnect) and re-raise
    anything else, so a real watcher crash is never hidden.
    """
    async with _worktree_lock(wt):
        task = _worktree_watchers.pop(wt, None)
        stop_event = _worktree_stop_events.pop(wt, None)
    if task is not None:
        if stop_event is not None:
            stop_event.set()

        # Give awatch a bounded cooperative grace period.  Disconnect and
        # graceful-shutdown cancellation belongs to the ASGI caller, so consume
        # repeated cancellation here without forwarding it to the watcher, then
        # propagate it after teardown.  If the stop event does not finish the
        # watcher in time, hard cancellation is the bounded fallback that lets
        # Uvicorn complete instead of waiting forever.
        caller_cancelled = False
        loop = asyncio.get_running_loop()
        deadline = loop.time() + WATCHER_STOP_TIMEOUT
        while not task.done() and loop.time() < deadline:
            remaining = deadline - loop.time()
            try:
                done, _ = await asyncio.wait({task}, timeout=remaining)
            except asyncio.CancelledError:
                caller_cancelled = True
                continue
            if done:
                break

        if not task.done():
            task.cancel()

        cancel_deadline = loop.time() + WATCHER_CANCEL_TIMEOUT
        while not task.done() and loop.time() < cancel_deadline:
            remaining = cancel_deadline - loop.time()
            try:
                done, _ = await asyncio.wait({task}, timeout=remaining)
            except asyncio.CancelledError:
                caller_cancelled = True
                continue
            if done:
                break

        if not task.done():
            # _watch_worktree does not suppress CancelledError, so real awatch
            # normally completes above.  A cancellation-suppressing replacement
            # cannot be killed by asyncio; schedule a process watchdog so it
            # cannot strand this auxiliary dashboard during loop shutdown.
            watchdog = _schedule_forced_process_exit(WATCHER_PROCESS_EXIT_TIMEOUT)

            def _observe_late_completion(done_task: asyncio.Task) -> None:
                if watchdog is not None:
                    watchdog.cancel()
                try:
                    done_task.result()
                except asyncio.CancelledError:
                    pass
                except BaseException as exc:  # noqa: BLE001 - report to loop
                    loop.call_exception_handler(
                        {
                            "message": "watcher failed after teardown timeout",
                            "exception": exc,
                            "task": done_task,
                        }
                    )

            task.add_done_callback(_observe_late_completion)
            if caller_cancelled:
                raise asyncio.CancelledError
            return

        try:
            task.result()
        except asyncio.CancelledError:
            # Intentional timeout fallback or event-loop shutdown.
            pass
        except BaseExceptionGroup as eg:
            _, rest = eg.split(_is_benign_awatch_teardown_race)
            if rest is not None:
                raise rest
        except BaseException as exc:  # noqa: BLE001 - re-raised unless benign
            if not _is_benign_awatch_teardown_race(exc):
                raise

        if caller_cancelled:
            raise asyncio.CancelledError


# ---------------------------------------------------------------------------
# Idle-shutdown monitor
# ---------------------------------------------------------------------------


def _open_connection_count() -> int:
    """Return the total number of live SSE connections across all worktrees."""
    return sum(len(s) for s in _worktree_clients.values())


def _should_idle_exit(open_count: int, idle_seconds: float, timeout: float) -> bool:
    """Return True when the server should shut down due to idleness.

    Keeps the shutdown decision separable from wall-clock so tests can drive
    it with a synthetic elapsed value.
    """
    return open_count == 0 and idle_seconds >= timeout


async def _idle_monitor(timeout: float = IDLE_TIMEOUT, poll: float = 1.0) -> None:
    """Monitor coroutine: request server shutdown after *timeout* idle seconds.

    "Idle" means zero open SSE connections summed across all worktrees.  The
    timer starts immediately (the server has zero connections at launch) and
    resets whenever at least one connection is open.  Once the elapsed-zero
    duration reaches *timeout*, sets ``_server.should_exit = True`` to trigger
    uvicorn's normal graceful shutdown, which runs the lifespan exit path and
    cancels all watchers.

    *poll* controls how often the count is sampled; it does not affect the
    timer's resolution beyond that granularity.
    """
    idle_elapsed: float = 0.0
    while True:
        await asyncio.sleep(poll)
        count = _open_connection_count()
        if count > 0:
            idle_elapsed = 0.0
        else:
            idle_elapsed += poll
        if _should_idle_exit(count, idle_elapsed, timeout):
            if _server is not None:
                _server.should_exit = True
            return


# ---------------------------------------------------------------------------
# Jinja2 rendering helpers
# ---------------------------------------------------------------------------

_jinja_env = None


def _get_jinja_env():
    """Lazy-init and return the Jinja2 environment."""
    global _jinja_env
    if _jinja_env is not None:
        return _jinja_env

    from jinja2 import Environment, FileSystemLoader, PackageLoader

    if __package__:
        loader = PackageLoader(__package__, "templates")
    else:
        templates_dir = Path(__file__).parent / "templates"
        loader = FileSystemLoader(str(templates_dir))
    env = Environment(
        loader=loader,
        autoescape=False,
    )

    def vscode_link(path: str, project_root: str) -> str:
        """Rewrite a relative file path to a vscode:// URI."""
        abs_path = Path(project_root) / path
        return f"vscode://file/{abs_path}"

    def file_url(path: str) -> str:
        """Rewrite an image path to the /files/ route."""
        return f"/files/{path}"

    env.filters["vscode_link"] = vscode_link
    env.filters["file_url"] = file_url

    _jinja_env = env
    return env


def _render_task_fragment(task: Task, project_root: str) -> str:
    """Render the task_children.html template for a single task."""
    env = _get_jinja_env()
    template = env.get_template("task_children.html")
    return template.render(task=task, project_root=project_root)


def _task_depth(task_path: str) -> int:
    """Return the depth of a task in the tree (0 for root children, etc.)."""
    if not task_path:
        return 0
    return task_path.count("/")


def _render_task_node(task: Task, project_root: str | None = None, depth: int | None = None) -> str:
    """Render a single task node via the task_node macro (for SSE swap).

    *depth* controls how many levels of children are rendered inline vs
    lazy-loaded.  When ``None``, the depth is inferred from the task's
    position in the tree (``task.path``).
    """
    if depth is None:
        depth = _task_depth(task.path)
    if project_root is None:
        project_root = _project_root
    env = _get_jinja_env()
    template = env.from_string(
        '{%- from "task_node.html" import render_task_node -%}'
        '{{ render_task_node(task, project_root, depth=depth) }}'
    )
    return template.render(task=task, project_root=project_root, depth=depth)


def _render_nav_node(task: Task, depth: int | None = None) -> str:
    """Render a single navigation-only task node (row + children, no body).

    *depth* controls inline vs lazy-loaded children, mirroring
    ``_render_task_node``.  When ``None``, depth is inferred from ``task.path``.
    """
    if depth is None:
        depth = _task_depth(task.path)
    env = _get_jinja_env()
    template = env.from_string(
        '{%- from "nav_node.html" import render_nav_node -%}'
        '{{ render_nav_node(task, depth=depth) }}'
    )
    return template.render(task=task, depth=depth)


def _render_nav_children(task: Task) -> str:
    """Render the nav_children.html fragment (body-free children) for a task."""
    env = _get_jinja_env()
    template = env.get_template("nav_children.html")
    return template.render(task=task)


def _render_node_body(task: Task, project_root: str | None = None) -> str:
    """Render the node_body.html fragment (body-only) for a single task."""
    if project_root is None:
        project_root = _project_root
    env = _get_jinja_env()
    template = env.get_template("node_body.html")
    return template.render(task=task, project_root=project_root)


def _render_summary(root_task: Task | None = None) -> str:
    """Render the summary_bar.html template for *root_task*'s tree."""
    if root_task is None:
        root_task = _root_task
    env = _get_jinja_env()
    template = env.get_template("summary_bar.html")
    all_tasks = collect_all_tasks(root_task) if root_task else []
    return template.render(root_task=root_task, all_tasks=all_tasks)


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: seed the launch worktree and start the idle monitor.
    Shutdown: cancel the monitor and every watcher.

    Watchers are no longer spawned at startup — each worktree's watcher starts on
    its first ``/events`` client and stops when the last leaves.  Shutdown cancels
    every per-worktree watcher still running, not just one.

    The idle monitor runs as a single background coroutine for the whole process;
    it sets ``_server.should_exit`` once the server has been idle for
    ``IDLE_TIMEOUT`` seconds, triggering uvicorn's normal graceful shutdown (which
    re-enters this context at the ``yield`` and cancels all watchers).
    """
    rebuild_tree()
    monitor_task = asyncio.create_task(_idle_monitor(timeout=IDLE_TIMEOUT))
    try:
        yield
    finally:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        for wt in list(_worktree_watchers):
            await _stop_watcher(wt)


app = FastAPI(lifespan=lifespan)


@app.get("/healthz")
async def healthz():
    """Identity probe the launcher uses to reuse an already-running dashboard.

    Reuse must not depend on the PID file alone: a server started in
    ``--foreground`` console mode writes none, and a background server's file
    can be lost or stale while the process is very much alive.  This endpoint
    lets the launcher confirm a *superRA dashboard* is the thing bound to the
    repo port, recover its PID (to repair the PID file), match serve mode so a
    task-mode launch never reuses a ``--doc-mode`` site (or vice versa), and
    match repo identity so a different repo colliding on the same hashed port is
    never silently adopted (which would root its dashboard at our tree and let
    its ``stop`` kill our server).
    """
    return {
        "service": "superra-dashboard",
        "pid": os.getpid(),
        "doc_mode": DOC_MODE,
        "repo_id": REPO_ID,
    }


# ---------------------------------------------------------------------------
# Per-request worktree resolution
# ---------------------------------------------------------------------------


def _discovered_worktree_map() -> dict[str, Path]:
    """Map worktree id (directory basename) -> plan root Path for every
    discovered worktree that has a task tree.

    On a basename collision between two discovered worktrees, neither bare
    basename is registered; the longest-unique-suffix forms are registered
    instead so a caller can still name each unambiguously.
    """
    plan_roots: list[Path] = []
    for w in discover_worktrees():
        if w.plan_root is not None:
            plan_roots.append(Path(w.plan_root))

    by_id: dict[str, list[Path]] = {}
    for pr in plan_roots:
        by_id.setdefault(pr.resolve().parent.name, []).append(pr)

    result: dict[str, Path] = {}
    for wt_id, roots in by_id.items():
        if len(roots) == 1:
            result[wt_id] = roots[0]
        else:
            # Basename collision: register each by its longest-unique-suffix of
            # path segments so every colliding worktree stays addressable.
            for pr in roots:
                segments = pr.resolve().parent.parts
                for depth in range(1, len(segments) + 1):
                    suffix = "/".join(segments[-depth:])
                    if not any(
                        other is not pr
                        and "/".join(other.resolve().parent.parts).endswith(suffix)
                        for other in roots
                    ):
                        result[suffix] = pr
                        break
    return result


def resolve_worktree(request: Request) -> WorktreeState:
    """Resolve the WorktreeState a request targets via its ``?wt=<name>`` param.

    Falls back to the launch worktree when ``?wt=`` is absent (preserving today's
    behavior and standalone export).  Builds and caches a worktree's state lazily
    on first use.  Raises 404 only when ``?wt=`` names a value that is neither the
    launch worktree nor any discovered worktree.
    """
    wt_name = request.query_params.get("wt")
    if not wt_name or wt_name == _launch_wt_id:
        state = _worktree_cache.get(_launch_wt_id)
        if state is None:
            raise HTTPException(status_code=500, detail="Task tree not initialized")
        return state

    cached = _worktree_cache.get(wt_name)
    if cached is not None:
        return cached

    plan_root = _discovered_worktree_map().get(wt_name)
    if plan_root is None:
        raise HTTPException(status_code=404, detail=f"Unknown worktree: {wt_name}")

    state = _build_worktree_state(wt_name, plan_root)
    _worktree_cache[wt_name] = state
    return state


# --- Route: GET / ----------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the full dashboard page."""
    state = resolve_worktree(request)
    if state.root_task is None:
        raise HTTPException(status_code=500, detail="Task tree not initialized")
    env = _get_jinja_env()
    template = env.get_template("base.html")
    all_tasks = collect_all_tasks(state.root_task)
    # The page is bound to the resolved worktree: the client carries ``wt_id`` as
    # ``?wt=`` on every server fetch and on its SSE connect, and PROJECT_ROOT
    # (the VS Code link base) follows it.  Empty for the launch worktree so the
    # default URL stays clean (``/`` with no ``?wt=``).
    wt_id = "" if state.wt_id == _launch_wt_id else state.wt_id
    resolved_root = str(state.plan_root.resolve())
    html = template.render(
        root_task=state.root_task,
        all_tasks=all_tasks,
        project_root=state.project_root,
        resolved_root=resolved_root,
        root_prefix=Path(resolved_root).name,
        wt_id=wt_id,
        doc_mode=DOC_MODE,
        search_index=_build_search_index(state.root_task, all_tasks),
    )
    return HTMLResponse(content=html)


# --- Route: GET /tree (tree HTML fragment for AJAX full-reload fallback) ----

@app.get("/tree", response_class=HTMLResponse)
async def tree_fragment(request: Request):
    """Return just the task tree HTML nodes (no page chrome)."""
    state = resolve_worktree(request)
    if state.root_task is None:
        raise HTTPException(status_code=500, detail="Task tree not initialized")
    env = _get_jinja_env()
    # Re-use the same rendering logic as base.html: if root has body, render
    # it as a node; otherwise render its children at depth 0.
    template = env.from_string(
        '{%- from "task_node.html" import render_task_node -%}'
        '{% if root_task.body and root_task.body.strip() %}'
        '{{ render_task_node(root_task, project_root, depth=0) }}'
        '{% else %}'
        '{% for child in root_task.children %}'
        '{{ render_task_node(child, project_root, depth=0) }}'
        '{% endfor %}'
        '{% endif %}'
    )
    html = template.render(root_task=state.root_task, project_root=state.project_root)
    return HTMLResponse(content=html)


# --- Route: GET /nav (navigation-only tree fragment) -----------------------

@app.get("/nav", response_class=HTMLResponse)
async def nav_fragment(request: Request):
    """Return the navigation-only tree (rows, no task bodies) for the sidebar.

    Mirrors /tree's root-or-children logic but renders nav_node (body-free).
    Children are inlined to depth 2; depth >=3 children are lazy-load stubs
    fetched via /nav/{path}.
    """
    state = resolve_worktree(request)
    if state.root_task is None:
        raise HTTPException(status_code=500, detail="Task tree not initialized")
    env = _get_jinja_env()
    template = env.from_string(
        '{%- from "nav_node.html" import render_nav_node -%}'
        '{% if root_task.body and root_task.body.strip() %}'
        '{{ render_nav_node(root_task, depth=0) }}'
        '{% else %}'
        '{% for child in root_task.children %}'
        '{{ render_nav_node(child, depth=0) }}'
        '{% endfor %}'
        '{% endif %}'
    )
    html = template.render(root_task=state.root_task)
    return HTMLResponse(content=html)


# --- Route: GET /events (SSE) ---------------------------------------------

@app.get("/events")
async def sse_events(request: Request):
    """Server-Sent Events endpoint for live updates, scoped to one worktree.

    The worktree is resolved from ``?wt=`` (task 01's resolver; default = launch
    worktree).  The client's queue is registered under that worktree *before* its
    watcher is ensured, so no change emitted during watcher startup is lost.  On
    disconnect the queue is removed and, if it was the worktree's last client,
    its watcher is stopped.
    """
    wt = resolve_worktree(request).wt_id

    async def event_generator() -> AsyncGenerator[str, None]:
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=256)
        # Register before ensuring the watcher so the queue cannot miss an early
        # event (watcher-init race).
        _worktree_clients.setdefault(wt, set()).add(queue)
        await _ensure_watcher(wt)
        try:
            # Send an initial heartbeat so the connection is established.
            yield ": heartbeat\n\n"
            while True:
                try:
                    # Wait up to HEARTBEAT_INTERVAL for an event; if none
                    # arrives, send a periodic heartbeat.  Writing to a dead
                    # connection raises so the generator falls through to
                    # ``finally`` and removes the queue, keeping the count
                    # accurate for the idle monitor.
                    message = await asyncio.wait_for(
                        queue.get(), timeout=HEARTBEAT_INTERVAL
                    )
                    yield message
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
        finally:
            clients = _worktree_clients.get(wt)
            if clients is not None:
                clients.discard(queue)
                if not clients:
                    _worktree_clients.pop(wt, None)
                    await _stop_watcher(wt)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# --- Route: GET /dag ---------------------------------------------------------

@app.get("/dag", response_class=HTMLResponse)
async def dag_view(request: Request, root: str | None = None):
    """Render the DAG mermaid diagram partial.

    Without ``root``: the global view over the whole tree, clustered by subtree.
    With ``root=<task path>``: an inline per-subtree panel scoped to that task's
    direct children (their sibling dependency graph), reusing the same template.
    """
    state = resolve_worktree(request)
    if state.root_task is None:
        raise HTTPException(status_code=500, detail="Task tree not initialized")
    env = _get_jinja_env()
    template = env.get_template("dag.html")
    if root:
        sub_root = _find_task(state, root)
        if sub_root is None:
            raise HTTPException(status_code=404, detail=f"Task not found: {root}")
        # Scope to the parent's direct children — the sibling-only graph.
        sub_tasks = list(sub_root.children)
        return HTMLResponse(content=template.render(root_task=sub_root, all_tasks=sub_tasks))
    all_tasks = collect_all_tasks(state.root_task)
    return HTMLResponse(content=template.render(root_task=state.root_task, all_tasks=all_tasks))


# --- Route: GET /kanban ------------------------------------------------------

@app.get("/kanban", response_class=HTMLResponse)
async def kanban_view(request: Request):
    """Render the kanban board partial."""
    state = resolve_worktree(request)
    if state.root_task is None:
        raise HTTPException(status_code=500, detail="Task tree not initialized")
    env = _get_jinja_env()
    template = env.get_template("kanban.html")
    all_tasks = collect_all_tasks(state.root_task)
    return HTMLResponse(content=template.render(all_tasks=all_tasks))


# --- Route: GET /files/{path} ----------------------------------------------

@app.get("/files/{path:path}")
async def serve_file(path: str, request: Request):
    """Serve files from the project root (for image embeds in markdown)."""
    state = resolve_worktree(request)
    file_path = Path(state.project_root) / path
    resolved = file_path.resolve()
    project_resolved = Path(state.project_root).resolve()

    # Security: prevent path traversal outside project root
    if not resolved.is_relative_to(project_resolved):
        raise HTTPException(status_code=403, detail="Access denied")
    if not resolved.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(resolved))


# --- Comment routes --------------------------------------------------------
# These use /api/ prefix to avoid ambiguity with the catch-all /task/{path:path}
# route.  The {path:path} parameter is greedy and would swallow /task/x/comments
# as path="x/comments".  Templates should call /api/task/PATH/comments etc.

@app.get("/api/comments/summary")
async def comments_summary(request: Request):
    """Return ``{taskPath: unresolvedCount}`` for all tasks with unresolved comments."""
    if not _COMMENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Comments module not available")
    state = resolve_worktree(request)
    if state.root_task is None:
        raise HTTPException(status_code=500, detail="Task tree not initialized")

    result: dict[str, int] = {}

    def _walk(task: Task) -> None:
        comments = load_comments(task.dir_path)
        unresolved = sum(1 for c in comments if not c.resolved)
        if unresolved > 0:
            result[task.path] = unresolved
        for child in task.children:
            _walk(child)

    _walk(state.root_task)
    return result


@app.get("/api/search-index")
async def search_index(request: Request):
    """Return the client search index for the resolved worktree — one record per
    node ({path, slug, title, text}).  The page embeds this index at render time;
    the client re-fetches here on a structural full-reload so live search reflects
    the current tree state."""
    state = resolve_worktree(request)
    if state.root_task is None:
        raise HTTPException(status_code=500, detail="Task tree not initialized")
    all_tasks = collect_all_tasks(state.root_task)
    return _build_search_index(state.root_task, all_tasks)


@app.post("/api/task/{path:path}/comment")
async def create_comment(path: str, request: Request):
    """Create a comment on a task."""
    if not _COMMENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Comments module not available")
    task = _find_task(resolve_worktree(request), path)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {path}")
    body = await request.json()
    comment = add_comment(
        task_dir=task.dir_path,
        section=body.get("section", ""),
        block_index=body.get("block_index", 0),
        text_preview=body.get("text_preview", ""),
        body=body.get("body", ""),
        author=body.get("author"),
    )
    return {"id": comment.id, "status": "created"}


@app.get("/api/task/{path:path}/comments")
async def list_comments(path: str, request: Request):
    """List comments for a task."""
    if not _COMMENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Comments module not available")
    task = _find_task(resolve_worktree(request), path)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {path}")
    comments = load_comments(task.dir_path)
    return [
        {
            "id": c.id,
            "author": c.author,
            "timestamp": c.timestamp,
            "resolved": c.resolved,
            "body": c.body,
            "anchor": {
                "section": c.anchor.section,
                "block_index": c.anchor.block_index,
                "text_preview": c.anchor.text_preview,
            },
        }
        for c in comments
    ]


@app.patch("/api/task/{path:path}/comment/{comment_id}")
async def toggle_comment(path: str, comment_id: int, request: Request):
    """Toggle resolved status or edit body of a comment.

    Without a JSON body (or empty body): toggle resolved.
    With JSON ``{"body": "..."}`` : update the comment text.
    """
    if not _COMMENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Comments module not available")
    task = _find_task(resolve_worktree(request), path)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {path}")

    # Try to read a JSON body; if absent or empty, fall back to resolve toggle
    try:
        data = await request.json()
    except Exception:
        data = {}

    if "body" in data:
        result = edit_comment(task.dir_path, comment_id, data["body"])
        if result is None:
            raise HTTPException(status_code=404, detail=f"Comment not found: {comment_id}")
        return {"id": result.id, "body": result.body}

    result = resolve_comment(task.dir_path, comment_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Comment not found: {comment_id}")
    return {"id": result.id, "resolved": result.resolved}


@app.delete("/api/task/{path:path}/comment/{comment_id}")
async def remove_comment(path: str, comment_id: int, request: Request):
    """Delete a comment."""
    if not _COMMENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Comments module not available")
    task = _find_task(resolve_worktree(request), path)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {path}")
    deleted = delete_comment(task.dir_path, comment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Comment not found: {comment_id}")
    return {"status": "deleted"}


# --- Worktree routes -------------------------------------------------------

@app.get("/api/worktrees")
async def list_worktrees():
    """Return discovered worktrees with plan info, ordered by last activity.

    Each entry carries the ``wt_id`` selector token (the worktree's ``?wt=`` name,
    matching task 01's basename map with longest-unique-suffix disambiguation).
    ``launch_wt_id`` names the default worktree (the one the server launched in);
    the client marks the *current* selection from the URL's ``?wt=`` and falls
    back to ``launch_wt_id`` when the URL names none.  There is no server-global
    "current worktree": under per-request resolution it would only drift.
    """
    launch_dir = str(PLAN_ROOT.resolve().parent)
    all_wts = discover_worktrees()
    if not all_wts:
        # Not in a git repo — return a single-entry fallback
        plan_title: str | None = None
        task_md = PLAN_ROOT / "task.md"
        if task_md.is_file():
            try:
                plan_title = _parse_plan_title(task_md)
            except Exception:
                pass
        return {
            "launch_wt_id": _launch_wt_id,
            "worktrees": [
                {
                    "path": launch_dir,
                    "wt_id": _launch_wt_id,
                    "branch": None,
                    "plan_title": plan_title,
                    "has_plan": True,
                    "is_agent": False,
                    "last_activity": None,
                }
            ],
        }

    filtered = filter_worktrees(all_wts)
    ordered = sort_worktrees(filtered)

    # Reverse the basename map so each worktree carries its ?wt= selector token.
    wt_id_by_plan_root: dict[str, str] = {
        str(pr.resolve()): wt_id for wt_id, pr in _discovered_worktree_map().items()
    }

    entries = []
    for w in ordered:
        wt_id = (
            wt_id_by_plan_root.get(str(Path(w.plan_root).resolve()))
            if w.plan_root is not None
            else None
        )
        entries.append(
            {
                "path": w.path,
                "wt_id": wt_id,
                "branch": w.branch,
                "plan_title": w.plan_title,
                "has_plan": w.plan_root is not None,
                "plan_root": w.plan_root,
                "is_agent": w.is_agent,
                "last_activity": w.last_activity,
            }
        )

    return {
        "launch_wt_id": _launch_wt_id,
        "worktrees": entries,
    }


# The former ``POST /api/worktree/switch`` is retired.  "Switching" is now a
# client navigation to a different ``?wt=`` URL (per-request resolution, task 03);
# there is no global mutation and no all-clients full-reload broadcast.  The
# selector's onchange pushes a new ``?wt=`` and re-renders that worktree in place.


# --- Route: GET /task/{path} -----------------------------------------------
# MUST come after comment routes — {path:path} is greedy and would swallow
# suffixes like /comments or /comment/123.

@app.get("/task/{path:path}", response_class=HTMLResponse)
async def get_task(path: str, request: Request):
    """Return an HTML fragment with the children of the task at *path*."""
    state = resolve_worktree(request)
    task = _find_task(state, path)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {path}")
    html = _render_task_fragment(task, state.project_root)
    return HTMLResponse(content=html)


# --- Route: GET /nav/{path} (nav-only lazy children) -----------------------
# {path:path} is greedy; keep after the comment routes for the same reason as
# /task/{path}.  Returns body-free children so deep sidebar nodes lazy-load
# without pulling task bodies.

@app.get("/nav/{path:path}", response_class=HTMLResponse)
async def get_nav(path: str, request: Request):
    """Return a navigation-only fragment with the children of the task at *path*."""
    task = _find_task(resolve_worktree(request), path)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {path}")
    html = _render_nav_children(task)
    return HTMLResponse(content=html)


# --- Route: GET /node/{path} (active-node body-only partial) ----------------
# {path:path} is greedy; keep after the comment routes.  Renders only the body
# half (meta pills + sections) of a single task, byte-for-byte the same section
# markup the index emits, so the client's renderMarkdown/loadComments consume it
# unchanged.

@app.get("/node/{path:path}", response_class=HTMLResponse)
async def get_node(path: str, request: Request):
    """Return the body-only HTML fragment for the task at *path*."""
    state = resolve_worktree(request)
    task = _find_task(state, path)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {path}")
    html = _render_node_body(task, state.project_root)
    return HTMLResponse(content=html)


# --- Route: GET /export (standalone subtree download) ----------------------
# The "Share" button backs onto this: it renders the same standalone single-file
# HTML the CLI `generate --root <path>` produces, scoped to a subtree, and serves
# it with Content-Disposition: attachment so the browser saves a portable file.

@app.get("/export")
async def export_subtree(request: Request, root: str = ""):
    """Return a self-contained standalone HTML dashboard scoped to *root*'s
    subtree as a file download.

    Empty *root* exports the whole tree.  The rendered HTML is identical to
    ``plan_dashboard.py generate [--root <path>]``: server-less, all fragments
    embedded inline, opens via ``file://``.  Resolves the worktree per request
    (defaulting to the launch worktree) and exports exactly that one worktree;
    restores live module state after rendering so the running server is
    unaffected.
    """
    state = resolve_worktree(request)
    if state.root_task is None:
        raise HTTPException(status_code=500, detail="Task tree not initialized")
    if root and _find_task(state, root) is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {root}")

    # render_standalone_html drives module state (_root_task/_task_index) the way
    # generate_dashboard does, so snapshot and restore the live server's state.
    saved_root, saved_index, saved_project = _root_task, _task_index, _project_root
    try:
        html = render_standalone_html(state.plan_root, root=root or None)
    finally:
        _set_module_state(saved_root, saved_index, saved_project)

    slug = root.rsplit("/", 1)[-1] if root else (state.root_task.slug or "plan")
    # Sanitize before interpolating into the quoted Content-Disposition value:
    # keep only filename-safe chars so a stray `"` (or path/control char) in a
    # slug cannot break out of the header. Falls back to "plan" if nothing left.
    safe_slug = re.sub(r"[^A-Za-z0-9._-]", "-", slug or "").strip("-") or "plan"
    filename = f"{safe_slug}-dashboard.html"
    return HTMLResponse(
        content=html,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Static HTML generation — single-file, server-less export from base.html
# ---------------------------------------------------------------------------
# The `generate` subcommand renders the SAME base.html template the live server
# serves, in standalone mode: every fragment the live client fetches (/nav,
# /nav/<path>, /node/<path>, /dag?root=<path>, /kanban) is pre-rendered here with
# the identical Jinja partials and embedded inline, and base.html's standalone
# fetch shim resolves the client's fetch() calls from that embedded map. There
# is exactly one dashboard source (base.html + its partials); no duplicate
# template string.


def _build_standalone_fragments() -> dict[str, str]:
    """Pre-render every server fragment the standalone client fetches.

    Mirrors the live routes (/nav, /nav/<path>, /node/<path>, /dag?root=<path>,
    /kanban) byte-for-byte by reusing the same render helpers, keyed by the exact
    URL the client requests so base.html's standaloneFetch resolves them offline.
    Assumes module state (``_root_task``, ``_project_root``) is already set.
    """
    assert _root_task is not None
    fragments: dict[str, str] = {}

    # /nav — the body-free sidebar tree (root-or-children logic, depth<3 inline).
    env = _get_jinja_env()
    nav_tmpl = env.from_string(
        '{%- from "nav_node.html" import render_nav_node -%}'
        '{% if root_task.body and root_task.body.strip() %}'
        '{{ render_nav_node(root_task, depth=0) }}'
        '{% else %}'
        '{% for child in root_task.children %}'
        '{{ render_nav_node(child, depth=0) }}'
        '{% endfor %}'
        '{% endif %}'
    )
    fragments["/nav"] = nav_tmpl.render(root_task=_root_task)

    # Per-task fragments: /node/<path>, /dag?root=<path>, and /nav/<path> for any
    # non-leaf (the depth>=3 lazy branches the sidebar requests on first open).
    # All three are keyed by the bare (decoded) path. /node and /nav are fetched
    # with raw string concatenation client-side, so their URLs carry the path
    # un-encoded. /dag is fetched with encodeURIComponent(path), which escapes the
    # '/' of a multi-segment path to %2F — so the standalone fetch shim decodes
    # the URL before the map lookup, matching all three against these bare keys.
    # Include the root itself, not just its descendants: the client fetches the
    # root's /node/ body and /dag?root= children-graph on initial load.
    # collect_all_tasks excludes the root, so without it the root card shows
    # "Could not load this task" — and a leaf-only subtree export (root with no
    # children) embeds no node body at all. /nav/<path> stays descendants-only
    # (the root is served by the main /nav fragment, never /nav/).
    all_tasks = collect_all_tasks(_root_task)
    for task in [_root_task, *all_tasks]:
        fragments[f"/node/{task.path}"] = _render_node_body(task)
        fragments[f"/dag?root={task.path}"] = _render_dag_fragment(task)
        if task.children and task.path:
            fragments[f"/nav/{task.path}"] = _render_nav_children(task)

    # /kanban — the full board.
    kanban_tmpl = env.get_template("kanban.html")
    fragments["/kanban"] = kanban_tmpl.render(all_tasks=all_tasks)

    return fragments


def _render_dag_fragment(task: Task) -> str:
    """Render dag.html scoped to a task's direct children — the same payload the
    live ``GET /dag?root=<path>`` route returns (sibling-only graph)."""
    env = _get_jinja_env()
    template = env.get_template("dag.html")
    return template.render(root_task=task, all_tasks=list(task.children))


def _rebase_subtree(task: Task, root_path: str) -> Task:
    """Return a copy of *task*'s subtree with every path re-based so *root_path*
    becomes the empty-string root.

    The whole standalone + navigation machinery (depth-based inline-vs-lazy nav,
    breadcrumb, the ``''`` JS root, ``TASK_PATHS``, the ``task-root`` nav id)
    keys on ``task.path`` and treats the empty path as the root.  A subtree node
    carries its full tree path (e.g. ``a/b/c``); stripping the ``root_path + '/'``
    prefix from it and every descendant re-roots the subtree so that identical
    machinery renders it as if it were a whole tree.  ``depends_on`` holds sibling
    slugs (last path segment), which are unaffected by re-basing, and ``dir_path``
    is left untouched so figure/file resolution still points at the real dirs.
    """
    prefix = f"{root_path}/" if root_path else ""

    def _rebase(node: Task) -> Task:
        new_path = node.path[len(prefix):] if prefix and node.path.startswith(prefix) else node.path
        if node.path == root_path:
            new_path = ""
        return replace(node, path=new_path, children=[_rebase(c) for c in node.children])

    return _rebase(task)


def _set_module_state(root_task: Task | None, index: dict[str, Task], project_root: str) -> None:
    """Set the render-helper module state in one place (used to snapshot/restore
    around a standalone render that must not perturb a live server)."""
    global _root_task, _task_index, _project_root
    _root_task = root_task
    _task_index = index
    _project_root = project_root


# ---------------------------------------------------------------------------
# Standalone embedding — figures (base64 data URIs) and vendored render libs
# ---------------------------------------------------------------------------

def _resource_dir(name: str):
    if __package__:
        return resources.files(__package__).joinpath(name)
    return Path(__file__).parent / name


_VENDOR_DIR = _resource_dir("vendor")

# Image extension -> MIME, for the data: URI of an embedded figure.
_IMG_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}

# Markdown `![alt](src)` and HTML `<img src=...>` (single/double/unquoted) refs.
_MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(\s*([^)\s]+)")
_HTML_IMG_RE = re.compile(r"""<img\b[^>]*?\bsrc\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", re.IGNORECASE)


def _iter_body_image_srcs(body: str) -> list[str]:
    """Extract every image src referenced in a raw markdown body — both
    ``![alt](src)`` and ``<img src=...>`` forms — preserving first-seen order."""
    srcs: list[str] = []
    seen: set[str] = set()
    for m in _MD_IMG_RE.finditer(body):
        s = m.group(1).strip()
        if s and s not in seen:
            seen.add(s)
            srcs.append(s)
    for m in _HTML_IMG_RE.finditer(body):
        s = (m.group(1) or m.group(2) or m.group(3) or "").strip()
        if s and s not in seen:
            seen.add(s)
            srcs.append(s)
    return srcs


def _is_embeddable_src(src: str) -> bool:
    """A relative figure path we should embed — not absolute, not a URL, not an
    already-inlined data URI."""
    low = src.lower()
    return not (
        src.startswith("/")
        or low.startswith("http://")
        or low.startswith("https://")
        or low.startswith("data:")
    )


def _build_standalone_images(scoped_root: Task) -> dict[str, str]:
    """Build the ``{ client-key: data-URI }`` map the standalone ``img[src]`` loop
    consults before its relative-path fallback.

    For every task in the (re-based) export tree, find the relative image refs in
    its raw markdown ``body``, resolve each against the task's **real on-disk** dir
    (``dir_path``, left un-rebased by ``_rebase_subtree`` precisely so figure bytes
    stay reachable), read the bytes, and base64-encode with the extension's MIME.

    The key is the exact string the client computes in the ``img[src]`` loop:
    ``task.path + '/' + src`` for a task body, and the bare ``src`` for the root
    body (empty path) — using the re-based ``task.path``, not ``dir_path``.
    Unreadable files / unknown extensions are skipped (the client then falls back
    to its relative-path rewrite, unchanged).
    """
    images: dict[str, str] = {}
    for task in [scoped_root, *collect_all_tasks(scoped_root)]:
        if not task.body:
            continue
        for src in _iter_body_image_srcs(task.body):
            if not _is_embeddable_src(src):
                continue
            key = f"{task.path}/{src}" if task.path else src
            if key in images:
                continue
            ext = Path(src.split("?", 1)[0].split("#", 1)[0]).suffix.lower()
            mime = _IMG_MIME.get(ext)
            if mime is None:
                continue
            img_path = (task.dir_path / src).resolve()
            try:
                raw = img_path.read_bytes()
            except OSError:
                continue
            b64 = base64.b64encode(raw).decode("ascii")
            images[key] = f"data:{mime};base64,{b64}"
    return images


# KaTeX @font-face blocks reference woff2 (and woff/ttf fallbacks) via url(...);
# match a whole @font-face block so we can rewrite just its src to one data URI.
_FONTFACE_RE = re.compile(r"@font-face\s*\{[^}]*\}", re.IGNORECASE)
_FONT_URL_RE = re.compile(r"url\(\s*(?:fonts/)?(KaTeX_[A-Za-z0-9_-]+)\.woff2\s*\)", re.IGNORECASE)


def _inline_katex_css(css: str, fonts_dir: Path) -> str:
    """Rewrite each KaTeX ``@font-face`` so its ``src`` is a single base64 ``data:``
    woff2 URI, dropping the woff/ttf fallback sources (woff2 only).

    KaTeX's CSS references its fonts via ``url(fonts/KaTeX_*.woff2)``; this reads the
    vendored woff2 bytes and replaces the whole ``src:`` declaration with one
    ``url(data:font/woff2;base64,...) format("woff2")`` so the inlined ``<style>``
    needs no external font fetch.
    """

    def _replace_block(block_match: re.Match[str]) -> str:
        block = block_match.group(0)
        font_match = _FONT_URL_RE.search(block)
        if font_match is None:
            return block
        woff2 = fonts_dir / f"{font_match.group(1)}.woff2"
        try:
            raw = woff2.read_bytes()
        except OSError:
            return block
        b64 = base64.b64encode(raw).decode("ascii")
        data_src = f'src:url(data:font/woff2;base64,{b64}) format("woff2")'
        # Replace the original src:...; (which lists woff2/woff/ttf) with our one.
        return re.sub(r"src\s*:[^;}]*", data_src, block, count=1)

    return _FONTFACE_RE.sub(_replace_block, css)


def _build_standalone_assets() -> dict[str, str]:
    """Read the vendored render libraries and return the inlined JS/CSS strings the
    standalone template emits in place of the CDN ``<link>``/``<script>`` tags.

    Returns ``markdown_it_js`` / ``katex_js`` / ``texmath_js`` / ``hljs_js`` /
    ``hljs_julia_js`` / ``purify_js`` (raw minified JS, emitted as inline
    ``<script>`` bodies) and ``katex_css`` (KaTeX CSS with every ``@font-face``
    rewritten to a base64 woff2 ``data:`` URI, emitted as an inline ``<style>``).
    """
    def _read_js(name: str) -> str:
        # Guard against a future re-pin whose body contains a literal </script>
        # that would prematurely close the inline block (none do today).
        text = (_VENDOR_DIR / name).read_text(encoding="utf-8")
        return re.sub(r"</(script)", r"<\\/\1", text, flags=re.IGNORECASE)

    fonts_dir = _VENDOR_DIR / "fonts"
    css = (_VENDOR_DIR / "katex.min.css").read_text(encoding="utf-8")
    css = _inline_katex_css(css, fonts_dir)
    css = re.sub(r"</(style)", r"<\\/\1", css, flags=re.IGNORECASE)
    return {
        "markdown_it_js": _read_js("markdown-it.min.js"),
        "katex_js": _read_js("katex.min.js"),
        "texmath_js": _read_js("texmath.min.js"),
        "hljs_js": _read_js("highlight.min.js"),
        "hljs_julia_js": _read_js("languages/julia.min.js"),
        "purify_js": _read_js("purify.min.js"),
        "katex_css": css,
    }


# Strip markdown punctuation/fences from a body so the search index matches on
# readable words rather than `#`, backticks, link syntax, etc.  Cheap and lossy
# by design — substring search over titles + body prose is the goal.
_MD_NOISE_RE = re.compile(r"(```.*?```|`[^`]*`)", re.DOTALL)
_MD_PUNCT_RE = re.compile(r"[#>*_\[\]()|`]+")


def _search_text(body: str) -> str:
    """Flatten a raw markdown body to indexable plain text: drop fenced/inline
    code, strip markdown punctuation, and collapse whitespace."""
    if not body:
        return ""
    text = _MD_NOISE_RE.sub(" ", body)
    text = _MD_PUNCT_RE.sub(" ", text)
    return " ".join(text.split())


def _build_search_index(root_task: Task, all_tasks: list[Task]) -> list[dict[str, str]]:
    """Build the client search index: one record per node (root included) with
    its tree ``path``, ``slug``, ``title``, and flattened body ``text``.

    Shared by the embedded index (rendered into base.html) and the live
    ``/api/search-index`` endpoint, so server and standalone search the same
    fields.  ``collect_all_tasks`` excludes the root, so it is prepended here.
    """
    index: list[dict[str, str]] = []
    for task in [root_task, *all_tasks]:
        index.append({
            "path": task.path,
            "slug": task.slug,
            "title": task.title or "",
            "text": _search_text(task.body),
        })
    return index


def render_standalone_html(
    plan_root: Path,
    output_path: Path | None = None,
    root: str | None = None,
    repo_file_base: str = "",
    repo_root_prefix: str = "",
    doc_mode: bool = False,
    doc_local_links: list[str] | None = None,
) -> str:
    """Render the self-contained standalone dashboard HTML and return it.

    Drives the render-helper module state (``_root_task`` / ``_task_index`` /
    ``_project_root``) the same way the serve lifespan does, renders base.html in
    standalone mode with every server fragment pre-rendered and embedded inline,
    and returns the HTML string (no file write).  When *root* names a task path,
    the export is scoped to that subtree: the node is located in the full tree,
    re-based so it becomes the root, and the embedded data / pre-rendered
    fragments / nav cover exactly that subtree.  Whole-tree export (``root=None``)
    is unchanged.  *output_path* (when given) only fixes where ``<img>`` sources
    resolve from a ``file://`` open; the HTML itself is not written here.
    *repo_file_base* optionally points file links at a repository browser base
    such as ``https://github.com/owner/repo/blob/sha`` instead of local editor
    links.  *repo_root_prefix* is the resolved root's path relative to the repo
    root (e.g. ``docs/showcase-demo``); repo-file links use it instead of the
    bare root basename so a tree nested below the repo root keeps its leading
    path.  Empty falls back to the basename (a tree at the repo root, e.g.
    ``superRA``).  *doc_mode* (opt-in) renders the tree as documentation: task-workflow
    chrome (status badges, summary stats/progress, kanban toggle, children
    dependency view) is suppressed, and a genuine body file link resolves
    repo-root-relative (the doc authoring contract) rather than against the doc
    node's dir.  *doc_local_links* names basenames the build emits beside the
    exported site (e.g. the showcase exports) so a doc-mode link to one stays a
    plain relative href instead of being rebased to *repo_file_base*.
    Default output is unchanged.
    """
    full_root = walk_plan(plan_root)
    project_root = str(plan_root.resolve().parent)

    if root:
        full_index: dict[str, Task] = {}
        _build_index(full_root, full_index)
        located = full_index.get(root)
        if located is None:
            raise KeyError(f"Task not found: {root}")
        # The dir the subtree's figures resolve against (its real on-disk dir).
        subtree_dir = located.dir_path
        scoped_root = _rebase_subtree(located, root)
    else:
        scoped_root = full_root
        subtree_dir = plan_root

    index: dict[str, Task] = {}
    _build_index(scoped_root, index)
    _set_module_state(scoped_root, index, project_root)

    all_tasks = collect_all_tasks(scoped_root)
    fragments = _build_standalone_fragments()

    # Where the embedded task tree sits relative to the dashboard file, so
    # standalone <img> sources resolve from a file:// open.  Tasks reference
    # figures relative to their dir, and re-based task paths are relative to the
    # subtree root, so the prefix is the subtree dir relative to the output file.
    standalone_plan_dir = ""
    if output_path is not None:
        output_parent = output_path.resolve().parent
        try:
            plan_rel = subtree_dir.resolve().relative_to(output_parent)
            standalone_plan_dir = f"{plan_rel.as_posix()}/" if plan_rel.as_posix() != "." else ""
        except ValueError:
            standalone_plan_dir = ""
        # The committed default (dashboard.html written INTO the subtree dir)
        # means task dirs sit beside the file, so no prefix is needed.
        if output_parent == subtree_dir.resolve():
            standalone_plan_dir = ""

    # Figures: a { client-key -> data-URI } map the standalone img loop consults
    # before its relative-path fallback, so figures survive a moved/offline file.
    standalone_images = _build_standalone_images(scoped_root)
    # Render libraries: inlined JS/CSS read from the vendored files (font-inlined
    # KaTeX CSS), emitted in standalone mode instead of the CDN tags.
    standalone_assets = _build_standalone_assets()

    env = _get_jinja_env()
    template = env.get_template("base.html")
    # XSS-safe: the embedded fragments and data are injected via Jinja's `| tojson`
    # filter, which escapes `<`, `>`, `&`, and line separators (so an embedded
    # `</script>` cannot prematurely close the <script> block).
    # The resolved root every task-path -> file link resolves against is the dir
    # paths are relative to: the subtree dir for a --root export (paths re-based
    # to it), else the plan root.  ``subtree_dir`` is exactly that dir.
    resolved_root = str(subtree_dir.resolve())
    return template.render(
        root_task=scoped_root,
        all_tasks=all_tasks,
        project_root=project_root,
        resolved_root=resolved_root,
        root_prefix=Path(resolved_root).name,
        standalone=True,
        standalone_fragments=fragments,
        standalone_plan_dir=standalone_plan_dir,
        standalone_images=standalone_images,
        standalone_assets=standalone_assets,
        repo_file_base=repo_file_base.rstrip("/"),
        repo_root_prefix=repo_root_prefix.strip("/"),
        doc_mode=doc_mode,
        doc_local_links=doc_local_links or [],
        search_index=_build_search_index(scoped_root, all_tasks),
    )


def generate_dashboard(
    plan_root: Path,
    output_path: Path | None = None,
    root: str | None = None,
    repo_file_base: str = "",
    repo_root_prefix: str = "",
    doc_mode: bool = False,
    doc_local_links: list[str] | None = None,
) -> Path:
    """Generate a self-contained static HTML dashboard from base.html.

    Renders base.html in standalone mode with all server fragments pre-rendered
    and embedded inline, so the output opens via ``file://`` with zero network
    calls for task data.  Import-compatible with the previous implementation:
    same name, defaults ``output_path`` to ``plan_root / "dashboard.html"``,
    writes the file, prints the path, and returns it.  *root* scopes the export
    to a subtree (see ``render_standalone_html``).  *doc_mode* renders the tree
    as a documentation site (chrome suppressed); *doc_local_links* names sibling
    artifacts left as relative links — see ``render_standalone_html``.
    """
    if output_path is None:
        output_path = plan_root / "dashboard.html"

    html = render_standalone_html(
        plan_root, output_path, root, repo_file_base=repo_file_base,
        repo_root_prefix=repo_root_prefix,
        doc_mode=doc_mode, doc_local_links=doc_local_links,
    )
    output_path.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {output_path}")
    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _default_port(plan_root: Path, git_common_dir: str | None = None) -> int:
    """Derive a deterministic port from the repo or plan root.

    When *git_common_dir* is provided, the port is derived from the common
    dir so all worktrees of the same repo share a single dashboard port.
    Otherwise falls back to plan-root hashing (backward compatible).

    Maps deterministically into range 8100-8999 with no "next free port" walk:
    the port is a pure function of the repo (or plan-root) identity, so every
    launch from every worktree targets the *same* start port and the reuse logic
    in ``serve_background`` can find the one server already there.  Walking off a
    busy port here is what let a repo accumulate one server per worktree on
    adjacent ports; ``serve_background`` now does a repo-aware walk instead —
    reusing a busy port when *our* dashboard serves it, and advancing only for a
    different repo (a hash collision) or a foreign process.
    """
    hash_source = git_common_dir if git_common_dir else str(plan_root.resolve())
    return int(hashlib.sha256(hash_source.encode()).hexdigest(), 16) % 900 + 8100


def _repo_id(git_common_dir: str | None, plan_root: Path) -> str:
    """Stable identity for the repo, matching ``_default_port``'s hash source.

    The git common dir (resolved, shared by all of a repo's worktrees) when
    there is one, else the plan root — hashed to a compact opaque token that
    ``/healthz`` reports so reuse can distinguish our repo's dashboard from a
    different repo colliding on the same port.
    """
    source = git_common_dir if git_common_dir else str(plan_root.resolve())
    return hashlib.sha256(source.encode()).hexdigest()[:16]


def _candidate_ports(base: int, count: int = 50):
    """Yield ``base, base+1, …`` — the ports a launch probes in order.

    A linear walk from the deterministic start port (skipping any that overflow
    the valid range) so a hash collision between two repos resolves them onto
    distinct adjacent ports deterministically: every worktree of a repo derives
    the same *base* and walks the same sequence, so all reach the same server.
    """
    for i in range(count):
        port = base + i
        if port > 65535:
            return
        yield port


def serve(port: int, host: str = "127.0.0.1") -> None:
    """Run the dashboard server on *port*, blocking until it exits.

    Binds *host*, defaulting to loopback (``127.0.0.1``).  The server is
    unauthenticated and exposes the project's files (``/files/{path}``), the
    full task tree (``/export``), and disk-writing comment routes; with
    background-by-default serving this is a long-lived ambient surface, so it
    must not be reachable off-host unless the operator deliberately opts in via
    ``--host`` (e.g. ``--host 0.0.0.0`` for trusted-LAN serving).

    Uses ``uvicorn.Server`` so the idle monitor can request shutdown via
    ``_server.should_exit = True``.  This is the single in-process serve path:
    both ``serve --foreground`` and the detached background child call it, so
    their lifecycle (idle self-exit included) is identical.  Run through
    ``Server.run()`` so uvicorn installs its configured event-loop factory
    (``auto`` uses uvloop when available) before serving.
    """
    import uvicorn

    global _server
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    _server = uvicorn.Server(config)
    try:
        _server.run()
    finally:
        _server = None


# ---------------------------------------------------------------------------
# Background supervisor: PID/log files, idempotent launch, stop
# ---------------------------------------------------------------------------
#
# The default ``serve`` is a thin supervisor: it spawns the in-process server
# (``serve()``) as a detached child, waits for the port to bind, writes a PID
# file, prints URL + PID + log path, and returns.  A second launch reuses a
# healthy running server instead of spawning a duplicate; ``stop`` terminates
# it.  PID and log files are keyed to the same repo identity as the port (the
# git common dir), so they are repo-scoped and shared across the repo's
# worktrees — matching one-server-per-repo.


def _runtime_dir(plan_root: Path, git_common_dir: str | None = None) -> Path:
    """Directory holding the PID and log files for this repo's dashboard.

    Keyed to the same repo identity as the port: the git common dir when there
    is one (so all worktrees of a repo share it), else the plan root — mirroring
    ``_default_port``.
    """
    return Path(git_common_dir) if git_common_dir else plan_root.resolve()


def _pid_file(plan_root: Path, git_common_dir: str | None = None) -> Path:
    return _runtime_dir(plan_root, git_common_dir) / "superra-dashboard.pid"


def _log_file(plan_root: Path, git_common_dir: str | None = None) -> Path:
    return _runtime_dir(plan_root, git_common_dir) / "superra-dashboard.log"


def _read_pid_port(pid_path: Path) -> tuple[int | None, int | None]:
    """Return ``(pid, port)`` recorded in *pid_path*.

    The PID file stores ``"<pid> <port>"`` (port lets a reuse check probe the
    port the running server actually bound, which can differ from a freshly
    derived port when the deterministic port was occupied at its launch).  A
    legacy single-int file (pid only) returns ``(pid, None)``.  Returns
    ``(None, None)`` when absent or unparseable.
    """
    try:
        text = pid_path.read_text(encoding="utf-8").strip()
    except OSError:
        return None, None
    parts = text.split()
    try:
        pid = int(parts[0])
    except (IndexError, ValueError):
        return None, None
    port: int | None = None
    if len(parts) > 1:
        try:
            port = int(parts[1])
        except ValueError:
            port = None
    return pid, port


def _read_pid(pid_path: Path) -> int | None:
    """Return the PID recorded in *pid_path*, or None if absent/unreadable."""
    return _read_pid_port(pid_path)[0]


def _write_pid_port(pid_path: Path, pid: int, port: int) -> None:
    """Record ``"<pid> <port>"`` to *pid_path*."""
    pid_path.write_text(f"{pid} {port}", encoding="utf-8")


def _pid_alive(pid: int) -> bool:
    """Return True if a process with *pid* exists and is not a reaped zombie.

    Uses a signal-0 probe.  When *pid* is a child of this process (e.g. a
    background server launched and stopped in the same interpreter, as in
    tests), a terminated child lingers as a zombie that the probe still reports
    as existing; a non-blocking ``waitpid`` reaps it first so the probe is
    accurate.  In normal CLI use launch and stop are separate processes, so the
    background server is never this process's child and ``waitpid`` is a no-op.
    """
    try:
        reaped, _ = os.waitpid(pid, os.WNOHANG)
        if reaped == pid:
            return False
    except ChildProcessError:
        # Not our child — nothing to reap; fall through to the signal probe.
        pass
    except OSError:
        pass
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # Exists but owned by another user — still alive for our purposes.
        return True
    return True


def _port_serving(port: int) -> bool:
    """Return True if something is accepting connections on *port* locally."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("localhost", port)) == 0


def _probe_dashboard(
    port: int, timeout: float = 0.5
) -> tuple[int, bool, str | None] | None:
    """Return ``(pid, doc_mode, repo_id)`` of a superRA dashboard on *port*.

    Hits the ``/healthz`` identity endpoint so reuse does not depend on the PID
    file: a foreground server (no PID file) or one whose file was lost is still
    recognised.  ``repo_id`` is the responder's repo identity, or None for a
    server predating the identity field — callers match it against the expected
    repo so a colliding different repo is not adopted.  Returns None when nothing
    answers, the responder is not a superRA dashboard (a foreign process holding
    the port), or the payload is unusable.  ``urllib`` keeps this stdlib-only.
    """
    import urllib.request

    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/healthz", timeout=timeout
        ) as resp:
            if resp.status != 200:
                return None
            payload = json.loads(resp.read(1000).decode("utf-8", "replace"))
    except Exception:
        return None
    if not isinstance(payload, dict) or payload.get("service") != "superra-dashboard":
        return None
    pid = payload.get("pid")
    if not isinstance(pid, int):
        return None
    repo_id = payload.get("repo_id") or None
    return pid, bool(payload.get("doc_mode", False)), repo_id


def _wait_for_dashboard(
    port: int, timeout: float = 10.0, poll: float = 0.1
) -> tuple[int, bool, str | None] | None:
    """Poll ``/healthz`` on *port* until a superRA dashboard answers.

    Returns its ``(pid, doc_mode, repo_id)`` or None on timeout.  Waiting on the
    identity endpoint (not a bare TCP accept) means the app has finished startup
    before the caller decides whether it launched the winner or lost a race.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        probed = _probe_dashboard(port)
        if probed is not None:
            return probed
        time.sleep(poll)
    return _probe_dashboard(port)


def _running_pid(pid_path: Path, port: int) -> tuple[int, int] | None:
    """Return ``(pid, port)`` of a healthy running dashboard, else None.

    Healthy = the PID file names a live process *and* its recorded port is
    serving.  The port a running server bound is read from the PID file (it can
    differ from a freshly derived *port* when the deterministic port was
    occupied at launch); *port* is the fallback for a legacy pid-only file.  A
    stale PID file (process gone, or port not actually serving) is cleaned up
    and None is returned so the caller can spawn a fresh server.
    """
    pid, recorded_port = _read_pid_port(pid_path)
    if pid is None:
        return None
    probe_port = recorded_port if recorded_port is not None else port
    if _pid_alive(pid) and _port_serving(probe_port):
        return pid, probe_port
    # Stale PID file — remove it so a fresh launch is not blocked.
    pid_path.unlink(missing_ok=True)
    return None


def _wait_for_bind(port: int, timeout: float = 10.0, poll: float = 0.1) -> bool:
    """Poll *port* until it accepts connections or *timeout* elapses."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _port_serving(port):
            return True
        time.sleep(poll)
    return _port_serving(port)


def _open_browser_async(url: str) -> None:
    """Open *url* in a browser without blocking the caller."""
    import threading

    def _open():
        time.sleep(1.0)
        webbrowser.open(url)

    threading.Thread(target=_open, daemon=True).start()


def serve_background(
    plan_root: Path,
    port: int,
    git_common_dir: str | None = None,
    *,
    host: str = "127.0.0.1",
    open_browser: bool = True,
    bind_timeout: float = 10.0,
    idle_timeout: float | None = None,
    doc_mode: bool = False,
) -> int:
    """Launch (or reuse) a detached background dashboard server for this repo.

    Returns a process exit code: 0 on success (spawned or already running), non-
    zero when a freshly spawned child fails to bind within *bind_timeout*.

    Idempotent one-server-per-repo, collision-safe across repos.  Reuse is
    decided in two layers so a missing/stale PID file cannot cause a duplicate:
    the PID file (fast path), then a repo-aware candidate walk from the
    deterministic port.  At each candidate the ``/healthz`` probe recognises a
    live server whose file was never written (foreground launch) or was lost; if
    it is *our* repo's dashboard (matching repo id and serve mode) it is reused
    and the PID file repaired, if it is a *different* repo (a hash collision) or
    a foreign process the walk advances to the next port, and the first free port
    is spawned on.  A different repo colliding on our start port thus gets its
    own adjacent port instead of silently adopting (and later ``stop``-killing)
    our server.  The bound port is recorded in the repo-keyed PID file so later
    launches reuse via layer 1.  Spawns ``serve()`` in a new session
    (``start_new_session=True``, stdio to the log file) so it survives the
    launching shell, then waits on ``/healthz``.  If a *different* dashboard
    answers (a concurrent launch won the bind race), the redundant child is
    terminated so it does not linger and the winner is reused; a foreign process
    or cross-repo/cross-mode conflict is reported rather than leaving a dead
    child.
    """
    pid_path = _pid_file(plan_root, git_common_dir)
    log_path = _log_file(plan_root, git_common_dir)
    repo_id = _repo_id(git_common_dir, plan_root)

    def _announce_reuse(reuse_pid: int, reuse_port: int) -> int:
        reuse_url = _dashboard_url(reuse_port, plan_root)
        print(f"Dashboard already running at {reuse_url} (PID {reuse_pid})")
        if open_browser:
            webbrowser.open(reuse_url)
        return 0

    def _spawn(target_port: int) -> int:
        """Spawn a detached server on *target_port*, wait for it, handle races."""
        url = _dashboard_url(target_port, plan_root)
        # ``start_new_session`` puts the child in its own session so it outlives
        # the launching shell; stdio is redirected to the log file (no TTY).
        cmd = [
            sys.executable,
            str(Path(__file__).resolve()),
            "serve",
            "--foreground",
            "--root",
            str(plan_root),
            "--port",
            str(target_port),
            "--host",
            host,
            "--repo-id",
            repo_id,
            "--no-open",
        ]
        if doc_mode:
            cmd.append("--doc-mode")
        if idle_timeout is not None:
            cmd += ["--idle-timeout", str(idle_timeout)]
        pid_path.parent.mkdir(parents=True, exist_ok=True)
        log_fh = open(log_path, "ab")
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=log_fh,
                stderr=log_fh,
                start_new_session=True,
                cwd=str(Path.cwd()),
            )
        finally:
            log_fh.close()

        served = _wait_for_dashboard(target_port, timeout=bind_timeout)
        if served is None:
            # No superRA dashboard came up: our child crashed, or a foreign
            # process grabbed the port between the probe and the bind.  Don't
            # leave a lingering child; surface the log tail.
            if proc.poll() is None:
                _terminate(proc.pid)
            if _port_serving(target_port):
                print(
                    f"Error: {url} is held by a non-dashboard process; stop it "
                    f"or launch with an explicit --port",
                    file=sys.stderr,
                )
            else:
                print(
                    f"Error: dashboard failed to bind {url} within {bind_timeout:.0f}s",
                    file=sys.stderr,
                )
            tail = _log_tail(log_path)
            if tail:
                print("--- log tail ---", file=sys.stderr)
                print(tail, file=sys.stderr)
            return 1

        served_pid, served_doc_mode, served_repo = served
        if served_pid == proc.pid:
            # Our child won the port.
            _write_pid_port(pid_path, proc.pid, target_port)
            print(f"Dashboard running at {url} (PID {proc.pid})")
            print(f"Logs: {log_path}")
            if open_browser:
                webbrowser.open(url)
            return 0

        # A different superRA dashboard is serving the port — we lost a
        # concurrent launch race (or one came up between the walk and the bind).
        # Terminate the redundant child so it does not linger, then reuse the
        # winner only when it is our repo and mode; otherwise report the
        # conflict rather than adopting another repo's (or mode's) server.
        if proc.poll() is None:
            _terminate(proc.pid)
        if (served_repo is None or served_repo == repo_id) and served_doc_mode == doc_mode:
            _write_pid_port(pid_path, served_pid, target_port)
            return _announce_reuse(served_pid, target_port)
        print(
            f"Error: {url} was taken by another server during launch; retry or "
            f"launch with an explicit --port",
            file=sys.stderr,
        )
        return 1

    # Layer 1 — PID file: the repo-keyed record of the exact port a server bound
    # (which may differ from a fresh derivation after a collision walk).  Reuse
    # unless the probe positively shows a different repo (PID recycled — stale
    # file) or a different serve mode.  A probe that can't answer — e.g. a server
    # predating /healthz — still reuses on the file's healthy verdict.
    existing = _running_pid(pid_path, port)
    if existing is not None:
        existing_pid, existing_port = existing
        probed = _probe_dashboard(existing_port)
        if probed is None:
            return _announce_reuse(existing_pid, existing_port)
        _, probed_doc, probed_repo = probed
        if probed_repo is not None and probed_repo != repo_id:
            # Our recorded PID was recycled by a different repo's dashboard: the
            # file is stale.  Drop it and fall through to the collision walk.
            pid_path.unlink(missing_ok=True)
        elif probed_doc == doc_mode:
            return _announce_reuse(existing_pid, existing_port)
        # else: our repo, different serve mode — fall through; the walk reports
        # the mode conflict on the same port.

    # Layer 2 — repo-aware candidate walk from the deterministic port.
    for index, candidate in enumerate(_candidate_ports(port)):
        probed = _probe_dashboard(candidate)
        if probed is not None:
            probed_pid, probed_doc, probed_repo = probed
            # A repo-id-less server (predating /healthz identity) is trusted as
            # ours only on the start port: under the old launcher a colliding
            # different repo would have walked off a busy port, so it never sat
            # on our start port; adjacent ports carry no such guarantee.
            is_our_repo = probed_repo == repo_id or (probed_repo is None and index == 0)
            if is_our_repo:
                if probed_doc == doc_mode:
                    _write_pid_port(pid_path, probed_pid, candidate)
                    return _announce_reuse(probed_pid, candidate)
                # Our repo already serves this port in the other mode; the PID
                # file is per-repo (not per-mode), so a second server can't
                # coexist.  Report rather than spawn a conflicting duplicate.
                url = f"http://localhost:{candidate}"
                print(
                    f"Error: {url} is already serving a "
                    f"{'doc-mode' if probed_doc else 'task-mode'} dashboard for "
                    f"this repo; stop it or launch with an explicit --port",
                    file=sys.stderr,
                )
                return 1
            # A different repo (hash collision) or foreign dashboard — advance.
            continue
        if _port_serving(candidate):
            # A foreign, non-dashboard process holds the port — advance.
            continue
        # First free candidate — spawn here.
        return _spawn(candidate)

    print(
        f"Error: no free port found near {port} for the dashboard; launch with "
        f"an explicit --port",
        file=sys.stderr,
    )
    return 1


def _log_tail(log_path: Path, lines: int = 20) -> str:
    """Return the last *lines* lines of the log file, or '' if unreadable."""
    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return "\n".join(text.splitlines()[-lines:])


def _terminate(pid: int, timeout: float = 5.0) -> bool:
    """Terminate *pid* (SIGTERM, then SIGKILL) and wait for it to exit.

    Returns True if the process is gone afterward.
    """
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return True
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not _pid_alive(pid):
            return True
        time.sleep(0.1)
    # Escalate.
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return True
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not _pid_alive(pid):
            return True
        time.sleep(0.1)
    return not _pid_alive(pid)


def stop_background(plan_root: Path, git_common_dir: str | None = None) -> int:
    """Terminate the background dashboard server for this repo.

    Reads the PID file and terminates the process, then removes the PID file.
    A clean no-op (exit 0) when nothing is running or the PID file is stale.
    """
    pid_path = _pid_file(plan_root, git_common_dir)
    pid = _read_pid(pid_path)
    if pid is None:
        print("No dashboard server is running.")
        return 0
    if not _pid_alive(pid):
        print("No dashboard server is running (stale PID file removed).")
        pid_path.unlink(missing_ok=True)
        return 0
    if _terminate(pid):
        print(f"Stopped dashboard server (PID {pid}).")
        pid_path.unlink(missing_ok=True)
        return 0
    print(f"Error: could not stop dashboard server (PID {pid}).", file=sys.stderr)
    return 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Task dashboard: live server or static HTML generation.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- serve ---
    serve_p = subparsers.add_parser("serve", help="Start the live dashboard server")
    serve_p.add_argument(
        "--root",
        default=f"{TASK_ROOT_DIRNAME}/",
        help=f"Path to the task root directory (default: {TASK_ROOT_DIRNAME}/ in cwd)",
    )
    serve_p.add_argument(
        "--port",
        type=int,
        default=None,
        help="Server port (default: deterministic port derived from plan root)",
    )
    serve_p.add_argument(
        "--host",
        default="127.0.0.1",
        help=(
            "Interface to bind (default: 127.0.0.1, loopback only). "
            "The server is unauthenticated and serves project files; pass "
            "--host 0.0.0.0 only to deliberately expose it on a trusted LAN."
        ),
    )
    serve_p.add_argument(
        "--no-open",
        action="store_true",
        help="Skip auto-opening the browser",
    )
    serve_p.add_argument(
        "--foreground",
        action="store_true",
        help="Run blocking in this terminal with logs on stdout (default: background)",
    )
    serve_p.add_argument(
        "--doc-mode",
        action="store_true",
        help="Render as a documentation site (suppress task-workflow chrome)",
    )
    serve_p.add_argument(
        "--idle-timeout",
        type=float,
        default=None,
        # Override the idle self-exit window (seconds).  Internal/testing knob:
        # the supervisor passes a sub-second value to a spawned child so a
        # background self-exit can be observed deterministically.
        help=argparse.SUPPRESS,
    )
    serve_p.add_argument(
        "--repo-id",
        default=None,
        # Repo identity reported by /healthz.  Internal: the background
        # supervisor passes the identity it derived so the child reports the
        # same token the launcher's reuse probe matches against (a child
        # re-deriving from cwd could diverge).  Omitted for a manual foreground
        # launch, which then derives its own.
        help=argparse.SUPPRESS,
    )

    # --- stop ---
    stop_p = subparsers.add_parser(
        "stop", help="Stop the background dashboard server for this repo"
    )
    stop_p.add_argument(
        "--root",
        default=f"{TASK_ROOT_DIRNAME}/",
        help=f"Path to the task root directory (default: {TASK_ROOT_DIRNAME}/ in cwd)",
    )

    # --- generate (backward compat) ---
    gen_p = subparsers.add_parser("generate", help="Generate a static HTML dashboard")
    gen_p.add_argument(
        "--plan-root",
        required=True,
        help="Path to the plan root directory",
    )
    gen_p.add_argument(
        "--output",
        default="",
        help="Output HTML path (default: <plan-root>/dashboard.html)",
    )
    gen_p.add_argument(
        "--root",
        dest="subtree_root",
        default="",
        help="Task path to scope the export to (default: whole tree)",
    )
    gen_p.add_argument(
        "--repo-file-base",
        default="",
        help="Repository browser base for file links, e.g. https://github.com/owner/repo/blob/sha",
    )
    gen_p.add_argument(
        "--repo-file-prefix",
        dest="repo_root_prefix",
        default="",
        help="Resolved root's path relative to the repo root for --repo-file-base "
             "links, e.g. docs/showcase-demo. Default: the root basename.",
    )
    gen_p.add_argument(
        "--doc-mode",
        action="store_true",
        help="Render as a documentation site (suppress task-workflow chrome)",
    )
    gen_p.add_argument(
        "--doc-local-link",
        dest="doc_local_links",
        action="append",
        default=[],
        metavar="BASENAME",
        help="Doc-mode only: a sibling artifact (e.g. demo-tree.html) the build "
             "emits beside the site; body links to it stay relative instead of "
             "being rebased to --repo-file-base. Repeatable.",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    raw = sys.argv[1:] if argv is None else argv
    if raw and raw[0] == "dashboard":
        # The task-tree wrapper routes the user-facing `dashboard …` surface
        # here (so the web stack stays off cli.py's hot path) but the surface
        # translation (export→generate, default→serve, artifact, root
        # auto-detect) is single-sourced in cli.py. Delegate to it; cli's
        # dashboard handler re-enters this module in-process with the
        # serve/stop/generate argv it speaks.
        import cli

        cli.main(raw)
        return

    args = parse_args(argv)

    if args.command == "serve":
        global PLAN_ROOT, DOC_MODE, REPO_ID
        PLAN_ROOT = Path(args.root).resolve()
        DOC_MODE = args.doc_mode

        if not PLAN_ROOT.exists():
            print(f"Error: plan root not found: {PLAN_ROOT}", file=sys.stderr)
            sys.exit(1)

        git_common_dir = get_git_common_dir()
        # Report the launcher-supplied identity when present so /healthz matches
        # the token the supervisor probes against; else derive it here.
        REPO_ID = args.repo_id or _repo_id(git_common_dir, PLAN_ROOT)
        port = args.port if args.port is not None else _default_port(PLAN_ROOT, git_common_dir)
        url = _dashboard_url(port, PLAN_ROOT)

        if args.foreground:
            # Blocking console mode: logs on stdout, Ctrl+C or idle self-exit.
            if args.idle_timeout is not None:
                global IDLE_TIMEOUT
                IDLE_TIMEOUT = args.idle_timeout
            if args.port is None:
                source = git_common_dir if git_common_dir else str(PLAN_ROOT)
                print(f"Starting dashboard at {url} (port derived from {source})")
            else:
                print(f"Starting dashboard at {url}")
            print(f"Watching: {PLAN_ROOT}")
            if not args.no_open:
                _open_browser_async(url)
            serve(port, host=args.host)
        else:
            # Default: detach a background server, wait for bind, return.
            rc = serve_background(
                PLAN_ROOT,
                port,
                git_common_dir,
                host=args.host,
                open_browser=not args.no_open,
                idle_timeout=args.idle_timeout,
                doc_mode=args.doc_mode,
            )
            sys.exit(rc)

    elif args.command == "stop":
        plan_root = Path(args.root).resolve()
        git_common_dir = get_git_common_dir()
        rc = stop_background(plan_root, git_common_dir)
        sys.exit(rc)

    elif args.command == "generate":
        plan_root = Path(args.plan_root)
        if not plan_root.exists():
            print(f"Error: plan root not found: {plan_root}", file=sys.stderr)
            sys.exit(1)
        output = Path(args.output) if args.output else None
        subtree_root = args.subtree_root or None
        try:
            generate_dashboard(
                plan_root, output, root=subtree_root,
                repo_file_base=args.repo_file_base,
                repo_root_prefix=args.repo_root_prefix,
                doc_mode=args.doc_mode,
                doc_local_links=args.doc_local_links,
            )
        except KeyError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    else:
        # No subcommand given — print help
        parse_args(["--help"])


if __name__ == "__main__":
    main()
