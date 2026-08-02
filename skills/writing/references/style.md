# Style — Sentence + Paragraph Rules

> Load when Polish or Draft mode applies sentence-level rules (polish, proofread, tighten, sentence-level clarity pass; draft self-check).

Sources: Little Red Schoolhouse (UChicago ENGL 13000/33000) — actions/nominalization (LRS 1-1a), information flow (LRS 3-4). Chaubey, *The Little Book on Research Writing* (2018) — reader-model, paragraph construction, key-idea-first.

The rules below are **heuristics in service of the reader**, not must-rewrite mandates; each carries its own non-firing cases. Apply them only inside the request's scope and only where they fix a real readability problem (substance and intent are sovereign per `SKILL.md §Preserve substance, polish prose`).

## How-To

### Audience: write to the reader, not the conversation

**Principle.** Stated in `SKILL.md §Write to the reader, not the conversation`. Build the audience model and their information set before editing; the markers below are the safety net for leaks that check missed. Examples use academic papers; the marker families read on any audience-bound document.

**Detection trick — four marker families.** Walk the families in order on every line in scope; on a match, classify by family and rewrite per the replacement pattern. The rule is line-level — one marker does not license a paragraph-level rewrite.

1. **Editing-history temporal markers.** `now`, `currently`, `at this point`, `previously`, `the new`, `the updated`, `the revised`, `as discussed`, `as we mentioned`. The audience has no "before". (Exception: section transitions like *we now turn to …* are conventional discourse — see §Do NOT.)
2. **Audience self-references.** `paper-facing`, `internal table`, `for the paper`, `internally`, `behind the scenes`, `the version shown to readers`, `the public version`. Naming an audience implies a second audience — a distinction internal to the editing process.
3. **Process-internal artifacts.** Repo paths (`input/country_information.csv`), input-file column names (`the AE column`), branch names, script names, variable names absent from the document, internal classification labels. The audience has no repo. Published replication packages are referenced in the data/code availability section by public identifier, not inline by file path.
4. **Conversation jargon used as document vocabulary.** Working terms the author and agent use to communicate but the document never defines — project nicknames, draft-stage shorthand, glossary terms living in chat or a working doc rather than the manuscript / deck / README. Test against the audience's info set (`SKILL.md §Write to the reader, not the conversation`): not in the set and not defined at first use → conversation vocabulary.

**Replacement patterns.**

- *Editing-history temporal marker.* Before: *The table now defines coreAE as …* → After: *Table 2 defines coreAE as …*
- *Audience self-reference.* Before: *In the paper-facing table, we define …* → After: *Table 2 defines …*
- *Process-internal artifact.* Before: *Throughout, AE refers to the IMF World Economic Outlook "Advanced Economies" classification, applied via the `AE` column of `input/country_information.csv`.* → After: *Throughout, AE refers to the IMF World Economic Outlook "Advanced Economies" classification.*
- *Conversation jargon.* Define the term once in the document's own voice at first use, or replace with the standard term the audience knows. If neither fits (no document-side equivalent, not worth defining), the surrounding argument needs rewriting, not patching — surface as `authorial` per §Triage.

**Do NOT rewrite when:**

- The temporal cue is internal to the document's own narrative ("we now turn to robustness", "the next subsection extends this") — conventional discourse markers.
- The artifact reference is to a public, citable resource the document's data/code availability section points to. (Even then, the inline reference is the public identifier, not a local repo path.)
- The term is a genuine field term of art the venue's audience knows. Test: would a typical reader / viewer / user at this venue recognize it without the document defining it?

### Actions in verbs (LRS 1-1a)

**Principle.** Express crucial actions as verbs, not nominalized nouns (`evaluation`, `development`, `understanding`, `measurement`). Action buried in nouns reads abstract and bureaucratic even when the sentence is grammatically active.

**Detection trick.** A word that still describes the action with `-ing` added is a candidate nominalization. Count the sentence's verbs carrying real work (`is`, `was`, `has`, `found`, `made` do not). Most of the action sitting in nouns → denominalize the crucial ones.

