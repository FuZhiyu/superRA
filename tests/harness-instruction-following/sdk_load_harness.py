#!/usr/bin/env python3
"""Live Claude Agent-SDK skill-load harness (manual-only).

Drives the Python ``claude_agent_sdk`` with in-process hooks so on-demand skill
loading is observable *by name*, reliably in headless mode — filesystem
``PreToolUse`` hooks do not fire under ``claude -p`` (see
references/load-testing-research.md).

The session is configured with the superRA plugin directory so ``Skill(...)``
resolves and the real plugin role agents (``superRA:implementer`` /
``superRA:reviewer``) are dispatchable, and it **dispatches the real role agent**
rather than running a bare ``query()`` — only a real role dispatch reproduces the
manifest-driven loads. A ``PreToolUse(matcher="Skill")`` hook records every skill
the agent loads on demand, by name; the live run confirmed it fires for an
explicit ``Skill(...)`` call. The linchpin for the downstream stage/domain smokes
(11/12) is that this hook *also* fires for tool use inside the dispatched
subagent — the SDK delivers subagent tool-lifecycle hooks, but the exact delivery
must be live-probed (see :func:`run_skill_load_session` and the standalone smoke
below, which print per-load source so the orchestrator can confirm subagent
loads are captured).

There is **no ``InstructionsLoaded`` hook**: it is not a registrable
``claude_agent_sdk`` ``HookEvent`` (the union is ``PreToolUse``, ``PostToolUse``,
``PostToolUseFailure``, ``UserPromptSubmit``, ``Stop``, ``SubagentStop``,
``PreCompact``, ``Notification``, ``SubagentStart``, ``PermissionRequest``), so
registering it is a silent no-op. Always-loaded skills (``using-superra``,
``report-in-markdown``) are preloaded via agent frontmatter ``skills: [...]`` and
are covered by the static frontmatter contract and the behavioral canary in
:mod:`sdk_load_evidence`, not by this hook.

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
    SkillLoadEvidence,
    SkillLoadRecord,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "task-trees" / "bundle-two-tasks"

# The plugin-qualified role agent the harness dispatches so manifest loads fire.
DEFAULT_AGENT_TYPE = "superRA:implementer"


class _EventCounter:
    """Monotonic event-index source shared across the registered hooks.

    The SDK fires hooks per tool-use; a single counter gives a total order so
    skill loads can be compared against the first edit/write even though they
    arrive through different hook callbacks, and whether the load happened in the
    top-level session or inside the dispatched subagent.
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


def _skill_name_from_tool_input(input_data) -> str:
    """Recover the skill name from a ``Skill`` PreToolUse payload.

    Defensive on key name (``name``/``skill``/``command``) so a minor SDK
    payload-shape difference degrades to ``<unknown>`` rather than crashing. The
    exact key should be confirmed against the installed SDK on the first live
    run (the live run that drove this revision recorded the name correctly).
    """

    tool_input = input_data.get("tool_input", {}) if isinstance(input_data, dict) else {}
    return str(
        tool_input.get("name")
        or tool_input.get("skill")
        or tool_input.get("command")
        or (input_data.get("tool_name", "<unknown>") if isinstance(input_data, dict) else "<unknown>")
    )


def _is_subagent_load(input_data) -> bool:
    """Did this hook fire for tool use inside a Task-dispatched subagent?

    The subagent attribution lives in the hook ``input_data`` (the SDK's
    ``_SubagentContextMixin``), not the ``context`` argument (which is just
    ``{'signal': None}``). Per the SDK, ``agent_id`` is "present only when the
    hook fires from inside a Task-spawned sub-agent; absent on the main thread",
    so it is the reliable discriminator; ``agent_type`` corroborates. Live-probed
    against the installed SDK: a subagent ``Skill`` load carries
    ``agent_id`` + ``agent_type='superRA:implementer'`` in ``input_data``.
    """

    if not isinstance(input_data, dict):
        return False
    return bool(input_data.get("agent_id") or input_data.get("agent_type"))


