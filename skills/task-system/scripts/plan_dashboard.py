#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["fastapi", "uvicorn[standard]", "jinja2", "watchfiles", "pyyaml"]
# ///
"""Live-updating task dashboard server with backward-compatible static generation.

Usage:
    uv run plan_dashboard.py serve [--root superRA/] [--port 8080] [--no-open]
    uv run plan_dashboard.py generate --plan-root PATH [--output PATH]
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import importlib.resources as resources
import json
import re
import socket
import sys
import webbrowser
from contextlib import asynccontextmanager
from dataclasses import replace
from pathlib import Path
from typing import AsyncGenerator

# ---------------------------------------------------------------------------
# Ensure sibling modules are importable
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))

from _task_io import TASK_ROOT_DIRNAME, Task, _walk_children, collect_all_tasks, parse_task, walk_plan
from _worktree_discovery import (
    WorktreeInfo,
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

# In-memory task tree and flat index
_root_task: Task | None = None
_task_index: dict[str, Task] = {}
_project_root: str = ""

# Watcher task (stored for cancellation on worktree switch)
_watcher_task: asyncio.Task | None = None

# Active worktree path (absolute); set from PLAN_ROOT at startup
_current_worktree_path: str = ""

# Concurrency guard for worktree switch sequence
_switch_lock: asyncio.Lock = asyncio.Lock()

# SSE broadcast: one asyncio.Queue per connected client
_sse_clients: set[asyncio.Queue[str]] = set()


# ---------------------------------------------------------------------------
# Data layer
# ---------------------------------------------------------------------------


def _build_index(task: Task, index: dict[str, Task]) -> None:
    """Recursively populate a flat path -> Task index."""
    index[task.path] = task
    for child in task.children:
        _build_index(child, index)


def rebuild_tree() -> None:
    """Full re-walk of the plan directory.  Updates root and index."""
    global _root_task, _task_index
    _root_task = walk_plan(PLAN_ROOT)
    _task_index = {}
    _build_index(_root_task, _task_index)


def rebuild_task(task_path: str) -> tuple[Task | None, bool]:
    """Re-parse a single task.md and update it in the index.

    Returns ``(updated_task, children_changed)``.  *updated_task* is ``None``
    when the file no longer exists.  *children_changed* is ``True`` when child
    directories were added or removed since the last index snapshot, signalling
    the caller to broadcast a full-reload instead of a single-task fragment.
    """
    global _root_task
    task_dir = PLAN_ROOT / task_path if task_path else PLAN_ROOT
    task_md = task_dir / "task.md"
    if not task_md.exists():
        _task_index.pop(task_path, None)
        return None, False
    try:
        updated = parse_task(task_md)
    except Exception:
        return _task_index.get(task_path), False

    # --- Re-discover children from the filesystem ---
    existing = _task_index.get(task_path)
    old_child_paths: set[str] = set()
    if existing is not None:
        old_child_paths = {c.path for c in existing.children}

    # Walk current child subdirectories that contain a task.md
    new_children = _walk_children(task_dir, PLAN_ROOT)
    new_child_paths = {c.path for c in new_children}

    children_changed = new_child_paths != old_child_paths

    updated.children = new_children

    # Update the flat index: register the task itself and all discovered
    # children; remove entries for children that no longer exist.
    _task_index[task_path] = updated
    for gone_path in old_child_paths - new_child_paths:
        _remove_from_index(gone_path)
    for child in new_children:
        _build_index(child, _task_index)

    # Patch the node inside the tree so the parent's reference stays valid
    _replace_node_in_tree(_root_task, task_path, updated)
    return updated, children_changed


def _remove_from_index(task_path: str) -> None:
    """Remove a task and all its descendants from the flat index."""
    task = _task_index.pop(task_path, None)
    if task is not None:
        for child in task.children:
            _remove_from_index(child.path)


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


def _find_task(path: str) -> Task | None:
    """O(1) task lookup by path."""
    return _task_index.get(path)


# ---------------------------------------------------------------------------
# SSE helpers
# ---------------------------------------------------------------------------


async def _broadcast(event: str, data: str) -> None:
    """Send an SSE-formatted message to every connected client.

    Multi-line data is handled per SSE spec: each line gets a ``data:`` prefix.
    """
    data_lines = "".join(f"data: {line}\n" for line in data.split("\n"))
    message = f"event: {event}\n{data_lines}\n"
    dead: list[asyncio.Queue[str]] = []
    for q in _sse_clients:
        try:
            q.put_nowait(message)
        except asyncio.QueueFull:
            dead.append(q)
    for q in dead:
        _sse_clients.discard(q)


# ---------------------------------------------------------------------------
# Filesystem watcher (watchfiles + debounce)
# ---------------------------------------------------------------------------


async def _watch_plan_root() -> None:
    """Background coroutine: watch plan_root for task.md / comments.yaml changes."""
    import watchfiles

    async for changes in watchfiles.awatch(PLAN_ROOT):
        # watchfiles already debounces (default 1600ms); the sleep adds a
        # short extra window so rapid back-to-back writes coalesce.
        await asyncio.sleep(0.2)

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
                rel = task_dir.relative_to(PLAN_ROOT)
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
            rebuild_tree()
            await _broadcast("full-reload", "{}")
            if _root_task is not None:
                summary_html = _render_summary()
                await _broadcast("summary-updated", summary_html)

        # Process content-only changes (skip paths already covered by the
        # structural full-reload above).
        content_paths = changed_paths - structural_parent_paths
        if content_paths:
            any_children_changed = False

            for task_path in content_paths:
                updated, children_changed = rebuild_task(task_path)
                if children_changed:
                    # A task.md edit that changes this task's own child set is
                    # structural too — let the client rebuild the sidebar.
                    any_children_changed = True
                elif updated is not None and _root_task is not None:
                    # Pure content edit: swap the body-free sidebar row. The
                    # client's active-card / children-DAG refresh keys off the
                    # event name, not this fragment, so a nav (no-body) row is
                    # the cheap, correct payload for the declarative sse-swap.
                    fragment = _render_nav_node(updated)
                    await _broadcast(f"task:{task_path}", fragment)

            if any_children_changed:
                rebuild_tree()
                await _broadcast("full-reload", "{}")

            if content_paths and _root_task is not None:
                summary_html = _render_summary()
                await _broadcast("summary-updated", summary_html)


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


def _render_task_fragment(task: Task) -> str:
    """Render the task_children.html template for a single task."""
    env = _get_jinja_env()
    template = env.get_template("task_children.html")
    return template.render(task=task, project_root=_project_root)


def _task_depth(task_path: str) -> int:
    """Return the depth of a task in the tree (0 for root children, etc.)."""
    if not task_path:
        return 0
    return task_path.count("/")


def _render_task_node(task: Task, depth: int | None = None) -> str:
    """Render a single task node via the task_node macro (for SSE swap).

    *depth* controls how many levels of children are rendered inline vs
    lazy-loaded.  When ``None``, the depth is inferred from the task's
    position in the tree (``task.path``).
    """
    if depth is None:
        depth = _task_depth(task.path)
    env = _get_jinja_env()
    template = env.from_string(
        '{%- from "task_node.html" import render_task_node -%}'
        '{{ render_task_node(task, project_root, depth=depth) }}'
    )
    return template.render(task=task, project_root=_project_root, depth=depth)


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


def _render_node_body(task: Task) -> str:
    """Render the node_body.html fragment (body-only) for a single task."""
    env = _get_jinja_env()
    template = env.get_template("node_body.html")
    return template.render(task=task, project_root=_project_root)


def _render_summary() -> str:
    """Render the summary_bar.html template."""
    env = _get_jinja_env()
    template = env.get_template("summary_bar.html")
    all_tasks = collect_all_tasks(_root_task) if _root_task else []
    return template.render(root_task=_root_task, all_tasks=all_tasks)


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: build task tree; spawn watcher.  Shutdown: cancel watcher."""
    global _project_root, _watcher_task, _current_worktree_path
    _project_root = str(PLAN_ROOT.resolve().parent)
    _current_worktree_path = _project_root
    rebuild_tree()
    _watcher_task = asyncio.create_task(_watch_plan_root())
    yield
    if _watcher_task is not None:
        _watcher_task.cancel()
        try:
            await _watcher_task
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan)


