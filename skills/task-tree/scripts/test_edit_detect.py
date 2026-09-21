"""Tool-agnostic edit detection: the PostToolUse hook sees an edit made through
Bash exactly as it sees one made through Edit.

Each case changes a file on disk, then sends the hook a `Bash` payload whose
command says nothing about the file — the shape of a Python-heredoc edit.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

import _edit_detect  # noqa: E402

HEREDOC = "python3 - <<'PY'\nimport pathlib\nPY"


def _task(path: Path, title: str, status: str, body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'---\ntitle: "{title}"\nstatus: {status}\ndepends_on: []\n---\n\n'
        f"## Objective\n\nDo {title}.\n{body}",
        encoding="utf-8",
    )


def _hook(project: Path, payload: dict, env: dict | None = None):
    payload = {"session_id": "s1", "cwd": str(project), **payload}
    run_env = {**os.environ, **(env or {})}
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "task_hook.py")],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=project,
        env=run_env,
    )


def _bash(project: Path, command: str = HEREDOC, **extra) -> str:
    """Run the hook on a Bash payload; return its feedback text ('' when silent)."""
    result = _hook(project, {"tool_name": "Bash", "tool_input": {"command": command}, **extra})
    assert result.returncode == 0
    assert result.stderr == ""
    if not result.stdout.strip():
        return ""
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]


STEPS = """
## Reproduction

