# BibTeX, Cite, and Bibliography

Full reference for the three citation commands in `scripts/zotero_tool.py`: `bibtex` (export entries + sync a master `.bib`), `cite` (insert a citation into a draft + sync its entry), and `bibliography` (render formatted references). Load this when you need command examples, the full flag list, the Better BibTeX key model, fallback semantics, group-library targeting, or troubleshooting.

## Contents

- [Key model: BBT default, built-in fallback](#key-model-bbt-default-built-in-fallback)
- [Selection flags (shared)](#selection-flags-shared)
- [`bibtex` — export and master-`.bib` sync](#bibtex--export-and-master-bib-sync)
- [`cite` — insert into a draft](#cite--insert-into-a-draft)
- [`bibliography` — formatted references](#bibliography--formatted-references)
- [Library targeting](#library-targeting)
- [Master-`.bib` sync semantics](#master-bib-sync-semantics)
- [JSON output fields](#json-output-fields)
- [Troubleshooting](#troubleshooting)

All commands run via `uv run --script <skill-dir>/scripts/zotero_tool.py <subcommand> ...`, where `<skill-dir>` is the directory containing `SKILL.md` — substitute the real path. All emit JSON; add `--help` to any subcommand for parameter details.

## Key model: BBT default, built-in fallback

The three commands resolve citekeys and entries from **Better BibTeX (BBT)** by default, so exported entries reuse the researcher's BBT citekeys and stay consistent with a BBT-maintained master `.bib`. BBT is a local-only Zotero plugin — it is **not** part of the Zotero Web API or pyzotero — so the BBT-keyed path requires local Zotero plus the Better BibTeX plugin installed and running. `health` reports `better_bibtex_available` so you can tell which path a command will take.

**Default — BBT keys.** The tool talks to BBT's JSON-RPC endpoint at `http://127.0.0.1:23119/better-bibtex/json-rpc`:

| BBT method | Purpose |
|---|---|
| `item.citationkey([itemKeys])` | Zotero item key → BBT citekey (`{itemKey: citekey}`; unknown keys map to `null`) |
| `item.export([citekeys], "better bibtex", libraryID)` | BibTeX text (with BBT citekeys) for the given **citekeys** |
| `item.bibliography([citekeys], {id, contentType})` | formatted reference entries (`id` is a CSL style, e.g. `apa`; `contentType: "text"` returns one plain-text entry per item, newline-joined) |

`item.export` and `item.bibliography` take **citekeys, not Zotero item keys**, so the tool first resolves item keys → citekeys via `item.citationkey`, then calls them. `libraryID` is BBT's library numbering: the user library is `1`; a group library uses its own numeric group id.

**Fallback — built-in translator / renderer.** When BBT is unreachable (Zotero closed, BBT not installed, or Web-API mode), the tool falls back over the active pyzotero access mode:

- `bibtex` / `cite` emit entries via Zotero's built-in BibTeX translator — `item(key, format="bibtex")`, which returns the raw BibTeX body in both local and Web mode.
- `bibliography` renders via the built-in CSL formatter — `item(key, include="bib", style=...)`, which returns the formatted reference under the `bib` key.

The built-in translator generates **different** citekeys from BBT. So on the `bibtex` / `cite` fallback path the command prints a key-mismatch warning and sets `bbt_fallback: true` in its JSON — the emitted keys may not match a BBT-exported `.bib`. The `bibliography` fallback also prints the same warning and sets `bbt_fallback: true` (the warning text is citekey-oriented; for `bibliography` it just signals the built-in renderer was used).

## Selection flags (shared)

All three commands select items the same way; at least one selection flag is required, or the command errors cleanly (rc 1, no stack trace):

| Flag | Meaning |
|---|---|
| `--item-key KEY` | a Zotero item key; repeatable to select several items |
| `--query "text"` | metadata search (reuses the `search` path) |
| `--doi DOI` | DOI lookup (reuses the `doiindex` resolution); repeatable |

`bibtex` and `bibliography` operate on every selected item. `cite` inserts the first selected item as the citation but still syncs every resolved entry into the `.bib`.

## `bibtex` — export and master-`.bib` sync

Emit BibTeX entries for selected items. With `--bib PATH`, sync them into a master `.bib`; without `--bib`, return the BibTeX in the JSON `bibtex` field.

```bash
# Print BibTeX for one item to stdout (JSON bibtex field)
zotero_tool.py bibtex --item-key ABCD1234

# Export several items and sync into a master .bib
zotero_tool.py bibtex --item-key ABCD1234 --item-key EFGH5678 --bib refs.bib

# Select by metadata search or DOI, sync into a master .bib
zotero_tool.py bibtex --query "term structure of interest rates" --bib refs.bib
zotero_tool.py bibtex --doi 10.1111/jofi.12345 --bib refs.bib
```

JSON reports `keys`, `bib_path`, `added` / `skipped`, and the `bbt_used` / `bbt_fallback` flags.

## `cite` — insert into a draft

Insert a citation into a draft and sync the cited entry into a master `.bib`. `--bib PATH` is **required** (a citation with no entry in the bibliography is useless). Give **exactly one** draft target:

| Flag | Inserts |
|---|---|
| `--tex FILE` | `\cite{KEY}` |
| `--markdown FILE` | `[@KEY]` |

With `--marker STR`, the first occurrence of the marker in the draft is replaced in place; a missing marker errors (rc 1) rather than appending. Without `--marker`, the citation is appended on its own line at the end of the draft.

```bash
# Append \cite{KEY} to a LaTeX draft and sync the entry
zotero_tool.py cite --item-key ABCD1234 --tex paper.tex --bib refs.bib

# Replace a placeholder marker in place in a Markdown draft
zotero_tool.py cite --query "Fama French 1993" --markdown draft.md --bib refs.bib --marker "[CITE-FF]"
```

JSON reports `edited_file`, `citation_key`, `citation`, `bib_path`, `added` / `skipped`, and the `bbt_used` / `bbt_fallback` flags. When the selection resolves to several items, the first is the inserted citation and every resolved entry is still synced.

## `bibliography` — formatted references

Render one formatted reference entry per selected item. Default CSL style is `apa`; override with `--style ID` (any CSL style id BBT or Zotero knows). `--text` prints the entries as plain lines instead of JSON.

```bash
# Render APA references for two items as JSON
zotero_tool.py bibliography --item-key ABCD1234 --item-key EFGH5678

# Render in a different style, as plain text
zotero_tool.py bibliography --query "monetary policy" --style chicago-author-date --text
```

JSON carries an `entries` list (one rendered string per item) plus `style`, `count`, and the `bbt_used` / `bbt_fallback` flags.

## Library targeting

By default the commands act on the user's own library ("My Library"). To act on a group library, run `libraries` first to get the group ids, then pass `--library <group-id>` (or `--library group:<id>`). The tool passes the correct BBT `libraryID` (user library is BBT `libraryID` 1; group libraries use their own numeric group id). `--library` works on `bibtex`, `cite`, and `bibliography` consistently with the read commands.

```bash
zotero_tool.py bibtex --query "your query" --library <group-id> --bib refs.bib
```

## Master-`.bib` sync semantics

`--bib` appends resolved entries **deduped by citekey** with a minimal touch:

- An entry whose citekey already appears in the file is **skipped** — never re-added.
- Existing entries are **never reordered or rewritten**; new entries are appended at the end.
- Re-running the same export into the same `.bib` is idempotent: the first run reports `added 1 / skipped 0`, a second run `added 0 / skipped 1`, and the file holds exactly one entry.

`cite` reuses this same dedup-append helper, so a citation and its bibliography entry stay in one source of truth. Because the `.bib` you point at may hold arbitrary externally-sourced entries, the entry parser balances braces (an `@type{key,` token only opens an entry at top level, depth 0), so a BibTeX-like token inside a field value — e.g. an abstract quoting `@inproceedings{notakey, ...}` — does not spawn a phantom entry. One known limitation: an unbalanced brace inside a double-quoted field value (`field = "...{..."`) in an externally-sourced `.bib` can throw the depth counter; BBT and the built-in translator both emit balanced, brace-delimited fields, so tool-generated input never triggers it.

## JSON output fields

| Field | Commands | Meaning |
|---|---|---|
| `keys` / `citation_key` | `bibtex` / `cite` | emitted citekey(s) |
| `bibtex` | `bibtex` (no `--bib`) | the BibTeX text |
| `entries` | `bibliography` | rendered reference strings |
| `bib_path` | `bibtex` / `cite` | the master `.bib` path written |
| `added` / `skipped` | `bibtex` / `cite` | citekeys newly appended vs. already present |
| `edited_file` / `citation` | `cite` | the draft written and the inserted citation string |
| `style` / `count` | `bibliography` | CSL style and number of rendered entries |
| `bbt_used` | all | `true` when BBT resolved the entry/keys |
| `bbt_fallback` | all | `true` when the built-in path was used; prints the BBT-unreachable warning on stderr (citekey mismatch matters for `bibtex`/`cite`) |

Credentials are never printed to the agent transcript (the no-secret-leak invariant from the read commands carries over).

## Troubleshooting

**BBT not installed / Zotero closed (`bbt_used: false`, `bbt_fallback: true`).** The command still works via the built-in translator, but on `bibtex`/`cite` the emitted citekeys may differ from your BBT-exported `.bib` (hence the printed warning). To get BBT keys, install the Better BibTeX plugin and keep Zotero Desktop running. Check `health` → `better_bibtex_available`.

**Web-API mode.** BBT is local-only, so any command run against the Web API uses the built-in fallback path. Same key-mismatch caveat applies.

**`item.export` / `item.bibliography` returns "not found".** BBT's export and bibliography methods take **citekeys**, not Zotero item keys. The tool resolves item key → citekey first; if `item.citationkey` returns `null` for a key, that item is not in the library (or BBT has not assigned it a key yet).

**Missing-marker error.** `cite --marker STR` errors (rc 1) when the marker is absent rather than silently appending, so a typo cannot insert a citation in the wrong place. Fix the marker text or drop `--marker` to append.

**`bibtex` / `cite` report no selection.** Pass at least one of `--item-key`, `--query`, or `--doi`.
