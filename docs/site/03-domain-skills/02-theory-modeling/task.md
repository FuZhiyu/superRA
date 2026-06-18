---
title: "theory-modeling"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Hand a portfolio-choice problem to a bare agent and you get back three pages of clean-looking algebra. When you read it, halfway down $\lambda$ is the Lagrange multiplier on the budget constraint; near the bottom $\lambda$ is a risk-aversion coefficient — same glyph, two objects, no flag. A "by symmetry" step quietly needs an interior solution that was never assumed. The algebra type-checks and the conclusion looks right, so the error survives until a referee catches it. `theory-modeling` exists to prevent this failure: an agent inventing notation as it goes and letting one symbol mean two things, or back-filling an assumption after the algebra needs it.

The fix is a fixed order of work. The skill runs work through four gates in sequence — **Objects & Notation → Assumptions → Derivations → Verification & Rendering** — and the order itself does the work. You cannot judge an assumption that rests on an undefined symbol, cannot trust a derivation without knowing which assumptions are live in it, and cannot accept a verification claim over a derivation you cannot audit. So the agent pins down its objects, fixes its assumptions, and only then manipulates equations, with verification last; the reviewer reads it back in the same order. Notation is fixed once set — no renaming an object mid-derivation without an explicit old-to-new mapping — and restrictions live on primitives, stated up front, never back-filled.

## How to invoke it

Load it the moment a task derives, solves, proves, or verifies something — first-order conditions, an equilibrium, comparative statics, a proof check, or renderable model notes — and say what the output is. That is enough to trigger the discipline; you do not configure the gates.

- "Load `theory-modeling` and derive the firm's first-order conditions for the problem in §2, with the per-symbol ledger."
- "Check this proof of uniqueness with `theory-modeling` — run the substitution and proof-deletion tests on every symbol and flag any assumption back-filled after the algebra."
- "Sign the comparative static $\partial p / \partial k$ under `theory-modeling`; state what is held fixed and verify with a numerical example."
- "Solve for the recursive competitive equilibrium under `theory-modeling` and verify the policy."

## What each gate forces

**Gate 1 — Objects & Notation.** Every new symbol gets a ledger entry in the task's `## Results` *before* it appears in proof text: its type and space, what it denotes in already-defined terms, and how it is constructed if derived. Indexed families count as one object; five symbols sharing a proof passage are five entries. The agent must name the nearest existing symbol it considered — from the project's canonical Notation Conventions table, the active lemma, or an upstream step — and say why it did not reuse it, so a fresh name has to defend itself against one already in scope. Placeholder labels like `A/B/C` or `T1/T2` are blocking. This gate prevents "one symbol, two meanings."

**Gate 2 — Assumptions.** Each assumption attaches to a primitive (preferences, technology, endowments, information, timing, a distribution, a parameter domain), carries a one-sentence plain-language reading a researcher can defend, and names the specific conclusion that changes "without this assumption." An assumption stated as a desired property of an endogenous object is blocking unless that property is later proved — which is what stops the agent from back-filling "assume the solution is interior" to make a step go through. When several weak technical restrictions can be replaced by one stronger interpretable primitive, the synthesis is preferred.

**Gate 3 — Derivations.** The solution concept and the one-sentence proof goal are stated before the first displayed equation. Each step is one logical move (no three substitutions collapsed into "therefore"), carries both its rule (envelope theorem, market clearing, differentiate w.r.t. $k$) and a reason for invoking it here, and cites dependencies by name or equation number. Case splits state the active branch and dispatch the excluded ones; comparative statics state what is held fixed and what sign is claimed; existence, uniqueness, and monotonicity are argued, not asserted by inspection.

**Gate 4 — Verification & Rendering.** Every headline result survives at least one independent check — substitute back into the original conditions, take a limiting case, or evaluate a numerical example with stated parameters and a pass condition. Limiting cases are interpreted economically ("at $\beta \to 0$ the policy reduces to the myopic rule"), not just confirmed numerically. If a step quietly needed a stronger restriction than the assumption map states, the map is updated before the result is used. When a CAS or solver is involved, the rendered math must match the computed object exactly; rendered output goes through `report-in-markdown`.

Two reviewer diagnostics back the Gate 1 and Gate 2 ledgers. The **substitution test** swaps a symbol or assumption for a sibling and re-reads its justification slot — if the slot is still true under the swap, it pins nothing down ("plays a role in the proof of Lemma 3.1" is true of every symbol in the proof) and is blocking. The **proof-deletion test** covers the surrounding proof and re-reads only a symbol's meaning slot — if it evaporates, it was describing what the symbol is *used for*, not what it *is*.

## At planning and integration

These four gates are the correctness floor for every implementation pass, including rough exploratory work. At the planning stage the skill adds a hard gate: before any tasks are drafted for a modeling project, you write a **Model Inventory / Assumption Map** — primitives, endogenous objects, timing, solution concept, the canonical Notation Conventions table, and a verification plan — into the top `superRA/task.md` objective and sign off on it, so a derivation starts from an agreed inventory rather than from algebra. That Notation Conventions table is user-gated: implementers log new symbols to their per-task ledger, and a symbol is promoted to the project-wide table only when you confirm it.

At the integration stage the skill adds a separate readability layer — objective-first rewriting, per-step local obviousness, cross-document notation coherence — for turning an audited-but-rough derivation into reader-ready output. Load that only when polishing for a human reader.

For the full gate checklists, ledger slot templates, falsification tests, and rendering conventions, see [theory-modeling](skills/theory-modeling/SKILL.md).
