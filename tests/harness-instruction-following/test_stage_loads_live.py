#!/usr/bin/env python3
"""CI-safe unit tests for the per-stage skill-load live coverage (task 11).

Drives the stage evaluator and the per-stage Codex canaries on synthetic inputs —
no model call, no ``claude_agent_sdk`` / codex-cli import:

- **Claude per-stage evaluator** (:func:`stage_loads_live.evaluate_stage_load`):
  green for each non-empty stage (skill channel via the Skill hook; the
  ``planning-review`` reference via the opt-in Read hook); red when the stage skill
  never loads, when the reference is never read, and when a load lands after the
  first edit; and the negative stages (``implementation`` / ``documentation``)
  green when no stage skill loaded, red when one did (over-load).
- **Codex per-stage canaries** (09's :func:`codex_load_evidence.evaluate_canary`):
  green when the stage skill's skill-unique token is at the artifact field, red
  when absent (skill body did not load).
- **Read-path suffix matching** (:func:`sdk_load_evidence._read_path_matches`):
  an absolute/workspace-relative read path matches the manifest-relative
  reference path; an unrelated path does not.
- **Fixture sanity:** each committed expected artifact satisfies its stage canary.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from codex_load_evidence import CanaryReport, evaluate_canary  # noqa: E402
from sdk_load_evidence import (  # noqa: E402
    _read_path_matches,
    evidence_from_hook_records,
)
from stage_loads_live import (  # noqa: E402
    ALL_STAGE_SKILLS,
    CHANNEL_NONE,
    CHANNEL_READ,
    CHANNEL_SKILL,
    STAGE_ROWS,
    StageLoadReport,
    evaluate_all_stage_loads,
    evaluate_stage_load,
    stage_dispatch_prompt,
    stage_row,
)

FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "task-trees" / "stage-loads"


def test_default_ci_path_never_imports_sdk_or_codex():
    assert "claude_agent_sdk" not in sys.modules
    assert importlib.util.find_spec("stage_loads_live") is not None
    for mod in sys.modules:
        assert not mod.startswith("codex_cli"), mod


# --------------------------------------------------------------------------- #
# Table integrity
# --------------------------------------------------------------------------- #


def test_table_matches_manifest_stage_rows():
    # The four non-empty stages and the two negative stages are all present, with
    # the manifest skill/reference each maps to. A drift here means the table no
    # longer matches skills/using-superra/SKILL.md.
    by_stage = {row.stage: row for row in STAGE_ROWS}
    assert by_stage["planning-review"].channel == CHANNEL_READ
    assert (
        by_stage["planning-review"].expected
        == "skills/superplan/references/planning-review.md"
    )
    assert by_stage["protection"].expected == "result-protection"
    assert by_stage["sync"].expected == "semantic-merge"
    assert by_stage["integration"].expected == "refactor-and-integrate"
    assert by_stage["implementation"].channel == CHANNEL_NONE
    assert by_stage["documentation"].channel == CHANNEL_NONE
    assert ALL_STAGE_SKILLS == {
        "result-protection",
        "semantic-merge",
        "refactor-and-integrate",
    }


def test_dispatch_prompt_carries_stage_line():
    # The dispatched implementer/reviewer must load per the manifest for the
    # dispatch's Stage:, so the Stage: line must be in the prompt.
    prompt = stage_dispatch_prompt("integration")
    assert prompt.startswith("Stage: integration")
    assert "stage-loads-task" in prompt


def test_stage_row_unknown_raises():
    try:
        stage_row("no-such-stage")
    except KeyError:
        return
    raise AssertionError("expected KeyError for unknown stage")


# --------------------------------------------------------------------------- #
# Claude evaluator: skill-channel stages (protection / sync / integration)
# --------------------------------------------------------------------------- #


def test_green_skill_stage_loaded_before_edit():
    row = stage_row("protection")
    evidence = evidence_from_hook_records(
        skill_tool_events=[("result-protection", 0)],
        edit_event_indices=[3],
    )
    report = StageLoadReport()
    evaluate_stage_load(report, row, evidence)
    report.assert_ok()
    assert len(report.observations) == 1


def test_red_skill_stage_never_loaded():
    # The stage skill the manifest should trigger never loads — a real
    # LC007–LC010 finding; the assertion must fail.
    row = stage_row("sync")
    evidence = evidence_from_hook_records(
        skill_tool_events=[("result-protection", 0)],  # wrong skill
        edit_event_indices=[3],
    )
    report = StageLoadReport()
    evaluate_stage_load(report, row, evidence)
    assert not report.ok
    assert "semantic-merge" in report.missing[0]
    assert "never loaded" in report.missing[0]


def test_red_skill_stage_loaded_after_first_edit():
    row = stage_row("integration")
    evidence = evidence_from_hook_records(
        skill_tool_events=[("refactor-and-integrate", 5)],
        edit_event_indices=[2],
    )
    report = StageLoadReport()
    evaluate_stage_load(report, row, evidence)
    assert not report.ok
    assert "before the first edit" in report.missing[0]


# --------------------------------------------------------------------------- #
# Claude evaluator: read-channel stage (planning-review reference)
# --------------------------------------------------------------------------- #

_PLANNING_REF = "skills/superplan/references/planning-review.md"


def test_green_read_stage_reference_read_before_edit():
    row = stage_row("planning-review")
    # The captured read path is what the SDK Read payload carried — an absolute
    # path through the plugin install; the suffix matcher ties it to the manifest.
    evidence = evidence_from_hook_records(
        read_tool_events=[
            (f"/tmp/plugin/{_PLANNING_REF}", 0),
        ],
        edit_event_indices=[2],
    )
    report = StageLoadReport()
    evaluate_stage_load(report, row, evidence)
    report.assert_ok()
    assert "reference" in report.observations[0]


def test_red_read_stage_reference_never_read():
    row = stage_row("planning-review")
    # The agent read other files but never the planning-review reference — the
    # Skill hook cannot catch this (it loads via Read), so the Read channel must.
    evidence = evidence_from_hook_records(
        read_tool_events=[("/tmp/plugin/skills/superplan/SKILL.md", 0)],
        edit_event_indices=[2],
    )
    report = StageLoadReport()
    evaluate_stage_load(report, row, evidence)
    assert not report.ok
    assert _PLANNING_REF in report.missing[0]
    assert "never read" in report.missing[0]


def test_red_read_stage_reference_read_after_first_edit():
    row = stage_row("planning-review")
    evidence = evidence_from_hook_records(
        read_tool_events=[(f"/tmp/plugin/{_PLANNING_REF}", 4)],
        edit_event_indices=[1],
    )
    report = StageLoadReport()
    evaluate_stage_load(report, row, evidence)
    assert not report.ok
    assert "before the first edit" in report.missing[0]


def test_read_path_suffix_matches_absolute_not_substring_false_positive():
    # Absolute / workspace-relative path matches the manifest-relative reference.
    assert _read_path_matches(f"/abs/install/{_PLANNING_REF}", _PLANNING_REF)
    assert _read_path_matches(f"./{_PLANNING_REF}", _PLANNING_REF)
    # A different file in the same directory must NOT match.
    assert not _read_path_matches(
        "/abs/install/skills/superplan/references/task-tree-design.md",
        _PLANNING_REF,
    )
    # A path that merely contains the basename as a non-segment suffix must not
    # match (segment-boundary, not raw substring).
    assert not _read_path_matches(
        "/abs/install/skills/superplan/references/x-planning-review.md",
        _PLANNING_REF,
    )


# --------------------------------------------------------------------------- #
# Claude evaluator: negative stages (implementation / documentation)
# --------------------------------------------------------------------------- #


def test_green_negative_stage_no_stage_skill_loaded():
    row = stage_row("implementation")
    # A non-stage skill may load (e.g. a domain skill) without tripping the
    # negative check; only a *stage* skill load is an over-load.
    evidence = evidence_from_hook_records(
        skill_tool_events=[("econ-data-analysis", 0)],
        edit_event_indices=[2],
    )
    report = StageLoadReport()
    evaluate_stage_load(report, row, evidence)
    report.assert_ok()
    assert "negative case holds" in report.observations[0]


def test_red_negative_stage_loaded_a_stage_skill():
    row = stage_row("documentation")
    evidence = evidence_from_hook_records(
        skill_tool_events=[("refactor-and-integrate", 0)],
        edit_event_indices=[2],
    )
    report = StageLoadReport()
    evaluate_stage_load(report, row, evidence)
    assert not report.ok
    assert "over-load" in report.missing[0]
    assert "refactor-and-integrate" in report.missing[0]


# --------------------------------------------------------------------------- #
# evaluate_all_stage_loads (per-stage evidence map)
# --------------------------------------------------------------------------- #


def test_evaluate_all_green_across_all_stages():
    evidence_by_stage = {
        "planning-review": evidence_from_hook_records(
            read_tool_events=[(f"/p/{_PLANNING_REF}", 0)],
        ),
        "protection": evidence_from_hook_records(
            skill_tool_events=[("result-protection", 0)],
        ),
        "sync": evidence_from_hook_records(
            skill_tool_events=[("semantic-merge", 0)],
        ),
        "integration": evidence_from_hook_records(
            skill_tool_events=[("refactor-and-integrate", 0)],
        ),
        "implementation": evidence_from_hook_records(),
        "documentation": evidence_from_hook_records(),
    }
    report = StageLoadReport()
    evaluate_all_stage_loads(report, evidence_by_stage)
    report.assert_ok()
    assert len(report.observations) == len(STAGE_ROWS)


def test_evaluate_all_reports_missing_evidence_for_a_stage():
    report = StageLoadReport()
    evaluate_all_stage_loads(report, {})
    # every stage missing -> one failure each
    assert len(report.missing) == len(STAGE_ROWS)
    assert all("no captured evidence" in m for m in report.missing)


# --------------------------------------------------------------------------- #
# Codex per-stage canaries
# --------------------------------------------------------------------------- #


def test_green_codex_canary_each_positive_stage_from_artifact():
    for row in STAGE_ROWS:
        if row.codex_canary is None:
            continue
        report = CanaryReport()
        evaluate_canary(
            report,
            row.codex_canary,
            command_strings=[],
            artifact={"stage_canary": row.codex_canary.token},
        )
        report.assert_ok()


def test_red_codex_canary_absent_for_a_stage():
    row = stage_row("sync")
    report = CanaryReport()
    evaluate_canary(
        report,
        row.codex_canary,
        command_strings=[],
        artifact={"stage_canary": "WRONG"},
    )
    assert not report.ok
    assert "semantic-merge" in report.missing[0]
    assert "did not load" in report.missing[0]


# --------------------------------------------------------------------------- #
# Fixture sanity: committed expected artifacts satisfy the canaries
# --------------------------------------------------------------------------- #


def test_committed_expected_artifacts_satisfy_canaries():
    for row in STAGE_ROWS:
        if row.codex_canary is None:
            continue
        expected = json.loads(
            (FIXTURE_ROOT / "expected" / f"{row.stage}.expected.json").read_text(
                encoding="utf-8"
            )
        )
        report = CanaryReport()
        evaluate_canary(
            report,
            row.codex_canary,
            command_strings=[],
            artifact=expected,
        )
        report.assert_ok()


def test_negative_stage_expected_artifacts_use_none_sentinel():
    for stage in ("implementation", "documentation"):
        expected = json.loads(
            (FIXTURE_ROOT / "expected" / f"{stage}.expected.json").read_text(
                encoding="utf-8"
            )
        )
        assert expected["stage"] == stage
        assert expected["stage_canary"] == "none"
