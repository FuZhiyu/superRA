# Theory-Modeling Planning Discipline

Load at the **PLAN phase** when the work involves mathematical
modeling. `planning-workflow` invokes this reference after Phase 1
(scope check) to apply domain-specific discipline before tasks are
drafted.

This reference carries two planning-only concerns that would otherwise
bloat the main `theory-modeling` skill body:

1. **Model Inventory / Assumption Map - the hard gate that blocks task drafting until the model objects and assumptions are surfaced and approved.**
2. **Verification Plan - the planning-time decision about which symbolic, limiting-case, and simple numerical checks will establish trust in the results.**

Both happen once, at planning time, and then live in `PLAN.md` as
sections the rest of the workflow references.

---

## Model Inventory / Assumption Map (Hard Gate)

The plan cannot be written without a model inventory. The researcher
arrives with a question and methodology already in mind. Your job at
this gate is not to redesign the model. Your job is to surface what the
model actually contains: primitives, endogenous objects, timing,
assumptions, normalization choices, and what evidence will count as
verification. The inventory becomes the **Model Inventory / Assumption
Map** section of `PLAN.md`.

<HARD-GATE>
Do NOT write any task structure, invoke any implementation skill, or
take any planning action beyond this gate until you have written the
Model Inventory / Assumption Map and the researcher has approved it.
This applies to EVERY theory/modeling project regardless of perceived
simplicity.
</HARD-GATE>

### Checklist

Complete the following planning checks in order:

1. **Understand the modeling goal** - ask the researcher what the model is meant to explain, what outputs matter, and whether the task is derivation, proof, comparative statics, calibration, or a mixed workflow.

2. **Inventory primitives and endogenous objects** - write down:
   - primitives: parameters, endowments, technologies, exogenous processes, information structure, timing, institutional rules
   - endogenous objects: choices, value functions, prices, allocations, laws of motion, equilibrium conditions, welfare objects

3. **Map assumptions explicitly** - for each primitive, record the assumptions that make the model well-defined: domains, signs, continuity/concavity/convexity, support of shocks, boundary or transversality conditions, normalizations, and equilibrium-selection rules. Put assumptions on primitives whenever possible; do not phrase them as desired properties of endogenous objects unless the project is proving those properties.

4. **Audit notation before drafting tasks** - list every symbol, what it means, and whether the notation is conventional. Ban lazy placeholders such as `A/B/C/D`, `T1/T2`, `eq1`, and `var2`. Conventional notation is allowed when explicit and intuitive, for example `r` for an interest rate or `beta` for a discount factor.

5. **Design the verification plan** - decide which results will be checked by substitution, which need limiting or special cases, which need a simple numerical example, what baseline parameter values or ranges will be used, and what pass condition each check must satisfy.

6. **Present the inventory and get researcher approval.** Write it into `PLAN.md` as a dedicated header section using this structure, then ask the researcher to confirm before proceeding to task drafting:

```markdown
**Model Inventory / Assumption Map:**

### Timing / Information Structure
- [State the sequence of moves, information available at each step, and any commitment or observability assumptions.]

### Solution Concept
- [State the active solution concept: planner problem, competitive equilibrium, recursive equilibrium, steady state, fixed point, or other.]

### Notation Conventions
| Symbol | Meaning | Why this notation |
|---|---|---|
| ... | ... | ... |

### Primitives
| Object | Meaning | Domain / Units | Notes |
|---|---|---|---|
| ... | ... | ... | ... |

### Endogenous Objects
| Object | Meaning | Defined by | Notes |
|---|---|---|---|
| ... | ... | ... | ... |

### Assumptions
| Assumption | Applies to | Role in the model | Notes |
|---|---|---|---|
| ... | ... | ... | ... |

### Verification Plan
| Result | Verification mode | Baseline case / parameters | Pass condition |
|---|---|---|---|
| ... | ... | ... | ... |
```

### Principles

- **Expose hidden assumptions early** - if a derivation will need positivity, interiority, monotonicity, or boundedness, state that in the map before tasks are drafted.
- **Prefer interpretable notation** - a reviewer should know what a symbol is without chasing aliases. Conventional symbols are fine; arbitrary placeholders are not.
- **Keep assumptions on primitives** - "assume `c > 0`" is weaker than naming the primitive restrictions that imply positive consumption. Prefer the latter.
- **Plan verification up front** - do not leave numerical or special-case checks as an afterthought.
- **Escalate methodology choices** - if the "right" utility form, equilibrium concept, or normalization depends on research intent, ask the researcher rather than choosing unilaterally.

### Common mistakes

- **Skipping the inventory because the model is "standard."** Standard models still hide timing, normalization, and branch-choice assumptions.
- **Drafting tasks while notation is unsettled.** Task steps written against unstable notation are usually rewritten from scratch.
- **Treating verification as implementation detail.** The plan must already say how trust will be established.

### Red Flags - Hard Gate Protection

The Model Inventory / Assumption Map gate applies to every
theory/modeling plan regardless of perceived simplicity. The following
loopholes are closed:

**Never:**
- Proceed to task drafting on the basis of a verbal description only. The inventory must be written into `PLAN.md`.
- Say "the notation is standard" without listing the symbols and meanings.
- Write tasks in parallel with the inventory "to save time."
- Use "TBD assumptions", "notation to be cleaned later", or "verify numerically if needed" in task steps.
- Assume existence, uniqueness, or interiority just because the target result would be nicer under those conditions.

**Common rationalizations that mean STOP:**
- "This is just a short derivation." Short derivations hide the same assumption drift as long ones.
- "The researcher obviously means the textbook setup." Write down the setup anyway. The doc is the record.
- "I can draft tasks now and pin down assumptions later." No. Unknown assumptions mean the task structure is speculative.

After the researcher approves the inventory, proceed to task drafting.

---

## Verification Plan

Every theory/modeling plan should include explicit verification tasks. At
the planning stage:

1. **Discuss with the researcher which checks matter.** Typical options:
   - substitution back into first-order conditions, laws of motion, or equilibrium conditions
   - limiting or special cases
   - sign checks for comparative statics
   - small numerical examples or calibrations
   - boundary and corner-case checks

2. **Design verification as dedicated task work.** Verification is usually its own task or an explicit step inside each derivation task; it is not a vague "sanity check later".

3. **Document expected outcomes.** For each planned check, note what should happen and what would count as a concerning failure.

4. **Tie verification to renderable outputs.** If the final artifact includes equations, tables, or figures for a human reader, plan to use `superRA:report-in-markdown` rather than inventing a separate formatting path.

5. **Keep reproducibility explicit.** If the modeling workflow uses more than one script or notebook, include a pipeline entry point in the plan so symbolic and numerical outputs can be rerun from source.

---

## Handoff to Implementation

After the Model Inventory / Assumption Map is approved, the verification
plan is agreed, and tasks are drafted, `planning-workflow` commits the
plan and hands off to `implementation-workflow`. The main
`theory-modeling` skill body carries the cross-cutting discipline that
applies at every implementation step: the Iron Law, Define-Derive-
Validate, verification, and documentation.
