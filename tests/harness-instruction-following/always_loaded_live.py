#!/usr/bin/env python3
"""Always-loaded skill coverage with static and command-event evidence.

Claude preloads ``superRA:using-superra`` and
``superRA:report-in-markdown`` from role frontmatter, so their loads do not emit
``Skill`` events. The deterministic contract parses that frontmatter.

Codex does not preload skills. Its live smoke checks the existing task-tree
wrapper-read and markdown-check ``command_execution`` events. The output
artifact carries only its schema version.
"""

from __future__ import annotations

from pathlib import Path

from codex_load_evidence import CanarySpec
from sdk_load_evidence import SkillLoadReport, check_always_loaded_frontmatter

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "task-trees" / "always-loaded-canary"
EXPECTED_ARTIFACT = {"schema_version": 1}

CODEX_REPORT_IN_MARKDOWN_CANARY = CanarySpec(
    skill="superRA:report-in-markdown",
    token="check_markdown.py",
)
CODEX_USING_SUPERRA_CANARY = CanarySpec(
    skill="superRA:using-superra",
    token="superra task read",
)
CODEX_ALWAYS_LOADED_CANARIES = (
    CODEX_REPORT_IN_MARKDOWN_CANARY,
    CODEX_USING_SUPERRA_CANARY,
)


def check_claude_always_loaded_static(
    report: SkillLoadReport,
    repo_root: Path | str = REPO_ROOT,
) -> None:
    """Check both role specs' always-loaded frontmatter declarations."""

    check_always_loaded_frontmatter(report, repo_root)
