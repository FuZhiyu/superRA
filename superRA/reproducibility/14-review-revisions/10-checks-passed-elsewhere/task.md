---
title: "Checks: A Check That Passed at These Inputs Elsewhere Reads Fresh"
status: not-started
depends_on: [01-engine-freshness]
---

## Objective

A coauthor's fresh clone reports a check `fresh` when the committed lock shows it passed at exactly the current inputs, so `status .` no longer exits 1 until every check reruns locally. The check still says it did not run on this machine.

- **Fresh on the lock's word.** A check step whose lock entry matches its current spec and deps, and whose only difference is the missing machine-local stamp, is `fresh`. Its reason stays `passed at these inputs in lock <rev> on <platform>; not run here`, the text [check_elsewhere_reason](../../../../skills/task-tree/scripts/_repro_provenance.py#L153-L158) writes today.
- **Local evidence wins.** A failed, running, or pending run of that check on this machine keeps it `failed`, since a check can depend on the machine. `--force` still reruns it, and a spec or dep change still makes it stale.
- **`build` skips it**, because `build` and `status` share one rule; `build --force` or a changed input reruns it.
- **Docs follow:** the state table in [commands.md](../../../../skills/task-tree/references/commands.md) §Reproduction and the matching row of [diagnosing.md](../../../reproducibility/references/diagnosing.md) §Read what explain names. The row keeps a rerun as the act when this machine's result is what gets reported. [07](../07-instruction-rewrite/task.md) still owns the gate rewrite.
- **Tests:** the two-clone fixture's check reads `fresh` with the reason above, and `status .` exits 0 there. A check that failed locally at the lock's inputs reads `failed`; `build` skips a check passed elsewhere, and `--force` runs it.

Owning task: [02-runner](../../02-runner/task.md).

## Details

- **Why the stamp stays local.** [02](../02-portable-records/task.md) stops stamps crossing machines, so a synced stamp cannot claim "ran here". This task makes the lock, not a borrowed stamp, the portable evidence that a check passed.
- **Acceptance is unchanged.** Accepting a check still requires its local stamp, so a check passed only elsewhere must run here before it can be accepted.
