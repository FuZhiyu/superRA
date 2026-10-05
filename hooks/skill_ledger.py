"""Per-session ledger of Skill calls the companion gate allowed.

Claude Code writes a tool call to the session transcript a few seconds after
the call returns, so a gate that retries right after loading a companion can
read a transcript that does not show the load yet. Gates treat a skill as
loaded when either the transcript or this ledger records it.
"""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path


def _path(data: dict) -> Path | None:
    session = data.get("session_id") or data.get("conversation_id")
    if not isinstance(session, str) or not session:
        return None
    key = session
    agent = data.get("agent_id")
    if isinstance(agent, str) and agent:
        key += "." + agent
    root = os.environ.get("SUPERRA_SKILL_LEDGER_DIR") or os.path.join(
        tempfile.gettempdir(), "superRA-skill-loads"
    )
    return Path(root) / re.sub(r"[^A-Za-z0-9_.-]", "_", key)


def record(data: dict, skill: str) -> None:
    path = _path(data)
    if path is None or not skill:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(skill + "\n")
    except OSError:
        pass


def loaded(data: dict) -> set[str]:
    path = _path(data)
    if path is None:
        return set()
    try:
        return {line.strip().lower() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}
    except OSError:
        return set()
