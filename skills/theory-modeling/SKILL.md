---
name: theory-modeling
description: >
  Use PROACTIVELY whenever doing mathematical-modeling work:
  defining primitives, stating assumptions, setting timing or
  information structure, deriving optimality conditions, solving
  equilibria, checking comparative statics, writing proofs,
  running simple numerical verification, or producing renderable
  markdown/LaTeX model notes. Triggers include "derive the
  model", "solve the equilibrium", "check the proof", "write
  the FOCs", "verify the comparative statics", "calibrate a toy
  example", or any task where algebra and assumptions must stay
  explicit.
user-invocable: true
---

# Theory Modeling

Domain skill for rigorous mathematical-modeling work; body carries
Stage-Scoped References, the Iron Law, the four-gate checklist
(Objects & Notation / Assumptions / Derivations / Verification &
Rendering), and Common Rationalizations.

## Stage-Scoped References

Companion reference files carry content that applies at a specific
phase. Load per stage; do not load them all at every dispatch:

| Reference | Load when |
|---|---|
| `references/planning.md` | PLAN phase - covers the **Model Inventory / Assumption Map hard gate** and the **Verification Plan**. Loaded by `planning-workflow` when the work is theory/modeling. |
| `references/integrate-drift-tests.md` | `drift-test` stage - identifies modeling results worth protecting, sets symbolic and numerical tolerance conventions, and catalogs theory-modeling failure modes drift tests catch. Loaded by `integration-workflow` Phase A. |
| `references/integration.md` | `integration` stage - modeling-specific refactor-integrity gates (notation consistency, assumption-map preservation, derivation discipline preserved through refactoring, verification pass-through). |

## The Iron Law

```
NO MANIPULATION WITHOUT DEFINED OBJECTS, INTERPRETABLE ASSUMPTIONS, AND STATED INTUITION
```

Every symbol has a meaning. Every assumption has a plain-language
interpretation a researcher can defend. Every non-trivial move has a
one-sentence reason.

If a symbol appears without a stated meaning, an assumption is written
only as a math restriction with no economic reading, or a derivation
step is invoked mechanically with no reason, back up and write the
missing meaning, interpretation, or reason first.

**No exceptions:**
- Do not introduce a symbol without a stated meaning or intuition.
- Do not state an assumption only as a math restriction without a plain-language interpretation a researcher can defend.
- Do not hide a key restriction in "assume interior solution" after the algebra is already written.
- Do not invoke a derivation rule (envelope theorem, market clearing, linearization) without a one-sentence reason for using it here.
- Do not rename objects mid-derivation without mapping the notation.
- Do not move a restriction from primitives to an endogenous variable just because the latter is shorter to write.
- Do not rely on memory of a previous draft or paper note.
- Back up means back up.

---

## The Four Gates

Four gates underpin trustworthy modeling work, organized around the
reader's trust chain: **Objects & Notation → Assumptions → Derivations
→ Verification & Rendering**. They are **concurrent, not sequential** -
every modeling step exercises all four. Documentation runs continuously
alongside them as a cross-cutting writing practice, not a fifth phase.

This section is both **teaching content** and the **shared checklist**.
The implementer walks it before returning DONE; the reviewer walks the
same items as verification.

- `[BLOCKING]` - must fix to earn APPROVE. Encodes the Iron Law,
  handoff-doc discipline, and other required items.
- `[ADVISORY]` - best practice. The reviewer MAY flag as MINOR; does
  not block APPROVE.

### Reviewer verdict protocol

**Walk the four gates top to bottom every time. Never halt on a
failure.** One comprehensive pass per review - halting early forces a
full re-review on the next pass, and reviewer dispatches are costly.

Two verdicts:

- **APPROVE** - no `[BLOCKING]` findings.
- **REVISE** - at least one `[BLOCKING]` finding.

**Handling dependent findings.** When a later finding depends on an
earlier `[BLOCKING]` item being fixed first, say so in plain prose
alongside the finding.

**Re-review after REVISE.** Implementer fixes all `[BLOCKING]` findings
and re-dispatches. The reviewer then (1) verifies each fix, and
(2) re-checks any finding that depended on an upstream fix. Everything
else is accepted from the first pass.

### Objects & Notation

A reader trusts a model only if every symbol has a clear meaning. Pin
down the objects and their names before manipulating them.

