#!/usr/bin/env python3
"""Live Claude Agent-SDK skill-load harness (manual-only).

Drives the Python ``claude_agent_sdk`` with in-process hooks so skill loading is
observable *by name*, reliably in headless mode — filesystem ``PreToolUse`` hooks
do not fire under ``claude -p`` (see references/load-testing-research.md). The
session is configured with the superRA plugin/skills directory so ``Skill(...)``
resolves; a ``PreToolUse(matcher="Skill")`` hook records every skill loaded by
name and its event index, and an ``InstructionsLoaded`` hook records auto-injected
CLAUDE.md / rules / always-loaded-skill loads.

This module is the *only* place ``claude_agent_sdk`` is imported, and the import
is deferred into :func:`run_skill_load_session`. The default CI path imports
:mod:`sdk_load_evidence` (and its unit test) instead, which never touches this
module, so the SDK dependency stays off the CI-safe path. Supply it on the live
path via ``uv run --with claude-agent-sdk``.

Gating mirrors the existing smokes:

- ``RUN_LIVE_HARNESS=1`` opt-in; a bare run is a documented no-op.
- ``CLAUDE_MODEL`` defaults to ``haiku`` (cheapest), overridable.
- ``CLAUDE_PLUGIN_DIR`` defaults to the repo root (resolved from this file).

Downstream smokes (10-12) call :func:`run_skill_load_session` and assert on the
returned :class:`~sdk_load_evidence.SkillLoadEvidence` via
:func:`~sdk_load_evidence.check_skills_loaded_before_first_edit`; they consume the
harness, not raw SDK calls.

Run standalone for a smoke check:

    RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk \\
      python tests/harness-instruction-following/sdk_load_harness.py
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from sdk_load_evidence import (
    InstructionsLoadedRecord,
    SkillLoadEvidence,
    SkillLoadRecord,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "task-trees" / "bundle-two-tasks"

# Edit/write tool names the Claude Agent SDK exposes (lowercased for matching).
EDIT_TOOL_NAMES = {"edit", "write", "multiedit", "notebookedit"}


class _EventCounter:
    """Monotonic event-index source shared across the registered hooks.

    The SDK fires hooks per tool-use / instruction-load; a single counter gives a
    total order so skill loads can be compared against the first edit/write even
    though they arrive through different hook callbacks.
    """

    def __init__(self) -> None:
        self._next = 0

    def take(self) -> int:
        index = self._next
        self._next += 1
        return index


def _gate_is_open() -> bool:
    return os.environ.get("RUN_LIVE_HARNESS") == "1"


def _plugin_dir() -> Path:
    override = os.environ.get("CLAUDE_PLUGIN_DIR")
    return Path(override).resolve() if override else REPO_ROOT


async def _run_session_async(
    *,
    prompt: str,
    cwd: Path,
    model: str,
    plugin_dir: Path,
    allowed_tools: list[str],
) -> SkillLoadEvidence:
    # Deferred import: keeps claude_agent_sdk off every default-CI import path.
    from claude_agent_sdk import (  # type: ignore import-not-found
        ClaudeAgentOptions,
        HookMatcher,
        query,
    )

    counter = _EventCounter()
    evidence = SkillLoadEvidence()

    async def on_skill_pretooluse(input_data, tool_use_id, context):
        index = counter.take()
        tool_input = input_data.get("tool_input", {}) if isinstance(input_data, dict) else {}
        name = (
            tool_input.get("name")
            or tool_input.get("skill")
            or tool_input.get("command")
            or input_data.get("tool_name", "<unknown>")
        )
        evidence.skill_loads.append(
            SkillLoadRecord(name=str(name), event_index=index, source="skill_tool")
        )
        return {}

    async def on_edit_pretooluse(input_data, tool_use_id, context):
        index = counter.take()
        if evidence.first_edit_index is None:
            evidence.first_edit_index = index
        return {}

    async def on_instructions_loaded(input_data, tool_use_id, context):
        index = counter.take()
        data = input_data if isinstance(input_data, dict) else {}
        file_path = str(data.get("file_path", "<unknown>"))
        memory_type = data.get("memory_type")
        load_reason = data.get("load_reason")
        evidence.instructions_loaded.append(
            InstructionsLoadedRecord(
                file_path=file_path,
                event_index=index,
                memory_type=memory_type,
                load_reason=load_reason,
            )
        )
        # An always-loaded skill surfaced as an InstructionsLoaded event (not a
        # Skill tool_use) still counts as that skill loading. Derive the skill
        # name from the loaded path so a required-skill assertion can match it.
        skill_name = _skill_name_from_path(file_path)
        if skill_name:
            evidence.skill_loads.append(
                SkillLoadRecord(
                    name=skill_name,
                    event_index=index,
                    source="instructions_loaded",
                )
            )
        return {}

    options = ClaudeAgentOptions(
        cwd=str(cwd),
        model=model,
        setting_sources=["project"],
        plugins=[str(plugin_dir)],
        allowed_tools=allowed_tools,
        permission_mode="acceptEdits",
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="Skill", hooks=[on_skill_pretooluse]),
                HookMatcher(matcher="Edit|Write", hooks=[on_edit_pretooluse]),
            ],
            "InstructionsLoaded": [
                HookMatcher(hooks=[on_instructions_loaded]),
            ],
        },
    )

    async for _message in query(prompt=prompt, options=options):
        # The hooks accumulate the evidence; messages are drained to completion.
        pass

    return evidence


def _skill_name_from_path(file_path: str) -> str | None:
    """Recover a superRA skill name from a loaded ``skills/<name>/SKILL.md`` path."""

    parts = Path(file_path).parts
    if "skills" in parts:
        idx = parts.index("skills")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return None


def run_skill_load_session(
    prompt: str,
    *,
    cwd: Path | str,
    model: str | None = None,
    plugin_dir: Path | str | None = None,
    allowed_tools: list[str] | None = None,
) -> SkillLoadEvidence:
    """Run one live SDK session and return structured skill-load evidence.

    Raises ``RuntimeError`` if the live gate (``RUN_LIVE_HARNESS=1``) is not set,
    so a CI run that imports this module by mistake fails loudly rather than
    making a model call.
    """

    if not _gate_is_open():
        raise RuntimeError(
            "RUN_LIVE_HARNESS is not set to 1 — the live SDK harness is "
            "manual-only and must never run in default CI."
        )

    resolved_model = model or os.environ.get("CLAUDE_MODEL", "haiku")
    resolved_plugin = Path(plugin_dir).resolve() if plugin_dir else _plugin_dir()
    resolved_tools = allowed_tools or ["Bash", "Read", "Write", "Skill"]

    return asyncio.run(
        _run_session_async(
            prompt=prompt,
            cwd=Path(cwd).resolve(),
            model=resolved_model,
            plugin_dir=resolved_plugin,
            allowed_tools=resolved_tools,
        )
    )


def _bundle_smoke_prompt() -> str:
    """Minimal prompt for the bundled fixture: read context, write a tiny JSON.

    Kept superficial per the parent objective — it should need the fixture
    context and a single JSON write, not a real coding task. The point of the
    live run is to confirm the in-process hooks record the skills the agent
    loaded by name (at minimum ``using-superra``), not to grade output.
    """

    return (
        "You are an implementer in this superRA workspace. Run "
        "`./superRA/superra task read agent-loading-bundle/02-primary-loading-task`, "
        "then write loading-evidence.json at the workspace root with "
        '{"artifact_content": "ARTIFACT_SENTINEL_QUARTZ"}. Do nothing else.'
    )


def _main() -> int:
    if not _gate_is_open():
        print(
            "SKIP  RUN_LIVE_HARNESS is not set to 1 — the SDK skill-load "
            "harness is opt-in and never runs in CI.\n"
            "      Set RUN_LIVE_HARNESS=1 (with claude-agent-sdk installed via "
            "uv run --with) to run it."
        )
        return 0

    import tempfile
    import shutil

    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp) / "ws"
        workspace.mkdir()
        shutil.copytree(FIXTURE_ROOT / "superRA", workspace / "superRA")
        shutil.copytree(FIXTURE_ROOT / "markers", workspace / "markers")
        wrapper = workspace / "superRA" / "superra"
        cli = REPO_ROOT / "skills" / "task-tree" / "scripts" / "cli.py"
        wrapper.write_text(
            "#!/usr/bin/env bash\n"
            f'exec python3 "{cli}" "$@"\n',
            encoding="utf-8",
        )
        wrapper.chmod(0o755)

        evidence = run_skill_load_session(
            _bundle_smoke_prompt(), cwd=workspace
        )

    print(f"skills loaded by name: {sorted(evidence.loaded_skill_names)}")
    print(f"instructions loaded:   {len(evidence.instructions_loaded)}")
    print(f"first edit index:      {evidence.first_edit_index}")

    if "using-superra" not in evidence.loaded_skill_names:
        print(
            "FAIL: expected at least 'using-superra' to load — that is a real "
            "finding in the loading contract, escalate it.",
        )
        return 1
    print("OK: using-superra loaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