# --- Route: GET / ----------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the full dashboard page."""
    if _root_task is None:
        raise HTTPException(status_code=500, detail="Task tree not initialized")
    env = _get_jinja_env()
    template = env.get_template("base.html")
    all_tasks = collect_all_tasks(_root_task)
    html = template.render(
        root_task=_root_task,
        all_tasks=all_tasks,
        project_root=_project_root,
    )
    return HTMLResponse(content=html)


# --- Route: GET /tree (tree HTML fragment for AJAX full-reload fallback) ----

@app.get("/tree", response_class=HTMLResponse)
async def tree_fragment():
    """Return just the task tree HTML nodes (no page chrome)."""
    if _root_task is None:
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
    html = template.render(root_task=_root_task, project_root=_project_root)
    return HTMLResponse(content=html)


# --- Route: GET /nav (navigation-only tree fragment) -----------------------

@app.get("/nav", response_class=HTMLResponse)
async def nav_fragment():
    """Return the navigation-only tree (rows, no task bodies) for the sidebar.

    Mirrors /tree's root-or-children logic but renders nav_node (body-free).
    Children are inlined to depth 2; depth >=3 children are lazy-load stubs
    fetched via /nav/{path}.
    """
    if _root_task is None:
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
    html = template.render(root_task=_root_task)
    return HTMLResponse(content=html)


