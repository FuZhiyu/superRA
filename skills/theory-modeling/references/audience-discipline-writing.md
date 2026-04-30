# Audience Discipline (Writing)

Reference for any agent producing prose that ships in a paper draft, an
appendix, a response letter, or any other artifact a third party will
read. Loaded on demand whenever a task touches paper sources
(`.tex`, `.md`, etc.).

## The failure mode: not modeling the reader's context

The recurring failure is not "wrong tone" or "wrong style". It is
**perspective collapse**: the agent writes from inside its own context
window — the chat history, the referee report, the PLAN.md task, the
user's last instruction — and forgets that none of that context exists
for the reader.

The reader of the published paper has only the paper. They do not know:

- there was a revision round
- there were referee reports
- there was a conversation with a user
- there was an LLM, a PLAN.md, a task, a workflow
- which sections were added "for the referee" vs. originally planned
- which case is the "main" one and which is the "illustration" in the
  agent's mental model
- what the agent considered and rejected

Anything that lives only in the chat / workflow context but not in the
paper itself is **invisible to the reader**. Sentences that quietly
assume otherwise read as non-sequiturs at best and as breaking the
fourth wall at worst.

The discipline: before writing or saving any paper sentence, ask
*what the reader knows at this point of the document*, given only what
the paper itself has said up to that line. Write only sentences that
make sense from inside that reader's head.

## The three communication channels

Keep them strictly separate:

1. **Chat with the user.** Free to reference the workflow, the referee,
   the task, the agent's reasoning, the alternatives considered.
2. **Handoff docs (`PLAN.md`, `RESULTS.md`, review notes).** Internal
   record. Free to reference task structure, decisions, what was checked.
3. **Paper body / appendix / response letter.** Audience-facing. The
   reader has only the document in front of them. Each document has its
   own audience: the response letter is read by the editor and referees
   who *did* see the report; the paper body is read by the field, who
   did not.

A leak from channel 1 or 2 into channel 3 is the failure mode below.

## Symptoms — what perspective collapse looks like

Real examples from `flighty_capital_flow_appendix.tex`:

> "The one-tree case is not the main theorem, but it is the cleanest
> comparative-static illustration."

This sentence makes sense in chat ("I'm including the one-tree case
because it's a cleaner illustration than the main theorem"). It does
not make sense to a reader who has no idea which result the agent
considered "the main theorem" or why the comparison is being volunteered.
The reader is at a subsection break and just wants the content. Trim:
"Specialize to a one-tree economy. ..."

> "To study the referee's endogeneity concern, I specialize to ..."

The reader of the paper does not know there is a referee, a report, or
a concern. The sentence references context that exists only in the
chat / response letter. Replace with the substantive motivation a fresh
reader can follow: "To isolate the role of [endogenous object X], I
specialize to ..."

## A reader-context test

Before each paragraph or transition sentence, fill in:

> *At this point in the paper, the reader knows {X, Y, Z} and has just
> read {previous sentence}. What do they need next?*

Then write only what passes that test. If a sentence answers a question
the reader is not asking — "why is this section here?", "why this case
and not another?", "is this what the referee wanted?" — it is leaking
chat context into the paper.

## Common leaks and fixes

| Leak | Reader's reaction | Fix |
|---|---|---|
| "As discussed in Task 3, ..." | "What is Task 3?" | Cite section / equation number, or just state the fact. |
| "The user asked me to ..." | "What user?" | State the case directly. |
| "To address the referee's concern, ..." | "What referee?" | State the substantive motivation. |
| "This is the simpler version; the full proof is in the appendix." | Sometimes useful, often noise. | Keep only when the signpost helps the reader navigate. |
| "We chose this normalization for tractability." | "Whose tractability?" | Either give the economic content of the normalization or drop the aside. |
| "In response to comments, ..." | "Whose comments?" | Just present the result. |
| "This addresses the concern that ..." | "Whose concern?" | State what the result says, not what worry it answers. |
| "It is worth noting / it should be emphasized that ..." | Filler. | Either state the point plainly or cut. |
| "I now turn to ..." (as a self-monologue) | Acceptable as a guidepost. Suspect when it justifies the agent's choice rather than orienting the reader. | Keep when it orients; cut when it explains. |

## Workflow vocabulary that should never appear in the paper body

`task`, `PLAN.md`, `RESULTS.md`, `user`, `agent`, `LLM`, `as requested`,
`the reviewer asked`, `in this round`, `for now`, `TODO`, `placeholder`,
`XXX`, `draft note`. `referee` and `reviewer` are fine in the response
letter and forbidden in the paper body unless used as a generic noun
unrelated to the current revision (rare).

## Where each kind of content does belong

| Content | Right home |
|---|---|
| "What the result is" | Paper body. |
| "How the result is proved" | Paper body / appendix. |
| "Why a researcher cares about this case" (audience-facing motivation) | Paper body, in the reader's terms. |
| "Why we chose this case in this revision" (workflow motivation) | `RESULTS.md` task block; never the paper. |
| "This responds to Referee N's concern about X" | Response letter only. |
| "What was tried and rejected" | `RESULTS.md`. A footnote in the paper only if genuinely informative for the reader. |

## Reviewer-side check

A reviewer agent walking paper prose should grep / scan for:

- The workflow-vocabulary list above.
- Sentences whose *subject* is the writing process or the agent's
  decisions rather than the economic content.
- "Referee", "reviewer", "round", "revision", "concern" inside paper
  body files (not the response-letter file).
- Sentences that compare a section to "the main theorem" or "the main
  case" without that comparison being defined for the reader.

Flag as `[BLOCKING]` in paper body files. `[ADVISORY]` in working notes
where leaks are tolerable but worth cleaning before merge.

## See also

- `audience-discipline-modeling.md` — perspective discipline applied to
  proof, derivation, and theory-appendix prose, where leaks are subtler
  because meta-commentary often masquerades as legitimate roadmap.
