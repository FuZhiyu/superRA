# Style — Sentence + Paragraph Rules

> Load when Polish or Draft mode applies sentence-level rules (polish, proofread, tighten, sentence-level clarity pass; draft self-check).

Sources: Little Red Schoolhouse (UChicago ENGL 13000/33000) — actions/nominalization (LRS 1-1a), information flow (LRS 3-4). Chaubey, *The Little Book on Research Writing* (2018) — reader-model, paragraph construction, key-idea-first.

The rules below are **heuristics the writer applies in service of the reader**, not mechanical must-rewrite mandates. Every rule has cases where it should NOT fire — those are called out explicitly. Apply rules only inside the scope of the request and only where they fix a real readability problem (substance and intent are sovereign per `SKILL.md §Preserve substance, polish prose`).

## How-To

### Actions in verbs (LRS 1-1a)

**Principle.** Express your most crucial actions as verbs, not as nominalized nouns. Sentences whose main actions live in nominalizations (`evaluation`, `development`, `understanding`, `measurement`) feel abstract, bureaucratic, and passive-ish even when grammatically active. Moving the action to a verb makes the sentence direct.

**Detection trick.** If you can add `-ing` to a word and it still describes the action, it is a candidate nominalization. Count how many of the sentence's verbs are carrying real work (`is`, `was`, `has`, `found`, `made` do not). If most of the action sits in nouns, denominalize the crucial ones.

**Before / after:**

- Before: *Our firm's development and standardization of an index for the measurement of option risk premiums has made quantification of investor response as a function of currency fluctuation possible.*
- After: *Now that our firm has developed and standardized an index to measure the risk premiums of options, we can quantify how investors respond to currency fluctuations.*

**Do NOT denominalize when:**

- **Daisy chain.** A nominalization picks up a previous verb: *The Board froze hiring. After the freeze, the Special Projects staff lost two members who retired. The Board decided that such retirements…* — `freeze` and `retirements` are both carrying the argument forward. Denominalizing would break the cohesion chain.
- **After a strong verb.** `I do not understand her intentions` is as clear as `I do not understand what she intends` — sometimes clearer because the active verb (`understand`) takes the nominalization (`intentions`) as its direct object. Judgment call.
- **Term of art for the audience.** For expert readers, `repurchase agreements`, `disintermediation`, `heteroskedasticity-robust standard errors` are faster than their denominalized forms. Do not denominalize field vocabulary.
- **Adjective nominalizations.** `precision → precise` is a different pattern; the rule targets *verb* nominalizations specifically (`evaluate → evaluation`).

### Old → new information flow (LRS 3-4)

**Principle.** Readers learn best when each sentence starts with information they already have (old) and ends with information that is new to them. A paragraph whose sentences start with new terms and end with known terms reads as confusing even when every sentence is grammatical. This is why the "first sentence of each paragraph carrying forward a phrase from the previous first sentence" heuristic (Chaubey p. 129) works: the linguistic link signals the logical link.

