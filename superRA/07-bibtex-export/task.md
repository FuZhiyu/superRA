---
title: "Add Better BibTeX Export and Master-Bib Sync"
status: approved
depends_on:
  - 02-pyzotero-tooling
tags: [python, uv, bibtex, better-bibtex]
script: skills/zotero-paper-reader/scripts/zotero_tool.py
input:
  - skills/zotero-paper-reader/scripts/zotero_tool.py
  - skills/zotero-paper-reader/references/access-modes.md
output:
  - skills/zotero-paper-reader/scripts/zotero_tool.py
created: 2026-06-08
---

## Objective

Add a `bibtex` subcommand to `skills/zotero-paper-reader/scripts/zotero_tool.py` that emits BibTeX entries using the user's **Better BibTeX (BBT) citekeys** and syncs them into a user-maintained master `.bib` file without disturbing existing entries. This is the foundation for the citation features in sibling tasks 08–09; it must expose a reusable key-resolution layer and a reusable bib-sync helper those tasks call.

### Key Model (binding — governs tasks 07–09)

Resolve citekeys and entries from Better BibTeX by default; fall back to Zotero's built-in BibTeX translator only when BBT is unreachable.

- **Default — BBT keys.** Talk to Better BibTeX's local endpoints on `http://127.0.0.1:23119/better-bibtex/`. Confirmed live on this machine: the JSON-RPC endpoint `POST /better-bibtex/json-rpc` serves `item.citationkey([zoteroItemKeys])` (Zotero item key → BBT citekey), `item.export([keys], "better bibtex", libraryID)` (entries with BBT keys), and `item.search(query)` (items including their BBT key and `libraryID`). BBT is **local-only** — it is not part of the Zotero Web API or pyzotero.
- **Fallback — built-in translator.** When BBT is not reachable (Zotero closed, BBT not installed, or web-API mode), emit entries via Zotero's built-in BibTeX translator over the active pyzotero access mode (works in both local and web mode). The built-in translator generates *different* citekeys from BBT, so the command MUST print a clear warning (and set a `bbt_fallback: true` flag in its JSON output) stating the emitted keys may not match the user's BBT-exported `.bib`.

### Required Behavior

- **Selection:** accept `--item-key KEY` (repeatable), `--query "text"` (metadata search, reuse the existing search path), or `--doi DOI` (reuse the existing `doiindex` resolution). At least one is required; error cleanly otherwise.
- **`--bib PATH` master-bib sync:** append resolved entries into the master `.bib`. **Dedup by citekey** — skip any entry whose key already appears in the file; never reorder or rewrite existing entries (minimal touch). Report `added` vs `skipped` keys. When `--bib` is omitted, print the BibTeX to stdout.
- **Library targeting:** support `--library user|<group-id>|group:<id>` consistent with the existing read commands, passing the correct BBT `libraryID` (user library is BBT `libraryID` 1; group libraries use their own numeric id).
- **Output:** JSON reporting emitted keys, the `.bib` path, added/skipped counts, and `bbt_used` / `bbt_fallback` flags. Never print API keys or secrets (preserve the existing no-secret-leak invariant).
- **Health:** extend the `health` subcommand to report a `better_bibtex_available` boolean.

### Validation

- Live: exporting a known item produces an entry whose key equals the BBT citekey shown for that item in Zotero (verify against the running library; record results generically per the public-repo constraint on the root task).
- Idempotence: syncing the same item into a `--bib` twice adds the entry once.
- Fallback: with BBT unreachable, the command still emits an entry and prints the key-mismatch warning with `bbt_fallback: true`.

## Planner Guidance

- The BBT JSON-RPC surface above was probed live and confirmed responding; `item.export` requires a `translator` arg ("better bibtex") and a `libraryID`. Keep the BBT client a small `urllib` layer — BBT is not in pyzotero. Reuse the existing `make_client` / config / `--library` plumbing.
- For the built-in fallback, pyzotero exposes BibTeX via the items `format`/`content` parameter; confirm the exact pyzotero 1.13.0 call against the pinned source and the returned type before relying on it.
- Factor key resolution and bib-sync (the dedup-append) into helpers task 08's `cite` can reuse, so the two commands share one source of truth for keys and `.bib` writes.

## Results

Added a `bibtex` subcommand to [`zotero_tool.py`](../../skills/zotero-paper-reader/scripts/zotero_tool.py) plus a reusable Better BibTeX key layer and a reusable `.bib`-sync helper, then verified the command end-to-end against the live local Zotero + Better BibTeX on this machine. The existing tool suite grew from 24 to 31 checks; both zotero suites pass (`tests/test-zotero-tool.sh` 31/31, `tests/test-zotero-skill-text.sh` 16/16).

### BBT JSON-RPC contract (probed live, recorded generically)

