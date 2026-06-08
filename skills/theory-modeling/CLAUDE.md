# theory-modeling — Contributor Notes

> Repo-wide design rules (DRY, Necessity, ownership boundaries, anti-patterns) live in the root `CLAUDE.md`. This file records the design choices specific to the theory-modeling vertical so future contributors do not re-litigate them.

## Why this skill exists

The dominant failure mode of modeling work is **silent algebra under unstated assumptions**: a symbol naming two different objects across a proof, an assumption back-filled after the algebra, a "by symmetry" step that quietly requires a sign restriction. LLMs are especially prone to it because they produce plausible algebra without a stable underlying model. The skill makes that discipline enforceable at every dispatch, not a matter of taste.

## What composes vs. what is new

The vertical is a **domain skill** under the existing PLAN → IMPLEMENT → INTEGRATE workflow — no new stage, workflow skill, or orchestration mechanism, just one added row in the `using-superra` Skill-Load Manifest domain add-on table. If you find yourself adding a workflow stage or workflow-shaped concept here, stop: the concern belongs in a workflow skill or an existing `Stage:` value reused with new references.

## Per-task ledger and user-gated canonical Notation Conventions

Why the root task.md Notation Conventions table is user-gated rather than implementer-editable: notation conventions in a paper are a researcher decision. Letting an implementer edit the canonical table mid-derivation lets locally-convenient names spread silently across the project. The per-task ledger discipline forces every implementer to walk a structured slot set per symbol, which surfaces near-duplicates against canonical names before they propagate. Promotion happens at `superimplement` Step 4 under researcher confirmation.

## Falsification tests

The Substitution and Proof-deletion tests exist because LLMs produce plausible-looking justifications that survive any specific change to the object they claim to justify ("plays a role in the proof of Lemma 3.1" is true of every symbol in the proof). They are reviewer diagnostics run against suspect slots, not gates walked on every entry.

## Correctness floor vs. readability layer

The split between `SKILL.md` (correctness floor) and `references/integration.md` (readability layer) exists because applying the readability layer to first-draft exploratory work bloats the cycle, while applying only the readability layer to final output loses the audit trail. The dividing question for any new check: "would a first-draft proof that fails this still be auditable?" If yes, it is readability (`integration.md`); if no, it is correctness (`SKILL.md`).

## Stage-scoped references

The Stage-Scoped References table in `SKILL.md` is the authoritative load map. Adding a reference requires a row with an explicit load condition; dropping one requires sweeping the routing rows. `objective-first.md` is loaded on demand from inside `integration.md` Section A — too long to live in the always-loaded reference, but pullable when the agent is stuck on the diagnostic move.

## What this skill deliberately does not carry

- **Generic reviewer-protocol mechanics** (verdicts, dependent findings, re-review behavior). These are owned by `agent-orchestration` and the canonical role specs in `agents/`. The Falsification tests in `SKILL.md` are theory-specific; everything else points at the standard protocol.
- **Generic codebase-coherence concerns** (naming consistency, utility reuse, PR-friendly diffs, Project Doc Audit). Owned by `refactor-and-integrate`. `integration.md` Sections A–C are the theory-modeling-specific rewriting layer; Section D guards correctness-discipline artifacts during refactoring; everything else loads `refactor-and-integrate` at `Stage: integration`.
- **Audience-discipline / perspective-collapse essays.** Earlier drafts carried `audience-discipline-modeling.md` and `audience-discipline-writing.md` (~315 lines combined). They were dropped: the operational core (workflow-vocabulary leak detection, three-channel separation) did not pay its keep against the framing-essay overhead, and the worked examples were paper-specific in a way that did not transfer. Concrete prose-to-math precision rules survive in `integration.md` Section B (math-symbol-not-English-description, equation-reference-not-position).
- **Rendering utility.** Owned by `superRA:report-in-markdown`. The skill points at it and otherwise does not invent rendering conventions.

## Extension patterns

**Adding a new check.** Decide whether it is a correctness concern or a readability concern. Correctness → new `[BLOCKING]` or `[ADVISORY]` item under the relevant gate in `SKILL.md`. Readability → new item in `integration.md` Section A/B/C. Walk the DRY/Necessity tests in repo CLAUDE.md before merging — most candidate checks are restatements of an existing gate item.

**Adding a new reference.** Only when the content has a clear load condition that the body of `SKILL.md` or `references/integration.md` cannot itself trigger. Add the row to the Stage-Scoped References table with an explicit load-when. Add a load directive at the call site. References stay one level deep from `SKILL.md`.

**Adding a new domain rationalization.** The Common Rationalizations table in `SKILL.md` is for patterns the gates cannot catch on their own. Do not add rows that restate an existing gate `[BLOCKING]` item; the gate is the authoritative copy.

**Tightening a gate.** First check whether the new restriction is already implied by an existing gate item under the falsification tests. If yes, it is a clarification of the existing item, not a new one. If no, ask whether the restriction is a creation-time correctness floor (gate) or a readability rewrite (integration.md). Most "I want to require X in proofs" turn out to be the latter.

## History

The four-gate architecture, per-task ledger, falsification tests, and correctness/readability split each emerged from concrete review feedback, not a priori design — the earliest versions were a single `Define-Derive-Validate` checklist. The correctness/readability split needed different checklists at different stages but, notably, no new workflow stage. If a future change triggers the "we need a new stage for X" instinct, first check whether `Stage: integration` with new references carries the same weight.