**Detection trick.** Underline the subjects of three consecutive sentences. If the subjects form a chain (each is either a repetition or a logical successor of the previous sentence's topic or object), old→new flow is intact. If each sentence's subject introduces a fresh term the paragraph has not yet earned, flow is broken.

**Before / after:**

- Before: *Information flow is essential for clear writing. Readers expect old information first. Cognitive load studies confirm this. Paragraph transitions rely on it.*
- After: *Clear writing relies on managing information flow. Information flow works when each sentence starts with old information — material the reader already has — and ends with new information. Old-to-new ordering lowers cognitive load, which in turn supports paragraph-level transitions.*

**Do NOT enforce mechanically when:**

- **The paragraph is introducing a topic.** The first sentence of a paragraph often has to introduce a term the paragraph has not earned — that is its job.
- **Parallel structure is active.** A parallel list of items with fresh subjects in each is not broken flow; it is deliberate parallelism.

### Single-hedge-per-claim

**Principle.** Hedging ("may", "might", "possibly", "suggests", "appears to", "could", "in some cases") calibrates claims to evidence strength. One hedge per claim is calibration; two or more is **epistemic cowardice** — the claim is either in the evidence or it is not. Stacked hedges also signal that the author is hiding behind uncertainty rather than stating a position.

**Detection trick.** Count hedging words in each claim-bearing sentence. More than one is usually one too many.

**Before / after:**

- Before: *The results may possibly suggest that returns could tentatively be somewhat higher for treated firms.*
- After: *The results suggest that returns are higher for treated firms.*  — if the evidence is weak, choose *one* hedge (`suggest`). If the evidence is strong, drop the hedge entirely.

**Do NOT de-hedge when:**

- **The claim is genuinely conditional.** *The effect may attenuate for firms with lower leverage* is one hedge, appropriately placed.
- **The author is stating a research-community-internal dispute.** *Some authors argue that X; others claim Y* is not hedged; it is reporting.

### Active voice with clear agency

**Principle.** Prefer active voice when the agent (who did the action) matters. Passive voice is legitimate when (a) the agent is unknown, (b) the agent is contextually obvious, or (c) the passage needs the object to occupy the grammatical subject slot for flow reasons. The rule is not "avoid passive" — it is "agent visible when agent matters".

**Before / after:**

- Before: *The sample was constructed.* (By whom? When?)
- After: *We constructed the sample by matching firms on industry and size.*
- Passive OK: *The paper was rejected.* (Agent obvious from context — the journal.)

### Parallel structure

**Principle.** When a sentence lists two or more items in grammatical equality, the items must share grammatical form (all noun phrases, or all infinitive clauses, or all gerunds). Broken parallelism is one of the most frequent ESL and draft-speed errors and reads as sloppiness.

**Before / after:**

- Before: *The paper describes the data, estimating the model, and results.* — three grammatically different forms.
- After: *The paper describes the data, estimates the model, and reports the results.* — three finite verbs.

**Applies equally to:**

- Bulleted lists (every bullet starts with the same grammatical form).
- Comparative sentences (`X is faster than running Y` → `X is faster than Y`).
- Section headings within a chapter (all noun phrases, or all imperatives).

### Noun-cluster avoidance

**Principle.** Three or more modifying nouns chained in a row ("customer satisfaction improvement strategy", "firm-year panel data regression specification") read as jargon-heavy and ambiguous. Break the cluster with `of`, a relative clause, or a verb.

**Before / after:**

- Before: *Firm-year panel data regression specification issues.*
- After: *Specification issues in the firm-year panel regression.*

**Do NOT split when** the cluster is a recognized term of art for the audience (e.g., `mutual fund holdings data`, `heteroskedasticity-robust standard errors`). Field vocabulary is faster than its denominalized form.

### Sentence-length guidance

**Principle.** Aim for ~20–25 words as a default; vary deliberately. Sentences above ~40 words almost always benefit from splitting — nested clauses and multiple subjects lose the reader. Very short sentences (<8 words) provide rhythm and emphasis when used sparingly.

**Do NOT split when** the length is deliberately carrying a cumulative argument or a long parallel list — splitting would break the parallelism or bury the argument's shape.

### Dangling modifier check

**Principle.** An introductory modifying phrase modifies the grammatical subject of the main clause. If the subject is not the thing being modified, the modifier dangles.

**Before / after:**

- Before: *Using panel data, the coefficient is negative.* — the coefficient is not using panel data.
- After: *Using panel data, we estimate a negative coefficient.*

**Do NOT rewrite when** the antecedent is unambiguous from the preceding clause and a fluent reader will not misparse — idiomatic scientific prose tolerates some modifier looseness.

### Paragraph-level rules

**Topic sentence first.** Every paragraph carries its main message in its first sentence. The first sentence should (1) include the paragraph's main message, (2) be recognizable as linked to the overall story, (3) provoke follow-up questions the rest of the paragraph answers. (Chaubey p. 137, 141.) *No exceptions — this is a structural norm for academic prose.*

**One idea per paragraph.** Chaubey (p. 158): RAP paragraphs should have 5–6 sentences. If an idea requires more, it is probably two ideas and the paragraph should split. If an idea is buried at the bottom, the paragraph is probably backward — move the buried idea up. *Do NOT split when the two apparent ideas are a single claim + its immediate qualification, which belong together.*

**Transitions at paragraph start.** Place transition words (`however`, `moreover`, `in contrast`, `consequently`) near the start of the paragraph or the start of the sentence that pivots, not buried mid-sentence. *No exceptions — this is a structural norm.*

**First-sentence link test.** Take the first sentence of every paragraph in a section; put them in a separate document; see if they read as a coherent storyline (Chaubey p. 128). If they do, the section's paragraph structure is sound. If they don't, the paragraph-level argument is broken and no amount of sentence polish will fix it. *Do NOT enforce rigidly when the section is a deliberate list or taxonomy where each paragraph is a peer — parallelism replaces the narrative link.*

### Precision of reference

Ambiguous pronouns — `this`, `it`, `that`, `these`, `those` — without a clear antecedent force the reader to reread. When a pronoun could refer to more than one recent noun, replace it with the noun or add a noun after it (`this effect`, `this result`, `this specification`).

**Do NOT replace `this` with a noun when** the paragraph's focus is the referent just named and the antecedent is singular and immediate — adding a noun clutters the prose.

### Clarity heuristics

**Nested-clause run-ons.** A sentence with 3+ embedded clauses, or one where you have to backtrack to recover the subject the main verb belongs to, is harder than it needs to be — consider splitting at the clause boundary that carries the most logical weight. Complements §Sentence-length guidance: length is the rough cue, lost subject-verb tracking is the precise one.

**Vague quantifiers.** `various`, `some`, `several`, `a number of` almost always read as filler the reader cannot calibrate — consider quantifying (`three`, `roughly half`, `the four cases listed in Table 2`) or naming the set. Skip the rewrite when the vagueness is deliberate (the count genuinely does not matter, or naming would mislead).

## Gated Checklist

Walked top to bottom for every sentence-level edit. The rules are heuristics, not verdict-determining items — apply them where they fix a real problem in the text being edited.

### Sentence-level rules

- Crucial actions carried by verbs (LRS 1-1a). Exceptions acknowledged where daisy-chain / after-strong-verb / term-of-art applies.
- Old → new information flow inside paragraphs (LRS 3-4). First-sentence link test passes for any paragraphs affected.
- Hedging calibrated. No stacked hedges (`may possibly`, `could tentatively`, `somewhat perhaps`).
- Active voice where agent matters; passive voice justified by context when used.
- Parallel structure in lists, comparisons, and headings.
- Noun clusters of 3+ modifying nouns broken up.
- Sentences over ~40 words split unless the length is deliberate.
- No dangling modifiers.
- Ambiguous pronouns (`this`, `it`) given an explicit antecedent noun.

### Paragraph-level rules

- Each paragraph's first sentence carries the main message (Chaubey p. 137).
- One idea per paragraph; paragraphs that bury the idea at the bottom are re-ordered (Chaubey p. 160).
- Transitions placed near paragraph start.
- First-sentence link test: first sentences of consecutive paragraphs form a coherent storyline (Chaubey p. 128).

### Handoff

- `[BLOCKING]` Every applied rule is traceable to a specific problem in the source text (no over-application).
- Edits that touched more than diction (i.e., changed sentence structure) noted in handoff so the author can confirm voice preservation.
