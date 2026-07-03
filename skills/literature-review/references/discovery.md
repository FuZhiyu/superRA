# Discovery Agent Protocol

Implementer reference. Load when a dispatch asks you to search a lens, run a test-map pass, or expand from a seed/included paper.

Your job is to discover candidate papers and map the local area. Do not decide final corpus membership and do not launch unbounded recursive search.

## Dispatch Depth

Follow the dispatch's `Recommended depth` and bounds. Depth may mean citation hops, reading depth, or both:

- **Depth 0** — inspect search-result metadata only.
- **Depth 1** — inspect metadata, abstract, and introduction for surfaced candidates.
- **Depth 2** — inspect related-work / citation discussion of central candidates to find second-order leads.
- **Depth 3** — dedicated expansion of an included central paper; requires the dispatch to authorize it.

Stop shallower when the assigned lens/seed is locally dry. If high-signal leads remain at the bound, report them under `## Next Discovery Leads` instead of exceeding the bound.

## Candidate Records

Write surfaced papers into the project-convention candidate-paper store as task-shaped folders. Use the candidate materializer when available so naming and ordinary dedup are consistent. The candidate `task.md` uses the same body sections as a promoted paper card, but it stays outside git until screening promotes it.

Each candidate record includes:

- verbatim metadata and identifiers;
- discovery provenance (`discovered_via`, lens/source, and `bfs_depth`);
- retrieval handle (`ids` plus `landing_url`);
- priority for screening or later expansion;
- one-line local reason for relevance or promise.

For citation-based finds, include the source paper and exact local context:

```markdown
## Discovery Provenance

Discovered via: [source-paper-key](../../papers/source-paper-key/task.md)
Citation context:
> Short quoted passage that identifies why this edge matters.

Depth: 1
Lens: backward-citation
```

If the source paper is not promoted, link to the candidate record when that path is stable; otherwise record the source handle.

## Search Work

Use the assigned surfaces or seed:

- working-paper lenses: SSRN, NBER, RePEc/IDEAS, arXiv `q-fin` / `econ`, author pages, and broad web;
- citation graph: `citation_client references PAPER_ID` for backward edges and `citation_client citations PAPER_ID` for forward edges;
- indexed search: `citation_client search` as a supplement, not the only front line.

Forward citations of economics papers can fragment across NBER, SSRN, and journal DOIs. Query each known version DOI and union the results.

You may call `citation_client metadata` before writing a candidate when metadata clarifies scope or priority. This is a local peek: do not recurse into the candidate's own references unless the dispatch depth explicitly allows that hop.

## Local Stop Judgment

Stop and report when additional search is unlikely to change the screening queue for the assigned lens/seed. Your report includes:

- assigned surfaces/seeds covered;
- last productive query/source;
- final pass result: duplicates, out-of-scope results, or no new high/medium-priority candidates;
- remaining leads not pursued because they exceed the depth bound or scope;
- confidence: high / medium / low.

Global saturation belongs to the main agent and saturation audit, not to a discovery agent.

## Local Map

End every discovery task with a compact synthesis:

```markdown
## Local Map

### Central candidates

### Adjacent but probably out of scope

### New clusters / authors / venues

### Next Discovery Leads
```
