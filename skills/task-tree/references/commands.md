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

Removing an explicit edge preserves inferred evidence for the same prerequisite. Dependency-changing commands preflight the proposed effective graph before writing; an invalid proposal leaves task files and directories unchanged.

## Move / rename a task

Intentional path changes use the CLI, not raw `mv` / `git mv`:

```bash
superra task move 01-data/01-load 01-data/01-load-raw
superra task move 01-data/03-filter 02-analysis/01-filtered-sample
```

`superra task rename FROM TO` is a compatibility alias for same-parent renames.

`move` carries the whole task directory — `task.md`, `comments.yaml`, attachments, descendants — and resolves relative paths and `depends_on` edges itself. Run it directly rather than rewriting links or rewiring dependencies by hand first.

It re-points every relative Markdown link the move would break: links inside the moved files, and links anywhere else in the tree pointing into the moved subtree.

Authored `depends_on` is sibling-only. Inferred dependencies are recomputed from step ownership after a proposed move; the resulting hierarchy must remain acyclic before filesystem writes. Same-parent rename: sibling `depends_on: old-slug` cascades to `new-slug`. Cross-parent move: each edge that no longer resolves under the new parent is dropped with a warning — an old sibling's edge to the moved slug, or the moved task's edge to a slug absent from the destination. Re-add a dropped edge that should still hold with `superra task dep add`.

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

`superra repro` runs the build graph the `## Reproduction` sections declare (schema: [task-file-contract.md](task-file-contract.md) §Reproduction Section).

```bash
superra repro status .                    # every registered step's freshness; exits 1 unless all are fresh
superra repro status 02-merge '02-merge#check-panel' # selected tasks/steps against saved inputs
superra repro status . --upstream --json  # full graph freshness and local evidence
superra repro build 02-merge -j 4         # task's own and descendant steps only
superra repro build 02-merge --upstream  # also rebuild stale producer ancestors
superra repro build 02-merge --dry-run   # what would run, why, and what it last cost
superra repro build '02-merge#check-panel' --force # force just the check
superra repro build 02-merge --upstream --force # force the full producer chain
superra repro build . --force            # rerun every registered step
superra repro explain '02-merge#build-panel' --json # changes, baseline diffs, acceptance, actual run
superra repro impact Code/helpers.jl --scope 02-merge --json # includes affected steps outside scope
superra repro dag --mermaid               # the step graph
```

Every target is a task path or a `task#step` selector; multiple targets select the deduplicated union. A task path includes its own and descendant steps. Paths are task-root-relative; `.` selects the whole active tree and `.#step` selects a root-owned step. A bare step name is rejected and names its qualified form. Unknown targets and tasks with no steps fail. `build` and `status` require at least one target.

Inputs from out-of-scope producers use existing files without requiring a successful baseline or override. Missing saved inputs block and identify their producer. `--upstream` adds transitive file-producer ancestors; it never selects unrelated steps in their owning tasks. `--force` reruns every step in the resulting scope.

`build --dry-run` previews without changing execution evidence; downstream execution remains conditional on regenerated bytes. It lists each step it would execute with that step's last recorded duration (`unknown` when it has never run), totals the known durations when there is at least one, and names `explain` and `accept` as the alternatives to executing.

`status` counts the steps outside the owning task that read a step's outs (`outside readers: N`); `explain` names them, or states that none does; status JSON carries the list as `external_consumers`. The count is one input to a significance judgment, never the judgment — a selected check, a maintained-path producer, and an out a document cites are significant at zero outside readers.

Status JSON also records `targets`, `upstream`, and `boundary_inputs` (paths, producer, fingerprints, provenance, consumers). Step entries retain full-scope `status`/`reason` and expose `local_status`/`local_reason` before upstream staleness propagation. Default status certifies only selected work against saved inputs; `status --upstream` assesses the chain. The task reader and dashboard retain global freshness while exposing local evidence.

`task read <path>` shows effective prerequisite tasks, including inherited group barriers, and a registered task's owned-step states. Its JSON includes the dependency snapshot and global findings; no pytask is required. `task frontier --json` additionally exposes actionable parent-owned steps with `kind: own-work`. `task dag [subtree]` renders child groups alongside own steps; `--json` returns the complete dependency snapshot so scope does not hide invalidity.

