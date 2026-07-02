# Zotero Access Modes

## Local API (default, read-only)

Pyzotero connects to Zotero Desktop over localhost when the local API is enabled. No credentials are required. This mode supports all read operations: metadata search, full-text search, item lookup, children, collections, tags, attachment full-text retrieval, and local file retrieval. The documented local `/api` is **read-only** — it serves no write path. Local writes go through the desktop **connector** instead (see [Write path](#write-path-adding-papers)).

**How to enable:** In Zotero Desktop → Settings → Advanced → enable "Allow other applications on this computer to communicate with Zotero."

Construct with `local=True`. Pyzotero 1.13.0 still requires both `library_id` and `library_type` in local mode; the local API serves the desktop's default user library at id `0`:

```python
from pyzotero import zotero
zot = zotero.Zotero(library_id=0, library_type="user", local=True)
```

The tool script detects local API availability via a probe of `http://localhost:23119/api/users/0/items` and uses local mode automatically when it returns a successful response. Note that the Zotero connector port can answer (`Zotero is running`) while the local API itself is disabled — in that case the `/api` path returns `403 Local API is not enabled`, which the probe treats as unavailable. When local is unavailable, the tool falls back to the Web API if credentials are configured.

## Web API (fallback)

Used when local Zotero is unavailable, when accessing a non-public group library, or for any future write operation.

**Required environment variables:**

| Variable | Description |
|---|---|
| `ZOTERO_LIBRARY_ID` | Integer user or group ID. Personal: find at zotero.org/settings/keys. Group: integer after `/groups/` in the group URL. |
| `ZOTERO_LIBRARY_TYPE` | `user` (default) or `group`. |
| `ZOTERO_API_KEY` | API key from zotero.org/settings/keys. Read-only scope covers every read command; the `add` / `attach` write commands on the Web API path need a **write-scoped** key for the target library. |

Set via environment (recommended — e.g., in `secrets.sh` or shell profile) or place in `Notes/.env` (gitignored, Dropbox-synced):

```
ZOTERO_API_KEY=your-key-here
ZOTERO_LIBRARY_ID=12345678
ZOTERO_LIBRARY_TYPE=user
```

The tool resolves each variable from the environment first, then from `Notes/.env` in the current working directory. Environment values win on conflict. Credentials are read by the tool script and never echoed to the agent transcript.

**Optional override:** `pdf --out-dir DIR` changes the Web-API download directory (default `/tmp`). There is no local-storage-path override — local PDFs are resolved from the standard `~/Zotero/storage/` location.

## Better BibTeX (BibTeX export, citation, bibliography)

The `bibtex`, `cite`, and `bibliography` commands resolve citekeys and entries from **Better BibTeX (BBT)** by default (over BBT's local-only JSON-RPC endpoint, so the BBT-keyed path needs local Zotero plus the Better BibTeX plugin), falling back to Zotero's built-in translator/CSL renderer over the active pyzotero access mode when BBT is unreachable. `health` reports `better_bibtex_available`. The full key model, BBT method table, fallback semantics, and command flags live in [`bibtex-citations.md`](bibtex-citations.md); the rows below record only how these commands map onto the local-vs-web access modes.

## Write path (adding papers)

The `add`, `attach`, and `selected` commands write to the library. The read-only local `/api` serves no write path, so a **local** write goes through the Zotero desktop **connector** (the same port, a different path: `http://localhost:23119/connector/…`), and a **cloud** write goes through the Web API with a write-scoped key. `add` selects the path automatically.

**Local connector (default).** Requires only Zotero desktop running with "allow other applications to communicate" enabled — no Docker, no key, no translation-server. The tool posts to `/connector/saveItems` with a small direct-HTTP helper (pyzotero cannot reach the connector — it is Web-API-only). Connector requests carry a non-`Mozilla/` `User-Agent` and a `zotero-allowed-request: 1` header (or the connector rejects the save), `X-Zotero-Connector-API-Version: 3`, and a fresh UUID `sessionID` per save; a `409 SESSION_EXISTS` is retried with a new session, and `200`/`201` are success.

`saveItems` **takes no target parameter** — the item lands in whatever library/collection is currently **selected in the Zotero desktop UI**. Read that selection with `selected` (`/connector/getSelectedCollection`) and report it before saving; steer a session to a listed `targets[].id` with `add --target ID` (`/connector/updateSession`). Because the destination follows the UI, tell the user to switch the selection first if they want a different one.

**Cloud Web API (fallback).** Used when the connector is unreachable, or when the destination is one the connector cannot target — a group library (`--library group:<id>`) or a specific collection (`--collection KEY`) routes `add` to the Web API automatically. It uses pyzotero `create_items` (and `attachment_simple` for `attach`) against any accessible library, and needs a **write-scoped** `ZOTERO_API_KEY`.

**Path selection.** `--mode local` forces the connector, `--mode web` forces the Web API. On the default `--mode auto`: a group library or `--collection` → Web API; otherwise the connector when reachable, else the Web API.

**Dedup and item mapping.** `add` checks the target library for the record's DOI before saving (the connector never dedups and would create duplicates); pass `--allow-duplicate` to skip. The item is built by a Crossref→Zotero mapper covering journalArticle / preprint / working-paper report, verbatim from the record and its `--raw` Crossref payload. Zotero's `report` type has no DOI field, so a report's DOI is preserved in `extra`. A Crossref-sourced (JATS-tagged) abstract is dropped rather than stored; S2/arXiv abstracts are kept.

## Capability Boundaries

| Capability | Local API | Web API |
|---|---|---|
| Metadata search (`items(q=..., qmode="titleCreatorYear")`) | yes | yes |
| Full-text search (`items(q=..., qmode="everything")`) | yes (indexed content) | yes (indexed content only) |
| Item lookup | yes | yes |
| Child-item lookup | yes | yes |
| Collection listing | yes | yes |
| Tag listing | yes | yes |
| DOI-to-key index | yes | yes |
| Attachment full-text retrieval (`fulltext_item(attachment_key)`) | yes | yes (indexed content only) |
| PDF file retrieval (local path) | yes (local storage) | download to `/tmp/` |
| List libraries (`libraries` → user + groups) | yes | yes |
| Group-library access (`--library <id>`) | yes | yes (key must have group access) |
| BibTeX export, BBT citekeys (`bibtex`) | yes (needs Better BibTeX) | no (built-in fallback only) |
| BibTeX export, built-in translator (`bibtex` fallback) | yes | yes |
| Cite into a draft + `.bib` sync (`cite`) | yes (BBT keys; built-in fallback) | yes (built-in fallback only) |
| Formatted references, BBT (`bibliography`) | yes (needs Better BibTeX) | no (built-in fallback only) |
| Formatted references, built-in CSL (`bibliography` fallback) | yes | yes |
| Add/attach papers (`add`, `attach`, `selected`) | via the desktop **connector**, not the read-only `/api` (no key) | yes (write-scoped API key) |

Two distinct full-text operations are easy to conflate:

- **Full-text *search*** finds items across the library by content. It is `items(q="term", qmode="everything")`, which expands matching beyond title/metadata to indexed full-text. It is served by **both** the local API and the Web API and returns only content Zotero has already indexed. `search --fulltext` honors the active access mode (local-first under `--mode auto`), so it works on a local-only machine with no Web API credentials. Note that full-text hits are often **attachment** items (the indexed content lives on the attachment) — see Step 2 parent-item hydration in `paper-reading.md`. (Verified live on 2026-06-04 against a local library: `qmode=everything` returned far more hits than `qmode=titleCreatorYear` for body-only terms, confirming the local API serves full-text search. This corrects task 02's earlier conservative default, which was set only because the local API was disabled on that machine.)
- **Attachment full-text *retrieval*** returns the indexed text of one known attachment. It is `fulltext_item(attachment_key)` and is available in both modes. It reflects what Zotero has already indexed; if a PDF has not been indexed, the field will be absent or empty.

## PDF Retrieval Logic

The `pdf` command in `zotero_tool.py` (uses pyzotero, not raw HTTP calls):

1. Checks `~/Zotero/storage/ATTACHMENT_KEY/` for a `.pdf` file.
2. If found, emits `{"source": "local-storage", "path": ...}` immediately (local, no network).
3. If not found, builds a Web API client, recovers the original filename from item metadata (`zot.item`), downloads the file bytes (`zot.file`) to the download directory (`/tmp` by default, or `--out-dir`), and emits `{"source": "web-download", "path": ...}`.
4. Fails with a non-zero exit code if neither path yields a valid PDF (minimum 1 KB).

Web API download requires `ZOTERO_API_KEY` and `ZOTERO_LIBRARY_ID`.

## Troubleshooting

**Local API not available:** Confirm Zotero Desktop is running and the local API option is enabled under Settings → Advanced. A running Zotero with the option *off* still answers the connector port but returns `403 Local API is not enabled` on the `/api` path, which the tool treats as unavailable. The `health` command reports `local_api_available` and the detected mode.

**API key errors:** Verify the key at zotero.org/settings/keys. Ensure the key has at least read access to the target library.

**PDF download fails or is too small:** The item may not have a stored PDF in the Zotero web library, or the attachment may be a linked file that exists only locally.

**Full-text empty:** The attachment may not have been indexed yet. In Zotero Desktop, right-click the item and choose "Retrieve Metadata for PDF" or allow background indexing to complete.

**`add` saves to the wrong library/collection:** The connector saves to the desktop UI's current selection. Run `selected` to see the target, switch the selection in Zotero, or pass `--target ID` / route to the Web API with `--library group:<id>` or `--collection KEY`.

**Connector unreachable:** Confirm Zotero desktop is running with "allow other applications to communicate" enabled. `add --mode auto` falls back to the Web API when the connector does not answer; `--mode local` fails instead.
