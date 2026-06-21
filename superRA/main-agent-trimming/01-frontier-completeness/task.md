---
title: "Frontier Completeness: Should task frontier Surface implemented/revise?"
status: implemented
depends_on: []
tags: []
created: 2026-06-21
---

## Objective

Decide — and implement the outcome — whether `superra task frontier` should surface the actionable in-flight states `implemented` (awaiting review) and `revise` (awaiting a fix), so that "run the frontier and execute what's on the table" is the *complete* resume loop rather than only the "ready for new implementation" slice.

**Current behavior:** `compute_frontier` (`skills/task-tree/scripts/_task_io.py:851`, helper `_collect_frontier`) appends a leaf only when its status is `not-started` or `in-progress` (deps met, not parked). `implemented` and `revise` tasks are off the frontier; today the orchestrator drives those by reading `status` directly against the table in `agent-orchestration/SKILL.md` §Review Status Reference.

**Resolve the design question:**

- Either (a) extend the frontier so it reports each leaf's *actionable next role* (e.g. `implemented` → review, `revise` → fix), making `task frontier` the single "what needs doing now" surface — likely a labelled/annotated frontier rather than a flat list, so callers can tell implement-work from review-work; or
- (b) keep the frontier as "ready for implementation" by design and document why, so the resume prose in the sibling rewrite leans on the status table for the review/revise half rather than implying the frontier covers it.

Pick the option that makes the resume model in [../02-resuming-work-rewrite](../02-resuming-work-rewrite/task.md) honest and minimal. Do not over-build: if (a), the smallest change that lets a resumer see review/fix work without re-reading every task file.

**Success:**

- A clear decision recorded in `## Results` with the rationale.
- If (a): `compute_frontier` (and its CLI/JSON output) updated, with `skills/task-tree/scripts/test_task_tree.py` cases covering `implemented` and `revise` leaves; existing frontier tests still green. Run `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts -k frontier`.
- If (b): a short rationale comment at the `compute_frontier` docstring and the decision captured for the rewrite task to cite.

## Planner Guidance

The frontmatter status enum and lifecycle are owned by `task-tree/references/task-file-contract.md` §status; the orchestrator-facing status→action mapping is owned by `agent-orchestration/SKILL.md` §Review Status Reference. Whatever this task decides must stay consistent with both — change them in the same pass if the decision shifts their content.

## Results

**Decision: option (a) — broaden the frontier to all actionable leaf statuses.**

The exclusion of `implemented`/`revise` was deliberate and tested ([test_task_tree.py](../../../skills/task-tree/scripts/test_task_tree.py) `test_revise_status_excluded_from_frontier`), but it contradicted `compute_frontier`'s own stated purpose — "leaf tasks ready to be worked on": a `revise` task is ready to be worked on by an implementer, an `implemented` task by a reviewer. Excluding them meant `task frontier` printed "No tasks on the frontier" while tasks sat awaiting review, so resuming required `frontier` *plus* a manual status scan — the exact friction the Resuming Work model removes.

**Scope/blast radius:** `compute_frontier` has a single consumer — the `task frontier` CLI (`task_query.py`). The dashboard/server does **not** call it (grep-confirmed), so broadening only affects that command + tests.

**Change (minimal):**
- [`_task_io.py`](../../../skills/task-tree/scripts/_task_io.py) `_collect_frontier`: leaf-inclusion set widened from `("not-started","in-progress")` to `_ACTIONABLE_STATUSES = ("not-started","in-progress","implemented","revise")`. Dependency-satisfaction is **unchanged** (`approved`/`archived` only), so dependents of unreviewed work correctly stay blocked. Docstring + a named constant document the semantics. The frontier output and JSON already carry per-task `status`, so the caller reads the next action (implement / review / fix) from it — no output-shape change.
- [`task_query.py`](../../../skills/task-tree/scripts/task_query.py): empty-frontier message corrected to "No tasks on the frontier (all approved, blocked, or parked)."
- [`test_task_tree.py`](../../../skills/task-tree/scripts/test_task_tree.py): the revise-exclusion test replaced by `test_revise_and_implemented_on_frontier`, asserting both states appear *and* that a non-`approved` dependency still blocks its dependents.

**Consistency:** no change to the status enum (`task-file-contract` §status) or the status→action map (`agent-orchestration` §Review Status Reference); this only makes `task frontier` surface the tasks those owners already describe. The `task-tree/SKILL.md` "dispatchable leaf tasks" wording stays accurate.

**Verification:** `pytest -k frontier` → 13 passed; full `skills/task-tree/scripts` suite → 698 passed, 2 skipped (pre-existing warnings only).
