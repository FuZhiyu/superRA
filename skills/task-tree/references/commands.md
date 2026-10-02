# Task-Tree Command Surface

Load when mutating a `superRA/` tree — scaffolding tasks, restructuring, re-wiring dependencies, bulk status operations.

Bare `superra …` below denotes the committed `./superRA/superra` wrapper.

**Single-field edits go through direct edit, not these CLIs.** One field on one task — including `status` — edit its `task.md` with Read/Edit (`using-superra/SKILL.md §Task Interface`); the PostToolUse hook validates and propagates. Reach for the commands below when direct edit would be tedious or error-prone: template scaffolding, bulk or scripted changes.

## Scaffold a new task

Creates the directory, fills the template with current dates, sets frontmatter defaults (`status: not-started`):

```bash
superra task create 01-data/03-filter \
  --title "Filter Sample" \
  --objective "Apply standard filters: drop obs before 2000, require non-missing returns." \
  --guidance "Consider reusing Code/common_filters.py." \
  --depends-on 02-merge
```

`--details` is optional — seeds a `## Details` section. `--guidance` is a working alias.

## Bulk status operations

```bash
superra task status propagate
superra task status cascade 01-data --status approved
superra task status fix
```

- `status propagate` — flips stale branch statuses to their computed rollup.
- `status cascade` — sets all descendant leaves to the given status (`approved`, `not-started`, `archived`, `postponed`).
- `status fix` — rewrites branch frontmatter `status` in place to match `compute_status()` from children, leaving leaves untouched.

## Append a result programmatically

```bash
superra task result add 01-data/01-load \
  --finding "Loaded 4.7M rows across 12K funds"
```

## Manage dependencies

Explicit logical dependency edits:

```bash
superra task dep add 01-data/03-filter 02-merge

superra task dep remove 01-data/03-filter 02-merge
```

- **`dep remove` removes only the `depends_on`:** a file edge between the same tasks remains, and the command names its file.
- **Preflight refuses only a new `depends_on` error** (a cycle or an unresolved slug), leaving task files and directories unchanged. Otherwise the command prints each new warning — a `depends_on` against the file flow, a postponed or archived prerequisite — and each task it takes off the frontier.

## Move / rename a task

Intentional path changes use the CLI, not raw `mv` / `git mv`:

```bash
superra task move 01-data/01-load 01-data/01-load-raw
superra task move 01-data/03-filter 02-analysis/01-filtered-sample
```

`superra task rename FROM TO` is a compatibility alias for same-parent renames.

`move` carries the whole task directory — `task.md`, `comments.yaml`, attachments, descendants — and resolves relative paths and `depends_on` edges itself. Run it directly rather than rewriting links or rewiring dependencies by hand first.

It re-points every relative Markdown link the move would break: links inside the moved files, and links anywhere else in the tree pointing into the moved subtree.

Authored `depends_on` is sibling-only. Inferred dependencies are recomputed from step ownership after a proposed move; the move is refused before filesystem writes if it adds a `depends_on` error. Same-parent rename: sibling `depends_on: old-slug` cascades to `new-slug`. Cross-parent move: each edge that no longer resolves under the new parent is dropped with a warning — an old sibling's edge to the moved slug, or the moved task's edge to a slug absent from the destination. Re-add a dropped edge that should still hold with `superra task dep add`.

The PostToolUse hook still revalidates raw filesystem moves and keeps the same-parent auto-cascade guardrail, but is not the canonical move mechanism. Raw `mv` / `git mv` only for recovery from tool failure, then `superra task check`.

## Diagnostics

`superra task check` is the tree's validation entry point. Run it after any bulk operation or raw filesystem change — it audits status validity, dependency integrity, and cycle-free ordering:

```bash
superra task check                    # validate full tree; prints findings grouped by task
superra task check --category status  # limit to one category: status, dependency, rollup, sync-impact, reproduction
superra task status fix               # repair branch status fields to match child rollups
superra task status propagate         # re-run parent status rollup after bulk edits
```

Findings are prefixed `[ERROR]` (blocking; tree inconsistent), `[WARNING]` (advisory), or `[INFO]`. After recovering from a raw `mv` / `git mv`, run the check before the next dispatch.

## Reproduction

`superra repro` runs the build graph the `## Reproduction` sections declare (schema and records: [task-file-contract.md](task-file-contract.md) §Reproduction Section).

```bash
superra repro status .                    # every registered step's freshness
superra repro status 02-merge '02-merge#check-panel' # selected tasks/steps and their producer chain
superra repro status 02-merge --only --json # the selected steps alone, against saved inputs
superra repro build 02-merge -j 4         # task's own and descendant steps, plus producers that need it
superra repro build 02-merge --only      # its own steps only; producers' files as they sit on disk
superra repro build 02-merge --dry-run   # what would run, why, and what it last cost
superra repro build '02-merge#check-panel' --force # force just the check; stale producers still build
superra repro build . --force            # rerun every registered step
superra repro explain 02-merge            # where each changed hash came from, grouped by cause
superra repro explain Output/panel.parquet --json # one file's provenance, producer, and readers
superra repro impact Code/helpers.jl --scope 02-merge # affected steps, including outside scope, with last durations
superra repro dag --mermaid               # the step graph
```

