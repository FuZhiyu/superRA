---
title: "Read-Once Review Agent — One Judgment-Bounded Role Replaces the Stage Pipeline"
status: not-started
depends_on:
  - shared-store-and-client-mechanisms
---

## Objective

Replace the three-stage per-paper pipeline (discovery -> screening -> extraction, each dispatch reopening the same source) with a **single review-agent role** whose dispatch may be recon-only or a substantive read. There is no discovery/screening/extraction role boundary — a dispatch assigns a frontier and loose bounds, and the agent's on-the-ground judgment decides what to materialize, what to claim for reading, and how deep to read once claimed. Rewrite the skill references accordingly.

### Required design

**One role, dispatch-bounded traversal** (`references/review-agent.md`, replacing both `discovery.md` and `screening.md`):

- A dispatch assigns a **frontier** — a seed to expand, a cluster of pending candidates, or a web lens — plus **loose bounds**: recommended citation hops (typically 2), extraction authorization, and a soft paper budget. Within bounds, the agent decides what to materialize and, when authorized, what to claim for a substantive read; beyond bounds, stub and report — don't chase.
- **Materialize many, claim before read.** A paper card exists only for a specific paper with minimal metadata and starts `status: not-started`. Recon work may inspect search metadata, abstracts, citation lists, or citation snippets to identify papers, materialize/update candidate cards, add provenance, and prioritize leads; it does not make those papers "read" and leaves them `not-started`. Before substantively reading a candidate for a decision, notes, or extraction, the agent calls the atomic claim command from the dependency task, which changes `status: not-started` to `status: in-progress`. A paper already claimed, implemented, approved, or archived is adopted, not re-read.
- **Edge triage uses the best signal available.** How the text in hand cites a paper is the primary signal for whether that paper is worth pursuing — so harvested leads carry the quoted citation context in their provenance. Bulk edge lists with no read context (e.g. hundreds of forward cites of a hub paper, via the version-union call) are triaged from metadata — hydrate DOI-only edges via `citation_client metadata`, judge scope fit from title/abstract/venue/year against the review's criteria — and stubbed with a priority, with the filtered remainder recorded as counts/patterns in the local map.
- **Everything one claimed read enables happens in that session**: the screening decision (rationale, gate, outlet tier, identification strategy per `econ-corpus.md`); extraction when the paper is included + central and the dispatch authorized it (load `grounding-and-extraction.md`, OCR via `mistral-pdf-to-markdown`, idempotent `md_path` reuse); lead harvest from its related-work discussion; escalation for ambiguous cases. The agent finishes the card as `implemented` when decision/notes/extraction are complete, or `archived` when local evidence closes it as duplicate, superseded, unusable, or out of scope.
- **Write-as-you-go.** Complete each paper's record before claiming the next substantive read, so an exhausted context loses nothing: the remaining frontier persists as `not-started` stubs and the next dispatch continues from written state.
- A web-lens sweep is the same role with a wide, mostly-metadata assignment: stub what the lens surfaces; claim a source only when the dispatch authorizes a substantive read and the read is needed to settle scope.
- The local-map and leads report survives from the current discovery protocol.

**Reading Notes are for substantive reads, not recon.** `SKILL.md` §Candidate And Paper Records keeps `## Reading Notes` as an append-only log for claimed reads (`[session, what was read]` + grounded takeaways) whose purpose is resuming a paper in a later session — deferred extraction, escalation, late centrality upgrade. Citation-context gathered while recon-expanding another paper belongs in discovery provenance, not Reading Notes for the cited paper.

**Extraction shape is a researcher-elicited hybrid** (`grounding-and-extraction.md`): setup elicits the comparison columns as "what must be comparable across every included paper" (may be empty) — those become shared matrix columns; everything else is a free-form grounded narrative note per paper; an empty column set collapses the shape to narrative-only. The grounding invariants (DOI resolution before trusting a cite, quote-per-claim with location, extract-then-verify, null vs "not reported") stay mandatory regardless of shape.

