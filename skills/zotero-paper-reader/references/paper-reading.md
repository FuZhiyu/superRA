# Paper-Reading Workflow

Complete step-by-step reference for reading and analyzing academic papers from a Zotero library. Covers command invocations, JSON fields, disambiguation, parent-item hydration, and troubleshooting.

Commands below are shown in full form: `uv run --script <skill-dir>/scripts/zotero_tool.py <subcommand>`, where `<skill-dir>` is the directory containing the skill's `SKILL.md` (substitute the real path before running). The SKILL.md quick-reference table abbreviates them to just the `<subcommand>` part.

---

## Step 1: Search the library

```bash
# Metadata search — title, creator, year (local or web API)
uv run --script <skill-dir>/scripts/zotero_tool.py search "author or title keywords"

# Full-text search — indexed PDF content (local or web)
uv run --script <skill-dir>/scripts/zotero_tool.py search "a phrase from the body text" --fulltext

# Search a specific group library (get ids from the `libraries` command)
uv run --script <skill-dir>/scripts/zotero_tool.py search "your topic" --library <group-id>
```

Searches default to the user's own library. To search a group library, first run `libraries` to list the user library and all groups with their ids, then pass `--library <group-id>` (or `--library group:<id>`) to `search` (and the other read commands). If the user names a project/group, resolve its id via `libraries` rather than guessing.

**Output shape:**

```json
{
  "mode": "local",
  "count": 3,
  "items": [
    {
      "key": "ABC12345",
      "data": {
        "itemType": "journalArticle",
        "title": "A Representative Paper Title",
        "creators": [{"lastName": "Author", "firstName": "First", "creatorType": "author"}, ...],
        "date": "2020",
        "DOI": "10.1234/example.doi",
        "abstractNote": "..."
      }
    }
  ]
}
```

**Fields to inspect:** `data.itemType`, `data.title`, `data.creators`, `data.date`, `data.DOI`, `data.abstractNote`, `key`.

---

## Step 2: Identify top-level items and handle attachment hits

Metadata search (`search "query"` without `--fulltext`) returns top-level items (`data.itemType` is `"journalArticle"`, `"book"`, `"conferencePaper"`, etc.). Use the `key` field directly as the item key.

Full-text search (`--fulltext`) can return **attachment items** (`data.itemType == "attachment"`). Attachment items have a `data.parentItem` field pointing to the top-level parent. When a hit is an attachment, retrieve the parent item:

```bash
# When data.itemType == "attachment", read data.parentItem:
uv run --script <skill-dir>/scripts/zotero_tool.py item PARENT_KEY
```

```json
{
  "mode": "web",
  "item": {
    "key": "XYZ98765",
    "data": {
      "itemType": "journalArticle",
      "title": "...",
      ...
    }
  }
}
```

After hydration, use `XYZ98765` (the parent key) as ITEM_KEY for all subsequent steps.

**Example — full-text hit requiring hydration:**

```json
{
  "mode": "web",
  "count": 2,
  "items": [
    {
      "key": "ATT11111",
      "data": {
        "itemType": "attachment",
        "title": "Du_2023.pdf",
        "parentItem": "PAR22222",
        "contentType": "application/pdf"
      }
    }
  ]
}
```

Action: call `item PAR22222` to get the paper metadata, then proceed with ITEM_KEY = `PAR22222`.

---

## Step 3: Disambiguate when multiple papers match

When the search returns multiple distinct top-level items, present a concise list to the user and ask them to choose — but only when the intended paper cannot be inferred from context (e.g., the user named a specific title or author that uniquely matches one result).

**Format for disambiguation:**

```
Found 3 papers matching "<query>":
1. Author A et al. (YYYY) — "First Matching Title" (Journal) [key: ABC12345]
2. Author B & Author C (YYYY) — "Second Matching Title" (Journal) [key: DEF67890]
3. Author D et al. (YYYY) — "Third Matching Title" (Journal) [key: GHI11223]

Which paper did you mean? (reply with number or key)
```

Once the user selects (or if only one match exists), note the ITEM_KEY and continue.

---

## Step 4: Get the PDF attachment key

```bash
uv run --script <skill-dir>/scripts/zotero_tool.py children ITEM_KEY
```

**Output shape:**

```json
{
  "mode": "local",
  "count": 2,
  "children": [
    {
      "key": "PDF44444",
      "data": {
        "itemType": "attachment",
        "contentType": "application/pdf",
        "title": "Du_et_al_2023.pdf",
        "filename": "Du_et_al_2023.pdf"
      }
    },
    {
      "key": "NOTE5555",
      "data": {
        "itemType": "note"
      }
    }
  ]
}
```

Find the child where `data.contentType == "application/pdf"`. Note its `key` as ATTACHMENT_KEY. If multiple PDF children exist, prefer the one whose `data.title` or `data.filename` does not contain "supplement" or "appendix" (use your judgment or ask the user).

---

## Step 5: Get the PDF file path

```bash
uv run --script <skill-dir>/scripts/zotero_tool.py pdf ATTACHMENT_KEY
```

**Output shape — local storage hit:**

