# Audience Awareness — superRA:writing Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-05-11 (planning)
**Status:** In Progress

---

## Task 1: Edit SKILL.md, style.md, and writing/CLAUDE.md for audience-awareness rule

**Status:** IMPLEMENTED

Three files edited, one atomic commit. The conversation/document boundary discipline now reads as: SKILL.md teaches the principle and the upstream audience-model protocol (always loaded, every Review / Polish / Draft); style.md teaches the four line-level marker families and replacement patterns (loaded when Polish / Draft / style-scoped Review runs); CLAUDE.md records why the rule is split across the two files.

- `skills/writing/SKILL.md` — added top-level section `## Write to the reader, not the conversation` between `## Preserve substance, polish prose` and `## Before you start`. Three paragraphs (audience distinct from conversation; two-question audience model; write/edit against the set) plus a pointer to `references/style.md §Audience` for the line-level safety net.
- `skills/writing/references/style.md` — inserted new heuristic `### Audience: write to the reader, not the conversation` as the first §How-To entry (before `### Actions in verbs`). Carries the four marker families (editing-history temporal, audience self-reference, process-internal artifact, conversation jargon), four replacement patterns (one per family), and three §Do NOT exceptions (conventional discourse transitions, public citable resources, genuine field terms of art). Appended one bullet to §Gated Checklist Sentence-level rules so the gated walk picks up the new rule.
- `skills/writing/CLAUDE.md` — appended new section `## Audience awareness as an upstream audience-model discipline` after §Sources. Records the SKILL.md / style.md split rationale (Review scope coverage without style.md; avoid forcing every Review to load marker families), the deliberate generalization beyond academic papers (slide decks, working-paper notes, replication READMEs, referee responses), and the do-not-collapse / do-not-re-narrow guidance for future contributors.

Verification of behavior change is deferred to Task 2 (constructed-fragment dispatch).

## Task 2: Verify the rule on constructed examples

**Status:** Not started
