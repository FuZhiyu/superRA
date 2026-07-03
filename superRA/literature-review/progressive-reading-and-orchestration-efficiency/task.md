---
title: "Progressive Reading And Orchestration Efficiency"
status: approved
depends_on:
  - client-and-materializer-mechanisms
---

## Objective

Revise the workflow/discovery/screening/extraction references so that (a) a paper's abstract/intro/related-work content is read once and reused across discovery -> screening -> extraction instead of re-opened by each stage, (b) extraction shape is a researcher-elicited hybrid — a small shared comparison matrix plus a free-form grounded narrative, matrix allowed empty — instead of a single mandatory concept-matrix format, and (c) the main-agent dispatch loop states when discovery lenses may run concurrently, when screening should sweep discovery leads, and when the Zotero-library dedup pass fires.

### Required design

**Progressive reading — no stage re-reads what an earlier stage already read and recorded:**

- Add a `## Reading Notes` section to the candidate/paper record template (`SKILL.md` §Candidate And Paper Records): an append-only log, one entry per stage/depth that opened the source, each tagged `[stage, depth, what was read]` and carrying the grounded takeaway (scope fit, sample/period, method/identification hint) — enough for the next stage to decide without reopening the source, not just a one-line relevance tag.
- `discovery.md`: when a discovery agent reads abstract/intro (depth 1) or related-work/citation discussion (depth 2), it appends a Reading Notes entry with the gate-relevant facts it found, not only the "local reason for relevance" it already writes.
- `screening.md`: before opening the abstract/intro itself, screening reads any existing Reading Notes first and decides from them when they answer the inclusion gate; it opens the source only when notes are missing, ambiguous, or don't cover the gate in question, and appends its own entry when it does.
- `grounding-and-extraction.md`: before extracting a schema field that overlaps a fact screening already grounded with a quote (e.g. identification strategy, outlet tier), extraction adopts and re-verifies that quote rather than re-deriving it from the full text.

**Flexible, goal-fit extraction:**

- `workflow.md` Part 1 interactive setup: alongside "Extraction schema," elicit the comparison columns explicitly as "what must be comparable across every included paper" (may be empty) — those become the matrix; everything else in the schema is narrative.
- `grounding-and-extraction.md`: restructure the concept-matrix section into the hybrid — matrix columns for the elicited comparison facts, a free-form grounded narrative note per paper for the rest. Keep the grounding invariants (DOI resolution before trusting a cite, quote-per-claim with location, extract-then-verify, null vs "not reported") mandatory regardless of shape; state that an empty comparison-column set collapses the shape to narrative-only.

**Dispatch-loop efficiency:**

- `workflow.md` Dispatch Loop: state that independent discovery dispatches (different lenses/seeds writing into the same non-git candidate store) may run concurrently via ordinary parallel Agent calls without worktree isolation, because the only shared mutable state is the candidate store and the materializer (from the dependency task) merges it safely — a stated exception to `agent-orchestration`'s default worktree-per-parallel-task rule, with the reason given inline.
- `workflow.md`/`screening.md`: state a cadence for sweeping accumulated `Discovery Leads` (e.g. at each periodic synthesis pass) instead of leaving "does the main agent notice and re-dispatch" unspecified.
- `workflow.md`: state that the Zotero-library dedup pass (routed to `zotero-paper-reader`) fires at promotion time, once per paper being promoted — not per discovery candidate — giving the composed-skill route in `SKILL.md` a concrete trigger point.
- Wire the new `candidate_materializer.py promote` subcommand into `screening.md`'s promotion instructions in place of the hand-rolled copy step.

### Files to update

- `skills/literature-review/SKILL.md` — Reading Notes section in the record schema.
- `skills/literature-review/references/workflow.md` — extraction-shape setup, parallel-dispatch exception, lead-sweep cadence, Zotero-dedup trigger point.
- `skills/literature-review/references/discovery.md` — Reading Notes writes, version-union tool call (replacing manual per-DOI looping), batching guidance for lens dispatches.
- `skills/literature-review/references/screening.md` — Reading Notes read-before-reread, promote-subcommand wiring, lead-sweep cadence.
- `skills/literature-review/references/grounding-and-extraction.md` — hybrid shape, adopt-screening's-grounded-facts.

### Validation criteria

- `rg` over the skill finds no remaining instruction telling screening to read abstract/intro unconditionally regardless of existing Reading Notes.
- `grounding-and-extraction.md` describes the hybrid shape with an empty-matrix (narrative-only) case, and the invariant grounding rules read as mandatory independent of shape.
- `workflow.md` states the parallel-discovery exception, the lead-sweep cadence, and the Zotero-dedup trigger point as explicit, checkable statements, not left implicit.
- `python3 skills/report-in-markdown/scripts/check_markdown.py skills/literature-review/SKILL.md skills/literature-review/references/workflow.md skills/literature-review/references/discovery.md skills/literature-review/references/screening.md skills/literature-review/references/grounding-and-extraction.md` runs clean.

## Planner Guidance

This task assumes the `promote` subcommand and version-DOI union tool call already exist (its dependency) and references them by name. Do not re-litigate the corpus-quality discipline in `econ-corpus.md` — only wire the two facts it already asks for (identification strategy, outlet tier) into the reuse-not-rederive rule for extraction.
