#!/usr/bin/env python3
"""Evaluate a live `superimplement` orchestrator transcript for dispatch evidence.

Used by the orchestrator behavior smoke. Asserts structural evidence that the
main agent followed the documented dispatch path instead of silently
implementing inline:

- An implementer subagent dispatch event for the frontier task, and
- a reviewer subagent dispatch event after it.

For the codex path, JSONL hides ``spawn_agent``, so dispatch evidence comes from
the ``SubagentStart`` hook's dispatch log (``--dispatch-log``), which records each
dispatched agent type out-of-band. This supersedes JSONL-based dispatch detection
for codex; the claude path still keys off Task/Agent tool events.

Usage:
    check_orchestrator_smoke.py --harness {claude,codex} --transcript <path> \\
        [--dispatch-log <path>]

Exit 0 when implementer+reviewer dispatch is observed (claude: dispatch events;
codex: SubagentStart log); exit 1 when dispatch evidence is partial or absent.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from codex_load_evidence import (  # noqa: E402
    DispatchReport,
    evaluate_dispatch_log,
)
from transcript_assertions import (  # noqa: E402
    AssertionReport,
    check_orchestrator_dispatches,
    parse_claude_stream_json,
    parse_codex_jsonl,
)

def _check_codex_with_dispatch_log(dispatch_log: str) -> AssertionReport:
    """Codex path: dispatch evidence is the SubagentStart log, not the JSONL."""

    report = AssertionReport()
    dispatch_report = DispatchReport()
    # Both seats spawn the default agent (the role is in the prompt, which the
    # hook payload does not carry), so the seats are counted, not named apart.
    evaluate_dispatch_log(dispatch_report, dispatch_log, minimum_dispatches=2)
    report.observations.extend(dispatch_report.observations)
    report.missing.extend(dispatch_report.missing)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harness", choices=("claude", "codex"), required=True)
    parser.add_argument("--transcript", required=True)
    parser.add_argument(
        "--dispatch-log",
        help="codex SubagentStart dispatch log (out-of-band dispatch evidence)",
    )
    args = parser.parse_args()

    if args.harness == "claude":
        events = parse_claude_stream_json(args.transcript)
    else:
        events = parse_codex_jsonl(args.transcript)

    if args.harness == "codex" and args.dispatch_log:
        dispatch_log_text = Path(args.dispatch_log).read_text(encoding="utf-8")
        report = _check_codex_with_dispatch_log(dispatch_log_text)
    else:
        report = AssertionReport()
        check_orchestrator_dispatches(report, events)

    for note in report.observations:
        print(f"observation: {note}")

    if report.ok:
        print(
            f"PASS {args.harness} orchestrator smoke: implementer + reviewer "
            "dispatch observed"
        )
        return 0

    print(f"FAIL {args.harness} orchestrator smoke:", file=sys.stderr)
    for msg in report.missing:
        print(f"  - {msg}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