**Before / after:**

- Before: *Our firm's development and standardization of an index for the measurement of option risk premiums has made quantification of investor response as a function of currency fluctuation possible.*
- After: *Now that our firm has developed and standardized an index to measure the risk premiums of options, we can quantify how investors respond to currency fluctuations.*

**Do NOT denominalize when:**

- **Daisy chain.** A nominalization picks up a previous verb: *The Board froze hiring. After the freeze, the Special Projects staff lost two members who retired. The Board decided that such retirements…* — `freeze` and `retirements` both carry the argument forward; denominalizing breaks the cohesion chain.
- **After a strong verb.** `I do not understand her intentions` is as clear as `I do not understand what she intends` — the active verb takes the nominalization as its direct object. Judgment call.
- **Term of art for the audience.** For expert readers, `repurchase agreements`, `disintermediation`, `heteroskedasticity-robust standard errors` are faster than their denominalized forms.
- **Adjective nominalizations.** `precision → precise` is a different pattern; the rule targets *verb* nominalizations (`evaluate → evaluation`).

### Old → new information flow (LRS 3-4)

**Principle.** Each sentence starts with information the reader already has (old) and ends with information new to them. A paragraph whose sentences start with new terms and end with known ones reads as confusing even when every sentence is grammatical. Same reason the carry-a-phrase-forward-between-first-sentences heuristic works (Chaubey p. 129): the linguistic link signals the logical one.

**Detection trick.** Underline the subjects of three consecutive sentences. Subjects forming a chain (each a repetition or logical successor of the previous topic or object) → flow is intact. Each subject introducing a fresh term the paragraph has not earned → flow is broken.

**Before / after:**

- Before: *Information flow is essential for clear writing. Readers expect old information first. Cognitive load studies confirm this. Paragraph transitions rely on it.*
- After: *Clear writing relies on managing information flow. Information flow works when each sentence starts with old information — material the reader already has — and ends with new information. Old-to-new ordering lowers cognitive load, which in turn supports paragraph-level transitions.*

**Do NOT enforce mechanically when:**

- **The paragraph is introducing a topic.** Its first sentence often has to introduce a term the paragraph has not earned — that is its job.
- **Parallel structure is active.** A parallel list with fresh subjects in each item is deliberate parallelism, not broken flow.

### Single-hedge-per-claim

**Principle.** Hedging ("may", "might", "possibly", "suggests", "appears to", "could", "in some cases") calibrates claims to evidence strength. One hedge per claim is calibration; two or more is **epistemic cowardice** — the claim is either in the evidence or it is not.

**Detection trick.** Count hedging words in each claim-bearing sentence. More than one is usually one too many.

**Before / after:**

- Before: *The results may possibly suggest that returns could tentatively be somewhat higher for treated firms.*
- After: *The results suggest that returns are higher for treated firms.*  — weak evidence: keep *one* hedge (`suggest`). Strong evidence: drop the hedge entirely.

**Do NOT de-hedge when:**

- **The claim is genuinely conditional.** *The effect may attenuate for firms with lower leverage* is one hedge, appropriately placed.
- **The author is reporting a research-community dispute.** *Some authors argue that X; others claim Y* is reporting, not hedging.

### Active voice with clear agency

**Principle.** Prefer active voice when the agent matters. Passive is legitimate when (a) the agent is unknown, (b) the agent is contextually obvious, or (c) flow needs the object in the grammatical subject slot. The rule is "agent visible when agent matters", not "avoid passive".

**Before / after:**

- Before: *The sample was constructed.* (By whom? When?)
- After: *We constructed the sample by matching firms on industry and size.*
- Passive OK: *The paper was rejected.* (Agent obvious from context — the journal.)

### Parallel structure

**Principle.** Items listed in grammatical equality share grammatical form (all noun phrases, or all infinitive clauses, or all gerunds). Broken parallelism reads as sloppiness.

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

