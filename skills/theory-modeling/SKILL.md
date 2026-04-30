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
| `references/integration.md` | `integration` stage - modeling-specific refactor-integrity gates (notation consistency, assumption-map preservation, derivation discipline preserved through refactoring, verification pass-through), plus task-level rewriting and document-internal coherence (objective-first structural rewriting, per-step local obviousness, notation/prior-result reuse, reader-perspective discipline). |
| `references/objective-first.md` | `integration` stage - worked bad/good walkthrough and identification-training drills for objective-first structural rewriting; loaded on demand from `references/integration.md` Section A. |
| `references/audience-discipline-modeling.md` | `integration` stage - reader-perspective discipline for modeling work; loaded on demand from `references/integration.md` Section C. |
| `references/audience-discipline-writing.md` | `integration` stage - reader-perspective discipline for the writing layer; loaded on demand from `references/integration.md` Section C. |

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
→ Verification & Rendering**. Each gate has an **artifact** the
implementer produces and a **checklist** of quality items walked while
producing it. The gates are **concurrent, not sequential** — every
modeling step exercises all four. Documentation is built into the
artifact definitions, not handled as a separate phase.

This section is both **teaching content** and the **shared checklist**.
The implementer walks it before returning DONE; the reviewer walks the
same items as verification.

- `[BLOCKING]` — must fix to earn APPROVE. Encodes the Iron Law,
  artifact discipline, and other required items.
- `[ADVISORY]` — best practice. The reviewer MAY flag as MINOR; does
  not block APPROVE.

### Reviewer verdict protocol

**For each gate, verify the artifact exists, then walk the checklist
against it. Walk top to bottom every time; never halt on a failure.**
One comprehensive pass per review — halting early forces a full
re-review on the next pass, and reviewer dispatches are costly.

Two verdicts:

- **APPROVE** — no `[BLOCKING]` findings.
- **REVISE** — at least one `[BLOCKING]` finding.

**Falsification tests, applied per ledger entry in Gates 1 and 2:**

- **Substitution test.** Mentally substitute a hypothetical extra
  symbol (or assumption) into the entry's "What the name carries" /
  "What this assumption carries" slot. If the slot still reads as
  true, the justification is structurally vacuous → BLOCKING. The
  slot must contain content specific to *this* object that would be
  false of a different one.
- **Proof-deletion test (Meaning slot).** Mentally delete the
  surrounding proof. Does the Meaning slot still let the reader
  reconstruct the object? If no, the slot was a usage description
  ("used to verify X"), not a meaning → BLOCKING.

**Handling dependent findings.** When a later finding depends on an
earlier `[BLOCKING]` item being fixed first, say so in plain prose
alongside the finding.

**Re-review after REVISE.** Implementer fixes all `[BLOCKING]` findings
and re-dispatches. The reviewer then (1) verifies each fix, and
(2) re-checks any finding that depended on an upstream fix. Everything
else is accepted from the first pass.

### Gate 1 — Objects & Notation

A reader trusts a model only if every symbol has a clear meaning. Pin
down the objects and their names before manipulating them.

**Artifact: per-symbol ledger entry in `RESULTS.md`.** One entry per
object. An indexed family ($x_k$ for $k=1,\dots,K$) counts as one
object, not $K$. Five distinct symbols sharing a proof passage are
five entries — bundling distinct objects under a shared justification
is a format violation, not a judgment call. Tasks that introduce no
new symbols record "None."

Symbols already named in `PLAN.md`'s Notation Conventions table are
reused with the canonical meaning rather than redefined locally; they
do not require a new ledger entry.

**Slot template** (all required except where noted):

```
Symbol: <name>
Meaning: <type/space + denotation + origin if derived>
First-use site: <RESULTS.md line or equation label in this task>
Reuse sites: <every additional site, with refs; "none" if one-site>
Inline alternative: <the actual expression substituted at first-use>
What the name carries beyond the expression:
  <interpretive content lost by inlining: sign meaning, role in a
   structural identity, named scalar cited at site X. "Shorter
   string" does not qualify.>
Nearest existing symbol considered:
  <from PLAN.md Notation Conventions, active lemma, or upstream
   derivation in this task; "none in scope" is a falsifiable claim>
Why this name and not that one:
  <only if "Nearest existing" is non-empty>
```

