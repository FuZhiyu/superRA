# Task System Internals

Load this reference when modifying the task-system skill itself — scripts, data layer, hooks, or migration logic.

## Setup: the `superra` CLI

The scripts here run as loose files via `uv run --script <file>` — there is no installable package and no `pyproject.toml`. Each entry script (`scripts/cli.py`, `scripts/plan_dashboard.py`, `scripts/task_hook.py`) carries a PEP 723 inline-metadata block as the single source of truth for its dependencies. `uv run --script` is script-scoped: it never provisions the caller's project environment and reads the file live each run, so a source edit lands on the next call with no cache-bust. The core is stdlib-only (the only third-party import, `pyyaml` in `_comments.py`, is lazy), so a `python3 <file>` fallback works almost everywhere; `cli.py` declares `pyyaml`, `plan_dashboard.py` declares the web stack, `task_hook.py` declares nothing.

**Canonical end-user / agent form: the task-tree wrapper.** A `superRA/` task tree carries a generated `superra` wrapper. It resolves the task-system source dir and runs the relevant entry script via `uv run --script` (falling back to `python3`) — no install step, no project `.venv`, always the live source:

```bash
./superRA/superra task tree          # resolves the installed plugin and runs cli.py
./superRA/superra dashboard          # routes to plan_dashboard.py (carries the web stack)
superra wrapper init                 # (re)write the wrapper into the task root; idempotent
```

The resolver (single-sourced in `scripts/wrapper_resolver.py`, embedded identically into the generated wrapper and the `hooks/task-hook` shim) tries, in order: `CLAUDE_PLUGIN_ROOT` / `PLUGIN_ROOT` env var → a local checkout (so contributor edits win over a copied cache snapshot) → the Claude install recorded in `~/.claude/plugins/installed_plugins.json` → a bounded depth-3 glob of `~/.codex/plugins/cache` (highest semver) → a GitHub fallback that shallow-clones the repo to the user cache and runs the loose `cli.py` from inside the clone (the only pinned reference, fires only when nothing local resolves). Each candidate is tested for `scripts/cli.py`. It is a fast bounded lookup, never a full-disk search. The wrapper routes by first argument: `dashboard` → `plan_dashboard.py` (so the web stack never lands on the task hot path); everything else → `cli.py`.

**Bootstrap (planner/main-only, fresh project).** The wrapper is what makes `superra` resolvable, so the first call — which creates the wrapper — cannot use a `superra` that does not exist yet. Run the loose entry script directly from the loaded skill directory (`<skill-dir>` = the directory containing `SKILL.md`; substitute the real path):

```bash
uv run --script <skill-dir>/scripts/cli.py wrapper init   # writes superRA/superra
```

After the wrapper exists, every call (including from subagents) uses `./superRA/superra …`.

**Never run bare `uv run superra` from a research project.** With no package there is no `superra` console entry, and `uv run` without `--script` would provision that project's environment — wrong. Use the wrapper, the bootstrap form above, or the checkout form below.

**Contributor form (local checkout):** run the loose entry script from the edited source so changes are picked up live — see `CLAUDE.md §Local Task-System CLI Development`:

```bash
uv run --script skills/task-system/scripts/cli.py task tree
uv run --script skills/task-system/scripts/plan_dashboard.py dashboard export --root superRA --output dashboard.html
python3 skills/task-system/scripts/cli.py task tree   # uv-free fallback (stdlib core)
```

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