**Do NOT split when** the cluster is a recognized term of art for the audience (e.g., `mutual fund holdings data`, `heteroskedasticity-robust standard errors`).

### Sentence-length guidance

**Principle.** ~20–25 words as a default; vary deliberately. Sentences above ~40 words almost always benefit from splitting. Very short sentences (<8 words) provide rhythm and emphasis when used sparingly.

**Do NOT split when** the length deliberately carries a cumulative argument or a long parallel list — splitting breaks the parallelism or buries the argument's shape.

### Dangling modifier check

**Principle.** An introductory modifying phrase modifies the grammatical subject of the main clause. Subject is not the thing being modified → the modifier dangles.

**Before / after:**

- Before: *Using panel data, the coefficient is negative.* — the coefficient is not using panel data.
- After: *Using panel data, we estimate a negative coefficient.*

**Do NOT rewrite when** the antecedent is unambiguous from the preceding clause and a fluent reader will not misparse — idiomatic scientific prose tolerates some modifier looseness.

### Paragraph-level rules

**Topic sentence first.** Every paragraph carries its main message in its first sentence, which should (1) state that message, (2) be recognizably linked to the overall story, (3) provoke follow-up questions the rest of the paragraph answers. (Chaubey p. 137, 141.) *No exceptions — structural norm for academic prose.*

**One idea per paragraph.** RAP paragraphs run 5–6 sentences (Chaubey p. 158). An idea needing more is probably two ideas — split. An idea buried at the bottom means the paragraph is backward — move it up. *Do NOT split a single claim plus its immediate qualification.*

**Transitions at paragraph start.** Place transition words (`however`, `moreover`, `in contrast`, `consequently`) near the start of the paragraph or of the pivoting sentence, not buried mid-sentence. *No exceptions — structural norm.*

**First-sentence link test.** Take the first sentence of every paragraph in a section, read them together, and check they form a coherent storyline (Chaubey p. 128). If they don't, the paragraph-level argument is broken and no sentence polish will fix it. *Do NOT enforce rigidly when the section is a deliberate list or taxonomy of peers — parallelism replaces the narrative link.*

### Precision of reference

Ambiguous pronouns — `this`, `it`, `that`, `these`, `those` — without a clear antecedent force a reread. When a pronoun could refer to more than one recent noun, replace it with the noun or add a noun after it (`this effect`, `this result`, `this specification`).

**Do NOT replace `this` with a noun when** the paragraph's focus is the referent just named and the antecedent is singular and immediate — the added noun clutters.

### Clarity heuristics

**Nested-clause run-ons.** A sentence with 3+ embedded clauses, or one needing a backtrack to recover the main verb's subject, is harder than it needs to be — consider splitting at the clause boundary carrying the most logical weight.

**Vague quantifiers.** `various`, `some`, `several`, `a number of` read as filler the reader cannot calibrate — consider quantifying (`three`, `roughly half`, `the four cases listed in Table 2`) or naming the set. Skip when the vagueness is deliberate (the count genuinely does not matter, or naming would mislead).

## Gated Checklist

Walked top to bottom for every sentence-level edit. Heuristics, not verdict-determining items — apply where they fix a real problem in the text being edited.

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
- Audience awareness: line scanned against the four marker families (editing-history temporal, audience self-reference, process-internal artifact, conversation jargon) per §Audience. Term-level check references the audience's information set per `SKILL.md §Write to the reader, not the conversation`.

### Paragraph-level rules

- Each paragraph's first sentence carries the main message (Chaubey p. 137).
- One idea per paragraph; paragraphs that bury the idea at the bottom are re-ordered (Chaubey p. 160).
- Transitions placed near paragraph start.
- First-sentence link test: first sentences of consecutive paragraphs form a coherent storyline (Chaubey p. 128).

### Status Return

- `[BLOCKING]` Every applied rule is traceable to a specific problem in the source text (no over-application).
- Edits that touched more than diction (i.e., changed sentence structure) noted in the status return or task body so the author can confirm voice preservation.