```json
{
  "source": "local-storage",
  "path": "/Users/username/Zotero/storage/PDF44444/Du_et_al_2023.pdf"
}
```

**Output shape — web download:**

```json
{
  "source": "web-download",
  "path": "/tmp/Du_et_al_2023.pdf"
}
```

Read `path` from the JSON output. This is the PDF path for the next step.

---

## Step 6: Convert to markdown

Invoke the `mistral-pdf-to-markdown` skill with the PDF path from Step 5. Do not implement PDF conversion yourself — delegate entirely to that skill.

Save the resulting markdown to:

```
Notes/PaperInMarkdown/Author_Year_ShortTitle.md
```

**Filename convention:** `Author_Year_ShortTitle.md` — replace spaces with underscores, remove special characters, truncate long titles to ~5 words.

Examples:
- `Smith_2021_Short_Descriptive_Title.md`
- `Jones_Lee_2019_Another_Paper_Title.md`
- `AuthorA_et_al_2020_Truncated_Long_Title.md`

The `mistral-pdf-to-markdown` skill is bundled in this repo (`skills/mistral-pdf-to-markdown`); invoke it by capability name. It needs a Mistral API key (`MISTRAL_API_KEY`) — see that skill's "API Key Setup".

The conversion skill places extracted images in an `images/` subfolder next to the markdown file. A project-local `Notes/PaperInMarkdown/` convention overrides this default if the project has one.

---

## Step 7: Read and analyze

Academic papers converted to markdown are often long. Read strategically — never load the whole file into context.

```python
# Start with abstract and introduction (first ~500 lines)
Read(file_path="Notes/PaperInMarkdown/FILENAME.md", offset=1, limit=500)
```

After the initial read, provide the user with:
- Paper metadata (authors, year, venue, DOI)
- Abstract summary (2-4 sentences)
- Main contribution and findings
- Section outline (list headers you observed)
- Offer to read specific sections

For subsequent sections, use `offset` and `limit` to read only the relevant part, or use Bash `grep -n "Section Title" file` to find the line number first.

```bash
# Find a section by heading keyword
grep -n "Empirical" Notes/PaperInMarkdown/FILENAME.md
```

```python
# Then read from that line
Read(file_path="Notes/PaperInMarkdown/FILENAME.md", offset=LINE_NUMBER, limit=300)
```

---

## Troubleshooting

### Zotero Desktop not running or local API disabled

**Symptom:** `health` reports `local_api_available: false`; commands return connection errors or fall through to Web API.

**Check:** Run `zotero_tool.py health` and read `active_mode`.

```bash
uv run --script <skill-dir>/scripts/zotero_tool.py health
```

If `local_api_available` is `false` and `web_api_configured` is `false`, no access mode is available. Ask the user to either (a) start Zotero Desktop and enable the local API under Settings → Advanced → "Allow other applications on this computer to communicate with Zotero", or (b) configure Web API credentials.

Note: Zotero may be running but the local API off — the connector port answers but the `/api` path returns `403 Local API is not enabled`. The `health` command distinguishes this from Zotero not running at all. See [`access-modes.md`](access-modes.md) for the enable path and the full local-vs-web fallback rules.

### No PDF child attachment

**Symptom:** `children` output has no child with `data.contentType == "application/pdf"`.

**Action:** Inform the user. The paper may be in Zotero as a metadata-only record without a stored PDF. Options: the user can attach a PDF in Zotero Desktop, or if the DOI is present you can search the web for an open-access copy.

### Missing local file (PDF not in local storage)

**Symptom:** `pdf ATTACHMENT_KEY` returns `{"source": "web-download", ...}` or fails with "PDF not in local storage and Web API not configured".

**If web download fails with credentials missing:** Ask the user to set `ZOTERO_LIBRARY_ID` and `ZOTERO_API_KEY` (see [`access-modes.md`](access-modes.md)). The `pdf --out-dir DIR` flag sets the download destination (default `/tmp`).

**If the attachment is a linked file:** Zotero stores a reference to a file outside its storage folder. The `pdf` command cannot retrieve linked files via the Web API. Ask the user to locate the file manually or change Zotero to use stored (not linked) attachments.

### Missing Web API credentials

**Symptom:** No access mode is available — the local API is disabled/unreachable and no Web API credentials are set — and a command fails with "Web API mode needs ZOTERO_LIBRARY_ID and ZOTERO_API_KEY".

**Action:** Inform the user. They need to set environment variables `ZOTERO_LIBRARY_ID` and `ZOTERO_API_KEY` (and optionally `ZOTERO_LIBRARY_TYPE`). These can go in the shell profile/`secrets.sh` or in `Notes/.env`. See [`access-modes.md`](access-modes.md) for where to find these values.

### Full-text search returns attachment hits (parent-item hydration)

**Symptom:** `search "query" --fulltext` returns items where `data.itemType == "attachment"` instead of journal articles or books.

**Action:** For each attachment hit, read `data.parentItem` and call `item PARENT_KEY` to retrieve the parent item metadata. Use the parent's `key` as ITEM_KEY for all subsequent steps. This is expected behavior — full-text search indexes attachment content, and the match is reported on the attachment rather than the parent. See Step 2 above for the exact pattern.
