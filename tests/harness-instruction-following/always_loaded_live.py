#!/usr/bin/env python3
"""Always-loaded skill coverage with static and command-event evidence.

``superRA:using-superra`` and ``superRA:communicate`` reach a dispatched agent
through the role skill's §Before You Start load instruction. The deterministic
contract parses that instruction.

Codex does not preload skills. Its live smoke checks the existing task-tree
wrapper-read ``command_execution`` event for ``superRA:using-superra`` plus the
markdown-check event for ``superRA:communicate``. The output artifact carries
only its schema version.
"""

from __future__ import annotations

from pathlib import Path

from codex_load_evidence import CanarySpec
from sdk_load_evidence import SkillLoadReport, check_always_loaded_load_instruction

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "task-trees" / "always-loaded-canary"
EXPECTED_ARTIFACT = {"schema_version": 1}

CODEX_COMMUNICATE_CANARY = CanarySpec(
    skill="superRA:communicate",
    token="check_markdown.py",
)
CODEX_USING_SUPERRA_CANARY = CanarySpec(
    skill="superRA:using-superra",
    token="superra task read",
)
CODEX_SKILL_LOAD_CANARIES = (
    CODEX_COMMUNICATE_CANARY,
    CODEX_USING_SUPERRA_CANARY,
)


def check_claude_always_loaded_static(
    report: SkillLoadReport,
    repo_root: Path | str = REPO_ROOT,
) -> None:
    """Check both role skills' always-loaded load instructions."""

    check_always_loaded_load_instruction(report, repo_root)
