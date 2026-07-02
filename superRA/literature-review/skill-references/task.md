---
title: "Skill References — Discipline, Econ Corpus, Grounding, Synthesis"
status: not-started
depends_on: [skill-core]
---

## Objective

Author the stage/domain references under `skills/literature-review/references/`, each with a clear load condition from `SKILL.md`, each teaching the **principle + a line-by-line identification protocol** (not just a checklist), each standalone-usable:

1. **Search & screening + convergence.** Wohlin backward + forward snowballing to saturation; the two-phase method (backward citation BFS from seeds + forward multi-lens web sweep, each lens blind); screen-first (metadata/abstract/intro, no OCR); the dedup cascade; the stopping/convergence judgment and how to record deliberate non-expansions.
2. **Econ/finance corpus discipline.** Working-paper-first coverage (SSRN / NBER / RePEc); published-version-of-record metadata with the WP-divergence flag; JEL codes as a scope/audit facet; weighting by outlet tier (Top-5 econ / Top-3 finance) + identification strategy (RCT/DiD/IV/RD/structural), not crawlability or raw citation count.
3. **Anti-hallucination grounding + extraction.** Resolve every DOI before trusting a cite; one-question-per-column **concept matrix**, every cell quote-grounded, honest null vs "not reported"; extract-then-verify.
4. **Synthesis & classification.** Concept-centric not author-centric; thematic / methodological / chronological organization; **matrix-sparsity gap detection** (empty cells = the gap); and the optional classification-axis pass (like the model-structure classification in the manual run).

### Validation criteria
- Every reference has a stated load condition from `SKILL.md` and works when read directly by a researcher.
- Each teaches principle + identification protocol.
- Shipped prose is self-contained — no citations to repo-internal contributor docs (`CLAUDE.md`/`AGENTS.md`), no AI-flavored prose, no cross-skill pattern citations.

## Planner Guidance

Keep references one level deep. Prefer positive instructions ("ground every cell in a quote" over "don't leave cells ungrounded"). Load `skill-creator` and `writing`. The four references map to the four analytic stages; do not merge them into one wall — each is loaded at a different point in the workflow.
