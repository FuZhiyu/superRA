---
title: "CLI Decision Support: One-Shot Accept, Cost and Role in Output, No Legacy Surface"
status: approved
depends_on: []
---

## Objective

Make `superra repro` cheap to use correctly: an agent facing a stale step sees why it is stale, what a rebuild would cost, and who consumes it, and can accept in one call. The command surface describes only the current v0.5 design.

- **One-shot accept.** `repro accept <targets> --reason …` applies atomically in one call, running the existing consistency checks inside it, and prints exactly what it accepted. `--dry-run` previews. The token form remains only for a deliberately separated preview and apply.
- **Cost in the preview.** `build --dry-run` reports each step it would execute with its last recorded duration and the total, marks unknown durations as unknown, and on a nonzero total names `explain` and `accept` as the alternatives.
- **Role in the output.** `status` and `explain` show whether consumers outside the owning task read the step's outs, the input for the significance inference in the [group decisions](../task.md#decisions-researcher-2026-09-20).
- **Help that teaches.** Each `repro` subcommand's `--help` carries a one-line purpose and worked examples; `superra repro --help` states the model in a few lines (steps belong to tasks, freshness is a content-hash comparison with the last build or acceptance, target scope and saved inputs, execute or accept), worded consistently with the skill's model section.
- **Legacy deleted.** Remove `--tier`, `repro tier`, `--force-all`, the `tier:` key handling, legacy bare step names, and acceptance records without `basis`, with their tests and every mention in [commands.md](../../../../skills/task-tree/references/commands.md#reproduction) and the [task-file contract](../../../../skills/task-tree/references/task-file-contract.md#reproduction-section). Move the dashboard paragraph out of commands.md §Reproduction to its owning section.
- **Validation:** runner fixtures cover one-shot accept (success, concurrent edit rejected, never-run check rejected), the dry-run cost report with known and unknown durations, and the outside-consumer flag; the full task-tree suite passes; commands.md and the contract match the shipped flags.

## Details

- Entry points: [repro_run.py](../../../../skills/task-tree/scripts/repro_run.py), [_repro_acceptance.py](../../../../skills/task-tree/scripts/_repro_acceptance.py), [_repro_state.py](../../../../skills/task-tree/scripts/_repro_state.py) (durations already surface at lines 822 and 871), [_repro_scope.py](../../../../skills/task-tree/scripts/_repro_scope.py).
- TreasuryGIV's `reproduction-graph` branch still carries `tier:` keys and old acceptance records; it needs a one-time manual fix once the legacy paths are gone. Report the exact breakage in `## Results`.
- Load `superRA:task-tree` for every edit under `skills/task-tree/`.

## Results

`superra repro` now answers the three questions a stale step raises — why, what a rerun costs, who reads the outs — and accepts in one call. The v0.5 surface carries no retired flag, key, or record shape.

### The four decision-support changes

- **One-shot accept is the default.** `repro accept <targets> --reason '…'` previews, revalidates, and writes the ledger inside one `mutation_lock`, then prints the steps it covered and what changed under each ([_repro_acceptance.py:372](../../../../skills/task-tree/scripts/_repro_acceptance.py#L372), [repro_run.py:447](../../../../skills/task-tree/scripts/repro_run.py#L447)). `--dry-run` previews and prints a token; `--apply <token>` accepts exactly that preview. Every guard the split form ran — source signature, run outcome, evidence bytes, re-preview token equality — runs inside the one-shot call.
- **`build --dry-run` reports cost.** Steps pytask marks `WouldBeExecuted` are listed with their last recorded duration, `unknown` when never run, then the `explain` / `accept` alternatives ([repro_run.py:421](../../../../skills/task-tree/scripts/repro_run.py#L421)). The total prints only when at least one duration is known, so an all-unknown scope reads `No step has a recorded duration` rather than a `0.0s` that looks free. A fully fresh scope prints `Nothing to execute`.
- **Outside readers are a fact in `status` and `explain`, not a verdict.** `status` prints `outside readers: N` — how many steps in other tasks read the step's outs — `explain` names them or states that none does, and status JSON exposes `external_consumers` ([_repro_state.py:565](../../../../skills/task-tree/scripts/_repro_state.py#L565)). The count is one input to the significance inference in the [group decisions](../task.md#decisions-researcher-2026-09-20); the CLI never labels a step task-local, because a selected check, a maintained-path producer, and an out a document cites are all significant at zero outside readers.
- **`--help` teaches.** `superra repro --help` states the model in six lines, naming pytask 0.6 as the engine; each subcommand carries a purpose line and worked examples.

### Legacy deleted

`--tier`, `repro tier`, `--force-all`, the `tier:` section key, bare step-name targets, and acceptance records without `basis` are gone with their tests. Two behaviors changed for callers:

- A bare step name is now rejected with its qualified form (`'build-a' is a step name, not a target; select it as '01-a#build-a'`) instead of resolving when unambiguous.
- `basis: reviewed` and a list `boundary_inputs` are required ledger fields, so `read_ledger` rejects a pre-`basis` record rather than applying the old successful-output-equality rule. That made the whole legacy branch in `apply_to_status` dead, and it is removed.

### TreasuryGIV `reproduction-graph` needs 21 deleted lines

All 21 `## Reproduction` sections on that branch carry a `tier:` key. Each now raises `[ERROR] ## Reproduction: unknown key 'tier'; expected one of ['steps']`, which fails `task check` and makes `repro build` exit 1 before selecting anything.

The fix is deleting the `tier:` line from each section — `git grep -l '^tier:' -- 'superRA/**/task.md' | xargs sed -i '' '/^tier: /d'`. Nothing else breaks: `tier` never entered the step spec hash ([spec_hashes](../../../../skills/task-tree/scripts/_repro_state.py#L320) covers `cmd`/`kind`/`params`/`deps`/`outs`/`sidecars`), so the committed `pytask.lock` and every step's freshness survive the edit. The branch commits no `repro-acceptance.json`, so no acceptance record needs migrating.

### Validation

Full task-tree suite passes. New fixtures: one-shot accept success with its printed output, concurrent declaration edit rejected, never-run check rejected, dry-run cost with known durations and with none at all, and the outside-reader count across JSON, `status`, and `explain` — the `status` case also asserts neither verdict word reaches the output ([test_repro_acceptance.py](../../../../skills/task-tree/scripts/test_repro_acceptance.py), [test_repro_runner.py](../../../../skills/task-tree/scripts/test_repro_runner.py)).

The dashboard UI paragraph moved from commands.md §Reproduction into [internals.md §Dashboard](../../../../skills/task-tree/references/internals.md), merged with the Task DAG navigator paragraph that already stated its overlapping half.

Four docs outside the two the objective named held stale invocations — three `reproducibility` files with a bare `<step>` placeholder or the token-only acceptance recipe, and the [CLI-commands docs page](../../../../docs/site/04-utility-skills/01-task-tree/02-cli-commands/task.md). All are corrected to `'<task>#<step>'` and the one-shot form. `03-skill-redesign` owns any further rewrite of the skill.
