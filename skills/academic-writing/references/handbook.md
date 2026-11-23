# Manuscript patterns

Apply [the reader test](../SKILL.md#the-reader-test) using these examples. See [Proofread](proofread.md) for reporting existing instances and [Where displaced material goes](../SKILL.md#where-displaced-material-goes) for material you cut.

## Construction detail

**Recognize it.** The sample sentence walks through the build in order or explains how a stray record was handled.

- **Before** — “We start with licensed childcare centers that accept subsidies, sort duplicate records by upload time, and retain the last record for each center.”
- **After** — “The sample covers licensed childcare centers that accept subsidies.”
- **Keep** — “The sample includes only centers licensed for overnight care.” Eligibility defines the population behind the overnight-care estimates.

## Verification and plausibility output

**Recognize it.** A residual, tolerance, or plausibility check shows that the calculation passed an internal check.

- **Before** — “We simulate waiting times at each service capacity. The simulation satisfies the queue balance equation to within $7.2\times10^{-17}$, and the resulting waits are plausible.”
- **After** — “We simulate waiting times at each service capacity.”
- **Keep** — “The sensor was offline during the gap in the observed series.” The note explains a visible break.

## Defensive framing

**Recognize it.** The sentence rebuts a view the paper gives readers little reason to hold. A neutral methods description may also end with an assurance that the method is conservative, robust, or safe. Look for the reason for the actual choice inside the defense.

- **Before** — “To rule out the possibility that we fitted the cutoff to the outcomes, we chose the date of the timetable change.”
- **After** — “We split the sample when the new timetable took effect.”
- **Keep** — “We pool adjacent districts because individual districts have too few inspections to estimate separate failure rates.” The reason explains a modeling choice in one sentence.

## Pre-emptive footnotes

**Recognize it.** An introduction footnote offers a robustness assurance whose evidence belongs with the result, or repeats a magnitude in another unit.

- **Before** — A footnote to the introduction’s delivery-delay result reads, “The decline also holds in the courier survey.” The results section already presents that evidence.
- **After** — Drop the footnote.
- **Keep** — A referee asks how the waiting-time adjustment was made. A footnote at the point of use explains it. “We estimate baseline waiting times on a separate set of calls and subtract the predicted baseline from each wait in the analysis sample.”

## Exactness replacing an approximation

**Recognize it.** The added decimals or exact averaging window leave the reader with the same magnitude, timing, and conclusion.

- **Before** — “Over the final seven operating days of the pilot, the mean wait was 17.062 minutes.” The draft described the wait as about seventeen minutes near the end of the pilot.
- **After** — “By the end of the pilot, waits averaged about seventeen minutes.”
- **Keep** — “We compare the seven days before the strike with the seven days after it ended.” The windows define the comparison.

### When an estimate changes

- **Before** — The draft says “A batch uses about 64 kilowatt-hours.” After the estimate moves to 64.3, the proposed edit says “A batch uses about 64.3 kilowatt-hours.”
- **After** — Retain “A batch uses about 64 kilowatt-hours.” The updated estimate still rounds to 64.
- **Keep** — If the estimate reaches 67.8, correct the sentence to “A batch uses about 68 kilowatt-hours.”

## Hedging a result the exhibit supports

**Recognize it.** An added hedge weakens the author’s description of a result the exhibit supports.

- **Before** — “The ridership curves appear broadly similar, although the evening counts fluctuate.” The curves nearly overlap throughout the figure.
- **After** — Restore the author’s “The ridership curves nearly overlap throughout the pilot.”
- **Keep** — The author writes “The survey suggests that riders switched routes” when few riders responded. For questions about claim strength, see [Substance is the author’s](../SKILL.md#substance-is-the-authors).

## Per-sentence significance

**Recognize it.** A result sentence reads the significance levels back from the table, group by group.

- **Before** — “We estimate a decline in complaints in both districts ($p=0.014$ inland and $p=0.074$ on the coast).” The table gives both intervals and test results.
- **After** — “We estimate a decline in complaints in both districts.”
- **Keep** — “The interval is wide enough to include a rise in complaints.” This matters when the paper asks whether the survey distinguishes a fall from a rise.

## Unrequested generality

**Recognize it.** The draft extends a result to additional cases outside its stated assumptions and the author’s request.

- **Before** — “The model gives all depots the same spoilage rate. Allowing depot-specific rates adds a correction based on each depot’s share of shipments.”
- **After** — “The model gives all depots the same spoilage rate.”
- **Keep** — “Because chilled goods spoil while they wait, the longest delivery delays account for most of the savings from faster dispatch.” The sentence interprets the result under the stated model.

## Specification differences between exhibits presented as one

**Recognize it.** A note explains an accidental difference in samples, controls, or transformations between exhibits presented as using one specification.

- **Before** — “The figure uses the table’s specification, except that the figure omits district fixed effects.”
- **After** — Report the missing fixed effects to the researcher for a code fix. Once both exhibits use the same specification, delete the note’s exception.
- **Keep** — “The first column counts scheduled trips. The second counts trips that departed.” Both definitions are needed when the table deliberately compares those measures.

## Pipeline vocabulary

**Recognize it.** Use [Style §Audience](style.md) to identify internal terms and artifacts.

- **Before** — “Each clinic-wave cell reports a median wait.”
- **After** — “We report the median wait for each clinic in each survey round.”
- **Keep** — “The regression includes clinic fixed effects.” The term names a feature of the specification.

## Restating a proposition, definition, or specification

**Recognize it.** The sentence repeats the proposition in words, defines the same object again, or copies the specification from the exhibit that establishes it.

- **Before** — After a proposition stating that an extra loading bay reduces delays only at capacity, the text adds, “In other words, an extra bay reduces delays only when all existing bays are occupied.”
- **After** — End with the proposition.
- **Keep** — “The next section tests this prediction using depot openings.” The signpost tells the reader how the analysis proceeds.

## A cut that changes a fact

**Recognize it.** A shorter version changes who is counted, what a symbol means, or what the exhibit shows.

- **Before** — “Each bar adds one service.” The last bar adds a group of services together.
- **After** — “The final bar adds counseling and transport together. Each earlier bar adds one service.”
- **Keep** — “The renewal rate is $R/E$, where $R$ is the number of renewals and $E$ the number of leases eligible to renew.” The denominator is needed to read the table.

## Detail by location

| Location | What belongs | What to flag |
|---|---|---|
| Main text | Definitions, equations, a brief sample description, and the economic meaning of the result. | Filter sequences, inference bookkeeping, and sensitivity ranges that leave the result unchanged. |
| Introduction footnotes | A clarification essential to following the introduction. | Duplicate conversions, side results, and assurances about objections the text gives readers little reason to raise. |
| Exhibit notes | What is shown, in exhibit order, and the definitions, units, markers, intervals, or sample needed to read it. Limit a table note to the length of the table body. | Repeated specifications, dispensable weighting or smoothing details, and prose that narrates the results. |
| Data appendix | Source, sample, and transformation for each series. Put sample selection in one short paragraph, following the source paper’s description when the construction is standard. | Attrition counts, one-record fixes, and counterfactuals about construction choices. A screen that defines coverage may belong here. |
| Methods or model appendix | Proofs, derivations, mechanisms, and calibration detail requested by a referee. | Repeated propositions, unsolicited extensions, and tolerances from internal checks. |
| Referee response | Details that answer the referee, including a line of verification arithmetic if it answers the question. | Extra digits showing how closely a check agrees and qualifications unrelated to the reply. |
