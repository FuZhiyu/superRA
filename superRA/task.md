---
title: "Replace Zotero MCP with Zotero Skills"
status: approved
depends_on: []
tags:
  - skill-creation
  - zotero
  - pyzotero
created: 2026-06-04
---

## Objective

Create a local-first Zotero skill in this repo that preserves the current Zotero paper-reading workflow while removing the MCP dependency. The skill should use `pyzotero` through `uv`-managed commands, prefer Zotero Desktop local API access when available, and keep the Zotero Web API as a fallback for machines without local Zotero.

A later increment (tasks 07–10) extends the skill from reading-only into BibTeX/citation support: a `bibtex` export with master-`.bib` sync, a `cite` draft-insertion command, and `bibliography` rendering. These reuse the researcher's existing **Better BibTeX (BBT)** citekeys by default so exported entries stay consistent with a BBT-maintained master `.bib`, falling back to Zotero's built-in BibTeX translator (with a key-mismatch warning) only when BBT is unreachable.

### Context

Planning walk completed on 2026-06-04. Repo guidance requires skill edits to follow `skill-creator`, to keep instructions minimal and behavior-shaping, and to update inventories when adding a skill. `AGENTS.md` is an alias for `CLAUDE.md`. `README.md` describes superRA as a PLAN -> IMPLEMENT -> INTEGRATE workflow with workflow, domain, utility, and meta skills. `skills/CATEGORIES.md` is the contributor-facing skill grouping index, while `skills/using-superRA/SKILL.md` is the runtime-facing skill inventory. The existing personal `zotero-paper-reader` skill uses Zotero MCP for search and child-item lookup, then a helper script to find or download PDFs, then the Mistral PDF-to-Markdown skill.

### Constraints

Use `pyzotero`, not a Zotero MCP server. Pyzotero 1.13.0 is the planning baseline checked on 2026-06-04 from PyPI/GitHub/Read the Docs; implementation must pin or otherwise log the exact version used so behavior drift is visible. Local Zotero API access is read-only, so mutating operations must either stay out of scope or route through the Web API with explicit user confirmation and credential handling. The skill must tell users how to enable local API access in Zotero Desktop: Zotero -> Settings -> Advanced -> allow other applications on this computer to communicate with Zotero.

This repo is **public**: never commit personal library data (real group names/ids, item keys, titles, counts, or query results). Record any live-test evidence generically with placeholders or hypothetical examples. Better BibTeX endpoints used by tasks 07–09 are local-only (not in the Web API or pyzotero); the BBT-keyed path therefore requires local Zotero + the Better BibTeX plugin, with the built-in translator as the web/no-BBT fallback.

### Planned Files

- `skills/zotero-paper-reader/SKILL.md`
- `skills/zotero-paper-reader/references/*.md`
- `skills/zotero-paper-reader/scripts/*`
- `skills/zotero-paper-reader/pyproject.toml`
- `skills/zotero-paper-reader/uv.lock`
- `skills/CATEGORIES.md`
- `README.md`
- `skills/using-superRA/SKILL.md`
- tests or script-level verification artifacts under the repo's existing test structure if a durable test harness is practical

## Workflow Status

