# Structures

## Choose the form

- **One sentence:** one outcome and no material qualification.
- **Nested pyramid (default):** several takeaways, each with support or action.
- **Paragraph:** connected reasoning, narrative, or causality whose dependency order a list would fragment.
- **Table:** repeated fields or exact comparisons across peers.

## Build a nested pyramid

- **Make each top-level bullet a takeaway.** A skimmer reading only that level gets the governing result, decision, or state.
  - Put evidence and interpretation one level down.
  - Put a material caveat beside the support it qualifies.
  - Put mechanics or optional detail at the deepest useful level.
- **Use short, complete sentences.** A child states its relationship to the parent; it is not a label, noun pile, or arrow chain.
- **Write conclusion headings.** `The merge loses 0.7% of observations` guides retrieval; `Merge results` only names a topic.
- **Split by takeaways, not by template slots.** Omit a heading or bullet whose removal loses no claim, decision, caveat, or action.

## Adapt by surface

- **Conversation:** answer in the opening line. More than one supporting fact, caveat, or action: nest them below instead of extending the paragraph.
- **Task results:** lead with what the task established or delivered.
  - Render independent findings, evidence, caveats, and mechanics as a nested pyramid; reserve paragraphs for one connected argument.
  - Separate findings a researcher would quote or act on.
  - Keep verification sufficient to trust or reproduce the result.
  - Link implementation mechanics and upstream facts.
- **Planner update:** lead with the proposed shape or current planning state.
  - Nest the tradeoff or unresolved choice under the affected task.
  - End with the researcher decision only when one blocks the design.
- **Review:** lead with the verdict.
  - Give each finding a cited problem and actionable fix.
  - Omit a narration of checks that passed.
- **Handoff:** lead with the current state and next owner.
  - Keep blockers and disqualifying caveats adjacent.
  - Link the task, commit, and artifacts needed to resume.
- **Role return:** preserve the role skill's status schema and exact enum; nest only the deltas that schema permits.
- **Standalone report:** lead with the decision-relevant result.
  - Follow with findings and limitations.
  - Leave methods, provenance, and appendices for readers who need depth.

## Diagnose structure

**Paragraph wall:** the outcome, evidence, caveat, and mechanics compete in one block.

> The panel build completed after joining CRSP and Compustat. We ran the merge on firm and month and retained 252,341 observations from 1994 through 2023. There were 1,663 observations without a CRSP match, which is 0.7% of the input, and the output is stored in `Data/panel.parquet`. This means the panel is ready for the alpha regressions, although analyses requiring unmatched firms need a different sample.

**Flat list:** shorter, but every item appears equally important and relationships disappear.

- The panel build completed.
- The panel has 252,341 observations from 1994 through 2023.
- The merge used firm and month.
- The output is in `Data/panel.parquet`.
- The merge dropped 1,663 observations, or 0.7%.
- Analyses requiring unmatched firms need a different sample.

**Nested pyramid:** the first level carries the result; support, caveat, and mechanics reveal themselves in order.

- The 252,341-observation panel is ready for the 1994–2023 alpha regressions.
  - The firm-month merge drops 1,663 observations, or 0.7%, without a CRSP match.
    - Analyses requiring unmatched firms need a different sample.
  - The maintained output is [`Data/panel.parquet`](../../../Data/panel.parquet).
