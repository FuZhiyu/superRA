# Rewrite

## Freeze invariants

- **Exact literals:** code, commands, paths, URLs, citations, equations, error text, names, dates, versions, numbers, units, and status tokens.
- **Meaning:** propositions, conditions, caveats, commitments, dependencies, and claim strength.
- **Voice:** useful terminology, emphasis, rhythm, and register unless they make the text harder to understand.

## Give every passage one verdict

The symptom picks it.

- **Keep** — unique information the reader needs and this document owns. *The 0.7% match failure, in the results file that produced it.*
- **Point** — content already maintained in a linked source. *The merge method, owned by the analysis script.*
- **Merge** — two passages overlap, and each carries a distinct fact. *"252,341 observations" in one bullet and "1994–2023" in another, both about one panel.*
- **Drop** — repetition, outdated state, filler, or implementation detail the reader does not need. *"We then re-ran the merge after fixing the path."*
- **Escalate** — incompatible claims or literals, or a deletion that would decide an authorial, research, or acceptance question. *Two different observation counts for the same table.*

Repair a sentence-level defect rather than dropping the passage that carries it: indirection, ambiguity, a missing actor, or a claim that outruns its evidence is fixed with [SKILL.md § Fix the sentence](../SKILL.md#fix-the-sentence).

The verdicts then set the scope:

- **Mostly Keep, with local Drops and Merges** — patch in place and leave the order alone.
- **The hierarchy itself hides the answer** — paragraph wall, flat list, process chronology, or stale headings: rebuild it per `SKILL.md` § Pyramid structure.
- **Any Escalate** — raise it before rewriting. Continuing past a conflict picks an answer silently.

## Preserve harmless style

- **Identify the reading problem before changing a style marker.** Preserve an em dash, domain term, hedge, first-person voice, contrast, list, or repeated cadence when it does not slow understanding.
- **Reject detector mechanics.** No banned-word lists, punctuation quotas, vocabulary tiers, rhythm targets, type-token targets, personality injection, or repeated passes until markers disappear. Inferring authorship is never the goal.

## Rebuild from the kept facts

1. **Write the answer.** State the outcome, decision, or honest current state without strengthening the source.
2. **Arrange dependencies.** Put evidence, caveats, and action beneath the claim they support or limit; preserve causal and temporal order.
3. **Replace copies with pointers.** Keep interpretation here only when this artifact owns it.
4. **Repair the connective tissue.** Add only the transitions and explicit relationships the new order requires.
5. **Delete superseded structure.** Remove stale headings, duplicate summaries, process chronology, and empty sections.

**Make the smallest edit that resolves each defect.** The rule caps the size of each fix, not their number.

## Verify

- **Word reduction alone is not a pass.** Every change makes the answer easier to find or the meaning easier to follow.
- **Invariants:** compare every retained passage against § Freeze invariants.
- **Evidence:** every retained claim the reader may rely on still links its artifact, output, source, or commit.
- **Cold read:** the first layer stands alone and each child has an explicit relationship to its parent.
