---
title: "Wire the Graph into the PLAN / IMPLEMENT / INTEGRATE Workflow"
status: approved
depends_on: [06-skill]
---

## Objective

Replace the linear "pipeline file" requirement with the reproduction graph across the workflow skills, and register the new skill in every inventory, without restating what [06-skill](../06-skill/task.md) owns.

- `superplan/references/build-and-review.md`: the artifact pipeline is planned as `## Reproduction` sections (the planner seeds expected outs; implementers fill deps); self-review item 3 checks the graph, not a pipeline file.
- `econ-data-analysis/references/planning.md` §Pipeline File and `theory-modeling/references/planning.md` item 5: delete the duplicated requirement, point to the skill.
- `superimplement/references/completion.md` §3 and `superimplement/SKILL.md` blocker wording: reproducibility verification is `repro build --tier canon` followed by a clean `repro status`.
- `superintegrate/references/protect.md`: configuring reproduction is a Protect step (tier per affected task, check steps for selected drift tests, boundary inputs), recorded in the `integrate(protect)` commit; `integrate.md` step 1 and 8 and `finish.md` step 2 run the graph as part of the protection suite; `mature-consolidate.md` moves `## Reproduction` sections with folds and never drops a canon step.
- `result-protection/SKILL.md`: graph coverage plus the committed lock is a listed protection mechanism.
- `implement-task/SKILL.md`: one duty line for registering or updating steps when a task adds or changes a producer.
- `using-superra/SKILL.md`: the `protection` Stage row also loads `reproducibility`; §Task Interface gains one line: a tree with reproduction config loads `superRA:reproducibility` before producing a maintained output. Update `tests/harness-instruction-following/test_contract.py` and `load_contract.json` for the new stage load.
- `skills/CATEGORIES.md`, `README.md`, and the `CLAUDE.md` ownership table (mechanics → `task-tree`, discipline → `reproducibility`).
- **Validation criteria:** every edited line passes the three-test gate; `grep -rn "pipeline file" skills/` returns only pointers; the harness contract tests pass; one live smoke of the protection stage load.

## Details

- Touch points were verified by grep on 2026-09-02 and listed in the parent task's `## Details`.
- `academic-writing/references/consistency/code-paper.md` line 22 mentions a pipeline file as a mapping source; make it name the graph instead.

## Results

`grep -rn "pipeline file"` now returns nothing across `skills/`, `tests/`, `README.md`, and `CLAUDE.md` — not even a pointer, because every site either names the graph or dropped the clause. The graph is the reproducibility mechanism at all three phases, and `reproducibility` is a listed skill in the manifest, the categories index, and the ownership table.

### Each phase names the graph

- **PLAN** — [build-and-review.md:13](../../../skills/superplan/references/build-and-review.md#L13) replaces the pipeline-file paragraph with the planner/implementer split (planner seeds `outs`, implementer fills `deps`); [self-review item 3](../../../skills/superplan/references/build-and-review.md#L52) checks that coverage instead of dependency order, which the graph now infers from files. The duplicated requirement in [econ-data-analysis/references/planning.md:75](../../../skills/econ-data-analysis/references/planning.md#L75) and [theory-modeling/references/planning.md:130](../../../skills/theory-modeling/references/planning.md#L130) is deleted down to a one-line pointer, taking the `run_all.sh` sample with it.
- **IMPLEMENT** — [completion.md:18](../../../skills/superimplement/references/completion.md#L18) runs `superra repro build --tier canon` then a clean `superra repro status --tier canon`, routing failures to the skill's completion gate rather than re-deriving it. [implement-task:29](../../../skills/implement-task/SKILL.md#L29) carries the duty line, adding the one thing no upstream file states: the section edit lands in the same commit as the producer change.
- **INTEGRATE** — [protect.md:5](../../../skills/superintegrate/references/protect.md#L5) loads the skill and [step 2](../../../skills/superintegrate/references/protect.md#L15) folds the reproduction decisions into the researcher proposal. [integrate.md:9](../../../skills/superintegrate/references/integrate.md#L9) puts the build and status check inside the protection suite, and [finish.md:39](../../../skills/superintegrate/references/finish.md#L39) runs the same two commands on the final tree, keeping targeted verification as the route for a tree that declares no graph. Both sites point at `protect-and-completion.md` §The completion gate, as [completion.md:18](../../../skills/superimplement/references/completion.md#L18) already did, so the command pair has one authority across all three. [mature-consolidate.md:29-31](../../../skills/superintegrate/references/mature-consolidate.md#L29-L31) tells the maturation drafter that a fold moves `## Reproduction` steps into the target and never drops a canon step.

### Registration and the protection-stage load

[using-superra:48](../../../skills/using-superra/SKILL.md#L48) adds `reproducibility` to the `protection` Stage row, and [:30](../../../skills/using-superra/SKILL.md#L30) adds the §Task Interface load trigger, keyed on a `reproduction:` key in `superRA/config.yaml`. [result-protection](../../../skills/result-protection/SKILL.md#L8) lists a registered step plus its committed lock as a protection mechanism, and [code-paper.md:22](../../../skills/academic-writing/references/consistency/code-paper.md#L22) names the graph as the paper-to-code mapping source. Inventories: [CATEGORIES.md](../../../skills/CATEGORIES.md#L52), [README.md:14](../../../README.md#L14), and two [CLAUDE.md](../../../CLAUDE.md#L88-L89) ownership rows splitting discipline (`reproducibility`) from mechanics (`task-tree`).

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