**Writing the Meaning slot.** Three components, all required:

1. **Type / space.** Scalar in $(0,1)$, $K$-vector in $\mathbb{R}^K$,
   $N\times N$ symmetric matrix, function $X \to Y$, random variable
   on $(\Omega,\mathcal{F},\mathbb{P})$. Include dimension and domain
   wherever applicable.
2. **Denotation in the model's vocabulary.** What the object
   represents in already-introduced terms: "the coefficient on $X_t$
   in eq. (12)", "the Lagrange multiplier on the resource
   constraint", "row $k$ of the dividend-loading matrix $H$". Must
   reference only objects already defined.
3. **Origin if derived.** How the symbol is constructed from prior
   symbols, e.g. $\mathbf{c}_k := H^\top e_k$. The construction of
   the symbol, not a step that uses it later.

Test: mentally delete the surrounding proof. Would the Meaning slot
still let a reader reconstruct the object? If no, the slot is a usage
description, not a meaning.

**Anti-patterns for Meaning:**

| Bad meaning | Why it fails |
|---|---|
| "Used to verify $h_k = m_D \beta_{E,k}$" | Role in proof, not what the object is. |
| "An auxiliary vector" | Adjective + type, no denotation. |
| "The column-$k$ object" | Tautology — restates the index. |
| "Defined as $\mathbf{c}_k = \dots$ below" | Forward reference; meaning must be defensible at first use. |
| "Local proof-only construct" | Locality is scope, not content. |

**Checklist:**

- `[BLOCKING]` Ledger entry written **before** the symbol appears in proof text. Other documentation can run concurrently with the math; symbol introduction cannot — post-hoc entries reverse-engineer justifications for choices already made.
- `[BLOCKING]` Notation is interpretable or genuinely conventional. Arbitrary placeholder labels like `A/B/C/D`, `T1/T2`, `eq1`, `var2` are not acceptable. Conventional notation such as `r` for an interest rate or `w` for a wage is acceptable when defined at first use.
- `[BLOCKING]` Meaning slot satisfies the type / denotation / origin recipe and survives the proof-deletion test.
- `[BLOCKING]` Reuse-sites slot cites every additional appearance with line or equation refs, or states "none." Claims of reuse without refs are REVISE.
- `[BLOCKING]` Inline-alternative slot shows the actual substituted expression, not a description of it ("would be unwieldy" is not an inline alternative).
- `[BLOCKING]` One-site symbols (Reuse sites: none) must justify via concrete content in "What the name carries" — sign meaning, structural role, named scalar cited elsewhere. One-time abbreviation fails regardless of length.
- `[BLOCKING]` "Nearest existing symbol considered: none in scope" is a falsifiable claim. If the reviewer finds a candidate in `PLAN.md`'s Notation Conventions, the active lemma, or an upstream derivation, REVISE.
- `[BLOCKING]` One entry per object. Indexed families ($x_k$ for $k=1,\dots,K$) count as one; bundling multiple distinct objects under a shared justification is REVISE.
- `[BLOCKING]` Domains, units, and sign restrictions are stated whenever they matter for the algebra, comparative statics, or numerical checks.
- `[ADVISORY]` When multiple notation choices are reasonable, prefer the one matching the literature or existing project docs; if you deviate, note the mapping.

### Gate 2 — Assumptions

Assumptions carry the economic content of a model. Each one must be
attached to a primitive object, readable as economics, and no weaker
than it needs to be — prefer a single interpretable primitive over a
scattering of weak technical restrictions.

**Artifact: per-assumption ledger entry in `RESULTS.md`.** One entry
per assumption. Tasks that introduce no new assumptions record "None."

**Slot template:**