Every target is a task path, a `task#step` selector, or a unique bare step name; multiple targets select the deduplicated union. A task path includes its own and descendant steps. Paths are task-root-relative; `.` selects the whole active tree and `.#step` selects a root-owned step. A task path wins over a step of the same name. `build` and `status` require at least one target.

`build`, `status`, and `build --dry-run` also assess each target's transitive producer chain, never unrelated steps in the producers' tasks. `--only` restricts them to the targets: files from producers outside them are saved inputs, existing files used without a successful baseline or override, and a missing saved input blocks and names its producer. `--upstream` is a hidden alias for the default. `--force` reruns the targets' own steps; an added producer runs only when its state calls for it. `accept` and `revoke` act on the named steps only.

`build` runs each `stale`, `missing`, `failed`, or forced step as one subprocess from the project root, in dependency order; `-j N` runs up to N at once. It never runs an `unverified` step and uses its outputs as they are. A step stale only through a producer reruns only if its inputs changed once that producer ran. Before executing, `build` prints the added producers that will run, with their last recorded durations. It prints a line for each step that executes or fails; steps that do not run are counted in the closing line. A failed step skips its descendants while unrelated steps continue, and `build` exits 1; Ctrl-C, SIGTERM, or SIGHUP stops running steps and records them failed; steps not yet started keep their records and acceptance. `build --dry-run` lists each step it would execute, every step below one included, with its last recorded duration; the total is an upper bound. Every command runs on Python 3.10+; reading a legacy `pytask.lock` needs Python 3.11, and the runner re-execs itself under `uv` for it.

**Download gate.** Before running anything, `build` refuses when a step that will run reads a file not on disk, online-only or absent with no producer, that no step in the build writes first. It runs nothing and lists those files with their sizes. It names `--only` as the way to build the steps that do not read them (under `--only`: download the files or narrow the targets), and points to the `superRA:reproducibility` download notes. `build --dry-run` prints its plan with recorded costs, then the same file list, and exits 1. The same check runs when each step starts, because a step can turn stale after its producers run; a step it stops writes no run record.

`status` prints one line per selected step, then its producers: their counts per state, each `stale`, `missing`, or `failed` producer by name, and the `unverified` ones on one line with their total online-only size and where tracing stops, the first `unverified` producer on each path back from the selection. Files the `unverified` steps cannot check here follow, with their sizes. It counts the steps outside the owning task that read a step's outs (`outside readers: N`); `explain` names them. Exit codes:

| Exit | When |
|---|---|
| 0 | Every assessed step is `fresh` or `unverified`. |
| 1 | A selected step's own state is `stale`, `missing`, or `failed`, or a graph error touches an assessed step. |
| 3 | Only a producer behind the selection is `stale`, `missing`, or `failed`. With `--only`, which assesses no producers, `status` names them. |

Default text output lists at most `OUTPUT_CAP` items per list; the rest collapse to a count and the `--json` command that lists them.

Status JSON records `targets`, `upstream` (false under `--only`), `steps` (the selected steps), `producers` (every assessed producer, uncapped), `ok` (every assessed step is `fresh` or `unverified`), and `summary` (selected-step counts per state, with producer counts under `producers`). It also records `boundary_inputs` (the saved inputs: paths, producer, fingerprints, provenance, consumers), under `--only` `behind` (each producer behind the selection that is `stale`, `missing`, or `failed`, with `name`, `task`, `status`), and per step `external_consumers`. Each step carries its reported `status`/`reason` and its own `local_status`/`local_reason` from before a producer lifts it. While another process's build holds the runner lock, a step it is executing reads reason `building now`, with `running: true` and `started_at`, instead of an interrupted run's `failed`.

`task read <path>` lists prerequisites (`depends_on`, own or inherited) apart from inputs (file, producer, state), and a registered task's owned-step states, with each step's own state when a producer lifts it. Its JSON adds the dependency snapshot, global findings, and `readiness` (`ready`, `blockers`, `inputs`). `task frontier --json` rows carry the `inputs` whose producer is `stale`, `missing`, or `failed`. `task dag [subtree]` renders child groups alongside own steps; `--json` returns the complete dependency snapshot.

| State | Meaning |
|---|---|
| `fresh` | Inputs and outputs match the successful build or the current reviewed baseline. Bytes matching the successful build stay fresh when an acceptance no longer validates; the reason names it and the `revoke` that clears it. A check whose lock entry matches its current inputs but has no local stamp is fresh with the reason `passed at these inputs in lock <rev> on <platform>; not run here`, unless it last failed here. |
| `stale` | A dep, an out, or the step definition changed; or a producer is `stale`, `missing`, or `failed`, and the reason names the furthest-upstream such step, JSON `origin`. |
| `missing` | Never built, or an out is gone. |
| `failed` | The last or interrupted run did not succeed and the step still has work to do; the reason names its log. Restoring inputs can clear an ordinary failure. |
| `unverified` | A file cannot be checked here: online-only and not in this machine's hash cache, unreadable, or absent with no step producing it. `build` never runs the step; its outputs are used as they are. |

