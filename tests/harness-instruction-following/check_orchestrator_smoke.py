#!/usr/bin/env python3
"""Evaluate a live `superimplement` orchestrator transcript for dispatch evidence.

Used by the orchestrator behavior smoke. Asserts structural evidence that the
main agent followed the documented dispatch path instead of silently
implementing inline:

- An implementer subagent dispatch event for the frontier task, and
- a reviewer subagent dispatch event after it.

When the harness cannot expose subagent dispatch events at all, the run records
the documented fallback (the agent stating it is using direct mode for one of
the documented exceptions, with reviewer dispatch still preserved) and skips
rather than failing on invisible behavior.

Usage:
    check_orchestrator_smoke.py --harness {claude,codex} --transcript <path>

Exit 0 when implementer+reviewer dispatch events are present OR a documented
fallback is observed; exit 1 when dispatch evidence is partial/absent with no
documented fallback.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from transcript_assertions import (  # noqa: E402
    AssertionReport,
    check_orchestrator_dispatches,
    parse_claude_stream_json,
    parse_codex_jsonl,
)

# Needles that mark a documented direct-mode fallback in transcript text:
# the three documented exceptions in superimplement (no subagent support,
# explicit user override, documented task triviality). Detected only as a
# co-occurring pair so a stray "direct mode" mention does not mask a missing
# dispatch — the agent must both name direct mode and a documented reason.
FALLBACK_NEEDLES = ("direct mode", "reviewer")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harness", choices=("claude", "codex"), required=True)
    parser.add_argument("--transcript", required=True)
    args = parser.parse_args()

    if args.harness == "claude":
        events = parse_claude_stream_json(args.transcript)
    else:
        events = parse_codex_jsonl(args.transcript)

    report = AssertionReport()
    check_orchestrator_dispatches(
        report,
        events,
        fallback_needles=FALLBACK_NEEDLES,
    )

    for note in report.observations:
        print(f"observation: {note}")
    for note in report.skipped:
        print(f"limitation: {note}")

    if report.ok:
        if report.skipped:
            print(
                f"PASS {args.harness} orchestrator smoke: documented fallback "
                "observed (dispatch events unavailable)"
            )
        else:
            print(
                f"PASS {args.harness} orchestrator smoke: implementer + reviewer "
                "dispatch events present"
            )
        return 0

    print(f"FAIL {args.harness} orchestrator smoke:", file=sys.stderr)
    for msg in report.missing:
        print(f"  - {msg}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
