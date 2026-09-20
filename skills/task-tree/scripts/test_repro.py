"""Tests for the reproduction graph model (_repro.py).

Covers the bounded YAML subset parser, ``## Reproduction`` section extraction,
variable resolution, Julia include closures, edge inference, external-input
classification, and every validation finding the contract defines.
"""

from __future__ import annotations

import json
import math

import pytest

from _repro import (
    Graph,
    PathRef,
    YamlSubsetError,
    build_graph,
    check_reproduction,
    extract_repro_block,
    graph_to_dict,
    include_closure,
    interpolate,
    parse_yaml_subset,
    resolve_variables,
)


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _write_repro_task(
    directory, title, block, *, status="not-started", depends_on=(), objective="Obj."
):
    """Write a task.md carrying a ``## Reproduction`` section holding *block*."""
    directory.mkdir(parents=True, exist_ok=True)
    deps_yaml = (
        "\n" + "".join(f"  - {d}\n" for d in depends_on) if depends_on else " []\n"
    )
    body = f"## Objective\n\n{objective}\n"
    if block is not None:
        body += f"\n## Reproduction\n\n```yaml\n{block.strip()}\n```\n"
    text = (
        "---\n"
        f'title: "{title}"\n'
        f"status: {status}\n"
        f"depends_on:{deps_yaml}"
        "---\n\n"
        f"{body}"
    )
    (directory / "task.md").write_text(text, encoding="utf-8")


def _plan(tmp_path):
    root = tmp_path / "superRA"
    root.mkdir()
    return root


def _no_shell(command, cwd):  # pragma: no cover - guards against real subprocesses
    raise AssertionError(f"unexpected shell evaluation: {command}")


def _graph(plan_root, **kwargs):
    kwargs.setdefault("env", {})
    kwargs.setdefault("shell_runner", _no_shell)
    return build_graph(plan_root, **kwargs)


def _messages(graph: Graph, severity=None):
    return [
        f.message
        for f in graph.findings
        if severity is None or f.severity == severity
    ]


def _has(graph: Graph, severity, fragment):
    return any(fragment in m for m in _messages(graph, severity))


# ---------------------------------------------------------------------------
# YAML subset — accepted forms
# ---------------------------------------------------------------------------

class TestSubsetAccepts:
    def test_block_mapping_and_nested_mapping(self):
        assert parse_yaml_subset("a: 1\nb:\n  c: two\n") == {"a": 1, "b": {"c": "two"}}

    def test_block_list_of_scalars_indented_and_flush(self):
        indented = parse_yaml_subset("deps:\n  - a\n  - b\n")
        flush = parse_yaml_subset("deps:\n- a\n- b\n")
        assert indented == flush == {"deps": ["a", "b"]}

    def test_block_list_of_mappings(self):
        parsed = parse_yaml_subset(
            "outs:\n  - path: out/big.arrow\n    sidecar: out/big.sha256\n"
        )
        assert parsed == {"outs": [{"path": "out/big.arrow", "sidecar": "out/big.sha256"}]}

    def test_inline_list_of_scalars(self):
        assert parse_yaml_subset("deps: [a, b, c]") == {"deps": ["a", "b", "c"]}

    def test_inline_list_empty_and_quoted_items(self):
        assert parse_yaml_subset("a: []\nb: [\"x, y\", 'z']") == {
            "a": [],
            "b": ["x, y", "z"],
        }

    def test_quoted_scalars_and_escapes(self):
        parsed = parse_yaml_subset('a: "tab\\there"\nb: \'it\'\'s\'\n')
        assert parsed == {"a": "tab\there", "b": "it's"}

    def test_comments_are_dropped_but_hashes_in_scalars_survive(self):
        parsed = parse_yaml_subset(
            "# leading comment\n"
            "cmd: julia run.jl  # trailing comment\n"
            "tag: v1#2\n"
        )
        assert parsed == {"cmd": "julia run.jl", "tag": "v1#2"}

    def test_hash_inside_a_quoted_scalar_is_content(self):
        assert parse_yaml_subset('cmd: "echo # not a comment"') == {
            "cmd": "echo # not a comment"
        }

    def test_implicit_scalar_typing_matches_yaml(self):
        parsed = parse_yaml_subset(
            "i: 42\nf: 0.5\nt: true\nfalsey: off\nnothing: ~\ns: 1.2.3\n"
        )
        assert parsed == {
            "i": 42,
            "f": 0.5,
            "t": True,
            "falsey": False,
            "nothing": None,
            "s": "1.2.3",
        }

    def test_special_floats(self):
        parsed = parse_yaml_subset("a: .inf\nb: -.inf\nc: .nan\n")
        assert parsed["a"] == math.inf
        assert parsed["b"] == -math.inf
        assert math.isnan(parsed["c"])

    def test_empty_document(self):
        assert parse_yaml_subset("") is None
        assert parse_yaml_subset("\n# only a comment\n") is None

    def test_key_with_no_value_is_null(self):
        assert parse_yaml_subset("a:\nb: 1\n") == {"a": None, "b": 1}


