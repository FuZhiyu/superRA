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
    # The harness sets CLAUDE_PROJECT_DIR per session; a case that cares supplies
    # its own, and no ambient value from the session running the suite leaks in.
    run_env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    run_env.update(env or {})
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "task_hook.py")],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=project,
        env=run_env,
    )


def _bash(project: Path, command: str = HEREDOC, env: dict | None = None, **extra) -> str:
    """Run the hook on a Bash payload; return its feedback text ('' when silent)."""
    result = _hook(
        project, {"tool_name": "Bash", "tool_input": {"command": command}, **extra}, env
    )
    assert result.returncode == 0
    assert result.stderr == ""
    if not result.stdout.strip():
        return ""
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]


def _seed_event(project: Path) -> None:
    result = _hook(project, {"hook_event_name": "UserPromptSubmit", "prompt": "go"})
    assert result.returncode == 0 and result.stdout.strip() == ""


def _pre_bash(project: Path, command: str = HEREDOC, env: dict | None = None) -> None:
    result = _hook(
        project,
        {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}},
        env,
    )
    assert result.returncode == 0 and result.stdout.strip() == "" and result.stderr == ""


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


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )


def _checkout(path: Path) -> Path:
    """A disposable git checkout carrying a committed three-task tree."""
    path.mkdir(parents=True)
    _git(path, "init", "-q")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test")
    _task(path / "superRA" / "task.md", "Root", "in-progress")
    _task(path / "superRA" / "01-first" / "task.md", "First", "in-progress")
    _task(path / "superRA" / "02-second" / "task.md", "Second", "approved")
    _git(path, "add", "-A")
    _git(path, "commit", "-qm", "init")
    return path


def _dirty(checkout: Path) -> set[str]:
    porcelain = _git(checkout, "status", "--porcelain").stdout
    return {line[3:] for line in porcelain.splitlines() if line}


class TestBashMadeEdits:
    def test_task_md_edit_reconciles_and_propagates(self, project):
        assert _bash(project) == ""  # seeds
        _rewrite(project / "superRA" / "01-first" / "task.md", "in-progress", "approved")
        context = _bash(project)
        assert "Markdown edited" in context
        root_text = (project / "superRA" / "task.md").read_text(encoding="utf-8")
        assert "status: approved" in root_text  # both children approved: rolled up

    def test_unchanged_content_is_silent(self, project):
        assert _bash(project) == ""
        task_md = project / "superRA" / "01-first" / "task.md"
        task_md.write_text(task_md.read_text(encoding="utf-8"), encoding="utf-8")
        os.utime(task_md, ns=(1, 1))
        assert _bash(project) == ""

    def test_first_edit_in_a_sibling_worktree_is_found_through_the_command(self, tmp_path):
        """A worktree created mid-session has no baseline: the PreToolUse seed
        takes one before the command runs, so its first edit is seen."""
        session = _checkout(tmp_path / "session")
        _seed_event(session)
        sibling = tmp_path / "sibling"
        _git(session, "worktree", "add", "-q", "-b", "sibling", str(sibling))
        command = f"cd {sibling} && {HEREDOC}"
        _pre_bash(session, command)
        _rewrite(sibling / "superRA" / "01-first" / "task.md", "in-progress", "approved")
        assert "Markdown edited" in _bash(session, command)
        assert "status: approved" in (sibling / "superRA" / "task.md").read_text(encoding="utf-8")

    def test_payload_cwd_in_a_sibling_worktree_names_its_tree(self, tmp_path):
        session = _checkout(tmp_path / "session")
        sibling = tmp_path / "sibling"
        _git(session, "worktree", "add", "-q", "-b", "sibling", str(sibling))
        env = {"CLAUDE_PROJECT_DIR": str(session)}
        _pre_bash(sibling, HEREDOC, env=env)
        _rewrite(sibling / "superRA" / "01-first" / "task.md", "in-progress", "approved")
        assert "Markdown edited" in _bash(sibling, HEREDOC, env=env)
        assert "status: approved" in (sibling / "superRA" / "task.md").read_text(encoding="utf-8")

    def test_pre_tool_seed_keeps_an_existing_baseline(self, project):
        assert _bash(project) == ""
        _rewrite(project / "superRA" / "01-first" / "task.md", "in-progress", "approved")
        _pre_bash(project)
        assert "Markdown edited" in _bash(project)

    def test_a_foreign_checkout_is_left_alone(self, tmp_path):
        """Naming a path in another repository's checkout must not rewrite its
        task files: the hook writes nowhere `guard-foreign-checkout` would prompt."""
        session = _checkout(tmp_path / "session")
        foreign = _checkout(tmp_path / "foreign")
        command = f"ls {foreign}/superRA"
        assert _bash(session, command) == ""
        _rewrite(foreign / "superRA" / "01-first" / "task.md", "in-progress", "approved")
        _rewrite(session / "superRA" / "01-first" / "task.md", "in-progress", "approved")

        assert "Markdown edited" in _bash(session, command)  # the session's own tree still reconciles
        assert _dirty(foreign) == {"superRA/01-first/task.md"}
        assert "status: in-progress" in (foreign / "superRA" / "task.md").read_text(encoding="utf-8")
        assert not (foreign / _edit_detect.STATE_DIRNAME).exists()

    def test_a_payload_cwd_inside_the_foreign_checkout_does_not_unlock_it(self, tmp_path):
        """A session that `cd`s into another checkout keeps the anchor it started
        with: `CLAUDE_PROJECT_DIR` outranks the payload cwd, as in the gate."""
        session = _checkout(tmp_path / "session")
        foreign = _checkout(tmp_path / "foreign")
        env = {"CLAUDE_PROJECT_DIR": str(session)}
        assert _bash(foreign, "ls", env=env) == ""
        _rewrite(foreign / "superRA" / "01-first" / "task.md", "in-progress", "approved")

        assert _bash(foreign, "ls", env=env) == ""
        assert _dirty(foreign) == {"superRA/01-first/task.md"}
        assert "status: in-progress" in (foreign / "superRA" / "task.md").read_text(encoding="utf-8")
        assert not (foreign / _edit_detect.STATE_DIRNAME).exists()


