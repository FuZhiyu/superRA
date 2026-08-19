#!/usr/bin/env python3
"""PreToolUse(Agent) gate: require explicit model controls on generic dispatches."""

from __future__ import annotations

import json
import sys


def _empty() -> None:
    print("{}")


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        _empty()
        return

    if not isinstance(payload, dict):
        _empty()
        return

    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        _empty()
        return

    reason = None
    if tool_name == "Agent":
        agent_type = tool_input.get("subagent_type")
        if agent_type in (None, "", "general-purpose"):
            model = tool_input.get("model")
            if not isinstance(model, str) or not model.strip() or model.strip().lower() == "inherit":
                reason = (
                    "Choose an explicit model for this generic Agent call, then retry; "
                    "model cannot be missing, empty, or inherit."
                )
    elif tool_name == "spawn_agent":
        agent_type = tool_input.get("agent_type")
        if agent_type in (None, "", "default"):
            missing = []
            for key in ("model", "reasoning_effort"):
                value = tool_input.get(key)
                if not isinstance(value, str) or not value.strip():
                    missing.append(key)
            if missing:
                reason = (
                    "Choose explicit "
                    + " and ".join(missing)
                    + " for this generic spawn_agent call, then retry."
                )

    if reason is None:
        _empty()
        return
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