**Dispatch loop** (`workflow.md` rewrite):

1. Dispatches are frontier assignments with bounds, sized by expected depth — recon sweeps are wide and shallow, while claimed-read assignments are narrow and deep. They run **concurrently as ordinary parallel Agent calls without worktree isolation** — routine shared writes go through the non-git candidate store and client cache, both concurrency-safe, and claim-for-read prevents double-processing (a stated exception to `agent-orchestration`'s worktree-per-parallel-task default, with this reason inline).
2. Extraction authorization per dispatch; default: authorized for seed expansions and high-priority central candidates, withheld otherwise, with the researcher able to redirect at synthesis passes.
3. **Lead sweep at each periodic synthesis pass**: accumulated stubs and `Discovery Leads` are prioritized into the next wave of frontier assignments.
4. **Permanent-record placement is main-agent owned.** The review agent may recommend inclusion/escalation, but the main agent chooses whether and where to move the candidate folder into a permanent record. `superRA/<review>/papers/` is the default destination, not a hard-coded requirement.
5. **Zotero-library dedup + add fires during main-agent finalization when the setup policy enables Zotero**, once per permanent paper record (routed to `zotero-paper-reader`) — not per candidate.
6. Saturation audit unchanged.

Part 1 interactive setup additionally elicits the comparison columns alongside the extraction schema.

### Files to update

- `skills/literature-review/SKILL.md` — reference map re-partitioned by loader (main agent: `workflow.md`; review agent: `review-agent.md` + `econ-corpus.md`, plus `grounding-and-extraction.md` at extraction depth; all: `citation-client.md`), record schema (`## Reading Notes`), composed-skill trigger points.
- `skills/literature-review/references/workflow.md` — frontier-assignment dispatch loop, setup elicitation, parallel-dispatch exception, authorization default, lead-sweep cadence, main-agent permanent-record placement, Zotero-dedup trigger.
- `skills/literature-review/references/discovery.md` + `screening.md` → `review-agent.md` — the single-role protocol above.
- `skills/literature-review/references/grounding-and-extraction.md` — hybrid shape, adopt-and-reverify.
- Any file referencing the retired reference filenames (trigger test, `econ-corpus.md`, `citation-client.md` cross-links).

### Validation criteria

- `rg` over the skill finds no instruction that routes a paper to a second agent to reopen a source already read — re-opening exists only on the Reading-Notes resume path (deferred extraction, escalation).
- `rg -l 'discovery\.md|screening\.md'` returns no hits repo-wide outside git history.
- `review-agent.md` states "materialize many, claim before read", write-as-you-go, the hop/budget bounds with stub-and-report beyond them, and both edge-triage modes (citation context from the source being read; metadata for bulk edge lists) as explicit protocol.
- `workflow.md` states the parallel-dispatch exception, extraction-authorization default, lead-sweep cadence, main-agent permanent-record placement, and policy-gated Zotero trigger as explicit checkable statements.
- `grounding-and-extraction.md` describes the hybrid with the empty-matrix (narrative-only) case; invariants read as mandatory independent of shape.
- `python3 skills/report-in-markdown/scripts/check_markdown.py` runs clean over every changed markdown file; the skill-trigger test still passes.

## Planner Guidance

This is skill-creation work — load `skill-creator` before editing any `SKILL.md`, and apply CLAUDE.md §Teach the Protocol line by line; collapsing two role references into one should shrink total instruction text, not grow it. The skill-file wording should teach the compact rule, not a new state taxonomy: candidate cards begin `not-started`; recon never changes that; the materializer claim command is the only way to enter `in-progress`; a finished substantive read lands `implemented` or `archived`; main-agent finalization lands `approved` when appropriate. The claim mechanism, `promote` subcommand, and version-union call exist from the dependency — reference them by name. Do not re-litigate `econ-corpus.md`'s corpus discipline; only its loader assignment changes. Bounds are guidance, not gates: the agent may stop shallower than the recommended hops when the frontier is locally dry, and must stub-and-report rather than exceed them.
