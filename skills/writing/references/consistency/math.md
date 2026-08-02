# Consistency: Math (derivations, proofs, statistical specifications)

> Load when Review or Polish mode targets **mathematical correctness** — derivation steps, proof integrity, statistical/econometric model specification, notation stability across sections. One of eight `consistency/*.md` dimensions. Severity markers: `[BLOCKING]` must fix; `[ADVISORY]` recorded, never blocks. A sign error in a main identifying equation is blocking; notation drift in an appendix lemma is usually advisory.

## Scope

Covers **correctness and stability of math content**: derivations step by step, proof integrity, statistical-model correctness, notation stability on the *meaning* side (typographic side in `consistency/notation.md`). Out of scope: prose terminology (`consistency/terminology.md`), table numbers matching prose (`consistency/numerical.md`).

The author owns the math (`SKILL.md §Preserve substance, polish prose`). *Flag* derivations that don't follow; do not rewrite them. Escalate genuinely broken steps.

## How-To

### Symbolic verification of derivations

Per algebraic step the paper claims:

- **Start state.** The equation immediately before the step.
- **End state.** The equation immediately after.
- **Claimed operation.** "Substituting (3) into (5)"; "taking the derivative"; "applying Jensen's inequality"; "by the law of total probability".
- **Verify.** Perform the operation on the start state; does it yield the end state?

Common failure modes:

- **Sign errors in rearrangement.** Terms cross the equality with the wrong sign.
- **Dropped terms.** A factor of `(1 - \rho)` or an expansion cross-term gets lost.
- **Incorrect factoring.** `a^2 - b^2 = (a-b)^2` (wrong) vs `(a-b)(a+b)` (right).
- **Chain rule mis-applied** on derivatives of composed functions.
- **Matrix dimensions.** `\mathbf{A} \mathbf{B}` valid only when inner dimensions match; transposes applied correctly (`(AB)^T = B^T A^T`).
- **Taylor expansion order.** First- vs second-order; remainder bounds; what is held constant.

### Numerical verification (sanity check)

Test complex algebraic claims with concrete numbers — it catches sign errors, dropped factors, and scaling mistakes symbolic inspection misses:

- Plug in `x = 0, 1, -1, 0.5` — does the claimed identity hold?
- Check boundary cases: parameter → 0, → ∞, → 1.
- Dimension / unit check: `dY / dX` has units `[Y] / [X]`.

### Notation meaning stability

Per defined object (coefficient, error term, parameter, set):

- Same meaning throughout. "The idiosyncratic error" in §3 must not silently become "the total error including measurement" in §5.
- Scope (time, sample) consistent: `\sigma_y` as the cross-sectional SD of `y` in §3 does not become the time-series SD in §5 without a rename.

Definitions once and only once: redefining `\theta` in §4 without saying so is a bug.

### Statistical / econometric specification

**Model assumptions.** Per model:

- **Error structure.** iid? Autocorrelated? Heteroskedastic? Stated explicitly?
- **Exogeneity.** Strict vs predetermined vs contemporaneous — stated?
- **Clustering.** Standard errors clustered at which level? Matches the identification level?
- **Distributional assumptions.** Normal? Finite moments? Stated where used?

**Delta method / asymptotic variance.** For transformed parameters (`\hat\beta / \hat\gamma`, probit marginal effects, VAR IRFs), the asymptotic variance formula is correctly derived.

**Moment conditions.** GMM / minimum distance: moment conditions stated; just- vs over-identified noted; weighting-matrix choice noted.

### Proofs

Per proof:

- **Structure clear.** Induction / contradiction / direct? Inductive hypothesis stated?
- **Proof assumptions match the theorem statement** — no hidden side-assumption.
- **Every "it follows that" step verifiable** without appeal to undocumented earlier lemmas.
- **Edge cases handled.** Parameter-space boundary, degenerate cases, measure-zero events.

### Appendix / body consistency

- Theorem in body, proof in appendix — statements match.
- Body says "see Appendix B"; Appendix B's contents match the promise.
- Notation identical across body and appendix (no silent appendix-only rename).

## Gated Checklist

- `[BLOCKING]` **Every derivation step walked** in the edited sections — each step either verifies or is flagged broken / unclear with location.
- `[BLOCKING]` **Broken steps flagged, not fixed** — escalated to the researcher, never silently rewritten (`SKILL.md §Preserve substance, polish prose`).
- `[BLOCKING]` **Definitions stable across the paper** — one meaning per defined object; drift reported.
- `[BLOCKING]` **Model assumptions stated where used.** Error structure, exogeneity, clustering, distributional assumptions.
- `[BLOCKING]` **Proofs' assumptions match theorem statements.**
- `[BLOCKING]` **Body ↔ appendix consistency verified** for every theorem / proposition proved in the appendix.
- `[ADVISORY]` **Numerical sanity check run on at least one key derivation.**
- `[ADVISORY]` **Dimension annotations recorded** for any dimension-sensitive step.
- `[ADVISORY]` **Boundary / edge cases discussed** where the result depends on them.

## Output format

```
[SEVERITY] Mathematical: <one-line title>
Location: eq. (N) / appendix §M / page P
Claim: "<quote the step>"
Verification attempt: <symbolic / numerical / what was tried>
Finding: <what does / does not check out>
Downstream impact: <what depends on this step>
Recommendation: <escalate to researcher / propose fix with specific formulation>
Fix: mechanical | conventional | authorial   # see review.md §Fix tiers
```
