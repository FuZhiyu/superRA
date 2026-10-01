---
title: "Include the Producer Chain by Default; `--only` Restricts"
status: not-started
depends_on: []
---

## Objective

Make `superra repro build` and `status` include the selection's producer chain by default, with `--only` restricting them to the named steps, so naming a result is enough to bring it current. This replaces the task-scoped default that [02-runner](../02-runner/task.md) states; at Mature, fold the result into 02-runner, [06-skill](../06-skill/task.md), [03-task-interface](../03-task-interface/task.md), and [04-dashboard-view](../04-dashboard-view/task.md).

### Decisions

- **Default scope.** `build`, `status`, and `build --dry-run` resolve the targets plus their transitive file-producer ancestors through one resolver. Fresh producers are skipped as before.
- **`--only`** restricts to the named selection against saved inputs, keeping today's scoped behavior: the saved-input list, a missing saved input blocking and naming its producer, and the line naming non-fresh producers behind the selection. Its help text says it trusts the files on disk.
- **`--upstream`** stays as a hidden no-op alias.
- **`--force`** reruns the named selection only. Added producers build only when they are not fresh. Forcing a chain means naming its steps, or `.`.
- **`accept` and `revoke`** act on the named steps only. When a producer behind an accepted step is not fresh, `accept` still records the step, then names those producers (capped) and says the step reads stale until they are built or accepted. `--dry-run` and JSON carry the same list.
- **Default `status` output.** One line per selected step. A step whose own evidence is fresh but whose producer is not reads `stale`, with the reason naming the producer. Non-fresh producers are listed, capped by `OUTPUT_CAP` with a count line pointing to `--json`; fresh producers are only counted. Exit 0 when all are fresh, 1 when a selected step is not fresh on its own evidence, 3 when the selection's own evidence is fresh but a producer is not.
- **Build preview.** Before executing, `build` prints the non-fresh producers it added with their last recorded durations (capped). It does not prompt.
- **Same-worktree concurrency.** When another session is editing a producer in this worktree, use `--only`. Parallel dispatch already gives each agent its own worktree.
- **Unchanged.** Freshness, acceptance validation, lock and acceptance-record formats, `explain`, and `impact`.

### Constraints

- [CLAUDE.md](../../../CLAUDE.md) §Bounded Agent-Facing Output governs every new or changed line of CLI and hook output.

## Details

### Why

A TreasuryGIV session (transcript `02d0fe7f`, 2026-10-01) ran `status paper-reframing`, saw stale steps across two tasks, and passed all seven `task#step` selectors to `build`. Its own afterword: "Running `compile-deck` alone would've skipped stale upstream steps, so I listed them manually to avoid an unexpectedly long rerun." Under the scoped default, the agent had to reconstruct the producer chain by hand. It also assumed a task target reruns every step in the task.

### Prior art (2026-10-01 survey)

- **Upstream-by-default is the norm.** DVC, Snakemake, R `targets`, make, doit, Bazel, and Luigi include it. dbt selects the node only, but it has no freshness state.
- **The "only" modes are escape hatches that trust disk state.** DVC `-s/--single-item`, doit `-s/--single`, `targets` `shortcut = TRUE` ("use with caution"), make `-o`.
- **Force scopes are separate.** Snakemake `-f` forces the target, `-F` the chain.
- **Accepting without running is step-local.** `dvc commit`, `make -t`, Snakemake `--touch`.
- **DVC's plain `status` misleads.** It reports a target up to date while its ancestor changed, until `--with-deps` is added. `targets`' `tar_outdated` predicts `tar_make` and includes upstream.
- Sources: [DVC repro](https://doc.dvc.org/command-reference/repro), [DVC status](https://doc.dvc.org/command-reference/status), [Snakemake CLI](https://snakemake.readthedocs.io/en/stable/executing/cli.html), [tar_make](https://docs.ropensci.org/targets/reference/tar_make.html), [tar_outdated](https://docs.ropensci.org/targets/reference/tar_outdated.html).

### Engine facts the change relies on

- **`accept` already ignores the default.** `preview` selects with `include_ancestors=False` and decides "own evidence fresh" from `local_status` ([_repro_acceptance.py:438](../../../skills/task-tree/scripts/_repro_acceptance.py#L438), [:483](../../../skills/task-tree/scripts/_repro_acceptance.py#L483)).
- **The upstream cascade never forces a rerun by itself.** It marks a fresh step stale when its parent is not fresh, in status only ([_repro_acceptance.py:384-385](../../../skills/task-tree/scripts/_repro_acceptance.py#L384-L385)). `build` reclassifies each step against its own target after its producers finish ([repro_run.py:116-120](../../../skills/task-tree/scripts/repro_run.py#L116-L120)). An accepted consumer whose producer regenerates identical bytes stays unchanged; changed bytes invalidate the acceptance and rerun it.
- **The dashboard already assesses upstream.** Its status calls pass `upstream=True` ([plan_dashboard.py:1483](../../../skills/task-tree/scripts/plan_dashboard.py#L1483)), as does the task snapshot ([_task_snapshot.py:68](../../../skills/task-tree/scripts/_task_snapshot.py#L68)).

### At Mature

These task files state the scoped default as current contract; rewrite their lines when folding: [02-runner](../02-runner/task.md), [04-dashboard-view](../04-dashboard-view/task.md), [06-skill](../06-skill/task.md), and [07-workflow-integration](../07-workflow-integration/task.md).
