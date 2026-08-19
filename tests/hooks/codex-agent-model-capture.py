#!/usr/bin/env python3
"""Capture a Codex PreToolUse payload, then run the shared model guard."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


def main() -> int:
    raw = sys.stdin.read()
    log = os.environ.get("AGENT_MODEL_CAPTURE_LOG")
    if log:
        with Path(log).open("a", encoding="utf-8") as f:
            f.write(raw.rstrip("\n") + "\n")
    guard = Path(__file__).resolve().parents[2] / "hooks" / "agent-model-guard"
    proc = subprocess.run([str(guard)], input=raw, text=True, capture_output=True)
    sys.stdout.write(proc.stdout or "{}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
