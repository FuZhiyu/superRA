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
for codex; the claude path still keys off Task/Agent tool events. When neither
the dispatch log (codex) nor the dispatch events (claude) show both subagents,
the run records the documented fallback only if the transcript names a direct-mode
switch with reviewer preservation AND names one of the three documented
direct-mode exceptions (no harness subagent support, explicit user override, or
documented task triviality), then skips rather than failing on invisible
behavior. A fabricated or undocumented "direct mode" reason does not qualify and
fails.

Usage:
    check_orchestrator_smoke.py --harness {claude,codex} --transcript <path> \\
        [--dispatch-log <path>]

Exit 0 when implementer+reviewer dispatch is observed (claude: dispatch events;
codex: SubagentStart log) OR a documented fallback is observed; exit 1 when
dispatch evidence is partial/absent with no documented fallback.
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

# The skip-pass fallback is taken only when a single transcript event names a
# direct-mode switch with reviewer preservation (FALLBACK_REQUIRED_NEEDLES) AND
# names at least one of superimplement's three documented direct-mode exceptions
# (FALLBACK_EXCEPTION_NEEDLES: no harness subagent support, explicit user
# override, or documented task triviality). Requiring a documented exception —
# not bare "direct mode" + "reviewer" co-occurrence — keeps a fabricated or
# undocumented reason from masking a genuinely missing subagent dispatch.
FALLBACK_REQUIRED_NEEDLES = ("direct mode", "reviewer")
FALLBACK_EXCEPTION_NEEDLES = (
    "no subagent",
    "no harness subagent",
    "lacks subagent",
    "harness lacks subagent",
    "without subagent",
    "subagents unavailable",
    "user requested",
    "user override",
    "user explicitly",
    "trivial",
    "triviality",
)


def _documented_fallback(events) -> bool:
    """True if a single transcript event names a documented direct-mode fallback."""

    return any(
        event.contains_all(FALLBACK_REQUIRED_NEEDLES)
        and event.contains_any(FALLBACK_EXCEPTION_NEEDLES)
        for event in events
    )


def _check_codex_with_dispatch_log(events, dispatch_log: str) -> AssertionReport:
    """Codex path: dispatch evidence is the SubagentStart log, not the JSONL.

    The hook log is the deterministic out-of-band signal (JSONL hides
    spawn_agent). When it shows both subagent types, pass; otherwise fall back to
    a documented direct-mode exception named in the transcript, else fail.
    """

    report = AssertionReport()
    dispatch_report = DispatchReport()
    evaluate_dispatch_log(dispatch_report, dispatch_log)
    report.observations.extend(dispatch_report.observations)
    if dispatch_report.ok:
        return report

    if _documented_fallback(events):
        report.skipped.append(
            "SubagentStart log shows no dispatch; documented direct-mode "
            "exception observed with reviewer preserved"
        )
        return report

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
        report = _check_codex_with_dispatch_log(events, dispatch_log_text)
    else:
        report = AssertionReport()
        check_orchestrator_dispatches(
            report,
            events,
            fallback_exception_needles=FALLBACK_EXCEPTION_NEEDLES,
            fallback_required_needles=FALLBACK_REQUIRED_NEEDLES,
        )

    for note in report.observations:
        print(f"observation: {note}")
    for note in report.skipped:
        print(f"limitation: {note}")

    if report.ok:
        if report.skipped:
            print(
                f"PASS {args.harness} orchestrator smoke: documented fallback "
                "observed (dispatch evidence unavailable)"
            )
        else:
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
