# Objective-First Derivations — Worked Example and Identification Training

> Loaded on demand from `references/integration.md` Section A. Carries the
> canonical bad/good walkthrough and identification-training drills for the
> objective-first principle. Teaching material — no checklist. The
> `[BLOCKING]` checklist lives in `references/integration.md` Section A.

## Principle

Start from the object the proof needs, then expand only the terms required
to evaluate that object. Forward writing runs along a backward dependency
walk: name the target, identify what the target requires, recurse only into
terms that are not already known. The good pattern keeps the proof linear
in the reader's experience — target object, needed derivative, structural
cancellation, canonical column, final substitution — so each equation
appears because the previous line named the object it computes.

## Worked bad pattern

Suppose the target is the covariance term in a differentiated portfolio FOC:

$$
\dot{\bar{\mathbf Q}} = \boldsymbol{\Sigma}^{-1}\!\left[\frac{1}{\gamma}\dot{\bar{\boldsymbol{\mu}}} - \dot{\boldsymbol{\Sigma}}\bar{\mathbf Q}\right].
$$

A confusing derivation starts by defining a local placeholder:

$$
z_j \equiv \left[\boldsymbol{\beta}_P^{\intercal}\mathbf e_E\right]_{US,j}.
$$

Then it derives return-loading columns in terms of $z_j$, solves for $z_j$,
and eventually uses this to compute $\dot{\boldsymbol{\Sigma}}$.

Why this is bad:

- The reader does not yet know why $z_j$ matters.
- The proof introduces notation that lives for only one algebraic detour.
- The derivation hides the objective, which is $\dot{\boldsymbol{\Sigma}}\bar{\mathbf Q}$.
- The route makes the cancellation look like a coincidence rather than a consequence of symmetry and market clearing.
- The proof risks using non-canonical notation even when the general solution already has the right objects.

The hidden logic is

$$
\dot{\boldsymbol{\Sigma}} \quad\text{requires}\quad \dot{\boldsymbol{\sigma}}_R \quad\text{requires}\quad \boldsymbol{\beta}_{P,E}.
$$

The bad derivation starts at the last object and works backward in the
writing — exactly the opposite of what the reader needs.

## Worked good pattern

If the FOC derivative needs $\dot{\boldsymbol{\Sigma}}\bar{\mathbf Q}$,
begin from the covariance identity in the general solution:

$$
\boldsymbol{\Sigma} = \boldsymbol{\sigma}_R\boldsymbol{\sigma}_R^{\intercal}.
$$

Take the derivative:

$$
\dot{\boldsymbol{\Sigma}} = \dot{\boldsymbol{\sigma}}_R\boldsymbol{\sigma}_R^{\intercal} + \boldsymbol{\sigma}_R\dot{\boldsymbol{\sigma}}_R^{\intercal}.
$$

Identify the only missing object via the canonical return-loading identity:

$$
\boldsymbol{\sigma}_R = \boldsymbol{\beta}_P^{\intercal}\mathbf G.
$$

Therefore the global-shock derivative satisfies:

$$
\dot{\boldsymbol{\sigma}}_{R,g} = \dot{\boldsymbol{\beta}}_P^{\intercal}\mathbf G\mathbf e_g + \boldsymbol{\beta}_{P,E}.
$$

Use structure before algebra. In the symmetric zero-flightiness benchmark,
the old dividend-state loading equations remain the symmetric zero-FX
system; the euro-risk perturbation only adds the antisymmetric
exchange-rate state. Symmetry and state-loading clearing kill the old-state
feedback term:

$$
\dot{\boldsymbol{\beta}}_P^{\intercal}\mathbf G\mathbf e_g = \mathbf 0,
$$

so the derivative reduces to:

$$
\dot{\boldsymbol{\sigma}}_{R,g} = \boldsymbol{\beta}_{P,E}.
$$

Now solve $\boldsymbol{\beta}_{P,E}$ from existing model equations:

1. Law of one price relates the starred and unstarred exchange-rate
   price-loading columns.
2. The $\hat E$ column of the return-loading equation maps price loadings
   into return loadings.
3. The $\hat E$ column of state-loading market clearing pins down the
   column.

For example:

$$
\boldsymbol{\beta}_{P,E}^{*} = \boldsymbol{\beta}_{P,E} - (\bar P_s,\bar P_f,\bar P_s,\bar P_f)^{\intercal},
$$

$$
\boldsymbol{\beta}_{R,E} = -(r+\alpha_E)\boldsymbol{\beta}_{P,E}, \qquad \boldsymbol{\beta}_{R,E}^{*} = -(r+\alpha_E)\boldsymbol{\beta}_{P,E}^{*}.
$$

State-loading clearing gives:

$$
\mathbf 0 = \boldsymbol{\Sigma}_0^{-1}\boldsymbol{\beta}_{R,E} + \boldsymbol{\Sigma}_0^{-1}\boldsymbol{\beta}_{R,E}^{*}.
$$

Substitute:

$$
\mathbf 0 = -(r+\alpha_E)\,\boldsymbol{\Sigma}_0^{-1}\!\left[2\boldsymbol{\beta}_{P,E} - (\bar P_s,\bar P_f,\bar P_s,\bar P_f)^{\intercal}\right].
$$

Since $\boldsymbol{\Sigma}_0$ is invertible:

$$
\boldsymbol{\beta}_{P,E} = \tfrac{1}{2}(\bar P_s,\bar P_f,\bar P_s,\bar P_f)^{\intercal}.
$$

Return to the objective:

$$
\dot{\boldsymbol{\Sigma}} = \dot{\boldsymbol{\sigma}}_R\boldsymbol{\sigma}_R^{\intercal} + \boldsymbol{\sigma}_R\dot{\boldsymbol{\sigma}}_R^{\intercal}.
$$

This keeps the proof linear: target object, needed derivative, symmetry
cancellation, canonical column, final substitution. The dependency walk is
visible in the prose itself — the proof needs
$\dot{\boldsymbol{\Sigma}}\bar{\mathbf Q}$, which requires
$\dot{\boldsymbol{\Sigma}}$, which requires $\dot{\boldsymbol{\sigma}}_R$,
which requires $\boldsymbol{\beta}_{P,E}$ — and each displayed equation
follows because the previous line named the object it computes.

## Identification training

Three short held-out snippets. For each, name the target object, walk the
dependency chain backward from target to primitives, and flag whether the
existing prose makes the walk visible or which anti-pattern is present.
The goal is to exercise the diagnostic move, not to enumerate every
failure mode.

### Snippet 1

> Define $\eta \equiv u'(c_1)/u'(c_0)$. Then $\eta = \beta(1+r)$ at the
> optimum, so $u'(c_1)/u'(c_0) = \beta(1+r)$. Substituting into the
> Lagrangian's first-order condition gives the Euler equation, which is
> what we wanted to derive.

- **Target object:** the consumption Euler equation
  $u'(c_0) = \beta(1+r)\,u'(c_1)$.
- **Backward walk:** the Euler equation requires the household FOCs in
  $c_0$ and $c_1$, which require the budget constraint and the
  Lagrangian.
- **Visible in prose?** No. The first move introduces $\eta$ as a local
  placeholder and only at the end reveals that the Euler equation was
  the target. **Anti-pattern: local placeholder before target named.**
  The placeholder $\eta$ does no structural work — substituting
  $u'(c_1)/u'(c_0)$ inline would lose nothing — and the reader holds an
  unmotivated symbol until the last sentence retroactively names the
  goal.

### Snippet 2

> We compute. Differentiate the market-clearing condition:
> $\partial_p D(p,\theta) - \partial_p S(p,\theta) = 0$ at the
> equilibrium price. By the implicit function theorem, $\mathrm dp/\mathrm
> d\theta = (\partial_\theta S - \partial_\theta D)/(\partial_p D -
> \partial_p S)$. Since the denominator is negative under standard
> regularity, the sign of $\mathrm dp/\mathrm d\theta$ matches the sign
> of $\partial_\theta S - \partial_\theta D$.

- **Target object:** the comparative-static $\mathrm dp/\mathrm d\theta$
  and its sign.
- **Backward walk:** $\mathrm dp/\mathrm d\theta$ requires the IFT
  applied to market clearing, which requires the partials of $D$ and $S$
  in $p$ and $\theta$, plus the regularity that pins the denominator's
  sign.
- **Visible in prose?** No. The opening "We compute." names neither the
  target nor a strategy, and the dependency walk is reconstructed by
  the reader after the fact. **Anti-pattern: deferred goal — target not
  named before the first displayed equation.** The fix is one sentence
  before the differentiation step: "We sign $\mathrm dp/\mathrm d\theta$
  by applying the implicit function theorem to market clearing; the
  denominator's sign comes from regularity, the numerator from the
  shift in supply minus demand."

### Snippet 3

> **Proof of Proposition 2.** [Twelve lines of algebra establishing that
> the value function is concave by composing concavity of $u$, linearity
> of the budget set, and preservation of concavity under maximization.
> Then twelve more lines establishing differentiability via the envelope
> theorem. No prose between the two blocks.] $\blacksquare$
>
> Concavity gives us the first-order conditions; differentiability lets us
> apply the envelope theorem in the next section.

- **Target object:** Proposition 2 (concavity and differentiability of
  the value function).
- **Backward walk:** the proposition requires (a) concavity of the value
  function, which requires concavity of $u$ + convexity of the budget
  set + a max-preserves-concavity argument; and (b) differentiability,
  which requires the envelope theorem applied to the optimum.
- **Visible in prose?** Partially. The proposition's existence implies a
  top-level target, but the two sub-arguments inside the proof carry no
  opening signposts and no transition prose between them.
  **Anti-pattern: signpost-less sub-arguments.** A reader entering at
  the differentiability block cannot recover its local goal from the
  surrounding prose. The fix is one sentence at the head of each
  sub-argument ("We first establish concavity by ...; we then establish
  differentiability by ...") plus a transition line at the join
  ("Having established concavity, we turn to differentiability.").
