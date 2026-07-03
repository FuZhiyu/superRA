---
title: "Batch-Screen Fan-Out — Match Dispatch Granularity to Work Weight"
status: approved
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

## Results

Implemented the fan-out granularity change as prose-only literature-review workflow guidance; `agent-orchestration` was not edited. A follow-up Markdown-results section makes paper mentions link to the best available target in a fixed pecking order.

**Workflow executor.**
- `references/workflow.md` now states each round as **search/expand → dedup/admit → batch-screen**. Seeds enter `seen`, form the round-1 included set, and start at expansion, not screening. ([workflow.md:17](../../../skills/literature-review/references/workflow.md#L17))
- Expansion is Tier-3, one dedicated agent per included paper, seeded by the carried handle and limited to that included paper's ledger entry. The expansion work now owns idempotent PDF fetch, deeper read when frontier prioritization needs it, and the ranked handle-bearing candidate set. ([workflow.md:19](../../../skills/literature-review/references/workflow.md#L19))
- Dedup/admission sits before screening: surfaced candidates are collapsed by `citation_client dedup`, only unique canonicals not in `seen` enter the screen bundle, and their handles are carried forward. ([workflow.md:25](../../../skills/literature-review/references/workflow.md#L25))
- Batch screening is Tier-2: one bundled agent screens many unique candidates from metadata + abstract, writes initial ledger entries, returns the included subset for expansion, and pulls depth-escalation candidates into dedicated agents. The text also records the lower same-round `citation_client` process count and reduced S2 rate-gate contention. ([workflow.md:27](../../../skills/literature-review/references/workflow.md#L27))
- The executor template now runs the alternating loop with `included` as the priority queue, Tier-3 expansion, central dedup, Tier-2 screening, and ranking-aware re-enqueueing of included decisions. The three invariants remain explicit. ([workflow.md:36](../../../skills/literature-review/references/workflow.md#L36), [workflow.md:61](../../../skills/literature-review/references/workflow.md#L61))
- The subtree-as-ledger alternative now seeds admitted `not-started` subtasks with handles for bundled screening and moves included subtasks into the dedicated expansion queue. ([workflow.md:65](../../../skills/literature-review/references/workflow.md#L65))

**Screening discipline and inherited convention.**
- `references/search-and-screening.md` now states screening is batched as one Tier-2 dispatch after dedup, distinct from expansion, while preserving the screen-first cost economy and identification-protocol tells. ([search-and-screening.md:28](../../../skills/literature-review/references/search-and-screening.md#L28))
- The depth-escalation rule now says to pull central included papers out of the screen bundle into a dedicated agent for related-work / citation-discussion reading before surfacing candidates. ([search-and-screening.md:30](../../../skills/literature-review/references/search-and-screening.md#L30))
- The parent `literature-review/task.md` snowball convention now matches the batched round shape: expand included papers, dedup/admit centrally, batch-screen unique candidates, keep the priority frontier central. ([../task.md:37](../task.md#L37))

**Markdown results link rule.**
- `SKILL.md` now has a separate `## Markdown Results and Summaries` section requiring literature-review results, summaries, candidate lists, extraction notes, and convergence notes in Markdown to follow `report-in-markdown`. Whenever that Markdown mentions a paper, it links to the first available target in this order: task file, Zotero, web, PDF, Markdown. ([SKILL.md:57](../../../skills/literature-review/SKILL.md#L57))

**Validation.**
- `python3 skills/report-in-markdown/scripts/check_markdown.py skills/literature-review/references/workflow.md skills/literature-review/references/search-and-screening.md superRA/literature-review/task.md` reported all three files clean.
- `rg` found the new loop/tier/rate-gate terms in the edited files and no remaining "one agent per paper" / "screening agent per paper" wording in the edited workflow path.
- The `SKILL.md` frontmatter now parses as YAML after quoting the existing description while adding the link rule. The generic `skill-creator` validator still rejects this repo's existing `user-invocable` key, so validation used YAML parse + markdown checks rather than removing repo-local metadata. ([SKILL.md:3](../../../skills/literature-review/SKILL.md#L3), [SKILL.md:4](../../../skills/literature-review/SKILL.md#L4))
- `./superRA/superra task check` reports no task-tree diagnostics.
