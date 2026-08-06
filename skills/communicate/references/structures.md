# Structures

## Choose the form

- **One sentence:** one outcome and no caveat that changes it.
- **Nested pyramid (default):** several main points, each with its support or action beneath it.
- **Paragraph:** connected reasoning, narrative, or causality whose order a list would break.
- **Table:** repeated fields or exact comparisons across items.

## Build a nested pyramid

- **Make each top-level bullet a main point.** A reader who stops at that level still gets the answer or current state.
  - Put evidence and interpretation one level down.
  - Put paths, commands, methods, and optional detail at the deepest useful level.
- **Make each child support, limit, extend, or act on its parent.** Use a short, complete sentence, not a label, noun pile, or arrow chain.
- **Write headings that state the point.** `The merge loses 0.7% of observations` helps the reader find the answer; `Merge results` only names a topic.
- **Split by main points, not by template slots.**

## Adapt by surface

- **Conversation:** answer in the opening line. More than one supporting fact, caveat, or action: nest them below instead of extending the paragraph.
- **Task results:** lead with what the task established or delivered.
  - Render independent findings, evidence, caveats, and implementation details as a nested pyramid; reserve paragraphs for one connected argument.
  - Separate findings a researcher would quote or act on.
  - Keep verification sufficient to trust or reproduce the result.
  - Link implementation details and upstream facts.
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
- **Standalone report:** lead with the result the reader will use.
  - Follow with findings and limitations.
  - Leave methods, provenance, and appendices for readers who need depth.

## Diagnose structure

**Paragraph wall:** the outcome, evidence, caveat, and implementation details compete in one block.

> The panel build completed after joining CRSP and Compustat. We ran the merge on firm and month and retained 252,341 observations from 1994 through 2023. There were 1,663 observations without a CRSP match, which is 0.7% of the input, and the output is stored in `Data/panel.parquet`. This means the panel is ready for the alpha regressions, although analyses requiring unmatched firms need a different sample.

**Flat list:** shorter, but every item appears equally important and relationships disappear.

- The panel build completed.
- The panel has 252,341 observations from 1994 through 2023.
- The merge used firm and month.
- The output is in `Data/panel.parquet`.
- The merge dropped 1,663 observations, or 0.7%.
- Analyses requiring unmatched firms need a different sample.

**Nested pyramid:** the first level carries the result; support, caveat, and implementation details appear below it.

- The 252,341-observation panel is ready for the 1994–2023 alpha regressions.
  - Analyses requiring unmatched firms need a different sample.
  - The firm-month merge drops 1,663 observations, or 0.7%, without a CRSP match.
  - The maintained output is [`Data/panel.parquet`](../../../Data/panel.parquet).
