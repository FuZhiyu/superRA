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

Run each round as **search/expand → dedup/admit → batch-screen**. Seeds are researcher-vetted, so they enter as the round-1 included set and start at expansion.

**Expand included papers** with Tier-3 dedicated agents. Each expansion agent starts from the **handle** the orchestrator seeded — the normalized record ids + `landing_url` — and updates only that included paper's ledger entry, then:

1. Fetches the PDF **idempotently** for its included paper — check the durable store first and reuse an existing copy, else fetch best-effort and record `pdf_url` + `access`, `pdf_path`, `fetched_at`; on a paywall fall back to the freely-available WP and set the version-divergence flag (`econ-corpus.md`). The store is the Zotero item's attachment when the setup survey's add policy targets Zotero (via `zotero-paper-reader`'s add/attach path), else a local `Notes/papers/<paper-key>/`.
2. Reads deeper only when the paper's related-work / citation discussion will change which frontier edges to prioritize (`search-and-screening.md`).
3. Returns a **ranked, annotated, handle-bearing** candidate set — backward references (`citation_client references`) and forward-citation / web-sweep hits, each carrying its retrieval handle, a priority, and a one-line reason — for the orchestrator to dedup and admit. Forward citations run S2 → OpenCitations (keyless) when S2 throttles, unioned across the paper's version DOIs (NBER / SSRN / journal); see `search-and-screening.md`.

**Dedup/admit** centrally before screening. The orchestrator runs `citation_client dedup` over every surfaced candidate, collapses same-round duplicates, admits only unique canonicals not already in `seen`, and carries each admitted handle into the screen bundle.

**Batch-screen candidates** with a Tier-2 bundled dispatch. One screening agent handles many unique candidates from metadata + abstract, writes one initial ledger entry per candidate, and returns the included subset for the next expansion round. A candidate that triggers the depth-escalation rule is pulled out of the bundle and assigned to a dedicated agent instead of being screened in the batch. The bundle also reduces same-round `citation_client` process count, lowering contention on the shared S2 rate gate.

The screening discipline, the bounded read-only candidate peek, the dedup cascade, and the stopping judgment are in `search-and-screening.md`.

## Executor template

The orchestrator owns the `seen` dedup index and frontier growth; each round is a parallel fan-out. The frontier is a **priority queue** — high-signal candidates expand first, weak ones defer — so the loop consumes the priority the agents attach to their surfaced candidates.

```
seen = {}                      # THE single dedup index: normalized DOI / title+year -> paper key (orchestrator-owned)
included = priority queue seeded from the setup survey       # seeds are pre-included; high-signal papers expand first

while included is non-empty:
    expand_batch = highest-priority included papers
    dispatch one dedicated expansion agent per paper,
        seeding each with its handle (ids + landing_url)     (Tier-3; in parallel)
    surfaced = union of every agent's ranked, handle-bearing candidates
                (backward references + forward-cite / web-sweep hits)

    clusters = citation_client dedup over surfaced           # cross-agent dedup/admission — orchestrator-owned
    new = canonicals not already in seen
    add new to seen

    screen_bundle = unique new candidates whose decision fits metadata + abstract
    dispatch one bundled screening agent over screen_bundle  # Tier-2; one writer per entry
    escalate central candidates needing deeper read to dedicated agents
    enqueue included decisions by candidate priority         # ranking-aware admission; carry each handle

    if the round added no in-scope canonical:                # a dry round
        break

record the convergence judgment and any deliberate non-expansions
```

Three invariants hold regardless of ranking: **one writer per entry** — a batch-screen agent creates each candidate entry, and later expansion is one dedicated agent per included entry; **one global dedup index** — `seen`, cross-agent dedup, and admission are the orchestrator's alone, agents surface but never admit; **one global stop** — saturation is judged over the whole frontier, not per agent. Local judgment (edge relevance, candidate priority) sits with the agent; global coordination stays central.

Stop on a dry round after both a full backward round and the forward web sweep have run — see `search-and-screening.md` for the concrete saturation test and what to record.

**Alternative executor.** Inside a superRA tree, run the rounds as a `superimplement`-style dispatch loop over the per-paper subtasks: the subtree-as-ledger `status` field carries each candidate's screen/expansion state. Admitting a candidate means creating its `not-started` subtask **seeded with the handle** — the normalized record ids + `landing_url` from the round that surfaced it — so the bundled screening agent reads warm handles instead of running cold searches. Included subtasks then enter the priority queue for dedicated expansion. Use the plain loop above when the review is standalone.
