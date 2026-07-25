#!/usr/bin/env python3
"""Evaluate a live Codex always-loaded behavior run.

Parses the Codex JSONL transcript and agent-written artifact. The transcript
must contain the task-read and markdown-validation command executions, and the
artifact must match the schema/task/path identity contract.

Usage:
    check_always_loaded_smoke.py --transcript <jsonl> --artifact <json>

Exit 0 when both commands and the artifact contract are present.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from always_loaded_live import (  # noqa: E402
    CODEX_ALWAYS_LOADED_COMMANDS,
    always_loaded_artifact_matches,
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
        CODEX_ALWAYS_LOADED_COMMANDS,
        command_strings=commands,
    )

    for note in report.observations:
        print(f"observation: {note}")

    artifact_ok = always_loaded_artifact_matches(artifact)
    if report.ok and artifact_ok:
        print("PASS codex always-loaded behavior: commands and artifact verified")
        return 0

    print("FAIL codex always-loaded behavior:", file=sys.stderr)
    for msg in report.missing:
        print(f"  - {msg}", file=sys.stderr)
    if not artifact_ok:
        print("  - output artifact schema/task/path identity mismatch", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
