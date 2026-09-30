---
title: "Wire the Graph into the PLAN / IMPLEMENT / INTEGRATE Workflow"
status: approved
depends_on:
  - 01-section-contract
  - 02-runner
  - 06-skill
---

## Objective

Keep reproduction integrated into planning, implementation, protection, and completion through the owning skills and public guidance. Complete the [0.5 workflow update](unified-dependency-workflow/task.md) without duplicating the graph/runner mechanics.

- Planning uses one effective dependency model and declares expected maintained outputs; implementation fills actual inputs and producers. Workflow readers consume authoritative task tooling rather than rebuilding dependency logic in prose.
- Protection and completion cover required kept results and selected checks, with targeted verification for on-demand claims and reviewed acceptance treated as fresh under the [0.5 design](../attachments/v05-design.md).
- Maturation preserves reproduction ownership, logical identities, and evidence when tasks are folded or moved. Task hierarchy may contain both own steps and child tasks.
- Keep skill inventories, harness load contracts, README, and relevant docs-site sources consistent. Verify edited instruction paths with realistic harness or script-level evidence.

## Details

- Touch points were verified by grep on 2026-09-02 and listed in the parent task's `## Details`.
- `academic-writing/references/consistency/code-paper.md` line 22 mentions a pipeline file as a mapping source; make it name the graph instead.

## Results

`grep -rn "pipeline file"` now returns nothing across `skills/`, `tests/`, `README.md`, and `CLAUDE.md` — not even a pointer, because every site either names the graph or dropped the clause. The graph is the reproducibility mechanism at all three phases, and `reproducibility` is a listed skill in the manifest, the categories index, and the ownership table.

### Each phase names the graph

The call sites below are as [08-workflow-wiring](../14-review-revisions/08-workflow-wiring/task.md) left them; each points to the `reproducibility` reference that owns its rule.