```yaml
steps:
  - name: build-panel
    cmd: echo build
    deps:
      - Code/build.jl
    outs:
      - out/panel.csv
  - name: fit-model
    cmd: echo fit
    deps:
      - out/panel.csv
    outs:
      - out/fit.csv
```
"""


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "superRA"
    _task(root / "task.md", "Root", "in-progress")
    _task(root / "01-first" / "task.md", "First", "in-progress")
    _task(root / "02-second" / "task.md", "Second", "approved")
    return tmp_path


@pytest.fixture
def repro_project(project):
    _task(project / "superRA" / "03-pipeline" / "task.md", "Pipeline", "in-progress", STEPS)
    (project / "Code").mkdir()
    (project / "Code" / "build.jl").write_text("# build\n", encoding="utf-8")
    (project / "out").mkdir()
    (project / "out" / "panel.csv").write_text("a\n1\n", encoding="utf-8")
    return project


def _rewrite(path: Path, old: str, new: str) -> None:
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


class TestBashMadeEdits:
    def test_task_md_edit_reconciles_and_propagates(self, project):
        assert _bash(project) == ""  # seeds
        _rewrite(project / "superRA" / "01-first" / "task.md", "in-progress", "approved")
        context = _bash(project)
        assert "Markdown edited" in context
        root_text = (project / "superRA" / "task.md").read_text(encoding="utf-8")
        assert "status: approved" in root_text  # both children approved: rolled up

    def test_approved_with_blocking_notes_is_advisory(self, project):
        assert _bash(project) == ""
        task_md = project / "superRA" / "02-second" / "task.md"
        task_md.write_text(
            task_md.read_text(encoding="utf-8")
            + "\n## Review Notes\n\n1. `[BLOCKING]` Wrong join.\n",
            encoding="utf-8",
        )
        context = _bash(project)
        assert "[BLOCKING]" in context
        assert "02-second" in context

    def test_task_root_markdown_draws_integrity_feedback(self, project):
        assert _bash(project) == ""
        notes = project / "superRA" / "01-first" / "notes.md"
        notes.write_text("Text directly above\n$$\nx = 1\n$$\n", encoding="utf-8")
        context = _bash(project)
        assert "Markdown render-integrity issue" in context
        assert "notes.md" in context

    def test_unchanged_content_is_silent(self, project):
        assert _bash(project) == ""
        task_md = project / "superRA" / "01-first" / "task.md"
        task_md.write_text(task_md.read_text(encoding="utf-8"), encoding="utf-8")
        os.utime(task_md, ns=(1, 1))
        assert _bash(project) == ""

    def test_first_event_seeds_and_still_handles_the_tool_path(self, project):
        task_md = project / "superRA" / "01-first" / "task.md"
        _rewrite(task_md, "in-progress", "approved")
        result = _hook(project, {"tool_name": "Edit", "tool_input": {"file_path": str(task_md)}})
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        assert "Markdown edited" in context
        assert "status: approved" in (project / "superRA" / "task.md").read_text(encoding="utf-8")
        assert _bash(project) == ""  # the Edit refreshed the baseline

    def test_edit_in_another_worktree_is_found_through_the_command(self, project, tmp_path_factory):
        elsewhere = tmp_path_factory.mktemp("session-cwd")
        command = f"cd {project} && {HEREDOC}"
        assert _bash(elsewhere, command) == ""
        _rewrite(project / "superRA" / "01-first" / "task.md", "in-progress", "approved")
        assert "Markdown edited" in _bash(elsewhere, command)


class TestReproductionReminder:
    def test_registered_script_reminds_once_per_session(self, repro_project):
        assert _bash(repro_project) == ""
        script = repro_project / "Code" / "build.jl"
        script.write_text("# build v2\n", encoding="utf-8")
        context = _bash(repro_project)
        assert "Code/build.jl changed" in context
        assert "build-panel" in context
        script.write_text("# build v3\n", encoding="utf-8")
        assert _bash(repro_project) == ""

    def test_rewritten_out_read_by_another_step_is_silent(self, repro_project):
        assert _bash(repro_project) == ""
        (repro_project / "out" / "panel.csv").write_text("a\n2\n", encoding="utf-8")
        assert _bash(repro_project) == ""
        # ...also when the tool names the out itself.
        result = _hook(
            repro_project,
            {"tool_name": "Write", "tool_input": {"file_path": str(repro_project / "out" / "panel.csv")}},
        )
        assert result.stdout.strip() == ""

    def test_unregistered_companion_script_reminds(self, repro_project):
        assert _bash(repro_project) == ""
        script = repro_project / "superRA" / "03-pipeline" / "attachments" / "explore.py"
        script.parent.mkdir()
        script.write_text("print(1)\n", encoding="utf-8")
        context = _bash(repro_project)
        assert "superRA/03-pipeline/attachments/explore.py changed" in context
        assert "owning step(s): none" in context

    def test_tree_without_reproduction_config_keeps_markdown_behaviors(self, project):
        assert _bash(project) == ""
        script = project / "superRA" / "01-first" / "attachments" / "explore.py"
        script.parent.mkdir()
        script.write_text("print(1)\n", encoding="utf-8")
        assert _bash(project) == ""
        _rewrite(project / "superRA" / "01-first" / "task.md", "Do First", "Do it")
        assert "Markdown edited" in _bash(project)

    def test_newly_registered_dep_is_seeded_not_reported(self, repro_project):
        assert _bash(repro_project) == ""
        (repro_project / "Code" / "extra.jl").write_text("# extra\n", encoding="utf-8")
        _rewrite(
            repro_project / "superRA" / "03-pipeline" / "task.md",
            "      - Code/build.jl\n",
            "      - Code/build.jl\n      - Code/extra.jl\n",
        )
        assert "extra.jl changed" not in _bash(repro_project)
        (repro_project / "Code" / "extra.jl").write_text("# extra v2\n", encoding="utf-8")
        assert "Code/extra.jl changed" in _bash(repro_project)

    def test_many_changes_collapse_to_one_line(self, repro_project):
        assert _bash(repro_project) == ""
        attachments = repro_project / "superRA" / "03-pipeline" / "attachments"
        attachments.mkdir()
        for i in range(8):
            (attachments / f"s{i}.py").write_text("x = 1\n", encoding="utf-8")
        context = _bash(repro_project)
        assert "8 tracked files changed" in context
        assert "s0.py" not in context


class TestCodexPayloads:
    ENV = {"SUPERRA_TASK_HOOK_EMPTY_JSON": "1"}

    def test_silent_bash_emits_empty_json(self, project):
        result = _hook(project, {"tool_name": "Bash", "tool_input": {"command": "ls"}}, env=self.ENV)
        assert json.loads(result.stdout) == {}

    def test_bash_made_edit_reaches_feedback(self, project):
        _hook(project, {"tool_name": "Bash", "tool_input": {"command": "ls"}}, env=self.ENV)
        _rewrite(project / "superRA" / "01-first" / "task.md", "in-progress", "approved")
        result = _hook(project, {"tool_name": "Bash", "tool_input": {"command": HEREDOC}}, env=self.ENV)
        output = json.loads(result.stdout)["hookSpecificOutput"]
        assert output["hookEventName"] == "PostToolUse"
        assert "Markdown edited" in output["additionalContext"]

    def test_apply_patch_path_and_detected_path_are_one_edit(self, project):
        _hook(project, {"tool_name": "Bash", "tool_input": {"command": "ls"}}, env=self.ENV)
        _rewrite(project / "superRA" / "01-first" / "task.md", "in-progress", "approved")
        patch = (
            "*** Begin Patch\n*** Update File: superRA/01-first/task.md\n"
            "@@\n-status: in-progress\n+status: approved\n*** End Patch"
        )
        result = _hook(project, {"tool_name": "apply_patch", "tool_input": {"command": patch}})
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        assert context.count("Markdown edited") == 1


class TestBaseline:
    def test_state_is_self_ignored_and_outside_the_task_root(self, project):
        _bash(project)
        state = project / _edit_detect.STATE_DIRNAME
        assert (state / ".gitignore").read_text(encoding="utf-8") == "*\n"
        assert list((state / _edit_detect.BASELINE_SUBDIR).glob("*.json"))
        assert not (project / "superRA" / _edit_detect.STATE_DIRNAME).exists()

    def test_concurrent_invocations_leave_a_readable_baseline(self, project):
        _bash(project)
        task_md = project / "superRA" / "01-first" / "task.md"

        def edit_and_run(i: int) -> int:
            task_md.write_text(task_md.read_text(encoding="utf-8") + f"\nline {i}\n", encoding="utf-8")
            return _hook(project, {"tool_name": "Bash", "tool_input": {"command": HEREDOC}}).returncode

        with ThreadPoolExecutor(max_workers=6) as pool:
            assert set(pool.map(edit_and_run, range(12))) == {0}

        baseline_dir = project / _edit_detect.STATE_DIRNAME / _edit_detect.BASELINE_SUBDIR
        (state_file,) = baseline_dir.glob("*.json")
        loaded = json.loads(state_file.read_text(encoding="utf-8"))
        assert str(task_md.resolve()) in loaded["files"]
        assert not list(baseline_dir.glob("*.tmp"))

    def test_corrupt_baseline_reseeds_silently(self, project):
        _bash(project)
        (state_file,) = (project / _edit_detect.STATE_DIRNAME / _edit_detect.BASELINE_SUBDIR).glob("*.json")
        state_file.write_text("{not json", encoding="utf-8")
        _rewrite(project / "superRA" / "01-first" / "task.md", "in-progress", "approved")
        assert _bash(project) == ""
        assert json.loads(state_file.read_text(encoding="utf-8"))["version"] == _edit_detect.BASELINE_VERSION

    def test_oversized_directory_is_not_watched(self, project, monkeypatch):
        monkeypatch.setattr(_edit_detect, "MAX_TREE_FILES", 2)
        assert _edit_detect.detect(project / "superRA", "s", lambda: []) == []
        assert not (project / _edit_detect.STATE_DIRNAME).exists()

    def test_plan_root_lookup_stops_at_a_repository_top(self, tmp_path):
        (tmp_path / "superRA").mkdir()
        repo = tmp_path / "repo"
        (repo / ".git").mkdir(parents=True)
        (repo / "src").mkdir()
        assert _edit_detect.plan_roots(repo / "src", [], "") == []