| State | Meaning |
|---|---|
| `fresh` | Inputs and outputs match the successful build or the current reviewed baseline. |
| `stale` | A dep, an out, the step definition, or an upstream step changed. |
| `missing` | Never built, or an out is gone. |
| `failed` | The last run exited non-zero and the step still has work to do; the reason names its log. Restoring inputs can clear an ordinary failure. A failed forced rerun requires a successful retry, which the next build attempts even with unchanged inputs. |
| `external` | A dep no step produces is not on disk, so the step cannot run. |

`pytask.lock` at the project root is committed: its ids are the logical `${VAR}` paths, so it reads the same on every checkout. `.superra-repro/` is not — the hash cache, per-step logs, run records, successful baseline receipts, and check stamps live there, and `repro` creates it and adds it to `.gitignore` on first run.

### Reviewed acceptance

`impact <path...> [--scope <task-or-step>]` reports direct consumers with script/declared/include/environment origins, affected descendants, and connecting files. Repeat `--scope` for multiple selections; `in_scope: false` keeps outside effects visible. This predicts invalidation; unchanged regenerated outputs can stop execution downstream.

`accept <step-or-task...> --reason '…'` records the current inputs, specification, and outputs as the reviewed baseline in one call. It supports first registration, harmless changes, and changed outputs from direct runs. A task expands to its owned and descendant steps; producers outside the selection remain saved inputs. Acceptance certifies the selection, not those producers.

```bash
superra repro accept 02-merge --reason 'Ran interactively and reviewed the current results'
superra repro accept 02-merge --reason '...' --dry-run   # preview; writes nothing
# Apply a specific preview, with the same arguments and its token:
superra repro accept 02-merge --reason '...' --apply <preview-token>
superra repro revoke 02-merge --json
```

`--reason` is required to accept. Optional `--review NODE=RATIONALE` adds per-node notes; optional `--evidence FILE` binds an existing evidence file's bytes (optional `#anchor` references). Repeat either option for multiple notes/files. Without `--json`, `accept` prints the steps it covered and what changed under each.

The one-shot call runs every consistency check inside it and writes all selected records atomically. `--dry-run` previews and prints a token instead of writing; `--apply <token>` then accepts exactly that preview, for a deliberately separated review and apply. The token binds selection, current hashes, preceding successful lock if any, review notes, supplied evidence bytes, and the preceding ledger. Invalid graphs, missing declared inputs/outputs, unavailable supplied evidence, concurrent edits, and failed or interrupted runs reject acceptance. Checks require an existing successful baseline and unchanged check stamp; a never-run check must execute.

Commit the project-root `repro-acceptance.json` with the declarations and reviewed changes. Valid records make ordinary builds and status `fresh`; `explain` and JSON `acceptance` retain the reason, optional notes/evidence, actor, recording time, and `basis: reviewed`. Last actual execution metadata, `pytask.lock`, and check stamps remain unchanged. Forced execution bypasses acceptance within the target scope; beginning a real attempt removes that step's record, including when the attempt fails. Revoke removes selected records; acceptances bound to them become ineffective.

Changes after acceptance invalidate its exact state, including actual sidecar-backed output bytes and saved-input bytes. A matching scoped status does not certify upstream producers; add `--upstream` to assess the chain.

`explain --json` reports verified successful-source snapshots when available, including dirty-checkout runs. Reviewed baselines supply recorded hashes; source text not captured at execution is explicitly unavailable. Raw source snapshots remain local. See [the record contract](task-file-contract.md#acceptance-and-successful-baseline-records).

Root relocation and command-resolution changes follow the [rerun model](../../reproducibility/references/rerun-model.md#what-makes-a-step-rerun).

Only `build` needs pytask, and it re-execs itself under `uv` to get it; nothing has to be installed first.

## Comments

Researchers pin comments to `task.md` blocks via the dashboard. `superra task read <path>` already shows unresolved comments with their anchored blocks (`using-superra/SKILL.md §Task Interface`), so use these only for the standalone read/resolve loop:

```bash
superra task comment list <task>           # unresolved comments on a task, each with its full anchored block
superra task comment list <task> --all     # include resolved comments
superra task comment tree                  # unresolved-comment counts across the whole tree
superra task comment resolve <task> <id>   # toggle a comment's resolved state
```

A comment stays **unresolved** until toggled; `resolve` flips it both ways. A comment whose anchored block was edited or moved away renders `[ORPHANED]` with the stored preview. `--json` on `list` / `tree` for scripted consumption.
