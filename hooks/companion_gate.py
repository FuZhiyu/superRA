#!/usr/bin/env python3
"""PreToolUse gate: superRA workflow skills require their companions loaded first.

One table drives all gates. superRA:superplan is intentionally ungated on
agent-orchestration — at quick/standard depth it dispatches nothing; its
SKILL.md instructs the load at its one dispatch point (§Agent Review).

A companion counts as loaded when the session transcript or the skill ledger
records it (see skill_ledger.py). A single deny lists every missing companion,
so one retry clears the gate. Fails open when the transcript is empty or
unreadable. Test vectors: tests/hooks/test-ensure-companion.sh.
"""

from __future__ import annotations

import json
import re
import sys

import skill_ledger

REQUIREMENTS = {
    "superRA:superplan": ["superRA:using-superra"],
    "superRA:superimplement": ["superRA:using-superra", "superRA:agent-orchestration"],
    "superRA:superintegrate": ["superRA:using-superra", "superRA:agent-orchestration"],
}


def emit(payload: dict) -> None:
    print(json.dumps(payload, separators=(",", ":")))
    sys.exit(0)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        emit({})
    if not isinstance(data, dict):
        emit({})

    tool_input = data.get("tool_input", {}) or {}
    skill = tool_input.get("skill", "") if isinstance(tool_input, dict) else ""
    if data.get("tool_name", "") != "Skill" or not isinstance(skill, str) or not skill:
        emit({})
    companions = REQUIREMENTS.get(skill)
    if not companions:
        skill_ledger.record(data, skill)
        emit({})

    transcript_path = data.get("transcript_path", "") or ""
    try:
        transcript = open(transcript_path, encoding="utf-8", errors="replace").read()
    except OSError:
        emit({})

    ledger = skill_ledger.loaded(data)
    # Match the skill-name field tolerantly (case-insensitive, whitespace-tolerant
    # around the colon) so minor transcript-format drift does not cause a
    # spurious deny.
    missing = [
        companion
        for companion in companions
        if companion.lower() not in ledger
        and not re.search(
            r"\"skill\"\s*:\s*\"" + re.escape(companion) + r"\"", transcript, re.IGNORECASE
        )
    ]
    if not missing:
        skill_ledger.record(data, skill)
        emit({})

    names = " and ".join(f"\"{companion}\"" for companion in missing)
    plural = "s" if len(missing) > 1 else ""
    pronoun = "them" if len(missing) > 1 else "it"
    reason = (
        f"\"{skill}\" requires the companion skill{plural} {names} loaded first. "
        f"Load {pronoun}, then retry \"{skill}\"."
    )
    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }
    )


if __name__ == "__main__":
    main()
