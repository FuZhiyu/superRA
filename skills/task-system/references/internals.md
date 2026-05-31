# Task System Internals

Load this reference when modifying the task-system skill itself — scripts, data layer, hooks, or migration logic.

## Data Layer: `_task_io.py`

All scripts share `_task_io.py` as the data layer. It provides:

### Task dataclass

```python
@dataclass
class Task:
    path: str           # relative path from plan root (empty string for root)
    dir_path: Path      # absolute path to the task directory
    title: str
    status: str         # not-started | in-progress | implemented | revise | approved | archived
    depends_on: list[str]
    tags: list[str]
    script: str
    input: list[str]
    output: list[str]
    created: str
    updated: str
    body: str           # full body text after frontmatter
    objective: str      # extracted from ## Objective
    results: str        # extracted from ## Results
    decisions: str      # extracted from ## Decisions (legacy)
    revision_notes: str # extracted from ## Revision Notes
    review_notes: str   # extracted from ## Review Notes
    children: list[Task]
```

Key properties:
- `is_leaf` — True when `children` is empty
- `is_root` — True when `path` is empty
- `slug` — last component of `path`
- `effective_status()` — returns own status for leaves, rolled-up status for branches

### Core functions

| Function | Purpose |
|---|---|
| `parse_frontmatter(text)` | Parse YAML frontmatter and body from task.md text. Returns `(dict, body_str)`. |
| `parse_body_sections(body)` | Split body on `## ` headers into `{section_name: content}`. |
| `serialize_frontmatter(fm)` | Serialize frontmatter dict back to YAML (without `---` delimiters). Field order is fixed. |
| `parse_task(path)` | Parse a `task.md` file into a `Task` object. Validates status enums. |
| `write_task(task)` | Write a `Task` back to disk, preserving body content. |
| `walk_plan(plan_root)` | Recursively walk plan directory, return root `Task` with populated children. |
| `resolve_path(plan_root, task_path)` | Resolve a relative task path to its directory. Rejects paths that escape the root. |
| `compute_status(task)` | Roll up status from children: all approved -> approved; any revise -> revise; any in-progress/implemented -> in-progress; else not-started. |
| `compute_frontier(root)` | Return leaf tasks ready for dispatch — status is not-started/in-progress and all sibling deps are approved. |
| `collect_all_tasks(root)` | Flatten the tree depth-first (excluding root). |
| `validate_frontmatter(task)` | Validate status enums, title non-empty, list types. Returns list of warning strings. |
| `validate_dependencies(task, siblings)` | Check that all `depends_on` entries reference existing sibling directory names. |
| `detect_cycles(tasks)` | DFS-based cycle detection among sibling tasks. Returns cycle description strings. |
| `validate_plan(plan_root)` | Walk the entire plan tree, run all validations at each level. Returns aggregated prefixed warnings. |

### Enum constants

```python
VALID_STATUSES = ("not-started", "in-progress", "implemented", "revise", "approved", "archived")
```

### Child ordering

`_walk_children` sorts children **topologically** by `depends_on` using a Kahn's algorithm implementation (`_topological_sort`). This means the tree traversal order respects the dependency DAG, with alphabetical tie-breaking. If cycles are detected, the remaining tasks fall back to alphabetical order.

### YAML parsing

The frontmatter parser handles:
- Scalar values (plain and quoted)
- Inline lists: `[a, b, c]`
- Multi-line lists with `  - item` continuation lines
- Tilde (`~`) as null

It does not use a YAML library — the parser is minimal and purpose-built.

## Hook Architecture

`task_hook.py` is the task system's PostToolUse hook, wired in `hooks/hooks.json` under two matchers:

- **`Edit|Write`** — fires when a `task.md` is edited directly, reconciling from the edited file's plan root.
- **`Bash`** — fires when a shell command both references `.plan` and contains a filesystem-mutating verb (`mv`, `git mv`, `rm`, `rmdir`, `cp`, `mkdir`), so a plain `mv` reorganization of the tree stays validated. Read-only `.plan` commands (`task_query.py`, `grep .plan`, `.plan/serve`) fail the verb test and early-exit.

On a match the hook runs the same best-effort reconcile — `validate_plan` (warnings to stderr), `propagate_parent_status`, `generate_dashboard` — each in its own try/except, never blocking, always exit 0. See `task_hook.py` for the gating regexes and plan-root discovery, and `hooks/hooks.json` for the wiring.

Frontmatter validation also happens inside `parse_task()` at parse time, independent of the hook — invalid enum values raise `ValueError`. The mutation scripts (`task_create`, `task_update`, `task_add_result`, `task_link`, `task_rename`) still rebuild the dashboard themselves after their mutation, so the dashboard stays current whether a task is changed by direct edit, by `mv`, or through a CLI.

The Codex and Cursor hook configs (`hooks/hooks-codex.json`, `hooks/hooks-cursor.json`) do not wire `task_hook.py` at all; task-validation parity for those harnesses is unimplemented.

## Migration: `plan_migrate.py`

### From legacy PLAN.md + RESULTS.md to .plan/

```bash
python3 <skill-dir>/scripts/plan_migrate.py \
  --plan-md PLAN.md --results-md RESULTS.md --output .plan
```