# ---------------------------------------------------------------------------
# YAML subset — rejected forms
# ---------------------------------------------------------------------------

class TestSubsetRejects:
    @pytest.mark.parametrize(
        "text, fragment",
        [
            ("a: &anchor 1\n", "anchors"),
            ("a: *anchor\n", "aliases"),
            ("a: !!str 1\n", "tags"),
            ("a: !custom 1\n", "tags"),
            ("a: |\n  multi\n  line\n", "literal block scalars"),
            ("a: >\n  folded\n  text\n", "folded block scalars"),
            ("a: {b: c}\n", "inline mappings"),
            ("a: [[1, 2]]\n", "nested inline lists"),
            ("a: [${OUT}/x]\n", "flow indicator"),
            ("a: 1\na: 2\n", "duplicate mapping key"),
            ("\ta: 1\n", "tabs"),
            ("just prose\n", "expected 'key: value'"),
            ('a: "unterminated\n', "unterminated"),
            ("a: 1\n    b: 2\n", "unexpected indentation"),
        ],
    )
    def test_rejected(self, text, fragment):
        with pytest.raises(YamlSubsetError) as excinfo:
            parse_yaml_subset(text)
        assert fragment in str(excinfo.value)

    def test_error_carries_a_line_number(self):
        with pytest.raises(YamlSubsetError) as excinfo:
            parse_yaml_subset("a: 1\nb: |\n  text\n")
        assert excinfo.value.line == 2


class TestPyyamlAgreement:
    """The optional dependency must read every accepted text identically."""

    FIXTURES = [
        "steps: []\n",
        (
            "steps:\n"
            "  - name: build-panel\n"
            "    cmd: julia --project=. Code/build_panel.jl\n"
            "    deps:\n"
            "      - Code/build_panel.jl\n"
            "      - ${DATA}/raw.csv\n"
            "    outs:\n"
            "      - ${OUT}/panel.parquet\n"
            "      - path: ${OUT}/big.arrow\n"
            "        sidecar: ${OUT}/big.arrow.sha256\n"
            "    params:\n"
            "      seed: 42\n"
            "      trim: 0.01\n"
            "      verbose: true\n"
            "      label: \"a, b\"\n"
            "  - name: check-panel  # drift check\n"
            "    kind: check\n"
            "    cmd: julia --project=. test/check_panel.jl\n"
            "    deps: [\"${OUT}/panel.parquet\", test/check_panel.jl]\n"
        ),
        (
            "reproduction:\n"
            "  vars:\n"
            "    DATA: data/raw\n"
            "    OUT:\n"
            "      shell: \"echo output\"\n"
            "    HOME_DIR:\n"
            "      env: HOME\n"
            "  runners:\n"
            "    julia: julia --project=. {script}\n"
            "  env_deps:\n"
            "    - Project.toml\n"
            "    - Manifest.toml\n"
            "  code_roots: [Code, test]\n"
        ),
    ]

    @pytest.mark.parametrize("text", FIXTURES)
    def test_identical_to_pyyaml(self, text):
        yaml = pytest.importorskip("yaml")
        assert json.dumps(parse_yaml_subset(text), sort_keys=True) == json.dumps(
            yaml.safe_load(text), sort_keys=True
        )


# ---------------------------------------------------------------------------
# Section extraction
# ---------------------------------------------------------------------------

