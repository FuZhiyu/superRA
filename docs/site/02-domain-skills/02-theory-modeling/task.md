---
title: "theory-modeling"
status: not-started
depends_on:  []
---

## Objective

`theory-modeling` makes the agent define every symbol and assumption before it manipulates equations, and verify each headline result before reporting it. It catches the two errors that read fine until a referee finds them: one symbol meaning two things, and an assumption back-filled after the algebra needed it.

## Work runs through four ordered gates

**Objects & Notation → Assumptions → Derivations → Verification & Rendering**. The reviewer checks in the same order.

- **What you read in the task's results:** the derivation, plus a notation ledger (each new symbol and its meaning) and an assumption ledger (each assumption with its plain-language reading).
- **Your project's canonical notation table stays yours.** The agent never edits it; a new symbol joins it only when you confirm.

## Ask for the output; steer notation and checks

Name the output — first-order conditions, an equilibrium, comparative statics, a proof check, renderable model notes.

> "Derive the first-order conditions for the household problem in §2, then verify them by substituting back into the budget constraint."

- **Point it at your existing notation** so a quantity keeps its name instead of picking up a second one.
- **Name the check you trust** — substituting back, a limiting case, a numerical example, or a benchmark the result must match.

For the gate checklists, ledger tests, the planning-stage Model Inventory, and the integration-stage readability pass, see [theory-modeling](skills/theory-modeling/SKILL.md).
