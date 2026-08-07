# Rewrite and Distill

## Freeze invariants

- **Exact literals:** code, commands, paths, URLs, citations, equations, error text, names, dates, versions, numbers, units, and status tokens.
- **Meaning:** propositions, conditions, caveats, commitments, dependencies, and claim strength.
- **Voice:** useful terminology, emphasis, rhythm, and register unless they make the text harder to understand.

## Audit by cost

Diagnose what slows the reader. This audit never tries to infer authorship or make prose "sound human."

- **Redundancy:** two passages make the same contribution.
  - Merge overlapping passages, link to the maintained source, or drop the repeat.
- **Indirection:** framing, meta-commentary, process narration, or a missing actor delays the claim.
  - Repair with [SKILL.md § Write sentences a cold reader parses once](../SKILL.md#write-sentences-a-cold-reader-parses-once); keep framing only when it changes interpretation.
- **Vague claims:** importance language, vague attribution, or a broad interpretation outruns the evidence.
  - State exactly what the evidence supports, or remove the claim.
- **Buried structure:** a topic heading, paragraph wall, or flat list hides priority and relationships.
  - Rebuild the visible hierarchy; keep connected reasoning in prose.
- **Ambiguity:** fragments, invented abbreviations, unclear pronouns, compressed dependencies, or inconsistent names force reconstruction.
  - Repair with the same section; restore the full relationship rather than the shortest phrasing.

### Preserve harmless style

- **Identify the reading problem before changing a style marker.** Preserve an em dash, domain term, hedge, first-person voice, contrast, list, or repeated cadence when it does not slow understanding.
- **Reject detector mechanics.** Do not use banned-word lists, punctuation quotas, vocabulary tiers, rhythm targets, type-token targets, personality injection, or repeated passes until markers disappear.

## Route the rewrite

- **Patch:** the main point and order already work; repair local repetition, ambiguity, or indirection.
- **Structural rewrite:** process order, copied facts, paragraph walls, flat lists, or stale headings hide the answer.
- **Stop:** sources conflict, truth is unclear, or a deletion would decide an authorial, research, or acceptance question.

## Classify each source passage

- **Keep:** unique information the reader needs and this document owns.
- **Point:** necessary content already maintained in a linked source.
- **Merge:** passages overlap but contain distinct facts that belong together.
- **Drop:** repetition, outdated state, filler, or implementation detail the reader does not need.
- **Conflict:** incompatible claims or literals requiring evidence or an owner decision.

## Rewrite

1. **Write the answer from kept facts.** State the outcome, decision, or honest current state without strengthening the source.
2. **Arrange dependencies.** Put evidence, caveats, and action beneath the claim they support or limit; preserve causal and temporal order.
3. **Replace copies with pointers.** Keep interpretation here only when this artifact owns it.
4. **Repair the connective tissue.** Add only the transitions and explicit relationships the new order requires.
5. **Delete superseded structure.** Remove stale headings, duplicate summaries, process chronology, and empty sections.

## Verify

- **Invariants:** compare every retained passage against § Freeze invariants.
- **Evidence:** apply the core [support rule](../SKILL.md#keep-only-useful-content).
- **Cold read:** the first layer stands alone and each child has an explicit relationship to its parent.
- **Diff:** every change makes the answer easier to find or the meaning easier to follow; word reduction alone is not a pass.
