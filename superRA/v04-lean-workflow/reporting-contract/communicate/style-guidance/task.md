---
title: "Make Communicate Easy to Read"
status: approved
depends_on:
  - skill-and-references
---

## Objective

Make `superRA:communicate` easy to understand and give sentence-level style guidance an explicit home.

- Rewrite the core in plain language and a visible nested pyramid. It must model the form it teaches and preserve the user's instruction to spend meaningful effort planning human-facing communication.
- Replace undefined abstractions with observable tests. In particular, replace “low-value units” with a rule based on whether a sentence or bullet adds a claim, evidence, caveat, decision, or action.
- Add `references/style.md` for sentence-level choices. Keep `structures.md` authoritative for arrangement, `rewrite.md` for transforming existing material, and `friction-audit.md` for review diagnostics; remove or point across overlaps rather than restating them.
- Teach direct wording, concrete actors and actions, short complete sentences, stable terminology, visible relationships, and voice preservation without banned-word lists, punctuation rules, or word quotas.
- Update routing and affected documentation, then validate with cold-reader and rewrite cases that expose vague labels, flat structure, paragraph walls, and harmless voice markers.

## Details

- The user identified “low-value units” and the first reader/action rule as opaque. Treat those comments as failures of the instruction surface, not requests for more terminology.
- The current dirty `skills/communicate/SKILL.md` contains user edits: a thinking-budget principle, an inline critique comment, and a shortened unresolved-work rule. Preserve their intent while producing clean final skill text.
- Keep the core short enough to remain always loaded. One concrete inclusion test and a small nested example are more useful than another taxonomy.

## Results

[`superRA:communicate`](../../../../../skills/communicate/SKILL.md) states its core rules in plain language and models the nested pyramid it teaches. "Low-value units" is replaced by one observable test: keep a sentence or bullet only when it adds a claim, evidence, caveat, decision, or action. Sentence-level guidance moved into the skill body alongside the structure rules, so the surviving references cover rewriting, Markdown mechanics, and standalone IO only.

**Two read-only probes passed.** A cold reader found no remaining ambiguous or duplicated rule after one correction round. A rewrite probe removed empty framing, preserved literals and claim strength, and attached a caveat directly to the claim it limits.

Skill validation, Markdown checks, task-tree checks, and diff checks pass.
