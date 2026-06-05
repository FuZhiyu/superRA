# Task System Internals

Load this reference when modifying the task-system skill itself — scripts, data layer, hooks, or migration logic.

## Setup: the `superra` CLI

The scripts here are packaged as `superra-task-system` (`pyproject.toml` in the skill directory), exposing one `superra` console entry point (`[project.scripts]` → `superra_task_system.cli:main`).

Install it as a standalone command on PATH:

```bash
uv tool install ./skills/task-system           # installs the `superra` executable (~/.local/bin/superra)
uv tool install --force ./skills/task-system   # reinstall to pick up source edits
uv tool uninstall superra-task-system          # remove
```

`uv tool install` installs a snapshot, so while iterating on the source, skip the install and run from the live checkout instead — see `CLAUDE.md §Local Task-System CLI Development` (the `uv run --project skills/task-system superra …` form), which always uses the edited source.

## Data Layer: `_task_io.py`

All scripts share `_task_io.py` as the data layer. It provides:

### Task dataclass

```python
@dataclass
class Task:
    path: str           # relative path from plan root (empty string for root)
    dir_path: Path      # absolute path to the task directory
    title: str
    status: str         # not-started | in-progress | implemented | revise | approved | archived | postponed
    depends_on: list[str]
    tags: list[str]
    script: str
    input: list[str]
    output: list[str]
    created: str
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
| `parse_body_sections(body)` | Split body on `## ` headers into `{section_name: content}`. Fence-aware: `## ` lines inside a ``` ``` ``` / `~~~` block are body content, not headers. |
| `serialize_frontmatter(fm)` | Serialize frontmatter dict back to YAML (without `---` delimiters). Field order is fixed. |
| `parse_task(path)` | Parse a `task.md` file into a `Task` object. Tolerates an unknown status (warns, preserves raw value); strict status validation lives in `task check`. |
| `write_task(task)` | Write a `Task` back to disk, preserving body content. |
| `walk_plan(plan_root)` | Recursively walk plan directory, return root `Task` with populated children. |
| `resolve_path(plan_root, task_path)` | Resolve a relative task path to its directory. Rejects paths that escape the root. |
| `compute_status(task)` | Roll up status from children, excluding parked (`archived` / `postponed`) children from the active set: all (active) approved -> approved; any revise -> revise; any in-progress/implemented -> in-progress; else not-started. When *every* child is parked the branch rolls up to `postponed` if any child is `postponed`, else `archived`. |
| `compute_frontier(root)` | Return leaf tasks ready for dispatch — status is not-started/in-progress and all sibling deps are approved. |
| `collect_all_tasks(root)` | Flatten the tree depth-first (excluding root). |
| `validate_frontmatter(task)` | Validate status enums, title non-empty, list types. Returns list of warning strings. |
| `validate_dependencies(task, siblings)` | Check that all `depends_on` entries reference existing sibling directory names. |
| `detect_cycles(tasks)` | DFS-based cycle detection among sibling tasks. Returns cycle description strings. |
| `validate_plan(plan_root)` | Walk the entire plan tree, run all validations at each level. Returns aggregated prefixed warnings. |

### Enum constants

```python
VALID_STATUSES = ("not-started", "in-progress", "implemented", "revise", "approved", "archived", "postponed")
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

`task_hook.py` is the task system's PostToolUse hook, wired in `hooks/hooks.json` and `hooks/hooks-codex.json` under two matcher groups:

- **`Edit|Write` / `apply_patch`** — fires when a `task.md` is edited directly, reconciling from the edited file's plan root. Codex's `Edit|Write` matcher covers `apply_patch`, and `task_hook.py` also accepts `tool_name: "apply_patch"` payloads.
- **`Bash`** — fires when a shell command both references `superRA` or `.plan` and contains a filesystem-mutating verb (`mv`, `git mv`, `rm`, `rmdir`, `cp`, `mkdir`), so a plain `mv` reorganization of the tree stays validated. Read-only task-tree commands (`superra task tree`, `grep superRA`) fail the verb test and early-exit.

On a match the hook runs the same best-effort reconcile — `validate_plan`, `propagate_parent_status`, `generate_dashboard` — each in its own try/except, never blocking, always exit 0. Validation warnings and non-fatal reconcile failures are collected into a PostToolUse JSON payload with both top-level `additionalContext` and Claude-style `hookSpecificOutput.additionalContext`, emitted on stdout only when there is feedback for the agent; valid edits and ignored fast paths stay silent. See `task_hook.py` for the gating regexes and plan-root discovery, and `hooks/hooks.json` / `hooks/hooks-codex.json` for the wiring.

`parse_task()` is lenient at parse time: an invalid status enum is **warned** (via `warnings.warn`) and the raw value is preserved, so a single malformed `task.md` never crashes a reader's tree walk (dashboard, `task query`, `task read`). Strict status validation is owned by `task check` (`check_status_validity`), which reports an invalid enum as an `[ERROR]` finding. The mutation scripts (`task_create`, `task_update`, `task_add_result`, `task_link`, `task_rename`) still rebuild the dashboard themselves after their mutation, so the dashboard stays current whether a task is changed by direct edit, by `mv`, or through a CLI.

Codex shell interception remains incomplete, so Codex `Bash` coverage is best-effort reconcile support rather than a complete enforcement boundary. Cursor does not wire `task_hook.py`.

## Migration: `plan_migrate.py`

### From legacy PLAN.md + RESULTS.md to superRA/

```bash
superra task migrate from-plan \
  --plan-md PLAN.md --results-md RESULTS.md --output superRA
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