The migrator:
1. Parses `PLAN.md` task blocks (delimited by `### Task N:` headings)
2. Extracts frontmatter fields from task-block metadata (status, review notes, steps)
3. Matches `RESULTS.md` sections to tasks by heading
4. Creates the directory hierarchy with `task.md` files
5. Generates the initial dashboard

### Parser Expectations and Preparation

The migration script uses strict regex patterns. Non-conforming PLAN.md files must be normalized before migration or migrated manually.

**Task block detection** — `TASK_BLOCK_RE`:

```
^###\s+Task\s+(\d+):\s+(.+?)$
```

Only `###`-level headings with the exact `Task N: Title` pattern are recognized. Tasks at `##` or `####`, unnumbered tasks, or tasks without the colon separator are invisible to the parser.

**Results section detection** — `RESULTS_SECTION_RE`:

```
^##\s+Task\s+(\d+):\s+(.+?)$
```

Matches `## Task N: Title` headings in RESULTS.md. Task numbers must correspond to those in PLAN.md. Sections whose first line contains "Not started" are skipped.

**Field extraction** — `FIELD_RE` dictionary of patterns, each matching a bold-label line:

| Field | Pattern | Notes |
|---|---|---|
| `depends_on` | `**Depends on:** <value>` | Comma-separated `Task N` refs or `*(none)*` |
| `review_status` | `**Review status:** <value>` | Legacy source field; normalized to lowercase and mapped to unified `status` |
| `integration_status` | `**Integration status:** <value>` | Legacy source field; same normalization and mapping |
| `script` | `**Script:** <value>` | Optional backtick wrapper stripped |
| `input` | `**Input:** <value>` | Backtick-delimited list or comma-separated |
| `output` | `**Output:** <value>` | Same as input |

Missing fields default to empty/none. The `_extract_file_list` helper recognizes `*(none)*` as empty list, backtick-delimited items (`` `a`, `b` ``), or plain comma-separated values.

**Status inference** — `_compute_status_from_steps`:

The migrator maps the legacy `(status, review_status, integration_status)` triple to a single `status` field:

1. If `integration_status` is set and non-`~` → use as `status` (most recent lifecycle event)
2. Else if `review_status` is set and non-`~` → use as `status`
3. Else infer from checkboxes: `- [xX]` (checked) and `- [ ]` (unchecked, exactly one space). All checked + none unchecked → `implemented`; mixed → `in-progress`; none checked → `not-started`

Checkbox variants like `- [~]`, `- [-]`, or `- [X ]` (with extra space) are not matched by either pattern and are effectively invisible — leading to incorrect status inference.

**Dependency resolution** — `_parse_depends_on` splits on commas, then `migrate` matches each `Task N` reference to the corresponding slug via `task_num_to_slug`. Unresolved references (e.g. `Task 5` when only Tasks 1–4 exist) are silently dropped.

**Header extraction** — everything before the first `### Task N:` heading becomes the root task's body.

**Slugification** — `slugify()` lowercases, strips non-word characters, replaces whitespace/underscores with hyphens, and truncates to 60 characters. Directory names are `NN-slug` (zero-padded task number prefix).

**Normalization vs manual migration:** When the PLAN.md structure diverges significantly (no numbered task headings, deeply nested prose, ≤3 tasks), manual migration using `task_create.py` is faster than reformatting the file to match parser expectations. See `SKILL.md` §Preparing a PLAN.md for migration for the normalization checklist and manual procedure.

### Upgrade from v1 to v2 format

```bash
python3 <skill-dir>/scripts/plan_migrate.py --upgrade --plan-root .plan
```

Converts `## Steps` (checkboxes) to `## Objective` (prose), removes redundant `# Title` headings. Idempotent — safe to run multiple times.

## Dashboard: `plan_dashboard.py`

The dashboard is a live-updating server (FastAPI + SSE), not a static HTML file. The primary launch method is `bash .plan/serve`; agents use `uv run <skill-dir>/scripts/plan_dashboard.py serve --root .plan/`. The static `generate` subcommand is deprecated.

For CLI usage, view options, and `.plan/serve` details, see `SKILL.md` §Dashboard — that section is authoritative.

**Auto-rebuild.** Mutation scripts (`task_create`, `task_update`, `task_add_result`, `task_link`, `task_rename`) trigger dashboard regeneration after completing their mutation. The SSE-based live server also watches for file changes and pushes updates to connected browsers.

## Script Inventory

| Script | Purpose |
|---|---|
| `_task_io.py` | Shared data layer (not invoked directly) |
| `task_read.py` | Context-aware task reading with ancestor chain and dependency status |
| `task_create.py` | Create a new task directory with template `task.md` |
| `task_update.py` | Update frontmatter fields on an existing task |
| `task_add_result.py` | Append a finding to a task's `## Results` section |
| `task_query.py` | Query the tree: `--tree`, `--frontier`, `--dag`, `--json` |
| `task_link.py` | Add or remove sibling dependencies |
| `task_rename.py` | Rename a task directory (cascades to sibling `depends_on`) |
| `plan_migrate.py` | Migrate from legacy PLAN.md/RESULTS.md or upgrade v1 -> v2 |
| `plan_dashboard.py` | Live dashboard server (`serve`) and static generation (`generate`, deprecated) |
| `test_task_system.py` | Test suite for `_task_io.py` |
