---
title: "Read-Once Review Agent — One Judgment-Bounded Role Replaces the Stage Pipeline"
status: not-started
depends_on:
  - shared-store-and-client-mechanisms
---

## Objective

Replace the three-stage per-paper pipeline (discovery → screening → extraction, each dispatch reopening the same source) with a **single review-agent role**: the agent that opens a paper finishes it. There is no survey/screening/extraction role boundary — a dispatch assigns a frontier and loose bounds, and the agent's on-the-ground judgment decides what to open and how deep to go. Rewrite the skill references accordingly.

### Required design

**One role, judgment-bounded traversal** (`references/review-agent.md`, replacing both `discovery.md` and `screening.md`):

- A dispatch assigns a **frontier** — a seed to expand, a cluster of pending candidates, or a web lens — plus **loose bounds**: recommended citation hops (typically 2), an extraction authorization, and a soft paper budget. Within bounds, the agent decides what to open; beyond bounds, stub and report — don't chase.
- **Edge triage uses the best signal available.** How the text in hand cites a paper is the primary signal for whether that paper is worth pursuing — so edge judgment happens while reading, and harvested leads carry the quoted citation context in their provenance. Bulk edge lists with no read context (e.g. hundreds of forward cites of a hub paper, via the version-union call) are triaged from metadata — hydrate DOI-only edges via `citation_client metadata`, judge scope fit from title/abstract/venue/year against the review's criteria — and stubbed with a priority, with the filtered remainder recorded as counts/patterns in the local map.
- **Everything one read enables happens in that session**: the screening decision (rationale, gate, outlet tier, identification strategy per `econ-corpus.md`); extraction when the paper is included + central and the dispatch authorized it (load `grounding-and-extraction.md`, OCR via `mistral-pdf-to-markdown`, idempotent `md_path` reuse); lead harvest from its related-work discussion; promotion via `candidate_materializer.py promote` when authorized; escalation for ambiguous cases. An included paper whose extraction was not authorized exits flagged `extraction-pending` with Reading Notes rich enough for a later session to resume from notes plus the stored artifact, not a cold re-read.
- **Claim-on-open.** Before opening any source, the agent claims it atomically in the shared store (mechanism from the dependency task). A paper already claimed or decided is adopted, not re-read — the claim, not batch pre-partitioning, is what makes parallel dispatches safe for papers discovered mid-flight.
- **Write-as-you-go.** Complete each paper's record (decision, notes, stubs harvested from it) before opening the next, so an exhausted context loses nothing: the remaining frontier persists as stubs and the next dispatch continues from written state.
- A web-lens sweep is the same role with a wide, mostly-metadata assignment: stub what the lens surfaces; open a source only when a quick read settles scope the metadata leaves ambiguous.
- The local-map and leads report survives from the current discovery protocol.

**Reading Notes are a resume log, not stage glue.** `SKILL.md` §Candidate And Paper Records keeps `## Reading Notes` as an append-only read log (`[session, depth, what was read]` + grounded takeaways) whose purpose is resuming a paper in a later session — deferred extraction, escalation, late centrality upgrade. The default path is that one session does all the reading; a resumed session adopts and re-verifies facts already grounded with a quote instead of re-deriving them.

**Extraction shape is a researcher-elicited hybrid** (`grounding-and-extraction.md`): setup elicits the comparison columns as "what must be comparable across every included paper" (may be empty) — those become shared matrix columns; everything else is a free-form grounded narrative note per paper; an empty column set collapses the shape to narrative-only. The grounding invariants (DOI resolution before trusting a cite, quote-per-claim with location, extract-then-verify, null vs "not reported") stay mandatory regardless of shape.

**Dispatch loop** (`workflow.md` rewrite):

1. Dispatches are frontier assignments with bounds, sized by expected depth — a web-lens sweep is wide and shallow, a seed expansion narrow and deep. They run **concurrently as ordinary parallel Agent calls without worktree isolation** — the only shared mutable state is the non-git candidate store and the client cache, both concurrency-safe, and claim-on-open prevents double-processing (a stated exception to `agent-orchestration`'s worktree-per-parallel-task default, with this reason inline).
2. Extraction authorization per dispatch; default: authorized for seed expansions and high-priority central candidates, withheld otherwise, with the researcher able to redirect at synthesis passes.
3. **Lead sweep at each periodic synthesis pass**: accumulated stubs and `Discovery Leads` are prioritized into the next wave of frontier assignments.
4. **Zotero-library dedup + add fires at promotion time**, once per promoted paper (routed to `zotero-paper-reader`) — not per candidate.
5. Saturation audit unchanged.

Part 1 interactive setup additionally elicits the comparison columns alongside the extraction schema.

### Files to update

- `skills/literature-review/SKILL.md` — reference map re-partitioned by loader (main agent: `workflow.md`; review agent: `review-agent.md` + `econ-corpus.md`, plus `grounding-and-extraction.md` at extraction depth; all: `citation-client.md`), record schema (`## Reading Notes`), composed-skill trigger points.
- `skills/literature-review/references/workflow.md` — frontier-assignment dispatch loop, setup elicitation, parallel-dispatch exception, authorization default, lead-sweep cadence, Zotero-dedup trigger.
- `skills/literature-review/references/discovery.md` + `screening.md` → `review-agent.md` — the single-role protocol above.
- `skills/literature-review/references/grounding-and-extraction.md` — hybrid shape, adopt-and-reverify.
- Any file referencing the retired reference filenames (trigger test, `econ-corpus.md`, `citation-client.md` cross-links).

### Validation criteria

- `rg` over the skill finds no instruction that routes a paper to a second agent to reopen a source already read — re-opening exists only on the Reading-Notes resume path (deferred extraction, escalation).
- `rg -l 'discovery\.md|screening\.md'` returns no hits repo-wide outside git history.
- `review-agent.md` states claim-on-open, write-as-you-go, the hop/budget bounds with stub-and-report beyond them, and both edge-triage modes (citation-context while reading; metadata for bulk edge lists) as explicit protocol.
- `workflow.md` states the parallel-dispatch exception, extraction-authorization default, lead-sweep cadence, and Zotero-dedup trigger as explicit checkable statements.
- `grounding-and-extraction.md` describes the hybrid with the empty-matrix (narrative-only) case; invariants read as mandatory independent of shape.
- `python3 skills/report-in-markdown/scripts/check_markdown.py` runs clean over every changed markdown file; the skill-trigger test still passes.

## Planner Guidance

This is skill-creation work — load `skill-creator` before editing any `SKILL.md`, and apply CLAUDE.md §Teach the Protocol line by line; collapsing two role references into one should shrink total instruction text, not grow it. The claim mechanism, `promote` subcommand, and version-union call exist from the dependency — reference them by name. Do not re-litigate `econ-corpus.md`'s corpus discipline; only its loader assignment changes. Bounds are guidance, not gates: the agent may stop shallower than the recommended hops when the frontier is locally dry, and must stub-and-report rather than exceed them.
