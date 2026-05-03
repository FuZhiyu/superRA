# Consistency: Terminology

> Load when Review or Polish mode targets **terminology** — the words used to name concepts, variables, groups, and defined terms. One of eight `consistency/*.md` dimensions; multi-dimensional sweeps dispatch one reviewer per file in parallel. Severity markers shape reviewer output: `[BLOCKING]` items must be reported; `[ADVISORY]` items are flaggable as MINOR.

Source dimensions harvested from `draft-reviewer:writing-clarity-reviewer` (terminology index) and Chaubey p. 76, p. 157 (consistent key words; don't use interchangeable terms for the same identity).

## Scope

This file covers **terminological consistency** — the words a paper uses to name entities — and only those. Out of scope here: math symbols (`consistency/notation.md`), labels (`consistency/cross-references.md`), claim accuracy (`consistency/argument-logic.md`).

Terminology fails in four patterns:

1. **Same concept, different names.** A paper calls the same thing "treatment group", "treated firms", "exposed units", and "affected sample" — reader has to infer these are the same.
2. **Different concepts, same name.** A paper uses "effect" to mean both the estimated coefficient and the underlying causal channel — reader cannot tell which is meant in a given sentence.
3. **Term drift.** A concept is introduced with name X in §2, renamed Y in §4, and referred to as Z in §6 — often a consequence of partial revision.
4. **Undefined term.** A technical term is used before (or without) a definition the paper's intended readers would need.

## How-To

### Build a terminology index

Before making terminological edits, build a short index of the paper's key terms. For each term:

- **First use / definition.** Section and page.
- **Role.** Variable name, concept, group name, defined term of art.
- **Synonyms spotted.** Every other phrase the paper uses for the same thing.

Twenty to thirty terms is usually enough for a paper — focus on the ones that carry the argument.

### Check for the four patterns

**Same concept, different names.** For each key entity, `grep` for the variant names. Report every alternate naming alongside the canonical one. Recommend a single canonical form per entity; do not silently rewrite unless the request authorizes it (`SKILL.md §Preserve substance, polish prose`).

**Different concepts, same name.** When one word is doing double duty ("effect" = coefficient *and* causal mechanism; "model" = econometric specification *and* theoretical framework), flag it. Recommend a disambiguated pair of terms (e.g., "estimate" vs "effect", "specification" vs "model").

**Term drift.** Compare term usage across sections. Drift is common when a paper has been revised section-by-section; flag every mid-paper rename.

**Undefined term.** First-use check: the first time a technical term appears, is there a definition? If the intended reader is a specialist, field terms-of-art may be acceptable without definition; if the intended reader is broader, they need it. Escalate to the researcher on doubt.

### Variable-name drift

Variable names in text should match variable names in tables and in code. `Y`, `y`, `Y_i`, `Y_{it}`, `y_{i,t}` used interchangeably for the same variable is a common drift source. For each variable:

- Canonical form fixed once.
- Subscript conventions stable (first subscript = unit, second = time, etc.).
- Bold / italic conventions stable (treated in `consistency/notation.md` for the typographic side).

### Treatment-group / treatment-sample style mismatches

Empirical economics papers have recurring ambiguity around "treatment":

- "Treatment" (the policy / exposure) vs "treated" (the units who received it).
- "Treatment group" vs "treated sample".
- "Control group" vs "comparison units" vs "unexposed sample".

Pick one set and use it consistently. Flag mixed use.

### Glossary audit (if a glossary exists)

If the paper has a glossary, every glossary term should be: (a) used in the paper, (b) used with the glossary definition. Orphan glossary entries and unglossed-but-critical terms both worth flagging.

### Definition-clarity audit

For each key term, the definition should be **explicit** (stated, not assumed the reader supplies it), **precise** (not circular — "X is defined as X-related" or "the effect is the effect of treatment"), and **consistent with field norms** (a term used against the field's standing meaning needs an explicit override). When a term is defined in math but not in prose, or in prose but not aligned with the formal object it names, flag the mismatch. The reviewer flags drift; the canonical form is the author's call.

## Gated Checklist

- `[BLOCKING]` **Same concept, different names flagged.** Every identified alias for a key entity is reported (file + line locations) even if not fixed.
- `[BLOCKING]` **Different concepts, same name flagged.** Any word doing double duty on a key argument is reported with both usages cited.
- `[BLOCKING]` **Term drift across sections flagged.** Any mid-paper rename of a key concept is reported with earlier and later locations.
- `[BLOCKING]` **No silent cross-scope rewrites.** For consistency-*check* tasks, mismatches are reported, not rewritten beyond scope (`SKILL.md §Preserve substance, polish prose`).
- `[BLOCKING]` **Variable-name drift across text and tables flagged.** Every variable used inconsistently between prose and tables is reported.
- `[ADVISORY]` **Terminology index attached to handoff.** Even a short one (key terms + canonical forms + observed variants) makes follow-up review faster.
- `[ADVISORY]` **Glossary audit** performed if a glossary exists — orphan and unglossed-but-critical terms reported.
- `[ADVISORY]` **Undefined technical terms flagged** when the audience is broader than pure specialists.

## Output format

For each finding, report:

```
[SEVERITY] Terminology: <one-line title>
Term(s): "<observed variant 1>" / "<observed variant 2>"
Locations:
  - file.tex:<line>: "<quoted phrase>"
  - file.tex:<line>: "<quoted phrase>"
Issue: <what's inconsistent>
Recommendation: <canonical form to use, or "escalate — researcher call">
Auto-fixable: Yes / No
```
