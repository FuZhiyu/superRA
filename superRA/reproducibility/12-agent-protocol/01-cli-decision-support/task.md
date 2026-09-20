---
title: "CLI Decision Support: One-Shot Accept, Cost and Role in Output, No Legacy Surface"
status: not-started
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
