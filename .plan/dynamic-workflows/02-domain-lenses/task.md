---
title: Expose Domain Gates as Review Lenses
status: not-started
created: 2026-05-30
updated: 2026-05-30
depends_on: [01-review-and-tier-patterns]
---

# Expose Domain Gates as Review Lenses

## Objective

The perspective-diverse review shape added in `01-review-and-tier-patterns` dispatches one reviewer per *lens*. Each domain skill already defines the lenses — they are its gates — but does not yet name them as the dispatchable lens set for parallel review. Make that explicit with a minimal pointer in each domain skill, so the orchestrator can read the lens set from the domain skill rather than inventing one.

Why: the perspective-diverse review shape only works if each lens is a genuinely distinct failure mode. The domain gates already *are* those failure modes (e.g. econ-data separates data-integrity from methodology-correctness from economic-plausibility); naming them as the lens set keeps one source of truth (domain discipline owned by the domain skill) instead of letting `agent-orchestration` invent a parallel list. Broader context in the parent task's `## Analysis` §4.

Scope, per domain skill (`skills/econ-data-analysis/SKILL.md`, `skills/theory-modeling/SKILL.md`, `skills/writing/SKILL.md`):
- Add at most a one-line label set that names the skill's existing gates as the review lenses (e.g. econ-data: data-integrity / methodology-correctness / economic-plausibility; theory: derivation-correctness / assumption-consistency / notation-rendering). Use the gate names the skill already uses — do not introduce new discipline.
- `writing` already runs per-dimension consistency reviewers; here only confirm/point that those dimensions ARE the lens set for the shared shape. If `writing` already says this clearly, add nothing (it would duplicate existing text — the DRY rule) and record that in Results.
- Do not copy the lens list into `agent-orchestration` — the shape there points to the domain skill (one source of truth: domain discipline is owned by the domain skill).

This is a pointer-only change. If exposing a domain's gates as lenses would require *new* discipline rather than relabeling existing gates, stop and flag it — that is a domain-skill design change beyond this task's scope.

## Validation

- Each touched domain skill names its lens set using only pre-existing gate vocabulary (no new gates introduced).
- No lens list duplicated between `agent-orchestration` and any domain skill.
- DRY + Necessity: any line that merely re-describes an existing gate without making it dispatchable-as-a-lens is removed.