class TestUnfinishedMerge:
    def test_conflicted_merge_validates_without_rewriting_parents(self, tmp_path):
        session = _checkout(tmp_path / "session")
        first = session / "superRA" / "01-first" / "task.md"
        second = session / "superRA" / "02-second" / "task.md"
        _git(session, "checkout", "-q", "-b", "other")
        _rewrite(first, "in-progress", "approved")
        _rewrite(second, "Do Second.", "Do Second, theirs.")
        _git(session, "commit", "-qam", "other")
        _git(session, "checkout", "-q", "-")
        _rewrite(second, "Do Second.", "Do Second, ours.")
        _git(session, "commit", "-qam", "ours")
        assert _bash(session) == ""  # seeds
        merge = subprocess.run(["git", "merge", "other"], cwd=session, capture_output=True, text=True)
        assert merge.returncode != 0 and (session / ".git" / "MERGE_HEAD").exists()

        context = _bash(session, "git merge other")
        assert "validated only" in context
        assert "status: in-progress" in (session / "superRA" / "task.md").read_text(encoding="utf-8")

    def test_conflict_markers_alone_freeze_writes(self, project):
        assert _bash(project) == ""
        first = project / "superRA" / "01-first" / "task.md"
        _rewrite(first, "in-progress", "approved")
        first.write_text(
            first.read_text(encoding="utf-8") + "\n<<<<<<< Updated upstream\na\n=======\nb\n>>>>>>> Stashed changes\n",
            encoding="utf-8",
        )
        assert "validated only" in _bash(project)
        assert "status: in-progress" in (project / "superRA" / "task.md").read_text(encoding="utf-8")


class TestBoundedFeedback:
    def test_many_integrity_issues_collapse_to_a_count(self, project):
        from _task_validate import OUTPUT_CAP
        assert _bash(project) == ""
        for i in range(30):
            _task(project / "superRA" / "01-first" / f"{i:02d}-child" / "task.md", f"Child {i}",
                  "in-progress", "\n$$\na\n$$\n$$\nb\n$$\n")
        context = _bash(project)
        assert context.count("render-integrity issue in") == OUTPUT_CAP
        assert f"{60 - OUTPUT_CAP} more render-integrity issue(s)" in context
        assert "check_markdown.py" in context

    def test_errors_are_listed_before_warnings_are_capped(self, project):
        from _task_validate import OUTPUT_CAP
        notes = "\n## Revision Notes\n\nleftover\n"
        for i in range(OUTPUT_CAP + 2):
            _task(project / "superRA" / f"{i + 10:02d}-done" / "task.md", f"Done {i}", "approved", notes)
        _task(project / "superRA" / "99-broken" / "task.md", "Broken", "in-progress",
              "\n## Reproduction\n\n```yaml\nsteps:\n  - cmd: echo\n```\n")
        context = _bash(project, "mkdir -p superRA/99-broken/attachments")
        assert "[ERROR]" in context
        assert "more validation warning(s)" in context
        assert "`superra task check --all`" in context


