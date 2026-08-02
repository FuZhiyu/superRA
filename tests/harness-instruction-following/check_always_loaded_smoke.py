#!/usr/bin/env python3
"""Evaluate a live Codex always-loaded smoke run.

Parses the Codex JSONL transcript and the agent-written schema artifact, then
runs the :class:`~always_loaded_live.CODEX_SKILL_LOAD_CANARIES`
against existing ``command_execution`` events.

Usage:
    check_always_loaded_smoke.py --transcript <jsonl> --artifact <json>

Exit 0 when both commands and the exact artifact schema are present.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from always_loaded_live import (  # noqa: E402
    CODEX_SKILL_LOAD_CANARIES,
    EXPECTED_ARTIFACT,
)
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
        CODEX_SKILL_LOAD_CANARIES,
        command_strings=commands,
    )
    if artifact != EXPECTED_ARTIFACT:
        report.missing.append("always-loaded evidence artifact schema mismatch")

    for note in report.observations:
        print(f"observation: {note}")

    if report.ok:
        print("PASS codex always-loaded command and artifact evidence")
        return 0

    print("FAIL codex always-loaded canary:", file=sys.stderr)
    for msg in report.missing:
        print(f"  - {msg}", file=sys.stderr)
    print(
        "  An absent canary is a real loading-contract finding "
        "(role-skill body-load path) to escalate, not a test to relax.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