async def _run_session_async(
    *,
    prompt: str,
    cwd: Path,
    model: str,
    plugin_dir: Path,
    agent_type: str,
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
        name = _skill_name_from_tool_input(input_data)
        # source tags where the load happened so the orchestrator can confirm,
        # on the live path, that loads inside the dispatched subagent are
        # captured (the linchpin for the 11/12 stage/domain smokes).
        source = "subagent_skill_tool" if _is_subagent_load(input_data) else "skill_tool"
        evidence.skill_loads.append(
            SkillLoadRecord(name=name, event_index=index, source=source)
        )
        return {}

    async def on_edit_pretooluse(input_data, tool_use_id, context):
        index = counter.take()
        if evidence.first_edit_index is None:
            evidence.first_edit_index = index
        return {}

    options = ClaudeAgentOptions(
        cwd=str(cwd),
        model=model,
        setting_sources=["project"],
        plugins=[{"type": "local", "path": str(plugin_dir)}],
        allowed_tools=allowed_tools,
        permission_mode="acceptEdits",
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="Skill", hooks=[on_skill_pretooluse]),
                HookMatcher(matcher="Edit|Write", hooks=[on_edit_pretooluse]),
            ],
        },
    )

    # Dispatch the real plugin role agent rather than running the prompt at the
    # top level: only a real role dispatch reproduces the manifest-driven loads,
    # and it is what exercises the subagent tool-lifecycle hook path.
    dispatch_prompt = (
        f"Dispatch the {agent_type} agent (via the Task/Agent tool) with this "
        f"instruction, then stop:\n\n{prompt}"
    )

    async for _message in query(prompt=dispatch_prompt, options=options):
        # The hooks accumulate the evidence; messages are drained to completion.
        pass

    return evidence


def run_skill_load_session(
    prompt: str,
    *,
    cwd: Path | str,
    model: str | None = None,
    plugin_dir: Path | str | None = None,
    agent_type: str = DEFAULT_AGENT_TYPE,
    allowed_tools: list[str] | None = None,
) -> SkillLoadEvidence:
    """Run one live SDK session that dispatches the real role agent.

    Dispatches ``agent_type`` (default ``superRA:implementer``) so the
    manifest-driven on-demand loads fire, and returns the structured skill-load
    evidence captured by the in-process ``Skill`` hook (including loads inside
    the dispatched subagent, tagged via ``SkillLoadRecord.source``).

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
    resolved_tools = allowed_tools or ["Bash", "Read", "Write", "Skill", "Task", "Agent"]

    return asyncio.run(
        _run_session_async(
            prompt=prompt,
            cwd=Path(cwd).resolve(),
            model=resolved_model,
            plugin_dir=resolved_plugin,
            agent_type=agent_type,
            allowed_tools=resolved_tools,
        )
    )


def _bundle_smoke_prompt() -> str:
    """Minimal prompt for the bundled fixture: read context, write a tiny JSON.

    Kept superficial per the parent objective — it should need the fixture
    context and a single JSON write, not a real coding task. The point of the
    live run is to confirm the in-process ``Skill`` hook records the on-demand
    skills the dispatched agent loaded by name (the fixture's manifest
    stage/domain load), not to grade output.
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
    print("per-load source (confirm subagent loads are captured):")
    for record in evidence.skill_loads:
        print(f"  - {record.name}  [event {record.event_index}, {record.source}]")
    print(f"first edit index:      {evidence.first_edit_index}")

    subagent_loads = [r for r in evidence.skill_loads if r.source == "subagent_skill_tool"]
    if not subagent_loads:
        print(
            "WARN: no skill load was tagged subagent_skill_tool. Confirm whether "
            "the Skill hook fires for tool use inside the dispatched subagent — "
            "this is the linchpin for the 11/12 stage/domain smokes. If the hook "
            "does not see subagent loads, escalate before building 11/12 on it.",
        )
    if not evidence.loaded_skill_names:
        print(
            "FAIL: the dispatched agent loaded no on-demand skill via the Skill "
            "tool. Expected at least the fixture's manifest stage/domain load — "
            "that is a real finding in the loading contract, escalate it.",
        )
        return 1
    print(f"OK: dispatched {DEFAULT_AGENT_TYPE} and recorded on-demand skill loads.")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
