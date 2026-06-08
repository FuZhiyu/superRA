---
title: "Verify BibTeX/Citation Behavior"
status: approved
depends_on:
  - 07-bibtex-export
  - 08-cite-and-bibliography
  - 09-docs-and-packaging
tags: [tests, verification, skill-creation]
input:
  - skills/zotero-paper-reader/scripts/zotero_tool.py
  - skills/zotero-paper-reader/SKILL.md
output:
  - tests/test-zotero-tool.sh
  - tests/test-zotero-skill-text.sh
  - skills/zotero-paper-reader/scripts/zotero_tool.py
created: 2026-06-08
---

## Objective

Extend the existing credential-free regression suites to cover the new BibTeX/citation commands, and run a documented live smoke test against the real library. Match the structure of the existing harnesses (`tests/test-zotero-tool.sh`, `tests/test-zotero-skill-text.sh`).

### Deterministic Tests (no credentials, no running Zotero required)

Extend `tests/test-zotero-tool.sh` (or add a sibling `tests/test-zotero-bibtex.sh` run from it):

- `--help` lists `bibtex`, `cite`, and `bibliography`.
- `bibtex` / `cite` with no selection flag (`--item-key` / `--query` / `--doi`) error cleanly with an `error:` line, not a stack trace.
- **Master-bib dedup:** sync a synthesized entry into a temp `.bib` twice → the key appears once (drive this through the bib-sync helper with a stub entry so it needs no live Zotero).
- `cite` marker replacement substitutes in place; a missing marker errors.
- The no-secret-leak invariant still holds for the new commands.

Extend `tests/test-zotero-skill-text.sh`: `SKILL.md` and `references/bibtex-citations.md` mention the new commands, the BBT-default/built-in-fallback key model, and the master-`.bib` sync; no stale or contradictory claims.

### Live Smoke Test (documented in Results, generic)

With local Zotero + Better BibTeX running: export a known item and confirm its key matches the BBT citekey; sync into a temp `.bib` (idempotent on re-run); `cite` into a temp `.tex` and a temp `.md`; render a `bibliography`; and confirm the built-in fallback path warns (`bbt_fallback: true`) when BBT is disabled.

### Constraint

This repo is **public**. Record all live-test results generically — placeholders or hypothetical examples only, never real group names/ids, counts, item keys, titles, or query results. The committed tests must pass without credentials and without a running Zotero.

### Validation

Full suite (existing + new checks) passes from the repo root; live smoke documented in `## Results` with no personal library data.

## Planner Guidance

Reuse the existing suites' helper patterns and exit-code branching on whether a local API is actually running, so the new checks stay deterministic in both states.

## Results

The deterministic regression coverage for the BibTeX/citation commands is complete and the full documented live smoke test passes against the running local Zotero + Better BibTeX. Both committed suites pass credential-free and Zotero-independent: [`tests/test-zotero-tool.sh`](../../tests/test-zotero-tool.sh) **42/42** and [`tests/test-zotero-skill-text.sh`](../../tests/test-zotero-skill-text.sh) **32/32** (the text suite grew from 16 to 32).

### Gap analysis — what tasks 07/08 already covered vs. what was missing

