#!/usr/bin/env python3
"""Evaluate a live Codex always-loaded canary run (task 10).

Parses the codex JSONL transcript and the agent-written canary artifact, then
runs the always-loaded :class:`~always_loaded_live.CODEX_ALWAYS_LOADED_CANARIES`
via 09's :func:`codex_load_evidence.evaluate_canaries`. Each canary's
skill-unique token must appear in a ``command_execution`` command or at its
artifact field — producible only if the always-loaded skill body loaded, which on
Codex (no autoload) means the role-spec body-load instruction was followed.

Usage:
    check_always_loaded_smoke.py --transcript <jsonl> --artifact <json>

Exit 0 when both canaries are present; exit 1 with a report otherwise. An absent
canary is a real "skill body did not load" finding to escalate.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from always_loaded_live import CODEX_ALWAYS_LOADED_CANARIES  # noqa: E402
from codex_load_evidence import (  # noqa: E402
    CanaryReport,
    command_strings_from_events,
    evaluate_canaries,
    load_artifact,
)
from transcript_assertions import parse_codex_jsonl  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--artifact", required=True)
    args = parser.parse_args()

    events = parse_codex_jsonl(args.transcript)
    commands = command_strings_from_events(events)
    artifact = load_artifact(args.artifact)

    report = CanaryReport()
    evaluate_canaries(
        report,
        CODEX_ALWAYS_LOADED_CANARIES,
        command_strings=commands,
        artifact=artifact,
    )

    for note in report.observations:
        print(f"observation: {note}")

    if report.ok:
        print("PASS codex always-loaded canary: both skill bodies evidenced loaded")
        return 0

    print("FAIL codex always-loaded canary:", file=sys.stderr)
    for msg in report.missing:
        print(f"  - {msg}", file=sys.stderr)
    print(
        "  An absent canary is a real always-loaded loading-contract finding "
        "(role-spec body-load path) to escalate, not a test to relax.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
