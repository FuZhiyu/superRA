#!/usr/bin/env python3
"""Stable structured findings for harness evaluators and diagnostic tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Finding:
    code: str
    outcome: str
    subject: str | None = None
    path: str | None = None
    event_index: int | None = None
    related_index: int | None = None
    actual: Any = None


def add_missing(report, code: str, message: str, **fields: Any) -> None:
    report.missing.append(message)
    report.findings.append(Finding(code=code, outcome="missing", **fields))


def add_observation(report, code: str, message: str, **fields: Any) -> None:
    report.observations.append(message)
    report.findings.append(Finding(code=code, outcome="observed", **fields))


def finding_codes(report, *, outcome: str | None = None) -> list[str]:
    return [
        finding.code
        for finding in report.findings
        if outcome is None or finding.outcome == outcome
    ]


def findings_for(report, code: str) -> list[Finding]:
    return [finding for finding in report.findings if finding.code == code]
