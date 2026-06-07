"""Comment sidecar handling for the task-system skill.

Provides a YAML-backed comment layer that lives alongside each task.md
as ``comments.yaml``.  Comments are anchored to specific blocks within
body sections and can be resolved/toggled by agents and humans.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from _task_io import parse_body_sections


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class CommentAnchor:
    section: str            # ## heading name
    block_index: int        # 0-indexed block within section
    text_preview: str       # first ~60 chars for fuzzy re-anchoring


@dataclass
class Comment:
    id: int
    author: str
    timestamp: str          # ISO 8601
    resolved: bool
    anchor: CommentAnchor
    body: str
    orphaned: bool = field(default=False, repr=False)


# ---------------------------------------------------------------------------
# YAML serialization helpers
# ---------------------------------------------------------------------------

def _comment_to_dict(c: Comment) -> dict:
    return {
        "id": c.id,
        "author": c.author,
        "timestamp": c.timestamp,
        "resolved": c.resolved,
        "anchor": {
            "section": c.anchor.section,
            "block_index": c.anchor.block_index,
            "text_preview": c.anchor.text_preview,
        },
        "body": c.body,
    }


def _dict_to_comment(d: dict) -> Comment:
    anchor = CommentAnchor(
        section=d["anchor"]["section"],
        block_index=d["anchor"]["block_index"],
        text_preview=d["anchor"]["text_preview"],
    )
    return Comment(
        id=d["id"],
        author=d["author"],
        timestamp=d["timestamp"],
        resolved=d["resolved"],
        anchor=anchor,
        body=d["body"],
    )


# ---------------------------------------------------------------------------
# Markdown block splitting
# ---------------------------------------------------------------------------

def split_into_blocks(section_content: str) -> list[str]:
    """Split a markdown section into block-level elements.

    Rules:
    - Fenced code blocks (``` delimited) are single blocks.
    - Consecutive list items (lines starting with ``- ``, ``* ``, or
      ``1. `` style) are grouped into a single block.
    - Paragraphs are separated by blank lines.

    Returns a list of block text strings (leading/trailing blank lines
    inside each block are stripped).
    """
    lines = section_content.split("\n")
    blocks: list[str] = []
    current: list[str] = []
    in_fence = False

    list_re = re.compile(r"^(\s*[-*+]|\s*\d+[.)]) ")

    def _flush() -> None:
        if current:
            text = "\n".join(current).strip()
            if text:
                blocks.append(text)
            current.clear()

    for line in lines:
        stripped = line.strip()

        # --- fenced code blocks ---
        if stripped.startswith("```"):
            if not in_fence:
                _flush()
                in_fence = True
                current.append(line)
            else:
                current.append(line)
                in_fence = False
                _flush()
            continue

        if in_fence:
            current.append(line)
            continue

        # --- blank line separates paragraphs ---
        if stripped == "":
            # If we're accumulating a list, a single blank line might
            # still be part of the same list in loose-list markdown, but
            # for anchoring purposes we treat a blank line as a boundary.
            _flush()
            continue

        # --- list items ---
        if list_re.match(line):
            # If current buffer is a non-list paragraph, flush first
            if current and not list_re.match(current[0]):
                _flush()
            current.append(line)
            continue

        # --- continuation of a list (indented non-blank after list item) ---
        if current and list_re.match(current[0]) and line.startswith("  "):
            current.append(line)
            continue

        # --- regular paragraph line ---
        if current and list_re.match(current[0]):
            _flush()
        current.append(line)

    _flush()
    return blocks


# ---------------------------------------------------------------------------
# Core sidecar I/O
# ---------------------------------------------------------------------------

def load_comments(task_dir: Path) -> list[Comment]:
    """Read ``comments.yaml`` from *task_dir*. Return [] if absent.

    The sidecar is written as JSON (a strict subset of YAML), so the common
    read path — including ``python3 task_read.py`` in an environment without
    ``pyyaml`` — parses it with the stdlib ``json`` module and never depends on
    a YAML library. Legacy block-style YAML files (written before the JSON
    switch) are still read via ``pyyaml`` when it is importable; the next
    ``save_comments`` rewrites them as JSON.
    """
    import json

    path = task_dir / "comments.yaml"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Legacy block-style YAML: only reachable with pyyaml present (the
        # environment that wrote it). Surface the failure rather than skip
        # silently so a legacy sidecar under bare python3 is never mistaken
        # for "no comments".
        try:
            import yaml
        except ModuleNotFoundError:
            raise RuntimeError(
                f"{path} is legacy YAML and pyyaml is unavailable; "
                "re-save it (any comment mutation) to upgrade it to JSON."
            )
        data = yaml.safe_load(text)
    if not data:
        return []
    return [_dict_to_comment(d) for d in data]


def save_comments(task_dir: Path, comments: list[Comment]) -> None:
    """Write *comments* to ``comments.yaml`` in *task_dir* as JSON.

    JSON is a strict subset of YAML, so the file stays a valid ``*.yaml`` for
    every existing reader while becoming parseable by the stdlib ``json``
    module (no ``pyyaml`` dependency on the read path).
    """
    import json

    path = task_dir / "comments.yaml"
    data = [_comment_to_dict(c) for c in comments]
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Author detection
# ---------------------------------------------------------------------------

def get_default_author() -> str:
    """Return the git user.name or ``'anonymous'``."""
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True, text=True, timeout=5,
        )
        name = result.stdout.strip()
        return name if name else "anonymous"
    except Exception:
        return "anonymous"


# ---------------------------------------------------------------------------
# Comment operations
# ---------------------------------------------------------------------------

def add_comment(
    task_dir: Path,
    section: str,
    block_index: int,
    text_preview: str,
    body: str,
    author: str | None = None,
) -> Comment:
    """Create a new comment, append it to the sidecar, and return it."""
    comments = load_comments(task_dir)
    next_id = max((c.id for c in comments), default=0) + 1
    comment = Comment(
        id=next_id,
        author=author or get_default_author(),
        timestamp=datetime.now().isoformat(),
        resolved=False,
        anchor=CommentAnchor(
            section=section,
            block_index=block_index,
            text_preview=text_preview,
        ),
        body=body,
    )
    comments.append(comment)
    save_comments(task_dir, comments)
    return comment


def resolve_comment(task_dir: Path, comment_id: int) -> Comment | None:
    """Toggle resolved status of *comment_id*. Return updated comment or None."""
    comments = load_comments(task_dir)
    target: Comment | None = None
    for c in comments:
        if c.id == comment_id:
            c.resolved = not c.resolved
            target = c
            break
    if target is None:
        return None
    save_comments(task_dir, comments)
    return target


def edit_comment(task_dir: Path, comment_id: int, body: str) -> Comment | None:
    """Update the body text of *comment_id*. Return updated comment or None."""
    comments = load_comments(task_dir)
    target: Comment | None = None
    for c in comments:
        if c.id == comment_id:
            c.body = body
            target = c
            break
    if target is None:
        return None
    save_comments(task_dir, comments)
    return target


def delete_comment(task_dir: Path, comment_id: int) -> bool:
    """Remove comment by ID. Return True if found and deleted."""
    comments = load_comments(task_dir)
    before = len(comments)
    comments = [c for c in comments if c.id != comment_id]
    if len(comments) == before:
        return False
    save_comments(task_dir, comments)
    return True


# ---------------------------------------------------------------------------
# Anchor resolution
# ---------------------------------------------------------------------------

def _reanchor(comment: Comment, sections: dict[str, str]) -> tuple[list[str], int] | None:
    """Re-resolve a single comment's anchor against parsed *sections*.

    Mutates ``comment.anchor.block_index`` (re-anchoring after the block
    moved) and ``comment.orphaned``.  Returns ``(blocks, block_index)`` of
    the section the comment resolves into, or ``None`` if the comment is
    orphaned (section gone, or preview matched no block).
    """
    anchor = comment.anchor
    section_content = sections.get(anchor.section)

    if section_content is None:
        comment.orphaned = True
        return None

    blocks = split_into_blocks(section_content)
    preview = anchor.text_preview.strip()

    # Check current index
    if (
        0 <= anchor.block_index < len(blocks)
        and preview in blocks[anchor.block_index]
    ):
        comment.orphaned = False
        return blocks, anchor.block_index

    # Scan for the preview elsewhere in the section
    for idx, block in enumerate(blocks):
        if preview in block:
            anchor.block_index = idx
            comment.orphaned = False
            return blocks, idx

    comment.orphaned = True
    return None


def resolve_anchors(comments: list[Comment], body: str) -> list[Comment]:
    """Re-resolve comment anchors against the current *body*.

    For each comment:
    1. Parse body into sections.
    2. Check whether ``anchor.block_index`` still matches
       ``anchor.text_preview`` in the section's blocks.
    3. If mismatch, scan all blocks in the section for the preview.
    4. If found, update ``block_index``.
    5. If not found, set ``orphaned = True`` (runtime flag, not persisted).
    """
    sections = parse_body_sections(body)
    for comment in comments:
        _reanchor(comment, sections)
    return comments


def anchored_block(comment: Comment, body: str) -> str | None:
    """Return the full text of the block *comment* is anchored to in *body*.

    Re-anchors against the live *body* using the same block-splitting and
    re-anchoring logic as :func:`resolve_anchors` (including after the block
    moved).  Returns ``None`` for an orphaned comment (section gone, or
    preview matched no block); does not raise.  Stdlib-only — usable without
    ``pyyaml`` since it operates on the body string.
    """
    sections = parse_body_sections(body)
    resolved = _reanchor(comment, sections)
    if resolved is None:
        return None
    blocks, idx = resolved
    return blocks[idx]
