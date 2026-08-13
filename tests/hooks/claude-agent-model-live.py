#!/usr/bin/env python3
"""Opt-in Claude Agent SDK smoke for generic-agent model enforcement."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys

from claude_agent_sdk import ClaudeAgentOptions, HookMatcher, query


REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "hooks" / "agent-model-guard"


async def main() -> None:
    if os.environ.get("RUN_LIVE_HARNESS") != "1":
        raise SystemExit("RUN_LIVE_HARNESS=1 is required")

    agent_calls: list[dict] = []
    starts: list[dict] = []

    async def guard(input_data, tool_use_id, context):
        agent_calls.append(input_data)
        proc = subprocess.run(
            [str(GUARD)],
            input=json.dumps(input_data),
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(proc.stdout)

    async def record_start(input_data, tool_use_id, context):
        starts.append(input_data)
        return {}

    options = ClaudeAgentOptions(
        cwd=str(REPO_ROOT),
        model=os.environ.get("CLAUDE_MODEL", "haiku"),
        allowed_tools=["Agent", "Task"],
        permission_mode="acceptEdits",
        hooks={
            "PreToolUse": [HookMatcher(matcher="Agent", hooks=[guard])],
            "SubagentStart": [HookMatcher(matcher="general-purpose", hooks=[record_start])],
        },
    )
    prompt = (
        "Use one general-purpose Agent to reply with the word ready. "
        "On the first Agent call, omit model. When the hook denies it, retry "
        "with model=haiku. Do not use a named or specialized agent."
    )
    async for _ in query(prompt=prompt, options=options):
        pass

    inputs = [event.get("tool_input", {}) for event in agent_calls]
    generic = [item for item in inputs if item.get("subagent_type") in (None, "", "general-purpose")]
    denied = [item for item in generic if str(item.get("model", "")).strip().lower() in ("", "inherit")]
    allowed = [item for item in generic if str(item.get("model", "")).strip().lower() not in ("", "inherit")]
    if not denied or not allowed or not starts:
        raise SystemExit(
            "missing live evidence: "
            f"denied={len(denied)} allowed={len(allowed)} starts={len(starts)} "
            f"calls={json.dumps(inputs, sort_keys=True)}"
        )
    print(
        "PASS Claude live model guard: "
        f"denied={len(denied)} allowed={len(allowed)} starts={len(starts)}"
    )
    print(json.dumps({"denied": denied[0], "allowed": allowed[-1], "start": starts[-1]}, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
