# Zotero Access Modes

## Local API (default)

Pyzotero connects to Zotero Desktop over localhost when the local API is enabled. No credentials are required. This mode supports metadata search, item lookup, children, collections, tags, attachment full-text retrieval, and local file retrieval. Library-wide full-text *search* is routed to the Web API; whether the local API serves it is unverified — see Capability Boundaries below.

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
| `ZOTERO_API_KEY` | API key from zotero.org/settings/keys. Read-only scope is sufficient for all commands in this skill. |

Set via environment (recommended — e.g., in `secrets.sh` or shell profile) or place in `Notes/.env` (gitignored, Dropbox-synced):

```
ZOTERO_API_KEY=your-key-here
ZOTERO_LIBRARY_ID=12345678
ZOTERO_LIBRARY_TYPE=user
```

The tool resolves each variable from the environment first, then from `Notes/.env` in the current working directory. Environment values win on conflict. Credentials are read by the tool script and never echoed to the agent transcript.

**Optional override:** `pdf --out-dir DIR` changes the Web-API download directory (default `/tmp`). There is no local-storage-path override — local PDFs are resolved from the standard `~/Zotero/storage/` location.

## Capability Boundaries

| Capability | Local API | Web API |
|---|---|---|
| Metadata search (`items(q=..., qmode="titleCreatorYear")`) | yes | yes |
| Full-text search (`items(q=..., qmode="everything")`) | no (unverified — see below) | yes (indexed content only) |
| Item lookup | yes | yes |
| Child-item lookup | yes | yes |
| Collection listing | yes | yes |
| Tag listing | yes | yes |
| DOI-to-key index | yes | yes |
| Attachment full-text retrieval (`fulltext_item(attachment_key)`) | yes | yes (indexed content only) |
| PDF file retrieval (local path) | yes (local storage) | download to `/tmp/` |
| Write operations | not supported | yes (with write-access API key) |

Two distinct full-text operations are easy to conflate:

- **Full-text *search*** finds items across the library by content. It is `items(q="term", qmode="everything")`, which expands matching beyond title/metadata to indexed full-text. On the Web API this returns only content Zotero has already indexed. The Zotero Desktop local API is **not relied on** for full-text search — whether its `qmode=everything` path is exposed the way the Web API's is could not be verified. The tool therefore routes `search --fulltext` to the Web API unconditionally and reports a clear error when Web API credentials are absent. (Resolution recorded in task 02: the local API on the verification machine was reachable on the connector port but the `/api` path returned `403 Local API is not enabled`, so a live local full-text probe was not possible; the boundary is set conservatively to Web-API-only, matching pyzotero's documented local-mode capability surface. Task 05 should confirm this live if a local instance with the API enabled is available.)
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
