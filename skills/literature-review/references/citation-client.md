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
| OpenCitations | keyless DOI→DOI forward `citations` (and backward `references`) edges from I4OC open references — the forward-citation fallback when S2 throttles | Keyless. `OPENCITATIONS_ACCESS_TOKEN` raises rate limits when set; sent in the `authorization` header only then. Its edges derive from Crossref open references, not OpenAlex, so it does not carry the OpenAlex quality problem. |

Config is read from the environment, then a project-local `Notes/.env`; environment wins. Key **values are never printed** — `health` reports presence as booleans only.

**S2 is optional and degrades gracefully.** On an S2 outage or sustained rate-limiting, any S2-backed command sets `"s2_available": false`, adds an explanatory `notes` entry, and returns whatever the remaining sources produced (exit 0) rather than crashing. Forward `citations` fall back S2 → OpenCitations → empty + a note to run the workflow-layer web sweep; the `source` field records which backend answered.

### Environment variables

| Variable | Meaning |
|---|---|
| `S2_API_KEY` / `SEMANTIC_SCHOLAR_API_KEY` | optional S2 key (institutional-only) |
| `CROSSREF_MAILTO` | opt into Crossref's polite pool |
| `OPENCITATIONS_ACCESS_TOKEN` | optional OpenCitations token; never echoed |
| `CITATION_CLIENT_CACHE_DIR` | coordination + response-cache root (default `Notes/.cache/citation-client/`, self-gitignored) |
| `CITATION_CLIENT_INTERVAL_<BACKEND>` | per-backend rate-gate spacing in seconds, e.g. `CITATION_CLIENT_INTERVAL_S2=1.5` |

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

The network commands (`search`, `references`, `citations`, `metadata`, and `health --probe`) all accept `--no-cache` and `--cache-ttl SECONDS`; see [Concurrency, caching, and rate limits](#concurrency-caching-and-rate-limits).

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
| `--source {s2,crossref,opencitations}` | default `s2`; `crossref` and `opencitations` need a DOI. `crossref` is the uneven, often DOI-less reference array; `opencitations` is DOI→DOI edges from I4OC |
| `--limit N` | max references (default 100) |
| `--raw` | include verbatim payloads |

Output: `{paper, source, s2_available, notes, count, records: […]}`. Crossref-array references carry `source: "crossref-reference"` and an `unstructured` field; they are frequently DOI-less — prefer S2 when available. OpenCitations references carry `source: "opencitations"`, are DOI-keyed, and expose only the DOI (title/authors null) — hydrate with `metadata` if needed.

### `citations PAPER_ID`

Forward citations — the snowball backbone.

| Flag | Meaning |
|---|---|
| `--source {auto,s2,opencitations}` | `auto` (default) = S2 then OpenCitations fallback; `s2` = S2 only (old behavior); `opencitations` = OpenCitations only (needs a DOI) |
| `--limit N` | max citations (default 100) |
| `--raw` | include verbatim payloads |

Output shape matches `references`; `source` reports which backend answered (`s2` or `opencitations`). Fallback chain under `auto`: **S2 → OpenCitations → empty + web-sweep note.** On S2 outage `s2_available: false`; if OpenCitations then answers, `source: "opencitations"` with the DOI→DOI records; if it too is unavailable (or no DOI), `records` is empty with a note to run the workflow-layer forward web sweep.

**Version-DOI union (workflow layer).** OpenCitations is DOI→DOI only, and in economics a paper's forward citations fragment across its version DOIs (NBER `10.3386/*`, SSRN `10.2139/ssrn.*`, and the journal DOI). The client stays **per-DOI**; complete forward coverage requires calling `citations` once per known version DOI and unioning the results — a workflow step, not a tool feature (see [workflow.md](workflow.md) and [search-and-screening.md](search-and-screening.md)).

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

Report `tool_version`, `python_version`, `dependencies` (`stdlib-only`), endpoint URLs (including `opencitations`), config presence (booleans — including `OPENCITATIONS_ACCESS_TOKEN` and `CITATION_CLIENT_CACHE_DIR`, values never printed), `s2_key_mode` (`anonymous-pool` / `keyed`), the resolved `cache_dir`, per-backend `rate_intervals`, and `coordination` (`cross-process` / `per-process`). Add `--probe` to make one S2 call and report `s2_reachable`; without it no network call is made. Pinning the runtime versions here makes behavior drift visible.

## Concurrency, caching, and rate limits

The fan-out is **unbounded** — every screening/extraction agent shells out its own client process, and they share one IP and one filesystem. Three shared-state layers sit in front of the live HTTP call so the collective request rate stays inside what the server measures (per IP), without funnelling agents through a single serialized caller:

- **Shared on-disk response cache.** Keyed by the canonicalized request URL (courtesy params like `mailto` dropped); writes are atomic (temp file + `os.replace`), reads are lock-free. TTL by mutability: immutable `references`/`metadata`/published records ~30d; forward `citations` ~7d (they grow). Snowballing re-hits the same hub papers, so a cache hit skips both the rate gate and the network entirely. `--no-cache` bypasses it; `--cache-ttl SECONDS` overrides the TTL for one call. The cache dir (`CITATION_CLIENT_CACHE_DIR`, default `Notes/.cache/citation-client/`) is created with a self-ignoring `.gitignore` so cached responses never enter version control.
- **Cross-process rate gate.** One next-allowed-time state file per backend host, guarded by `fcntl.flock`. Before each live call a process briefly locks the file, reads `next_ts`, claims `slot = max(now, next_ts)`, writes `next_ts = slot + interval`, releases the lock, then sleeps until `slot`. **The lock is never held during the sleep**, so concurrency is preserved while the global rate is bounded to one request per `interval` across all processes. Defaults (seconds/request): S2 `1.1`, Crossref `0.2`, OpenCitations `0.5`, arXiv `3.0`; override per backend via `CITATION_CLIENT_INTERVAL_<BACKEND>`.
- **Adaptive backoff.** A live `429`/`503` widens the backend's shared `next_ts`/interval (decaying back over subsequent successes), so a real overload signal slows the whole fan-out, not just the unlucky process. The default transport's own `Retry-After`/exponential retry stays behind the gate as a second line of defense, and it still sleeps between Crossref requests per the advertised `X-Rate-Limit-Limit`/`X-Rate-Limit-Interval` headers.

**Coordination scope.** The gate and cache are per-filesystem, so they coordinate exactly the processes on one machine — which is the right granularity because S2 rate-limits per IP and one machine shares one IP. Across machines the gate is per-machine (no shared state); that matches per-IP limits as long as each machine has its own IP. Where `fcntl` is unavailable (non-POSIX), the client degrades to per-process-only coordination rather than crashing; `health` reports `coordination` as `cross-process` or `per-process`.

The offline test suite injects a fake transport plus an injectable clock/sleep and a tmp coordination dir, so it runs deterministically with no network, no keys, and no real waits.