class TestSectionExtraction:
    def test_extracts_the_fenced_block(self):
        assert extract_repro_block("\n```yaml\nsteps: []\n```\n") == "steps: []"

    def test_prose_outside_the_fence_is_rejected(self):
        with pytest.raises(YamlSubsetError) as excinfo:
            extract_repro_block("These steps rebuild the panel.\n\n```yaml\nsteps: []\n```\n")
        assert "prose outside the fenced yaml block" in str(excinfo.value)

    def test_trailing_prose_is_rejected(self):
        with pytest.raises(YamlSubsetError):
            extract_repro_block("```yaml\nsteps: []\n```\n\nSee the runner docs.\n")

    def test_a_second_block_is_rejected(self):
        with pytest.raises(YamlSubsetError) as excinfo:
            extract_repro_block("```yaml\nsteps: []\n```\n```yaml\nsteps: []\n```\n")
        assert "exactly one fenced yaml block" in str(excinfo.value)

    def test_non_yaml_info_string_is_rejected(self):
        with pytest.raises(YamlSubsetError) as excinfo:
            extract_repro_block("```\nsteps: []\n```\n")
        assert "must be ```yaml" in str(excinfo.value)

    def test_unclosed_fence_is_rejected(self):
        with pytest.raises(YamlSubsetError):
            extract_repro_block("```yaml\nsteps: []\n")


# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

class TestVariables:
    def test_literal_env_and_shell_sources(self, tmp_path):
        values, errors = resolve_variables(
            {
                "DATA": "data/raw",
                "HOME_DIR": {"env": "FAKE_HOME"},
                "OUT": {"shell": "echo output/sandbox"},
            },
            tmp_path,
            env={"FAKE_HOME": "/home/researcher"},
            shell_runner=lambda cmd, cwd: "output/sandbox",
        )
        assert errors == []
        assert values == {
            "DATA": "data/raw",
            "HOME_DIR": "/home/researcher",
            "OUT": "output/sandbox",
        }

    def test_shell_runs_once_per_invocation(self, tmp_path):
        calls = []
        resolve_variables(
            {"OUT": {"shell": "echo x"}},
            tmp_path,
            env={},
            shell_runner=lambda cmd, cwd: calls.append(cmd) or "x",
        )
        assert calls == ["echo x"]

    def test_missing_env_var_is_an_error(self, tmp_path):
        _, errors = resolve_variables(
            {"HOME_DIR": {"env": "ABSENT"}}, tmp_path, env={}, shell_runner=_no_shell
        )
        assert "is not set" in errors[0]

    def test_failing_shell_is_an_error(self, tmp_path):
        def boom(cmd, cwd):
            raise RuntimeError("exit 1")

        _, errors = resolve_variables(
            {"OUT": {"shell": "false"}}, tmp_path, env={}, shell_runner=boom
        )
        assert "shell command failed" in errors[0]

    def test_unknown_spec_shape_is_an_error(self, tmp_path):
        _, errors = resolve_variables(
            {"OUT": {"file": "x"}}, tmp_path, env={}, shell_runner=_no_shell
        )
        assert "literal" in errors[0]

    def test_interpolate_reports_unknown_names(self):
        text, unknown = interpolate("${OUT}/a/${MISSING}", {"OUT": "output"})
        assert text == "output/a/${MISSING}"
        assert unknown == ["MISSING"]


# ---------------------------------------------------------------------------
# Julia include closures
# ---------------------------------------------------------------------------

