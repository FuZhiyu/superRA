# Workflow — Task-Tree Review Orchestration

Main-agent reference. Load when running a literature review end to end. Dispatched review agents do not load this.

## Setup

Before discovery, settle the review contract with the researcher, then scaffold the review root task and candidate-paper store:

- **Research question and scope** — the topic boundary the review covers.
- **Inclusion/exclusion criteria + quality bar** — the gates a paper must pass, and the outlet-tier / identification-strategy bar (`econ-corpus.md`).
- **Comparison columns** — facts that must be comparable across every included paper; may be empty.
- **Narrative extraction scope** — free-form grounded notes the review should collect per included paper.
- **Seed set** — starting papers or search lenses.
- **Zotero add policy** — whether to save permanent papers to Zotero, and if so which library and collection.
- **Candidate store convention** — where non-git candidate-paper folders live for this project.

Use this tree shape as a recommendation, not a schema:

```text
superRA/<review>/
  task.md                 # live progress page
  frontier/
  papers/                 # default permanent-record destination
  synthesis/
  saturation-audit/
```

Keep the review root task current with corpus counts, candidate-store location, active frontier, dedup conflicts, permanent-record links, discovery leads, and saturation evidence.

## Written State

There is no hidden round state. Read the review from:

- the review root task;
- frontier task results and local maps;
- candidate-paper records in the non-git store;
- permanent paper records;
- synthesis and saturation-audit notes.

Pre-screen candidates live outside git as task-shaped folders. Use the candidate materializer to create/update folders, dedup clear identity matches, claim papers for substantive reads, and move candidates into durable locations. The materializer owns ordinary identity merges; the main agent resolves flagged conflicts.

## Paper State

A paper card starts at `status: not-started`. That means the paper has enough metadata to identify or refetch it and is available for future work; it does not mean the paper has been read.

Recon dispatches materialize or update paper cards and leave them `not-started`. If recon sees a candidate that already exists, use that written state for prioritization and local mapping rather than following it by default.

A substantive read starts only after an agent wins `candidate_materializer.py claim`, which changes the card to `status: in-progress`. A losing claim adopts the existing card state.

A completed claimed read lands `implemented` when the decision, notes, lead harvest, and extraction for an included or escalated paper are complete. It lands `archived` when the card is closed as duplicate, superseded, unusable, or out of scope.

## Dispatch Shapes

Choose a loose dispatch type at the frontier boundary: `recon` or `claimed read`. Synthesis passes choose the next frontier from the written state.

### Recon Dispatch

Use recon to expand the map: web lenses, seed metadata, reference lists, forward-citation edges, author pages, venue clusters, or a backlog of not-started candidates. Recon answers: what should enter the candidate store, what changed in priorities, and what the local map reveals.

Recon may inspect metadata, abstracts, citation lists, citation snippets, and source text needed to understand citation context. It materializes useful papers and high-signal beyond-bounds stubs, records provenance, and reports patterns or counts for filtered edges. It leaves papers `not-started`.

### Claimed-Read Dispatch

Use a claimed-read dispatch when the next question requires a paper-level decision or extraction. Assign a narrow set of candidates or an included paper that needs its permanent extraction. The agent claims each paper before reading it.

Claimed reads answer: whether assigned papers are included, excluded, or escalated; what evidence supports the decision; which leads deserve follow-up; and what grounded facts or narrative notes enter the review for included or escalated papers.

Extraction is part of the same claimed-read job. The review agent loads `grounding-and-extraction.md` and extracts from an included or escalated paper before closing the card.

Claimed reads may have recon side effects: while reading one source, the agent may materialize leads freely, but it claims before substantively reading any newly surfaced paper.

### Synthesis Pass

Use synthesis passes to turn accumulated written state into the next frontier. Prioritize not-started stubs, `Discovery Leads`, unresolved dedup conflicts, included-paper expansions, and gaps in the comparison columns or narrative extraction scope.

## Parallelism

Literature-review frontier dispatches can run as ordinary parallel Agent calls without worktree isolation. Routine shared writes go through the locked candidate store and citation-client cache, and claim-for-read prevents duplicate substantive reads.

Control review cost at packet level: review frontier maps, candidate additions, claimed-read outcomes, extraction notes, permanent-record placement choices, and saturation judgments.

## Permanent Records And Zotero

Permanent-record placement is main-agent owned. `superRA/<review>/papers/<paper-key>/` is the default destination, but the main agent may choose another durable location. Use `candidate_materializer.py promote` to move the candidate folder and preserve provable links.

For included or escalated papers that need durable placement, choose the destination, promote the folder, apply the Zotero add policy when configured, and update the paper record. Zotero dedup/add fires during main-agent finalization for permanent papers, not for every candidate. If no Zotero target was configured, keep local artifact links in the paper record.

Before any local Zotero save, report the currently selected desktop Zotero destination so the researcher can switch it if needed. For a group or collection the local connector cannot target, route through `zotero-paper-reader`'s cloud Web API path.

## Saturation Judgment

Stop only when the written state supports it:

- assigned backward and forward frontier work has run to local dry conditions or recorded unpursued leads;
- candidate records have no unresolved high/medium-priority backlog;
- included papers that matter to scope have been expanded or explicitly skipped;
- dedup conflicts are resolved or named as limitations;
- a final discovery pass or lead review adds no new in-scope paper.

Record the evidence on the root progress page and saturation-audit task, including deliberate non-expansions.
