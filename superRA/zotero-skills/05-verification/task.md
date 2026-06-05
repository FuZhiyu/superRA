---
title: "Verify Zotero Skill Behavior"
status: approved
depends_on:
  - 04-inventory-and-packaging
tags: [tests, verification, skill-creation]
input:
  - skills/zotero-paper-reader/SKILL.md
  - skills/zotero-paper-reader/scripts/zotero_tool.py
output:
  - superRA/05-verification/task.md
created: 2026-06-04
---

## Objective

Verify the skill at the script and agent-instruction levels. The verification must prove that local-disabled and missing-credential paths fail with actionable guidance, that commands emit parseable JSON without leaking secrets, that the pyzotero version is logged, and that the paper-reading instructions no longer mention MCP. If a live local Zotero instance with the local API enabled is available, also run a smoke test for health, search, child lookup, and PDF-path retrieval, and confirm the deferred local full-text-search boundary (`items(q=..., qmode="everything")` against the local API) — update `references/access-modes.md` if the live result differs from the current conservative "unverified / Web-API-only" default.

### Constraints

Use deterministic script-level tests where possible so verification does not require a private Zotero library. Any live-library smoke result must record only non-sensitive metadata and must not commit API keys, PDF contents, or private library data.

## Planner Guidance

Consider adding tests that mock pyzotero responses and filesystem storage. Also run text checks over `skills/zotero-paper-reader` to block `mcp__zotero` regressions and stale setup instructions. Record verification commands and outcomes in this task's `## Results`.

## Results

### Test Suites

Two deterministic test suites now cover the skill. Both run from the repo root without credentials, a live library, or network access.

**[tests/test-zotero-tool.sh](../../tests/test-zotero-tool.sh)** (task 02, extended here) — 24 checks: subcommand presence (incl. `libraries`), health/version JSON, no-access error paths, deterministic `--library` validation (an invalid spec is rejected before any access attempt), the no-secret-leak invariant, and `Notes/.env` credential parsing. The `.env` checks confirm that with environment variables unset, `load_env_file` picks up `ZOTERO_LIBRARY_ID` and `ZOTERO_API_KEY` from a project-local `Notes/.env` (fake non-secret values) and that a `.env`-sourced key never leaks to stdout/stderr. All 24 pass.

**[tests/test-zotero-skill-text.sh](../../tests/test-zotero-skill-text.sh)** (new, this task) — 16 checks in three groups:

- MCP regression guards (4 checks): `mcp__zotero`, `mcp_zotero`, `call_mcp`, `use_mcp_tool` must be absent from the entire skill tree.
- Stale/hardcoded-path guards (7 checks): `.claude/skills/mistral`, the `.claude/skills/` prefix, the Claude-only `CLAUDE_SKILL_DIR` env var, `get_zotero_pdf.py`, `uv run --project`, `zotero-mcp-server`, and `zotero_mcp` must all be absent.
- Positive invariants (5 checks): `SKILL.md` and `paper-reading.md` use the harness-neutral `<skill-dir>` placeholder for the `zotero_tool.py` invocation; `access-modes.md` documents the `403` edge case; the script pins `pyzotero==1.13.0`; `SKILL.md` mentions `pyzotero`.

All 16 pass.

### Verification Commands and Outcomes

```
$ bash tests/test-zotero-tool.sh
Passed: 24    Failed: 0

$ bash tests/test-zotero-skill-text.sh
Passed: 16    Failed: 0
```

### Live Smoke Test (local API enabled, 2026-06-04)

The researcher enabled the Zotero Desktop local API; a full live smoke test was then run against the real library with no Web API credentials (local mode throughout). All commands succeeded. Results are reported generically below — no private library contents (titles, item keys, group names/ids, counts, file paths) are recorded here.

| Command | Outcome |
|---|---|
| `health` | `local_api_available: true`, `active_mode: "local"`, `pyzotero_version: 1.13.0`, exit 0 |
| `collections` / `tags` | returned the library's collections and tags as JSON (mode local) |
| `search "<term>" --limit 3` | returned matching items (mode local); fields `data.itemType/title/creators/date/DOI` present |
| `children <ITEM_KEY>` | listed children; a PDF attachment was identified by `data.contentType == "application/pdf"` |
| `pdf <ATTACHMENT_KEY>` | `{"source": "local-storage", "path": ...}` — resolved straight from local storage, no network |
| `libraries` | listed "My Library" plus the user's group libraries, each with `library_id` / `library_type` / `name` |
| `search "<term>" --library <GROUP_ID>` | returned hits from a group library (group `items(qmode=...)`); `--library group:<id>` alias verified; invalid `--library` value rejected with a clean error |

### Deferred Boundary Resolved (corrected): local full-text search WORKS

The task-01/02 deferred question — whether the *local* API serves `qmode="everything"` full-text search — is now resolved **live, and the earlier conservative "no" was wrong** (it was set only because the local API was *disabled* during task 02). Direct probes of the local API returned substantially more hits for `qmode=everything` than `qmode=titleCreatorYear` on body-only terms (terms that appear in PDF text but not in titles/metadata), confirming the local API performs full-text content matching.

This exposed a behavioral bug: `cmd_search` previously routed `--fulltext` to the Web API *unconditionally*, so on a local-only machine (local API enabled, no Web credentials — exactly this setup) `search --fulltext` failed with "requires Web API access" even though the local API serves it. **Fix:** `cmd_search` now uses `qmode="everything"` against the active access mode (local-first under `--mode auto`), identical mode-resolution to plain search. Verified live: `search "<term>" --fulltext` now runs in local mode (exit 0) and returns full-text matches (far more than the metadata-only `search`). Full-text hits are frequently attachment items, handled by the existing parent-item hydration step in `paper-reading.md`. The contract (`references/access-modes.md` capability matrix), `SKILL.md`, and `paper-reading.md` were updated to mark local full-text search as supported.

### Mocked Tests

Mocked-pyzotero tests were considered for two categories of logic: `load_env_file` / `get_config` (pure Python, no pyzotero) and `make_client` error-message paths. Both are now covered without mocking:

- The `make_client` web-credential-absent path is exercised by `test-zotero-tool.sh` (clean `error:` line, `Web API` named, no-secret-leak — checks 15, 17, 18).
- The `load_env_file` `Notes/.env` parsing branch is now exercised by the three `.env` checks added to `test-zotero-tool.sh` (a temp `Notes/.env` with environment variables unset, asserting both keys are read and that a `.env`-sourced key does not leak). Mocking is unnecessary — a real temp `.env` is deterministic and credential-free.

One residual gap is accepted: `get_config`'s env-wins-over-file precedence is not asserted, because `health`'s observable surface is only booleans (`config_present`), so both an env value and a `.env` value present as `true` and the source cannot be distinguished from the JSON output. The logic is a one-line `os.environ.get(name) or file_values.get(name)`; the security-critical property (no leak from either source) is covered. No `pyzotero`-response mocks were added — they would duplicate the already-passing deterministic error-path coverage without new signal.
