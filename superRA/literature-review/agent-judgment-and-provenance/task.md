---
title: "Agent Judgment & Retrieval Provenance — Delegate Depth/Traversal, Centralize Admission"
status: not-started
depends_on: [citation-client-resilience]
---

## Objective

Rebalance the screen/snowball division of labor in the `literature-review` skill along one principle: **push per-paper judgment to the agent on the spot; keep global coordination — dedup, frontier admission, stopping — central.** And make provenance carry a **retrieval trace**, not just discovery lineage, so a paper surfaced in one round is cheaply refetchable in the next. Three coupled discipline changes to the shipped skill; they compose with the shared response cache and normalized-record handles from [citation-client-resilience](../citation-client-resilience/task.md).

### Context

This is skill-authoring work in the superRA repo: load `skill-creator` before editing `skills/literature-review/SKILL.md` (CLAUDE.md gate), and apply the DRY + Necessity gate to every added line. The skill's **two-role partition must be preserved** — orchestration wording lives in the main-agent `references/workflow.md`; per-paper discipline lives in `references/search-and-screening.md` / `references/grounding-and-extraction.md`. Do not leak orchestration into the per-paper references or vice versa. Scope all edits/commits to this worktree (`/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/literature-review`).

### Deliverables

**1. Screening depth — default economy, not prohibition** (`references/search-and-screening.md`).

- Reframe §Screen-first from "metadata/abstract/intro **only**" into a **default with an escalation trigger**. The binary in/out call resolves from metadata/abstract/intro; when a paper is central and clearly included **and** how it cites the literature will change which frontier edges to prioritize, the agent reads its related-work / citation discussion. Give the agent the decision rule — *read to the depth the decision in front of you needs, no deeper* — not a page budget. Deeper reading uses cheaply-available text (intro / related-work, arXiv HTML); bulk `mistral-pdf-to-markdown` OCR stays the deferred **extraction** step, not a screening escalation. Record the escalation in the ledger (`read_depth` + a one-line reason) so it is an audited choice.
- Narrow the §Identification-protocol **"Over-read screen"** tell so it flags the real waste — full-text reading to make a routine in/out call, or an *exclusion* justified by page numbers (criteria too fine) — while a recorded deeper read of a central included paper for snowball prioritization is legitimate, not a defect.

**2. Retrieval provenance — a refetch trace distinct from discovery lineage** (`SKILL.md` ledger schema, `references/workflow.md`).

- Split the ledger's provenance into **discovery lineage** (`discovered_via`, `bfs_depth` — unchanged) and a new **retrieval block**: `ids` (doi/arxiv/s2/corpus_id), `landing_url`, `pdf_url` + `access` (`oa` | `paywall` | `wp-fallback`), `pdf_path`, `md_path`, `fetched_at`. The version-divergence flag lives in this block. `read_depth` (from Deliverable 1) sits with the decision fields.
- **Carry the handle across rounds.** A surfaced candidate is the normalized paper record the discovering agent already held (ids + url from `citation_client references`), not a bare key/title. In subtree-as-ledger mode, the orchestrator seeds each admitted `not-started` subtask with that handle, so the next dispatched agent reads it via `superra task read` and starts warm — one directed hydration/fetch, no cold search. This composes with the shared client cache (re-hydration is usually a cache hit).

**3. Local traversal + priority frontier — delegate the edge judgment, keep admission central** (`references/workflow.md` executor, `references/search-and-screening.md` snowball sections).

- The dispatched agent, for its paper, **traverses the references and judges relevance in context**, and surfaces a **ranked, annotated, handle-bearing** candidate set: each candidate carries its retrieval handle + a priority + a one-line local reason. It MAY do a **bounded, read-only local peek** — resolve a candidate's metadata (`citation_client metadata`) to confirm scope before surfacing — but it **never creates a ledger entry and never recurses**. Being read-only and non-recursive is what keeps it from reintroducing the duplication/uncoordinated-stop problems that keep admission central; the shared cache makes overlapping peeks cheap.
- The **orchestrator keeps** the single `seen` index, candidate admission, cross-agent dedup, and the saturation/stop judgment — now **ranking-aware**: the frontier becomes a **priority queue** (expand high-signal candidates first, defer weak ones). Update the executor template to consume candidate priority; the file-ownership invariant (one writer per entry) and the global-dedup / global-stop invariants are unchanged and stay explicit.

### Validation criteria

- Two-role partition holds: no orchestration wording in the per-paper references, no per-paper discipline in `workflow.md`.
- Screen-first still communicates the cost economy (no bulk OCR to triage); escalation is selective, recorded (`read_depth`), and the narrowed over-read tell catches waste but not legitimate deeper reads.
- Ledger schema shows the lineage/retrieval split; the executor seeds handles into admitted subtasks; the priority-frontier and central-dedup/stop invariants are explicit and the bounded peek is stated read-only + non-recursive.
- DRY + Necessity gate (CLAUDE.md): every added line shapes behavior; no restated defaults, no cross-skill design rationale in skill bodies; `read_depth` and the retrieval block are the only schema additions.

## Planner Guidance

Prose-tight discipline wording, not new tooling — no code, no new client subcommands. The parent `literature-review/task.md` conventions are reconciled to this design in the same plan revision that creates this task, so treat the parent's Conventions as the current spec and make the skill match it. The bounded local peek is read-only metadata resolution; state plainly that it is not entry creation and not recursion.
