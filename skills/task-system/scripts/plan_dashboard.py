# /// script
# requires-python = ">=3.10"
# dependencies = ["fastapi", "uvicorn[standard]", "jinja2", "watchfiles", "pyyaml"]
# ///
"""Live-updating task dashboard server with backward-compatible static generation.

Usage:
    uv run plan_dashboard.py serve [--root .plan/] [--port 8080] [--no-open]
    uv run plan_dashboard.py generate --plan-root PATH [--output PATH]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import webbrowser
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

# ---------------------------------------------------------------------------
# Ensure sibling modules are importable
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))

from _task_io import Task, collect_all_tasks, parse_task, walk_plan
from task_query import tree_to_json

# ---------------------------------------------------------------------------
# Optional comment module (created by another agent)
# ---------------------------------------------------------------------------
try:
    from _comments import (
        add_comment,
        delete_comment,
        load_comments,
        resolve_comment,
    )

    _COMMENTS_AVAILABLE = True
except ImportError:
    _COMMENTS_AVAILABLE = False

# ---------------------------------------------------------------------------
# Module-level state (configured before uvicorn.run)
# ---------------------------------------------------------------------------
PLAN_ROOT: Path = Path(".plan")

# In-memory task tree and flat index
_root_task: Task | None = None
_task_index: dict[str, Task] = {}
_project_root: str = ""

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


def rebuild_task(task_path: str) -> Task | None:
    """Re-parse a single task.md and update it in the index.

    Returns the updated Task or None if the file no longer exists.
    """
    global _root_task
    task_dir = PLAN_ROOT / task_path if task_path else PLAN_ROOT
    task_md = task_dir / "task.md"
    if not task_md.exists():
        _task_index.pop(task_path, None)
        return None
    try:
        updated = parse_task(task_md)
    except Exception:
        return _task_index.get(task_path)

    # Preserve children from the existing index entry
    existing = _task_index.get(task_path)
    if existing is not None:
        updated.children = existing.children

    _task_index[task_path] = updated

    # Patch the node inside the tree so the parent's reference stays valid
    _replace_node_in_tree(_root_task, task_path, updated)
    return updated


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
    """Send an SSE-formatted message to every connected client."""
    message = f"event: {event}\ndata: {data}\n\n"
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
        # Debounce: collect all changes over a 200ms window
        await asyncio.sleep(0.2)

        structural_change = False
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
                    structural_change = True
            elif change_type == watchfiles.Change.deleted:
                if name == "task.md":
                    structural_change = True
            else:
                changed_paths.add(task_path)

        if structural_change:
            rebuild_tree()
            await _broadcast("full-reload", "{}")
        else:
            for task_path in changed_paths:
                updated = rebuild_task(task_path)
                if updated is not None and _root_task is not None:
                    # Render the updated task HTML fragment
                    fragment = _render_task_fragment(updated)
                    data = json.dumps({"path": task_path, "html": fragment})
                    await _broadcast("task-updated", data)

                    # Also update summary bar
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

    from jinja2 import Environment, FileSystemLoader

    templates_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
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
    global _project_root
    _project_root = str(PLAN_ROOT.resolve().parent)
    rebuild_tree()
    watcher_task = asyncio.create_task(_watch_plan_root())
    yield
    watcher_task.cancel()
    try:
        await watcher_task
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
async def dag_view():
    """Render the DAG mermaid diagram partial."""
    if _root_task is None:
        raise HTTPException(status_code=500, detail="Task tree not initialized")
    env = _get_jinja_env()
    template = env.get_template("dag.html")
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
async def toggle_comment(path: str, comment_id: int):
    """Toggle resolved status of a comment."""
    if not _COMMENTS_AVAILABLE:
        raise HTTPException(status_code=501, detail="Comments module not available")
    task = _find_task(path)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task not found: {path}")
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


# ---------------------------------------------------------------------------
# Static HTML generation (backward compatibility)
# ---------------------------------------------------------------------------

# Keep the full DASHBOARD_HTML template from the old plan_dashboard.py for the
# `generate` subcommand.  It is a self-contained single-file HTML dashboard.

DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Plan Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/markdown-it@14/dist/markdown-it.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<style>
/* ── Light / Dark tokens ── */
:root {
  --font-display: 'Source Serif 4', 'Georgia', serif;
  --font-mono: 'IBM Plex Mono', 'Menlo', monospace;

  --bg:        #faf9f7;
  --bg-alt:    #f2f0ec;
  --bg-card:   #ffffff;
  --bg-hover:  #edeae4;
  --text:      #2c2a25;
  --text-mid:  #6b6560;
  --text-mute: #9e9890;
  --border:    #ddd8d0;
  --border-lt: #eae6df;
  --accent:    #b44d2d;
  --accent-hover: #953f24;
  --accent-soft: rgba(180,77,45,0.08);

  --tree-line: #d4cfc7;

  --st-ns:     #e8e5df;  --st-ns-t:   #8a857d;
  --st-ip:     #d6e6f5;  --st-ip-t:   #2a6496;
  --st-impl:   #f5edd4;  --st-impl-t: #8a6d1b;
  --st-rev:    #f5d9d4;  --st-rev-t:  #9b3228;
  --st-ok:     #d4e8d4;  --st-ok-t:   #2d6a30;

  --progress-bg:    #e8e5df;
  --progress-fill:  #6b9e6d;

  --kanban-bg: var(--bg-alt);
  --kanban-card-bg: var(--bg-card);
  --kanban-card-border: var(--border);

  --shadow-sm: 0 1px 2px rgba(44,42,37,0.06);
  --shadow-md: 0 2px 8px rgba(44,42,37,0.08);
}

[data-theme="dark"] {
  --bg:        #1c1b19;
  --bg-alt:    #252320;
  --bg-card:   #2c2a27;
  --bg-hover:  #353330;
  --text:      #e0ddd7;
  --text-mid:  #a09b93;
  --text-mute: #706b63;
  --border:    #3d3a35;
  --border-lt: #33302c;
  --accent:    #e07850;
  --accent-hover: #f09070;
  --accent-soft: rgba(224,120,80,0.10);

  --tree-line: #3d3a35;

  --st-ns:     #33312e;  --st-ns-t:   #9e9890;
  --st-ip:     #1f3248;  --st-ip-t:   #7ab0e0;
  --st-impl:   #3a3018;  --st-impl-t: #d4b64a;
  --st-rev:    #3e201c;  --st-rev-t:  #e08070;
  --st-ok:     #1e3320;  --st-ok-t:   #7ec080;

  --progress-bg:    #33312e;
  --progress-fill:  #5a9a5c;

  --kanban-bg: var(--bg-alt);
  --kanban-card-bg: var(--bg-card);
  --kanban-card-border: var(--border);

  --shadow-sm: 0 1px 2px rgba(0,0,0,0.2);
  --shadow-md: 0 2px 8px rgba(0,0,0,0.3);
}

/* ── Reset + base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 14px; -webkit-font-smoothing: antialiased; }
body {
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.5;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
}

/* ── Header bar ── */
.header {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; gap: 16px;
  padding: 10px 24px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}
.header-title {
  font-family: var(--font-display);
  font-size: 18px; font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text);
  white-space: nowrap;
}
.header-stats {
  display: flex; align-items: center; gap: 14px;
  margin-left: 8px;
  font-size: 12px; color: var(--text-mute);
}
.header-stats strong { color: var(--text-mid); font-weight: 600; }

/* Progress bar */
.progress-track {
  width: 120px; height: 6px;
  background: var(--progress-bg);
  border-radius: 3px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: var(--progress-fill);
  border-radius: 3px;
  transition: width 0.4s ease;
}

.header-spacer { flex: 1; }

/* Controls */
.header-controls {
  display: flex; align-items: center; gap: 6px;
}
.hc-btn, .hc-select {
  font-family: var(--font-mono);
  font-size: 12px;
  padding: 4px 10px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg);
  color: var(--text-mid);
  cursor: pointer;
  transition: all 0.15s ease;
}
.hc-btn:hover, .hc-select:hover { background: var(--bg-hover); color: var(--text); }
.hc-btn.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}
.hc-search {
  font-family: var(--font-mono);
  font-size: 12px;
  padding: 4px 10px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg);
  color: var(--text);
  width: 180px;
  transition: border-color 0.15s ease;
}
.hc-search:focus {
  outline: none;
  border-color: var(--accent);
}
.hc-search::placeholder { color: var(--text-mute); }
.theme-toggle {
  font-size: 16px; line-height: 1;
  background: none; border: none;
  color: var(--text-mute); cursor: pointer;
  padding: 4px;
  transition: color 0.15s ease;
}
.theme-toggle:hover { color: var(--text); }

/* ── Main content area ── */
.main-content {
  max-width: 960px;
  margin: 0 auto;
  padding: 20px 24px 60px;
}

/* ── Tree View ── */
.task-tree { }
.task-node {
  position: relative;
}
.task-node + .task-node { margin-top: 1px; }

/* Tree connector lines */
.task-children {
  position: relative;
  margin-left: 20px;
  padding-left: 16px;
  border-left: 1px solid var(--tree-line);
}

/* ── Task row (always visible) ── */
.task-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px;
  border-radius: 4px;
  cursor: pointer;
  user-select: none;
  transition: background 0.12s ease;
}
.task-row:hover { background: var(--bg-hover); }

.task-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px; height: 16px;
  font-size: 10px;
  color: var(--text-mute);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}
.task-toggle.expanded { transform: rotate(90deg); }
.task-toggle.leaf { visibility: hidden; }

.task-slug {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 500;
  color: var(--text);
  white-space: nowrap;
}
.task-title-text {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 400;
  color: var(--text-mid);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

/* Status badge */
.badge {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.03em;
  padding: 1px 7px;
  border-radius: 3px;
  white-space: nowrap;
  flex-shrink: 0;
}
.badge-not-started  { background: var(--st-ns);   color: var(--st-ns-t);   }
.badge-in-progress  { background: var(--st-ip);   color: var(--st-ip-t);   }
.badge-implemented  { background: var(--st-impl); color: var(--st-impl-t); }
.badge-revise       { background: var(--st-rev);  color: var(--st-rev-t);  }
.badge-approved     { background: var(--st-ok);   color: var(--st-ok-t);   }

.task-progress {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-mute);
  flex-shrink: 0;
}

/* ── Task body (expanded) ── */
.task-body {
  overflow: hidden;
  max-height: 0;
  opacity: 0;
  transition: max-height 0.3s ease, opacity 0.2s ease, padding 0.2s ease;
  padding: 0 8px 0 30px;
}
.task-body.open {
  max-height: 5000px;
  opacity: 1;
  padding: 4px 8px 8px 30px;
}

/* Section toggles inside task body */
.section-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  margin: 2px 0;
  border-radius: 3px;
  cursor: pointer;
  user-select: none;
  transition: background 0.12s ease;
}
.section-toggle:hover { background: var(--bg-hover); }
.section-icon {
  font-size: 9px;
  color: var(--text-mute);
  transition: transform 0.2s ease;
  width: 12px;
  text-align: center;
}
.section-icon.expanded { transform: rotate(90deg); }
.section-label {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  color: var(--text-mid);
}
.section-preview {
  font-size: 11px;
  color: var(--text-mute);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 400px;
}

.section-content {
  overflow: hidden;
  max-height: 0;
  opacity: 0;
  transition: max-height 0.3s ease, opacity 0.2s ease;
  padding-left: 20px;
}
.section-content.open {
  max-height: 8000px;
  opacity: 1;
  padding-bottom: 4px;
}

/* Rendered markdown inside sections */
.rendered-md {
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.6;
  color: var(--text);
  padding: 6px 0;
}
.rendered-md h1, .rendered-md h2, .rendered-md h3 {
  font-family: var(--font-display);
  font-weight: 600;
  margin: 12px 0 6px;
}
.rendered-md h1 { font-size: 16px; }
.rendered-md h2 { font-size: 14px; }
.rendered-md h3 { font-size: 13px; }
.rendered-md p { margin: 4px 0; }
.rendered-md ul, .rendered-md ol { padding-left: 18px; margin: 4px 0; }
.rendered-md li { margin: 2px 0; }
.rendered-md pre {
  background: var(--bg-alt);
  padding: 10px 12px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 6px 0;
  border: 1px solid var(--border-lt);
}
.rendered-md code {
  font-family: var(--font-mono);
  font-size: 12px;
}
.rendered-md p code, .rendered-md li code {
  background: var(--bg-alt);
  padding: 1px 4px;
  border-radius: 2px;
}
.rendered-md blockquote {
  border-left: 3px solid var(--accent);
  padding: 4px 12px;
  margin: 6px 0;
  background: var(--accent-soft);
  border-radius: 0 3px 3px 0;
}
.rendered-md table {
  border-collapse: collapse;
  margin: 6px 0;
  font-size: 12px;
}
.rendered-md th, .rendered-md td {
  border: 1px solid var(--border);
  padding: 4px 8px;
  text-align: left;
}
.rendered-md th { background: var(--bg-alt); font-weight: 600; }

/* Metadata pills inside task body */
.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid var(--border-lt);
}
.meta-pill {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-mute);
  background: var(--bg-alt);
  padding: 2px 7px;
  border-radius: 3px;
  white-space: nowrap;
}
.meta-pill strong { color: var(--text-mid); font-weight: 600; }

/* ── DAG view ── */
.dag-container {
  padding: 16px 0;
}
.dag-controls {
  font-family: var(--font-display);
  font-size: 14px;
  margin-bottom: 12px;
  color: var(--text-mid);
}
.dag-controls strong { color: var(--text); }

/* ── Kanban view ── */
.kanban {
  display: flex;
  gap: 14px;
  padding: 16px 0;
  overflow-x: auto;
  min-height: 400px;
}
.kanban-col {
  min-width: 200px;
  flex: 1;
  background: var(--kanban-bg);
  border-radius: 6px;
  padding: 10px;
}
.kanban-col-header {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  padding-bottom: 8px;
  margin-bottom: 8px;
  border-bottom: 2px solid var(--border);
  color: var(--text-mid);
}
.kanban-col-header .count {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-mute);
  font-weight: 400;
}
.kanban-card {
  padding: 8px 10px;
  margin-bottom: 6px;
  background: var(--kanban-card-bg);
  border: 1px solid var(--kanban-card-border);
  border-radius: 5px;
  cursor: pointer;
  font-size: 12px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.kanban-card:hover {
  border-color: var(--accent);
  box-shadow: var(--shadow-sm);
}
.kanban-card-title {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 12px;
  color: var(--text);
}
.kanban-card-path {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-mute);
  margin-top: 3px;
}

/* ── Utility ── */
.hidden { display: none !important; }

/* ── Animations ── */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}
.task-node { animation: fadeIn 0.15s ease both; }
.task-tree > .task-node:nth-child(1)  { animation-delay: 0.02s; }
.task-tree > .task-node:nth-child(2)  { animation-delay: 0.04s; }
.task-tree > .task-node:nth-child(3)  { animation-delay: 0.06s; }
.task-tree > .task-node:nth-child(4)  { animation-delay: 0.04s; }
.task-tree > .task-node:nth-child(5)  { animation-delay: 0.10s; }
.task-tree > .task-node:nth-child(6)  { animation-delay: 0.12s; }
.task-tree > .task-node:nth-child(7)  { animation-delay: 0.14s; }
.task-tree > .task-node:nth-child(8)  { animation-delay: 0.16s; }
.task-tree > .task-node:nth-child(9)  { animation-delay: 0.18s; }
.task-tree > .task-node:nth-child(10) { animation-delay: 0.20s; }
</style>
</head>
<body>

<!-- ── Header ── -->
<div class="header">
  <span class="header-title" id="plan-title">Plan Dashboard</span>
  <div class="header-stats">
    <span id="stat-tasks"></span>
    <span id="stat-approved"></span>
    <div class="progress-track"><div class="progress-fill" id="progress-fill"></div></div>
    <span id="stat-updated"></span>
  </div>
  <div class="header-spacer"></div>
  <div class="header-controls">
    <input type="text" class="hc-search" id="search-box" placeholder="Search tasks..." oninput="applyFilters()">
    <select class="hc-select" id="filter-status" onchange="applyFilters()">
      <option value="">All statuses</option>
      <option value="not-started">not-started</option>
      <option value="in-progress">in-progress</option>
      <option value="implemented">implemented</option>
      <option value="revise">revise</option>
      <option value="approved">approved</option>
    </select>
    <button class="hc-btn active" id="btn-tree" onclick="showView('tree')">Tree</button>
    <button class="hc-btn" id="btn-dag" onclick="showView('dag')">DAG</button>
    <button class="hc-btn" id="btn-kanban" onclick="showView('kanban')">Kanban</button>
    <button class="theme-toggle" onclick="toggleTheme()" title="Toggle dark/light mode">&#9681;</button>
  </div>
</div>

<!-- ── Content ── -->
<div class="main-content">
  <div id="view-tree" class="task-tree"></div>
  <div id="view-dag" class="dag-container hidden"></div>
  <div id="view-kanban" class="kanban hidden"></div>
</div>

<script>
const TASK_DATA = __TASK_DATA_JSON__;
const md = window.markdownit({ html: false, linkify: true });
let currentView = 'tree';
const taskByPath = {};
const expandedTasks = new Set();
const expandedSections = new Set();

/* ── Helpers ── */

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function sanitizeMermaid(s) {
  return s.replace(/"/g, "'").replace(/[\\[\\](){}]/g, '');
}

function flattenTasks(task) {
  let r = [task];
  for (const c of task.children) r = r.concat(flattenTasks(c));
  return r;
}

function buildIndex(task) {
  taskByPath[task.path] = task;
  for (const c of task.children) buildIndex(c);
}

function parseBodySections(body) {
  const lines = body.split('\\n');
  const sections = [];
  let cur = null;
  for (const line of lines) {
    const m = line.match(/^## (.+)$/);
    if (m) {
      if (cur) sections.push(cur);
      cur = { name: m[1], content: '' };
    } else if (cur) {
      cur.content += line + '\\n';
    }
  }
  if (cur) sections.push(cur);
  return sections;
}

function sectionPreview(content) {
  const stripped = content.replace(/\\n/g, ' ').replace(/[#*`>\\-]/g, '').trim();
  if (!stripped) return '';
  return stripped.length > 80 ? stripped.slice(0, 80) + '...' : stripped;
}

function taskMatches(task, status, search) {
  if (status && task.effective_status !== status) return false;
  if (search && !(task.title || '').toLowerCase().includes(search) &&
      !(task.path || '').toLowerCase().includes(search)) return false;
  return true;
}

function anyDescendantMatches(task, status, search) {
  if (taskMatches(task, status, search)) return true;
  for (const c of task.children) {
    if (anyDescendantMatches(c, status, search)) return true;
  }
  return false;
}

/* ── Init ── */

function init() {
  document.documentElement.setAttribute('data-theme',
    localStorage.getItem('dashboard-theme') || 'light');
  mermaid.initialize({ startOnLoad: false, theme: 'neutral' });
  buildIndex(TASK_DATA);
  renderSummary();
  renderTree();
}

/* ── Theme ── */

function toggleTheme() {
  const html = document.documentElement;
  const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('dashboard-theme', next);
}

/* ── View switching ── */

function showView(view) {
  currentView = view;
  document.querySelectorAll('.hc-btn').forEach(function(b) { b.classList.remove('active'); });
  document.getElementById('btn-' + view).classList.add('active');
  document.getElementById('view-tree').classList.toggle('hidden', view !== 'tree');
  document.getElementById('view-dag').classList.toggle('hidden', view !== 'dag');
  document.getElementById('view-kanban').classList.toggle('hidden', view !== 'kanban');
  if (view === 'dag') renderDag();
  if (view === 'kanban') renderKanban();
}

/* ── Summary bar ── */

function renderSummary() {
  const all = flattenTasks(TASK_DATA);
  const leaves = all.filter(function(t) { return t.is_leaf; });
  const approved = leaves.filter(function(t) { return t.effective_status === 'approved'; }).length;
  const pct = leaves.length ? Math.round(100 * approved / leaves.length) : 0;

  document.getElementById('plan-title').textContent = TASK_DATA.title || 'Plan Dashboard';
  document.getElementById('stat-tasks').innerHTML =
    '<strong>' + leaves.length + '</strong> tasks, <strong>' + (all.length - leaves.length) + '</strong> groups';
  document.getElementById('stat-approved').innerHTML =
    '<strong>' + approved + '/' + leaves.length + '</strong> approved';
  document.getElementById('progress-fill').style.width = pct + '%';
  const dates = all.map(function(t) { return t.updated; }).filter(Boolean).sort();
  if (dates.length) {
    document.getElementById('stat-updated').textContent = dates[dates.length - 1];
  }
}

/* ── Tree view (recursive expand/collapse) ── */

function renderTree() {
  const root = document.getElementById('view-tree');
  root.innerHTML = '';
  for (var i = 0; i < TASK_DATA.children.length; i++) {
    root.appendChild(renderTaskNode(TASK_DATA.children[i], 0));
  }
}

function renderTaskNode(task, depth) {
  const node = document.createElement('div');
  node.className = 'task-node';
  node.dataset.path = task.path;

  /* ── Row (always visible) ── */
  const row = document.createElement('div');
  row.className = 'task-row';

  const hasExpandable = task.children.length > 0 || (task.body && task.body.trim());
  const toggle = document.createElement('span');
  toggle.className = 'task-toggle' + (hasExpandable ? '' : ' leaf');
  toggle.textContent = '\\u25B8';

  const slug = document.createElement('span');
  slug.className = 'task-slug';
  const slugText = task.path ? task.path.split('/').pop() : '';
  slug.textContent = slugText;

  const titleSpan = document.createElement('span');
  titleSpan.className = 'task-title-text';
  titleSpan.textContent = task.title || '';

  const badge = document.createElement('span');
  badge.className = 'badge badge-' + task.effective_status;
  badge.textContent = task.effective_status;

  row.appendChild(toggle);
  if (slugText) row.appendChild(slug);
  row.appendChild(titleSpan);
  row.appendChild(badge);

  if (!task.is_leaf && task.children.length) {
    const approvedCount = task.children.filter(function(c) { return c.effective_status === 'approved'; }).length;
    const prog = document.createElement('span');
    prog.className = 'task-progress';
    prog.textContent = '(' + approvedCount + '/' + task.children.length + ')';
    row.appendChild(prog);
  }

  node.appendChild(row);

  /* ── Body (expandable) ── */
  const body = document.createElement('div');
  body.className = 'task-body';

  const sections = parseBodySections(task.body || '');
  const sectionKeys = ['Objective', 'Results', 'Decisions', 'Review Notes'];
  const shownSections = sections.filter(function(s) { return sectionKeys.indexOf(s.name) >= 0 && s.content.trim(); });
  const otherSections = sections.filter(function(s) { return sectionKeys.indexOf(s.name) < 0 && s.content.trim(); });
  var allSections = shownSections.concat(otherSections);

  for (var si = 0; si < allSections.length; si++) {
    (function(sec) {
      var secKey = task.path + '::' + sec.name;
      var secDiv = document.createElement('div');

      var secToggle = document.createElement('div');
      secToggle.className = 'section-toggle';
      var secIcon = document.createElement('span');
      secIcon.className = 'section-icon';
      secIcon.textContent = '\\u25B8';
      var secLabel = document.createElement('span');
      secLabel.className = 'section-label';
      secLabel.textContent = sec.name;
      var secPreview = document.createElement('span');
      secPreview.className = 'section-preview';
      secPreview.textContent = sectionPreview(sec.content);

      secToggle.appendChild(secIcon);
      secToggle.appendChild(secLabel);
      secToggle.appendChild(secPreview);

      var secContent = document.createElement('div');
      secContent.className = 'section-content';
      var rendered = document.createElement('div');
      rendered.className = 'rendered-md';

      secToggle.onclick = function(e) {
        e.stopPropagation();
        var isOpen = secContent.classList.toggle('open');
        secIcon.classList.toggle('expanded', isOpen);
        if (isOpen) {
          expandedSections.add(secKey);
          if (!rendered.innerHTML) {
            rendered.innerHTML = md.render(sec.content);
          }
          secPreview.style.display = 'none';
        } else {
          expandedSections.delete(secKey);
          secPreview.style.display = '';
        }
      };

      secContent.appendChild(rendered);
      secDiv.appendChild(secToggle);
      secDiv.appendChild(secContent);
      body.appendChild(secDiv);
    })(allSections[si]);
  }

  /* Metadata pills */
  var hasMeta = (task.depends_on && task.depends_on.length) ||
                task.script ||
                (task.tags && task.tags.length) ||
                (task.input && task.input.length) ||
                (task.output && task.output.length);
  if (hasMeta) {
    var metaDiv = document.createElement('div');
    metaDiv.className = 'task-meta';
    if (task.depends_on && task.depends_on.length) {
      var pill = document.createElement('span');
      pill.className = 'meta-pill';
      pill.innerHTML = '<strong>depends:</strong> ' + task.depends_on.map(function(d) { return esc(d); }).join(', ');
      metaDiv.appendChild(pill);
    }
    if (task.script) {
      var pill2 = document.createElement('span');
      pill2.className = 'meta-pill';
      pill2.innerHTML = '<strong>script:</strong> ' + esc(task.script);
      metaDiv.appendChild(pill2);
    }
    if (task.tags && task.tags.length) {
      var pill3 = document.createElement('span');
      pill3.className = 'meta-pill';
      pill3.innerHTML = '<strong>tags:</strong> ' + task.tags.map(function(t) { return esc(t); }).join(', ');
      metaDiv.appendChild(pill3);
    }
    if (task.input && task.input.length) {
      var pill4 = document.createElement('span');
      pill4.className = 'meta-pill';
      pill4.innerHTML = '<strong>in:</strong> ' + task.input.map(function(x) { return esc(x); }).join(', ');
      metaDiv.appendChild(pill4);
    }
    if (task.output && task.output.length) {
      var pill5 = document.createElement('span');
      pill5.className = 'meta-pill';
      pill5.innerHTML = '<strong>out:</strong> ' + task.output.map(function(x) { return esc(x); }).join(', ');
      metaDiv.appendChild(pill5);
    }
    body.appendChild(metaDiv);
  }

  node.appendChild(body);

  /* ── Children (recursive) ── */
  if (task.children.length) {
    var childrenDiv = document.createElement('div');
    childrenDiv.className = 'task-children';
    if (!expandedTasks.has(task.path)) childrenDiv.style.display = 'none';
    for (var ci = 0; ci < task.children.length; ci++) {
      childrenDiv.appendChild(renderTaskNode(task.children[ci], depth + 1));
    }
    node.appendChild(childrenDiv);
  }

  /* Restore expanded state on re-render */
  if (expandedTasks.has(task.path)) {
    toggle.classList.add('expanded');
    body.classList.add('open');
  }

  /* ── Click handler ── */
  (function(taskRef, toggleEl, bodyEl, nodeEl) {
    row.onclick = function(e) {
      e.stopPropagation();
      var isExpanded = expandedTasks.has(taskRef.path);
      if (isExpanded) {
        expandedTasks.delete(taskRef.path);
        toggleEl.classList.remove('expanded');
        bodyEl.classList.remove('open');
        var ch = nodeEl.querySelector(':scope > .task-children');
        if (ch) ch.style.display = 'none';
      } else {
        expandedTasks.add(taskRef.path);
        toggleEl.classList.add('expanded');
        bodyEl.classList.add('open');
        var ch2 = nodeEl.querySelector(':scope > .task-children');
        if (ch2) ch2.style.display = '';
      }
    };
  })(task, toggle, body, node);

  return node;
}

/* ── Filters ── */

function applyFilters() {
  var status = document.getElementById('filter-status').value;
  var search = document.getElementById('search-box').value.toLowerCase();
  document.querySelectorAll('.task-node').forEach(function(el) {
    var path = el.dataset.path || '';
    var task = taskByPath[path];
    if (!task) { el.style.display = ''; return; }
    var visible = anyDescendantMatches(task, status, search);
    el.style.display = visible ? '' : 'none';
  });
}

/* ── DAG view ── */

async function renderDag() {
  var container = document.getElementById('view-dag');
  var task = TASK_DATA;

  if (!task.children.length) {
    container.innerHTML = '<p style="color:var(--text-mute)">No subtasks to visualize.</p>';
    return;
  }

  var statusColors = {
    'not-started': '#e0e0e0', 'in-progress': '#bbdefb',
    'implemented': '#fff9c4', 'revise': '#ffcdd2', 'approved': '#c8e6c9'
  };

  var mermaidCode = 'graph LR\\n';
  var allTasks = flattenTasks(task).filter(function(t) { return t.path; });
  for (var i = 0; i < allTasks.length; i++) {
    var child = allTasks[i];
    var s = child.effective_status;
    var color = statusColors[s] || '#e0e0e0';
    var nodeId = child.path.replace(/[^a-zA-Z0-9_]/g, '_');
    mermaidCode += '    ' + nodeId + '["' + sanitizeMermaid(child.title || child.path) + '"]\\n';
    mermaidCode += '    style ' + nodeId + ' fill:' + color + '\\n';
  }
  for (var j = 0; j < allTasks.length; j++) {
    var ch = allTasks[j];
    var childId = ch.path.replace(/[^a-zA-Z0-9_]/g, '_');
    for (var k = 0; k < ch.depends_on.length; k++) {
      var depId = ch.depends_on[k].replace(/[^a-zA-Z0-9_]/g, '_');
      mermaidCode += '    ' + depId + ' --> ' + childId + '\\n';
    }
  }

  container.innerHTML = '<div class="dag-controls">' +
    '<strong>Dependency Graph:</strong> ' + esc(task.title || 'root') + '</div>' +
    '<div class="mermaid">' + mermaidCode + '</div>';

  try {
    await mermaid.run({ nodes: container.querySelectorAll('.mermaid') });
  } catch(e) {
    container.innerHTML += '<p style="color:var(--st-rev-t);margin-top:8px">DAG render error: ' + esc(e.message) + '</p>';
  }
}

/* ── Kanban view ── */

function renderKanban() {
  var container = document.getElementById('view-kanban');
  container.innerHTML = '';
  var statuses = ['not-started', 'in-progress', 'implemented', 'revise', 'approved'];
  var labels = {
    'not-started': 'Not Started', 'in-progress': 'In Progress',
    'implemented': 'Implemented', 'revise': 'Revise', 'approved': 'Approved'
  };
  var all = flattenTasks(TASK_DATA).filter(function(t) { return t.is_leaf && t.path; });

  for (var i = 0; i < statuses.length; i++) {
    var st = statuses[i];
    var col = document.createElement('div');
    col.className = 'kanban-col';
    var tasks = all.filter(function(t) { return t.effective_status === st; });
    col.innerHTML = '<div class="kanban-col-header">' + labels[st] +
      ' <span class="count">' + tasks.length + '</span></div>';
    for (var j = 0; j < tasks.length; j++) {
      (function(t) {
        var card = document.createElement('div');
        card.className = 'kanban-card';
        card.innerHTML = '<div class="kanban-card-title">' + esc(t.title || t.path) + '</div>' +
          '<div class="kanban-card-path">' + esc(t.path) + '</div>';
        card.onclick = function() { showView('tree'); expandToPath(t.path); };
        col.appendChild(card);
      })(tasks[j]);
    }
    container.appendChild(col);
  }
}

function expandToPath(path) {
  var parts = path.split('/');
  var accumulated = '';
  for (var i = 0; i < parts.length; i++) {
    accumulated = i === 0 ? parts[i] : accumulated + '/' + parts[i];
    expandedTasks.add(accumulated);
  }
  renderTree();
  requestAnimationFrame(function() {
    var el = document.querySelector('.task-node[data-path="' + path + '"]');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
}

document.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>
"""


