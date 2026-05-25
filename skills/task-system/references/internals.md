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
    status: str         # not-started | in-progress | implemented | revise | approved
    review_status: str  # ~ | implemented | revise | approved
    integration_status: str
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
VALID_STATUSES = ("not-started", "in-progress", "implemented", "revise", "approved")
VALID_REVIEW_STATUSES = ("~", "implemented", "revise", "approved")
VALID_INTEGRATION_STATUSES = ("~", "implemented", "revise", "approved")
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

The task system does not currently ship its own hooks. Frontmatter validation happens inside `parse_task()` at parse time — invalid enum values raise `ValueError`.

The dashboard is regenerated automatically by mutation scripts (`task_create`, `task_update`, `task_add_result`, `task_link`, `task_rename`) — each calls `plan_dashboard.py` after completing its mutation.

Hook integration points for future development:
- **PostToolUse on Edit/Write** — validate frontmatter when `task.md` is edited directly (currently not wired)
- **PostToolUse on Edit/Write** — auto-regenerate dashboard after direct edits (currently only mutation scripts trigger this)

The plugin hook configuration lives in `hooks/hooks.json` (Claude Code) and `hooks/hooks-codex.json` (Codex). See those files for the hook wiring format.

## Migration: `plan_migrate.py`

### From PLAN.md + RESULTS.md to .plan/

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

### Upgrade from v1 to v2 format

```bash
python3 <skill-dir>/scripts/plan_migrate.py --upgrade --plan-root .plan
```

Converts `## Steps` (checkboxes) to `## Objective` (prose), removes redundant `# Title` headings. Idempotent — safe to run multiple times.

## Dashboard Generation: `plan_dashboard.py`

```bash
python3 <skill-dir>/scripts/plan_dashboard.py --plan-root .plan
```

Generates `.plan/dashboard.html` — a single-file HTML page with:
- **Tree view** — hierarchical task display with status badges
- **DAG view** — dependency graph rendered with Mermaid
- **Kanban view** — tasks grouped by status column

The dashboard requires internet access for full rendering (loads Mermaid and CSS from CDN). It is regenerated automatically after mutation commands.

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
| `plan_migrate.py` | Migrate from PLAN.md/RESULTS.md or upgrade v1 -> v2 |
| `plan_dashboard.py` | Generate the HTML dashboard |
| `test_task_system.py` | Test suite for `_task_io.py` |