# --- Route: GET /events (SSE) ---------------------------------------------

@app.get("/events")
async def sse_events():
    """Server-Sent Events endpoint for live updates."""

    async def event_generator() -> AsyncGenerator[str, None]:
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=256)
        _sse_clients.add(queue)
        try:
            # Send an initial heartbeat so the connection is established
            yield ": heartbeat\n\n"
            while True:
                message = await queue.get()
                yield message
        except asyncio.CancelledError:
            pass
        finally:
            _sse_clients.discard(queue)

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
async def dag_view(root: str | None = None):
    """Render the DAG mermaid diagram partial.

    Without ``root``: the global view over the whole tree, clustered by subtree.
    With ``root=<task path>``: an inline per-subtree panel scoped to that task's
    direct children (their sibling dependency graph), reusing the same template.
    """
    if _root_task is None:
        raise HTTPException(status_code=500, detail="Task tree not initialized")
    env = _get_jinja_env()
    template = env.get_template("dag.html")
    if root:
        sub_root = _find_task(root)
        if sub_root is None:
            raise HTTPException(status_code=404, detail=f"Task not found: {root}")
        # Scope to the parent's direct children — the sibling-only graph.
        sub_tasks = list(sub_root.children)
        return HTMLResponse(content=template.render(root_task=sub_root, all_tasks=sub_tasks))
    all_tasks = collect_all_tasks(_root_task)
    return HTMLResponse(content=template.render(root_task=_root_task, all_tasks=all_tasks))


# --- Route: GET /kanban ------------------------------------------------------

@app.get("/kanban", response_class=HTMLResponse)
async def kanban_view():
    """Render the kanban board partial."""
    if _root_task is None:
        raise HTTPException(status_code=500, detail="Task tree not initialized")
    env = _get_jinja_env()
    template = env.get_template("kanban.html")
    all_tasks = collect_all_tasks(_root_task)
    return HTMLResponse(content=template.render(all_tasks=all_tasks))


# --- Route: GET /files/{path} ----------------------------------------------

@app.get("/files/{path:path}")
async def serve_file(path: str):
    """Serve files from the project root (for image embeds in markdown)."""
    file_path = Path(_project_root) / path
    resolved = file_path.resolve()
    project_resolved = Path(_project_root).resolve()

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
async def comments_summary():
    """Return ``{taskPath: unresolvedCount}`` for all tasks with unresolved comments."""
    if not _COMMENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Comments module not available")
    if _root_task is None:
        raise HTTPException(status_code=500, detail="Task tree not initialized")

    result: dict[str, int] = {}

    def _walk(task: Task) -> None:
        comments = load_comments(task.dir_path)
        unresolved = sum(1 for c in comments if not c.resolved)
        if unresolved > 0:
            result[task.path] = unresolved
        for child in task.children:
            _walk(child)

    _walk(_root_task)
    return result


@app.post("/api/task/{path:path}/comment")
async def create_comment(path: str, request: Request):
    """Create a comment on a task."""
    if not _COMMENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Comments module not available")
    task = _find_task(path)
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
async def list_comments(path: str):
    """List comments for a task."""
    if not _COMMENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Comments module not available")
    task = _find_task(path)
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
    task = _find_task(path)
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
async def remove_comment(path: str, comment_id: int):
    """Delete a comment."""
    if not _COMMENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Comments module not available")
    task = _find_task(path)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {path}")
    deleted = delete_comment(task.dir_path, comment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Comment not found: {comment_id}")
    return {"status": "deleted"}


# --- Worktree routes -------------------------------------------------------

@app.get("/api/worktrees")
async def list_worktrees():
    """Return discovered worktrees with plan info, ordered by last activity."""
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
            "current": _current_worktree_path,
            "worktrees": [
                {
                    "path": _current_worktree_path,
                    "branch": None,
                    "plan_title": plan_title,
                    "is_current": True,
                    "has_plan": True,
                    "is_agent": False,
                    "last_activity": None,
                }
            ],
        }

    filtered = filter_worktrees(all_wts)
    ordered = sort_worktrees(filtered)

    entries = []
    for w in ordered:
        is_current = (
            w.plan_root is not None
            and str(Path(w.plan_root).resolve()) == str(PLAN_ROOT.resolve())
        )
        entries.append(
            {
                "path": w.path,
                "branch": w.branch,
                "plan_title": w.plan_title,
                "is_current": is_current,
                "has_plan": w.plan_root is not None,
                "plan_root": w.plan_root,
                "is_agent": w.is_agent,
                "last_activity": w.last_activity,
            }
        )

    return {
        "current": _current_worktree_path,
        "worktrees": entries,
    }


