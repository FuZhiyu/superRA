---
title: "Wire the Graph into the PLAN / IMPLEMENT / INTEGRATE Workflow"
status: not-started
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
