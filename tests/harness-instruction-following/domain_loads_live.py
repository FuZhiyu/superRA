#!/usr/bin/env python3
"""Per-domain skill-load live coverage (task 12), CI-safe core + manual live entry.

Verifies that a domain-worded fixture task loads its domain skill before domain
action (load-contracts LC003, LC011–LC014), in both harnesses, and that the
**multi-domain** case loads *every* matching domain skill (the manifest requires
loading every matching domain, not just the first):

- ``econ-data-analysis`` — wording about importing/cleaning/merging/regressing data
- ``theory-modeling``    — wording about deriving/solving/proving
- ``writing``            — wording about drafting/polishing reader-facing prose
- ``slide-design``       — wording about creating/revising slides/Beamer

One parametrized table (:data:`DOMAIN_ROWS`) is the single source of truth, so
adding a future domain is a one-row change. The trigger wording is kept close to
the manifest's Domain-table phrasing so the test reflects the documented contract.

All domain skills load through the ``Skill`` tool, so 08's
``PreToolUse(matcher="Skill")`` hook records them by name — the same channel as
the per-stage skill rows (11). There is no Read-channel / reference case here
(unlike 11's ``planning-review`` reference): every domain skill is a top-level
``Skill`` load. The evaluator reuses 08's :class:`SkillLoadEvidence` and 11's
plugin-prefix-insensitive name matching (live loads are ``superRA:``-qualified,
e.g. ``superRA:econ-data-analysis``; a raw compare against a bare expected name is
a false negative — this was live-caught in 11), so it does not re-implement
capture or name normalization.

The evaluator takes already-captured inputs (the dispatched agent's skill-load
evidence for Claude; the output artifact / command strings for Codex), so the
default ``pytest`` path drives it on synthetic inputs with no model call and no
``claude_agent_sdk`` / codex-cli import. The live Claude entry
:func:`run_claude_domain_canary` consumes 08's
:func:`sdk_load_harness.run_skill_load_session` and is gated behind
``RUN_LIVE_HARNESS=1``.

The live SDK dispatch is mildly nondeterministic (it leans on the top-level model
to issue the Task dispatch). The live entry defaults to ``sonnet`` and runs a
small pass@k window so a single flaky dispatch does not red a domain. A domain
whose triggering wording reliably does **not** load its skill — or the
multi-domain case loading only one of several matching skills — is a real
LC003/LC011–LC014 finding to record and escalate, not an assertion to relax. The
multi-domain case is the load-bearing one: it proves the "load every matching
domain" rule, not just first-match.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from codex_load_evidence import CanarySpec
from sdk_load_evidence import SkillLoadEvidence, normalize_skill_name

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "task-trees" / "domain-loads"


# --------------------------------------------------------------------------- #
# Codex per-domain canaries (skill-unique tokens, recorded in the artifact list)
# --------------------------------------------------------------------------- #

# Each token is a discriminating concept the domain skill body prescribes (named
# in the fixture task only as "the discriminating concept that domain's body
# prescribes"), so the agent can only write it once that body is in context.
# Recorded in the artifact list field `domain_canaries` (a domain skill has no
# bundled command side effect, so the artifact is the channel). A list rather than
# a scalar field so the multi-domain artifact can carry every matched domain's
# concept at once.
DOMAIN_CANARY_FIELD = "domain_canaries"

CODEX_ECON_CANARY = CanarySpec(
    skill="econ-data-analysis",
    token="describe before transform",
    in_command=False,
    in_artifact_field=DOMAIN_CANARY_FIELD,
)
CODEX_THEORY_CANARY = CanarySpec(
    skill="theory-modeling",
    token="comparative statics",
    in_command=False,
    in_artifact_field=DOMAIN_CANARY_FIELD,
)
CODEX_WRITING_CANARY = CanarySpec(
    skill="writing",
    token="audience model",
    in_command=False,
    in_artifact_field=DOMAIN_CANARY_FIELD,
)
CODEX_SLIDE_CANARY = CanarySpec(
    skill="slide-design",
    token="live communication",
    in_command=False,
    in_artifact_field=DOMAIN_CANARY_FIELD,
)


@dataclass(frozen=True)
class DomainRow:
    """One ``{domain_skill, trigger_wording}`` parametrization row.

    - ``skill`` is the manifest domain skill *name* (e.g. ``"econ-data-analysis"``),
      bare; the evaluator normalizes the recorded ``superRA:``-qualified load
      against it.
    - ``trigger_wording`` is the dispatch phrasing that should trigger this domain,
      kept close to the manifest Domain-table wording.
    - ``codex_canary`` is the per-domain :class:`CanarySpec` whose skill-unique
      token is only producible if that domain body loaded.
    """

    skill: str
    trigger_wording: str
    codex_canary: CanarySpec


# --------------------------------------------------------------------------- #
# The parametrized domain table (single source of truth)
# --------------------------------------------------------------------------- #

DOMAIN_ROWS: tuple[DomainRow, ...] = (
    DomainRow(
        skill="econ-data-analysis",
        trigger_wording=(
            "import, clean, merge, and run a regression on a panel of economic data"
        ),
        codex_canary=CODEX_ECON_CANARY,
    ),
    DomainRow(
        skill="theory-modeling",
        trigger_wording=(
            "derive the first-order conditions, solve for the equilibrium, and prove "
            "the result mathematically"
        ),
        codex_canary=CODEX_THEORY_CANARY,
    ),
    DomainRow(
        skill="writing",
        trigger_wording=(
            "draft and polish the reader-facing prose of the manuscript section"
        ),
        codex_canary=CODEX_WRITING_CANARY,
    ),
    DomainRow(
        skill="slide-design",
        trigger_wording=(
            "create and revise the Beamer presentation slides for this result"
        ),
        codex_canary=CODEX_SLIDE_CANARY,
    ),
)

DOMAIN_BY_SKILL: dict[str, DomainRow] = {row.skill: row for row in DOMAIN_ROWS}

# All domain skill names, for membership / over-load reasoning.
ALL_DOMAIN_SKILLS: frozenset[str] = frozenset(row.skill for row in DOMAIN_ROWS)


def domain_row(skill: str) -> DomainRow:
    """Return the :class:`DomainRow` for ``skill`` (raises if unknown)."""

    try:
        return DOMAIN_BY_SKILL[skill]
    except KeyError as exc:
        raise KeyError(f"no domain row for {skill!r}") from exc


# --------------------------------------------------------------------------- #
# Multi-domain case: wording matching more than one domain at once
# --------------------------------------------------------------------------- #

# The load-bearing case: wording that matches BOTH theory-modeling (derive a
# result) AND writing (write it up). The manifest requires loading EVERY matching
# domain, so the assertion below requires the FULL set, not just the first match.
MULTI_DOMAIN_SKILLS: tuple[str, ...] = ("theory-modeling", "writing")
MULTI_DOMAIN_WORDING = (
    "derive the equilibrium result and then draft the reader-facing prose that "
    "writes it up in the manuscript"
)
MULTI_DOMAIN_CANARIES: tuple[CanarySpec, ...] = tuple(
    DOMAIN_BY_SKILL[skill].codex_canary for skill in MULTI_DOMAIN_SKILLS
)


# --------------------------------------------------------------------------- #
# Claude evaluator (consumes 08's SkillLoadEvidence)
# --------------------------------------------------------------------------- #


@dataclass
class DomainLoadReport:
    """Collect every failed domain-load expectation from one evidence check."""

    missing: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing

    def assert_ok(self) -> None:
        if self.missing:
            joined = "\n".join(f"- {msg}" for msg in self.missing)
            raise AssertionError(f"Domain-load evidence failures:\n{joined}")


def _check_one_skill(
    report: DomainLoadReport,
    context: str,
    skill: str,
    evidence: SkillLoadEvidence,
) -> None:
    """Require ``skill`` to have loaded, before the first edit, in ``evidence``.

    Plugin-prefix-insensitive via 08/11's normalization: a load recorded as
    ``superRA:econ-data-analysis`` satisfies a bare expected ``econ-data-analysis``.
    """

    if normalize_skill_name(skill) not in evidence.loaded_skill_names:
        report.missing.append(
            f"{context}: required domain skill {skill!r} never loaded "
            f"(observed skill loads: {sorted(evidence.loaded_skill_names)})"
        )
    elif not evidence.loaded_before_first_edit(skill):
        report.missing.append(
            f"{context}: domain skill {skill!r} loaded at event "
            f"{evidence.first_load_index(skill)} but the first edit/write was at "
            f"event {evidence.first_edit_index} — must load before the first edit"
        )
    else:
        report.observations.append(
            f"{context}: domain skill {skill!r} loaded before first edit"
        )


def evaluate_domain_load(
    report: DomainLoadReport,
    row: DomainRow,
    evidence: SkillLoadEvidence,
) -> None:
    """Check one single-domain row: the manifest domain skill loaded before edit.

    A reliable failure is a real LC003/LC011–LC014 finding to escalate, not an
    assertion to relax.
    """

    _check_one_skill(report, f"domain {row.skill!r}", row.skill, evidence)


def evaluate_multi_domain_load(
    report: DomainLoadReport,
    expected_skills: tuple[str, ...],
    evidence: SkillLoadEvidence,
) -> None:
    """Check the multi-domain case: EVERY matching domain skill loaded before edit.

    The load-bearing assertion of task 12: when the dispatch wording matches more
    than one domain, the manifest requires loading *all* of them. Loading only one
    of several (first-match instead of every-match) is a real LC011–LC014 finding,
    so this requires the full set — each missing matching skill is reported.
    """

    context = f"multi-domain {sorted(expected_skills)}"
    for skill in expected_skills:
        _check_one_skill(report, context, skill, evidence)


def evaluate_all_domain_loads(
    report: DomainLoadReport,
    evidence_by_domain: dict[str, SkillLoadEvidence],
) -> None:
    """Evaluate every single-domain row against its per-domain captured evidence."""

    for row in DOMAIN_ROWS:
        if row.skill not in evidence_by_domain:
            report.missing.append(
                f"domain {row.skill!r}: no captured evidence supplied"
            )
            continue
        evaluate_domain_load(report, row, evidence_by_domain[row.skill])


# --------------------------------------------------------------------------- #
# Codex artifact-list canary (the multi-domain artifact carries several tokens)
# --------------------------------------------------------------------------- #


def domain_canary_in_artifact(spec: CanarySpec, artifact: dict | None) -> bool:
    """True if ``spec.token`` is present in the artifact's ``domain_canaries`` list.

    The per-domain Codex canary records its discriminating concept as one entry of
    the artifact list field :data:`DOMAIN_CANARY_FIELD`, so the multi-domain
    artifact can carry every matched domain's concept at once. Membership (not
    scalar equality) is the right test here — :func:`codex_load_evidence.evaluate_canary`'s
    dotted-field path checks a scalar field, which cannot express a multi-token
    artifact, so the list channel uses this helper instead.
    """

    if spec.in_artifact_field is None or artifact is None:
        return False
    values = artifact.get(spec.in_artifact_field)
    if isinstance(values, str):
        return spec.token == values
    if isinstance(values, (list, tuple)):
        return spec.token in values
    return False


def evaluate_codex_domain_canary(
    report: DomainLoadReport,
    spec: CanarySpec,
    artifact: dict | None,
) -> None:
    """Check one Codex domain canary against the artifact ``domain_canaries`` list.

    Passes if the domain's skill-unique token is present in the list; fails
    otherwise — an absent canary is a real "domain skill body did not load"
    finding, not a test bug.
    """

    if domain_canary_in_artifact(spec, artifact):
        report.observations.append(
            f"codex canary for domain {spec.skill!r} present in artifact field "
            f"{spec.in_artifact_field!r}"
        )
        return
    report.missing.append(
        f"codex canary for domain {spec.skill!r} (token {spec.token!r}) absent "
        f"from artifact field {spec.in_artifact_field!r} — the skill-unique "
        f"concept was not produced, so the domain skill body did not load"
    )


def evaluate_codex_multi_domain(
    report: DomainLoadReport,
    specs: tuple[CanarySpec, ...],
    artifact: dict | None,
) -> None:
    """Multi-domain Codex check: EVERY matched domain's token is in the artifact.

    The Codex counterpart to :func:`evaluate_multi_domain_load`: a multi-domain
    artifact that carries only one of several matched domains' concepts is a
    first-match-instead-of-every-match finding, so each missing token is reported.
    """

    for spec in specs:
        evaluate_codex_domain_canary(report, spec, artifact)


# --------------------------------------------------------------------------- #
# Live Claude entry (manual-only; consumes 08's harness)
# --------------------------------------------------------------------------- #


def _gate_is_open() -> bool:
    return os.environ.get("RUN_LIVE_HARNESS") == "1"


def domain_dispatch_prompt(trigger_wording: str) -> str:
    """The per-domain dispatch instruction: carries the domain-triggering wording.

    The fixture body is shared across domains; only the wording differs, so the
    dispatched implementer loads every domain skill the manifest maps that wording
    to before acting. Kept superficial per the parent objective — read the fixture
    context and write one tiny evidence JSON, no real domain work.
    """

    return (
        "You are an implementer in this superRA workspace. Your task is to "
        f"{trigger_wording}. First run "
        "`./superRA/superra task read domain-loads-task`, load every domain skill "
        "the Skill-Load Manifest maps that work to, then write "
        "domain-loads-evidence.json at the workspace root exactly as the task "
        "objective specifies. Do nothing else — do not do the actual domain work."
    )


def run_claude_domain_canary(
    skills_expected: tuple[str, ...],
    trigger_wording: str,
    *,
    cwd: Path | str,
    model: str | None = None,
    attempts: int = 3,
) -> DomainLoadReport:
    """Run the live Claude per-domain skill-load canary (manual-only).

    Dispatches the real ``superRA:implementer`` via 08's
    :func:`sdk_load_harness.run_skill_load_session`, then asserts every skill in
    ``skills_expected`` loaded before the first edit (a one-element tuple for a
    single-domain row, the full matching set for the multi-domain case). Because
    the live SDK dispatch is nondeterministic, it runs up to ``attempts`` times
    (pass@k) and returns the first passing report, or the last failing report if
    none pass.

    Defaults to ``CLAUDE_MODEL`` or ``sonnet``. Gated on ``RUN_LIVE_HARNESS=1``;
    raises if the gate is closed so a stray CI import fails loudly instead of
    calling a model. Deferred import of the SDK runner keeps it off the CI path.
    """

    if not _gate_is_open():
        raise RuntimeError(
            "RUN_LIVE_HARNESS is not set to 1 — the per-domain skill-load canary "
            "is manual-only and must never run in default CI."
        )

    # Deferred: importing the runner pulls claude_agent_sdk on the live path only.
    from sdk_load_harness import run_skill_load_session

    resolved_model = model or os.environ.get("CLAUDE_MODEL", "sonnet")

    last_report = DomainLoadReport()
    for _ in range(max(1, attempts)):
        evidence = run_skill_load_session(
            domain_dispatch_prompt(trigger_wording),
            cwd=cwd,
            model=resolved_model,
        )
        report = DomainLoadReport()
        evaluate_multi_domain_load(report, skills_expected, evidence)
        if report.ok:
            return report
        last_report = report
    return last_report


def _seed_workspace(workspace: Path) -> None:
    """Copy the domain fixture tree into ``workspace`` and write the CLI wrapper."""

    import shutil

    shutil.copytree(FIXTURE_ROOT / "superRA", workspace / "superRA")
    wrapper = workspace / "superRA" / "superra"
    cli = REPO_ROOT / "skills" / "task-tree" / "scripts" / "cli.py"
    wrapper.write_text(
        "#!/usr/bin/env bash\n" f'exec python3 "{cli}" "$@"\n',
        encoding="utf-8",
    )
    wrapper.chmod(0o755)


def _live_cases() -> list[tuple[str, tuple[str, ...], str]]:
    """(label, expected_skills, trigger_wording) for each live shot."""

    cases: list[tuple[str, tuple[str, ...], str]] = [
        (row.skill, (row.skill,), row.trigger_wording) for row in DOMAIN_ROWS
    ]
    cases.append(("multi-domain", MULTI_DOMAIN_SKILLS, MULTI_DOMAIN_WORDING))
    return cases


def _main() -> int:
    if not _gate_is_open():
        print(
            "SKIP  RUN_LIVE_HARNESS is not set to 1 — the per-domain skill-load "
            "canary is opt-in and never runs in CI.\n"
            "      Set RUN_LIVE_HARNESS=1 (with claude-agent-sdk installed via "
            "uv run --with) to run it."
        )
        return 0

    import tempfile

    failures: list[str] = []
    for label, expected, wording in _live_cases():
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "ws"
            workspace.mkdir()
            _seed_workspace(workspace)
            report = run_claude_domain_canary(expected, wording, cwd=workspace)
        for obs in report.observations:
            print(f"OK ({label}): {obs}")
        if not report.ok:
            for msg in report.missing:
                print(f"FAIL ({label}): {msg}")
            failures.extend(report.missing)

    if failures:
        print(
            "\nA reliable-dispatch failure here is a real LC003/LC011–LC014 "
            "loading-contract finding to escalate, not a test to relax."
        )
        return 1
    print(
        f"\nOK: all {len(DOMAIN_ROWS)} domains loaded their manifest skill and the "
        "multi-domain case loaded every matching skill."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
