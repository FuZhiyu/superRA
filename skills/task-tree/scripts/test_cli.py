#!/usr/bin/env python3
"""Tests for the packaged superra command surface."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent
SKILL_DIR = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import cli


def _write_task_md(
    path: Path,
    title: str,
    status: str = "not-started",
    results: str = "",
    depends_on: list[str] | None = None,
) -> None:
    body = "## Objective\n\nTest objective.\n"
    if results:
        body += f"\n## Results\n\n{results}\n"
    deps = depends_on or []
    deps_yaml = "\n" + "".join(f"  - {dep}\n" for dep in deps) if deps else " []"
    path.write_text(
        "\n".join(
            [
                "---",
                f'title: "{title}"',
                f"status: {status}",
                f"depends_on:{deps_yaml}",
                "tags: []",
                "created: 2026-01-01",
                "---",
                "",
                body,
            ]
        ),
        encoding="utf-8",
    )


@pytest.fixture
def task_root(tmp_path: Path) -> Path:
    root = tmp_path / "superRA"
    root.mkdir()
    _write_task_md(root / "task.md", "Root")

    first = root / "01-first"
    first.mkdir()
    _write_task_md(first / "task.md", "First", "approved", results="- done")

    second = root / "02-second"
    second.mkdir()
    _write_task_md(second / "task.md", "Second")
    return root


def test_task_read_autodetects_root_from_nested_cwd(
    task_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(task_root / "01-first")

    cli.main(["task", "read", "01-first", "--json"])

    data = json.loads(capsys.readouterr().out)
    assert data["task"]["path"] == "01-first"
    assert data["task"]["title"] == "First"


def test_task_tree_autodetect_prefers_superra_over_plan(
    tmp_path: Path,
    task_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    legacy = tmp_path / ".plan"
    legacy.mkdir()
    _write_task_md(legacy / "task.md", "Legacy")
    monkeypatch.chdir(tmp_path)

    cli.main(["task", "tree", "--json"])

    data = json.loads(capsys.readouterr().out)
    assert data["title"] == "Root"


def test_task_tree_autodetects_legacy_plan_when_superra_absent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    legacy = tmp_path / ".plan"
    legacy.mkdir()
    _write_task_md(legacy / "task.md", "Legacy")
    monkeypatch.chdir(tmp_path)

    cli.main(["task", "tree", "--json"])

    data = json.loads(capsys.readouterr().out)
    assert data["title"] == "Legacy"


def test_task_create_uses_autodetected_root_for_legacy_wrapper(
    task_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(task_root)

    cli.main(["task", "create", "03-third", "--title", "Third"])

    created = task_root / "03-third" / "task.md"
    assert created.exists()
    assert 'title: "Third"' in created.read_text(encoding="utf-8")
    assert not (task_root / "serve").exists()


def test_task_comment_list_preserves_json_mode(
    task_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(task_root)

    cli.main(["task", "comment", "list", "01-first", "--json"])

    assert json.loads(capsys.readouterr().out) == []


@pytest.mark.parametrize(
    "argv",
    [
        ["task", "update", "../outside", "--title", "Escaped"],
        ["task", "status", "cascade", "../outside", "--status", "approved"],
        ["task", "result", "add", "../outside", "--finding", "Escaped"],
        ["task", "dep", "add", "../outside", "01-first"],
        ["task", "dep", "remove", "../outside", "01-first"],
        ["task", "rename", "../outside", "outside-renamed"],
        ["task", "rename", "01-first", "../outside-renamed"],
    ],
)
def test_mutation_commands_reject_paths_outside_root(
    task_root: Path,
    argv: list[str],
    capsys: pytest.CaptureFixture[str],
) -> None:
    outside = task_root.parent / "outside"
    outside.mkdir()
    _write_task_md(outside / "task.md", "Outside")
    before = (outside / "task.md").read_text(encoding="utf-8")

    with pytest.raises(SystemExit) as excinfo:
        cli.main([*argv, "--root", str(task_root)])

    assert excinfo.value.code == 1
    assert "escapes plan root" in capsys.readouterr().err
    assert (outside / "task.md").read_text(encoding="utf-8") == before


def test_dep_add_rejects_path_like_dependency_slug(
    task_root: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    outside = task_root.parent / "outside"
    outside.mkdir()
    _write_task_md(outside / "task.md", "Outside")

    with pytest.raises(SystemExit) as excinfo:
        cli.main(["task", "dep", "add", "02-second", "../outside", "--root", str(task_root)])

    assert excinfo.value.code == 1
    assert "dependency must be a sibling slug" in capsys.readouterr().err
    second = (task_root / "02-second" / "task.md").read_text(encoding="utf-8")
    assert "../outside" not in second


def test_task_move_cross_parent_rewrites_relative_markdown_links(
    task_root: Path,
    tmp_path: Path,
) -> None:
    code = tmp_path / "Code" / "script.py"
    code.parent.mkdir()
    code.write_text("print('ok')\n", encoding="utf-8")

    parent = task_root / "01-parent"
    parent.mkdir()
    _write_task_md(parent / "task.md", "Parent")
    child = parent / "01-child"
    child.mkdir()
    _write_task_md(child / "task.md", "Child")
    (child / "attachments").mkdir()
    (child / "attachments" / "chart.png").write_text("png", encoding="utf-8")
    task_md = child / "task.md"
    task_md.write_text(
        task_md.read_text(encoding="utf-8")
        + "\nSee [script](../../../Code/script.py#L1) and ![chart](attachments/chart.png).\n",
        encoding="utf-8",
    )

    cli.main(["task", "move", "01-parent/01-child", "03-child", "--root", str(task_root)])

    assert not child.exists()
    moved = task_root / "03-child"
    assert moved.exists()
    moved_text = (moved / "task.md").read_text(encoding="utf-8")
    assert "[script](../../Code/script.py#L1)" in moved_text
    assert "![chart](attachments/chart.png)" in moved_text
    assert (moved / "attachments" / "chart.png").exists()


def test_task_move_cross_parent_rejects_stranded_old_sibling_dependency(
    task_root: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    parent = task_root / "01-parent"
    parent.mkdir()
    _write_task_md(parent / "task.md", "Parent")
    child = parent / "01-child"
    child.mkdir()
    _write_task_md(child / "task.md", "Child")
    dependent = parent / "02-dependent"
    dependent.mkdir()
    _write_task_md(dependent / "task.md", "Dependent", depends_on=["01-child"])
    target_parent = task_root / "03-parent"
    target_parent.mkdir()
    _write_task_md(target_parent / "task.md", "Target Parent")

    with pytest.raises(SystemExit) as excinfo:
        cli.main(["task", "move", "01-parent/01-child", "03-parent/01-child", "--root", str(task_root)])

    assert excinfo.value.code == 1
    assert "would strand dependency" in capsys.readouterr().err
    assert child.exists()
    assert not (target_parent / "01-child").exists()


def test_task_move_allows_rootless_forest_destination_root(
    tmp_path: Path,
) -> None:
    root = tmp_path / "superRA"
    root.mkdir()
    parent = root / "01-parent"
    parent.mkdir()
    _write_task_md(parent / "task.md", "Parent")
    child = parent / "01-child"
    child.mkdir()
    _write_task_md(child / "task.md", "Child")

    cli.main(["task", "move", "01-parent/01-child", "02-child", "--root", str(root)])

    assert not child.exists()
    assert (root / "02-child" / "task.md").exists()


def test_task_rename_alias_cascades_same_parent_dependency(
    task_root: Path,
) -> None:
    dependent = task_root / "03-dependent"
    dependent.mkdir()
    _write_task_md(dependent / "task.md", "Dependent", depends_on=["01-first"])

    cli.main(["task", "rename", "01-first", "01-renamed", "--root", str(task_root)])

    assert not (task_root / "01-first").exists()
    assert (task_root / "01-renamed" / "task.md").exists()
    dependent_text = (dependent / "task.md").read_text(encoding="utf-8")
    assert "  - 01-renamed" in dependent_text
    assert "01-first" not in dependent_text


def test_task_rename_alias_rejects_cross_parent_move(
    task_root: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    parent = task_root / "01-parent"
    parent.mkdir()
    _write_task_md(parent / "task.md", "Parent")
    child = parent / "01-child"
    child.mkdir()
    _write_task_md(child / "task.md", "Child")

    with pytest.raises(SystemExit) as excinfo:
        cli.main(["task", "rename", "01-parent/01-child", "03-child", "--root", str(task_root)])

    assert excinfo.value.code == 1
    assert "same-parent only" in capsys.readouterr().err
    assert child.exists()
    assert not (task_root / "03-child").exists()


def test_status_fix_routes_existing_update_fix_mode(
    task_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(task_root)

    cli.main(["task", "status", "fix"])

    out = capsys.readouterr().out
    assert "Scanning" in out


def test_dashboard_export_is_top_level_command(
    task_root: Path,
    tmp_path: Path,
) -> None:
    output = tmp_path / "dashboard.html"

    cli.main(["dashboard", "export", "--root", str(task_root), "--output", str(output)])

    assert output.exists()
    assert "Root" in output.read_text(encoding="utf-8")


def test_uv_run_script_exports_dashboard_from_file_relative_assets(
    task_root: Path,
    tmp_path: Path,
) -> None:
    if shutil.which("uv") is None:
        pytest.skip("uv is required to exercise `uv run --script`")

    output = tmp_path / "packaged-dashboard.html"
    # `uv run --script plan_dashboard.py dashboard …` is the wrapper's terminal
    # exec for the dashboard subcommand: it loads the PEP 723 web stack, renders
    # templates/vendor from __file__-relative paths (loose-script mode), and is
    # project-independent (run from an unrelated tmp cwd, no caller venv).
    result = subprocess.run(
        [
            "uv",
            "run",
            "--script",
            str(SCRIPTS_DIR / "plan_dashboard.py"),
            "dashboard",
            "export",
            "--root",
            str(task_root),
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
        timeout=120,
    )

    assert result.returncode == 0, result.stderr
    html = output.read_text(encoding="utf-8")
    assert "Root" in html
    assert "window.STANDALONE = true" in html
    assert "markdown-it" in html


def test_uv_run_script_creates_no_caller_venv_with_conflicting_project(
    task_root: Path,
    tmp_path: Path,
) -> None:
    if shutil.which("uv") is None:
        pytest.skip("uv is required to exercise `uv run --script`")

    # A caller project that already carries a pyproject.toml and a .venv — the
    # exact shape that made bare `uv run superra` collide. `uv run --script` is
    # script-scoped, so it must run the CLI without provisioning the caller env.
    caller = tmp_path / "caller"
    caller.mkdir()
    (caller / "pyproject.toml").write_text(
        '[project]\nname = "caller"\nversion = "0.0.0"\nrequires-python = ">=3.10"\n',
        encoding="utf-8",
    )
    (caller / ".venv").mkdir()

    result = subprocess.run(
        [
            "uv",
            "run",
            "--script",
            str(SCRIPTS_DIR / "cli.py"),
            "task",
            "tree",
            "--root",
            str(task_root),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(caller),
        timeout=120,
    )

    assert result.returncode == 0, result.stderr
    assert "Root" in result.stdout
    # No environment was provisioned into the caller's pre-existing empty .venv.
    assert list((caller / ".venv").iterdir()) == []
    assert not (caller / ".venv" / "pyvenv.cfg").exists()


def test_python3_fallback_runs_core_without_third_party_deps(
    task_root: Path,
) -> None:
    if shutil.which("python3") is None:
        pytest.skip("python3 required")

    # The python3 fallback (no uv) must run the stdlib-only core; pyyaml is a
    # lazy import only reached by comment parsing, not by `task tree`. Run with
    # an empty PYTHONPATH and no site packages assumption beyond stdlib.
    result = subprocess.run(
        ["python3", str(SCRIPTS_DIR / "cli.py"), "task", "tree", "--root", str(task_root)],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    assert "Root" in result.stdout


def test_backward_compatible_direct_script_query(
    task_root: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "task_query.py"),
            "--plan-root",
            str(task_root),
            "--tree",
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["title"] == "Root"


def test_task_dashboard_is_not_registered(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["task", "dashboard", "--help"])

    assert excinfo.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


# --- wrapper / source-resolver surface ----------------------------------


import os

import wrapper_resolver


def test_wrapper_init_writes_executable_resolver_wrapper(
    task_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(task_root)

    cli.main(["wrapper", "init"])

    wrapper = task_root / "superra"
    assert wrapper.exists()
    assert os.access(wrapper, os.X_OK)
    content = wrapper.read_text(encoding="utf-8")
    assert content.startswith("#!/usr/bin/env bash")
    # Carries the shared resolver chain and runs scripts with `uv run --script`
    # (python3 fallback), not an install/uvx step.
    assert "_superra_resolve_source" in content
    assert "uv run --script" in content
    assert "python3" in content
    assert "uvx" not in content
    # No baked plugin/cache/version path: the only literal path is the GitHub
    # fallback subdirectory and the runtime "skills/task-tree" suffix.
    assert str(task_root) not in content


def test_wrapper_init_is_idempotent(
    task_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(task_root)

    cli.main(["wrapper", "init"])
    first = (task_root / "superra").read_text(encoding="utf-8")
    cli.main(["wrapper", "init"])
    second = (task_root / "superra").read_text(encoding="utf-8")

    assert first == second


def test_generated_wrapper_and_hook_are_valid_bash() -> None:
    if shutil.which("bash") is None:
        pytest.skip("bash required for syntax check")
    for content in (wrapper_resolver.render_wrapper(), wrapper_resolver.render_hook_shim()):
        result = subprocess.run(
            ["bash", "-n", "/dev/stdin"],
            input=content,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr


def test_dashboard_missing_web_stack_reports_friendly_error(
    task_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # When cli.py is run script-scoped (PEP 723 omits the web stack), importing
    # plan_dashboard raises ModuleNotFoundError. The handler must catch it and
    # point at the wrapper / entry script instead of leaking a raw traceback.
    def _raise(*_args, **_kwargs):
        raise ModuleNotFoundError("No module named 'fastapi'", name="fastapi")

    monkeypatch.setattr(cli, "_module_main", _raise)
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["dashboard", "export", "--root", str(task_root)])
    assert excinfo.value.code == 1
    err = capsys.readouterr().err
    assert "fastapi" in err
    assert "plan_dashboard.py" in err
    assert "Traceback" not in err


def test_committed_hook_shim_matches_generator() -> None:
    committed = (SKILL_DIR.parent.parent / "hooks" / "task-hook")
    if not committed.exists():
        pytest.skip("committed hooks/task-hook not present in this layout")
    assert committed.read_text(encoding="utf-8") == wrapper_resolver.render_hook_shim()


def test_committed_wrapper_matches_generator() -> None:
    # Symmetric to the hook test: pin the committed superRA/superra wrapper to
    # render_wrapper() so a resolver-chain edit that skips regeneration fails CI.
    committed = (SKILL_DIR.parent.parent / "superRA" / "superra")
    if not committed.exists():
        pytest.skip("committed superRA/superra not present in this layout")
    assert committed.read_text(encoding="utf-8") == wrapper_resolver.render_wrapper()


def _resolver_probe_script() -> str:
    """Bash that sources the resolver chain and prints _superra_resolve_source."""
    snippet = wrapper_resolver.render_resolver_snippet()
    return "set -uo pipefail\n" + snippet + "\n_superra_resolve_source\n"


def _render_resolver_with_subdir_flag(flag: str) -> str:
    """Render the resolver snippet with the GitHub-subdir gate forced to *flag*.

    The committed gate is ``[ "<GITHUB_REF_HAS_SUBDIR>" = "1" ]``; substituting
    the embedded literal lets a test exercise the GIT branch (flag "1") without
    flipping the source constant.
    """
    snippet = wrapper_resolver.render_resolver_snippet()
    committed = f'[ "{wrapper_resolver.GITHUB_REF_HAS_SUBDIR}" = "1" ]'
    forced = f'[ "{flag}" = "1" ]'
    assert committed in snippet
    return snippet.replace(committed, forced)


def _run_resolver_probe(env: dict[str, str], cwd: Path) -> str:
    result = subprocess.run(
        ["bash", "-c", _resolver_probe_script()],
        env=env,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


@pytest.fixture
def resolver_env(tmp_path: Path) -> dict[str, str]:
    """A clean env with HOME pointed at an empty fake home (no caches)."""
    home = tmp_path / "home"
    home.mkdir()
    env = {k: v for k, v in os.environ.items()}
    for var in ("CLAUDE_PLUGIN_ROOT", "PLUGIN_ROOT", "SUPERRA_REPO_ROOT"):
        env.pop(var, None)
    env["HOME"] = str(home)
    return env


def test_resolver_env_var_outranks_everything(
    tmp_path: Path,
    resolver_env: dict[str, str],
) -> None:
    if shutil.which("bash") is None:
        pytest.skip("bash required")
    plugin = tmp_path / "envplugin"
    (plugin / "skills" / "task-tree" / "scripts").mkdir(parents=True)
    (plugin / "skills" / "task-tree" / "scripts" / "cli.py").touch()
    resolver_env["CLAUDE_PLUGIN_ROOT"] = str(plugin)

    out = _run_resolver_probe(resolver_env, tmp_path)
    assert out == f"DIR:{plugin}/skills/task-tree"


def test_resolver_fails_fast_when_no_source_and_pin_lacks_subdir(
    tmp_path: Path,
    resolver_env: dict[str, str],
) -> None:
    # While GITHUB_REF_HAS_SUBDIR is "0" the pinned ref does not yet carry
    # skills/task-tree, so the GitHub branch fails fast (no `GIT:` spec, no
    # shallow clone) rather than cloning the whole repo only to fail the cli.py
    # existence test.
    if shutil.which("bash") is None:
        pytest.skip("bash required")
    assert wrapper_resolver.GITHUB_REF_HAS_SUBDIR == "0"

    result = subprocess.run(
        ["bash", "-c", _resolver_probe_script()],
        env=resolver_env,
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode != 0
    assert result.stdout.strip() == ""


def test_resolver_emits_github_spec_when_pin_carries_subdir(
    tmp_path: Path,
    resolver_env: dict[str, str],
) -> None:
    # When the pin is flipped to carry the subdir, the GitHub branch resolves to
    # the shallow-clone target (repo@ref); `uv run --script` cannot fetch a git
    # subdirectory, so the clone carries the loose scripts.
    if shutil.which("bash") is None:
        pytest.skip("bash required")
    snippet = _render_resolver_with_subdir_flag("1")
    result = subprocess.run(
        ["bash", "-c", "set -uo pipefail\n" + snippet + "\n_superra_resolve_source\n"],
        env=resolver_env,
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "GIT:https://github.com/FuZhiyu/superRA.git@main"


def test_resolver_github_branch_clones_then_resolves_loose_script(
    tmp_path: Path,
    resolver_env: dict[str, str],
) -> None:
    """When only GitHub resolves, the branch shallow-clones and points at the
    loose ``scripts/cli.py`` inside the clone — the script `uv run --script`
    then executes. Uses a local bare remote so no network is needed."""
    if shutil.which("bash") is None or shutil.which("git") is None:
        pytest.skip("bash + git required")

    # Build a local bare remote carrying skills/task-tree/scripts/cli.py.
    work = tmp_path / "work"
    (work / "skills" / "task-tree" / "scripts").mkdir(parents=True)
    (work / "skills" / "task-tree" / "scripts" / "cli.py").write_text(
        'print("FAKE CLONE CLI RAN")\n', encoding="utf-8"
    )
    remote = tmp_path / "remote.git"
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    for cmd in (
        ["git", "init", "-q", "-b", "main", str(work)],
        ["git", "-C", str(work), "add", "-A"],
        ["git", "-C", str(work), "commit", "-qm", "init"],
        ["git", "init", "-q", "--bare", "-b", "main", str(remote)],
        ["git", "-C", str(work), "remote", "add", "origin", str(remote)],
        ["git", "-C", str(work), "push", "-q", "origin", "main"],
    ):
        subprocess.run(cmd, check=True, env=env, capture_output=True, timeout=60)

    # Rewrite the resolver's GitHub repo to the local bare remote, force the
    # subdir gate on (the pin does not yet carry the subdir), then resolve.
    snippet = _render_resolver_with_subdir_flag("1").replace(
        "https://github.com/FuZhiyu/superRA.git", str(remote)
    )
    cache = tmp_path / "cache"
    probe_env = {**resolver_env, "XDG_CACHE_HOME": str(cache)}
    result = subprocess.run(
        ["bash", "-c", "set -uo pipefail\n" + snippet + "\n_superra_resolve_dir\n"],
        env=probe_env,
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    resolved = result.stdout.strip()
    assert resolved.endswith("/skills/task-tree")
    assert (Path(resolved) / "scripts" / "cli.py").exists()


def test_resolver_picks_claude_manifest_over_codex(
    tmp_path: Path,
    resolver_env: dict[str, str],
) -> None:
    if shutil.which("bash") is None or shutil.which("python3") is None:
        pytest.skip("bash + python3 required")
    home = Path(resolver_env["HOME"])
    claude_install = tmp_path / "claude-install"
    (claude_install / "skills" / "task-tree" / "scripts").mkdir(parents=True)
    (claude_install / "skills" / "task-tree" / "scripts" / "cli.py").touch()
    (home / ".claude" / "plugins").mkdir(parents=True)
    manifest = home / ".claude" / "plugins" / "installed_plugins.json"
    manifest.write_text(
        json.dumps(
            {
                "version": 1,
                "plugins": {
                    "superRA@superRA": [
                        {"scope": "user", "installPath": str(claude_install), "projectPath": None}
                    ]
                },
            }
        ),
        encoding="utf-8",
    )
    # Also lay down a codex cache; the Claude manifest must still win.
    codex = home / ".codex" / "plugins" / "cache" / "superRA" / "superra" / "0.9.0" / "skills" / "task-tree"
    (codex / "scripts").mkdir(parents=True)
    (codex / "scripts" / "cli.py").touch()

    out = _run_resolver_probe(resolver_env, tmp_path)
    assert out == f"DIR:{claude_install}/skills/task-tree"


def test_resolver_codex_picks_highest_semver_within_depth_bound(
    tmp_path: Path,
    resolver_env: dict[str, str],
) -> None:
    if shutil.which("bash") is None:
        pytest.skip("bash required")
    home = Path(resolver_env["HOME"])
    cache = home / ".codex" / "plugins" / "cache" / "superRA" / "superra"
    for ver in ("0.1.0", "0.10.0", "0.2.0"):
        d = cache / ver / "skills" / "task-tree" / "scripts"
        d.mkdir(parents=True)
        (d / "cli.py").touch()
    # Decoy nested too deep for the depth-3 glob; must be ignored.
    deep = cache / "extra" / "deep" / "0.99.0" / "skills" / "task-tree" / "scripts"
    deep.mkdir(parents=True)
    (deep / "cli.py").touch()

    out = _run_resolver_probe(resolver_env, tmp_path)
    assert out == f"DIR:{cache}/0.10.0/skills/task-tree"


def test_resolver_skips_cache_lacking_cli_script(
    tmp_path: Path,
    resolver_env: dict[str, str],
) -> None:
    if shutil.which("bash") is None or shutil.which("python3") is None:
        pytest.skip("bash + python3 required")
    home = Path(resolver_env["HOME"])
    # Claude manifest points at an install dir missing the cli.py entry script.
    stale = tmp_path / "stale-claude"
    (stale / "skills" / "task-tree" / "scripts").mkdir(parents=True)  # no cli.py
    (home / ".claude" / "plugins").mkdir(parents=True)
    (home / ".claude" / "plugins" / "installed_plugins.json").write_text(
        json.dumps(
            {
                "version": 1,
                "plugins": {
                    "superRA@superRA": [
                        {"scope": "user", "installPath": str(stale), "projectPath": None}
                    ]
                },
            }
        ),
        encoding="utf-8",
    )
    # Codex cache has a usable package; resolution must fall through to it.
    codex = home / ".codex" / "plugins" / "cache" / "superRA" / "superra" / "0.3.0" / "skills" / "task-tree"
    (codex / "scripts").mkdir(parents=True)
    (codex / "scripts" / "cli.py").touch()

    out = _run_resolver_probe(resolver_env, tmp_path)
    assert out == f"DIR:{codex}"
