# Consistency: Math (derivations, proofs, statistical specifications)

> Load when a task involves checking **mathematical correctness** — derivation steps, proof integrity, statistical/econometric model specification, notation stability across sections. One of eight `consistency/*.md` dimensions. Severity: `[BLOCKING]` must fix to earn APPROVE; `[ADVISORY]` flaggable as MINOR.

Source dimensions harvested from `draft-reviewer:mathematical-reviewer` (derivations and proofs, notation consistency, statistical specifications, common errors catalog).

## Scope

Covers **correctness and stability of math content**: derivation step-by-step, proof integrity, statistical-model correctness, cross-section notation stability (on the *meaning* side — the typographic stability side is in `consistency/notation.md`). Out of scope: prose terminology (`consistency/terminology.md`), table numbers matching prose (`consistency/numerical.md`).

Per the Iron Law (main SKILL.md): the author owns the math. Your job as reviewer is to *flag* derivations that don't follow — not to rewrite them. Where a step is genuinely broken, escalate.

## How-To

### Symbolic verification of derivations

For each algebraic step the paper claims:

- **Start state.** Read the equation immediately before the step.
- **End state.** Read the equation immediately after.
- **Claimed operation.** "Substituting (3) into (5)"; "taking the derivative"; "applying Jensen's inequality"; "by the law of total probability".
- **Verify.** Perform the operation on the start state; does it yield the end state?

Common failure modes:

- **Sign errors in rearrangement.** Terms move across the equality with the wrong sign.
- **Dropped terms.** A factor of `(1 - \rho)` or a cross-term from an expansion gets lost.
- **Incorrect factoring.** `a^2 - b^2 = (a-b)^2` (wrong) vs `(a-b)(a+b)` (right).
- **Chain rule mis-applied.** For derivatives of composed functions.
- **Matrix dimensions.** `\mathbf{A} \mathbf{B}` valid only if inner dimensions match; transposes applied correctly (`(AB)^T = B^T A^T`).
- **Taylor expansion order.** First-order vs second-order; remainder bounds; what's being held constant.

### Numerical verification (sanity check)

For a complex algebraic claim, test with concrete numbers:

- Plug in `x = 0, 1, -1, 0.5` — does the claimed identity hold?
- Check boundary cases: parameter → 0, → ∞, → 1.
- Dimension / unit check: `dY / dX` should have units `[Y] / [X]`.

Numerical sanity-checking catches sign errors, dropped factors, and scaling mistakes that symbolic inspection misses.

### Notation meaning stability

For every defined object (coefficient, error term, parameter, set):

- Same meaning throughout the paper. An object that is "the idiosyncratic error" in §3 must not silently become "the total error including measurement" in §5.
- Scope (time, sample) consistent: if `\sigma_y` is the cross-sectional SD of `y` in §3, it doesn't become the time-series SD in §5 without a rename.

Definitions once-and-only-once: redefining `\theta` differently in §4 without saying so is a bug.

### Statistical / econometric specification

**Model assumptions.** For each model:

- **Error structure.** iid? Autocorrelated? Heteroskedastic? Stated explicitly?
- **Exogeneity.** Strict exogeneity vs predetermined vs contemporaneously exogenous — stated?
- **Clustering.** Standard errors clustered at which level? Matches the identification level?
- **Distributional assumptions.** Normal? Finite moments? — stated where used?

**Delta method / asymptotic variance.** For transformed parameters (`\hat\beta / \hat\gamma`, marginal effects of probit, IRFs from a VAR), the asymptotic variance formula is correctly derived.

**Moment conditions.** For GMM / minimum distance: moment conditions stated; just-identified vs over-identified noted; weighting matrix choice noted.

### Proofs

For each proof:

- **Proof structure clear.** Induction / contradiction / direct? Inductive hypothesis stated?
- **Assumptions in proof statement match the theorem statement.** No hidden side-assumption used in the proof that is not in the theorem.
- **Every "it follows that" step is verifiable** without appeal to undocumented earlier lemmas.
- **Edge cases handled.** Boundary of parameter space, degenerate cases, measure-zero events.

### Appendix / body consistency

- Theorem in body and proof in appendix — statement matches.
- Body says "see Appendix B"; Appendix B's contents match what the body promised.
- Notation identical across body and appendix (no silent rename for appendix-only use).

## Gated Checklist

- `[BLOCKING]` **Every derivation step walked.** For each step in the derivations of the edited sections, either (a) the step verifies or (b) the step is flagged as broken / unclear with location.
- `[BLOCKING]` **Broken steps flagged, not fixed.** Per the Iron Law, math errors are escalated to the researcher; the reviewer reports, does not silently rewrite.
- `[BLOCKING]` **Definitions stable across the paper.** Every defined object has one meaning; any drift is reported.
- `[BLOCKING]` **Model assumptions stated where used.** Error structure, exogeneity, clustering, distributional assumptions.
- `[BLOCKING]` **Proofs' assumptions match theorem statements.**
- `[BLOCKING]` **Body ↔ appendix consistency verified** for every theorem / proposition with proof in the appendix.
- `[ADVISORY]` **Numerical sanity checks run on at least one key derivation** — concrete values plugged in.
- `[ADVISORY]` **Matrix-dimension / vector-dimension annotations attached** in handoff for any dimension-sensitive step.
- `[ADVISORY]` **Boundary / edge cases discussed** where the result depends on them.

## Reviewer verdict protocol

Walk top to bottom, never halt, return APPROVE / REVISE. Mathematical issues are almost always `MAJOR` or `CRITICAL` — a sign error in a main identifying equation is an APPROVE-blocker; a notation drift in an appendix lemma may be `MINOR`.

## Output format

```
[SEVERITY] Mathematical: <one-line title>
Location: eq. (N) / appendix §M / page P
Claim: "<quote the step>"
Verification attempt: <symbolic / numerical / what was tried>
Finding: <what does / does not check out>
Downstream impact: <what depends on this step>
Recommendation: <escalate to researcher / propose fix with specific formulation>
```