- `[BLOCKING]` Every symbol is introduced in narrative order before first use: primitives, choice variables, state variables, parameters, shocks, constraints, value objects, prices, and equilibrium conditions. A symbol may not appear in any derivation, equation, proof step, or verification before the paragraph or table that introduces it. For symbols reused across tasks, `PLAN.md`'s Notation Conventions table is the authoritative source - reuse its meaning rather than redefining the symbol locally.
- `[BLOCKING]` Notation is explicit and interpretable or genuinely conventional. Arbitrary placeholder labels like `A/B/C/D`, `T1/T2`, `eq1`, and `var2` are not acceptable. Conventional notation such as `r` for an interest rate or `w` for a wage is acceptable when defined at first use.
- `[BLOCKING]` Every new symbol introduced during implementation carries a stated intuition or mnemonic (one short sentence), unless it reuses a conventional name already in `PLAN.md`'s Notation Conventions.
- `[BLOCKING]` Domains, units, and sign restrictions are clear whenever they matter for the algebra, comparative statics, or numerical checks.
- `[ADVISORY]` When multiple notation choices are reasonable, prefer the one matching the literature or existing project docs; if you deviate, note the mapping.

### Assumptions

Assumptions carry the economic content of a model. Each one must be
attached to a primitive object, readable as economics, and no weaker
than it needs to be - prefer a single interpretable primitive over a
scattering of weak technical restrictions.

- `[BLOCKING]` Assumptions are explicit and attached to primitives: preferences, technology, endowments, information, timing, distributions, parameter domains, boundary conditions, and normalizations. Do not state assumptions as desired properties of endogenous objects unless those properties are later proved.
- `[BLOCKING]` Each assumption carries a one-sentence plain-language interpretation a researcher can defend (e.g., "risk aversion bounded so the value function is finite"); assumptions stated only as math restrictions without economic interpretation are REVISE.
- `[BLOCKING]` When multiple scattered assumptions can be replaced by a single stronger primitive assumption with a cleaner interpretation, prefer the synthesis and record the trade. Reviewer applies a judgement margin - flag only when a clearly cleaner synthesis is available.

### Derivations

Derivations must be auditable. A correct result that cannot be checked
is not an acceptable handoff artifact. Every non-trivial move needs both
the technical rule and a reason for invoking it here.

- `[BLOCKING]` The active solution concept is named before derivation starts: planner problem, competitive equilibrium, recursive equilibrium, steady state, fixed point, or other relevant concept.
- `[BLOCKING]` One logical algebraic move per displayed step. Do not collapse multiple substitutions, cancellations, and sign changes into "therefore".
- `[BLOCKING]` Each non-obvious step states the rule being used: substitute a constraint, differentiate with respect to a variable, apply the envelope theorem, impose market clearing, linearize around a point, or similar.
- `[BLOCKING]` Each non-trivial step carries both the technical rule (envelope theorem, market clearing, ...) and a one-sentence reason for invoking it; mechanical rule-labels without a reason are REVISE.
- `[BLOCKING]` When a result depends on case splits or domains (interior vs corner, positive vs negative branch, existence/uniqueness conditions), the active case is stated and excluded cases are either checked or explicitly deferred.
- `[BLOCKING]` Comparative statics state what is held fixed, which object moves, and what sign or ranking is being claimed.
- `[BLOCKING]` Reused symbols keep the same meaning throughout the task. If notation changes, old and new notation are mapped explicitly.
- `[BLOCKING]` Claims of existence, uniqueness, monotonicity, or concavity are supported by a stated argument, not asserted by inspection.
- `[ADVISORY]` Keep displayed equations short enough to audit; break long chains into aligned steps rather than dense one-line algebra.

### Verification & Rendering

Symbolic work still needs verification. A derivation is not complete
until it has survived at least one independent check and reads cleanly
for a human audience.

- `[BLOCKING]` Every headline symbolic result is checked against at least one independent verification mode: substitute back into the original conditions, test a limiting or special case, or evaluate a simple numerical example.
- `[BLOCKING]` Numerical verification uses explicit parameter values and states what is being checked: residual near zero, sign, monotonicity, feasibility, branch selection, or fixed-point convergence.
- `[BLOCKING]` Special cases and limiting cases are compared against intuition and any stated hypotheses in `PLAN.md`; divergences are flagged before proceeding.
- `[BLOCKING]` Special and limiting cases are interpreted economically, not just numerically confirmed (e.g., "at `β → 0` the policy reduces to the myopic rule, which matches the one-period benchmark").
- `[BLOCKING]` Results are checked back against the assumption map. If a step quietly needs a stronger sign, domain, or regularity restriction than the current map states, update the assumption map before using the result.
- `[BLOCKING]` When code, CAS output, or a solver is used, the human-readable result matches the computed object exactly. No manual transcription drift.
- `[BLOCKING]` If an expression is rendered for a human reader, markdown and LaTeX are unambiguous: subscripts, superscripts, fractions, summation limits, and align environments read cleanly.
- `[ADVISORY]` For numerically delicate objects, verify more than one parameter set or a small perturbation around the baseline.

