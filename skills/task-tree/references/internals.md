# Task Tree Internals

Load this reference when modifying the task-tree skill itself — scripts, data layer, hooks, or migration logic.

## Setup: the `superra` CLI

Bootstrap and end-user invocation are covered in `SKILL.md §CLI Setup`. Contributor run forms (local checkout) are owned by `CLAUDE.md §Local Task-Tree CLI Development`.

**Never run bare `uv run superra` from a research project.** With no package there is no `superra` console entry, and `uv run` without `--script` would provision that project's environment — wrong. Use the wrapper or the bootstrap form in `SKILL.md §CLI Setup`.

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
| `write_task(task)` | Write a `Task` back to disk, preserving body content. Atomic: temp file + `os.replace`, so concurrent readers never see a half-written file. |
| `walk_plan(plan_root)` | Recursively walk plan directory, return root `Task` with populated children. |
| `resolve_path(plan_root, task_path)` | Resolve a relative task path to its directory. Rejects paths that escape the root. |
| `compute_status(task)` | Roll up status from children. Parked-status exclusion and all-parked branch rules are specified in `task-file-contract.md §Field-by-Field Notes`. |
| `compute_frontier(root)` | Return leaf tasks ready for dispatch — status is not-started/in-progress and all sibling deps are approved. |
| `collect_all_tasks(root)` | Flatten the tree depth-first (excluding root). |

### Validation suite: `_task_validate.py`

The validation rules live in their own module so each rule has one owner and one message source. `invalid_status_message(status)` is the single source for the status-validity message — `parse_task`'s lenient warning and `task check`'s strict `[ERROR]` finding both render it.

| Function | Purpose |
|---|---|
| `invalid_status_message(status)` | The single message source for the status-validity rule. |
| `validate_frontmatter(task)` | Validate status enums, title non-empty, list types. Returns list of warning strings. |
| `validate_revision_notes(task)` | Warn when an `approved` task still carries a `## Revision Notes` section. |
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

`task_hook.py` is the task tree's PostToolUse hook, wired in `hooks/hooks.json` and `hooks/hooks-codex.json`. See `task_hook.py` for the gating regexes and plan-root discovery, and `hooks/hooks.json` / `hooks/hooks-codex.json` for the wiring.

**Matcher gating.** Two groups fire the hook:
- **`Edit|Write` / `apply_patch`** — fires on any `.md` edited under a task root (runs render-integrity check) and on `task.md` edits specifically (also runs reconcile). Codex's matcher covers `apply_patch`; `task_hook.py` also accepts `tool_name: "apply_patch"` payloads.
- **`Bash`** — fires when a shell command both references `superRA` or `.plan` and contains a filesystem-mutating verb (`mv`, `git mv`, `rm`, `rmdir`, `cp`, `mkdir`). Read-only commands fail the verb test and early-exit.

**Reconcile.** On a match the hook runs `validate_plan` and `propagate_parent_status`, each in its own try/except, never blocking, always exit 0.

**Render-integrity check.** Every edited `.md` under a task root is run through `_markdown_integrity_feedback` (imports `check()` from `report-in-markdown/scripts/md_integrity.py`): findings (display `$$` blocks not blank-line separated, TeX-only KaTeX macros) merge into the feedback payload. Checker failure is swallowed and never breaks the hook.

**Same-parent rename auto-cascade.** On a same-parent `mv`/`git mv` rename (`_detect_same_parent_rename`: two-operand move, no flags, same parent, differing slug, both inside a task root, destination is a task), the hook performs the same lossless maintenance `superra task move` does, via the shared `_task_io` core: it cascades sibling `depends_on` (`cascade_depends_on_rename`) and re-points relative Markdown links into and out of the renamed task (`compute_move_link_rewrites`) before reconcile, so `validate_plan` sees a coherent tree. Both are mechanical repairs of the move's own breakage. Cross-parent moves, task deletes, and merges are ambiguous post-hoc state: the hook never reconstructs a clean from→to for them, so they warn via normal dangling-dependency validation rather than auto-mutating.

**Dashboard.** The hook does not regenerate the dashboard. Only `superra dashboard export` writes a static file.

