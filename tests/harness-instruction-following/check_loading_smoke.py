#!/usr/bin/env python3
"""Evaluate a live loading-smoke transcript + artifact against the bundle contract.

Used by the Claude and Codex live smokes. Both harnesses run the same bundled
mock task (see live_smoke_lib.sh::smoke_task_prompt), so this evaluator is
shared: it parses the transcript with the shared assertions and compares the
agent-written artifact to the committed expected artifact.

Usage:
    check_loading_smoke.py --harness {claude,codex} \\
        --transcript <path> --artifact <path> --expected <path>

Exit 0 when every required-before-write load/read event is present and the
artifact matches; exit 1 with a report otherwise. Observations and skips
(harness limitations) are printed but do not fail the run.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from transcript_assertions import (  # noqa: E402
    AssertionReport,
    check_file_reads_before_write,
    check_json_artifact,
    check_task_reads_before_write,
    parse_claude_stream_json,
    parse_codex_jsonl,
)

PRIMARY_TASK = "agent-loading-bundle/02-primary-loading-task"
SECONDARY_TASK = "agent-loading-bundle/03-secondary-loading-task"
MARKER_PATHS = (
    "markers/primary-marker.txt",
    "markers/secondary-marker.txt",
    "markers/shared-marker.json",
)
ARTIFACT_NAME = "loading-evidence.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harness", choices=("claude", "codex"), required=True)
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--expected", required=True)
    args = parser.parse_args()

    if args.harness == "claude":
        events = parse_claude_stream_json(args.transcript)
    else:
        events = parse_codex_jsonl(args.transcript)

    report = AssertionReport()

    # Both task reads must precede the artifact write. The shared parser keys
    # task-read detection off a shell command running `superra task read <path>`,
    # which both harnesses expose as a command/exec event — the strongest
    # available observable for this requirement on either harness.
    check_task_reads_before_write(
        report,
        events,
        [PRIMARY_TASK, SECONDARY_TASK],
        write_path=ARTIFACT_NAME,
    )

    # The three marker files live outside the task tree, so they require an
    # explicit read tool / read command before the write.
    check_file_reads_before_write(
        report,
        events,
        MARKER_PATHS,
        write_path=ARTIFACT_NAME,
    )

    # The artifact can only be filled with the right sentinels if the agent
    # actually read the task-read context and markers; dependency_results_excluded
    # being true is the structural evidence that the dependency ## Results
    # sentinel never leaked into the target task-read context.
    artifact_path = Path(args.artifact)
    if not artifact_path.exists():
        report.missing.append(f"artifact {ARTIFACT_NAME}: file was never written")
    else:
        check_json_artifact(report, artifact_path, args.expected)

    for note in report.observations:
        print(f"observation: {note}")
    for note in report.skipped:
        print(f"limitation: {note}")

    if report.ok:
        print(f"PASS {args.harness} loading smoke: all required evidence present")
        return 0

    print(f"FAIL {args.harness} loading smoke:", file=sys.stderr)
    for msg in report.missing:
        print(f"  - {msg}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
