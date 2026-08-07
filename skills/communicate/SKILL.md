---
name: communicate
description: Human-facing communication discipline for writing, rewriting, distilling, and reviewing conversation, task files, planning updates, results, reports, reviews, handoffs, and documentation. Use for every message or artifact a human will read; load with using-superra in every superRA role.
---

# Communicate

**Budget for communication.** Before returning, plan the message as deliberately as the work itself.

**Write for a reader with no session context.** They have the artifact and the repo — not your conversation, your scratchpad, or the vocabulary you built while working.

- Session vocabulary: use the standard term, or define yours at first use.
- Process-internal artifacts: link the committed file, not a scratch path, branch name, or dispatch label.
- Editing-history cues: "the table now defines" and "the updated script" have no *before* for this reader.
- A correction is an instruction, not content. "No, this is not a robustness check" means fix or delete the sentence; the reader never saw the wrong version, so a line denying it is a new claim they had no reason to doubt.
- Reintroduce a term, sample, or object when it returns after a long gap.

## Put the answer first

- **Lead with the outcome, decision, or honest current state.** Unresolved work: say what is settled and what is still open. A reader who stops at the top level still has the answer.
  - **Nest support under the claim it changes** — evidence, interpretation, limitation, next action, and any caveat that narrows or reverses it.
  - **Push implementation detail to the deepest level, or link it** — commands, paths, commits, methods.
- **Make each child support, limit, extend, or act on its parent.** Use a short, complete sentence, not a label, noun pile, or arrow chain.
- **Give sibling bullets the same grammatical form.** All noun phrases, or all imperatives, or all full sentences.
- **Write headings that state the point.** `The merge loses 0.7% of observations` helps the reader find the answer; `Merge results` only names a topic.
- **Make each section survive being read alone.** Readers skim and agents retrieve fragments.
- **Split by main points, not by template slots.**

## Choose the form

- **One sentence:** one outcome and no caveat that changes it.
- **Nested pyramid (default):** several main points, each with its support or action beneath it.
- **Paragraph:** connected reasoning, narrative, or causality whose order a list would break.
- **Table:** repeated fields or exact comparisons across items.

## Write the paragraph

- **Put the paragraph's message in its first sentence.** No exceptions.
- **Start each sentence with something the reader already has; end with what is new.**
  - Test: read the subjects of three consecutive sentences. Each subject repeating or succeeding the previous topic means the flow holds; three fresh terms mean it broke.
  - Introducing a topic, or running a deliberate parallel list: fresh subjects are the job.
- **One idea per paragraph.** An idea that needs more than five or six sentences is two ideas.
- **Put the transition at the start.** `however`, `in contrast`, `consequently` belong at the front of the pivoting sentence, not buried mid-sentence.

## Shape by surface

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
  - The maintained output is [`Data/panel.parquet`](../../Data/panel.parquet).

## Keep only useful content

- **Keep a sentence or bullet only when it adds a claim, evidence, caveat, decision, or action.**
  - Preserve words that show cause, contrast, conditions, or sequence.
- **State each fact once.** Put the full detail where it is produced or maintained; link there elsewhere.
- **Keep one example.** Add a second only when it teaches a different case.
- **Shorten by dropping whole units.** Cut a bullet or a section before compressing the sentences inside one.
- **Report only what you can point to.** Link the artifact, output, source, or commit behind every claim the reader may rely on.
- **Choose clear over short.** Explain dependencies, surprising results, irreversible actions, and easy-to-miss caveats in full.

## Write sentences a cold reader parses once

Each rule fires on a real reading problem. Applying one to a line that already reads clearly is a failed edit.

- **Name the actor and the action.**
  - "The hook blocks the edit" — not "Blocking is performed."
  - "The firm-month merge drops 1,663 observations" — not "There is some observation loss."
  - Passive voice when the actor is unknown or irrelevant.
- **Delete the clause that survives deletion.** Read the sentence without it; if it still works, it was filler.
  - "in order to" → "to"; "serves as" → "is"; "utilize" → "use".
  - "It is worth noting that the merge drops 0.7%." → "The merge drops 0.7%."
  - "This is a significant improvement." → give the number, or cut the sentence.
  - Say what a thing is, not what it is not: never "it's not X, it's Y."
- **Keep the hedge that changes a decision.**
  - Keep: "The estimate is probably biased downward."
  - Cut: "somewhat unclear results were obtained" — say what the results are.
  - Never stack hedges: "may possibly suggest" claims less than "suggests".
- **Give `this`, `it`, and `these` a noun** when more than one recent noun could be the antecedent: "this drop", "this specification".
- **Replace a vague quantifier with the count.** "several observations" → "1,663 observations"; "a number of tests" → "three tests". Keep the vague form when the count genuinely does not matter.
- **Break a stack of three or more nouns.** "firm-year panel data regression specification" → "the specification of the firm-year panel regression". Keep recognized terms of art intact.
- **Use one name per concept.** No rotating synonyms, and no abbreviation you invented (`cfg`, `impl`) — the reader decodes it and the tokenizer saves nothing. Define an unfamiliar term at first use.
- **Write short, complete sentences.** In prose, no fragments and no arrow chains (`merge → 0.7% → fine`).
- **Preserve voice.** Technical vocabulary, first-person voice, emphasis, and meaningful punctuation survive an edit.

## Route the work

- **Rewriting, distilling, or auditing why text is hard to read:** load [rewrite.md](references/rewrite.md).
- **Source citations, math, tables, figures, or raw HTML:** load [markdown.md](references/markdown.md).
- **Permanent standalone Markdown:** load [baseline-io.md](references/baseline-io.md). Task-local companions follow `using-superra/references/task-companion-files.md`.
- **Manuscript prose:** compose this skill with `superRA:academic-writing`; that skill owns academic argument, voice, citations, and venue conventions.

## Final pass

- **Read only the opening and top-level bullets.** They should carry the answer or current state. In prose sections, the first sentences of consecutive paragraphs should read as a coherent storyline on their own.
- **Apply § Keep only useful content once.** Restore any relationship that became unclear.
- **Check the diff, not the length.** No claim got stronger, no caveat disappeared, no voice flattened.