@app.post("/api/worktree/switch")
async def switch_worktree(request: Request):
    """Hot-swap the active plan root to a different worktree."""
    global PLAN_ROOT, _project_root, _watcher_task, _current_worktree_path

    body = await request.json()
    plan_root_str = body.get("plan_root")
    if not plan_root_str:
        raise HTTPException(status_code=400, detail="Missing 'plan_root' field")

    new_plan_root = Path(plan_root_str).resolve()

    # Validate: must be a known worktree with a valid task root.
    all_wts = discover_worktrees()
    if not all_wts:
        raise HTTPException(status_code=404, detail="Not in a git repo; switching unavailable")

    # Find matching worktree
    target_wt: WorktreeInfo | None = None
    for w in all_wts:
        if w.plan_root is not None and str(Path(w.plan_root).resolve()) == str(new_plan_root):
            target_wt = w
            break

    if target_wt is None:
        raise HTTPException(
            status_code=404,
            detail=f"No worktree found with plan root: {new_plan_root}",
        )

    if not new_plan_root.is_dir() or not (new_plan_root / "task.md").is_file():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid plan root (missing task.md): {new_plan_root}",
        )

    # --- Atomic switch sequence (serialized via lock) ---
    async with _switch_lock:
        # Save previous state for rollback
        prev_plan_root = PLAN_ROOT
        prev_project_root = _project_root
        prev_worktree_path = _current_worktree_path

        # 1. Cancel existing watcher
        if _watcher_task is not None:
            _watcher_task.cancel()
            try:
                await _watcher_task
            except asyncio.CancelledError:
                pass
            _watcher_task = None

        try:
            # 2. Update PLAN_ROOT
            PLAN_ROOT = new_plan_root

            # 3. Rebuild tree
            rebuild_tree()

            # 4. Update project root and current worktree path
            _project_root = str(PLAN_ROOT.resolve().parent)
            _current_worktree_path = target_wt.path

            # 5. Spawn new watcher
            _watcher_task = asyncio.create_task(_watch_plan_root())
        except Exception:
            # Roll back to previous state
            PLAN_ROOT = prev_plan_root
            _project_root = prev_project_root
            _current_worktree_path = prev_worktree_path
            # Re-spawn watcher on the old root
            _watcher_task = asyncio.create_task(_watch_plan_root())
            raise HTTPException(
                status_code=500,
                detail="Switch failed; rolled back to previous worktree",
            )

        # 6. Broadcast full-reload
        await _broadcast("full-reload", "{}")

    return {
        "ok": True,
        "plan_root": str(PLAN_ROOT),
        "branch": target_wt.branch,
    }


# --- Route: GET /task/{path} -----------------------------------------------
# MUST come after comment routes — {path:path} is greedy and would swallow
# suffixes like /comments or /comment/123.

@app.get("/task/{path:path}", response_class=HTMLResponse)
async def get_task(path: str):
    """Return an HTML fragment with the children of the task at *path*."""
    task = _find_task(path)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {path}")
    html = _render_task_fragment(task)
    return HTMLResponse(content=html)


# --- Route: GET /nav/{path} (nav-only lazy children) -----------------------
# {path:path} is greedy; keep after the comment routes for the same reason as
# /task/{path}.  Returns body-free children so deep sidebar nodes lazy-load
# without pulling task bodies.

@app.get("/nav/{path:path}", response_class=HTMLResponse)
async def get_nav(path: str):
    """Return a navigation-only fragment with the children of the task at *path*."""
    task = _find_task(path)
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
async def get_node(path: str):
    """Return the body-only HTML fragment for the task at *path*."""
    task = _find_task(path)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {path}")
    html = _render_node_body(task)
    return HTMLResponse(content=html)


# --- Route: GET /export (standalone subtree download) ----------------------
# The "Share" button backs onto this: it renders the same standalone single-file
# HTML the CLI `generate --root <path>` produces, scoped to a subtree, and serves
# it with Content-Disposition: attachment so the browser saves a portable file.

