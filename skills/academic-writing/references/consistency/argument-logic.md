# Consistency: Argument Logic

> Load when Review or Polish mode targets **logical structure and evidence support** — claim-evidence mapping, causal-inference validity, alternative-explanations coverage, overclaiming / underclaiming, hedging calibration. One of eight `consistency/*.md` dimensions. Severity markers: `[BLOCKING]` must fix; `[ADVISORY]` recorded, never blocks. Issues touching **main causal claims** are blocking; issues on supporting or secondary claims are usually advisory.

## Scope

Covers the paper's **logical and evidential** dimension: do claims follow from the evidence, are causal claims backed by identification, are alternative explanations ruled out, is the rhetoric calibrated to the evidence. Out of scope: derivation correctness (`consistency/math.md`), numerical text-table match (`consistency/numerical.md`), citations (`consistency/citations.md`).

**The reviewer flags logical gaps; the researcher decides how to close them** (`SKILL.md §Preserve substance, polish prose`). Report with specific evidence and a recommended direction; do not rewrite claims.

## How-To

### Map the argument

Outline the paper's logical spine before checking:

- **Governing claim.** The paper's overall claim, in one sentence.
- **Sub-claims.** The handful that together deliver it.
- **Evidence.** Per sub-claim, the table / figure / derivation / cited result supporting it.

Every sub-claim has evidence; every piece of evidence works for some claim. Orphan claims (no evidence) and orphan evidence (no claim) are both flags.

### Classify each claim

- **Descriptive.** "X exists / is common / happens at rate Y." → summary statistics, documentation of existence.
- **Correlational.** "X is associated with Y in this sample." → regression coefficient with appropriate controls, or unconditional correlation with context.
- **Causal.** "X causes Y" — strongest, most support. → an identification strategy with stated assumptions.

**Claim-evidence match check.** Per main claim, does the evidence type match the claim type? Common failure: causal language on correlational evidence ("the effect of X" vs "the association between X and Y").

### Causal inference evaluation

Papers making causal claims:

- **Identification strategy stated.** "We identify by… [DiD / IV / RD / natural experiment / structural model]" — not "we control for X".
- **Key identifying assumptions stated.** Parallel trends for DiD; exclusion restriction + relevance for IV; continuity / no-manipulation for RD.
- **Assumptions' plausibility discussed** — at least one paragraph per assumption.
- **Tests of testable assumptions reported.** Pre-trends, overidentification, McCrary density.
- **Threats to validity addressed.** Selection bias, omitted-variable bias, reverse causality, measurement error — each ruled out by design or discussed.

### Alternative explanations

Per main empirical finding: *what else could produce this pattern?*

- **Reverse causality** — could Y be causing X?
- **Omitted variable** — is there a Z causing both X and Y?
- **Selection** — does the sample over-represent cases where X and Y move together?
- **Mechanical / definitional** — is X constructed from Y?
- **Anticipation** — are units responding to expected X, not realized X?
- **Measurement artifact** — is the "effect" a change in measurement, not reality?

The paper addresses the plausible ones explicitly, rather than listing "we cannot rule out X".

### Overclaiming / underclaiming

**Overclaiming.** Red flags:

- Causal verbs (`causes`, `induces`, `leads to`) on correlational evidence.
- "Proves" where "suggests" fits.
- Generalizing beyond sample scope ("in this sample of large US banks, X" → "banks X").
- Significance stars stated as "strong evidence" without effect-size context.

**Underclaiming**, equally a problem:

- Strong, well-identified, magnitude-meaningful effects buried in hedges ("results may possibly suggest that there could be a small relationship").
- Main findings buried in robustness tables.

### Hedging calibration

One hedge per claim; no stacking (`../style.md` §Single-hedge-per-claim). Per headline claim: is the hedge level proportional to the evidence strength?

### Logical gaps and circular reasoning

- **Skipped steps.** B asserted after A with the A→B link taken for granted.
- **Circular.** X defined in terms of Y, then shown to relate to Y.
- **Post-hoc.** Hypothesis formulated to fit already-seen results; tell from whether the specification menu reads as exploratory.
- **False dichotomy.** "Either X or Y explains this", where Z also exists.

## Gated Checklist

- `[BLOCKING]` **Argument spine traced** — governing claim, sub-claims, evidence mapping — in task notes or the status return.
- `[BLOCKING]` **Each main claim has matching evidence type** (descriptive / correlational / causal); mismatches flagged.
- `[BLOCKING]` **Causal claims** state an identification strategy and name its assumptions.
- `[BLOCKING]` **Plausible alternative explanations** addressed by the paper or flagged as gaps.
- `[BLOCKING]` **Overclaiming flagged** — causal verbs on correlational evidence, generalizations beyond sample scope.
- `[BLOCKING]` **No silent claim rewrites.** Gaps reported with specific evidence; the researcher decides (`SKILL.md §Preserve substance, polish prose`).
- `[BLOCKING]` **Tests of testable identifying assumptions** reported (pre-trends, overid, McCrary, as appropriate).
- `[ADVISORY]` **Underclaiming flagged** — findings stronger than the paper admits.
- `[ADVISORY]` **Hedging calibrated** — one hedge per claim, proportional to evidence strength.
- `[ADVISORY]` **Circular reasoning / post-hoc / false-dichotomy patterns** flagged.

## Output format

```
[SEVERITY] Logic: <one-line title>
Location: §N.M, page P
Claim type: <descriptive / correlational / causal>
Evidence type: <summary / correlation / identification strategy>
Current argument: <one-sentence summary>
Problem: <logical gap / overclaim / missing alternative / circular>
What would close it: <identification assumption / additional test / rewording / alternative addressed>
Recommendation: <escalate to researcher — logical issues are author calls>
Fix: mechanical | conventional | authorial   # see review.md §Fix tiers
```
