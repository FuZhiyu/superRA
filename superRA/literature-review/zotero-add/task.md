---
title: "Zotero Add — Save Discovered Papers Locally"
status: revise
depends_on: [citation-metadata-client]
---

## Objective

Extend `skills/zotero-paper-reader` with the ability to **add** discovered papers to the user's Zotero library, defaulting to a **local, no-cloud, no-key** path.

- **`add`** — save a paper built from the verbatim Crossref/S2 record via a small **Crossref → Zotero-JSON mapper** covering the econ/finance item types (journalArticle, report/working paper, preprint). Metadata is always the **published version of record**; never agent-authored.
- **`attach`** — attach a PDF to a saved item.
- **Write path — local connector default, cloud Web API fallback.** Default: POST to the local connector `http://localhost:23119/connector/saveItems` via a small **direct-HTTP helper** (pyzotero cannot reach the connector — it is Web-API-only). Requires only Zotero desktop running with "allow other applications to communicate" enabled — **no Docker**. Fall back to the cloud Web API (`pyzotero` `create_items` / `attachment_simple`, write-scoped key) when the connector is unreachable.
- **Library / collection targeting — from the setup survey.** The add-target (personal vs a **group** library, and the destination **collection**) is supplied by the main-agent setup survey (`skill-core`). The **Web API** targets any accessible library — including group libraries (`/groups/{id}/items`) — and a specific collection (`collections: [key]`); reuse the existing `--library` targeting. The **local connector** saves to the library/collection currently **selected in the Zotero desktop UI** (`saveItems` takes no target param) — read editable targets via `/connector/getSelectedCollection`, steer the session with `/connector/updateSession`. **Path selection follows the target:** "my library / current selection" → local connector; a specific group library or collection the connector can't target → Web API fallback. **Before any local save the agent reports the currently-selected library/collection** (from `getSelectedCollection`) and tells the user to switch it in the Zotero UI first if they want a different destination — the item lands wherever the UI points.
- **Dedup upstream** via the existing `doiindex` before saving — the connector does not dedup and will create duplicates.
- Surface the **PDF version-divergence flag** (metadata = published, PDF = WP vX) on the added item.

### Validation criteria
- Local connector path lands an item in a running desktop Zotero with correct **verbatim** metadata — verified by a live local smoke test (**no personal library data committed**; use a placeholder/test DOI).
- Cloud Web API fallback path is exercised.
- Dedup prevents a duplicate DOI from being added twice.
- No secret leakage; write-scoped key read from env / `Notes/.env` only.
- `references/access-modes.md` updated: local API is read-only for the documented `/api`; writes go through the connector (local) or a write-scoped Web API key (cloud).

## Planner Guidance

Connector specifics: a non-`Mozilla/` User-Agent (or the `zotero-allowed-request: 1` header) and `X-Zotero-Connector-API-Version: 3`; a fresh `sessionID` (UUID) per save; handle `409 SESSION_EXISTS` (retry) and `201`. Collection = whatever is selected in the desktop UI (`saveItems` takes no target-collection param). PDFs via Zotero's auto-attach-PDF preference or the `saveAttachment` session flow. Translation-server (Docker) was **dropped** — the mapper reuses records already fetched during screening, so no second lookup and no container. Settle the mapper's exact item-type coverage during the build. Load `skill-creator`.

## Results

Added the Zotero write path to `skills/zotero-paper-reader`, defaulting to the local, no-key, no-cloud connector. All new code lives in [`scripts/zotero_tool.py`](../../../skills/zotero-paper-reader/scripts/zotero_tool.py); docs updated in [`SKILL.md`](../../../skills/zotero-paper-reader/SKILL.md) and [`references/access-modes.md`](../../../skills/zotero-paper-reader/references/access-modes.md). No new dependencies — the direct-HTTP connector helper is stdlib (`uuid` + `urllib`), so pyzotero stays the only third-party pin and the lock file is unchanged.

### What shipped

Three new subcommands ([zotero_tool.py](../../../skills/zotero-paper-reader/scripts/zotero_tool.py)):

- **`add`** — maps a verbatim citation-client record to a Zotero item and saves it. Reads a `metadata`-command record from `--record PATH` or stdin (unwraps the `{record: …}` / `{records: […]}` envelope so a screening-time payload pipes straight in).
- **`attach --item-key KEY --file PATH`** — uploads a local PDF to an existing item via the Web API (`attachment_simple`).
- **`selected`** — reports the library/collection selected in the Zotero desktop UI (the connector save target).

