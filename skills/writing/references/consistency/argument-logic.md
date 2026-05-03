# Consistency: Argument Logic

> Load when Review or Polish mode targets **logical structure and evidence support** — claim-evidence mapping, causal-inference validity, alternative-explanations coverage, overclaiming / underclaiming, hedging calibration. One of eight `consistency/*.md` dimensions. Severity markers shape reviewer output: `[BLOCKING]` items must be reported; `[ADVISORY]` items are flaggable as MINOR. Issues touching **main causal claims** are `CRITICAL` / `MAJOR`; issues on supporting or secondary claims may be `MINOR`.

Source dimensions harvested from `draft-reviewer:argument-logic-reviewer` (logical flow, claim-evidence, causal-inference, alternative explanations, overclaiming / underclaiming, post-hoc reasoning).

## Scope

Covers the **logical and evidential** dimension of the paper: do claims follow from the evidence? Are causal claims backed by identification? Are alternative explanations ruled out? Is the rhetoric calibrated to the evidence? Out of scope: mathematical correctness of derivations (`consistency/math.md`), numerical text-table match (`consistency/numerical.md`), citations (`consistency/citations.md`).

**The reviewer flags logical gaps; the researcher decides how to close them** (`SKILL.md §Preserve substance, polish prose`). Do not rewrite claims unilaterally; report with specific evidence and recommended direction.

## How-To

### Map the argument

Before checking, outline the paper's logical spine:

- **Governing claim.** What does the paper claim overall? One sentence.
- **Sub-claims.** The handful of claims that together deliver the governing claim.
- **Evidence.** For each sub-claim, which table / figure / derivation / cited result supports it?

Every sub-claim should have evidence; every piece of evidence should be doing work for some claim. Orphan claims (no evidence) and orphan evidence (no claim) are both flags.

### Classify each claim

Three types:

- **Descriptive.** "X exists / is common / happens at rate Y."
- **Correlational.** "X is associated with Y in this sample."
- **Causal.** "X causes Y." (Strongest, requires most support.)

Each type demands specific evidence:

- Descriptive → summary statistics, documentation of existence.
- Correlational → regression coefficient with appropriate controls, or unconditional correlation with context.
- Causal → an identification strategy with stated assumptions.

**Claim-evidence match check.** For each main claim, does the evidence type match the claim type? Common failure: causal language used for correlational evidence ("the effect of X" vs "the association between X and Y").

### Causal inference evaluation

For papers making causal claims:

- **Identification strategy stated.** "We identify by... [DiD / IV / RD / natural experiment / structural model]." Not just "we control for X".
- **Key identifying assumptions stated.** Parallel trends for DiD; exclusion restriction + relevance for IV; continuity / no-manipulation for RD; etc.
- **Assumptions' plausibility discussed.** At least one paragraph on why each assumption is defensible here.
- **Tests of testable assumptions reported.** Pre-trends; overidentification; McCrary density; etc.
- **Threats to validity addressed.** Selection bias, omitted-variable bias, reverse causality, measurement error — each either ruled out by the design or discussed.

### Alternative explanations

For each main empirical finding, ask: *what else could produce this pattern?* Common alternatives:

- **Reverse causality** — could Y be causing X instead?
- **Omitted variable** — is there a Z that causes both X and Y?
- **Selection** — does the sample over-represent cases where X and Y move together?
- **Mechanical / definitional** — is X literally constructed from Y?
- **Anticipation** — are units responding to expected X, not realized X?
- **Measurement artifact** — is the "effect" a change in measurement, not reality?

The paper should address the plausible ones explicitly, not just list "we cannot rule out X".

### Overclaiming / underclaiming

**Overclaiming.** Red flags:

- Causal verbs (`causes`, `induces`, `leads to`) for correlational evidence.
- "Proves" where "suggests" is appropriate.
- Generalizing beyond sample scope ("in this sample of large US banks, X" → "banks X").
- Significance-stars stated as "strong evidence" without effect-size context.

**Underclaiming.** Also a problem:

- Strong, well-identified, magnitude-meaningful effects described with excessive hedging ("results may possibly suggest that there could be a small relationship").
- Main findings buried in robustness tables.

### Hedging calibration

One hedge per claim; no stacking. See `writing/references/style.md` §Single-hedge-per-claim. Reviewer perspective: read each headline claim and ask "is the hedge level proportional to the evidence strength?".

### Logical gaps and circular reasoning

- **Skipped steps.** The paper asserts B after A, but the link from A to B is taken for granted.
- **Circular.** X defined in terms of Y, then X shown to be related to Y.
- **Post-hoc.** The hypothesis is formulated to fit the already-seen results. Tell by: whether the paper's specification menu reads as exploratory.
- **False dichotomy.** "Either X or Y explains this", where Z also exists.

## Gated Checklist

- `[BLOCKING]` **Argument spine traced.** Governing claim + sub-claims + evidence mapping documented in the handoff.
- `[BLOCKING]` **Each main claim has matching evidence type** (descriptive / correlational / causal). Mismatches flagged.
- `[BLOCKING]` **Causal claims** have an identification strategy stated and its assumptions named.
- `[BLOCKING]` **Plausible alternative explanations** addressed by the paper or flagged as gaps.
- `[BLOCKING]` **Overclaiming flagged** — causal verbs for correlational evidence; generalizations beyond sample scope.
- `[BLOCKING]` **No silent claim rewrites.** Logical gaps are reported with specific evidence; the researcher decides how to address (`SKILL.md §Preserve substance, polish prose`).
- `[BLOCKING]` **Tests of testable identifying assumptions** reported (pre-trends / overid / McCrary / etc. as appropriate).
- `[ADVISORY]` **Underclaiming flagged** — findings that are stronger than the paper admits.
- `[ADVISORY]` **Hedging calibrated** — no stacked hedges; one hedge per claim proportional to evidence strength.
- `[ADVISORY]` **Circular reasoning / post-hoc / false-dichotomy patterns** flagged if present.

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
Auto-fixable: Yes / No
```
