---
title: "Define the `## Reproduction` Section Contract and Graph Model"
status: not-started
depends_on: []
---

## Objective

Specify the `## Reproduction` section and ship the shared library that turns a task tree into a validated reproduction graph. Every later task (runner, task interface, dashboard, hook, skill) consumes this library and this contract; neither runs pytask.

- **Contract** lands in [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) as a new body section: the section body is exactly one fenced `yaml` block; prose outside the fence is a contract violation. Top-level keys: `tier` (`canon` | `task`, default `task`), `steps` (list), and, in the root `superRA/task.md` only, `config`.
- **Step keys:** `name` (slug, unique across the tree), `cmd` (shell string run from the project root) or `runner` + `script` (expands a runner template from config), `deps` (files or directories read, the script included), `outs` (files or directories written; a directory means every file inside), optional `kind: check` (no `outs`; reruns when deps change), optional `params` (mapping hashed into the step state), and per-out sidecar tracking as `{path: …, sidecar: …}`.
- **Config keys** (root task only): `vars` (each literal, `{env: NAME}`, or `{shell: "…"}` evaluated once per invocation), `runners` (name → command template with `{script}`), `env_deps` (paths added to every step's deps), `code_roots` (directories the reminder hook watches). `${VAR}` interpolation applies to `cmd`, `deps`, `outs`, and `script`.
- **Graph model** (`skills/task-tree/scripts/_repro.py`): parse every task's section; resolve variables; expand each `.jl` dep to its transitive `include("…")` closure (string-literal paths relative to the including file; unresolvable includes are warnings); infer step edges by matching `outs` to `deps`; classify deps no step produces as external inputs; derive task-level edges (task B depends on task A when any B step reads any A step output). Expose the graph as plain dataclasses plus a JSON serialization the CLI and dashboard reuse.
- **Validation** returns findings in the `task check` `Finding` shape: duplicate step names; two steps declaring the same out; a dep that neither exists on disk nor is produced; a `canon` task with a step whose outs are absent (never built); a `check` step with outs; a derived task edge that contradicts sibling `depends_on` order (warning); prose outside the fence; a non-root task carrying `config`.
- **Validation criteria:** unit tests under `skills/task-tree/scripts/` cover parsing, variable sources, include-closure extraction on a fixture with nested includes, edge inference including directory outs, external-input classification, every finding above, and a stdlib-only (no `pyyaml`) parse of a well-formed section.

## Details

- The fence-aware section splitter is [`parse_body_sections`](../../../skills/task-tree/scripts/_task_io.py#L326); `Task` objects already carry the parsed body, and [task_check.py](../../../skills/task-tree/scripts/task_check.py) shows the `Finding` shape and the `--category` convention (add `reproduction`).
- Keep the parser lazy on `pyyaml` like `task_comment.py`: import inside the function and fall back to a clear error under bare `python3` only for the mutation path; reads must not require it.
- Include-closure extractor: TreasuryGIV's `Code/run_estimates.jl` resolves to 16 transitive helpers with a ~30-line regex extractor; `include(joinpath(@__DIR__, "x.jl"))` is common there, so resolve `@__DIR__` as the including file's directory.
- Sidecar semantics: the runner hashes the sidecar instead of the out; the contract must say the trade-off (a hand-edited out goes unnoticed).
- `${OUT}` in TreasuryGIV must equal the routing in `Code/output_paths.jl`: `output/` when `TREASURYGIV_WRITE_CANONICAL` is set, else `output/sandbox/<email-local-part>/<branch>/`; a `{shell: …}` var covers it without duplicating the slug rules.

## Results
