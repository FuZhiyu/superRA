#!/usr/bin/env python3
"""Codex ``SubagentStart`` hook: append the dispatched agent type to a log file.

Wired into the Codex live profile (matcher = agent type) by the orchestrator
live smoke. Codex JSONL exposes no ``spawn_agent`` item, so this hook is the
deterministic out-of-band signal that the main agent dispatched a subagent: on
every ``SubagentStart`` it reads the hook payload from stdin, pulls the agent
type (disambiguated by the agent-type field, never by ``session_id``), and
appends it to the file named by ``SUPERRA_SUBAGENT_LOG``.

Always exits 0 and prints ``{}`` so it never blocks or perturbs the codex run.
Stdlib-only and reuses the shared payload handler in :mod:`codex_load_evidence`,
which the CI-safe unit test exercises on synthetic payloads. The actual codex
dispatch is verified on the manual live path; CI only exercises the handler.

Usage (as a codex hook command):
    SUPERRA_SUBAGENT_LOG=/path/to/dispatch.log python3 subagent_start_hook.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from codex_load_evidence import append_subagent_start  # noqa: E402


def main() -> int:
    log_path = os.environ.get("SUPERRA_SUBAGENT_LOG")
    raw = sys.stdin.read()
    # Never fail the codex run on a malformed or empty payload: emit {} and exit
    # 0. A missing log path or unparseable payload simply records nothing.
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    if log_path and isinstance(payload, dict):
        append_subagent_start(log_path, payload)
    sys.stdout.write("{}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
