---
title: "Citation Client Resilience — Cross-Process Rate Coordination + OpenCitations Fallback"
status: not-started
depends_on: [citation-metadata-client]
---

## Objective

Make the bundled `citation_client.py` safe for **concurrent fan-out use** and add a **keyless forward-citation fallback**, so parallel screening/extraction agents stop collectively rate-limiting Semantic Scholar. Today each fan-out agent shells out its own client process; the per-process backoff in `_DefaultTransport` cannot see the other processes, so N agents collide on S2's anonymous pool and 429 even at low per-agent volume.

The design keeps the fan-out unbounded (agents are **not** funneled through a single serialized caller). Coordination is via **shared on-disk state**, guarded by a filesystem lock. This is the correct granularity because S2 rate-limits per IP and all fan-out processes on one machine share an IP and a filesystem — so a filesystem-scoped gate bounds exactly the quantity the server measures.

### Deliverables

**1. Cross-process coordination inside `citation_client.py`** — three additions in front of the existing transport, which stays as the second line of defense:

- **Shared on-disk response cache.** Key = `(subcommand, backend, normalized identifier/query, salient params)`; value = the JSON response + fetch timestamp. Reads are lock-free; writes are atomic (temp file + `os.replace`). Cache dir configurable via `CITATION_CLIENT_CACHE_DIR`, defaulting to a project-local `Notes/.cache/citation-client/`; ensure it is gitignored. TTL by result mutability: effectively-immutable results (`references`, `metadata`, published records) long (default ~30d); forward `citations` shorter (default ~7d, they grow). Flags `--no-cache` and `--cache-ttl`. Snowballing re-hits the same hub papers, so the cache is a first-order win independent of the rate gate.
- **Cross-process rate gate — one "next-allowed-time" state file per backend host**, guarded by `fcntl.flock`. Before each live HTTP call: acquire the lock briefly, read `next_ts`, compute `slot = max(now, next_ts)`, write `next_ts = slot + interval`, release the lock, then sleep until `slot`. The lock is **never held during the sleep**, so concurrency is preserved while the global request rate is bounded to one per `interval` across all processes. Per-backend `interval` configurable via env; conservative defaults (S2 anonymous ≈ 1 req/s → ~1.1s; Crossref polite faster; OpenCitations a few req/s).
- **Adaptive backoff on 429/503.** When a live call still returns 429/503, in addition to the existing per-process retry, push the backend's shared `next_ts` outward (widen the effective interval, decaying back over subsequent successful calls) so a real overload signal slows the whole fan-out, not just the unlucky process.

**2. OpenCitations backend (keyless) for forward citations.**

- `citations` and `references` gain `--source … opencitations`. OpenCitations Index v2: `/index/api/v2/citations/{doi}` (forward), `/index/api/v2/references/{doi}` (backward). **Keyless**; send an optional `OPENCITATIONS_ACCESS_TOKEN` in the `authorization` header only when set. Its edges derive from Crossref open references (I4OC), not from OpenAlex — so it does not carry the OpenAlex quality problem.
- Fallback chain for `citations`: S2 → on sustained rate-limit / outage, OpenCitations → else empty records + the existing web-sweep note. Records normalized to the standard paper-record shape with `source: "opencitations"`, DOI-keyed. Set `s2_available`/`notes` so the consumer sees which backend answered.
- OpenCitations is DOI→DOI only. In econ, a paper's forward citations fragment across its version DOIs (NBER `10.3386/*`, SSRN `10.2139/ssrn.*`, and the journal DOI), so complete forward coverage requires **unioning across a paper's known version DOIs**. Keep the client **per-DOI**; document the version-union as a workflow-layer step in the reference and workflow docs.

**3. Reference + workflow doc updates.**

- `references/citation-client.md`: add the cache and coordination model, the OpenCitations backend row + subcommand flags, the new env vars (`CITATION_CLIENT_CACHE_DIR`, per-backend interval overrides, `OPENCITATIONS_ACCESS_TOKEN`), and rewrite the `## Rate limits` section to describe the cross-process gate. Note the per-IP/per-filesystem coordination scope and its degradation (across machines, the gate is per-machine — which matches per-IP limits).
- `references/workflow.md` (and `search-and-screening.md` where forward-citation snowballing is taught): add the version-DOI union step for forward citations and note OpenCitations as the keyless fallback when S2 is throttled.

### Validation criteria

- **Offline suite extended** (`test_citation_client.py`, injected fake transport + injectable clock/sleep + a tmp coord dir — no network, no keys, matching the existing 42-test convention): cache hit / miss / TTL-expiry / atomic-write; rate-gate slot spacing under a simulated set of concurrent callers (assert issued request times are spaced ≥ `interval`); adaptive-backoff widening on a 429; OpenCitations payload parsing → normalized record; the S2→OpenCitations→web-sweep fallback chain.
- **No-key / no-network preserved**: OpenCitations works keyless; the gate and cache require no network; `health` reports the new config presence as booleans only and never prints token values.
- **Concurrency smoke**: launch several client processes at once against a fake/stub endpoint and confirm the shared `next_ts` file spaces them (no self-collision) and the fan-out is not serialized to one-at-a-time beyond the rate bound.
- **Secret hygiene**: `OPENCITATIONS_ACCESS_TOKEN` read from env / `Notes/.env` only, never echoed; cache dir gitignored; no personal data written to cache fixtures in tests (repo is public).

## Planner Guidance

Prefer the "next-allowed-time" gate over a classic token bucket — it is simpler to make correct across processes and never holds the lock during the wait. Reuse `_DefaultTransport`'s existing 429/503 retry and Crossref header sleep as-is; the gate sits in front of the live call, the retry stays behind it. `fcntl.flock` is POSIX (macOS/Linux) — fine for this environment; if a portability guard is cheap, degrade to no-coordination (per-process only) rather than crashing on a platform without `fcntl`. Keep the client per-DOI for OpenCitations; the version-DOI union belongs in the workflow, not the tool. This modifies the [citation-metadata-client](../citation-metadata-client/task.md) deliverable, so keep the pinned command-surface additions backward-compatible — new flags and a new `--source` value only, no changes to existing JSON shapes.
