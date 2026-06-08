---
title: "Add Citation Insertion and Bibliography Rendering"
status: approved
depends_on:
  - 07-bibtex-export
tags: [python, uv, bibtex, better-bibtex]
script: skills/zotero-paper-reader/scripts/zotero_tool.py
input:
  - skills/zotero-paper-reader/scripts/zotero_tool.py
output:
  - skills/zotero-paper-reader/scripts/zotero_tool.py
---

## Objective

Add two further subcommands to `skills/zotero-paper-reader/scripts/zotero_tool.py`, building on the BBT key-resolution and bib-sync helpers from task 07: `cite` (insert a citation into a draft and sync its entry into the master `.bib`) and `bibliography` (render formatted reference entries). Both reuse the **same BBT-default / built-in-fallback key model defined in task 07's Objective** — including the fallback key-mismatch warning and the `--library` targeting — rather than re-deriving keys independently.

### `cite` — insert into a draft

- Select the item by `--item-key`, `--query`, or `--doi` (same selection logic as `bibtex` in task 07).
- Ensure the item's entry is synced into the master `.bib` via `--bib PATH` (reuse task 07's dedup-append helper).
- Insert a citation into a target draft: `\cite{KEY}` when `--tex FILE` is given, `[@KEY]` when `--markdown FILE` is given (exactly one target required). If `--marker STR` is supplied, replace the first occurrence of the marker; otherwise append the citation. Error cleanly if the marker is not found.
- Output JSON: edited file, inserted citation key, `.bib` path, added/skipped, and the `bbt_used` / `bbt_fallback` flags.

### `bibliography` — render formatted references

- Select one or more items (`--item-key` repeatable, `--query`, or `--doi`).
- Render formatted reference entries (default style APA) via BBT's `item.bibliography`, falling back to pyzotero's built-in formatted-citation output (`include=citation&style=...`) when BBT is unreachable, with the same fallback warning.
- Emit JSON (and a readable text mode) with one rendered entry per item.

### Shared-helper hardening (carried from task 07 review)

`cite` reuses the `sync_bib` / `bib_entry_keys` / `split_bib_entries` helpers from task 07. Task 07's review found `_BIB_ENTRY_RE` matches a `@type{key,` sequence embedded inside a field value (e.g. an abstract containing `@inproceedings{notakey, ...}`), producing a phantom entry and a bogus `added` key, and splitting the real entry mid-field. It is latent (BBT-escaped exports don't trigger it) but these helpers are the declared single source of truth for `.bib` writes, and `cite` will write into a user-maintained master `.bib` that may hold arbitrary externally-sourced entries. Harden entry detection so only true entry starts count (anchor `@type{key,` to a line start / after the closing `}` of the previous entry, or track brace depth rather than a bare regex), and add a deterministic regression test on synthetic input containing an `@type{...}`-like token inside a field value.

### Validation

- `cite` into a temporary `.tex` inserts `\cite{<bbtkey>}` and the entry appears exactly once in the temporary `.bib`; marker replacement substitutes in place; a missing marker errors rather than appending.
- `cite --markdown` inserts `[@<bbtkey>]`.
- `bibliography` returns a non-empty rendered entry for a known item.
- Record live checks generically per the root-task public-repo constraint (no real titles, keys, or ids).

## Planner Guidance

- Keep `cite`'s draft-insertion logic (marker-replace vs append) small and local to this command; only the key resolution and `.bib` sync are shared with task 07.
- Confirm BBT `item.bibliography` parameters and the pyzotero built-in formatted-citation call against the pinned sources before relying on either.

## Results

Added the `cite` and `bibliography` subcommands to [`zotero_tool.py`](../../skills/zotero-paper-reader/scripts/zotero_tool.py), both reusing task 07's `resolve_keys` / `sync_bib` / `bbt_citekeys` layer for the BBT-default / built-in-fallback key model (no second key derivation, no second `.bib` write path), and hardened the shared `.bib` entry-detection helpers per the carried task-07 review finding. Both commands were verified end-to-end against the live local Zotero + Better BibTeX on this machine. The credential-free tool suite grew from 31 to 42 checks; all suites pass (`tests/test-zotero-tool.sh` 42/42, `tests/test-zotero-skill-text.sh` 16/16).

### `cite` — insert into a draft, sync the entry

[`cmd_cite`](../../skills/zotero-paper-reader/scripts/zotero_tool.py) selects via the same `select_item_keys` path as `bibtex` (`--item-key` / `--query` / `--doi`), resolves entries through `resolve_keys`, dedup-appends them into a required `--bib` via `sync_bib`, then inserts the citation into exactly one draft target. `--tex FILE` inserts `\cite{KEY}`; `--markdown FILE` inserts `[@KEY]`. The small draft-insertion logic is local to this command in [`insert_citation`](../../skills/zotero-paper-reader/scripts/zotero_tool.py): with `--marker STR` the first occurrence is replaced in place; a missing marker raises rather than appending; without a marker the citation is appended on its own line. When the selection resolves to several items the first is cited and every resolved entry is still synced. JSON output carries `edited_file`, `citation_key`, `citation`, `bib_path`, `added`/`skipped`, and the `bbt_used`/`bbt_fallback` flags.

### `bibliography` — formatted references

