# Zotero Access Modes

## Local API (default)

Pyzotero can connect to Zotero Desktop over localhost when the local API is enabled. No credentials are required. This mode supports metadata search, item lookup, children, collections, tags, attachment full-text retrieval, and local file retrieval. Library-wide full-text *search* may not be served by the local API — see Capability Boundaries below.

**How to enable:** In Zotero Desktop → Settings → Advanced → enable "Allow other applications on this computer to communicate with Zotero."

Construct with `local=True`:

```python
from pyzotero import zotero
zot = zotero.Zotero(library_id=None, library_type="user", local=True)
```

The tool script detects local API availability at startup (via `health` check against `http://localhost:23119/`) and uses it automatically when Zotero Desktop is running. If the local API is unavailable, the tool falls back to the Web API if credentials are configured.

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

Credentials are read by the tool script and never echoed to the agent transcript.

## Capability Boundaries

| Capability | Local API | Web API |
|---|---|---|
| Metadata search (`items(q=..., qmode="titleCreatorYear")`) | yes | yes |
| Full-text search (`items(q=..., qmode="everything")`) | verify in task 02 | yes (indexed content only) |
| Item lookup | yes | yes |
| Child-item lookup | yes | yes |
| Collection listing | yes | yes |
| Tag listing | yes | yes |
| DOI-to-key index | yes | yes |
| Attachment full-text retrieval (`fulltext_item(attachment_key)`) | yes | yes (indexed content only) |
| PDF file retrieval (local path) | yes (local storage) | download to `/tmp/` |
| Write operations | not supported | yes (with write-access API key) |

Two distinct full-text operations are easy to conflate:

- **Full-text *search*** finds items across the library by content. It is `items(q="term", qmode="everything")`, which expands matching beyond title/metadata to indexed full-text. On the Web API this returns only content Zotero has already indexed. Whether pyzotero's local mode (a thin proxy to Zotero Desktop's local HTTP server) serves the `qmode=everything` path is uncertain — historically the local server has not exposed full-text search the way the Web API does. Task 02 must verify this against a running local instance; until verified, treat full-text *search* as Web-API-only and have `search --fulltext` fall back to the Web API when local cannot serve it.
- **Attachment full-text *retrieval*** returns the indexed text of one known attachment. It is `fulltext_item(attachment_key)` and is available in both modes. It reflects what Zotero has already indexed; if a PDF has not been indexed, the field will be absent or empty.

## PDF Retrieval Logic

The `pdf` command in `zotero_tool.py`:

1. Checks `~/Zotero/storage/ATTACHMENT_KEY/` for a `.pdf` file.
2. If found, returns that path immediately (local, no network).
3. If not found, queries the item's metadata via the Web API to recover the original filename, then downloads the file to `/tmp/ORIGINAL_FILENAME` and returns that path.
4. Fails with a non-zero exit code if neither path yields a valid PDF (minimum 1 KB).

Web API download requires `ZOTERO_API_KEY` and `ZOTERO_LIBRARY_ID`.

## Troubleshooting

**Local API not available:** Confirm Zotero Desktop is running and the local API option is enabled under Settings → Advanced. The `health` command reports the detected mode.

**API key errors:** Verify the key at zotero.org/settings/keys. Ensure the key has at least read access to the target library.

**PDF download fails or is too small:** The item may not have a stored PDF in the Zotero web library, or the attachment may be a linked file that exists only locally.

**Full-text empty:** The attachment may not have been indexed yet. In Zotero Desktop, right-click the item and choose "Retrieve Metadata for PDF" or allow background indexing to complete.
