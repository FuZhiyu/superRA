# Objective-First Derivations — Worked Example and Identification Training

> Loaded on demand from `references/integration.md` Section A. Carries a
> bad/good walkthrough and identification-training drills for the
> objective-first principle. Teaching material — no checklist. Principle
> and `[BLOCKING]` checklist live in `references/integration.md` Section A.

## Worked example: the consumption Euler equation

### Bad pattern

A confusing derivation opens with a local placeholder:

$$
\eta := \frac{u'(c_1)}{u'(c_0)}.
$$

It then computes $\eta = \beta(1+r)$ at the household optimum, substitutes
back, and arrives at $u'(c_0) = \beta(1+r)\,u'(c_1)$.

Why this is bad:

- The reader does not yet know why $\eta$ matters.
- The proof introduces a symbol that lives for one algebraic detour and
  is discarded at the end.
- The derivation hides the objective until the final substitution; the
  Euler equation looks like a fortunate coincidence rather than a
  consequence of intertemporal optimization.

The hidden logic is

$$
\text{Euler equation} \;\text{requires}\; \text{FOCs in } c_0, c_1
\;\text{require}\; \text{Lagrangian}
\;\text{requires}\; \text{preferences} + \text{budget constraint}.
$$

The bad derivation traverses this dependency chain in writing-order from
the wrong end.

### Good pattern

Name the target and the dependency walk before any algebra:

> **Goal.** Derive the consumption Euler equation: the indifference
> condition between $c_0$ and $c_1$ along the household's intertemporal
> optimum. We need the household FOCs in $c_0$ and $c_1$, which require
> the Lagrangian, which requires preferences $\sum_t \beta^t u(c_t)$ and
> the budget constraint.

Then write forward along the walk:

$$
\mathcal{L}(c_0, c_1, \lambda) = u(c_0) + \beta\,u(c_1) - \lambda\!\left[c_0 + \tfrac{c_1}{1+r} - y_0 - \tfrac{y_1}{1+r}\right].
$$

FOCs:

$$
\partial_{c_0} \mathcal{L} = 0:\quad u'(c_0) = \lambda,
\qquad
\partial_{c_1} \mathcal{L} = 0:\quad \beta\,u'(c_1) = \tfrac{\lambda}{1+r}.
$$

Eliminate $\lambda$:

$$
u'(c_0) = \beta(1+r)\,u'(c_1).
$$

Each equation appears because the previous prose named the object it
computes. No placeholder is introduced without the reader holding its
purpose first.

## Identification training

Two short held-out snippets. For each, name the target, walk the
dependency chain backward to primitives, and flag whether the prose
makes the walk visible or which anti-pattern is present.

### Snippet 1

> We compute. Differentiate the market-clearing condition:
> $\partial_p D(p,\theta) - \partial_p S(p,\theta) = 0$ at the
> equilibrium price. By the implicit function theorem, $\mathrm dp/\mathrm
> d\theta = (\partial_\theta S - \partial_\theta D)/(\partial_p D -
> \partial_p S)$. Since the denominator is negative under standard
> regularity, the sign of $\mathrm dp/\mathrm d\theta$ matches the sign
> of $\partial_\theta S - \partial_\theta D$.

- **Target:** the comparative-static $\mathrm dp/\mathrm d\theta$ and its
  sign.
- **Backward walk:** $\mathrm dp/\mathrm d\theta$ ← IFT applied to market
  clearing ← partials of $D$ and $S$ in $p$ and $\theta$ ← regularity for
  the denominator's sign.
- **Visible in prose?** No. "We compute." names neither target nor
  strategy; the dependency walk is reconstructed by the reader after the
  fact. **Anti-pattern: deferred goal — target not named before the first
  displayed equation.** Fix: one sentence before the differentiation —
  "We sign $\mathrm dp/\mathrm d\theta$ by applying the IFT to market
  clearing; the denominator's sign comes from regularity, the numerator
  from the shift in supply minus demand."

### Snippet 2

> **Proof of Proposition 2.** [Twelve lines of algebra establishing that
> the value function is concave by composing concavity of $u$, linearity
> of the budget set, and preservation of concavity under maximization.
> Then twelve more lines establishing differentiability via the envelope
> theorem. No prose between the two blocks.] $\blacksquare$
>
> Concavity gives us the first-order conditions; differentiability lets us
> apply the envelope theorem in the next section.

- **Target:** Proposition 2 (concavity and differentiability of the value
  function).
- **Backward walk:** the proposition requires (a) concavity of $V$ ←
  concavity of $u$ + convexity of the budget set + max-preserves-concavity;
  and (b) differentiability of $V$ ← envelope theorem at the optimum.
- **Visible in prose?** Partially. The proposition implies a top-level
  target, but the two sub-arguments inside the proof carry no opening
  signposts and no transition prose between them. **Anti-pattern:
  signpost-less sub-arguments.** A reader entering at the differentiability
  block cannot recover its local goal from the surrounding prose. Fix:
  one sentence at each sub-argument's head ("We first establish concavity
  by ...; we then establish differentiability by ...") plus a transition
  at the join ("Having established concavity, we turn to
  differentiability.").
