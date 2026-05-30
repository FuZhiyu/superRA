---
title: Contributor Note — State Externalization & Workflow Boundary
status: not-started
created: 2026-05-30
updated: 2026-05-30
depends_on: []
---

# Contributor Note — State Externalization & Workflow Boundary

## Objective

Record the two understanding-only lessons (full statement in the parent task's `## Analysis` §2, §3) that must NOT go into skill bodies — they would fail the Necessity test there (they explain rather than change what an agent does) — but are valuable contributor framing. Add them to the repo-root `CLAUDE.md`, in the §Internal Design Philosophy / §Architectural Patterns area. Keep it to contributor rationale — these are notes for humans and future design work, not agent instructions.

Two notes:
- **Externalize orchestration state; durable for research.** superRA and Claude Code dynamic workflows independently moved orchestration state out of the context window — workflows into ephemeral script variables, superRA into the durable `.plan/` tree. The durable choice is deliberate: research spans sessions and must be provenance-auditable. The Frontier Resolver (superRA's mechanism for computing the next action from the durable task tree rather than turn-by-turn) is the determinism mechanism. State this as the shared principle; do not turn it into a skill instruction.
- **Workflow-eligible-segment boundary (future Claude-adapter option).** A segment of a superRA stage may be delegated to a dynamic workflow as an execution engine *only if it is fan-out-heavy and contains no decision from the three pause classes* — the decision types that must stop for the human, which the runtime forbids mid-run. Record this as a documented future option behind the Claude adapter — keeping the Claude-only runtime dependency out of core skills while preserving the design decision. Cross-reference the wide-fan-out tier added in `01-review-and-tier-patterns`.

Do not duplicate the analysis — `CLAUDE.md` carries the principle in contributor-doc form; the parent task's `## Analysis` carries the full reasoning. Per CLAUDE.md's own rules, no cross-skill pattern citations in skill bodies; `CLAUDE.md` is the correct home for the rationale.

## Validation

- Both notes land in `CLAUDE.md` contributor sections, not in any `skills/*` body.
- Each note states the principle/boundary and points to the memo rather than reproducing it.
- The workflow-eligible boundary explicitly names the no-pause-class condition and the constraint that the core skills stay harness-agnostic (the Claude-only runtime dependency stays behind the adapter).
