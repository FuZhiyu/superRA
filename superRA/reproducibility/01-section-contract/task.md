---
title: "Define the `## Reproduction` Section Contract and Graph Model"
status: implemented
depends_on: []
---

## Objective

Specify the `## Reproduction` section and ship the shared library that turns a task tree into a validated reproduction graph. Every later task (runner, task interface, dashboard, hook, skill) consumes this library and this contract; neither runs pytask.

- **Contract** lands in [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) as a new body section: the section body is exactly one fenced `yaml` block; prose outside the fence is a contract violation. Top-level keys: `tier` (`canon` | `local`, default `local`) and `steps` (list). Project-wide config is the `reproduction:` key of `superRA/config.yaml`, a new project-config file whose top-level keys are namespaced by concern so other configuration can move there later; the contract documents both.
- **Bounded YAML subset**, pinned in the contract and parsed by a stdlib parser in the core: block mappings and block lists, inline lists of scalars, plain and quoted scalars, comments; no anchors, tags, multi-line scalars, or inline mappings. Per-out sidecar tracking is therefore a nested block item (`- path: …` / `sidecar: …`). `pyyaml`, when present, parses the same text identically.
- **Step keys:** `name` (slug, unique across the tree), `cmd` (shell string run from the project root) or `runner` + `script` (expands a runner template from config), `deps` (files or directories read, the script included), `outs` (files or directories written; a directory means every file inside), optional `kind: check` (no `outs`; reruns when deps change), optional `params` (flat mapping hashed into the step state).
- **Config keys:** `vars` (each a literal, `env: NAME`, or `shell: "…"`, evaluated once per invocation), `runners` (name → command template with `{script}`), `env_deps` (paths added to every step's deps in the subtree), `code_roots` (directories the reminder hook watches). `${VAR}` interpolation applies to `cmd`, `deps`, `outs`, and `script`; every node keeps its logical (variable-form) path as its id alongside the resolved path.
- **Graph model** (`skills/task-tree/scripts/_repro.py`): parse every task's section; resolve config and variables; expand each `.jl` dep to its transitive `include("…")` closure (string-literal paths relative to the including file, `@__DIR__` resolved to that directory; unresolvable includes are warnings); infer step edges by matching `outs` to `deps`; classify deps no step produces as external inputs; derive task-level edges (task B depends on task A when any B step reads any A step output). Expose the graph as plain dataclasses plus a JSON serialization the CLI and dashboard reuse.
- **Validation** returns findings in the `task check` `Finding` shape: `[ERROR]` duplicate step names, two steps declaring the same out, a `check` step with outs, prose outside the fence, YAML outside the subset in a section or in `config.yaml`, an unknown variable; `[WARNING]` a dep that neither exists on disk nor is produced, a derived task edge that contradicts sibling `depends_on` order. Never-built outs are runner state (`missing` in `repro status`), not a check finding, so a fresh clone checks clean.
- **Validation criteria:** unit tests under `skills/task-tree/scripts/` cover the subset parser (accepted forms, and rejection of every excluded form), variable sources and scoping, include-closure extraction on a fixture with nested includes, edge inference including directory outs, external-input classification, every finding above, and byte-identical results from the stdlib parser and `pyyaml` on the fixture sections.

## Details

- The fence-aware section splitter is [`parse_body_sections`](../../../skills/task-tree/scripts/_task_io.py#L326); `Task` objects already carry the parsed body, and [task_check.py](../../../skills/task-tree/scripts/task_check.py) shows the `Finding` shape and the `--category` convention (add `reproduction`).
- The stdlib subset parser serves every read path; `pyyaml` is optional and, when importable, only cross-checks the subset parser in tests.
- Include-closure extractor: TreasuryGIV's `Code/run_estimates.jl` resolves to 16 transitive helpers with a ~30-line regex extractor; `include(joinpath(@__DIR__, "x.jl"))` is common there, so resolve `@__DIR__` as the including file's directory.
- Sidecar semantics: the runner hashes the sidecar instead of the out; the contract must say the trade-off (a hand-edited out goes unnoticed).
- `${OUT}` in TreasuryGIV must equal the routing in `Code/output_paths.jl`: `output/` when `TREASURYGIV_WRITE_CANONICAL` is set, else `output/sandbox/<email-local-part>/<branch>/`; a `shell:` var covers it without duplicating the slug rules.
- The frontmatter parser in `_task_io.py` (`_parse_yaml_value`, `_parse_yaml_list_continuation`) is the existing stdlib subset precedent; the comment sidecar chose JSON for the same reason ([_comments.py:179](../../../skills/task-tree/scripts/_comments.py#L179)). The section stays YAML because humans write and comment on it; the subset keeps the parser bounded.

## Results

The reproduction graph library and its contract are in place; [02-runner](../02-runner/task.md) through [06-skill](../06-skill/task.md) can build on them without re-reading a task file.

### What later tasks call

[`_repro.py`](../../../skills/task-tree/scripts/_repro.py) is stdlib-only and never executes a build.

- `build_graph(plan_root, *, project_root, root, env, shell_runner)` returns a `Graph` of `Step` / `Out` / `PathRef` / `ExternalInput` dataclasses plus `findings`. It never raises: one malformed task costs its own steps and nothing else.
- `graph_to_dict(graph)` is the JSON shape the runner, `task read`, and the dashboard share.
- `check_reproduction(plan_root, root)` returns the same findings for the `task check` `reproduction` category ([03-task-interface](../03-task-interface/task.md) wires it); pass the already-walked `root` to avoid a second tree walk.
- `parse_yaml_subset` and `extract_repro_block` are separately callable, so the hook can read one section without building the tree.

`Finding` moved from [task_check.py](../../../skills/task-tree/scripts/task_check.py) to [_task_validate.py](../../../skills/task-tree/scripts/_task_validate.py) so both validators emit one shape and `task check` can import `_repro` without a cycle. `task_check` re-exports it; no call site changed.

### Three contract decisions the plan did not settle

- **A `${VAR}` path inside an inline list must be quoted.** PyYAML rejects `deps: [${OUT}/panel.parquet]` outright — `{` is a reserved flow indicator — so accepting it would have made the two parsers disagree on the very form agents write most. The subset parser rejects it with a message naming the quoted fix; block lists are unaffected.
- **Structural step errors are `[ERROR]` findings too.** Beyond the findings the objective lists, a missing or non-slug `name`, an unknown `kind`, a step declaring neither `cmd` nor `runner` + `script`, an unknown step or section key, an undefined runner, a runner template without `{script}`, a non-list `deps` or `outs`, a malformed `outs` entry, and a non-flat `params` all report rather than crash the walk. The contract's §Validation lists all of them, since that is where an agent looks a rejection message up.
- **`env_deps` are interpolated.** The objective scopes `${VAR}` to `cmd`, `deps`, `outs`, and `script`, and `env_deps` entries become deps of every step, so treating them as literal would have made `env_deps: ["${SCRATCH}/env.lock"]` a dep on a path that cannot exist. An unknown variable there is one `[ERROR]` against `config.yaml` rather than one per step.

### The include closure resolves four forms, not one

The [08-pilot-treasurygiv](../08-pilot-treasurygiv/task.md) pilot found the first version blind on the idiom TreasuryGIV actually uses. Resolving only a string literal and `joinpath(@__DIR__, …)` left 56 of the pilot's 57 findings as unresolved-include warnings, because DrWatson projects write `include(projectdir("Code", "helpers.jl"))` and tests write `include(joinpath(REPO_ROOT, "Code", "x.jl"))`. An unresolved include is not a cosmetic warning: it drops the helper from the step's deps, so a helper edit stops invalidating the step that reads it — the property the closure exists to provide.

`_include_target` now returns candidate `(anchor, path)` pairs and resolves, in addition to the two original forms, `projectdir("…")` / `srcdir` / `scriptsdir` against the project root, and `joinpath(<variable>, "…")` against the project root first and the including file second, keeping whichever candidate is on disk. Extraction also moved off the nested-parens regex onto a balanced-paren scan, so `include(joinpath(projectdir(), "Code", "io.jl"))` — two levels deep — is seen at all. Registering all 44 TreasuryGIV producers now leaves two warnings: `Base.include(mod, path)`, which is genuinely dynamic, and one derived task edge that contradicts a `depends_on` order.

### Validation

95 tests in [test_repro.py](../../../skills/task-tree/scripts/test_repro.py); suite at 1036 passed with pytask installed.

Coverage follows the objective's list, plus: the subset parser agrees with `pyyaml` byte-for-byte on three fixture sections (`json.dumps(..., sort_keys=True)` equality), scalar typing included — the parser reimplements PyYAML's YAML 1.1 resolvers for null, bool, int, and float. The two resolvers it drops, sexagesimals and timestamps, and the three forms it rejects that `pyyaml` accepts (an unpaired quote in a plain scalar, an escaped `\"`, an escape outside the supported set) are listed in the contract's §The YAML subset.

Contract prose is [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) §Reproduction Section, with the section listed in §Task Anatomy and both new modules in [internals.md](../../../skills/task-tree/references/internals.md) §Script Inventory.
