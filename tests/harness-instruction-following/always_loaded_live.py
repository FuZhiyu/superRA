#!/usr/bin/env python3
"""Always-loaded skill coverage with structural and observable evidence.

Claude preloads ``superRA:using-superra`` and
``superRA:report-in-markdown`` from role frontmatter, so their loads do not emit
``Skill`` events. The deterministic contract parses that frontmatter. The live
run dispatches the real role, requires a file mutation with a fixed schema, and
checks that neither always-loaded skill was loaded on demand.

Codex does not preload skills. Its live smoke checks two actual
``command_execution`` events: the task-tree wrapper read and the markdown
self-diagnose script. The output artifact carries only schema, task, and path
identities; it does not repeat authored skill instructions.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from codex_load_evidence import CommandSpec
from sdk_load_evidence import (
    ALWAYS_LOADED_SKILLS,
    SkillLoadEvidence,
    SkillLoadReport,
    check_always_loaded_frontmatter,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "task-trees" / "always-loaded-canary"

ALWAYS_LOADED_ARTIFACT_SCHEMA = "superra.always-loaded-evidence/v1"
ALWAYS_LOADED_TASK_PATH = "always-loaded-task"
ALWAYS_LOADED_OUTPUT_PATH = "always-loaded-evidence.json"


def expected_always_loaded_artifact() -> dict[str, str]:
    """Return the exact schema/identity artifact for the live task."""

    return {
        "schema": ALWAYS_LOADED_ARTIFACT_SCHEMA,
        "task_path": ALWAYS_LOADED_TASK_PATH,
        "output_path": ALWAYS_LOADED_OUTPUT_PATH,
    }


def always_loaded_artifact_matches(artifact: dict | None) -> bool:
    """Return whether ``artifact`` exactly matches the structural contract."""

    return artifact == expected_always_loaded_artifact()


@dataclass
class AlwaysLoadedBehaviorReport:
    """Collect failed always-loaded behavioral expectations."""

    missing: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing

    def assert_ok(self) -> None:
        if self.missing:
            joined = "\n".join(f"- {msg}" for msg in self.missing)
            raise AssertionError(f"Always-loaded behavior failures:\n{joined}")


def _skill_load_count(evidence: SkillLoadEvidence, skill: str) -> int:
    return sum(1 for record in evidence.skill_loads if record.name == skill)


def evaluate_always_loaded_behavior(
    report: AlwaysLoadedBehaviorReport,
    evidence: SkillLoadEvidence,
    artifact: dict | None,
) -> None:
    """Check dispatch mutation, artifact schema, and autoload event shape."""

    for skill in ALWAYS_LOADED_SKILLS:
        count = _skill_load_count(evidence, skill)
        if count:
            report.missing.append(
                f"always-loaded skill {skill!r} emitted {count} on-demand load(s)"
            )

    if evidence.first_edit_index is None:
        report.missing.append("dispatched role produced no Edit/Write event")
    if not always_loaded_artifact_matches(artifact):
        report.missing.append(
            "output artifact did not match the always-loaded schema and path identities"
        )

    if not report.missing:
        report.observations.append(
            "role dispatch wrote the structured artifact with zero on-demand "
            "loads for both frontmatter skills"
        )


def check_claude_always_loaded_static(
    report: SkillLoadReport,
    repo_root: Path | str = REPO_ROOT,
) -> None:
    """Check both role specs' always-loaded frontmatter declarations."""

    check_always_loaded_frontmatter(report, repo_root)


# These are command identities, not authored instruction text. The Codex live
# evaluator accepts only command_execution evidence; the artifact is validated
# separately against ``expected_always_loaded_artifact``.
CODEX_REPORT_IN_MARKDOWN_COMMAND = CommandSpec(
    subject="superRA:report-in-markdown markdown check",
    executable="python3",
    args=(
        "check_markdown.py",
        "superRA/always-loaded-task/task.md",
    ),
)
CODEX_USING_SUPERRA_COMMAND = CommandSpec(
    subject="superRA:using-superra task read",
    executable="./superRA/superra",
    args=("task", "read", "always-loaded-task"),
)
CODEX_ALWAYS_LOADED_COMMANDS = (
    CODEX_REPORT_IN_MARKDOWN_COMMAND,
    CODEX_USING_SUPERRA_COMMAND,
)


def _gate_is_open() -> bool:
    return os.environ.get("RUN_LIVE_HARNESS") == "1"


def _load_artifact(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def run_claude_always_loaded_behavior(
    *,
    cwd: Path | str,
    model: str | None = None,
    attempts: int = 3,
) -> AlwaysLoadedBehaviorReport:
    """Run the live role dispatch and evaluate its observable output."""

    if not _gate_is_open():
        raise RuntimeError(
            "RUN_LIVE_HARNESS is not set to 1 — the always-loaded live run "
            "is manual-only and must never run in default CI."
        )

    from sdk_load_harness import run_skill_load_session

    workspace = Path(cwd)
    resolved_model = model or os.environ.get("CLAUDE_MODEL", "sonnet")
    prompt = (
        "You are an implementer assigned the superRA task always-loaded-task. "
        "Run `./superRA/superra task read always-loaded-task`, load the skills "
        "your role requires, and complete only that task's objective."
    )

    last_report = AlwaysLoadedBehaviorReport()
    for _ in range(max(1, attempts)):
        evidence = run_skill_load_session(
            prompt,
            cwd=workspace,
            model=resolved_model,
        )
        artifact = _load_artifact(workspace / ALWAYS_LOADED_OUTPUT_PATH)
        report = AlwaysLoadedBehaviorReport()
        evaluate_always_loaded_behavior(report, evidence, artifact)
        if report.ok:
            return report
        last_report = report
    return last_report


def _seed_workspace(workspace: Path) -> None:
    """Copy the fixture tree and install the source-resolving task wrapper."""

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
            "SKIP  RUN_LIVE_HARNESS is not set to 1 — the always-loaded live "
            "run is opt-in and never runs in CI."
        )
        return 0

    import tempfile

    static_report = SkillLoadReport()
    check_claude_always_loaded_static(static_report)
    if not static_report.ok:
        static_report.assert_ok()

    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp) / "ws"
        workspace.mkdir()
        _seed_workspace(workspace)
        report = run_claude_always_loaded_behavior(cwd=workspace)

    for obs in report.observations:
        print(f"OK: {obs}")
    if not report.ok:
        print("FAIL: always-loaded behavior did not pass:")
        for msg in report.missing:
            print(f"  - {msg}")
        return 1
    print("OK: frontmatter contract and structured role mutation verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