- **PLAN** — [build-and-review.md:13](../../../skills/superplan/references/build-and-review.md#L13) has the planner name each artifact and its planned script in the producing task's `## Details`; the implementer registers the step. Self-review item 3 checks that each artifact is named. [econ-data-analysis/references/planning.md](../../../skills/econ-data-analysis/references/planning.md) and [theory-modeling/references/planning.md](../../../skills/theory-modeling/references/planning.md) keep a one-line pointer, taking the `run_all.sh` sample with them.
- **IMPLEMENT** — [completion.md:18](../../../skills/superimplement/references/completion.md#L18) points to [§The completion gate](../../../skills/reproducibility/references/protect-and-completion.md#the-completion-gate): `status .`, the stale rule, then `status .` again. [implement-task](../../../skills/implement-task/SKILL.md) Self-Check 4 points to the claim gate in `claiming-results.md`.
- **INTEGRATE** — [protect.md:15](../../../skills/superintegrate/references/protect.md#L15) asks the researcher which inputs are external. [integrate.md:9](../../../skills/superintegrate/references/integrate.md#L9) puts the completion gate in the protection suite, and [finish.md:39](../../../skills/superintegrate/references/finish.md#L39) runs it on the final tree; both point to the same section. [mature-consolidate.md:30](../../../skills/superintegrate/references/mature-consolidate.md#L30) has the maturation drafter move or retire steps per §Step lifecycle.

### Registration and the protection-stage load

[using-superra](../../../skills/using-superra/SKILL.md#stage) lists `reproducibility` in the `protection` Stage row and in a Domain row for any task that plans, produces, changes, records, or reviews a result computed by code. [result-protection](../../../skills/result-protection/SKILL.md#L8) counts drift tests registered as check steps as protection, and [code-paper.md:22](../../../skills/academic-writing/references/consistency/code-paper.md#L22) names the graph as the paper-to-code mapping source. Inventories: [CATEGORIES.md](../../../skills/CATEGORIES.md), [README.md:14](../../../README.md#L14), and two [CLAUDE.md](../../../CLAUDE.md) ownership rows splitting discipline (`reproducibility`) from mechanics (`task-tree`).

### Deviations

- **The stage-load table and its unit fixtures were edited beyond the two test files the objective names.** `test_contract.py` and `load_contract.json` alone would leave [stage_loads_live.py](../../../tests/harness-instruction-following/stage_loads_live.py#L106) asserting a `protection` row of `("result-protection",)` — exactly the manifest drift its own test exists to catch. `STAGE_ROWS`, [test_stage_loads_live.py](../../../tests/harness-instruction-following/test_stage_loads_live.py#L74), and the [tests README](../../../tests/harness-instruction-following/README.md#L96) move with the manifest.
- **`integrate.md` step 8 is unchanged.** It says "Run the protection suite again"; step 1 defines that suite, so the graph reaches step 8 without a second copy of the commands.
- **`CLAUDE.md` §Agent Load Surface needed a correction this change caused.** Its claim that subagents never load `task-file-contract.md` outside maturation stops holding once implementers register steps, since `reproducibility` routes there for the section schema.

### Verification

| Check | Result |
|---|---|
| `grep -rn "pipeline file" skills/ tests/ README.md CLAUDE.md` | no matches |
| `uv run --with pytest python -m pytest tests/harness-instruction-following -q` | 125 passed, 1 failed |
| `uv run --with pytest … python -m pytest skills/task-tree/scripts -q` | 967 passed, 30 skipped |

The harness failure is `test_contract.py::test_task_companion_contract_has_one_canonical_route`, which fails identically at this task's base (`5e24398e`): commit `6d8dbb74` reworked [skills/communicate/SKILL.md](../../../skills/communicate/SKILL.md) and dropped the `using-superra/references/task-companion-files.md` mention the test asserts. Unrelated to this task and left alone.

### Notes

- **The live smoke of the protection stage load did not run.** `stage_loads_live.py` needs `RUN_LIVE_HARNESS=1` and a live Claude SDK dispatch, which a dispatched session cannot provide. `LC008`'s `notes` field records that the `reproducibility` half of the row is not live-verified yet.
- **All fifteen `skills/using-superra/SKILL.md#L…` anchors in [load_contract.json](../../../tests/harness-instruction-following/load_contract.json) now point at current lines** — LC001–LC004, LC007–LC016, LC023, and static finding SF002. Most pointed past that file's 64 lines and had been stale since before this task. Nothing reads them, so the sweep is documentation correctness: they are how a reader finds the manifest text an entry audits.

## Review Notes

Re-review of six advisory findings: four resolved (one moot on merge, two implemented and verified, one a documentation sweep verified against the file). Two remain, both deferred for reasons outside this task's seat rather than left undone.

1. **[ADVISORY]** The objective's live-smoke criterion is unmet and needs a seat that can produce it. `## Results` §Notes discloses this; the per-stage suite is classified `manual_live_claude` and dispatches against an installed plugin, so it cannot verify a manifest row that exists only on this branch. Fix: run it after merge-back, then drop the `reproducibility`-not-yet-verified caveat from `LC008.covered_by.notes` in [load_contract.json:242](../../../tests/harness-instruction-following/load_contract.json#L242).
   → not implemented: out of scope for this round — the smoke needs an interactive harness with `RUN_LIVE_HARNESS=1` and an installed plugin, which a dispatched session cannot provide. The `LC008.covered_by.notes` caveat stands until it runs.

2. **[ADVISORY]** [docs/site/04-utility-skills/task.md](../../../docs/site/04-utility-skills/task.md) still lists eight utility skills and omits `reproducibility`, while [README.md:14](../../../README.md#L14) now advertises the capability to the same reader. Outside the inventories `CLAUDE.md` §Skill Authoring Guidelines mandates, so this is a divergence to schedule rather than a gap in this task.
   → not implemented: out of scope for this round — the docs-site workstream is postponed, so the utility-skill inventory page waits for it.