class TestReproductionReminder:
    def test_registered_script_reminds_once_per_session(self, repro_project):
        assert _bash(repro_project) == ""
        script = repro_project / "Code" / "build.jl"
        script.write_text("# build v2\n", encoding="utf-8")
        context = _bash(repro_project)
        assert "Code/build.jl changed" in context
        assert "build-panel" in context
        # the command the reminder prints needs a target, and names the owning step
        assert "`superra repro status 03-pipeline#build-panel`" in context
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
        assert "`superra repro status .`" in context  # no owner: the whole tree

    def test_tree_without_reproduction_config_keeps_markdown_behaviors(self, project):
        assert _bash(project) == ""
        script = project / "superRA" / "01-first" / "attachments" / "explore.py"
        script.parent.mkdir()
        script.write_text("print(1)\n", encoding="utf-8")
        assert _bash(project) == ""
        _rewrite(project / "superRA" / "01-first" / "task.md", "Do First", "Do it")
        assert "Markdown edited" in _bash(project)


VAR_STEPS = """
## Reproduction

```yaml
steps:
  - name: est
    runner: julia
    script: ${CODE}/est.jl
    deps:
      - ${CODE}/lib
    outs:
      - out/est.csv
```
"""

CONFIG = """reproduction:
  vars:
    CODE: Code
    SECRET:
      shell: "echo never-run"
  runners:
    julia: "julia --project=. {script}"
"""


@pytest.fixture
def var_project(project):
    (project / "superRA" / "config.yaml").write_text(CONFIG, encoding="utf-8")
    _task(project / "superRA" / "03-pipeline" / "task.md", "Pipeline", "in-progress", VAR_STEPS)
    (project / "Code" / "lib").mkdir(parents=True)
    (project / "Code" / "est.jl").write_text("# est\n", encoding="utf-8")
    (project / "Code" / "lib" / "helper.jl").write_text("# helper\n", encoding="utf-8")
    return project


class TestEveryProducerEdit:
    def test_shell_variable_is_never_run(self, var_project):
        marker = var_project / "ran"
        (var_project / "superRA" / "config.yaml").write_text(
            CONFIG.replace("echo never-run", f"touch {marker}"), encoding="utf-8"
        )
        _bash(var_project)
        (var_project / "Code" / "est.jl").write_text("# est v2\n", encoding="utf-8")
        _bash(var_project)
        assert not marker.exists()

    def test_new_file_in_a_declared_directory_reminds(self, var_project):
        assert _bash(var_project) == ""
        (var_project / "Code" / "lib" / "more.jl").write_text("# new\n", encoding="utf-8")
        assert "Code/lib/more.jl changed" in _bash(var_project)

    def test_edit_in_the_first_tool_call_is_seen_after_a_prompt_seed(self, var_project):
        _seed_event(var_project)
        (var_project / "Code" / "est.jl").write_text("# est v2\n", encoding="utf-8")
        assert _bash(var_project).count("Code/est.jl changed") == 1

    def test_new_runner_script_draws_the_soft_reminder(self, var_project):
        assert _bash(var_project) == ""
        (var_project / "Code" / "new_producer.jl").write_text("# new\n", encoding="utf-8")
        context = _bash(var_project)
        assert context.count("new script Code/new_producer.jl") == 1
        assert "register" not in context


class TestCodexPayloads:
    ENV = {"SUPERRA_TASK_HOOK_EMPTY_JSON": "1"}

    def test_silent_bash_emits_empty_json(self, project):
        result = _hook(project, {"tool_name": "Bash", "tool_input": {"command": "ls"}}, env=self.ENV)
        assert json.loads(result.stdout) == {}


class TestBaseline:
    def test_state_is_self_ignored_and_outside_the_task_root(self, project):
        _bash(project)
        state = project / _edit_detect.STATE_DIRNAME
        assert (state / ".gitignore").read_text(encoding="utf-8") == "*\n"
        assert list((state / _edit_detect.BASELINE_SUBDIR).glob("*.json"))
        assert not (project / "superRA" / _edit_detect.STATE_DIRNAME).exists()
        from test_repro_acceptance import _dropbox_ignored
        assert _dropbox_ignored(state)

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
