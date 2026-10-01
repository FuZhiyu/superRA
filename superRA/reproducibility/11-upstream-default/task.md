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

## Review Notes

Planning review, design-review mode. Checked against the code at `c0fcbe07`. The engine facts in §Engine facts hold: `accept` selects without ancestors and reads `local_status`, `_decide` reclassifies with `upstream=False` after producers finish, and `force_names` is the whole resolved scope today.

1. **[BLOCKING] No decision covers a producer in the chain that cannot run on this machine.** Take a producer `P` whose external input is absent here, such as raw data kept on another machine, but whose outputs are on disk. Today, `build C` uses `P`'s outputs as saved inputs. Under the new default:
   - **Build fails.** `P` joins the selection and fails with "cannot start" ([repro_run.py:147-148](../../../skills/task-tree/scripts/repro_run.py#L147-L148) in `--dry-run`, [:152](../../../skills/task-tree/scripts/repro_run.py#L152) otherwise). `C` is then skipped ([:279](../../../skills/task-tree/scripts/repro_run.py#L279)), so the default `build` and `build --dry-run` both exit 1.
   - **Status stays at exit 3.** The cascade treats `external` as not fresh ([_repro_acceptance.py:384](../../../skills/task-tree/scripts/_repro_acceptance.py#L384)), and `accept P` refuses because its input is missing ([_repro_acceptance.py:458](../../../skills/task-tree/scripts/_repro_acceptance.py#L458)). The only way out is `--only`, which breaks §Bounded Agent-Facing Output's "every warning has an exit".

   **Fix:** decide what happens, with the researcher if it changes a settled bullet. Options:
   - Stop the walk at an `external` producer whose outputs exist, and report those outputs on the saved-input line.
   - Refuse before running anything, with a message naming `--only`.

   Then add the decision to §Decisions and a regression test to [01-cli](01-cli/task.md) §Validation.
2. **[BLOCKING] [02-discipline](02-discipline/task.md) misses the completion gate, which depends on the scoped default.** [protect-and-completion.md:8](../../../skills/reproducibility/references/protect-and-completion.md#L8) says "building by name only the steps the rule says to run". Under the new default, building a consumer by name also runs every stale producer behind it. That includes a costly producer the stale rule set aside to accept or to ask the researcher about ([rerun-or-accept.md](../../../skills/reproducibility/references/rerun-or-accept.md) §The stale rule). The rerun-or-accept bullet in 02-discipline adds "to cover a producer, name it", but says nothing about order. **Fix:** add protect-and-completion.md to 02-discipline. In it and in rerun-or-accept.md, have the agent accept the steps the rule says to accept before building the rest, or build with `--only`.
3. **[BLOCKING] [01-cli](01-cli/task.md) leaves the default `status` contract unspecified where the engine needs it.** §Details says the flip happens at the CLI layer. The parent's default output and exit codes need more than that:
   - **`selected` must split from the assessed set.** `compute_status` sets `selected` to the whole resolved scope, ancestors included ([_repro_state.py:802-815](../../../skills/task-tree/scripts/_repro_state.py#L802-L815)). `reported`, `ok`, and `to_dict` all read from `selected` ([:734-777](../../../skills/task-tree/scripts/_repro_state.py#L734-L777)). Printing one line per selected step needs `selected` to hold only the targets' steps.
   - **The exit code needs `local_status`.** Exit 1 vs 3 must depend on the selected steps' `local_status`. Today it depends on `report.ok`, and in upstream mode that reads every assessed step ([repro_run.py:780](../../../skills/task-tree/scripts/repro_run.py#L780)).
   - **Default-mode JSON is unspecified.** Text output elides producers and points to `--json`, so the JSON must list them. Only `--only` mode gets `behind`, so the tree must say where producers go in default mode, how a reader tells a selected step from a producer, and what `ok` and `summary` count. If `selected` is simply narrowed, `to_dict` drops the producers, and the pointer leads nowhere.

   **Fix:** state the StatusReport change and the default-mode JSON shape in 01-cli §Details, and add a §Validation test for that JSON.
4. **[ADVISORY] Call sites missing from the two child tasks:**
   - [docs/site/.../04-dashboard/task.md:26](../../../docs/site/04-utility-skills/01-task-tree/04-dashboard/task.md#L26) describes the Build menu as "with its upstream producers, or a forced rerun of all of them". It contains no `--upstream`, so 02-discipline's grep won't find it.
   - The `MODEL` help text at [repro_run.py:479](../../../skills/task-tree/scripts/repro_run.py#L479) says targets scope every command and that out-of-scope files are saved inputs.
   - The dashboard estimate counts every step in scope under force ([dashboard.js:2316](../../../skills/task-tree/scripts/templates/dashboard.js#L2316)). Its scope helper `reproBuildScope` and the `POST /api/repro/build` body (`upstream`, with no `only` field) also follow the old modes. 01-cli names only `_build_args` and the command string.
   - [task-file-contract.md:103](../../../skills/task-tree/references/task-file-contract.md#L103) shows the frontier hint with `--upstream`.
5. **[ADVISORY] The two fold lists disagree.** The Objective folds into 02-runner, 06-skill, 03-task-interface, and 04-dashboard-view. §At Mature lists 02, 04, 06, and 07-workflow-integration. [07-workflow-integration:30](../07-workflow-integration/task.md) states `status --upstream`, and 03-task-interface has no line about the scoped default. Use one list.
6. **[ADVISORY] Two smaller gaps.**
   - **Release notes.** The hidden alias changes the exit code of `status X --upstream` from 1 to 3 when only a producer is stale ([test_repro_engine.py:367](../../../skills/task-tree/scripts/test_repro_engine.py#L367), [test_repro_scope.py:64](../../../skills/task-tree/scripts/test_repro_scope.py#L64)). Note that in RELEASE-NOTES.
   - **Build preview.** Say whether the preview also prints under `--dry-run`, which already lists every step it would run. Also say whether "non-fresh" means a producer's own evidence or its cascaded status.