class TestIncludeClosure:
    def test_transitive_nested_includes(self, tmp_path):
        code = tmp_path / "Code"
        (code / "helpers").mkdir(parents=True)
        (code / "run.jl").write_text(
            'include("setup.jl")\n'
            'include(joinpath(@__DIR__, "helpers", "io.jl"))\n',
            encoding="utf-8",
        )
        (code / "setup.jl").write_text('include("helpers/stats.jl")\n', encoding="utf-8")
        (code / "helpers" / "io.jl").write_text("# leaf\n", encoding="utf-8")
        (code / "helpers" / "stats.jl").write_text("# leaf\n", encoding="utf-8")

        found, warnings_out = include_closure(code / "run.jl", tmp_path)
        assert found == [
            "Code/helpers/io.jl",
            "Code/helpers/stats.jl",
            "Code/setup.jl",
        ]
        assert warnings_out == []

    def test_cycles_terminate(self, tmp_path):
        code = tmp_path / "Code"
        code.mkdir()
        (code / "a.jl").write_text('include("b.jl")\n', encoding="utf-8")
        (code / "b.jl").write_text('include("a.jl")\n', encoding="utf-8")
        found, _ = include_closure(code / "a.jl", tmp_path)
        assert found == ["Code/b.jl"]

    def test_commented_include_is_ignored(self, tmp_path):
        code = tmp_path / "Code"
        code.mkdir()
        (code / "a.jl").write_text('# include("gone.jl")\n', encoding="utf-8")
        found, warnings_out = include_closure(code / "a.jl", tmp_path)
        assert found == []
        assert warnings_out == []

    def test_project_root_anchored_includes_resolve(self, tmp_path):
        """DrWatson's `projectdir` and a variable repo root are the dominant idioms."""
        code = tmp_path / "Code"
        (code / "Sub").mkdir(parents=True)
        (code / "Sub" / "run.jl").write_text(
            'include(projectdir("Code", "helpers.jl"))\n'
            'include(projectdir("Code/paths.jl"))\n'
            'include(joinpath(projectdir(), "Code", "io.jl"))\n'
            'include(joinpath(REPO_ROOT, "Code", "stats.jl"))\n',
            encoding="utf-8",
        )
        for name in ("helpers.jl", "paths.jl", "io.jl", "stats.jl"):
            (code / name).write_text("# leaf\n", encoding="utf-8")

        found, warnings_out = include_closure(code / "Sub" / "run.jl", tmp_path)
        assert found == [
            "Code/helpers.jl",
            "Code/io.jl",
            "Code/paths.jl",
            "Code/stats.jl",
        ]
        assert warnings_out == []

    def test_variable_root_falls_back_to_the_including_directory(self, tmp_path):
        code = tmp_path / "Code"
        code.mkdir()
        (code / "run.jl").write_text(
            'include(joinpath(HERE, "helper.jl"))\n', encoding="utf-8"
        )
        (code / "helper.jl").write_text("# leaf\n", encoding="utf-8")
        found, warnings_out = include_closure(code / "run.jl", tmp_path)
        assert found == ["Code/helper.jl"]
        assert warnings_out == []

    def test_variable_root_ambiguity_warns(self, tmp_path):
        """Both a project-root and an including-directory candidate existing is ambiguous."""
        code = tmp_path / "Code"
        code.mkdir()
        (tmp_path / "helper.jl").write_text("# root-relative leaf\n", encoding="utf-8")
        (code / "helper.jl").write_text("# dir-relative leaf\n", encoding="utf-8")
        (code / "run.jl").write_text(
            'include(joinpath(SHARE, "helper.jl"))\n', encoding="utf-8"
        )
        found, warnings_out = include_closure(code / "run.jl", tmp_path)
        assert found == ["helper.jl"]
        assert "matches both helper.jl and Code/helper.jl" in warnings_out[0]

    def test_srcdir_and_scriptsdir_resolve_as_direct_include_arguments(self, tmp_path):
        """DrWatson's `srcdir`/`scriptsdir` resolve as direct calls, not only inside `joinpath`."""
        code = tmp_path / "Code"
        code.mkdir()
        (tmp_path / "src").mkdir()
        (tmp_path / "scripts").mkdir()
        (code / "run.jl").write_text(
            'include(srcdir("model.jl"))\n'
            'include(scriptsdir("run_estimates.jl"))\n',
            encoding="utf-8",
        )
        (tmp_path / "src" / "model.jl").write_text("# leaf\n", encoding="utf-8")
        (tmp_path / "scripts" / "run_estimates.jl").write_text("# leaf\n", encoding="utf-8")

        found, warnings_out = include_closure(code / "run.jl", tmp_path)
        assert found == ["scripts/run_estimates.jl", "src/model.jl"]
        assert warnings_out == []

    def test_two_argument_include_warns(self, tmp_path):
        """`Base.include(mod, path)` evaluates into a module; the path is not static."""
        code = tmp_path / "Code"
        code.mkdir()
        (code / "a.jl").write_text("include(mod, path)\n", encoding="utf-8")
        found, warnings_out = include_closure(code / "a.jl", tmp_path)
        assert found == []
        assert "not a static path" in warnings_out[0]

    def test_dynamic_include_warns(self, tmp_path):
        code = tmp_path / "Code"
        code.mkdir()
        (code / "a.jl").write_text("include(script_name)\n", encoding="utf-8")
        found, warnings_out = include_closure(code / "a.jl", tmp_path)
        assert found == []
        assert "not a static path" in warnings_out[0]

    def test_missing_include_target_warns(self, tmp_path):
        code = tmp_path / "Code"
        code.mkdir()
        (code / "a.jl").write_text('include("gone.jl")\n', encoding="utf-8")
        found, warnings_out = include_closure(code / "a.jl", tmp_path)
        assert found == []
        assert "does not exist" in warnings_out[0]


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

