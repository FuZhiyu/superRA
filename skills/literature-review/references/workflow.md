# Workflow — Task-Tree Review Orchestration

Main-agent reference. Load when running a literature review end to end. Dispatched discovery, screening, and extraction agents do not load this.

## Part 1 — Interactive setup

Before discovery, settle the parameters below with the researcher (`AskUserQuestion`), then scaffold the review root task and candidate-paper store. Elicit these — do not impose defaults:

- **Research question and scope** — the topic boundary the review covers.
- **Inclusion/exclusion criteria + quality bar** — the gates a paper must pass, and the outlet-tier / identification-strategy bar (`econ-corpus.md`).
- **Extraction schema** — the per-paper fields each ledger entry records.
- **Seed set** — the starting papers the snowball expands from.
- **Zotero add policy** — whether to save discovered/included papers to Zotero, and if so which **library** (personal or a specific group) and **collection**. This selects the add path in `zotero-paper-reader`: "my library / current selection" saves via the local connector; a group or collection it cannot target uses the cloud Web API. Before any local save, report the currently-selected Zotero destination so the researcher can switch it in the desktop UI first.
- **Candidate store convention** — where non-git candidate-paper folders live for this project.

## Dashboard Shape

Use this tree shape as a recommendation, not a required schema:

```text
superRA/<review>/
  task.md                 # live progress page
  discovery/
  screening/
  papers/                 # promoted included/escalated paper cards
  synthesis/
  saturation-audit/
```

The review root task is the live progress page. Keep it current with corpus counts, candidate-store location, active frontier, dedup conflicts, promoted paper-card links, discovery leads, and saturation evidence.

## Candidate Store And Materialization

Pre-screen candidates live outside git as task-shaped folders. Use the candidate materializer to create/update folders and perform ordinary dedup. The materializer owns clear identity merges; the main agent resolves only flagged conflicts.

Promotion is copy/rename work: when inclusion is clear and promotion is authorized, copy the candidate folder into `superRA/<review>/papers/<paper-key>/` and keep the same body template.

## Dispatch Loop

There is no hidden round state. The written state is: discovery task results, candidate-paper records, screening task results, promoted paper cards, root progress, and saturation-audit notes.

1. Dispatch discovery tasks by lens, seed, included paper, or test-run map. Include `Recommended depth` and bounds; depth can mean citation hops, reading depth, or both.
2. Run the materializer over surfaced records. It updates candidate folders, merges clear duplicates, and reports conflicts.
3. Dispatch screening over candidate records or candidate batches. Screening agents decide membership, may promote authorized included papers, and record `Discovery Leads` rather than broad-searching inline.
4. Dispatch extraction only for included central papers.
5. Periodically synthesize discovery maps, screening batch syntheses, promoted paper cards, and unresolved leads into the review root.
6. Run saturation audit when no unscreened candidate backlog remains, no important included frontier is unexpanded, and the latest discovery pass adds no new in-scope paper.

Review cost is controlled at packet level: review discovery maps/candidate additions, screening batches/promotion choices, extraction tasks, and saturation judgments. Do not dispatch one reviewer per candidate by default.

## Search-Screen Boundary

Search answers: what should enter the candidate store, and what local map did this lens or seed reveal?

Screening answers: which assigned candidates are in scope, with what evidence, and which deserve promotion?

Screening may do targeted verification for the candidate in hand and may add a directly relevant individual candidate record. It must route cluster-level opportunities as `Discovery Leads`; the main agent decides whether to create a new discovery dispatch.

## Saturation Judgment

Stop only when the written state supports it:

- assigned backward and forward discovery has run to local dry conditions or recorded unpursued leads;
- screening has no unresolved high/medium-priority candidate backlog;
- promoted included papers that matter to scope have been expanded or explicitly skipped;
- dedup conflicts are resolved or named as limitations;
- a final discovery pass or lead review adds no new in-scope paper.

Record the evidence on the root progress page and saturation-audit task, including deliberate non-expansions.