- Base branch: `main` (GitHub default; researcher decision 2026-06-04). Branch forked from `main` HEAD `3e0de358`; `main` has not advanced, so Sync is a no-op (clean fast-forward).
- **First increment** — the MCP-free `zotero-paper-reader` skill (tasks 01–05) was integrated via PR [#31](https://github.com/FuZhiyu/superRA/pull/31) to `main`. PR #31 (carrying the first and second increments) **merged into `main` on 2026-06-05**; `main` is now at `5dfe928b`.
- **Second increment (post-PR)** — after PR #31, the branch gained: the vendored `mistral-pdf-to-markdown` skill (task 06), multi-library support and the local-API full-text-search fix in `zotero_tool.py`, harness-neutral `<skill-dir>` paths, and expanded tests. Captured as task 06 plus refreshed Results in tasks 02–05; all of tasks 02–06 re-reviewed and re-approved in this second integration pass.
- Protect: drift/regression suite is `tests/test-zotero-tool.sh` (24), `tests/test-zotero-skill-text.sh` (16), and `tests/test-mistral-skill-text.sh` (9) — full suite passes.
- Integrate: integration review APPROVED over `3e0de358..HEAD`; one MAJOR (vendored converter must run via `uv run --script`, not `uv run python`/bare `python`, or PEP 723 deps are ignored) and one MINOR (stale verification prose) found and fixed. Minimum-net-diff sweep clean: every hunk is net-new and ties to an approved objective. Consolidation gate: clean-enough (6 coherent tasks, no structural debt) — no pass needed.
- Document: Results are reader-facing and reviewer-confirmed across all six tasks; no separate maturation pass needed.
- Finish: second increment pushed to update the existing open PR [#31](https://github.com/FuZhiyu/superRA/pull/31) to `main` (fast-forward, no re-create). Freshness re-checked before push: `origin/main` unchanged at `3e0de358`.
- **Third increment (post-merge, #32)** — after #31 merged, branch `analysis/fix-mistralai-v2` was forked from `main` HEAD `5dfe928b` to repair the vendored converter's broken `mistralai` dependency (task 06, 2026-06-07). `mistralai` 2.0 dropped the top-level `Mistral` export, so the unpinned `from mistralai import Mistral` broke on every fresh `uv run --script`; fixed by migrating to the v2 client import and pinning the PEP 723 dep to `mistralai>=2,<3`. Protect: `tests/test-mistral-skill-text.sh` passes 11/11 (the result guard — no numerical results to drift-test). Integrate: integration review APPROVED over `5dfe928b..#32-HEAD`; minimum-net-diff sweep clean (4 files, every hunk ties to the v2-fix objective); project-doc audit clean; consolidation gate clean-enough. Document: task 06 Results reader-facing and reviewer-confirmed. Finish: merged into `main` via PR [#32](https://github.com/FuZhiyu/superRA/pull/32); `010a5c1e` then quoted the `zotero-paper-reader` SKILL.md frontmatter for valid YAML. Both land on `main` at `010a5c1e` and are folded into this branch by the fourth-increment Sync below.
- **Fourth increment (implemented + verified, 2026-06-08)** — BibTeX/citation support (tasks 07–10): `bibtex` export + master-`.bib` sync (07), `cite` insertion + `bibliography` rendering (08), docs + packaging (09), verification (10). Key model: Better BibTeX keys by default via BBT's local JSON-RPC/export endpoints, built-in translator as fallback with a key-mismatch warning. All four tasks `approved` through the implementer-reviewer loop; full credential-free suite passes (`test-zotero-tool.sh` 42, `test-zotero-skill-text.sh` 32, `test-mistral-skill-text.sh` 9 — see Sync Map for post-merge counts) plus a generic live smoke test.
  - **Protect (2026-06-08):** confirmed — the regression suite is the protection mechanism; researcher confirmed coverage complete; no new drift tests to author (all tasks approved).
  - **Sync (2026-06-08):** `BASE_REF=origin/main`. `origin/main` advanced past the stale notes above to `010a5c1e` (PR #31 and #32 are merged, not open). Anchors: `PRE_SYNC_BASE_SHA=5dfe928b`, `BASE_HEAD_SHA=010a5c1e`. Incoming `5dfe928b..010a5c1e` = 2 commits (#32 mistralai dependency fix; `010a5c1e` quoted the `zotero-paper-reader` SKILL.md frontmatter description for valid YAML). Both were resolved by a semantic merge whose two conflicts — SKILL.md `description` and root Workflow Status — were synthesized to preserve both intents (the `description` is now a single-quoted YAML scalar carrying our citation triggers); sync review APPROVED. The branch was later **rebased onto `origin/main`@`010a5c1e`** for the PR, so this reconciliation now lives directly in the citation-increment commits rather than a merge commit — tasks 01–06 and the base `zotero_tool.py` are already in `main`, so the rebased diff adds only the citation increment.
  - **Integrate (2026-06-08):** post-sync integration review APPROVED over `010a5c1e..HEAD` — minimum net diff clean (every hunk ties to an approved task 07–10 objective or sync context), convention fit and progressive-disclosure norms upheld, project-doc audit consistent (skill stays non-Manifest-loaded), full suite green (42/32/11). **Consolidation gate: clean-enough** — 10 coherent tasks, the citation increment is a clean new branch with no structural debt, no misplaced tasks; no pass needed. Temporary Sync Map removed at close; task 09 retains a lasting single-quoted-YAML Sync impact note.
  - **Document (2026-06-08):** tasks 07–10 `## Results` were already reader-facing and reviewer-confirmed; no per-task maturation pass needed. Added a selective citation-increment rollup to the root `## Results` Key Findings. Docs finalized.
  - **Finish (2026-06-08):** freshness re-checked — `origin/main` unchanged at `010a5c1e`, no re-sync. Final suite green (42/32/11). Branch pushed; opened **new** PR [#33](https://github.com/FuZhiyu/superRA/pull/33) to `main` (PR #31 was already merged, so a new PR rather than an update). No worktree cleanup: the increment ran serially in the persistent `zotero-skill-improvement` worktree; no orchestrator-seeded ephemeral worktrees were created.
  - **Rebase for PR (2026-06-08):** branch linearized onto `origin/main`@`010a5c1e` (which already contains tasks 01–06 + the base skill) and the citation increment recommitted as a small set of logical commits, replacing the prior merge-based history that had carried the already-merged base commits into PR #33. Force-pushed; tree unchanged (suite still 42/32/11). Pre-rebase history preserved locally on `backup/zotero-merge-history`.

## Results

### Key Findings

The MCP-free `zotero-paper-reader` skill is complete and verified, and now self-contained in-repo. Tasks 01–06 built the reading/library-query skill; tasks 07–10 added BibTeX/citation support that reuses the researcher's Better BibTeX keys.

- **Contract** ([01-skill-contract](01-skill-contract/task.md)) — `SKILL.md` + `references/access-modes.md` define a local-first / Web-API-fallback contract with a capability matrix; full-text *search* (`items(q=..., qmode="everything")`) is kept distinct from attachment full-text *retrieval* (`fulltext_item`).
- **Tooling** ([02-pyzotero-tooling](02-pyzotero-tooling/task.md)) — `scripts/zotero_tool.py` (PEP 723, `pyzotero==1.13.0` pinned + sidecar lock) exposes 9 JSON subcommands, local-first with Web fallback, local-storage-first PDF retrieval, and no secret leakage. Local full-text search (`qmode="everything"`) was later verified live (task 05, after the local API was enabled) to work in local mode; an early bug that forced `--fulltext` to the Web API was fixed so it honors the active access mode.
- **Workflow** ([03-paper-reading-workflow](03-paper-reading-workflow/task.md)) — `references/paper-reading.md` migrates the search → locate PDF → convert via `mistral-pdf-to-markdown` → save `Notes/PaperInMarkdown/Author_Year_ShortTitle.md` → section-by-section read workflow onto the new tooling, with no MCP.
- **Inventory** ([04-inventory-and-packaging](04-inventory-and-packaging/task.md)) — registered in `README.md`, `skills/CATEGORIES.md`, and `skills/using-superRA/SKILL.md` as a standalone Utility skill (not loaded by the Skill-Load Manifest); workflow choreography and generated agent files untouched.
- **Verification** ([05-verification](05-verification/task.md)) — credential-free deterministic suites cover behavior, the no-secret-leak invariant, `.env` parsing, and MCP/stale-instruction regression guards; plus a live local-mode smoke test (after the researcher enabled the Zotero local API) that confirmed health/search/children/pdf and the corrected local full-text-search boundary.
- **Vendored conversion skill** ([06-vendor-mistral-skill](06-vendor-mistral-skill/task.md)) — `mistral-pdf-to-markdown` was migrated into `skills/mistral-pdf-to-markdown/` as the canonical in-repo home for the PDF→Markdown step behind `zotero-paper-reader`, removing the external-plugin dependency that previously left conversion as a dead end. Registered as a standalone Utility skill (not loaded by the Manifest) and locked with a text-regression test.

**BibTeX/citation increment (tasks 07–10).** The skill now exports and cites using the researcher's existing Better BibTeX (BBT) citekeys, so output stays consistent with a BBT-maintained master `.bib`:

- **BibTeX export + master-`.bib` sync** ([07-bibtex-export](07-bibtex-export/task.md)) — a `bibtex` command resolves item key → BBT citekey → entry over BBT's local JSON-RPC, with Zotero's built-in translator as a warned fallback (`bbt_fallback: true`) when BBT is unreachable. `--bib` dedup-appends into a master `.bib`, minimal-touch (existing entries never reordered/rewritten) via a brace-balanced entry parser. `resolve_keys` / `sync_bib` are the shared key/`.bib` source of truth reused downstream; `health` reports `better_bibtex_available`.
- **Citation insertion + bibliography** ([08-cite-and-bibliography](08-cite-and-bibliography/task.md)) — `cite` inserts `\cite{key}` (`--tex`) / `[@key]` (`--markdown`) at a `--marker` (or appends) and syncs the entry; it validates the draft/marker *before* touching the `.bib`, so a typo cannot pollute the master file. `bibliography` renders formatted references (default APA) via BBT with a CSL fallback.
- **Docs + packaging** ([09-docs-and-packaging](09-docs-and-packaging/task.md)) — progressive disclosure: `SKILL.md` stays a lean routing surface, depth lives in `references/bibtex-citations.md`; CATEGORIES/README/using-superRA inventories updated; skill remains a standalone Utility (not Manifest-loaded).
- **Verification** ([10-bibtex-verification](10-bibtex-verification/task.md)) — credential-free suites grew to `test-zotero-tool.sh` 42 and `test-zotero-skill-text.sh` 32, plus a generic live smoke test confirming the BBT key match, idempotent sync, draft insertion, the `.bib`-protection ordering, and the warned built-in fallback.

