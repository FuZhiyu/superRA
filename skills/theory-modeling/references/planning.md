# Theory-Modeling Planning Discipline

Load at the **PLAN phase** when the work involves mathematical modeling. `superplan` invokes it after Phase 1 (scope check), before tasks are drafted.

---

## Model Inventory / Assumption Map

Surface what the model contains — primitives, endogenous objects, timing, assumptions, normalization choices, and what evidence counts as verification. Not a redesign of the researcher's model.

Both homes are the governing ancestor task, the one whose subtree is the whole model. The **catalogue** — timing, primitives, endogenous objects — goes in its `## Details`. What a reviewer rejects work against goes in its `## Objective`: the solution concept, the canonical Notation Conventions, the Assumptions, and the Verification Plan. A restriction the timing implies is an Assumptions row, not a details line.

### Checklist

In order:

1. **Understand the modeling goal** - what the model explains, what outputs matter, and whether the work is derivation, proof, comparative statics, calibration, or mixed.

2. **Inventory primitives and endogenous objects** - write down:
   - primitives: parameters, endowments, technologies, exogenous processes, information structure, timing, institutional rules
   - endogenous objects: choices, value functions, prices, allocations, laws of motion, equilibrium conditions, welfare objects

3. **Map assumptions explicitly** - per primitive, the assumptions making the model well-defined: domains, signs, continuity/concavity/convexity, support of shocks, boundary or transversality conditions, normalizations, equilibrium-selection rules. Assumptions go on primitives, not on desired properties of endogenous objects — unless the project proves those properties.

4. **Audit notation before drafting tasks** - every symbol, its meaning, and whether the notation is conventional. No placeholders (`A/B/C/D`, `T1/T2`, `eq1`, `var2`). Conventional notation is fine when explicit and intuitive — `r` for an interest rate, `beta` for a discount factor.

5. **Design the verification plan** - which results are checked by substitution, which need limiting or special cases, which need a simple numerical example, what baseline parameter values or ranges apply, and what pass condition each check must satisfy.

6. **Write it into the two homes**, in this structure.

`## Details`:

```markdown
**Model inventory:**

### Timing / Information Structure
- [State the sequence of moves, information available at each step, and any commitment or observability assumptions.]

### Primitives
| Object | Meaning | Domain / Units | Notes |
|---|---|---|---|
| ... | ... | ... | ... |

### Endogenous Objects
| Object | Meaning | Defined by | Notes |
|---|---|---|---|
| ... | ... | ... | ... |
```

`## Objective`:

```markdown
**Assumption map:**

### Solution Concept
- [State the active solution concept: planner problem, competitive equilibrium, recursive equilibrium, steady state, fixed point, or other.]

### Notation Conventions
| Symbol | Meaning | Why this notation |
|---|---|---|
| ... | ... | ... |

The **Why this notation** column is required for every non-conventional
symbol — the intuition or mnemonic behind the choice. Symbols already
fixed by the literature (`r`, `beta`, `w`) may leave it as "conventional".

### Assumptions
| Assumption | Applies to | Role in the model | Interpretation | Notes |
|---|---|---|---|---|
| risk aversion bounded | preferences | ensures the value function is finite | risk aversion bounded so the value function is finite | ... |
| ... | ... | ... | ... | ... |

### Verification Plan
| Result | Verification mode | Baseline case / parameters | Pass condition |
|---|---|---|---|
| ... | ... | ... | ... |
```

### Frontier Contributions

The inventory settles facts; the choices it exposes go to the researcher as frontier questions (`superplan §Grilling`):

- **Functional form** — the "right" utility, production, or cost specification for this research intent.
- **Solution concept and equilibrium selection** where more than one is defensible.
- **Normalizations** that change interpretation rather than only algebra.
- **Verification mode per result** — substitution, limiting case, numerical example — and what counts as a concerning failure.

### Principles (non-default constraints)

- **Notation Conventions is canonical and user-gated** - the planner seeds the table with the symbols agreed at planning time. During implementation, new symbols go to the per-task **Notation & Assumptions Ledger** in the task's `## Results` (`SKILL.md` §Documentation and handoff); promotion to the canonical table requires explicit user confirmation.
- **Interpretability is blocking; prefer synthesis** - every assumption carries a plain-language interpretation a researcher can defend at planning time, and scattered weak restrictions replaceable by one stronger interpretable primitive are synthesized. Full checklist: `skills/theory-modeling/SKILL.md` §Assumptions.
- **Escalate methodology choices** - never choose one silently; they are §Frontier Contributions.

### Red Flags

**Never:**
- Proceed to task drafting on a verbal description. The inventory goes into the governing ancestor task.
- Say "the notation is standard" without listing the symbols and meanings.
- Write tasks in parallel with the inventory "to save time."
- Use "TBD assumptions", "notation to be cleaned later", or "verify numerically if needed" in task steps.
- Assume existence, uniqueness, or interiority because the target result is nicer under them.
- Leave a symbol's intuition or mnemonic as "TBD" in the Notation Conventions table.
- Write an assumption row with a blank **Interpretation** column, or "later" / "to be explained".
- Enumerate weak technical assumptions where one stronger interpretable primitive is clearly available.

**Rationalizations that mean STOP:**
- "This is just a short derivation." Short derivations hide the same assumption drift as long ones.
- "The researcher obviously means the textbook setup." Write the setup down anyway; the doc is the record.
- "I can draft tasks now and pin down assumptions later." Unknown assumptions make the task structure speculative.

---

## Verification Plan

Every theory/modeling plan includes explicit verification tasks.

1. **Propose which checks matter** — a §Frontier Contributions question, so recommend rather than choose. Typical options:
   - substitution back into first-order conditions, laws of motion, or equilibrium conditions
   - limiting or special cases
   - sign checks for comparative statics
   - small numerical examples or calibrations
   - boundary and corner-case checks

2. **Design verification as dedicated task work.** Its own task, or an explicit step inside each derivation task — never a vague "sanity check later".

3. **Document expected outcomes.** Per check: what should happen, and what counts as a concerning failure.

4. **Tie verification to renderable outputs.** Equations, tables, or figures for a human reader route through `superRA:communicate`, not a separate formatting path.

5. **Keep reproducibility explicit.** More than one script or notebook: include a pipeline entry point so symbolic and numerical outputs rerun from source.

---

## Handoff to Implementation

Inventory written down, frontier empty, tasks drafted: `superplan` commits and hands off to execution. Implementation-step discipline is the `theory-modeling` SKILL.md body (Iron Law and the four gates).