### Preparing a legacy PLAN.md for migration

Before running the migrator, verify compatibility.

**Quick check — does the script see your tasks?**

```bash
grep -c '^### Task [0-9]*:' PLAN.md
```

If the count does not match the number of tasks in the file, the PLAN.md needs normalization or manual migration.

**Normalization checklist** (for files that diverge from the parser expectations above):

1. Renumber task headings to `### Task 1: Title`, `### Task 2: Title`, etc.
2. Fix heading levels — tasks must be `###` (not `##` or `####`).
3. Add missing metadata fields with safe defaults: `**Depends on:** *(none)*`, `**Script:** *(none)*`.
4. Standardize checkboxes to `- [x]` (done) or `- [ ]` (not done) — markers like `[~]` or `[-]` are not recognized.
5. If RESULTS.md exists, ensure headings match: `## Task N: Title` with the same numbering.

**Normalization vs manual migration:** When the PLAN.md structure diverges significantly (no numbered task headings, deeply nested prose, ≤3 tasks), manual migration is faster than reformatting the file to match parser expectations:

1. Create `superRA/` and its root `task.md` (or use `superra task create` for children).
2. For each logical task, create a child directory and write `task.md` directly — see `SKILL.md §Task File Format` for the template.
3. Run `superra dashboard --root superRA` to launch the dashboard.

### Upgrade from v1 to v2 format

```bash
superra task migrate upgrade --root superRA
```

Converts `## Steps` (checkboxes) to `## Objective` (prose), removes redundant `# Title` headings. Idempotent — safe to run multiple times.

## Dashboard: `plan_dashboard.py`

The dashboard is a live-updating server (FastAPI + SSE), not a static HTML file.

```bash
superra dashboard --root superRA                                     # installed package
uv run --project skills/task-system superra dashboard --root superRA  # local checkout
superra dashboard --foreground --root superRA                         # block in this terminal
superra dashboard stop --root superRA                                 # stop the background server
```

Task trees no longer carry a committed `serve` launcher script; the packaged `superra dashboard` command resolves `plan_dashboard.py` itself. Use the `uv run --project skills/task-system` form against a local checkout so edits are picked up from the live source, and the installed `superra dashboard` form for installed plugin/package sources.

**Lifecycle.** `superra dashboard` is fire-and-forget: it launches the server detached in the background, waits for it to bind, prints the URL + PID + log path, and returns the terminal. A second launch for the same repo reuses the running server (opens a tab, does not spawn a duplicate) rather than starting a second. The server self-exits after 5 continuous minutes with zero open tabs (a live `/events` SSE connection is one open tab, summed across all worktrees; periodic heartbeats prune connections dropped by sleep/network loss), so a detached server always self-cleans within the idle window. `--foreground` runs it blocking in the current terminal with logs on stdout (it also self-exits on idle); `superra dashboard stop` terminates the background server (a clean no-op when nothing is running). The PID and log files (`superra-dashboard.pid` / `.log`) live under the git common dir alongside the port key, so they are repo-scoped and shared across the repo's worktrees.

The server provides SSE hot-reload — it auto-updates when the task files of the worktree you are viewing change. Port is derived deterministically from the repository's git common directory (range 8100–8999; the plan-root path is the fallback when there is no git), so all of a repository's worktrees map to one shared server rather than each running its own. That single server resolves any of the repo's worktrees on demand per request: the active worktree is carried in the browser URL as `?wt=<worktree-basename>` (absent means the worktree the server was launched in), and switching worktrees via the selector is in-page navigation, not a server-wide switch — so two tabs can view different worktrees on the same port without interfering. Use `--port N` to override. The static `generate` subcommand is deprecated — use the live `superra dashboard`, or `superra dashboard export --output dashboard.html` for a one-off static file.

### GitHub Actions artifact sharing

Install the managed artifact workflow from the repository root:

```bash
superra dashboard artifact setup
```

The command writes `.github/workflows/superra-dashboard-artifact.yml` and refuses to overwrite a non-superRA-managed workflow unless `--force` is passed. Useful options:

```bash
superra dashboard artifact setup \
  --branch main \
  --branch 'analysis/**' \
  --retention-days 14 \
  --task-root superRA \
  --output .superra-dashboard/dashboard.html
```

At runtime the workflow checks out the pushed branch, exports that branch's `superRA/` tree with `uv run --project skills/task-system superra dashboard export`, passes a GitHub blob URL for the triggering commit as the export's file-link base, deletes older artifacts with the same branch-derived artifact name, then uploads the new HTML artifact. Artifact names are `superra-dashboard-<branch-slug>-<ref-hash>` by default; the hash prevents collisions between refs such as `feature/foo` and `feature-foo`.

This mode is repo-access-gated by GitHub Actions artifact permissions but is not a hosted webpage. Collaborators download the artifact from the workflow run and open the HTML locally.

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