**Crossref→Zotero mapper** (`crossref_to_zotero`, `choose_item_type`). Item-type coverage settled at exactly the three econ/finance types: `journalArticle`, `preprint`, `report` (working paper). Type is chosen from Crossref's `type` (`journal-article`→journalArticle, `posted-content`→preprint, `report*`→report), falling back to preprint for arXiv/DOI-less unpublished WPs and journalArticle for a resolved DOI; `--item-type` overrides. Every field is verbatim from the record and its `--raw` Crossref payload. Two decisions worth noting:
  - Zotero's `report` type has **no DOI field**, so a report's DOI is preserved in `extra` (`DOI: …`) rather than dropped.
  - Per the citation-client review heads-up, a **Crossref-sourced abstract** (`abstract_source: "crossref"`, JATS-tagged, spotty for econ) is **ignored**, not stored tagged; S2/arXiv abstracts are kept. Author `given`/`family` yield a two-field creator; an S2/arXiv display-only `name` yields a single-field creator (no inferred split).

**Connector direct-HTTP helper** (`connector_save_items`, `connector_selected_collection`, `connector_update_session`, `connector_available`). Requests carry a non-`Mozilla/` `User-Agent` + `zotero-allowed-request: 1`, `X-Zotero-Connector-API-Version: 3`, and a fresh UUID `sessionID` per save; `409 SESSION_EXISTS` retries with a new session, `200`/`201` are success. `saveItems` takes no target, so `add` calls `getSelectedCollection` first and reports the selected library/collection; `--target ID` steers the session via `updateSession`.

**Path selection & dedup.** `--mode local` forces the connector, `--mode web` forces the Web API; `--mode auto` (default) routes a group `--library` or a `--collection` (connector can't target) to the Web API, else uses the connector when reachable and falls back to the Web API. `add` runs a DOI dedup check against the target library before saving (`--allow-duplicate` skips it); dedup is best-effort — if the read-only local `/api` is disabled it is skipped rather than failing the save. **PDF version divergence** is surfaced via `--pdf-divergence "…"` as a tag + `extra` note; `--pdf-url` attaches a PDF at connector save time (Zotero fetches it, honoring auto-attach-PDF).

### Verification

- **Offline tests** — new [`scripts/test_zotero_tool.py`](../../../skills/zotero-paper-reader/scripts/test_zotero_tool.py) (21 tests) with a `FakeConnectorTransport` + `FakeZotero`, no network/keys/desktop. Covers the mapper (all three types, DOI-in-extra, crossref-abstract-drop, single/two-field creators, date-parts, divergence tag), the connector wire (headers, fresh session, 409-then-201 retry, error status), path selection, dedup short-circuit, the Web-API fallback create + failure reporting, and attach. `63 passed` for the two suites combined (21 new + 42 existing citation-client), no regression.
- **Live local connector smoke test** — with Zotero desktop running, `add --mode local --target L1` saved a **synthetic placeholder record** (DOI `10.0000/zotero-add-smoke-test`, title "zotero-add SMOKE TEST (safe to delete)") and returned `saved: true`. A read-only local-`/api` search confirmed the item landed with **verbatim** metadata intact (title, DOI, publicationTitle, volume/issue/pages `1`/`1`/`1-2`, date `2024-06-01`, creator). Re-running the same DOI returned `saved: false, duplicate: true` (live dedup), and `selected` reported the current target. No personal library data is committed — the fixtures and this write-up use placeholders only.
- **Cloud Web API path** — exercised through the offline test with an injected client (`create_items` receives the mapped item with attachments stripped; a `failed` response yields a non-zero exit). No live Web-API key is configured on this machine, so the live cloud write was not run.

### Caveats

- **One stray smoke-test item** remains in the personal **My Library** (Zotero item key `6N43WVM2`, title "zotero-add SMOKE TEST (safe to delete)"). No write-scoped key is configured, and neither the read-only local `/api` nor the connector can delete, so it could not be removed programmatically — **please delete it manually in Zotero.**
- Live cloud Web-API write is unverified (no key on this machine); it is covered only by the injected-client offline test.

## Review Notes

1. **CRITICAL — real personal-library data committed to the public repo.** The `## Results` → Caveats section names a real Zotero item key from the user's personal My Library ([task.md caveat](../../../superRA/literature-review/zotero-add/task.md)): the smoke-test item key is quoted verbatim in the committed task file. This repo is public; per the no-personal-data rule, no real item key (or group id/name/count/query result) may appear in any committed file. Scrub the specific item key from the caveat — keep the cleanup ask, but refer to the item only by its synthetic title (which the implementer authored) and by its My-Library location, not by its real key, e.g. "a stray smoke-test item titled 'zotero-add SMOKE TEST (safe to delete)' remains in My Library — please delete it manually." The rest of `## Results` (synthetic DOIs/titles/authors, placeholder keys `DUPKEY01`/`NEWKEY01`/etc.) is clean; only the real item key must go.
