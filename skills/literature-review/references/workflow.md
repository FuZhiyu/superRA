# Workflow — Task-Tree Review Orchestration

Main-agent reference. Load when running a literature review end to end. Dispatched review agents do not load this.

## Part 1 — Interactive setup

Before discovery, settle the parameters below with the researcher (`AskUserQuestion`), then scaffold the review root task and candidate-paper store. Elicit these — do not impose defaults:

- **Research question and scope** — the topic boundary the review covers.
- **Inclusion/exclusion criteria + quality bar** — the gates a paper must pass, and the outlet-tier / identification-strategy bar (`econ-corpus.md`).
- **Comparison columns** — facts that must be comparable across every included paper; may be empty.
- **Narrative extraction scope** — any free-form grounded notes the review should collect per included paper.
- **Seed set** — the starting papers the snowball expands from.
- **Zotero add policy** — whether to save discovered/included papers to Zotero, and if so which **library** (personal or a specific group) and **collection**. This selects the add path in `zotero-paper-reader`: "my library / current selection" saves via the local connector; a group or collection it cannot target uses the cloud Web API. Before any local save, report the currently-selected Zotero destination so the researcher can switch it in the desktop UI first.
- **Candidate store convention** — where non-git candidate-paper folders live for this project.

## Dashboard Shape

Use this tree shape as a recommendation, not a required schema:

```text
superRA/<review>/
  task.md                 # live progress page
  frontier/
  papers/                 # default permanent-record destination
  synthesis/
  saturation-audit/
```

The review root task is the live progress page. Keep it current with corpus counts, candidate-store location, active frontier, dedup conflicts, permanent-record links, discovery leads, and saturation evidence.

## Candidate Store And Materialization

Pre-screen candidates live outside git as task-shaped folders. Use the candidate materializer to create/update folders, perform ordinary dedup, claim papers for substantive reads, and move candidates to permanent-record destinations. The materializer owns clear identity merges; the main agent resolves only flagged conflicts.

Permanent-record placement is main-agent owned. `superRA/<review>/papers/<paper-key>/` is the default destination, but the main agent may choose another durable location. Use `candidate_materializer.py promote` to move the candidate folder and preserve links.

## Dispatch Loop

There is no hidden round state. The written state is: frontier task results, candidate-paper records, permanent paper records, root progress, and saturation-audit notes.

1. Dispatch frontier assignments by lens, seed, included paper, candidate cluster, or test-run map. Size bounds by expected depth: recon sweeps are wide and shallow; claimed-read assignments are narrow and deep.
2. Recon materializes or updates candidates and leaves them `status: not-started`.
3. A substantive read starts only after the agent wins the materializer claim, which changes the card to `status: in-progress`.
4. Extraction authorization is per dispatch; default to seed expansions and high-priority central candidates, and withhold it for broad recon.
5. At synthesis passes, prioritize accumulated stubs and `Discovery Leads` into the next wave.
6. For included/escalated papers that need durable placement, choose the destination, run `candidate_materializer.py promote`, apply the Zotero add policy when configured, then update the card/task state.
7. Run saturation audit when no unscreened candidate backlog remains, no important included frontier is unexpanded, and the latest discovery pass adds no new in-scope paper.

Review cost is controlled at packet level: review frontier maps, candidate additions, claimed-read outcomes, extraction notes, permanent-record placement choices, and saturation judgments.

Literature-review frontier dispatches can run as ordinary parallel Agent calls without worktree isolation: routine shared writes go through the locked candidate store and citation-client cache, and claim-for-read prevents duplicate substantive reads.

## Dispatch Boundary

Recon answers: what should enter the candidate store, and what local map did this lens or seed reveal?

Claimed reads answer: which assigned candidates are in scope, with what evidence, and which leads deserve follow-up?

Mixed dispatches may expand while reading: materialize leads freely, but claim before reading any newly surfaced paper.

## Saturation Judgment

Stop only when the written state supports it:

- assigned backward and forward frontier work has run to local dry conditions or recorded unpursued leads;
- candidate records have no unresolved high/medium-priority backlog;
- included papers that matter to scope have been expanded or explicitly skipped;
- dedup conflicts are resolved or named as limitations;
- a final discovery pass or lead review adds no new in-scope paper.

Record the evidence on the root progress page and saturation-audit task, including deliberate non-expansions.
