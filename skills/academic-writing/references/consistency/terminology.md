# Consistency: Terminology

> Load when Review or Polish mode targets **terminology** — the words used to name concepts, variables, groups, and defined terms. One of eight `consistency/*.md` dimensions. Severity markers: `[BLOCKING]` must fix; `[ADVISORY]` recorded, never blocks.

Source: Chaubey p. 76, p. 157 — consistent key words; no interchangeable terms for one identity.

## Scope

Covers **terminological consistency** — the words a paper uses to name entities. Out of scope: math symbols (`consistency/notation.md`), labels (`consistency/cross-references.md`), claim accuracy (`consistency/argument-logic.md`).

Terminology fails in four patterns:

1. **Same concept, different names.** "Treatment group", "treated firms", "exposed units", "affected sample" for one thing — the reader has to infer they match.
2. **Different concepts, same name.** "Effect" meaning both the estimated coefficient and the underlying causal channel — the reader cannot tell which a sentence means.
3. **Term drift.** Name X in §2, Y in §4, Z in §6 — often a partial revision.
4. **Undefined term.** A technical term used before, or without, a definition the paper's intended readers need.

## How-To

### Build a terminology index

Before terminological edits, index the paper's key terms:

- **First use / definition.** Section and page.
- **Role.** Variable name, concept, group name, defined term of art.
- **Synonyms spotted.** Every other phrase the paper uses for the same thing.

Twenty to thirty terms is usually enough — focus on the ones carrying the argument.

### Check for the four patterns

**Same concept, different names.** `grep` each key entity's variant names. Report every alternate naming alongside the canonical one, and recommend a single canonical form; do not silently rewrite unless the request authorizes it (`SKILL.md §Preserve substance, polish prose`).

**Different concepts, same name.** Flag words doing double duty ("effect" = coefficient *and* causal mechanism; "model" = econometric specification *and* theoretical framework) and recommend a disambiguated pair ("estimate" vs "effect", "specification" vs "model").

**Term drift.** Compare term usage across sections — common after section-by-section revision. Flag every mid-paper rename.

**Undefined term.** At each technical term's first use, is there a definition? Specialist readers tolerate field terms of art undefined; broader readers need them. Escalate on doubt.

### Variable-name drift

Variable names in text match those in tables and code. `Y`, `y`, `Y_i`, `Y_{it}`, `y_{i,t}` used interchangeably for one variable is a common drift source. Per variable:

- Canonical form fixed once.
- Subscript conventions stable (first subscript = unit, second = time, etc.).
- Bold / italic conventions stable (typographic side in `consistency/notation.md`).

### Treatment-group / treatment-sample style mismatches

Recurring ambiguity around "treatment" in empirical economics papers:

- "Treatment" (the policy / exposure) vs "treated" (the units who received it).
- "Treatment group" vs "treated sample".
- "Control group" vs "comparison units" vs "unexposed sample".

Pick one set, use it consistently, flag mixed use.

### Glossary audit (if a glossary exists)

Every glossary term is (a) used in the paper, (b) used with the glossary definition. Flag orphan entries and unglossed-but-critical terms.

### Definition-clarity audit

Each key term's definition is **explicit** (stated, not left to the reader), **precise** (not circular — "the effect is the effect of treatment"), and **consistent with field norms** (a term used against the field's standing meaning needs an explicit override). Flag terms defined in math but not prose, or in prose but misaligned with the formal object they name.

## Gated Checklist

- `[BLOCKING]` **Same concept, different names flagged.** Every identified alias for a key entity is reported with source locations even if not fixed.
- `[BLOCKING]` **Different concepts, same name flagged.** Any word doing double duty on a key argument is reported with both usages cited.
- `[BLOCKING]` **Term drift across sections flagged.** Any mid-paper rename of a key concept is reported with earlier and later locations.
- `[BLOCKING]` **No silent cross-scope rewrites.** For consistency-*check* tasks, mismatches are reported, not rewritten beyond scope (`SKILL.md §Preserve substance, polish prose`).
- `[BLOCKING]` **Variable-name drift across text and tables flagged.** Every variable used inconsistently between prose and tables is reported.
- `[ADVISORY]` **Terminology index recorded** — key terms, canonical forms, observed variants.
- `[ADVISORY]` **Glossary audit** performed if a glossary exists — orphan and unglossed-but-critical terms reported.
- `[ADVISORY]` **Undefined technical terms flagged** when the audience is broader than pure specialists.

## Output format

```
[SEVERITY] Terminology: <one-line title>
Term(s): "<observed variant 1>" / "<observed variant 2>"
Locations:
  - [file.tex:42](file.tex#L42): "<quoted phrase>"
  - [file.tex:87](file.tex#L87): "<quoted phrase>"
Issue: <what's inconsistent>
Recommendation: <canonical form to use, or "escalate — researcher call">
Fix: mechanical | conventional | authorial   # see review.md §Fix tiers
```
