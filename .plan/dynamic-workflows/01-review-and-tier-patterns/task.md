---
title: Review & Tier Patterns in agent-orchestration
status: not-started
created: 2026-05-30
updated: 2026-05-30
depends_on: []
---

# Review & Tier Patterns in agent-orchestration

## Objective

Add three behavior-changing patterns to `skills/agent-orchestration/SKILL.md`. All three are harness-agnostic — they work on any agent harness, being just parallel `Agent` dispatch plus prose discipline. Load `skill-creator` and re-read `CLAUDE.md §"Teach the Protocol"` first; every added line must pass DRY + Necessity (the repo's rule that a line stays only if no other file already carries it and removing it would change what an agent does). Do not restate rationale in the skill body — the why for these three is below; broader context is in the parent task's `## Analysis` (§4, §5) if needed.

Why these three (the lesson, distilled): Claude Code dynamic workflows show that orchestration *quality* comes from repeatable verification structure, not agent count. superRA currently runs a single implementer→reviewer pass. The repo's own `.claude/workflows/verify-workflow-skill-rename.js` already embodies the target shape — N parallel reviewers each on a distinct lens, a per-finding verify step that opens the cited file, and an explicit up-front scope statement — so these patterns are validated, not speculative.

**1. Perspective-diverse review shape (optional).** In the review-orchestration area (near §Handling Reviewer Feedback), add a short optional shape: for a high-stakes task, instead of one reviewer the orchestrator may dispatch N reviewers in parallel, each scoped to a *distinct lens*, then adjudicate the union of findings under the existing verdict protocol. State the gate: use it only when the failure mode is *not noticing* and lenses are genuinely disjoint; otherwise one reviewer is the default. Name where lenses come from — the active domain skill's gates (task `02-domain-lenses` exposes them) — by pointer, not by copying any lens list here. Do not duplicate the single-reviewer adjudication mechanics; this shape reuses them.

**2. No-silent-caps line.** Add one line to the orchestrator discipline: when a dispatch bounds coverage (top-N, sampling, no-retry, a frontier subset), the orchestrator must `log`/state what was excluded. Silent truncation reads as full coverage. Keep to one sentence — it shapes behavior the agent would not otherwise produce.

**3. Wide-fan-out tier.** In §Workload Balancing, add a tier above "Tier 3 — dedicated agent": a wide pause-free fan-out (many independent agents covering a sweep or many disjoint reviews in one stage). Gate it explicitly: eligible only when the segment contains **no decision from the three pause classes** (the decision types that must stop for the human) — any such decision keeps the work in the LLM-orchestrated loop. Note that on Claude Code this tier is the natural home for delegating to a dynamic workflow, but the tier itself is harness-agnostic (it is just many parallel dispatches); the runtime-delegation option is documented in task `04-contributor-note`, not here.

## Validation

- Re-read the diff line by line against the DRY + Necessity test; each new line either restates nothing already owned elsewhere and changes behavior, or is removed.
- Confirm no duplication of single-reviewer adjudication mechanics (DRY vs §Handling Reviewer Feedback).
- Confirm the wide-fan-out tier's no-pause-class gate is stated, not implied.
- One realistic check: re-read §Workload Balancing top-to-bottom and confirm the four tiers form a clean escalation with non-overlapping triggers.