```
Assumption: <statement>
Interpretation:
  <one-sentence plain-language reading a researcher can defend>
Attached to:
  <primitive — preferences / technology / endowment / information /
   timing / distribution / parameter domain / boundary / normalization>
First-bite site: <where in this task's derivation it is invoked>
Reuse / scope: <every result that depends on it>
Without this assumption:
  <which conclusion changes; if "none", the assumption fails
   necessity and should be removed>
What this assumption carries beyond existing assumptions:
  <the additional restriction on the named primitive that no
   existing assumption already imposes. "Cleaner statement" does
   not qualify.>
Nearest existing assumption considered:
  <from PLAN.md Assumption Map or upstream derivations>
Why state it this way and not via the existing one:
  <only if "Nearest existing" is non-empty; if a stronger version of
   the existing assumption would cover this case, prefer the synthesis>
```

**Checklist:**

- `[BLOCKING]` Assumption is attached to a primitive (preferences, technology, endowments, information, timing, distributions, parameter domains, boundary conditions, normalizations). Assumptions stated as desired properties of endogenous objects are REVISE unless those properties are later proved.
- `[BLOCKING]` Interpretation slot carries a one-sentence plain-language reading a researcher can defend (e.g., "risk aversion bounded so the value function is finite"). Math-only restrictions without economic interpretation are REVISE.
- `[BLOCKING]` "Without this assumption" slot names a specific conclusion that changes. Vague claims ("the result would be weaker") are REVISE.
- `[BLOCKING]` "What this assumption carries" slot names the additional restriction on the named primitive that existing assumptions do not impose. Generic claims ("makes the proof cleaner") are REVISE.
- `[BLOCKING]` When multiple scattered assumptions can be replaced by a single stronger primitive assumption with a cleaner interpretation, prefer the synthesis and record the trade in "Why state it this way." Reviewer applies a judgement margin — flag only when a clearly cleaner synthesis is available.

### Gate 3 — Derivations

Derivations must be auditable. A correct result that cannot be checked
is not an acceptable handoff artifact. Every non-trivial move needs both
the technical rule and a reason for invoking it here.

**Artifact: the proof / derivation body in `RESULTS.md`.**

**Checklist:**

- `[BLOCKING]` The active solution concept is named before derivation starts: planner problem, competitive equilibrium, recursive equilibrium, steady state, fixed point, or other relevant concept.
- `[BLOCKING]` Top-level proof goal stated in one sentence before the first displayed equation. Derivations whose first move is algebra without a stated target are REVISE. (Full reader-facing recursive signposting — sub-arguments at every level, transition prose — lives in `references/integration.md` Section A as ex-post rewriting discipline.)
- `[BLOCKING]` When a derivation step depends on a previously established equation, lemma, or proposition, the dependency is cited by name or equation number. Asserted equations with no path to a named source are REVISE. (Cite-with-operative-form-recall for distant sources is owned by `references/integration.md` Section B.)
- `[BLOCKING]` One logical algebraic move per displayed step. Do not collapse multiple substitutions, cancellations, and sign changes into "therefore".
- `[BLOCKING]` Each non-obvious step states the rule being used: substitute a constraint, differentiate with respect to a variable, apply the envelope theorem, impose market clearing, linearize around a point, or similar.
- `[BLOCKING]` Each non-trivial step carries both the technical rule (envelope theorem, market clearing, ...) and a one-sentence reason for invoking it; mechanical rule-labels without a reason are REVISE.
- `[BLOCKING]` When a result depends on case splits or domains (interior vs corner, positive vs negative branch, existence/uniqueness conditions), the active case is stated and excluded cases are either checked or explicitly deferred.
- `[BLOCKING]` Comparative statics state what is held fixed, which object moves, and what sign or ranking is being claimed.
- `[BLOCKING]` Reused symbols keep the same meaning throughout the task. If notation changes, old and new notation are mapped explicitly.
- `[BLOCKING]` Claims of existence, uniqueness, monotonicity, or concavity are supported by a stated argument, not asserted by inspection.
- `[BLOCKING]` New equations, named statements (lemmas, propositions, definitions, corollaries), and derivation steps are checked under the same necessity lens as ledger entries: if removal leaves the reasoning intact, remove it. Equations and named statements do not require individual ledger entries (per-equation cost too high) — the one-move-per-step and reason-per-move items above are how the lens is enforced in practice.
- `[ADVISORY]` Keep displayed equations short enough to audit; break long chains into aligned steps rather than dense one-line algebra.

### Gate 4 — Verification & Rendering