@app.get("/export")
async def export_subtree(root: str = ""):
    """Return a self-contained standalone HTML dashboard scoped to *root*'s
    subtree as a file download.

    Empty *root* exports the whole tree.  The rendered HTML is identical to
    ``plan_dashboard.py generate [--root <path>]``: server-less, all fragments
    embedded inline, opens via ``file://``.  Restores live module state after
    rendering so the running server is unaffected.
    """
    if _root_task is None:
        raise HTTPException(status_code=500, detail="Task tree not initialized")
    if root and _find_task(root) is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {root}")

    # render_standalone_html drives module state (_root_task/_task_index) the way
    # generate_dashboard does, so snapshot and restore the live server's state.
    saved_root, saved_index, saved_project = _root_task, _task_index, _project_root
    try:
        html = render_standalone_html(PLAN_ROOT, root=root or None)
    finally:
        _set_module_state(saved_root, saved_index, saved_project)

    slug = root.rsplit("/", 1)[-1] if root else (_root_task.slug or "plan")
    filename = f"{slug or 'plan'}-dashboard.html"
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

    Returns ``markdown_it_js`` / ``katex_js`` / ``texmath_js`` (raw minified JS, emitted
    as inline ``<script>`` bodies) and ``katex_css`` (KaTeX CSS with every ``@font-face``
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
        "katex_css": css,
    }


def render_standalone_html(
    plan_root: Path,
    output_path: Path | None = None,
    root: str | None = None,
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
    return template.render(
        root_task=scoped_root,
        all_tasks=all_tasks,
        project_root=project_root,
        standalone=True,
        standalone_fragments=fragments,
        standalone_plan_dir=standalone_plan_dir,
        standalone_images=standalone_images,
        standalone_assets=standalone_assets,
    )


def generate_dashboard(
    plan_root: Path,
    output_path: Path | None = None,
    root: str | None = None,
) -> Path:
    """Generate a self-contained static HTML dashboard from base.html.

    Renders base.html in standalone mode with all server fragments pre-rendered
    and embedded inline, so the output opens via ``file://`` with zero network
    calls for task data.  Import-compatible with the previous implementation:
    same name, defaults ``output_path`` to ``plan_root / "dashboard.html"``,
    writes the file, prints the path, and returns it.  *root* scopes the export
    to a subtree (see ``render_standalone_html``).
    """
    if output_path is None:
        output_path = plan_root / "dashboard.html"

    html = render_standalone_html(plan_root, output_path, root)
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

    Maps into range 8100-8999. If the port is in use, tries the next port up
    (wrapping at 8999). Falls back to OS-assigned (port=0) after 10 attempts.
    """
    hash_source = git_common_dir if git_common_dir else str(plan_root.resolve())
    base_port = int(hashlib.sha256(hash_source.encode()).hexdigest(), 16) % 900 + 8100
    for i in range(10):
        port = 8100 + (base_port - 8100 + i) % 900
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) != 0:
                return port
    return 0


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
        "--no-open",
        action="store_true",
        help="Skip auto-opening the browser",
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

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if args.command == "serve":
        global PLAN_ROOT
        PLAN_ROOT = Path(args.root).resolve()

        if not PLAN_ROOT.exists():
            print(f"Error: plan root not found: {PLAN_ROOT}", file=sys.stderr)
            sys.exit(1)

        git_common_dir = get_git_common_dir()
        port = args.port if args.port is not None else _default_port(PLAN_ROOT, git_common_dir)

        import uvicorn

        url = f"http://localhost:{port}"
        if args.port is None:
            source = git_common_dir if git_common_dir else str(PLAN_ROOT)
            print(f"Starting dashboard at {url} (port derived from {source})")
        else:
            print(f"Starting dashboard at {url}")
        print(f"Watching: {PLAN_ROOT}")

        if not args.no_open:
            # Open browser after a short delay to let the server start
            import threading

            def _open_browser():
                import time
                time.sleep(1.0)
                webbrowser.open(url)

            threading.Thread(target=_open_browser, daemon=True).start()

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
        )

    elif args.command == "generate":
        plan_root = Path(args.plan_root)
        if not plan_root.exists():
            print(f"Error: plan root not found: {plan_root}", file=sys.stderr)
            sys.exit(1)
        output = Path(args.output) if args.output else None
        subtree_root = args.subtree_root or None
        try:
            generate_dashboard(plan_root, output, root=subtree_root)
        except KeyError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    else:
        # No subcommand given — print help
        parse_args(["--help"])


if __name__ == "__main__":
    main()
