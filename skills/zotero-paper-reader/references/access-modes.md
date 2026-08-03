# Zotero Access Modes

## Local API (default)

Pyzotero connects to Zotero Desktop over localhost when the local API is enabled. No credentials. Supports every read operation: metadata search, full-text search, item lookup, children, collections, tags, attachment full-text retrieval, and local file retrieval.

**How to enable:** In Zotero Desktop → Settings → Advanced → enable "Allow other applications on this computer to communicate with Zotero."

Construct with `local=True`. Pyzotero 1.13.0 still requires both `library_id` and `library_type` in local mode; the local API serves the desktop's default user library at id `0`:

```python
from pyzotero import zotero
zot = zotero.Zotero(library_id=0, library_type="user", local=True)
```

The tool probes `http://localhost:23119/api/users/0/items` and uses local mode on a successful response. The Zotero connector port can answer (`Zotero is running`) while the local API itself is disabled — the `/api` path then returns `403 Local API is not enabled`, which the probe treats as unavailable. When local is unavailable, the tool falls back to the Web API if credentials are configured.

## Web API (fallback)

Used when local Zotero is unavailable, when accessing a non-public group library, or for any future write operation.

**Required environment variables:**

| Variable | Description |
|---|---|
| `ZOTERO_LIBRARY_ID` | Integer user or group ID. Personal: find at zotero.org/settings/keys. Group: integer after `/groups/` in the group URL. |
| `ZOTERO_LIBRARY_TYPE` | `user` (default) or `group`. |
| `ZOTERO_API_KEY` | API key from zotero.org/settings/keys. Read-only scope is sufficient for all commands in this skill. |

Set in the environment (recommended — `secrets.sh` or shell profile) or in `Notes/.env` (gitignored, Dropbox-synced):

```
ZOTERO_API_KEY=your-key-here
ZOTERO_LIBRARY_ID=12345678
ZOTERO_LIBRARY_TYPE=user
```

The tool resolves each variable from the environment first, then from `Notes/.env` in the current working directory; environment values win on conflict. Credentials are never echoed to the agent transcript.

**Optional override:** `pdf --out-dir DIR` changes the Web-API download directory (default `/tmp`). There is no local-storage-path override — local PDFs resolve from the standard `~/Zotero/storage/` location.

## Better BibTeX (BibTeX export, citation, bibliography)

`bibtex`, `cite`, and `bibliography` resolve citekeys and entries from **Better BibTeX (BBT)** by default over BBT's local-only JSON-RPC endpoint, so the BBT-keyed path needs local Zotero plus the Better BibTeX plugin; when BBT is unreachable they fall back to Zotero's built-in translator/CSL renderer over the active pyzotero access mode. `health` reports `better_bibtex_available`. Key model, BBT method table, fallback semantics, and command flags: [`bibtex-citations.md`](bibtex-citations.md). The rows below record only the local-vs-web mapping.

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
| Write operations | not supported | yes (with write-access API key) |

Two distinct full-text operations, easy to conflate:

- **Full-text *search*** finds items across the library by content: `items(q="term", qmode="everything")`, which expands matching beyond title/metadata to indexed full-text. Served by **both** the local API and the Web API, over already-indexed content only. `search --fulltext` honors the active access mode (local-first under `--mode auto`), so it works on a local-only machine with no Web API credentials. Hits are often **attachment** items, since the indexed content lives on the attachment — see Step 2 parent-item hydration in `paper-reading.md`.
- **Attachment full-text *retrieval*** returns the indexed text of one known attachment: `fulltext_item(attachment_key)`, available in both modes. An unindexed PDF yields an absent or empty field.

## PDF Retrieval Logic

The `pdf` command resolves in order:

1. Checks `~/Zotero/storage/ATTACHMENT_KEY/` for a `.pdf` file.
2. If found, emits `{"source": "local-storage", "path": ...}` immediately.
3. If not found, builds a Web API client, recovers the original filename from item metadata (`zot.item`), downloads the file bytes (`zot.file`) to the download directory (`/tmp` by default, or `--out-dir`), and emits `{"source": "web-download", "path": ...}`.
4. Fails with a non-zero exit code if neither path yields a valid PDF (minimum 1 KB).

Web API download requires `ZOTERO_API_KEY` and `ZOTERO_LIBRARY_ID`.

## Troubleshooting

**Local API not available:** Confirm Zotero Desktop is running and the local API option is enabled under Settings → Advanced. `health` reports `local_api_available` and the detected mode.

**API key errors:** Verify the key at zotero.org/settings/keys; it needs at least read access to the target library.

**PDF download fails or is too small:** The item may have no stored PDF in the Zotero web library, or the attachment may be a linked file that exists only locally.

**Full-text empty:** The attachment may not be indexed yet. In Zotero Desktop, right-click the item and choose "Retrieve Metadata for PDF", or let background indexing finish.
