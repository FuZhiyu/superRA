---
title: "theory-modeling"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Hand a derivation to a bare agent and it invents notation as it goes: it names a load-bearing quantity like expected returns with a throwaway $A$ or $B$, then reuses that symbol for something else a few lines down. Or a "by symmetry" step quietly needs an interior solution that was never assumed, so the agent back-fills the assumption to rescue the algebra. The result type-checks and reads right, so the error survives until a referee finds it. `theory-modeling` prevents both: one symbol meaning two things, and assumptions invented after the algebra needs them.

It works by forcing a fixed order — **Objects & Notation → Assumptions → Derivations → Verification** — because that is the order trust depends on. You cannot judge an assumption resting on an undefined symbol, trust a derivation without knowing which assumptions are live in it, or accept a verification over a derivation you cannot audit. So the agent pins down its symbols, fixes its assumptions, then manipulates equations, with verification last; the reviewer reads it back in the same order.

## How to ask for it

Say what the output is — first-order conditions, an equilibrium, comparative statics, a proof check, renderable model notes — and the discipline triggers on its own. You do not configure the gates or name the skill.

> "Derive the first-order conditions for the household problem in §2, then verify them by substituting back into the budget constraint."

Two requests are worth making explicitly, because they steer the two failures the skill exists to catch. Tell the agent to **reuse the project's existing notation** rather than coin fresh symbols, so a quantity you have already named keeps its name across the derivation instead of picking up a second one. And tell it to **verify the result before reporting it** — substitute back, take a limiting case, or check a numerical example — so a clean-looking derivation that does not actually satisfy the original conditions gets caught before you build on it.

For the gate checklists, the per-symbol notation ledger, the substitution and proof-deletion tests, the planning-stage Model Inventory, and the integration-stage readability layer, see [theory-modeling](skills/theory-modeling/SKILL.md).
