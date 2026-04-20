# Structure Checklist — Pyramid Principle + Section Anatomy

> Load at the **IMPLEMENT phase** when the task drafts, restructures, or reviews the structure of a section or paper (methods section draft, intro revision, pre-submission structure check). The implementer walks §Gated Checklist as pre-handoff self-check; the reviewer walks the same items as verification.

Sources: Minto, B., *The Pyramid Principle* (governing idea, MECE, horizontal/vertical logic, SCQ / SCQA framing). Chaubey, V. (2018), *The Little Book on Research Writing* (RAP = Research question + Answer + Positioning, three-layer building: argument → outline → paragraphs, two-part introduction). Little Red Schoolhouse (UChicago) — introductions (LRS 5, 6), argument structure (LRS Arg 1–3), triage. Supporting: Brandeis, CGDev, IZA DP15057, Bellemare, Conversable Economist guidance on economics-paper structure.

The rules below describe how a well-structured research paper reads to its audience. Per the Iron Law (main SKILL.md), structural changes beyond the requested scope are *proposed*, not performed unilaterally.

## How-To

### Pyramid Principle (Minto)

**Governing idea first.** At every level of the document — the paper, the section, the paragraph — state the single governing idea *first*. The reader who reads only the first sentence should get the most important takeaway. The reader who reads the first two sentences should get the takeaway plus its scaffold. This is "descending structure" (Chaubey p. 24).

**MECE (Mutually Exclusive, Collectively Exhaustive).** The supporting points under a governing idea must not overlap (mutually exclusive) and must together cover the territory (collectively exhaustive). Overlapping points confuse the reader about what distinguishes them; gaps invite the question "what about X?" that the paper then fails to answer.

**Horizontal logic.** Sibling points at the same level of the pyramid must be parallel in *type* — all causes, all effects, all pieces of evidence, all counterarguments. Mixing types ("three reasons this works: first it's cheap; second, anecdote from 2019; third, our framework predicts it") is horizontal-logic failure.

**Vertical logic.** Each level answers the question raised by the level above. If the top of the pyramid is "X causes Y", the supporting points must each answer "*why* should I believe X causes Y?" — not "*what* is X?" or "*what* is Y?", which belong at a lower level.

**Test.** For any section, write the governing idea as a single sentence. Then write each supporting paragraph's first-sentence message. Check: do the supporting sentences collectively answer the question the governing sentence raises? Are they parallel in type? Is any one of them really a restatement of another?

### SCQ (Situation–Complication–Question) framing

**Used for introductions and for motivating any sub-argument.** The structure is:

- **Situation.** State the stable, agreed-upon context — what "everyone knows" about the domain. Reader nods.
- **Complication.** State the instability, gap, or tension in the situation. Reader frowns — something is unresolved.
- **Question.** State the question the complication poses. Reader leans in — they want the answer.
- (**Answer.** In SCQA, this is the paper's thesis or the section's main finding, delivered next.)

**Why it works.** SCQ positions the paper as the answer to a question the reader has just agreed is worth asking. Skipping S (launching straight into the gap) loses the reader who doesn't share the domain framing. Skipping C (situation → question with no tension) feels unmotivated.

### RAP — Research question, Answer, Positioning (Chaubey)

An economics paper's abstract and introduction should distill down to three letters (Chaubey p. 34):

- **R — Research question.** The version of the question the reader would ask. Put the paper at a level the reader can recognize as relevant to *their* concerns.
- **A — Answer.** The paper's main finding. High-level enough that it summarizes the detail below, specific enough that it is actually an answer.
- **P — Positioning.** The space in the literature R and A occupy. Lets the reader infer (1) the current state of knowledge, (2) a worthwhile direction to advance, (3) how this paper moves in that direction. (Chaubey p. 41.)

Most economics intros order it RAP or APR; Chaubey's default is RPA (p. 65). Choose for your audience.

### Two-part introduction (Chaubey, LRS 5–6)

An introduction has two jobs, in order (Chaubey p. 108):

**Part 1 — Provoke curiosity.** Help the reader learn about the context — why this question matters in the field. Transition: "what other papers do" → "what your paper does".

**Part 2 — Prepare the reader.** Help the reader visualize what is coming and provoke the right follow-up questions. Part 2 follows RAP and writes up paragraphs using section takeaways (Chaubey p. 126).

**Checks on Part 1:**

- Takes only as much brain space as an impatient reader will give before wanting to get to the paper's business (Chaubey p. 116).
- Provokes curiosity; doesn't just list "the importance of this topic".
- First sentence is not a grand contextual platitude that vaguely hints at importance (Chaubey p. 110) — the "world of X is important" opener.

**Checks on Part 2:**

- Previews the paper's main finding explicitly. No "mystery novel" — the reader should not have to read §6 to find out what the paper shows.
- Ends with a **table-of-contents paragraph** (or roadmap paragraph) telling the reader what the rest of the paper does, section by section.

### Title should state the finding

A title that states a topic (`Returns and Trading Volume`) is weaker than a title that states a finding (`Trading Volume Predicts Future Returns Only in the Cross-Section`). The strongest titles carry the governing idea of the whole paper — the reader who reads only the title should already know the answer the paper delivers. Exceptions: survey papers, methodology papers where the method is the finding.

### Section-level anatomy

