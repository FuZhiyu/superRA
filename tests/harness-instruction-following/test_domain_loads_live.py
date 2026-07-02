#!/usr/bin/env python3
"""CI-safe unit tests for the per-domain skill-load live coverage (task 12).

Drives the domain evaluator and the per-domain Codex artifact canaries on
synthetic inputs — no model call, no ``claude_agent_sdk`` / codex-cli import:

- **Claude per-domain evaluator** (:func:`domain_loads_live.evaluate_domain_load`):
  green for each domain (skill loaded before edit via the Skill hook, including the
  ``superRA:``-qualified live shape); red when the domain skill never loads and when
  it loads after the first edit.
- **Claude multi-domain evaluator** (:func:`domain_loads_live.evaluate_multi_domain_load`):
  green when EVERY matching domain skill loaded; red when only one of several
  matching skills loaded (first-match instead of every-match) — the load-bearing
  case for task 12.
- **Codex per-domain canaries** (:func:`domain_loads_live.evaluate_codex_domain_canary`):
  green when the domain skill-unique token is in the artifact ``domain_canaries``
  list; red when absent; and the multi-domain Codex check requires every matched
  domain's token, red when one is missing.
- **Fixture sanity:** each committed expected artifact satisfies its domain canary,
  and the multi-domain artifact satisfies every multi-domain canary.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from sdk_load_evidence import evidence_from_hook_records  # noqa: E402
from domain_loads_live import (  # noqa: E402
    ALL_DOMAIN_SKILLS,
    DOMAIN_ROWS,
    MULTI_DOMAIN_CANARIES,
    MULTI_DOMAIN_SKILLS,
    MULTI_DOMAIN_WORDING,
    DomainLoadReport,
    domain_dispatch_prompt,
    domain_row,
    evaluate_all_domain_loads,
    evaluate_codex_domain_canary,
    evaluate_codex_multi_domain,
    evaluate_domain_load,
    evaluate_multi_domain_load,
)

FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "task-trees" / "domain-loads"


def test_default_ci_path_never_imports_sdk_or_codex():
    assert "claude_agent_sdk" not in sys.modules
    assert importlib.util.find_spec("domain_loads_live") is not None
    for mod in sys.modules:
        assert not mod.startswith("codex_cli"), mod


# --------------------------------------------------------------------------- #
# Table integrity
# --------------------------------------------------------------------------- #


def test_table_matches_manifest_domain_rows():
    # The four manifest domains are all present. A drift here means the table no
    # longer matches the Skill-Load Manifest Domain table.
    assert ALL_DOMAIN_SKILLS == {
        "econ-data-analysis",
        "theory-modeling",
        "writing",
        "slide-design",
    }


def test_multi_domain_is_a_genuine_superset():
    # The multi-domain case must require MORE than one domain, or it does not test
    # the "load every matching domain" rule.
    assert len(MULTI_DOMAIN_SKILLS) >= 2
    assert set(MULTI_DOMAIN_SKILLS) <= ALL_DOMAIN_SKILLS


def test_dispatch_prompt_carries_trigger_wording():
    row = domain_row("econ-data-analysis")
    prompt = domain_dispatch_prompt(row.trigger_wording)
    assert row.trigger_wording in prompt
    assert "domain-loads-task" in prompt


def test_domain_row_unknown_raises():
    try:
        domain_row("no-such-domain")
    except KeyError:
        return
    raise AssertionError("expected KeyError for unknown domain")


# --------------------------------------------------------------------------- #
# Claude per-domain evaluator
# --------------------------------------------------------------------------- #


def test_green_each_domain_loaded_before_edit():
    for row in DOMAIN_ROWS:
        evidence = evidence_from_hook_records(
            skill_tool_events=[(row.skill, 0)],
            edit_event_indices=[3],
        )
        report = DomainLoadReport()
        evaluate_domain_load(report, row, evidence)
        report.assert_ok()
        assert len(report.observations) == 1


def test_green_domain_loaded_as_plugin_qualified_name():
    # Live regression (caught in 11): the Skill tool records loads plugin-qualified
    # (superRA:econ-data-analysis); the table names them bare. The qualified load
    # must satisfy the bare expectation — a raw compare would be a false negative.
    row = domain_row("econ-data-analysis")
    evidence = evidence_from_hook_records(
        skill_tool_events=[("superRA:econ-data-analysis", 0), ("superRA:using-superra", 1)],
        edit_event_indices=[3],
    )
    report = DomainLoadReport()
    evaluate_domain_load(report, row, evidence)
    report.assert_ok()


def test_red_domain_never_loaded():
    row = domain_row("theory-modeling")
    evidence = evidence_from_hook_records(
        skill_tool_events=[("superRA:econ-data-analysis", 0)],  # wrong domain
        edit_event_indices=[3],
    )
    report = DomainLoadReport()
    evaluate_domain_load(report, row, evidence)
    assert not report.ok
    assert "theory-modeling" in report.missing[0]
    assert "never loaded" in report.missing[0]


def test_red_domain_loaded_after_first_edit():
    row = domain_row("writing")
    evidence = evidence_from_hook_records(
        skill_tool_events=[("writing", 5)],
        edit_event_indices=[2],
    )
    report = DomainLoadReport()
    evaluate_domain_load(report, row, evidence)
    assert not report.ok
    assert "before the first edit" in report.missing[0]


def test_evaluate_all_green_across_all_domains():
    evidence_by_domain = {
        row.skill: evidence_from_hook_records(skill_tool_events=[(row.skill, 0)])
        for row in DOMAIN_ROWS
    }
    report = DomainLoadReport()
    evaluate_all_domain_loads(report, evidence_by_domain)
    report.assert_ok()
    assert len(report.observations) == len(DOMAIN_ROWS)


def test_evaluate_all_reports_missing_evidence_for_a_domain():
    report = DomainLoadReport()
    evaluate_all_domain_loads(report, {})
    assert len(report.missing) == len(DOMAIN_ROWS)
    assert all("no captured evidence" in m for m in report.missing)


# --------------------------------------------------------------------------- #
# Claude multi-domain evaluator (the load-bearing case)
# --------------------------------------------------------------------------- #


def test_green_multi_domain_all_loaded():
    # Both matching domains loaded -> green. This is the "load every matching
    # domain" rule holding.
    evidence = evidence_from_hook_records(
        skill_tool_events=[
            ("superRA:theory-modeling", 0),
            ("superRA:writing", 1),
        ],
        edit_event_indices=[4],
    )
    report = DomainLoadReport()
    evaluate_multi_domain_load(report, MULTI_DOMAIN_SKILLS, evidence)
    report.assert_ok()
    assert len(report.observations) == len(MULTI_DOMAIN_SKILLS)


def test_red_multi_domain_loaded_only_one():
    # Only theory-modeling loaded; writing did not. First-match instead of
    # every-match is a real LC011–LC014 finding — must fail, naming the missing
    # domain.
    evidence = evidence_from_hook_records(
        skill_tool_events=[("superRA:theory-modeling", 0)],
        edit_event_indices=[4],
    )
    report = DomainLoadReport()
    evaluate_multi_domain_load(report, MULTI_DOMAIN_SKILLS, evidence)
    assert not report.ok
    assert any("writing" in m and "never loaded" in m for m in report.missing)
    # theory-modeling DID load, so it is not in the failures.
    assert not any("'theory-modeling' never loaded" in m for m in report.missing)


def test_red_multi_domain_none_loaded():
    evidence = evidence_from_hook_records(
        skill_tool_events=[("superRA:econ-data-analysis", 0)],
        edit_event_indices=[4],
    )
    report = DomainLoadReport()
    evaluate_multi_domain_load(report, MULTI_DOMAIN_SKILLS, evidence)
    assert not report.ok
    assert len(report.missing) == len(MULTI_DOMAIN_SKILLS)


# --------------------------------------------------------------------------- #
# Codex per-domain artifact canaries
# --------------------------------------------------------------------------- #


def test_green_codex_canary_each_domain_from_artifact_list():
    for row in DOMAIN_ROWS:
        report = DomainLoadReport()
        evaluate_codex_domain_canary(
            report,
            row.codex_canary,
            {"domain_canaries": [row.codex_canary.token]},
        )
        report.assert_ok()


def test_red_codex_canary_absent_for_a_domain():
    row = domain_row("slide-design")
    report = DomainLoadReport()
    evaluate_codex_domain_canary(
        report,
        row.codex_canary,
        {"domain_canaries": ["WRONG"]},
    )
    assert not report.ok
    assert "slide-design" in report.missing[0]
    assert "did not load" in report.missing[0]


def test_green_codex_multi_domain_all_tokens_present():
    artifact = {
        "domain_canaries": [spec.token for spec in MULTI_DOMAIN_CANARIES],
    }
    report = DomainLoadReport()
    evaluate_codex_multi_domain(report, MULTI_DOMAIN_CANARIES, artifact)
    report.assert_ok()
    assert len(report.observations) == len(MULTI_DOMAIN_CANARIES)


def test_red_codex_multi_domain_missing_one_token():
    # Only the first matched domain's token present -> the others fail.
    artifact = {"domain_canaries": [MULTI_DOMAIN_CANARIES[0].token]}
    report = DomainLoadReport()
    evaluate_codex_multi_domain(report, MULTI_DOMAIN_CANARIES, artifact)
    assert not report.ok
    assert len(report.missing) == len(MULTI_DOMAIN_CANARIES) - 1


def test_codex_canary_absent_artifact_fails():
    row = domain_row("econ-data-analysis")
    report = DomainLoadReport()
    evaluate_codex_domain_canary(report, row.codex_canary, None)
    assert not report.ok


# --------------------------------------------------------------------------- #
# Fixture sanity: committed expected artifacts satisfy the canaries
# --------------------------------------------------------------------------- #


def _load_expected(name: str) -> dict:
    return json.loads(
        (FIXTURE_ROOT / "expected" / f"{name}.expected.json").read_text(
            encoding="utf-8"
        )
    )


def test_committed_single_domain_artifacts_satisfy_canaries():
    for row in DOMAIN_ROWS:
        expected = _load_expected(row.skill)
        report = DomainLoadReport()
        evaluate_codex_domain_canary(report, row.codex_canary, expected)
        report.assert_ok()
        assert expected["domains"] == [row.skill]


def test_committed_multi_domain_artifact_satisfies_all_canaries():
    expected = _load_expected("multi-domain")
    report = DomainLoadReport()
    evaluate_codex_multi_domain(report, MULTI_DOMAIN_CANARIES, expected)
    report.assert_ok()
    assert set(expected["domains"]) == set(MULTI_DOMAIN_SKILLS)


def test_multi_domain_wording_is_nonempty_and_used():
    # The wording drives the live dispatch; an empty one would silently no-op.
    assert MULTI_DOMAIN_WORDING.strip()
    prompt = domain_dispatch_prompt(MULTI_DOMAIN_WORDING)
    assert MULTI_DOMAIN_WORDING in prompt
