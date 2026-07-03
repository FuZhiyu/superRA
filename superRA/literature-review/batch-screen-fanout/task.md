---
title: "Batch-Screen Fan-Out — Match Dispatch Granularity to Work Weight"
status: not-started
depends_on: [agent-judgment-and-provenance]
---

## Objective

Restructure the loop-until-dry executor in `references/workflow.md` so each round runs as three alternating steps — **search (expand the included set) → dedup → batch-screen** — instead of "one agent per frontier paper does everything." Screening is a light, uniform metadata+abstract decision and most candidates are rejected, so paying a dedicated per-paper dispatch to screen each one is Tier-3 cost for Tier-1 work. Batch it; reserve dedicated agents for the papers that earn a deeper read.

The coordination model from [agent-judgment-and-provenance](../agent-judgment-and-provenance/task.md) — the single `seen` index, ranking-aware admission, the priority frontier, and the three invariants — is unchanged. This changes only the **fan-out granularity**, using the `agent-orchestration` tiering (a Tier-2 bundle for the batched screen, Tier-3 dedicated agents for expansion). Prose-only, no code.

### Context

Skill-authoring in the superRA repo: load `skill-creator` before editing under `skills/`, apply the DRY + Necessity gate, and preserve the two-role partition (orchestration in `workflow.md`; per-paper discipline in `search-and-screening.md`). Scope edits/commits to this worktree (`/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/literature-review`). Build on the just-approved executor — do not undo the priority-queue / handle-seeding / invariants structure.

### Deliverables

**1. Restructure the round into search → dedup → batch-screen** (`references/workflow.md` Part 2 + Executor template).

- **Batch-screen** (Tier-2 bundle): one agent screens *many* unique candidates from metadata + abstract → in/out decision + ledger entry each. Light and uniform. A candidate that triggers the depth-escalation (central, needs its related-work read) is pulled *out* of the batch into its own agent.
- **Expand** (Tier-3, one dedicated agent per **included** paper): the per-paper work that currently lives in the single agent — idempotent PDF fetch, deeper read as needed, and surfacing the **ranked, annotated, handle-bearing** backward + forward candidate set — moves here, because only included papers are expanded and expansion benefits from the deeper read. The multi-lens web sweep runs here as the forward discovery lens.
- **Dedup sits between search and screen** so each unique candidate is screened **exactly once**: a hub paper surfaced by several lenses in one round is collapsed by the `seen`/`citation_client dedup` pass *before* screening, never screened three times.
- **Seeds are the round-1 included set** — researcher-pre-vetted, so they bypass screening; round 1 starts at *expand* (seed expansion + the initial web sweep), not screen.
- Rewrite the executor pseudo-code to the alternating loop; keep the three invariants (one-writer-per-entry, one global dedup/admission, one global stop) and the priority frontier explicit. Note that batching the screen also cuts the number of concurrent `citation_client` processes per round — less contention on the shared S2 rate gate.

**2. Screen section reflects batching** (`references/search-and-screening.md`).

- The §Screen-first / triage guidance states screening is **batched** — one agent screens many candidates because it is metadata+abstract only — and is a step distinct from expansion; the depth-escalation is the signal to pull a paper out of the batch into a dedicated agent. Keep the identification-protocol tells intact.

### Validation criteria

- Executor shows the alternating **search → dedup → batch-screen** loop; dedup is between search and screen (each unique candidate screened once); seeds enter pre-included (round 1 starts at expand); batch-screen is a bundled dispatch and expansion is per-included-paper dedicated.
- The three invariants and the priority frontier survive verbatim in intent; the handle-seeding of admitted candidates is unchanged.
- Two-role partition holds; DRY + Necessity — no new stage vocabulary invented, the change is expressed in `agent-orchestration` tiering terms; the parent `literature-review/task.md` §Snowball convention is reconciled to the batched round shape when this task is implemented.

## Planner Guidance

This is a granularity change, not a new pipeline stage — resist adding a formal "search stage" / "screen stage" to the workflow map; express it as *how the orchestrator sizes each round's dispatches*. The PDF-fetch and candidate-surfacing steps currently enumerated in `workflow.md`'s per-paper agent move into the expansion (per-included) agent; the batch-screen agent does metadata+abstract+decision+ledger-entry only. Keep the `superimplement`-style subtree-as-ledger alternative executor consistent with the new round shape.