The Better BibTeX JSON-RPC endpoint `POST http://127.0.0.1:23119/better-bibtex/json-rpc` was probed live and its exact shape pinned down (it differs from the planner's first read in two load-bearing ways):

- `item.citationkey([[itemKey, ...]])` returns `{itemKey: citekey}`; an unknown item key maps to `null`.
- `item.export([citekey, ...], "better bibtex", libraryID)` takes **citekeys, not Zotero item keys** — passing raw item keys (bare or `libraryID:itemKey`) returns `not found`. So the resolver does item key → citekey (`item.citationkey`) → export (`item.export`). `libraryID` is BBT numbering: user library `1`, group library = its group id.
- BBT item abstracts can contain raw control characters, so RPC responses are parsed with `json.loads(..., strict=False)` — strict parsing crashes on real library data.

### Built-in fallback (confirmed against pinned pyzotero 1.13.0)

`zot.item(key, format="bibtex")` returns the **raw BibTeX body** (the local API serves it as `text/plain`, so pyzotero's retrieve path returns `bytes` rather than a parsed `BibDatabase`; the tool decodes and concatenates). Confirmed live in both the BBT-present and BBT-unreachable paths. The fallback warns and sets `bbt_fallback: true` because the built-in translator's citekeys differ from BBT's.

### Reusable layer for tasks 08–09

- `resolve_keys(zot, item_keys, library) -> (bbt_used, citekeys, bibtex_text)` — single key/entry resolver (BBT-first, built-in fallback) that the `cite`/`bibliography` commands call.
- `sync_bib(path, text) -> (added, skipped)` — dedup-append by citekey, minimal touch (never reorders/rewrites existing entries), with `bib_entry_keys` / `split_bib_entries` parsing helpers. Citation features in sibling tasks reuse this for `.bib` writes so keys and entries have one source of truth.
- `bbt_available()` backs the new `health` field `better_bibtex_available`.

### Validation (live, against the running library; recorded generically)

- **Live key match** — exporting a real library item via `bibtex --item-key KEY` produced an entry whose citekey equals the BBT citationkey returned directly by `item.citationkey` for that item, with `bbt_used: true` / `bbt_fallback: false`. Selection via `--query` and `--doi` also resolves to entries.
- **Idempotence** — syncing the same item into a fresh `--bib` twice yields `added 1 / skipped 0` then `added 0 / skipped 1`; the file holds exactly one `@…{}` entry across both runs.
- **Fallback** — with the BBT endpoint forced unreachable, the command still emits an entry via the built-in translator, prints the key-mismatch warning, and sets `bbt_fallback: true`.
- **Clean errors (rc 1, no stack trace)** — no selection flags, invalid `--library`, and an unknown `--doi` each produce a single `error:` line.

### Tests added (credential-free, deterministic)

In [`tests/test-zotero-tool.sh`](../../tests/test-zotero-tool.sh): `bibtex` listed in `--help`; `health` reports `better_bibtex_available`; the selection guard and invalid-`--library` rejection; and a unit test of `sync_bib` that imports the module (no Zotero/BBT access) and asserts dedup-append, idempotence, minimal touch, and order preservation.

### Docs

- [`SKILL.md`](../../skills/zotero-paper-reader/SKILL.md) — command-table row, a `## BibTeX Export` section (selection flags, BBT-default / fallback behavior, dedup-append semantics, JSON fields), and `bibtex` added to the `--library` targeting list.
- [`references/access-modes.md`](../../skills/zotero-paper-reader/references/access-modes.md) — a Better BibTeX section (the JSON-RPC method table, libraryID numbering, citekey-not-itemkey gotcha, fallback path) and two capability-matrix rows.

Task 09 (docs-and-packaging) owns the deeper citation-workflow narrative; the docs here are the minimal accurate surface to make the command discoverable and correct.

## Review Notes

1. **MINOR (robustness, carry to tasks 08–09)** — `_BIB_ENTRY_RE` in [`zotero_tool.py:346`](../../skills/zotero-paper-reader/scripts/zotero_tool.py#L346) matches any `@word{token,` sequence, including one embedded *inside* a field value (e.g. an `abstract`/`note` containing `... @inproceedings{notakey, ...} ...`). On such input `bib_entry_keys`/`split_bib_entries` invent a phantom entry: `sync_bib` then records a bogus `added` citekey and splits the real entry mid-field (inserts a blank-line gap), and dedup can mis-skip on the phantom key. Verified reproducible on synthetic input. Not triggered on real BBT output — a 30-item live BBT export parsed with zero false positives because BBT escapes/wraps field content — so this is latent, not a live failure, hence non-blocking. Worth hardening (anchor entry starts to line-start / brace-balance the split) because these helpers are the declared single source of truth that tasks 08–09 reuse for `.bib` writes, where a regression here would propagate.
