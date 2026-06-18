---
title: "theory-modeling"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Hand a derivation to a bare agent and it invents notation as it goes: $\lambda$ is a Lagrange multiplier halfway down and a risk-aversion coefficient near the bottom, same glyph and no flag. Or a "by symmetry" step quietly needs an interior solution that was never assumed, so the agent back-fills the assumption to rescue the algebra. The result type-checks and reads right, so the error survives until a referee finds it. `theory-modeling` prevents both: one symbol meaning two things, and assumptions invented after the algebra needs them.

It works by forcing a fixed order — **Objects & Notation → Assumptions → Derivations → Verification** — because that is the order trust depends on. You cannot judge an assumption resting on an undefined symbol, trust a derivation without knowing which assumptions are live in it, or accept a verification over a derivation you cannot audit. So the agent pins down its symbols, fixes its assumptions, then manipulates equations, with verification last; the reviewer reads it back in the same order.

## How to ask for it

Say what the output is — first-order conditions, an equilibrium, comparative statics, a proof check, renderable model notes. That triggers the discipline; you do not configure the gates. Two patterns are worth asking for explicitly: tell the agent to reuse the project's existing notation rather than name fresh symbols, and tell it to verify the result before reporting it.

> Load `theory-modeling` and derive the firm's first-order conditions for §2, reusing the notation already in the model inventory, and verify with a numerical example.

For the gate checklists, per-symbol ledger format, the substitution and proof-deletion tests, the planning-stage Model Inventory, and the integration-stage readability layer, see [theory-modeling](skills/theory-modeling/SKILL.md).