**Introduction** (see above): Motivation → Gap → RAP (R → A → P or RPA) → Contribution → Roadmap.

**Methods / Data:** Data sources named and cited → sample construction (filters, exclusions, time range) described in the order the reader would apply them → specification equation stated → identification strategy (for causal papers) stated as the question it answers ("why should you believe this estimate is causal?") → control variables listed with rationale → standard-error discipline stated (clustering level and why).

**Results:** Main result first — the headline specification in the first table, with the coefficient of interest clearly labeled. Then robustness: sensitivity to sample, alternative specifications, alternative variable definitions. Each robustness check is introduced with the question it answers ("does this effect survive when we restrict to X?"). Do NOT bury the main finding behind five robustness tables.

**Conclusion:** Restate the research question and answer (not a new finding). State limitations honestly. Name the implication — for whom, and what follows next. Do NOT introduce new empirical findings in the conclusion (reviewers notice).

**Abstract:** RAP in 150–200 words. R explicit. A with magnitude (not just sign). P in one sentence.

### "No mystery novel" — front-load

Economics readers skim. The first sentence of each section should reveal what that section shows. The first sentence of the paper should reveal the finding. The abstract reveals the finding. The title reveals the finding where possible. Burying the point for dramatic effect is a readability failure, not a stylistic choice.

### Headings as reader-navigation

Headings exist to help the reader find what they want (Chaubey p. 71), not to organize the writer's thoughts. Write headings + takeaways from the reader's perspective: "Firm size does not explain the return premium" (reader-facing takeaway) beats "Size controls" (writer-facing filing label).

Subheadings should add *specifics* to the key words of the section heading (Chaubey p. 76) — not rename the same idea with different words. Key words are not key words if they are not used consistently across the paper (Chaubey p. 76).

### Chunking within sections

Miller's 7±2 rule (Chaubey p. 20): a reader holds about 7 items in working memory at once. If a section has more than about 7 top-level points, chunk into subsections of ≤7 points each. "Flat lists of 15 things" invites the reader to remember none.

## Gated Checklist

Walked top to bottom when the task drafts, restructures, or reviews structure. Severity markers apply:

- `[BLOCKING]` — fix to earn APPROVE. Anchors the Iron Law (no unilateral structural changes) and correctness.
- `[ADVISORY]` — best-practice heuristic. Reviewer MAY flag as MINOR. Does not block APPROVE.

### Scope and authorization

- `[BLOCKING]` Structural changes (reorder, add, remove sections or subsections; merge or split paragraphs at the subsection level) were *requested* by the researcher, or are *proposed* rather than performed.
- `[BLOCKING]` Author's argument and claim structure preserved. No section that previously argued for X now argues for X' as a side-effect of restructuring.

### Governing idea + MECE

- `[ADVISORY]` Each section has a single governing idea expressible in one sentence.
- `[ADVISORY]` Supporting paragraphs inside a section are MECE — no paragraph is a restatement of another; none obviously missing.
- `[ADVISORY]` Supporting paragraphs are parallel in type (horizontal logic) — all causes, all pieces of evidence, all counterarguments, etc.
- `[ADVISORY]` Each level answers the question raised above it (vertical logic).

### Introductions

- `[ADVISORY]` SCQ (Situation–Complication–Question) framing present and ordered correctly.
- `[ADVISORY]` Part 1 provokes curiosity without resorting to "the importance of X" platitudes (Chaubey p. 110).
- `[ADVISORY]` Part 2 previews the paper's finding explicitly — no mystery-novel opener.
- `[ADVISORY]` RAP (Research question / Answer / Positioning) statable from the intro alone (Chaubey p. 34).
- `[ADVISORY]` Intro ends with a roadmap paragraph listing the sections that follow.

### Section anatomy

- `[ADVISORY]` Methods / Data section orders content as the reader would apply it: sources → sample → specification → identification → controls → SEs.
- `[ADVISORY]` Results section leads with the main specification; robustness follows; main finding is not buried behind robustness tables.
- `[ADVISORY]` Conclusion restates the research question + answer; lists limitations; does not introduce new findings.
- `[ADVISORY]` Abstract: RAP in 150–200 words, with magnitude for A.

### Headings, titles, navigation

- `[ADVISORY]` Title states the finding where possible (or identifies the paper as survey / methodology).
- `[ADVISORY]` Section headings are reader-facing (takeaway-style), not writer-facing (filing-label-style) (Chaubey p. 71).
- `[ADVISORY]` Subheadings add specifics to the section heading's key words, not synonyms (Chaubey p. 76).
- `[ADVISORY]` No flat list of >7 top-level points inside a section (Miller 7±2, Chaubey p. 20).

### First-sentence storyline (Chaubey p. 128)

- `[ADVISORY]` Extracting the first sentence of every paragraph in the section produces a coherent storyline.

### Handoff

- `[BLOCKING]` Any structural change was documented in the handoff (chat / `PLAN.md` / review notes) so the researcher can verify it matches what was requested.
- `[ADVISORY]` Any structural concerns noticed but *not* acted on (because out of scope) were flagged for the researcher.

## Reviewer verdict protocol

Same as `writing/SKILL.md` §Three Concurrent Disciplines: **walk this file top to bottom, never halt on a failure, return APPROVE / REVISE.** Dependent findings noted in prose. Re-review after REVISE is narrow.