Tasks 07/08 had already taken the tool suite to 42 checks, so the deterministic *behavior* coverage the Objective lists was largely in place: `--help` lists `bibtex`/`cite`/`bibliography` ([test-zotero-tool.sh:69-71](../../tests/test-zotero-tool.sh#L69-L71)); `bibtex`/`cite`/`bibliography` selection guards and the `cite` exactly-one-target guard; the `sync_bib` dedup/idempotence/minimal-touch unit test ([test-zotero-tool.sh:168-200](../../tests/test-zotero-tool.sh#L168-L200)); `insert_citation` append / marker-replace / missing-marker ([test-zotero-tool.sh:267-288](../../tests/test-zotero-tool.sh#L267-L288)); the hardened brace-balanced `split_bib_entries`; and the no-secret-leak invariant. I filled the **gaps** rather than duplicating:

1. **Text-regression surface (the main gap).** `test-zotero-skill-text.sh` had no assertion that the new commands or the key model were documented. Added 16 checks ([test-zotero-skill-text.sh:82-149](../../tests/test-zotero-skill-text.sh#L82-L149)): `SKILL.md` surfaces `bibtex`/`cite`/`bibliography`, names the Better BibTeX key model, and routes to `references/bibtex-citations.md`; the reference documents all three commands, the BBT-default / built-in-fallback model, the `bbt_fallback` flag, and the master-`.bib` dedup-by-citekey sync; plus stale/contradictory-claim guards (no surface claims BBT works over the Web API or that pyzotero exposes BBT) and a Manifest-loading-claim guard (the skill is a standalone Utility).
2. **`.bib`-protection invariant for the `cite` ordering fix.** Extended the existing module-import unit test ([test-zotero-tool.sh:288-307](../../tests/test-zotero-tool.sh#L288-L307)) to cover the new `check_draft_target` helper: a missing draft and a missing marker both raise without writing, and a valid target is a no-op — the invariant that lets `cmd_cite` reject a bad target before it mutates the master `.bib`.

### Least-surprise fix carried from task 08 (Step-3 verification cleanup)

Task 08's Review Note #2 was deferred by the orchestrator to "the Step 3 verification cleanup … validate the draft target / marker before mutating the `.bib` … To be re-reviewed when fixed." `cmd_cite` previously ran `sync_bib` *before* `insert_citation`, so a typo'd `--marker` synced the entry into the user's master `.bib` and *then* errored. Fixed by factoring a read-only [`check_draft_target`](../../skills/zotero-paper-reader/scripts/zotero_tool.py#L747) out of `insert_citation` and calling it in [`cmd_cite`](../../skills/zotero-paper-reader/scripts/zotero_tool.py#L791) **before** `sync_bib`. Now a missing draft/marker errors with the master `.bib` untouched. Covered deterministically (unit test above) and live (T6b below).

### Live smoke test (against the running library; recorded generically)

Run against local Zotero + Better BibTeX (`health` reported `local_api_available: true`, `better_bibtex_available: true`). A real journal-article item was selected by metadata search and driven through every documented step; only generic pass/fail flags are recorded here per the public-repo Constraint — no real keys, citekeys, titles, ids, or counts.

| Step | Check | Result |
|---|---|---|
| `bibtex` export | resolves via BBT (`bbt_used: true`, `bbt_fallback: false`), non-empty citekey | pass |
| key match | exported citekey equals the BBT `item.citationkey` for the same item key (probed directly over JSON-RPC) | pass |
| master-`.bib` sync | first run `added 1 / skipped 0`, second run `added 0 / skipped 1`, exactly one `@…{}` entry in the file (idempotent) | pass |
| `cite --tex` | appends `\cite{<bbtkey>}` to the `.tex` | pass |
| `cite --markdown` | appends `[@<bbtkey>]` to the `.md` | pass |
| `cite --marker` | marker replaced in place (marker gone, one `\cite{}` present) | pass |
| `cite --marker` missing | rc 1, clean `error:` line, draft byte-for-byte unchanged, **fresh `.bib` left unsynced** (ordering fix) | pass |
| `bibliography` | one non-empty APA entry rendered, `bbt_used: true` | pass |
| built-in fallback | with BBT forced unreachable (RPC pointed at a dead port), `bbt_available()` is false; `resolve_keys` and `resolve_bibliography` fall back to the built-in translator/renderer (`bbt_used: false`, the `bbt_fallback: true` warning path) and still return a non-empty entry | pass |

### Credential-free / no-Zotero confirmation

Both suites' assertions are credential-free and do not depend on a running Zotero: the access-dependent checks force `--mode web` with no credentials (deterministic no-access path), the unit tests import the module and call pure helpers (`sync_bib`, `insert_citation`, `check_draft_target`, `split_bib_entries`) with no library access, and the lone `health` rc check branches on `local_api_available` so it is deterministic in both states. The text suite only reads files. No real library data is committed.