[`cmd_bibliography`](../../skills/zotero-paper-reader/scripts/zotero_tool.py) renders one formatted reference per item (default CSL style `apa`, overridable with `--style ID`). BBT path uses `item.bibliography([citekeys], {id: style, contentType: "text"})` (probed live to confirm the signature — it requires a `{id, contentType}` options object and returns newline-joined plain-text entries); the fallback uses pyzotero's `item(key, include="bib", style=...)`, which returns the rendered reference under the `bib` key in both local and Web mode. JSON carries an `entries` list (one per item) plus `style`/`count`/`bbt_used`/`bbt_fallback`; `--text` prints the entries as plain lines.

### Shared-helper hardening (carried from task 07)

[`split_bib_entries`](../../skills/zotero-paper-reader/scripts/zotero_tool.py) now scans with brace-depth balancing instead of a bare regex: an `@type{key,` token is an entry opener only at top level (depth 0), so a BibTeX-like token embedded inside a field value — e.g. an `abstract` quoting `@inproceedings{notakey, ...}` — stays part of its enclosing entry rather than spawning a phantom entry and splitting the real one mid-field. `bib_entry_keys` is now derived from `split_bib_entries`, so the single source of truth for `.bib` writes (`sync_bib`, reused by `cite`) no longer invents a bogus `added` key or corrupts the real entry. Verified on the exact synthetic reproduction from the task-07 finding plus a nested-brace title case, both as a unit test and through `sync_bib`.

### Live validation (against the running library; recorded generically)

- **`bibliography` (BBT)** — a real library item rendered one non-empty APA entry with `bbt_used: true`; `--text` printed one line per entry.
- **`cite` into `.tex`** — appending inserted `\cite{<bbtkey>}`, the entry appeared exactly once in the `.bib` (`added 1 / skipped 0`), and a second `cite` of the same item left the file at one entry (`added 0 / skipped 1`) — idempotent through the reused `sync_bib`.
- **`cite --marker`** — the marker was replaced in place (marker gone, one `\cite{}` present); a missing marker exited rc 1 with a clean `error:` line and left the draft byte-for-byte unchanged (no append).
- **`cite --markdown`** — inserted `[@<bbtkey>]`.
- **Target guards** — neither and both of `--tex`/`--markdown` each exit rc 1 with an "exactly one" error; no selection flags exits rc 1 naming `--item-key`.
- **Fallback (BBT forced unreachable)** — over the real selection path (which filters out attachment/note items), both `resolve_keys` and `resolve_bibliography` fall back to the built-in translator/renderer, returning a non-empty entry with `bbt_used: false`.

### Tests added (credential-free, deterministic)

In [`tests/test-zotero-tool.sh`](../../tests/test-zotero-tool.sh): `cite`/`bibliography` listed in `--help`; the `cite` selection guard and the exactly-one-target guard (neither/both); the `bibliography` selection guard; and a module-import unit test covering `insert_citation` (append / marker replace-in-place / missing-marker error leaves the draft unchanged) and the hardened `split_bib_entries`/`bib_entry_keys`/`sync_bib` on the phantom-token and nested-brace inputs.

### Docs

- [`SKILL.md`](../../skills/zotero-paper-reader/SKILL.md) — two command-table rows, a `## Cite and Bibliography` section (shared selection/key model, draft-target and marker semantics, JSON fields, default APA style), and `cite`/`bibliography` added to the `--library` targeting list.
- [`references/access-modes.md`](../../skills/zotero-paper-reader/references/access-modes.md) — the `item.bibliography` method row, the citekey-not-itemkey note extended to it, the built-in CSL fallback (`include="bib"`), and three capability-matrix rows.

Task 09 (docs-and-packaging) owns the deeper citation-workflow narrative; the docs here are the minimal accurate surface to make the two commands discoverable and correct.

## Review Notes

Verdict: APPROVE. Two MINOR, non-blocking observations adjudicated by the orchestrator (deferred, not REVISE items):

> 1. [MINOR] `split_bib_entries` brace-depth counter can be thrown by an unbalanced brace inside a double-quoted field value (`field = "...{..."`) in an externally-sourced `.bib`. ([zotero_tool.py:408](../../skills/zotero-paper-reader/scripts/zotero_tool.py))
>    → orchestrator: accepted as a known limitation. Same latency class as the fixed task-07 finding — BBT and the built-in translator both emit balanced, brace-delimited fields, so tool-generated input never triggers it. A full bibtex/quoted-string parser is out of scope for a sync helper.
> 2. [MINOR] `cmd_cite` runs `sync_bib` before `insert_citation`, so a missing draft/marker errors after the master `.bib` is already synced (draft untouched; `sync_bib` idempotent, so retry is harmless). ([zotero_tool.py:792](../../skills/zotero-paper-reader/scripts/zotero_tool.py))
>    → orchestrator: accepted for a least-surprise fix at the Step 3 verification cleanup — validate the draft target / marker before mutating the `.bib`, so a typo'd `--marker` cannot pollute the user's master `.bib`. To be re-reviewed when fixed.
>    → RESOLVED in task 10 (commit `89da6b09`, re-reviewed `16ca53a9`): `cmd_cite` now calls a read-only `check_draft_target` before `sync_bib`, so a missing draft/marker errors with the master `.bib` untouched. Covered by a unit test and the live smoke test.
