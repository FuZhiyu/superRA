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

Screen/extract agents run in rounds. Each round selects the current frontier, dispatches **one agent per paper**, then the orchestrator dedups what the agents surface, admits the in-scope canonicals, and grows the frontier. Each agent writes **only its own** ledger entry, so no two agents touch the same file.

Each dispatched agent starts from the **handle** the orchestrator seeded — the normalized record ids + `landing_url` from the round that surfaced its paper — so it hydrates a known artifact rather than running a cold search. For its one paper it:

1. Fetch metadata + abstract verbatim from the published version of record (`citation_client metadata` on the seeded ids, or a source-page `citation_*` / Dublin Core tag when no structured record exists). Re-hydration off the handle is usually a shared-cache hit.
2. Screen against the criteria from metadata / abstract / intro, escalating read depth only when the decision needs it (`search-and-screening.md`).
3. For an included paper, fetch the PDF **idempotently** — check the durable store first and reuse an existing copy, else fetch best-effort and record `pdf_url` + `access`, `pdf_path`, `fetched_at`; on a paywall fall back to the freely-available WP and set the version-divergence flag (`econ-corpus.md`). The store is the Zotero item's attachment when the setup survey's add policy targets Zotero (via `zotero-paper-reader`'s add/attach path), else a local `Notes/papers/<paper-key>/`.
4. Write its ledger entry per the schema in SKILL.md, rendering the retrieval fields as the navigable trace link cluster that schema specifies.
5. Return a **ranked, annotated, handle-bearing** candidate set — backward references (`citation_client references`) and forward-citation / web-sweep hits, each carrying its retrieval handle, a priority, and a one-line reason — for the orchestrator to dedup and admit. Forward citations run S2 → OpenCitations (keyless) when S2 throttles, unioned across the paper's version DOIs (NBER / SSRN / journal); see `search-and-screening.md`.

The screening discipline, the bounded read-only candidate peek, the dedup cascade, and the stopping judgment are in `search-and-screening.md`.

## Executor template

The orchestrator owns the `seen` dedup index and frontier growth; each round is a parallel fan-out. The frontier is a **priority queue** — high-signal candidates expand first, weak ones defer — so the loop consumes the priority the agents attach to their surfaced candidates.

```
seen = {}                      # THE single dedup index: normalized DOI / title+year → paper key (orchestrator-owned)
frontier = priority queue seeded from the setup survey       # high-signal candidates first

while frontier is non-empty:
    batch = highest-priority papers on the frontier
    dispatch one screening agent per paper in batch,
        seeding each with its handle (ids + landing_url)     (in parallel; one writer per entry)
    returned = union of every agent's ranked, handle-bearing candidates
               (backward references + forward-cite / web-sweep hits)

    clusters = citation_client dedup over returned           # cross-agent dedup — orchestrator-owned
    new = in-scope canonicals not already in seen
    add new to seen
    enqueue new onto frontier by candidate priority          # ranking-aware admission; carry each handle

    if the round added no in-scope canonical:                # a dry round
        break

record the convergence judgment and any deliberate non-expansions
```

Three invariants hold regardless of ranking: **one writer per entry** — each agent edits only its own ledger file; **one global dedup index** — `seen`, cross-agent dedup, and admission are the orchestrator's alone, agents surface but never admit; **one global stop** — saturation is judged over the whole frontier, not per agent. Local judgment (edge relevance, candidate priority) sits with the agent; global coordination stays central.

Stop on a dry round after both a full backward round and the forward web sweep have run — see `search-and-screening.md` for the concrete saturation test and what to record.

**Alternative executor.** Inside a superRA tree, run the rounds as a `superimplement`-style dispatch loop over the per-paper subtasks: the subtree-as-ledger `status` field is the frontier, so each round dispatches the `not-started` entries and marks them as they are screened. Admitting a candidate means creating its `not-started` subtask **seeded with the handle** — the normalized record ids + `landing_url` from the round that surfaced it — so the dispatched agent reads it via `superra task read` and starts warm off that handle instead of a cold search. Use the plain loop above when the review is standalone.
