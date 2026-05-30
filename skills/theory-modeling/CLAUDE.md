# theory-modeling — Contributor Notes

> Read `superRA-dev/CLAUDE.md` for the repo-wide design rules (DRY, Necessity, ownership boundaries, anti-patterns). Apply them line by line when editing anything in this directory. This file records the high-level design choices specific to the theory-modeling vertical so future contributors do not re-litigate them.

## Why this skill exists

Theory and modeling work — derivations, equilibria, proofs, comparative statics, simple numerical verification — has a different failure profile than data analysis. The dominant failure mode is **silent algebra under unstated assumptions**: a symbol that names two different objects across a proof, an assumption back-filled after the algebra, a "by symmetry" step that quietly requires a sign restriction. LLMs are especially prone to it because they will produce plausible algebra without a stable underlying model. The skill exists to make that discipline enforceable at every dispatch, not as taste.

## What composes vs. what is new

The vertical was added as a **domain skill** under the existing PLAN → IMPLEMENT → INTEGRATE workflow. No new workflow stage, no new workflow skill, no new orchestration mechanism. The Skill-Load Manifest in `using-superra` was extended by one row in the domain add-on table; everything else — `superplan`, `superimplement`, `superintegrate`, `agent-orchestration`, `result-protection`, `refactor-and-integrate`, `semantic-merge` — works unchanged. **If you find yourself adding a workflow stage or a workflow-shaped concept here, stop**: the concern probably belongs in a workflow skill or in an existing `Stage:` value reused with new references.

## The Iron Law and the four gates

The Iron Law is the through-line: every symbol has a meaning, every assumption has a plain-language interpretation a researcher can defend, every non-trivial derivation move has a one-sentence reason. The four gates — **Objects & Notation / Assumptions / Derivations / Verification & Rendering** — are organized around the reader's trust chain in that order. Each gate has an **artifact** the implementer produces (per-symbol ledger entry, per-assumption ledger entry, the derivation body, the verification record) and a **checklist** walked while producing the artifact. Documentation is built into the artifact definitions, not a separate phase.

The four-gate ordering encodes the trust-chain dependency: a reader cannot evaluate an assumption that uses an undefined symbol; cannot evaluate a derivation step without knowing the active assumption set; cannot accept a verification claim without an auditable derivation. Gates are concurrent, not sequential — every modeling step exercises all four at once.

## Per-task ledger and user-gated canonical Notation Conventions

A subtle but load-bearing choice: `PLAN.md`'s **Notation Conventions** table is canonical and **user-gated**. Implementers do NOT inline-edit it during implementation. Symbols introduced during implementation are logged to a per-task **Notation & Assumptions Ledger** in `RESULTS.md`, with the structured slot template in Gate 1 / Gate 2. Promotion from per-task ledger to canonical table happens at `superimplement` Step 4, where the orchestrator surfaces ledger candidates for the researcher's explicit confirmation.

Why: notation conventions in a paper are a researcher decision, not a per-task implementer decision. Letting an implementer edit the canonical table mid-derivation lets locally-convenient names spread silently across the project. The ledger discipline forces every implementer to walk a structured slot set per symbol — which surfaces near-duplicates against canonical names before they propagate.

## Falsification tests

The two tests in §Falsification tests (Substitution, Proof-deletion) exist because LLMs produce plausible-looking justifications that survive any specific change to the object they claim to justify. "Plays a role in the proof of Lemma 3.1" reads as a justification but is true of every symbol in the proof. The Substitution test catches that by mentally swapping the symbol; the Proof-deletion test catches "usage descriptions" masquerading as meanings by mentally hiding the proof. They are diagnostic moves the reviewer runs against slots they suspect are not pulling their weight, not gates walked top-to-bottom on every entry.

## Correctness floor vs. readability layer

`SKILL.md` is the **creation-time correctness floor**: walked at every implementation dispatch, including rough exploratory work, to keep the math trustworthy and machine-checkable. `references/integration.md` is the **readability layer**: loaded when the document needs to be polished for a human reader (paper draft, results write-up, section that has to fit alongside other sections). The two are kept separate because applying the readability layer to first-draft exploratory work bloats the cycle; applying only the readability layer to final output loses the audit trail.

The split is enforced by line-by-line ownership:

- **SKILL.md owns correctness/auditability.** Whether the math is trustworthy, whether each move is justified, whether notation is consistent, whether verification was performed.
- **`references/integration.md` owns readability.** Whether each line is obvious from a half-page reading window, whether prose-to-math references are precise, whether rendered LaTeX is unambiguous, whether the document fits its surrounding sections, whether refactoring preserves the correctness artifacts already produced.

When in doubt: ask "would a first-draft proof that fails this still be auditable?" If yes, it is a readability concern (`integration.md`). If no, it is a correctness concern (`SKILL.md`).

## Stage-scoped references

References load **only at the stage they apply**, per the Stage-Scoped References table in `SKILL.md`. The four references (`planning.md`, `integration.md`, `integrate-drift-tests.md`, `objective-first.md`) are not loaded at every dispatch — the table is the authoritative load map. Adding a new reference requires adding a row with an explicit load condition; dropping a reference requires sweeping the routing rows.

`objective-first.md` is loaded **on demand** from inside `integration.md` Section A — its worked example and identification drills are too long to live in the always-loaded reference but useful enough that the agent can pull them when stuck on the diagnostic move.

## What this skill deliberately does not carry

- **Generic reviewer-protocol mechanics** (verdicts, dependent findings, re-review behavior). These are owned by `agent-orchestration` and the canonical role specs in `agents/`. The Falsification tests in `SKILL.md` are theory-specific; everything else points at the standard protocol.
- **Generic codebase-coherence concerns** (naming consistency, utility reuse, PR-friendly diffs, Project Doc Audit). Owned by `refactor-and-integrate`. `integration.md` Sections A–C are the theory-modeling-specific rewriting layer; Section D guards correctness-discipline artifacts during refactoring; everything else loads `refactor-and-integrate` at `Stage: integration`.
- **Audience-discipline / perspective-collapse essays.** Earlier drafts carried `audience-discipline-modeling.md` and `audience-discipline-writing.md` (~315 lines combined). They were dropped: the operational core (workflow-vocabulary leak detection, three-channel separation) did not pay its keep against the framing-essay overhead, and the worked examples were paper-specific in a way that did not transfer. Concrete prose-to-math precision rules survive in `integration.md` Section B (math-symbol-not-English-description, equation-reference-not-position).
- **Rendering utility.** Owned by `superRA:report-in-markdown`. The skill points at it and otherwise does not invent rendering conventions.

## Extension patterns

**Adding a new check.** Decide whether it is a correctness concern or a readability concern. Correctness → new `[BLOCKING]` or `[ADVISORY]` item under the relevant gate in `SKILL.md`. Readability → new item in `integration.md` Section A/B/C. Walk the DRY/Necessity tests in repo CLAUDE.md before merging — most candidate checks are restatements of an existing gate item.

**Adding a new reference.** Only when the content has a clear load condition that the body of `SKILL.md` or `references/integration.md` cannot itself trigger. Add the row to the Stage-Scoped References table with an explicit load-when. Add a load directive at the call site. References stay one level deep from `SKILL.md`.

**Adding a new domain rationalization.** Common Rationalizations table in `SKILL.md` is for **patterns the gates cannot catch on their own** — placeholder spread, illustrative-numerics excuse, CAS-without-pass-condition, NotConv-table-edit excuse, inherited-notation excuse, cluster-framing dodge. Do not add rows that restate an existing gate `[BLOCKING]` item; the gate is the authoritative copy.

**Tightening a gate.** First check whether the new restriction is already implied by an existing gate item under the falsification tests. If yes, it is a clarification of the existing item, not a new one. If no, ask whether the restriction is a creation-time correctness floor (gate) or a readability rewrite (integration.md). Most "I want to require X in proofs" turn out to be the latter.

## History

This skill was developed across 13 tasks on the `superRA-model-skill` branch, with the four-gate architecture, per-task ledger, falsification tests, and correctness/readability split each emerging from concrete review feedback rather than a priori design. The earliest versions had a single `Define-Derive-Validate` checklist; the four-gate restructuring (Task 5) made the trust-chain order explicit. The per-task ledger (Task 8) and falsification tests (Task 9) responded to LLM-specific failure modes the earlier checklist could not catch. The correctness/readability split (Tasks 10–13) emerged when "produce a correct derivation" and "produce a readable integrated derivation" turned out to need different checklists at different stages — but, importantly, no new workflow stage. If a future change triggers the same instinct ("we need a new stage for X"), revisit whether `Stage: integration` with new references would carry the same weight.