- **`Edit|Write` / `apply_patch`** — fires when a `task.md` is edited directly (reconciling from the edited file's plan root) and, more broadly, when **any `.md` under a task root** is edited (running the render-integrity check below). Codex's `Edit|Write` matcher covers `apply_patch`, and `task_hook.py` also accepts `tool_name: "apply_patch"` payloads.
- **`Bash`** — fires when a shell command both references `superRA` or `.plan` and contains a filesystem-mutating verb (`mv`, `git mv`, `rm`, `rmdir`, `cp`, `mkdir`), so a plain `mv` reorganization of the tree stays validated. Read-only task-tree commands (`superra task tree`, `grep superRA`) fail the verb test and early-exit.

On a match the hook runs a best-effort reconcile — `validate_plan`, `propagate_parent_status` — each in its own try/except, never blocking, always exit 0. Alongside the reconcile, every edited `.md` under a task root is run through the warn-only **render-integrity check** (`_markdown_integrity_feedback` imports `check()` from the sibling `report-in-markdown/scripts/md_integrity.py`): findings — display `$$` blocks not blank-line separated, TeX-only macros KaTeX cannot render — merge into the same feedback payload, and a checker failure is swallowed so it never breaks the hook. **On a same-parent `mv`/`git mv` rename it also auto-cascades sibling `depends_on`** via `_task_io.cascade_depends_on_rename` (the shared helper `task_rename.py` uses), classified by `_detect_same_parent_rename`: a two-operand move, no flags, same parent, differing slug, both inside a task root, destination is a task. It runs before reconcile so `validate_plan` sees the rewired edges and emits no spurious dangling-dependency warning, and is surfaced in the feedback payload. The auto-cascade is scoped to this lossless same-parent rename only — cross-parent moves (inexpressible in the sibling-only model), deletes of a depended-on task (drops a real edge), and merges (no `task merge` command; the human integrates nuance) instead warn via the normal dangling-dependency validation. The boundary is YAML metadata only — never task content, and display prefixes are never auto-renumbered. It does not regenerate the dashboard (only `superra dashboard export` does). Validation warnings and non-fatal reconcile failures go into a PostToolUse JSON payload with both top-level `additionalContext` and `hookSpecificOutput.additionalContext`; no-feedback paths stay silent for Claude-compatible invocations and emit `{}` when Codex requests parseable empty hook JSON. See `task_hook.py` for the gating regexes and plan-root discovery, and `hooks/hooks.json` / `hooks/hooks-codex.json` for the wiring.

`hooks/task-hook` is the stable shell entry point the manifests invoke. It is a **generated** file: it embeds the same source-resolution chain as the task-tree wrapper (see §Setup) so the two cannot drift, then forwards stdin to the resolved `scripts/task_hook.py` via `uv run --script` (falling back to `python3 scripts/task_hook.py` when `uv` is unavailable, else no-op — it never blocks). Both the shim and the wrapper render from `scripts/wrapper_resolver.py`; regenerate the committed shim with `superra wrapper render-hook --output hooks/task-hook` rather than hand-editing it (a byte-identity test pins the committed shim to the generator).

`parse_task()` is lenient at parse time: an invalid status enum is **warned** (via `warnings.warn`) and the raw value is preserved, so a single malformed `task.md` never crashes a reader's tree walk (dashboard, `task query`, `task read`). Strict status validation is owned by `task check` (`check_status_validity`), which reports an invalid enum as an `[ERROR]` finding.

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
3. Run `superra dashboard` to launch the dashboard.

### Upgrade from v1 to v2 format

```bash
superra task migrate upgrade
```

Converts `## Steps` (checkboxes) to `## Objective` (prose), removes redundant `# Title` headings. Idempotent — safe to run multiple times.

## Dashboard: `plan_dashboard.py`

The dashboard is a live-updating server (FastAPI + SSE), not a static HTML file.

```bash
superra dashboard                                                       # installed plugin (via the task-tree wrapper)
uv run --script skills/task-system/scripts/plan_dashboard.py dashboard   # local checkout (loose script)
superra dashboard --foreground                                          # block in this terminal
superra dashboard stop                                                  # stop the background server
```

The wrapper's `dashboard` subcommand routes straight to `plan_dashboard.py` via `uv run --script`; against a local checkout, run the loose `plan_dashboard.py dashboard …` form for live-source edits. `cli.py` translates the user-facing `dashboard` surface (`export` / `stop` / default-serve / `artifact`) to `plan_dashboard.py`'s internal `serve` / `stop` / `generate` argv, so the translation has one home.

**Lifecycle.** `superra dashboard` is fire-and-forget: it launches the server detached, waits for it to bind, prints URL + PID + log path, and returns the terminal. A second launch for the same repo reuses the running server (opens a tab) rather than spawning a duplicate. The server self-exits after 5 continuous minutes with zero open tabs (a live `/events` SSE connection counts as one open tab, summed across worktrees; heartbeats prune connections dropped by sleep/network loss). `--foreground` runs it blocking with logs on stdout (also self-exits on idle); `superra dashboard stop` terminates the background server (no-op when none is running). The PID and log files (`superra-dashboard.pid` / `.log`) live under the git common dir alongside the port key — repo-scoped, shared across the repo's worktrees.

The server provides SSE hot-reload, auto-updating when the viewed worktree's task files change. Port is derived deterministically from the git common directory (range 8100–8999; the plan-root path is the no-git fallback), so all of a repo's worktrees share one server. That server resolves any worktree per request: the active worktree rides the browser URL as `?wt=<worktree-basename>` (absent means the launch worktree), and the selector does in-page navigation, not a server-wide switch — so two tabs can view different worktrees on one port without interfering. `--port N` overrides. The static `generate` subcommand is deprecated — use live `superra dashboard`, or `superra dashboard export --output dashboard.html` for a one-off static file.

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

At runtime the workflow checks out the pushed branch, exports that branch's `superRA/` tree with `uv run --script skills/task-system/scripts/plan_dashboard.py dashboard export`, passes a GitHub blob URL for the triggering commit as the export's file-link base, deletes older artifacts with the same branch-derived artifact name, then uploads the new HTML artifact. Artifact names are `superra-dashboard-<branch-slug>-<ref-hash>` by default; the hash prevents collisions between refs such as `feature/foo` and `feature-foo`.

This mode is repo-access-gated by GitHub Actions artifact permissions but is not a hosted webpage. Collaborators download the artifact from the workflow run and open the HTML locally.

**On-demand export.** A static `dashboard.html` is produced only by an explicit `superra dashboard export` (including the GitHub Actions workflow above) — neither the mutation scripts nor the PostToolUse hook write it. For interactive viewing, the live SSE server renders on demand without ever writing a file.

## Script Inventory

| Script | Purpose |
|---|---|
| `_task_io.py` | Shared data layer (not invoked directly) |
| `_comments.py` | Comment sidecar data layer — load, re-anchor, resolve, and full-block extraction (not invoked directly) |
| `task_read.py` | Context-aware task reading with ancestor chain, dependency status, and unresolved comments |
| `task_comment.py` | Read and resolve task comments: `list`, `list-tree`, `resolve` |
| `task_create.py` | Create a new task directory with template `task.md` |
| `task_update.py` | Update frontmatter fields on an existing task |
| `task_add_result.py` | Append a finding to a task's `## Results` section |
| `task_query.py` | Query the tree: `--tree`, `--frontier`, `--dag`, `--json` |
| `task_link.py` | Add or remove sibling dependencies |
| `task_rename.py` | Rename a task directory (cascades to sibling `depends_on`) |
| `plan_migrate.py` | Migrate from legacy PLAN.md/RESULTS.md or upgrade v1 -> v2 |
| `plan_dashboard.py` | Live dashboard server (`serve`) and static generation (`generate`, deprecated) |
| `wrapper_resolver.py` | Single-source bash source-resolution chain; renders the task-tree `superra` wrapper (`superra wrapper init`) and the committed `hooks/task-hook` shim (`superra wrapper render-hook`) |
| `test_task_system.py` | Test suite for `_task_io.py` |
