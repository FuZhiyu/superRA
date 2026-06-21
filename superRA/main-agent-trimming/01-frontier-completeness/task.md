---
title: "Frontier Completeness: Should task frontier Surface implemented/revise?"
status: not-started
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
