---
title: "Define the `## Reproduction` Section Contract and Graph Model"
status: not-started
depends_on: []
---

## Objective

Specify the `## Reproduction` section and ship the shared library that turns a task tree into a validated reproduction graph. Every later task (runner, task interface, dashboard, hook, skill) consumes this library and this contract; neither runs pytask.

- **Contract** lands in [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) as a new body section: the section body is exactly one fenced `yaml` block; prose outside the fence is a contract violation. Top-level keys: `tier` (`canon` | `local`, default `local`), `steps` (list), `config` (any task; governs its subtree).
- **Bounded YAML subset**, pinned in the contract and parsed by a stdlib parser in the core: block mappings and block lists, inline lists of scalars, plain and quoted scalars, comments; no anchors, tags, multi-line scalars, or inline mappings. Per-out sidecar tracking is therefore a nested block item (`- path: …` / `sidecar: …`). `pyyaml`, when present, parses the same text identically.
- **Step keys:** `name` (slug, unique across the tree), `cmd` (shell string run from the project root) or `runner` + `script` (expands a runner template from config), `deps` (files or directories read, the script included), `outs` (files or directories written; a directory means every file inside), optional `kind: check` (no `outs`; reruns when deps change), optional `params` (flat mapping hashed into the step state).
- **Config keys:** `vars` (each a literal, `env: NAME`, or `shell: "…"`, evaluated once per invocation), `runners` (name → command template with `{script}`), `env_deps` (paths added to every step's deps in the subtree), `code_roots` (directories the reminder hook watches). Config scopes to the declaring task's subtree; the nearest ancestor wins per key. `${VAR}` interpolation applies to `cmd`, `deps`, `outs`, and `script`; every node keeps its logical (variable-form) path as its id alongside the resolved path.
- **Graph model** (`skills/task-tree/scripts/_repro.py`): parse every task's section; resolve config and variables; expand each `.jl` dep to its transitive `include("…")` closure (string-literal paths relative to the including file, `@__DIR__` resolved to that directory; unresolvable includes are warnings); infer step edges by matching `outs` to `deps`; classify deps no step produces as external inputs; derive task-level edges (task B depends on task A when any B step reads any A step output). Expose the graph as plain dataclasses plus a JSON serialization the CLI and dashboard reuse.
- **Validation** returns findings in the `task check` `Finding` shape: `[ERROR]` duplicate step names, two steps declaring the same out, a `check` step with outs, prose outside the fence, YAML outside the subset, an unknown variable; `[WARNING]` a dep that neither exists on disk nor is produced, a derived task edge that contradicts sibling `depends_on` order; `[INFO]` a `canon` step whose outs are absent in this checkout (never built here).
- **Validation criteria:** unit tests under `skills/task-tree/scripts/` cover the subset parser (accepted forms, and rejection of every excluded form), variable sources and scoping, include-closure extraction on a fixture with nested includes, edge inference including directory outs, external-input classification, every finding above, and byte-identical results from the stdlib parser and `pyyaml` on the fixture sections.

## Details

- The fence-aware section splitter is [`parse_body_sections`](../../../skills/task-tree/scripts/_task_io.py#L326); `Task` objects already carry the parsed body, and [task_check.py](../../../skills/task-tree/scripts/task_check.py) shows the `Finding` shape and the `--category` convention (add `reproduction`).
- Keep the parser lazy on `pyyaml` like `task_comment.py`: import inside the function and fall back to a clear error under bare `python3` only for the mutation path; reads must not require it.
- Include-closure extractor: TreasuryGIV's `Code/run_estimates.jl` resolves to 16 transitive helpers with a ~30-line regex extractor; `include(joinpath(@__DIR__, "x.jl"))` is common there, so resolve `@__DIR__` as the including file's directory.
- Sidecar semantics: the runner hashes the sidecar instead of the out; the contract must say the trade-off (a hand-edited out goes unnoticed).
- `${OUT}` in TreasuryGIV must equal the routing in `Code/output_paths.jl`: `output/` when `TREASURYGIV_WRITE_CANONICAL` is set, else `output/sandbox/<email-local-part>/<branch>/`; a `shell:` var covers it without duplicating the slug rules.
- The frontmatter parser in `_task_io.py` (`_parse_yaml_value`, `_parse_yaml_list_continuation`) is the existing stdlib subset precedent; the comment sidecar chose JSON for the same reason ([_comments.py:179](../../../skills/task-tree/scripts/_comments.py#L179)). The section stays YAML because humans write and comment on it; the subset keeps the parser bounded.

## Results
