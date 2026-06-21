#!/usr/bin/env python3
"""Per-stage skill-load live coverage (task 11), CI-safe core + manual live entry.

Verifies that each non-empty workflow stage loads the skill(s)/reference the
Skill-Load Manifest assigns it before stage action (load-contracts LC002,
LC007–LC010), in both harnesses, and that the sole negative stage
(``implementation``) carries no extra stage-skill expectation:

- ``planning-review`` → ``skills/superplan/references/planning-review.md``
- ``protection``      → ``result-protection``
- ``sync``            → ``semantic-merge``
- ``integration``     → ``refactor-and-integrate``
- ``maturation``      → ``task-tree`` + ``superplan`` (always); ``writing``
  conditional ("prose-heavy maturation"), so it is not a guaranteed load

``maturation`` is the one positive stage whose manifest row loads **multiple**
skills, so its row carries a tuple of expected skill names; the single-skill
positive rows and the read-channel row are unchanged.

One parametrized table (:data:`STAGE_ROWS`) is the single source of truth, so
adding a future stage is a one-row change. Each row names the expected evidence
and which of the two channels carries it — load-bearing for the harness design:

- **Stage skills** (``result-protection``, ``semantic-merge``,
  ``refactor-and-integrate``) load through the ``Skill`` tool, so 08's
  ``PreToolUse(matcher="Skill")`` hook records them by name — same channel as the
  ordering smoke. The evaluator reuses 08's evidence model; it does not
  re-implement capture.
- **The ``planning-review`` reference** is a file loaded via ``Read``, not the
  ``Skill`` tool, so the ``Skill`` hook cannot see it. 11 extends 08's harness
  with an opt-in ``PreToolUse(matcher="Read")`` hook (``capture_reads=True``)
  that records read paths; the evaluator matches the manifest reference path
  against the captured reads.

The evaluator takes already-captured inputs (the dispatched agent's skill-load +
read evidence for Claude; command strings + the output artifact for Codex), so
the default ``pytest`` path drives it on synthetic inputs with no model call and
no ``claude_agent_sdk`` / codex-cli import. The live Claude entry
:func:`run_claude_stage_canary` consumes 08's
:func:`sdk_load_harness.run_skill_load_session` and is gated behind
``RUN_LIVE_HARNESS=1``.

The live SDK dispatch is mildly nondeterministic (it leans on the top-level model
to issue the Task dispatch). The live entry defaults to ``sonnet`` (haiku was
flaky at dispatching) and runs a small pass@k window so a single flaky dispatch
does not red a stage. A stage that reliably does **not** load its manifest
skill/reference is a real LC002/LC007–LC010 finding to record and escalate, not
an assertion to relax — this is the heart of what task 11 verifies.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from codex_load_evidence import CanarySpec
from sdk_load_evidence import SkillLoadEvidence

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "task-trees" / "stage-loads"

# Evidence channels a stage's manifest entry loads through.
CHANNEL_SKILL = "skill"  # loaded via the Skill tool -> 08's Skill hook records it
CHANNEL_READ = "read"  # a reference file loaded via Read -> 08's opt-in Read hook
CHANNEL_NONE = "none"  # negative stage: no extra stage-skill expectation


@dataclass(frozen=True)
class StageRow:
    """One ``{stage, expected_skill(s)_or_refpath}`` parametrization row.

    - ``stage`` is the ``Stage:`` value the dispatch carries.
    - For a ``CHANNEL_SKILL`` row, ``expected_skills`` holds the manifest skill
      *name(s)* the stage **always** loads (e.g. ``("result-protection",)`` for a
      single-skill stage, ``("task-tree", "superplan")`` for the multi-skill
      ``maturation`` stage). A skill the manifest marks conditional (``writing``
      on ``maturation``) is **not** listed — it must not be a guaranteed-load
      assertion. ``expected`` is ``None`` for skill-channel rows.
    - For a ``CHANNEL_READ`` row, ``expected`` is the reference *path* (e.g.
      ``"skills/superplan/references/planning-review.md"``) and ``expected_skills``
      is empty.
    - For a negative stage, both ``expected`` is ``None`` and ``expected_skills``
      is empty.
    - ``channel`` selects how the evaluator looks for the evidence.
    - ``codex_canary`` is the per-stage Codex :class:`CanarySpec` whose
      skill-unique token is only producible if a stage skill/reference body
      loaded; ``None`` for a negative stage.
    """

    stage: str
    expected: str | None
    channel: str
    codex_canary: CanarySpec | None
    expected_skills: tuple[str, ...] = ()


# --------------------------------------------------------------------------- #
# Codex per-stage canaries (skill-unique tokens, recorded at the artifact field)
# --------------------------------------------------------------------------- #

# Each token is a discriminating concept the stage skill/reference body
# prescribes (named in the fixture task only as "the discriminating concept that
# stage's body prescribes"), so the agent can only write it once that body is in
# context. Recorded at the artifact field `stage_canary` (the same artifact-field
# convention task 10's always-loaded canaries use); a stage skill with no
# bundled script has no command-execution side effect, so the artifact field is
# the channel.
_STAGE_CANARY_FIELD = "stage_canary"

CODEX_PROTECTION_CANARY = CanarySpec(
    skill="result-protection",
    token="drift test",
    in_command=False,
    in_artifact_field=_STAGE_CANARY_FIELD,
)
CODEX_SYNC_CANARY = CanarySpec(
    skill="semantic-merge",
    token="intent conflict",
    in_command=False,
    in_artifact_field=_STAGE_CANARY_FIELD,
)
CODEX_INTEGRATION_CANARY = CanarySpec(
    skill="refactor-and-integrate",
    token="minimum net diff",
    in_command=False,
    in_artifact_field=_STAGE_CANARY_FIELD,
)
CODEX_PLANNING_REVIEW_CANARY = CanarySpec(
    skill="skills/superplan/references/planning-review.md",
    token="handoff-readiness",
    in_command=False,
    in_artifact_field=_STAGE_CANARY_FIELD,
)
# maturation loads task-tree + superplan (always) and writing (conditional). The
# canary anchors on a concept unique to one *always-loaded* maturation skill —
# task-tree's `frontier` view — so the token is producible only if that body
# reached context. We do NOT anchor on writing (conditional) lest a maturation
# run that legitimately skips the prose-heavy load red the canary.
CODEX_MATURATION_CANARY = CanarySpec(
    skill="task-tree",
    token="frontier",
    in_command=False,
    in_artifact_field=_STAGE_CANARY_FIELD,
)


# --------------------------------------------------------------------------- #
# The parametrized stage table (single source of truth)
# --------------------------------------------------------------------------- #

STAGE_ROWS: tuple[StageRow, ...] = (
    StageRow(
        stage="planning-review",
        expected="skills/superplan/references/planning-review.md",
        channel=CHANNEL_READ,
        codex_canary=CODEX_PLANNING_REVIEW_CANARY,
    ),
    StageRow(
        stage="protection",
        expected=None,
        channel=CHANNEL_SKILL,
        codex_canary=CODEX_PROTECTION_CANARY,
        expected_skills=("result-protection",),
    ),
    StageRow(
        stage="sync",
        expected=None,
        channel=CHANNEL_SKILL,
        codex_canary=CODEX_SYNC_CANARY,
        expected_skills=("semantic-merge",),
    ),
    StageRow(
        stage="integration",
        expected=None,
        channel=CHANNEL_SKILL,
        codex_canary=CODEX_INTEGRATION_CANARY,
        expected_skills=("refactor-and-integrate",),
    ),
    # Positive multi-skill stage: maturation always loads task-tree + superplan.
    # writing is conditional ("prose-heavy maturation"), so it is deliberately
    # absent from expected_skills — only the guaranteed loads are asserted.
    StageRow(
        stage="maturation",
        expected=None,
        channel=CHANNEL_SKILL,
        codex_canary=CODEX_MATURATION_CANARY,
        expected_skills=("task-tree", "superplan"),
    ),
    # Negative stage: no extra stage-skill expectation.
    StageRow(stage="implementation", expected=None, channel=CHANNEL_NONE, codex_canary=None),
)

# All stage skill names, for the negative-case "no stage skill loaded" check.
# Flattens every positive skill-channel row's expected_skills, including the
# multi-skill maturation row, so a maturation skill loaded on the negative stage
# is caught as an over-load.
ALL_STAGE_SKILLS: frozenset[str] = frozenset(
    skill
    for row in STAGE_ROWS
    if row.channel == CHANNEL_SKILL
    for skill in row.expected_skills
)


def stage_row(stage: str) -> StageRow:
    """Return the :class:`StageRow` for ``stage`` (raises if unknown)."""

    for row in STAGE_ROWS:
        if row.stage == stage:
            return row
    raise KeyError(f"no stage row for {stage!r}")


# --------------------------------------------------------------------------- #
# Claude evaluator (consumes 08's SkillLoadEvidence)
# --------------------------------------------------------------------------- #


@dataclass
class StageLoadReport:
    """Collect every failed stage-load expectation from one evidence check."""

    missing: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing

    def assert_ok(self) -> None:
        if self.missing:
            joined = "\n".join(f"- {msg}" for msg in self.missing)
            raise AssertionError(f"Stage-load evidence failures:\n{joined}")


def evaluate_stage_load(
    report: StageLoadReport,
    row: StageRow,
    evidence: SkillLoadEvidence,
) -> None:
    """Check one stage's manifest load against captured SDK evidence.

    - ``CHANNEL_SKILL``: every skill in ``expected_skills`` must have loaded via
      the ``Skill`` tool before the first edit (08's ordering check, applied to
      each guaranteed-load stage skill). A multi-skill stage (``maturation``)
      requires all of its guaranteed loads; a conditional skill is not listed, so
      its absence is never a failure here.
    - ``CHANNEL_READ``: the manifest reference path must have been read via the
      ``Read`` tool before the first edit (08's opt-in Read channel). Requires the
      session to have been run with ``capture_reads=True``.
    - ``CHANNEL_NONE``: the negative stage must load **none** of the stage
      skills — a stage-skill load on ``implementation`` is a real over-load
      finding.

    A clear failure names the stage and the missing/late/unexpected evidence.
    A reliable failure is a real LC002/LC007–LC010 finding to escalate, not an
    assertion to relax.
    """

    if row.channel == CHANNEL_SKILL:
        for skill in row.expected_skills:
            if skill not in evidence.loaded_skill_names:
                report.missing.append(
                    f"stage {row.stage!r}: required skill {skill!r} never loaded "
                    f"(observed skill loads: {sorted(evidence.loaded_skill_names)})"
                )
            elif not evidence.loaded_before_first_edit(skill):
                report.missing.append(
                    f"stage {row.stage!r}: skill {skill!r} loaded at event "
                    f"{evidence.first_load_index(skill)} but the first edit/write "
                    f"was at event {evidence.first_edit_index} — must load before "
                    f"the first edit"
                )
            else:
                report.observations.append(
                    f"stage {row.stage!r}: skill {skill!r} loaded before first edit"
                )

    elif row.channel == CHANNEL_READ:
        ref = row.expected
        if evidence.first_read_index(ref) is None:
            report.missing.append(
                f"stage {row.stage!r}: required reference {ref!r} never read "
                f"(observed reads: {sorted(evidence.read_paths)}) — the "
                f"reference loads via the Read tool, so run the session with "
                f"capture_reads=True"
            )
        elif not evidence.read_before_first_edit(ref):
            report.missing.append(
                f"stage {row.stage!r}: reference {ref!r} read at event "
                f"{evidence.first_read_index(ref)} but the first edit/write was "
                f"at event {evidence.first_edit_index} — must read before the "
                f"first edit"
            )
        else:
            report.observations.append(
                f"stage {row.stage!r}: reference {ref!r} read before first edit"
            )

    elif row.channel == CHANNEL_NONE:
        loaded_stage_skills = sorted(
            evidence.loaded_skill_names & ALL_STAGE_SKILLS
        )
        if loaded_stage_skills:
            report.missing.append(
                f"stage {row.stage!r} carries no stage-skill expectation, but the "
                f"dispatch loaded stage skill(s) {loaded_stage_skills} — an "
                f"over-load finding"
            )
        else:
            report.observations.append(
                f"stage {row.stage!r}: no stage skill loaded (negative case holds)"
            )

    else:  # pragma: no cover - guarded by the table
        report.missing.append(f"stage {row.stage!r}: unknown channel {row.channel!r}")


def evaluate_all_stage_loads(
    report: StageLoadReport,
    evidence_by_stage: dict[str, SkillLoadEvidence],
) -> None:
    """Evaluate every stage row against its per-stage captured evidence."""

    for row in STAGE_ROWS:
        if row.stage not in evidence_by_stage:
            report.missing.append(
                f"stage {row.stage!r}: no captured evidence supplied"
            )
            continue
        evaluate_stage_load(report, row, evidence_by_stage[row.stage])


# --------------------------------------------------------------------------- #
# Live Claude entry (manual-only; consumes 08's harness)
# --------------------------------------------------------------------------- #


def _gate_is_open() -> bool:
    return os.environ.get("RUN_LIVE_HARNESS") == "1"


def stage_dispatch_prompt(stage: str) -> str:
    """The per-stage dispatch instruction: carries the ``Stage:`` line.

    The fixture body is shared across stages; only this ``Stage:`` line differs,
    so the dispatched implementer/reviewer loads per the manifest for that stage.
    Kept superficial per the parent objective — read the fixture context and write
    one tiny evidence JSON, no real work.
    """

    return (
        f"Stage: {stage}\n\n"
        "You are an implementer in this superRA workspace. Run "
        "`./superRA/superra task read stage-loads-task`, load the skill or "
        "reference the Skill-Load Manifest maps your Stage: to, then write "
        "stage-loads-evidence.json at the workspace root exactly as the task "
        "objective specifies. Do nothing else."
    )


def run_claude_stage_canary(
    stage: str,
    *,
    cwd: Path | str,
    model: str | None = None,
    attempts: int = 3,
) -> StageLoadReport:
    """Run the live Claude per-stage skill-load canary for one stage (manual-only).

    Dispatches the real ``superRA:implementer`` via 08's
    :func:`sdk_load_harness.run_skill_load_session` with ``capture_reads=True``
    (so the ``planning-review`` reference read is observed), then evaluates the
    stage row. Because the live SDK dispatch is nondeterministic, it runs up to
    ``attempts`` times (pass@k) and returns the first passing report, or the last
    failing report if none pass.

    Defaults to ``CLAUDE_MODEL`` or ``sonnet`` — sonnet dispatched reliably in the
    live confirmation; haiku was flaky. Gated on ``RUN_LIVE_HARNESS=1``; raises if
    the gate is closed so a stray CI import fails loudly instead of calling a
    model. Deferred import of the SDK runner keeps it off the CI path.
    """

    if not _gate_is_open():
        raise RuntimeError(
            "RUN_LIVE_HARNESS is not set to 1 — the per-stage skill-load canary "
            "is manual-only and must never run in default CI."
        )

    # Deferred: importing the runner pulls claude_agent_sdk on the live path only.
    from sdk_load_harness import run_skill_load_session

    row = stage_row(stage)
    resolved_model = model or os.environ.get("CLAUDE_MODEL", "sonnet")

    last_report = StageLoadReport()
    for _ in range(max(1, attempts)):
        evidence = run_skill_load_session(
            stage_dispatch_prompt(stage),
            cwd=cwd,
            model=resolved_model,
            capture_reads=True,
        )
        report = StageLoadReport()
        evaluate_stage_load(report, row, evidence)
        if report.ok:
            return report
        last_report = report
    return last_report


def _seed_workspace(workspace: Path) -> None:
    """Copy the stage fixture tree into ``workspace`` and write the CLI wrapper."""

    import shutil

    shutil.copytree(FIXTURE_ROOT / "superRA", workspace / "superRA")
    wrapper = workspace / "superRA" / "superra"
    cli = REPO_ROOT / "skills" / "task-tree" / "scripts" / "cli.py"
    wrapper.write_text(
        "#!/usr/bin/env bash\n" f'exec python3 "{cli}" "$@"\n',
        encoding="utf-8",
    )
    wrapper.chmod(0o755)


def _main() -> int:
    if not _gate_is_open():
        print(
            "SKIP  RUN_LIVE_HARNESS is not set to 1 — the per-stage skill-load "
            "canary is opt-in and never runs in CI.\n"
            "      Set RUN_LIVE_HARNESS=1 (with claude-agent-sdk installed via "
            "uv run --with) to run it."
        )
        return 0

    import shutil
    import tempfile

    # Only the non-empty stages have a load expectation worth a live shot; the
    # negative stage is covered by the CI-safe unit test (asserting no stage
    # skill loads), so a live run focuses on the positive stages.
    positive = [r.stage for r in STAGE_ROWS if r.channel != CHANNEL_NONE]
    failures: list[str] = []
    for stage in positive:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "ws"
            workspace.mkdir()
            _seed_workspace(workspace)
            report = run_claude_stage_canary(stage, cwd=workspace)
        for obs in report.observations:
            print(f"OK: {obs}")
        if not report.ok:
            for msg in report.missing:
                print(f"FAIL: {msg}")
            failures.extend(report.missing)

    if failures:
        print(
            "\nA reliable-dispatch failure here is a real LC002/LC007–LC010 "
            "loading-contract finding to escalate, not a test to relax."
        )
        return 1
    print(f"\nOK: all {len(positive)} non-empty stages loaded their manifest skill/reference.")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