class TestGraphConstruction:
    def test_unregistered_tasks_produce_an_empty_clean_graph(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(plan / "01-load", "Load", None)
        graph = _graph(plan)
        assert graph.steps == []
        assert graph.section_tasks == []
        assert graph.findings == []

    def test_section_presence_registers_the_task(self, tmp_path):
        plan = _plan(tmp_path)
        (tmp_path / "run.sh").write_text("echo hi\n", encoding="utf-8")
        _write_repro_task(
            plan / "01-load",
            "Load",
            "steps:\n  - name: load\n    cmd: sh run.sh\n    deps: [run.sh]\n    outs: [out/raw.csv]\n",
        )
        graph = _graph(plan)
        assert graph.section_tasks == ["01-load"]
        step = graph.step("load")
        assert step.kind == "build"
        assert step.task_path == "01-load"

    def test_variables_resolve_in_cmd_deps_and_outs(self, tmp_path):
        plan = _plan(tmp_path)
        (plan / "config.yaml").write_text(
            "reproduction:\n"
            "  vars:\n"
            "    DATA: data/raw\n"
            "    OUT:\n"
            "      shell: \"echo output/sandbox\"\n",
            encoding="utf-8",
        )
        _write_repro_task(
            plan / "01-load",
            "Load",
            "steps:\n"
            "  - name: load\n"
            "    cmd: sh build.sh ${DATA} ${OUT}\n"
            "    deps:\n"
            "      - ${DATA}/raw.csv\n"
            "    outs:\n"
            "      - ${OUT}/panel.parquet\n",
        )
        graph = build_graph(
            plan, env={}, shell_runner=lambda cmd, cwd: "output/sandbox"
        )
        step = graph.step("load")
        assert step.cmd == "sh build.sh data/raw output/sandbox"
        assert step.cmd_logical == "sh build.sh ${DATA} ${OUT}"
        assert step.declared_deps == [
            PathRef(logical="${DATA}/raw.csv", resolved="data/raw/raw.csv")
        ]
        assert step.outs[0].path == PathRef(
            logical="${OUT}/panel.parquet", resolved="output/sandbox/panel.parquet"
        )

    def test_runner_template_expands_and_the_script_becomes_a_dep(self, tmp_path):
        plan = _plan(tmp_path)
        (plan / "config.yaml").write_text(
            "reproduction:\n  runners:\n    julia: julia --project=. {script}\n",
            encoding="utf-8",
        )
        _write_repro_task(
            plan / "01-load",
            "Load",
            "steps:\n"
            "  - name: figures\n"
            "    runner: julia\n"
            "    script: Code/figures.jl\n"
            "    outs: [output/fig.pdf]\n",
        )
        step = _graph(plan).step("figures")
        assert step.cmd == "julia --project=. Code/figures.jl"
        assert step.deps[0].logical == "Code/figures.jl"

    def test_env_deps_join_every_step(self, tmp_path):
        plan = _plan(tmp_path)
        (plan / "config.yaml").write_text(
            "reproduction:\n  env_deps:\n    - Project.toml\n    - Manifest.toml\n",
            encoding="utf-8",
        )
        _write_repro_task(
            plan / "01-load", "Load", "steps:\n  - name: load\n    cmd: true\n"
        )
        assert [d.logical for d in _graph(plan).step("load").deps] == [
            "Project.toml",
            "Manifest.toml",
        ]

    def test_env_deps_interpolate_variables(self, tmp_path):
        plan = _plan(tmp_path)
        (plan / "config.yaml").write_text(
            "reproduction:\n"
            "  vars:\n"
            "    SCRATCH: build/scratch\n"
            "  env_deps:\n"
            '    - "${SCRATCH}/env.lock"\n',
            encoding="utf-8",
        )
        _write_repro_task(
            plan / "01-load", "Load", "steps:\n  - name: load\n    cmd: true\n"
        )
        dep = _graph(plan).step("load").deps[0]
        assert (dep.logical, dep.resolved) == (
            "${SCRATCH}/env.lock",
            "build/scratch/env.lock",
        )

    def test_julia_deps_pull_in_their_include_closure(self, tmp_path):
        plan = _plan(tmp_path)
        code = tmp_path / "Code"
        code.mkdir()
        (code / "run.jl").write_text('include("helper.jl")\n', encoding="utf-8")
        (code / "helper.jl").write_text("# leaf\n", encoding="utf-8")
        _write_repro_task(
            plan / "01-load",
            "Load",
            "steps:\n"
            "  - name: load\n"
            "    cmd: julia Code/run.jl\n"
            "    deps: [Code/run.jl]\n"
            "    outs: [out/raw.csv]\n",
        )
        assert [d.logical for d in _graph(plan).step("load").deps] == [
            "Code/run.jl",
            "Code/helper.jl",
        ]

    def test_params_are_carried_onto_the_step(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(
            plan / "01-load",
            "Load",
            "steps:\n  - name: load\n    cmd: true\n    params:\n      seed: 42\n      trim: 0.01\n",
        )
        assert _graph(plan).step("load").params == {"seed": 42, "trim": 0.01}


# ---------------------------------------------------------------------------
# Edges, external inputs, serialization
# ---------------------------------------------------------------------------

def _two_task_pipeline(tmp_path, *, second_outs="outs: [output/table.tex]"):
    plan = _plan(tmp_path)
    (tmp_path / "input.csv").write_text("x\n", encoding="utf-8")
    _write_repro_task(
        plan / "01-build",
        "Build",
        "steps:\n"
        "  - name: build\n"
        "    cmd: sh build.sh\n"
        "    deps: [input.csv]\n"
        "    outs: [output/panel.parquet]\n",
    )
    _write_repro_task(
        plan / "02-estimate",
        "Estimate",
        "steps:\n"
        "  - name: estimate\n"
        "    cmd: sh estimate.sh\n"
        "    deps: [output/panel.parquet]\n"
        f"    {second_outs}\n",
        depends_on=["01-build"],
    )
    return plan


class TestEdges:
    def test_step_and_task_edges_follow_the_files(self, tmp_path):
        graph = _graph(_two_task_pipeline(tmp_path))
        assert graph.step_edges == [("build", "estimate", "output/panel.parquet")]
        assert graph.task_edges == [("01-build", "02-estimate")]

    def test_a_directory_out_produces_every_file_below_it(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(
            plan / "01-build",
            "Build",
            "steps:\n  - name: build\n    cmd: sh build.sh\n    outs: [output/figures]\n",
        )
        _write_repro_task(
            plan / "02-paper",
            "Paper",
            "steps:\n"
            "  - name: paper\n"
            "    cmd: latexmk paper.tex\n"
            "    deps: [output/figures/fig1.pdf]\n"
            "    outs: [output/paper.pdf]\n",
            depends_on=["01-build"],
        )
        graph = _graph(plan)
        assert graph.step_edges == [("build", "paper", "output/figures/fig1.pdf")]
        assert graph.external_inputs == []

    def test_a_dep_no_step_produces_is_an_external_input(self, tmp_path):
        graph = _graph(_two_task_pipeline(tmp_path))
        assert [e.path.logical for e in graph.external_inputs] == ["input.csv"]
        assert graph.external_inputs[0].consumers == ["build"]
        assert graph.external_inputs[0].exists is True

    def test_a_step_reading_its_own_out_is_a_cycle(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(
            plan / "01-build",
            "Build",
            "steps:\n"
            "  - name: build\n"
            "    cmd: sh build.sh\n"
            "    deps: [output/panel.parquet]\n"
            "    outs: [output/panel.parquet]\n",
        )
        graph = _graph(plan)
        assert graph.step_edges == [("build", "build", "output/panel.parquet")]
        assert _has(graph, "error", "step cycle")
        assert graph.external_inputs == []

    def test_json_serialization_round_trips(self, tmp_path):
        payload = graph_to_dict(_graph(_two_task_pipeline(tmp_path)))
        assert json.loads(json.dumps(payload)) == payload
        assert [t["path"] for t in payload["tasks"]] == ["01-build", "02-estimate"]
        assert payload["step_edges"] == [
            {"from": "build", "to": "estimate", "via": "output/panel.parquet"}
        ]
        assert [(e["from"], e["to"]) for e in payload["task_edges"]] == [("01-build", "02-estimate")]
        assert {e["kind"] for e in payload["task_edges"][0]["evidence"]} == {"logical", "inferred"}
        assert payload["steps"][0]["outs"][0]["sidecar"] is None

    def test_sidecar_survives_into_the_serialized_out(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(
            plan / "01-build",
            "Build",
            "steps:\n"
            "  - name: build\n"
            "    cmd: sh build.sh\n"
            "    outs:\n"
            "      - path: output/big.arrow\n"
            "        sidecar: output/big.arrow.sha256\n",
        )
        out = graph_to_dict(_graph(plan))["steps"][0]["outs"][0]
        assert out["sidecar"]["logical"] == "output/big.arrow.sha256"


# ---------------------------------------------------------------------------
# Validation findings
# ---------------------------------------------------------------------------

class TestFindings:
    def test_a_complete_graph_on_a_fresh_clone_checks_clean(self, tmp_path):
        plan = _two_task_pipeline(tmp_path)
        assert _graph(plan).findings == []

    def test_never_built_outs_are_not_findings(self, tmp_path):
        plan = _two_task_pipeline(tmp_path)
        assert not (tmp_path / "output").exists()
        assert _graph(plan).findings == []

    def test_duplicate_step_names_across_the_tree(self, tmp_path):
        plan = _plan(tmp_path)
        for slug in ("01-a", "02-b"):
            _write_repro_task(
                plan / slug, slug, "steps:\n  - name: load\n    cmd: true\n"
            )
        graph = _graph(plan)
        assert _has(graph, "error", "step name 'load' is already used by task 01-a")
        assert len(graph.steps) == 1

    def test_two_steps_declaring_the_same_out(self, tmp_path):
        plan = _plan(tmp_path)
        for slug, name in (("01-a", "first"), ("02-b", "second")):
            _write_repro_task(
                plan / slug,
                slug,
                f"steps:\n  - name: {name}\n    cmd: true\n    outs: [output/panel.parquet]\n",
            )
        assert _has(_graph(plan), "error", "is declared by both step 'first'")

    def test_check_step_with_outs(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(
            plan / "01-a",
            "A",
            "steps:\n  - name: drift\n    kind: check\n    cmd: true\n    outs: [out/x]\n",
        )
        assert _has(_graph(plan), "error", "check step 'drift' declares outs")

    def test_prose_outside_the_fence(self, tmp_path):
        plan = _plan(tmp_path)
        (plan / "01-a").mkdir()
        (plan / "01-a" / "task.md").write_text(
            '---\ntitle: "A"\nstatus: not-started\ndepends_on: []\n---\n\n'
            "## Objective\n\nObj.\n\n"
            "## Reproduction\n\nThese steps rebuild the panel.\n\n"
            "```yaml\nsteps: []\n```\n",
            encoding="utf-8",
        )
        assert _has(_graph(plan), "error", "prose outside the fenced yaml block")

    def test_yaml_outside_the_subset_in_a_section(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(
            plan / "01-a", "A", "steps:\n  - name: load\n    cmd: |\n      echo hi\n"
        )
        assert _has(_graph(plan), "error", "literal block scalars")

    def test_yaml_outside_the_subset_in_config(self, tmp_path):
        plan = _plan(tmp_path)
        (plan / "config.yaml").write_text(
            "reproduction:\n  vars: &base\n    DATA: data\n", encoding="utf-8"
        )
        assert _has(_graph(plan), "error", "anchors")

    def test_unknown_config_key(self, tmp_path):
        plan = _plan(tmp_path)
        (plan / "config.yaml").write_text(
            "reproduction:\n  variables:\n    DATA: data\n", encoding="utf-8"
        )
        assert _has(_graph(plan), "error", "unknown 'reproduction' key 'variables'")

    def test_unknown_variable(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(
            plan / "01-a",
            "A",
            "steps:\n  - name: load\n    cmd: true\n    outs:\n      - ${MISSING}/x.csv\n",
        )
        graph = _graph(plan)
        assert _has(graph, "error", "references unknown variable ${MISSING}")
        assert graph.steps == []

    def test_unknown_section_key(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(plan / "01-a", "A", "level: high\nsteps: []\n")
        assert _has(_graph(plan), "error", "unknown key 'level'")

    def test_unknown_step_key(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(
            plan / "01-a", "A", "steps:\n  - name: load\n    cmd: true\n    output: x\n"
        )
        assert _has(_graph(plan), "error", "unknown step key 'output'")

    def test_step_needs_exactly_one_of_cmd_or_runner(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(plan / "01-a", "A", "steps:\n  - name: load\n")
        assert _has(_graph(plan), "error", "must declare either 'cmd' or 'runner'")

    def test_undefined_runner(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(
            plan / "01-a",
            "A",
            "steps:\n  - name: load\n    runner: julia\n    script: Code/run.jl\n",
        )
        assert _has(_graph(plan), "error", "which config.yaml does not define")

    @pytest.mark.parametrize(
        "block, fragment",
        [
            ("steps:\n  - cmd: true\n", "step 'name' must be a slug, found None"),
            (
                "steps:\n  - name: load panel\n    cmd: true\n",
                "step 'name' must be a slug, found 'load panel'",
            ),
            (
                "steps:\n  - name: load\n    kind: verify\n    cmd: true\n",
                "has kind 'verify'",
            ),
            (
                "steps:\n  - name: load\n    cmd: true\n    deps: Code/load.jl\n",
                "'deps' must be a list",
            ),
            (
                "steps:\n  - name: load\n    cmd: true\n    outs: out/panel.parquet\n",
                "'outs' must be a list",
            ),
            (
                "steps:\n  - name: load\n    cmd: true\n"
                "    outs:\n      - checksum: out/panel.sha256\n",
                "'outs' entries are a path, or 'path:' with an optional 'sidecar:'",
            ),
            (
                "steps:\n  - name: load\n    cmd: true\n"
                "    params:\n      window: [1, 2]\n",
                "'params' must be a flat mapping",
            ),
        ],
    )
    def test_structural_step_errors(self, tmp_path, block, fragment):
        plan = _plan(tmp_path)
        _write_repro_task(plan / "01-a", "A", block)
        graph = _graph(plan)
        assert _has(graph, "error", fragment)
        assert graph.steps == []

    def test_runner_template_without_a_script_placeholder(self, tmp_path):
        plan = _plan(tmp_path)
        (plan / "config.yaml").write_text(
            "reproduction:\n  runners:\n    julia: julia --project=.\n", encoding="utf-8"
        )
        _write_repro_task(
            plan / "01-a",
            "A",
            "steps:\n  - name: load\n    runner: julia\n    script: Code/run.jl\n",
        )
        graph = _graph(plan)
        assert _has(graph, "error", "runner template 'julia' must contain '{script}'")
        assert graph.steps == []

    def test_env_deps_unknown_variable_is_a_config_error(self, tmp_path):
        plan = _plan(tmp_path)
        (plan / "config.yaml").write_text(
            'reproduction:\n  env_deps:\n    - "${MISSING}/env.lock"\n', encoding="utf-8"
        )
        _write_repro_task(
            plan / "01-a", "A", "steps:\n  - name: load\n    cmd: true\n"
        )
        assert _has(_graph(plan), "error", "references unknown variable ${MISSING}")

    def test_dep_that_is_neither_produced_nor_on_disk(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(
            plan / "01-a",
            "A",
            "steps:\n  - name: load\n    cmd: true\n    deps: [data/absent.csv]\n",
        )
        graph = _graph(plan)
        assert _has(graph, "warning", "which no step produces and which is not on disk")
        assert graph.external_inputs[0].exists is False

    def test_derived_edge_contradicting_sibling_depends_on(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(
            plan / "01-build",
            "Build",
            "steps:\n"
            "  - name: build\n"
            "    cmd: sh build.sh\n"
            "    outs: [output/panel.parquet]\n",
            depends_on=["02-estimate"],
        )
        _write_repro_task(
            plan / "02-estimate",
            "Estimate",
            "steps:\n"
            "  - name: estimate\n"
            "    cmd: sh estimate.sh\n"
            "    deps: [output/panel.parquet]\n"
            "    outs: [output/table.tex]\n",
        )
        assert _has(
            _graph(plan),
            "error",
            "dependency cycle",
        )

    def test_consistent_depends_on_raises_nothing(self, tmp_path):
        assert _messages(_graph(_two_task_pipeline(tmp_path)), "warning") == []

    def test_include_warnings_are_attributed_to_the_owning_task(self, tmp_path):
        plan = _plan(tmp_path)
        code = tmp_path / "Code"
        code.mkdir()
        (code / "run.jl").write_text('include("gone.jl")\n', encoding="utf-8")
        _write_repro_task(
            plan / "01-a",
            "A",
            "steps:\n"
            "  - name: load\n"
            "    cmd: julia Code/run.jl\n"
            "    deps: [Code/run.jl]\n"
            "    outs: [out/x.csv]\n",
        )
        graph = _graph(plan)
        warning = next(f for f in graph.findings if f.severity == "warning")
        assert warning.task_path == "01-a"
        assert warning.category == "reproduction"
        assert "does not exist" in warning.message

    def test_findings_use_the_task_check_finding_shape(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(plan / "01-a", "A", "level: high\nsteps: []\n")
        finding = check_reproduction(plan)[0]
        assert finding.to_dict().keys() == {
            "task_path",
            "category",
            "severity",
            "message",
        }
        assert finding.to_text().startswith("[ERROR] [reproduction] 01-a:")

    def test_one_broken_task_does_not_hide_the_rest(self, tmp_path):
        plan = _plan(tmp_path)
        _write_repro_task(plan / "01-broken", "Broken", "steps:\n  - name: a\n    cmd: |\n      x\n")
        _write_repro_task(plan / "02-good", "Good", "steps:\n  - name: b\n    cmd: true\n")
        graph = _graph(plan)
        assert [s.name for s in graph.steps] == ["b"]
        assert _has(graph, "error", "literal block scalars")
