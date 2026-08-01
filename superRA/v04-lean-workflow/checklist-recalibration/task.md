---
title: "Domain Checklist Recalibration"
status: not-started
depends_on: [review-calibration]
---

## Objective

Recalibrate the domain and utility skill checklists to the two-severity model and frontier-model defaults.

- Align every gated checklist with the blocking/advisory verdict semantics from `review-calibration`: econ-data-analysis, theory-modeling, refactor-and-integrate, result-protection, semantic-merge, slide-design, writing consistency lanes. (`planning-review.md` is aligned by `review-calibration` itself; the final-diff-self-check trail item in refactor-and-integrate is owned by `writing-contract` — leave both alone here.)
- Delete verification-scaffolding instructions frontier models perform unprompted (re-check/double-check/verify-before-returning lines, verify-subagent instructions) — audit each skill body against the Opus 5 guidance.
- Prune checklist items failing the `CLAUDE.md` DRY/Necessity tests; keep domain-substantive gates (merge validation, look-ahead bias, proof verification) intact — the target is redundant process items, not domain discipline.
- Researcher decision: do not add "what not to flag" exclusion lists.
- Validation: one severity vocabulary repo-wide; no checklist instructs re-verification of work the model already verifies; domain hard gates survive.

## Planner Guidance

- Checklist inventory with per-file `[BLOCKING]` counts and load conditions: [review-architecture map](../attachments/map-review-architecture.md) §3c. Largest surfaces: econ-data-analysis (66 items), theory-modeling (45).
- The Opus 5 doc's over-verification findings and wording implications: [review-prompting research](../attachments/research-review-prompting.md) §D.
- The three competing severity vocabularies to unify are enumerated at the end of the map's §3c.

## Results