A step takes the first state its own evidence supports, in the order `failed`, `missing`, `stale`, `unverified`, `fresh`; `local_status` keeps it when a producer lifts it to `stale`. No check downloads a file: an online-only file (`SF_DATALESS`, or a legacy Dropbox placeholder) is never opened, and one whose size differs from the lock's reads changed. Each step's JSON `files` lists every dep and out with its `outcome` (`matches`, `changed`, `absent`, `unknown`, or null for a never-built step's file on disk), `online_only`, and `size`.

A project last built by the pytask engine reads `pytask.lock` and `repro-builds.json` until its first build writes `repro-lock.json`; that build prints the `git rm` that retires them.

`impact <path...> [--scope <task-or-step>]` lists each affected step with its last recorded duration and total: direct consumers with script/declared/include/environment origins, then descendants with the file connecting them. `superRA/config.yaml` affects every step using a runner template, a `${VAR}`, or `env_deps`. Repeat `--scope` for multiple selections; steps outside it are marked, and stay in JSON as `in_scope: false`. `--json` adds the connecting edges.

### Reviewed acceptance

`accept <step-or-task...> --reason '…'` records the current inputs, specification, and outputs as the reviewed baseline in one call. It supports first registration, harmless changes, and changed outputs from direct runs. A task expands to its owned and descendant steps.

```bash
superra repro accept 02-merge --reason 'Ran interactively and reviewed the current results'
superra repro accept 02-merge --reason '...' --dry-run   # preview; writes nothing
superra repro revoke 02-merge --json
```

`--reason` is required to accept; cite any evidence file in it. Optional `--review NODE=RATIONALE` adds a per-node note; repeat it for several.

The call runs every consistency check, rechecks hashes and declarations immediately before writing, and writes each changed step's record atomically. A selected step whose own `status` reads fresh keeps its evidence; no record is written for it. Invalid graphs, missing declared inputs/outputs, files this machine cannot hash (listed with their sizes), concurrent edits, and failed or interrupted runs reject acceptance. After recording, and in `--dry-run`, it names the `stale`, `missing`, or `failed` producers behind the accepted steps (JSON `behind`): the accepted steps read stale until those are built or accepted. `explain` and JSON `acceptance` show the reason, optional notes, and `basis: reviewed`.

Forced execution bypasses acceptance within the target scope; beginning a real attempt removes that step's record, including when the attempt fails. Revoke removes selected records; a downstream acceptance keeps its own reviewed state, and `status` reports it stale while the revoked producer is not fresh.

### Explain

`explain <target>` reports, for every changed node, its recorded and current hash, where each came from, a cause keyed on the node's role in the step, and one tool pointer.

- **Targets.** A task path groups rows by cause across its non-fresh steps; `task#step` or a unique bare step name gives one row per changed node; a declared file path gives that file's provenance, producer, and readers.
- **Sources.** Each side names where its hash came from; a lock or git revision states its relation to HEAD: `in HEAD's lock, entry <step>`, `earlier commit, N behind HEAD`, or `not in HEAD's history; on <branch>, …`. A row whose bytes came from a build compares the builder's environment (`env: same as lock builder` or `env: differs — <field>`). History search is bounded and never fetches ([internals.md §Explain sources and history](internals.md#explain-sources-and-history)).
- **Diffs.** A step or file target shows the first 20 diff lines of a tracked dependency; `--diff` shows all, in a task view too. `--json` carries full hashes, every source, one row per step and node, and groups.
- **Graph errors.** A graph error on an explained step is listed with the `N graph error(s)` line `status` prints, and `explain` exits 1, as `build` refuses that step.

| `cause` | Node | Hint | Pointer |
|---|---|---|---|
| `input-changed` | a dependency (including another step's output) or the step definition | an input or the step definition differs from the last build | `git diff <recorded> [<current>] -- <path>`; for a produced input, the producer's `explain`, or `build <step>` once the producer is fresh |
| `other-build` | an output | the output holds bytes from another recorded build | `git show --stat <rev>` of the revision the row prints |
| `unknown-output` | an output | the output matches no recorded build | `explain <path> --json` |

A missing out, a failed run, an upstream step, and a check that passed elsewhere are status reasons, listed without a cause.

## Comments

Researchers pin comments to `task.md` blocks via the dashboard. `superra task read <path>` already shows unresolved comments with their anchored blocks (`using-superra/SKILL.md §Task Interface`), so use these only for the standalone read/resolve loop:

```bash
superra task comment list <task>           # unresolved comments on a task, each with its full anchored block
superra task comment list <task> --all     # include resolved comments
superra task comment tree                  # unresolved-comment counts across the whole tree
superra task comment resolve <task> <id>   # toggle a comment's resolved state
```

A comment stays **unresolved** until toggled; `resolve` flips it both ways. A comment whose anchored block was edited or moved away renders `[ORPHANED]` with the stored preview. `--json` on `list` / `tree` for scripted consumption.