**Feedback payload.** Validation warnings and non-fatal reconcile failures go into a PostToolUse JSON payload under `hookSpecificOutput.additionalContext`, with `hookEventName: "PostToolUse"`. Do not also emit a top-level `additionalContext`: current Codex validates PostToolUse output against the event-specific shape and rejects that legacy sibling field. No-feedback paths stay silent for Claude-compatible invocations and emit `{}` when Codex requests parseable empty hook JSON.

**Hook shim.** `hooks/task-hook` is the stable shell entry point the manifests invoke. It is a **generated** file that embeds the same source-resolution chain as the task-tree wrapper so the two cannot drift, then forwards stdin to `scripts/task_hook.py`. Both the shim and wrapper render from `scripts/wrapper_resolver.py`; regenerate the committed shim with `superra wrapper render-hook --output hooks/task-hook` rather than hand-editing it.

**Lenient parse, strict check.** `parse_task()` warns on an invalid status enum and preserves the raw value (never crashes a tree walk). `task check` (`check_status_validity`) reports an invalid enum as `[ERROR]`.

**Codex / Cursor coverage.** Codex shell interception remains incomplete: `Bash` coverage is best-effort, not a complete enforcement boundary. Cursor does not wire `task_hook.py`.

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

### Consolidate legacy status fields

```bash
superra task migrate upgrade-status
```

Consolidates the legacy `review_status`/`integration_status` fields into the single `status` field (precedence: `integration_status` > `review_status` > existing `status`). Supports `--dry-run` to preview changes.

## Dashboard: `plan_dashboard.py`

The dashboard is a live-updating server (FastAPI + SSE), not a static HTML file.

```bash
superra dashboard                                                       # installed plugin (via the task-tree wrapper)
uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard   # local checkout (loose script)
superra dashboard --foreground                                          # block in this terminal
superra dashboard stop                                                  # stop the background server
```

The wrapper's `dashboard` subcommand routes straight to `plan_dashboard.py` via `uv run --script`; against a local checkout, run the loose `plan_dashboard.py dashboard …` form for live-source edits. `cli.py` translates the user-facing `dashboard` surface (`export` / `stop` / default-serve / `artifact`) to `plan_dashboard.py`'s internal `serve` / `stop` / `generate` argv, so the translation has one home.

**Lifecycle.** `superra dashboard` is fire-and-forget: it launches the server detached, waits for it to bind, prints URL + PID + log path, and returns the terminal. A second launch for the same repo reuses the running server (opens a tab) rather than spawning a duplicate. The server self-exits after 5 continuous minutes with zero open tabs (a live `/events` SSE connection counts as one open tab, summed across worktrees; heartbeats prune connections dropped by sleep/network loss). `--foreground` runs it blocking with logs on stdout (also self-exits on idle); `superra dashboard stop` terminates the background server (no-op when none is running). The PID and log files (`superra-dashboard.pid` / `.log`) live under the git common dir alongside the port key — repo-scoped, shared across the repo's worktrees.

**Binding.** The server binds loopback (`127.0.0.1`) by default and is unauthenticated — it serves project files (`/files/{path}`), the full task tree (`/export`), and disk-writing comment routes. Pass `--host 0.0.0.0` only to deliberately expose it on a trusted LAN; with background-by-default serving an all-interfaces bind is a long-lived ambient surface, so it is opt-in, not the default.

The server provides SSE hot-reload, auto-updating when the viewed worktree's task files change. Port is derived deterministically from the git common directory (range 8100–8999; the plan-root path is the no-git fallback), so all of a repo's worktrees share one server. That server resolves any worktree per request: the active worktree rides the browser URL as `?wt=<worktree-basename>` (absent means the launch worktree), and the selector does in-page navigation, not a server-wide switch — so two tabs can view different worktrees on one port without interfering. `--port N` overrides. The static `generate` subcommand is deprecated — use live `superra dashboard`, or `superra dashboard export --output dashboard.html` for a one-off static file.

### Headless ensure-running and task URLs

`superra dashboard --no-open` is the browser-free, idempotent way to guarantee a server is up: it reuses a healthy background server — printing `Dashboard already running at http://localhost:<port>` — or starts one detached and prints `Dashboard running at http://localhost:<port>`. The reuse check reads the repo-scoped PID file, so this one command both reports whether a server was already running and leaves one running either way; the printed `localhost:<port>` is the live URL.

