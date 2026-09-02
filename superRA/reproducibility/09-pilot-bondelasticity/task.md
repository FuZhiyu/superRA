---
title: "Pilot: Migrate the BondElasticity Snakefile to the Graph"
status: postponed
depends_on: [08-pilot-treasurygiv]
---

## Objective

Port the ten-rule Snakefile in `/Users/zhiyufu/Dropbox/BondElasticity-Reproduction` into `## Reproduction` sections and make `reproduce.sh` call `superra repro build` instead of Snakemake, keeping the 14 manuscript outputs byte-identical to the current build.

- One step per rule, owners chosen by the `.plan/` task that produced each script (fallback: the repo's root task); the two ex-frozen artifacts stay external inputs; the seven `tests/drift/test_*.sh` register as `check` steps.
- The interpreter pin (`julia +1.10.5`) lives once, in the `superRA/config.yaml` runner template.
- **Verification:** clean-room build on the synthetic package reproduces all 14 outputs; drift tests pass; `--dry-run` after a no-op edit schedules nothing.
- Postponed until [08-pilot-treasurygiv](../08-pilot-treasurygiv/task.md) lands; the repo is on a legacy `.plan/` tree and may need `task migrate` first.

## Results
