---
title: "Read-Once Paper Processing — Survey/Paper Roles Replace the Stage Pipeline"
status: not-started
depends_on:
  - shared-store-and-client-mechanisms
---

## Objective

Replace the three-stage per-paper pipeline (discovery → screening → extraction, each dispatch reopening the same source) with a two-role, read-once architecture: roles split by **cost class**, not pipeline stage, so one agent completes everything a paper needs in one reading session. Rewrite the skill references accordingly.

### Required design

**Two roles by cost class:**

- **Survey role** (`references/survey.md`, renaming `discovery.md`) — metadata-only breadth work: web lenses, indexed search, citation-graph expansion using the version-union call, forward sweeps. Writes candidate stubs (verbatim metadata, provenance, priority, one-line relevance judged from the metadata/abstract already in hand) into the shared store via the materializer. Citation-graph edges are triaged at metadata level: hydrate DOI-only edges via `citation_client metadata`, judge scope fit from title/abstract/venue/year against the review's criteria, stub the in-scope-plausible with a priority, and record the filtered remainder as counts/patterns in the local map rather than stubbing every edge. Survey triage sets screening priority, never membership; high-precision edge judgment from citation context belongs to the paper role's lead harvest. A survey agent never fetches the paper artifact (landing-page full text or PDF). The local-map and leads report survives from the current discovery protocol.
- **Paper role** (`references/paper-processing.md`, replacing `screening.md`) — a paper agent receives a **disjoint batch** of pending candidates; per paper, one reading session completes everything the paper needs at its warranted depth:
  1. screening decision from metadata/abstract/intro, with rationale, gate, outlet tier, and identification strategy (`econ-corpus.md`);
  2. when the paper is included + central **and the dispatch authorizes extraction**, continue in the same session to full-text extraction — load `grounding-and-extraction.md`, OCR via `mistral-pdf-to-markdown` (idempotent: reuse `md_path`);
  3. harvest backward-citation / related-work leads while the text is open, written as candidate stubs with quoted citation context — write stubs, never recurse into them;
  4. promote via `candidate_materializer.py promote` when authorized; escalate ambiguous cases.

  An included paper whose extraction was not authorized is flagged `extraction-pending` with Reading Notes rich enough that the later extraction wave resumes from notes plus the stored artifact, not a cold re-read.

**Reading Notes become a resume log, not stage glue.** `SKILL.md` §Candidate And Paper Records keeps `## Reading Notes` as an append-only read log (`[session, depth, what was read]` + grounded takeaways), but its purpose is resuming a paper in a *later* session — deferred extraction, escalation, late centrality upgrade. The default path is that one session does all the reading and no second session is needed.

**Extraction shape is a researcher-elicited hybrid** (`grounding-and-extraction.md`): setup elicits the comparison columns as "what must be comparable across every included paper" (may be empty) — those become shared matrix columns; everything else is a free-form grounded narrative note per paper; an empty column set collapses the shape to narrative-only. The grounding invariants (DOI resolution before trusting a cite, quote-per-claim with location, extract-then-verify, null vs "not reported") stay mandatory regardless of shape. A fact already grounded with a quote earlier in the session or in Reading Notes is adopted and re-verified, not re-derived.

**Dispatch loop** (`workflow.md` rewrite):

1. Survey dispatches by lens/seed run **concurrently as ordinary parallel Agent calls without worktree isolation** — the only shared mutable state is the non-git candidate store and the client cache, both concurrency-safe (a stated exception to `agent-orchestration`'s worktree-per-parallel-task default, with this reason inline).
2. Materializer/dedup pass over surfaced records → the pending queue.
3. Paper dispatches over **disjoint pending batches** — assignment-based claiming: the main agent partitions the queue so no two dispatches share a paper; stubs harvested mid-flight land as pending for the next wave. Batch size follows authorized depth: screen-only batches larger (~10–20), extraction-authorized batches small (~2–5). Each dispatch states whether extraction is authorized; default: authorized for seed expansions and high-priority central candidates, withheld otherwise, with the researcher able to redirect at synthesis passes.
4. **Lead sweep at each periodic synthesis pass**: accumulated stubs and `Discovery Leads` are prioritized into the next survey or paper wave.
5. **Zotero-library dedup + add fires at promotion time**, once per promoted paper (routed to `zotero-paper-reader`) — not per candidate.
6. Saturation audit unchanged.

Part 1 interactive setup additionally elicits the comparison columns alongside the extraction schema.

### Files to update

- `skills/literature-review/SKILL.md` — reference map re-partitioned by loader (main agent: `workflow.md`; survey agent: `survey.md`; paper agent: `paper-processing.md` + `econ-corpus.md`, plus `grounding-and-extraction.md` at extraction depth; all: `citation-client.md`), record schema (`## Reading Notes`), composed-skill trigger points.
- `skills/literature-review/references/workflow.md` — dispatch loop, setup elicitation, parallel-survey exception, batch/authorization defaults, lead-sweep cadence, Zotero-dedup trigger.
- `skills/literature-review/references/discovery.md` → `survey.md` — metadata-only boundary, version-union call, stub writing.
- `skills/literature-review/references/screening.md` → `paper-processing.md` — the read-once session protocol above, `promote` wiring.
- `skills/literature-review/references/grounding-and-extraction.md` — hybrid shape, adopt-and-reverify.
- Any file referencing the renamed reference filenames (trigger test, `econ-corpus.md`, `citation-client.md` cross-links).

### Validation criteria

- `rg` over the skill finds no instruction that routes a paper to a second agent to reopen a source already read — re-opening exists only on the Reading-Notes resume path (deferred extraction, escalation).
- `rg -l 'discovery\.md|screening\.md'` returns no hits repo-wide outside git history.
- `workflow.md` states the parallel-survey exception, disjoint-batch assignment, extraction-authorization default, lead-sweep cadence, and Zotero-dedup trigger as explicit checkable statements.
- `grounding-and-extraction.md` describes the hybrid with the empty-matrix (narrative-only) case; invariants read as mandatory independent of shape.
- `python3 skills/report-in-markdown/scripts/check_markdown.py` runs clean over every changed markdown file; the skill-trigger test still passes.

## Planner Guidance

This is skill-creation work — load `skill-creator` before editing any `SKILL.md`, and apply CLAUDE.md §Teach the Protocol line by line; the rewrite should shrink total instruction text, not grow it. The `promote` subcommand and version-union call exist from the dependency — reference them by name. Do not re-litigate `econ-corpus.md`'s corpus discipline; only its loader assignment changes. The survey/paper split exists because a breadth agent surfacing dozens of candidates cannot hold per-paper deep reads in one context — keep that boundary crisp rather than letting survey agents "peek just a little" into artifacts.