### Implementation standards

- `[BLOCKING]` Each task satisfies the current `PLAN.md` objective and scope. When steps are present, they stay in sync with the current route rather than drifting away from the work.
- `[BLOCKING]` If the evidence shows that an extra lemma, case split, derivation step, or verification pass is required to trust the result, add it inside the current task and rewrite the step text to match.
- `[BLOCKING]` Solver scripts, symbolic code, and model notes are organized so a reviewer can trace the chain from primitives and assumptions to the reported result.
- `[BLOCKING]` Major modeling decisions (normalization, timing, equilibrium selection, parameter baseline, approximation point) carry a markdown explanation or nearby comment.

### Documentation and handoff

- `[BLOCKING]` `RESULTS.md` is updated in place for this task's section. The doc is the record - findings live there before they appear in any status report.
- `[BLOCKING]` When implementation introduces a symbol not yet in `PLAN.md`'s Notation Conventions table, update the table via inline-edit BEFORE using the symbol in algebra, and commit the `PLAN.md` edit atomically with the derivation work. Follow `superRA:handoff-doc` inline-edit discipline.
- `[BLOCKING]` Definitions, assumptions, and the reason for major derivation choices are written alongside the math or code, not left only in chat.
- `[BLOCKING]` When a task section includes equations, tables, or figures for human reading, use `superRA:report-in-markdown`; do not invent a separate rendering utility.
- `[BLOCKING]` Rendered math, prose, and any supporting code use consistent notation for the same object.
- `[BLOCKING]` No dangling TODO / placeholder / `XXX` strings ship.

### Stage-scoped discipline (not walked at every implementation dispatch)

- **`drift-test` stage** - `references/integrate-drift-tests.md` carries the modeling-specific guidance for symbolic identities, comparative statics, and simple numerical invariants that should be protected before merge.
- **`integration` stage** - `references/integration.md` carries the full integration-stage checklist (notation consistency, assumption-map preservation, verification checks surviving refactors, rendering utility reuse) with its own `[BLOCKING]` / `[ADVISORY]` markers and two-verdict protocol.
- **End-of-workflow completion verification** - `superRA:implementation-workflow` Step 3 carries the reproducibility gate. Walked by the orchestrator, not by dispatched subagents.

## Common Rationalizations

LLM-specific excuses that usually precede broken derivations or hidden
assumptions. When you catch yourself forming one of these, stop and make
the definitions or assumptions explicit.

| Excuse | Reality |
|---|---|
| "The notation is obvious from context." | If it is not named, the reviewer cannot audit it. |
| "I can clean up assumptions after the algebra." | Late assumptions are usually post-hoc patches for a broken step. |
| "A/B/C is temporary; I will rename it later." | Temporary placeholder notation spreads and becomes the model. |
| "The numerical check is only illustrative." | Even toy checks need explicit parameters and a stated pass condition. |
| "The CAS says it simplifies to zero." | You still need to say what was checked and under which assumptions. |
| "I'll update the Notation Conventions table after the derivation is clean." | Late notation updates mean the derivation was written against undefined symbols; update the table first, then derive. |
| "The intuition is obvious." | If the intuition is not written, the reader is reconstructing it from algebra - which is exactly what the Iron Law rules out. |
| "I'll add interpretation after the algebra is clean." | Post-hoc interpretation is where hidden assumptions hide; the interpretation must be defensible at the moment the assumption is stated. |
| "Weaker assumptions are always safer." | Scattered weak technical restrictions are harder to defend than one stronger primitive with a clean economic reading; prefer the synthesis when it is available. |
| "This assumption is technical, not economic." | A technical restriction with no economic reading is a bet the restriction does not bite; if it does not bite, drop it, and if it does, name the economics. |

## Key References

- `references/planning.md` - planning hard gate: Model Inventory / Assumption Map plus Verification Plan
- `references/integrate-drift-tests.md` - drift-test guidance for symbolic and numerical invariants
- `references/integration.md` - integration-stage checklist for modeling work
- `superRA:report-in-markdown` - format discipline for equations, tables, figures, and LaTeX in markdown
