---
title: Loop-Until-Dry Sweep Discipline
status: not-started
created: 2026-05-30
updated: 2026-05-30
depends_on: [02-domain-lenses]
---

# Loop-Until-Dry Sweep Discipline

## Objective

Two discovery sweeps in superRA currently run as a single pass; convergence-based iteration catches the tail a single pass misses. Add loop-until-dry discipline — keep sweeping until a round turns up nothing new — to each, in its owning skill. Load `skill-creator` first; apply DRY + Necessity (the repo's rule that a line stays only if no other file already carries it and removing it would change agent behavior) on every line.

Why: dynamic workflows use a loop-until-dry pattern for unknown-size discovery — keep sweeping until K consecutive rounds find nothing new, rather than assuming one pass is exhaustive. Discovery sweeps (stale references, consistency issues) have exactly that unknown-size property: fixing one item can reveal another, so a single pass systematically under-covers. Broader context in the parent task's `## Analysis` §4.

**1. `skills/semantic-merge/SKILL.md` — stale-reference sweep.** Where the skill specifies the stale-reference detect-and-resolve sweep, state that the sweep repeats until a round surfaces no new stale references (a clean round), not just once. Keep it to the convergence condition — do not restate the detection mechanics the skill already owns.

**2. `skills/writing/SKILL.md` — review mode.** In Review mode, state the same convergence condition for the consistency/issue sweep: repeat until a clean pass, rather than a single sweep. If `writing` already implies iteration, prefer a one-word tightening over a new paragraph; if it is already explicit, add nothing and record that in Results (DRY).

Depends on `02-domain-lenses` only to avoid colliding with that task's edit to `writing/SKILL.md`; the changes are otherwise independent.

## Validation

- Each sweep states an explicit convergence/termination condition (clean round), not an unbounded loop and not a fixed count.
- No detection or review mechanics restated (DRY against the owning skill's existing text).
- Confirm the loop has a stated stopping rule so it cannot be read as "sweep forever."
