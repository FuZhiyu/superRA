---
title: "The `## Reproduction` Section Contract, Graph Library, and Effective Dependencies"
status: approved
depends_on: []
---

## Objective

Own the `## Reproduction` section contract and the stdlib library that turns a task tree into a validated reproduction graph, plus the effective dependency snapshot that task readiness, validation, and every task view read. The runner, task interface, dashboard, hook, and skill consume this library; none parses a section itself.

- **Contract** in [task-file-contract.md §Reproduction Section](../../../skills/task-tree/references/task-file-contract.md#reproduction-section): the section body is one fenced `yaml` block in a bounded subset a stdlib parser reads, and `pyyaml`, when present, parses identically. Step keys are `name`, `cmd` or `runner` + `script`, `deps`, `outs`, optional `kind: check` and `params`; project config (`vars`, `runners`, `env_deps`) lives under `reproduction:` in `superRA/config.yaml`. Every node keeps its logical `${VAR}` path as its id beside the resolved path.
- **Graph model** ([_repro.py](../../../skills/task-tree/scripts/_repro.py)): parse every section, resolve config and variables, expand each `.jl` dep to its `include` closure, infer step edges by matching `outs` to `deps` (directory outs by prefix), classify unproduced deps as external inputs, and report findings in the `task check` shape. One malformed task costs only its own steps.
- **Effective dependencies** ([_task_dependencies.py](../../../skills/task-tree/scripts/_task_dependencies.py)): readiness follows `depends_on` only, own or inherited; file edges between steps are reported as inputs and never gate. Parents may own steps beside child tasks; archived subtrees leave the active graph with warnings to their active consumers. Cycle errors cover step cycles and `depends_on` cycles only. A reproduction error blocks only the builds it touches, never planning commands. The [0.5 design](../attachments/v05-design.md#one-task-dag-combines-both-sources-of-dependency) records the decisions.

## Results

The library, the contract, and the dependency snapshot are in place, and every consumer reads one snapshot per command.

### What consumers call

- [`build_graph`](../../../skills/task-tree/scripts/_repro.py) returns a `Graph` of plain dataclasses plus `findings`, and never raises. `graph_to_dict` is the JSON the runner, `task read`, and the dashboard share; its `dependencies` block carries tasks, archived tasks, and the `depends_on` edges as `logical`.
- `check_reproduction(plan_root, root)` feeds the `task check` `reproduction` category; `parse_yaml_subset` and `extract_repro_block` read one section without building the tree.
- `step_errors` decides which reproduction errors touch a selection: an error on a selected step's own task or a target's subtree, a step cycle through a selected step, or project-wide configuration.
- [Preflight](../../../skills/task-tree/scripts/_task_snapshot.py) builds the current and edited trees without resolving variables and refuses only a new `depends_on` error. `task create`, `move`, `dep add`, and archive transitions print each task they take off the frontier and each new dependency warning.
- Mechanics are documented in [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md#effective-dependencies), [commands.md §Manage dependencies](../../../skills/task-tree/references/commands.md#manage-dependencies), and [internals.md §Effective dependency snapshot](../../../skills/task-tree/references/internals.md#effective-dependency-snapshot).

### Contract decisions

- **A `${VAR}` path inside an inline list must be quoted.** PyYAML rejects `deps: [${OUT}/x]` because `{` is a flow indicator, so the subset parser rejects it too, naming the quoted fix.
- **Structural step errors are `[ERROR]` findings**, not crashes: a missing or non-slug `name`, an unknown key or `kind`, no command, an undefined runner, and malformed `deps`, `outs`, or `params`. The contract's §Validation lists them.
- **`env_deps` entries are interpolated**, so `${SCRATCH}/env.lock` is a real path; an unknown variable there is one error against `config.yaml`.
- **Retired keys warn and are ignored.** A leftover `tier:` in a section or step, or `env_probe` / `code_roots` under `reproduction:`, is a `[WARNING]`. None entered a step's hash, so upgrading a pre-release project reruns nothing.
- **A `depends_on` that runs against the file flow is a warning**, not an error; a loop that appears only when file edges are grouped by task is neither.

### The include closure resolves the idioms projects use

The [TreasuryGIV pilot](../08-pilot-treasurygiv/task.md) found the first resolver blind to DrWatson-style includes: 56 of its 57 findings were unresolved includes, each dropping a helper from its step's deps so helper edits stopped invalidating the step. The resolver now handles string literals, `joinpath(@__DIR__, …)`, `projectdir` / `srcdir` / `scriptsdir`, and `joinpath(<variable>, …)` with a balanced-paren scan; `Base.include(mod, path)` stays a warning because it is genuinely dynamic. Details: [internals.md §Julia include closure](../../../skills/task-tree/references/internals.md#julia-include-closure).

### Known limits

- Python imports are not tracked; only the Julia `include` closure extends a step's deps.
- A build blocked by an archived producer's missing file lists it as `not on disk, and no step produces it` without naming the producer; `task read` and the frontier name it.

Tests: [test_repro.py](../../../skills/task-tree/scripts/test_repro.py) (parser, variables, closure, findings, and `pyyaml` agreement) and [test_task_dependencies.py](../../../skills/task-tree/scripts/test_task_dependencies.py) (readiness, cycles, archived producers, preflight, and parent-owned steps).