Symbolic work still needs verification. A derivation is not complete
until it has survived at least one independent check and reads cleanly
for a human audience.

**Artifact: verification record + rendered output.** The verification
record states the check performed (substitute back, limiting case,
numerical evaluation), the parameters used if any, and the pass
condition. The rendered output is the human-readable markdown / LaTeX
that ships in `RESULTS.md`.

**Checklist:**

- `[BLOCKING]` Every headline symbolic result is checked against at least one independent verification mode: substitute back into the original conditions, test a limiting or special case, or evaluate a simple numerical example.
- `[BLOCKING]` Numerical verification uses explicit parameter values and states what is being checked: residual near zero, sign, monotonicity, feasibility, branch selection, or fixed-point convergence.
- `[BLOCKING]` Special cases and limiting cases are compared against intuition and any stated hypotheses in `PLAN.md`; divergences are flagged before proceeding.
- `[BLOCKING]` Special and limiting cases are interpreted economically, not just numerically confirmed (e.g., "at $\beta \to 0$ the policy reduces to the myopic rule, which matches the one-period benchmark").
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

The ledger artifacts for Gates 1 and 2 already live in `RESULTS.md`;
the items below are the cross-cutting documentation rules that apply
beyond the per-symbol / per-assumption ledgers.

- `[BLOCKING]` `RESULTS.md` is updated in place for this task's section. The doc is the record — findings live there before they appear in any status report.
- `[BLOCKING]` `PLAN.md`'s Notation Conventions table is **canonical and user-gated**. Implementers do NOT inline-edit it during implementation. A symbol is promoted from the RESULTS.md ledger to the Notation Conventions table only when the user confirms it should become a canonical project-wide symbol; until then the ledger entry is the source of truth for that task.
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
| "I'll update the Notation Conventions table after the derivation is clean." | The Notation Conventions table is user-gated and canonical; log new symbols to the per-task RESULTS.md ledger instead, and let the user confirm any promotion. |
| "It's defined locally and used in the algebra, so it's fine." | Local definition is necessary, not sufficient. If an existing upstream symbol names the same object, the local one hides the connection and adds reader load. |
| "It came from the derivation note, so it's already vetted." | Inherited notation is on trial again in the new proof. Legacy legitimacy does not beat a cleaner upstream name available right now. |
| "It only abbreviates this one expression." | One-time shorthand adds a symbol the reader must memorize for one line. Expand inline or fold into an existing name. |
| "It's a local proof-only object." | Locality is scope, not content. Each symbol still walks the ledger procedure on its own; "proof-only" does not discharge necessity or non-duplication. Cluster framings ("these are local proof-only objects") dodge per-symbol scrutiny by reframing the unit of evaluation — one entry per object, no exceptions. |
| "Each is used in the proof step that uses it." | Restatement of the gate, not evidence. Walk the slots: cite reuse sites by ref, or fill "What the name carries" with concrete interpretive payload (sign, structural role, named scalar cited at site X). A justification that would still read as true for a hypothetical extra symbol is vacuous. |
| "The meaning is clear from how it's used." | Usage is not meaning. Mentally delete the surrounding proof; if the Meaning slot becomes vacuous, it was a usage description, not a meaning. Apply the type / denotation / origin recipe instead. |
| "The intuition is obvious." | If the intuition is not written, the reader is reconstructing it from algebra - which is exactly what the Iron Law rules out. |
| "I'll add interpretation after the algebra is clean." | Post-hoc interpretation is where hidden assumptions hide; the interpretation must be defensible at the moment the assumption is stated. |
| "Weaker assumptions are always safer." | Scattered weak technical restrictions are harder to defend than one stronger primitive with a clean economic reading; prefer the synthesis when it is available. |
| "This assumption is technical, not economic." | A technical restriction with no economic reading is a bet the restriction does not bite; if it does not bite, drop it, and if it does, name the economics. |

## Key References

- `references/planning.md` - planning hard gate: Model Inventory / Assumption Map plus Verification Plan
- `references/integrate-drift-tests.md` - drift-test guidance for symbolic and numerical invariants
- `references/integration.md` - integration-stage checklist for modeling work
- `superRA:report-in-markdown` - format discipline for equations, tables, figures, and LaTeX in markdown
