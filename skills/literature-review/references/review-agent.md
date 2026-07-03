# Review Agent Protocol

Load for literature-review frontier dispatches.

## Frontier Bounds

A dispatch gives a frontier, a loose type (`recon` or `claimed read`), and bounds: seed, candidate cluster, or web lens; recommended citation hops; and a soft paper budget. Stay within those bounds. For high-signal leads beyond the bounds, materialize/update a `not-started` stub when minimal metadata exists and report why it was not chased.

## Materialize Many, Claim Before Read

Use [citation-client.md](citation-client.md) for materializer commands.

Recon may inspect search metadata, abstracts, citation lists, citation snippets, or source text needed to understand citation context. Use that context to identify papers, materialize/update candidate cards, add provenance, and prioritize leads. Recon leaves surfaced papers `status: not-started`.

Before a substantive read for decision, notes, or extraction, run `candidate_materializer.py claim <key> --by <dispatch-label>`. The winning claim changes the card to `status: in-progress`; a losing claim returns the existing state, which you adopt.

## Edge Triage

For citation leads found while reading a source paper, record the source paper and quoted citation context in the candidate's discovery provenance. For bulk edge lists without read context, hydrate DOI-only edges with `citation_client metadata`, judge title/abstract/venue/year against the review criteria, and materialize the useful records with priority notes.

Use `citation_client.py citations-union` when a paper has multiple known version DOIs.

## Claimed Reads

Load [grounding-and-extraction.md](grounding-and-extraction.md) for claimed-read dispatches.

A claimed read settles the paper:

- decide `included`, `excluded`, or `escalate`;
- record reason, failed gate when excluded, outlet tier, and identification strategy;
- harvest targeted leads from related-work/citation discussion;
- extract when the paper is included or escalated.

For included or escalated papers, complete extraction before closing the claimed read.

Write the card before claiming another paper. Finish as `implemented` when decision/notes/extraction are complete, or `archived` when the card is closed as duplicate, superseded, unusable, or out of scope.

## Reading Notes

Use `## Reading Notes` for claimed reads: session label, what was read, and grounded takeaways. Citation context gathered while recon-expanding another paper stays in discovery provenance for the cited paper.

## Local Map

End every dispatch with:

```markdown
## Local Map

### Central candidates

### Adjacent but probably out of scope

### New clusters / authors / venues

### Next Discovery Leads
```