A specific task's URL extends that base — task path in the hash, worktree in `?wt=`:

```
http://localhost:<port>/?wt=<worktree-basename>#/<task-path>
```

- `<task-path>` — the task-root-relative locator, exactly the `superra task read` argument (no `superRA/` prefix), e.g. `data-preparation/merge`; empty for the tree root.
- `?wt=` — selects the worktree (the `?wt=` rule above); drop it for the launch worktree.

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

At runtime the workflow checks out the pushed branch, exports that branch's `superRA/` tree with `uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard export`, passes a GitHub blob URL for the triggering commit as the export's file-link base, deletes older artifacts with the same branch-derived artifact name, then uploads the new HTML artifact. Artifact names are `superra-dashboard-<branch-slug>-<ref-hash>` by default; the hash prevents collisions between refs such as `feature/foo` and `feature-foo`.

This mode is repo-access-gated by GitHub Actions artifact permissions but is not a hosted webpage. Collaborators download the artifact from the workflow run and open the HTML locally.

**On-demand export.** A static `dashboard.html` is produced only by an explicit `superra dashboard export` (including the GitHub Actions workflow above) — neither the mutation scripts nor the PostToolUse hook write it. For interactive viewing, the live SSE server renders on demand without ever writing a file.

## Script Inventory

**Data layer (not invoked directly):**

| Script | Purpose |
|---|---|
| `_task_io.py` | Core data layer — parse, write, walk, frontier, status rollup, body section parsing |
| `_task_validate.py` | Validation suite — one owner per validity rule, single message source |
| `_comments.py` | Comment sidecar data layer — load, re-anchor, resolve, and full-block extraction |
| `_worktree_discovery.py` | Worktree discovery — enumerate git worktrees, identify those with a task root |

**Entry scripts (invoked via `cli.py` or directly):**

| Script | Purpose |
|---|---|
| `cli.py` | Console entry point — routes `superra task *` and `superra dashboard *` sub-commands |
| `task_read.py` | Context-aware task reading with ancestor chain, dependency status, and unresolved comments |
| `task_comment.py` | Read and resolve task comments: `list`, `list-tree`, `resolve` |
| `task_create.py` | Create a new task directory with template `task.md` |
| `task_update.py` | Update frontmatter fields on an existing task |
| `task_add_result.py` | Append a finding to a task's `## Results` section |
| `task_query.py` | Query the tree: `--tree`, `--frontier`, `--dag`, `--json` |
| `task_link.py` | Add or remove sibling dependencies |
| `task_rename.py` | Move or rename a task directory; rewrites relative links and cascades/drops sibling `depends_on` (mechanics in `references/commands.md §Move / rename a task`) |
| `task_check.py` | Read-only diagnostic — validates status, dependencies, and cycles; use `task status fix` to repair branch status fields |
| `plan_migrate.py` | Migrate from legacy PLAN.md/RESULTS.md or upgrade v1 -> v2 |
| `plan_dashboard.py` | Live dashboard server and static export (`generate`, deprecated; use `dashboard export`) |
| `dashboard_artifact_workflow.py` | Render and install the GitHub Actions artifact-sharing workflow |
| `task_hook.py` | PostToolUse hook — reconcile, render-integrity check, same-parent rename auto-cascade |
| `wrapper_resolver.py` | Single-source resolution chain; renders the `superra` wrapper (`superra wrapper init`) and the `hooks/task-hook` shim (`superra wrapper render-hook`) |

**Test modules (collected by pytest from `skills/task-tree/scripts/`):**

| Module | Coverage |
|---|---|
| `test_task_tree.py` | Data layer, CLI scripts, migration, hooks, parser robustness, status model, tree validation |
| `test_dashboard.py` | Dashboard server routes, SSE, templates, standalone export, server lifecycle, master-detail partials |
| `test_cli.py` | `cli.py` command surface — argument parsing, routing, end-to-end command flows |
| `test_multi_worktree.py` | Multi-worktree forest detection and per-worktree task-root resolution |
| `test_worktree_selector.py` | Worktree selector UI and live refresh |
| `tests/test_comments.py` | Comment surfacing on the agent read path (`_comments`, `task_read`, `task_comment`) |
| `tests/test_state_preservation.py` | Dashboard state preservation across reloads |
