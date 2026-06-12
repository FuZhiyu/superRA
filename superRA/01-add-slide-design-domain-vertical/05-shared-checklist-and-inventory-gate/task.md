---
title: "Operationalize the Quick Checklist: Shared Walk and Inventory-Backed Context Gate"
status: approved
depends_on:  []
tags: []
output:
  - skills/slide-design/SKILL.md
created: 2026-06-12
---

## Objective

Make the slide-design Quick Checklist match the repo's shared-gated-checklist pattern and give its headline audience-context gate a verifiable standard of evidence.

- The checklist preamble states that the implementer walks the checklist as a self-check before returning DONE and the reviewer walks it as verification — the shared-walk pattern stated in `CLAUDE.md §Architectural Patterns` and phrased in `econ-data-analysis/SKILL.md §Three Concurrent Disciplines` ("walked by implementer (before DONE) and reviewer (as verification)"). The current "Reviewers walk this checklist for slide-design tasks" drops the implementer half.
- The `[BLOCKING]` audience-context item names its standard of evidence: when the work runs inside a superRA task tree, claims about established context are verified against the audience-context inventory recorded at planning time (`references/planning.md §Audience-Context Inventory`); when no inventory exists (standalone invocation), the reviewer states the assumed representative audience member in the review notes and judges against that. Today the gate floats on reviewer intuition while `references/integration.md` already checks the deck route against the inventory — the implement-stage checklist needs the same anchor.

Validation: each changed line passes the `CLAUDE.md §Teach the Protocol` DRY and Necessity tests; the inventory is referenced by pointer, not paraphrased.

## Planner Guidance

Tasks 06 and 07 also edit `skills/slide-design/SKILL.md`. Dispatch 05–07 as one bundle or serialize them to avoid edit conflicts; there is no logical dependency among them.

## Results

Two edits to [skills/slide-design/SKILL.md](../../../skills/slide-design/SKILL.md):

1. Checklist preamble changed from "Reviewers walk this checklist for slide-design tasks" to "Shared checklist walked by the implementer (before DONE) and by the reviewer (as verification)." This matches the pattern in `econ-data-analysis/SKILL.md §Three Concurrent Disciplines` and CLAUDE.md §Architectural Patterns.

2. The `[BLOCKING]` audience-context item extended with the inventory anchor: when inside a superRA task tree, verify against the audience-context inventory at `references/planning.md §Audience-Context Inventory`; when standalone, reviewer states the assumed representative audience member and judges against that. The inventory is referenced by pointer only — not paraphrased.

DRY/Necessity check: both lines are behavior-shaping (the implementer-walk was a missing non-default constraint; the inventory pointer gives the gate a verifiable standard of evidence it did not have before). Neither restates content carried elsewhere.