def generate_dashboard(plan_root: Path, output_path: Path | None = None) -> Path:
    """Generate a self-contained static HTML dashboard (backward-compat)."""
    root = walk_plan(plan_root)
    data = tree_to_json(root)

    if output_path is None:
        output_path = plan_root / "dashboard.html"

    data_json = json.dumps(data, indent=2)
    data_json = data_json.replace("<", "\\u003c").replace(">", "\\u003e")
    html = DASHBOARD_HTML.replace("__TASK_DATA_JSON__", data_json)

    output_path.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {output_path}")
    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Task dashboard: live server or static HTML generation.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- serve ---
    serve_p = subparsers.add_parser("serve", help="Start the live dashboard server")
    serve_p.add_argument(
        "--root",
        default=".plan/",
        help="Path to the .plan/ directory (default: .plan/ in cwd)",
    )
    serve_p.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Server port (default: 8080)",
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

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if args.command == "serve":
        global PLAN_ROOT
        PLAN_ROOT = Path(args.root).resolve()

        if not PLAN_ROOT.exists():
            print(f"Error: plan root not found: {PLAN_ROOT}", file=sys.stderr)
            sys.exit(1)

        import uvicorn

        url = f"http://localhost:{args.port}"
        print(f"Starting dashboard server at {url}")
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
            port=args.port,
            log_level="info",
        )

    elif args.command == "generate":
        plan_root = Path(args.plan_root)
        if not plan_root.exists():
            print(f"Error: plan root not found: {plan_root}", file=sys.stderr)
            sys.exit(1)
        output = Path(args.output) if args.output else None
        generate_dashboard(plan_root, output)

    else:
        # No subcommand given — print help
        parse_args(["--help"])


if __name__ == "__main__":
    main()
