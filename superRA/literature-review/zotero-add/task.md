---
title: "Zotero Add — Save Discovered Papers Locally"
status: not-started
depends_on: [citation-metadata-client]
---

## Objective

Extend `skills/zotero-paper-reader` with the ability to **add** discovered papers to the user's Zotero library, defaulting to a **local, no-cloud, no-key** path.

- **`add`** — save a paper built from the verbatim Crossref/S2 record via a small **Crossref → Zotero-JSON mapper** covering the econ/finance item types (journalArticle, report/working paper, preprint). Metadata is always the **published version of record**; never agent-authored.
- **`attach`** — attach a PDF to a saved item.
- **Write path — local connector default, cloud Web API fallback.** Default: POST to the local connector `http://localhost:23119/connector/saveItems` via a small **direct-HTTP helper** (pyzotero cannot reach the connector — it is Web-API-only). Requires only Zotero desktop running with "allow other applications to communicate" enabled — **no Docker**. Fall back to the cloud Web API (`pyzotero` `create_items` / `attachment_simple`, write-scoped key) when the connector is unreachable.
- **Library / collection targeting — from the setup survey.** The add-target (personal vs a **group** library, and the destination **collection**) is supplied by the main-agent setup survey (`skill-core`). The **Web API** targets any accessible library — including group libraries (`/groups/{id}/items`) — and a specific collection (`collections: [key]`); reuse the existing `--library` targeting. The **local connector** saves to the library/collection currently **selected in the Zotero desktop UI** (`saveItems` takes no target param) — read editable targets via `/connector/getSelectedCollection`, steer the session with `/connector/updateSession`. **Path selection follows the target:** "my library / current selection" → local connector; a specific group library or collection the connector can't target → Web API fallback.
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
