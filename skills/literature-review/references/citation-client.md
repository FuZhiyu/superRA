# Citation-Graph & Metadata Client — Command Surface

Bundled script: [`../scripts/citation_client.py`](../scripts/citation_client.py). Stdlib-only, PEP 723. Run from anywhere:

```
uv run --script <skill-root>/scripts/citation_client.py <subcommand> [args]
```

`python3 <skill-root>/scripts/citation_client.py …` also works (no third-party deps). Every subcommand prints one JSON object on stdout; errors go to stderr as `error: <message>` with a non-zero exit. `--help` is available on every subcommand.

This client is **one discovery lens, not the entry point.** Front-line discovery leads with the agent's web search (S2/Crossref lag on the newest working papers); the client supplies filterable indexed search, the citation graph for snowballing, and verbatim metadata hydration.

## Backends and keys

| Backend | Role | Key |
|---|---|---|
| Semantic Scholar (S2) | relevance search, backward `references`, forward `citations`, abstracts | Optional. Anonymous pool by default; `S2_API_KEY` (or `SEMANTIC_SCHOLAR_API_KEY`) used when set. S2 keys are now institutional-only — treat as optional. |
| Crossref | authoritative published-version-of-record metadata by DOI/title; uneven `reference` array fallback | Keyless. Set `CROSSREF_MAILTO` to use the faster, more reliable polite pool. |
| arXiv | q-fin/econ preprint abstracts + metadata | Keyless. |

Config is read from the environment, then a project-local `Notes/.env`; environment wins. Key **values are never printed** — `health` reports presence as booleans only.

**S2 is optional and degrades gracefully.** On an S2 outage or sustained rate-limiting, any S2-backed command sets `"s2_available": false`, adds an explanatory `notes` entry, and returns whatever the remaining sources produced (exit 0) rather than crashing. Forward `citations` are S2-only, so on an S2 outage they return empty with a note to fall back to the workflow-layer web sweep.

## Normalized paper record

`search`, `references`, `citations`, and `metadata` return records in this shape. Bibliographic fields are mapped **verbatim** from the source payload — the client never composes metadata.

```json
{
  "id": {"doi": "10.1111/jofi.10001", "arxiv": "2101.00001", "s2": "aaaa1111", "corpus_id": 900001},
  "title": "Heterogeneous Investors and Asset Prices",
  "authors": [{"name": "Ada Lovelace", "given": "Ada", "family": "Lovelace"}],
  "year": 2023,
  "venue": "The Journal of Finance",
  "abstract": "We study how investor heterogeneity ...",
  "abstract_source": "s2",
  "url": "https://doi.org/10.1111/jofi.10001",
  "is_open_access": true,
  "external_ids": {"DOI": "10.1111/jofi.10001", "ArXiv": "2101.00001", "CorpusId": 900001},
  "source": "crossref"
}
```

- `id.doi` is normalized (lowercased, prefix-stripped) and is the primary dedup key. Any field may be `null`.
- `authors[].given` / `family` are populated only from Crossref (published version of record); S2 and arXiv expose a display `name` only, so `given`/`family` are `null` there — never infer a split downstream.
- `abstract_source` is `"s2"`, `"arxiv"`, `"crossref"`, or `null`. In `metadata`, abstract preference is S2 plain text → arXiv (`q-fin.*`/`econ.*`) → Crossref only as a last resort (Crossref abstracts are JATS-tagged and spotty for econ).
- `source` records which backend produced the record. S2 records also carry `fields_of_study`, `citation_count`, `reference_count`; Crossref records also carry `type`, `volume`, `pages`.
- `--raw` adds the verbatim source payload under `raw` (for the Zotero web-translator mapping downstream).

## Subcommands

### `search QUERY`

Indexed relevance/bibliographic search.

| Flag | Meaning |
|---|---|
| `--source {s2,crossref,both}` | backend(s), default `both` |
| `--limit N` | max results per source (default 25) |
| `--year-min Y` / `--year-max Y` | publication-year filter |
| `--venue V` | venue / container-title filter |
| `--field F` | S2 `fieldsOfStudy` filter (e.g. `Economics`) |
| `--raw` | include verbatim payloads |

Output: `{query, source, s2_available, notes, count, records: [record, …]}`.

### `references PAPER_ID`

Backward references. `PAPER_ID` is a DOI, arXiv id, or S2 id.

| Flag | Meaning |
|---|---|
| `--source {s2,crossref}` | default `s2`; `crossref` needs a DOI and is the uneven, often DOI-less fallback |
| `--limit N` | max references (default 100) |
| `--raw` | include verbatim payloads |

Output: `{paper, source, s2_available, notes, count, records: […]}`. Crossref-array references carry `source: "crossref-reference"` and an `unstructured` field; they are frequently DOI-less — prefer S2 when available.

### `citations PAPER_ID`

Forward citations — the snowball backbone. **S2-only** (Crossref has none). Same `--limit` / `--raw`. Output shape matches `references` with `source: "s2"`. On S2 outage: `s2_available: false`, empty `records`, and a note to use the forward web sweep.

### `metadata IDENTIFIER`

Hydrate one record from `IDENTIFIER` (DOI / arXiv id / S2 id), resolving to the published version of record when one exists.

- Resolves to a DOI (given, or discovered via S2 `externalIds`) and fetches the **authoritative Crossref record** as the primary.
- Layers an abstract preferring S2 → arXiv over a Crossref abstract, without overwriting any other verbatim Crossref field.
- Falls back to the arXiv record (preprint) when no published DOI resolves, else to the S2 record.

Output: `{identifier, id_type, version_of_record, s2_available, sources_used, notes, record}`. `version_of_record` is `true` only when a Crossref published record was found. A working paper with no published version yet yields `version_of_record: false` with a note — the workflow layer then takes metadata from the source page's `citation_*` / Dublin Core meta tags.

### `dedup`

Run the dedup cascade over a JSON array of records (from `--file PATH` or stdin; also accepts a `{"records": […]}` or a prior `{"clusters": [{"canonical": …}]}` wrapper).

Cascade: normalized **DOI** → exact normalized **title+year** → **fuzzy** title (`SequenceMatcher`) at same year.

| Band | Behavior |
|---|---|
| ratio ≥ 0.98 | auto-merge (`match_basis: "fuzzy-title"`) |
| 0.90 ≤ ratio < 0.98 | **flagged in `review_pairs`, never auto-merged** |
| exact title+year, conflicting volume/pages | blocked, flagged as `title-year-volpages-conflict` |

Handles DOI-less preprints (fuzzy title+year) and reordered author lists (keyed on DOI/title/year, not author order). Borderline matches are **flagged for review, never auto-dropped.**

Output: `{n_input, n_clusters, clusters: [{cluster_id, members: [input-idx…], size, match_basis, canonical}], review_pairs: [{a, b, ratio, basis, note}]}`. `canonical` is the richest member of the cluster. `members` are indices into the input array.

### `health`

Report `tool_version`, `python_version`, `dependencies` (`stdlib-only`), endpoint URLs, config presence (booleans), and `s2_key_mode` (`anonymous-pool` / `keyed`). Add `--probe` to make one S2 call and report `s2_reachable`; without it no network call is made. Pinning the runtime versions here makes behavior drift visible.

## Rate limits

The default transport retries `429`/`503` with `Retry-After`/exponential backoff and, for Crossref, sleeps between requests per the advertised `X-Rate-Limit-Limit` / `X-Rate-Limit-Interval` headers. The offline test suite injects a fake transport, so it runs with no network and no keys.
