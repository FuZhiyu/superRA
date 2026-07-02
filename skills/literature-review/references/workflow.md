# Workflow — Setup & Fan-Out Orchestration

Main-agent reference. Load when running a review end to end: the interactive setup, then the loop-until-dry fan-out. Dispatched per-paper agents do not load this — they screen and extract per the dispatch prompt and the domain references it names.

## Part 1 — Interactive setup

Before any discovery, settle the parameters below with the researcher (`AskUserQuestion`), then scaffold the ledger. Elicit these — do not impose defaults:

- **Research question and scope** — the topic boundary the review covers.
- **Inclusion/exclusion criteria + quality bar** — the gates a paper must pass, and the outlet-tier / identification-strategy bar (`econ-corpus.md`).
- **Extraction schema** — the per-paper fields each ledger entry records.
- **Seed set** — the starting papers the snowball expands from.
- **Zotero add policy** — whether to save discovered/included papers to Zotero, and if so which **library** (personal or a specific group) and **collection**. This selects the add path in `zotero-paper-reader`: "my library / current selection" saves via the local connector; a group or collection it cannot target uses the cloud Web API. Before any local save, report the currently-selected Zotero destination so the researcher can switch it in the desktop UI first.

## Part 2 — Fan-out execution (loop-until-dry)

Screen/extract agents run in rounds. Each round selects the current frontier, dispatches **one agent per paper**, then the orchestrator dedups what the agents surface and grows the frontier. Each agent writes **only its own** ledger entry, so no two agents touch the same file.

Each dispatched agent, for its one paper:

1. Fetch metadata + abstract verbatim from the published version of record (`citation_client metadata`, or a source-page `citation_*` / Dublin Core tag when no structured record exists).
2. Screen against the criteria from metadata / abstract / intro only.
3. Write its ledger entry per the schema in SKILL.md.
4. Return surfaced candidates — backward references (`citation_client references`) and forward-citation / web-sweep hits — for the orchestrator to dedup.

The screening discipline, dedup cascade, and stopping judgment are in `search-and-screening.md`.

## Executor template

The orchestrator owns the `seen` dedup index and frontier growth; each round is a parallel fan-out.

```
seen = {}                      # normalized DOI / title+year → paper key
frontier = seed set            # from the setup survey

while frontier is non-empty:
    dispatch a screening agent for each paper in frontier   (in parallel)
    returned = union of every agent's surfaced candidates
               (backward references + forward-cite / web-sweep hits)

    clusters = citation_client dedup over returned           # cross-agent dedup
    new = in-scope canonicals not already in seen
    add new to seen
    frontier = new

    if new is empty:           # a dry round
        break

record the convergence judgment and any deliberate non-expansions
```

Stop on a dry round after both a full backward round and the forward web sweep have run — see `search-and-screening.md` for the concrete saturation test and what to record.

**Alternative executor.** Inside a superRA tree, run the rounds as a `superimplement`-style dispatch loop over the per-paper subtasks: the subtree-as-ledger `status` field is the frontier, so each round dispatches the `not-started` entries and marks them as they are screened. Use the plain loop above when the review is standalone.
