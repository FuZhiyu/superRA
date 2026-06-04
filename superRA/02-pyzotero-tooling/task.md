---
title: "Build UV-Managed Pyzotero Tooling"
status: approved
depends_on:
  - 01-skill-contract
tags: [python, uv, pyzotero]
script: skills/zotero-paper-reader/scripts/zotero_tool.py
input:
  - skills/zotero-paper-reader/references/access-modes.md
  - skills/zotero-paper-reader/SKILL.md
output:
  - skills/zotero-paper-reader/scripts/zotero_tool.py
created: 2026-06-04
---

## Objective

Implement a skill-owned Python command surface that agents can run with `uv` to query Zotero without MCP. The tooling must support local-first reads through pyzotero, fall back to the Zotero Web API when configured, emit structured JSON for agent consumption, and report the pyzotero version in diagnostic output. It must never print API keys or secrets.

### Required Commands

The command surface must cover at least: health/check-access, search metadata, search full text, get item, get children, list collections, list tags, DOI index, get attachment full text, and get PDF path or download path. The PDF command must preserve the old local-storage-first behavior and use pyzotero/web API rather than raw MCP calls.

Build against the capability contract in `references/access-modes.md` (approved task 01): library full-text *search* is `items(q=..., qmode="everything")` and is distinct from attachment full-text *retrieval* (`fulltext_item(attachment_key)`) — they are separate subcommands. The contract leaves one boundary for this task to resolve: whether Zotero's *local* API actually serves `qmode="everything"` full-text search. Verify it against a running local instance if available; if local search is unavailable or unreliable, route `search --fulltext` to the Web API and document the boundary in `access-modes.md` (replacing its "verify in task 02" marker with the verified answer).

### Configuration Contract

Read configuration from environment variables and, when present, a project-local `Notes/.env` without exposing values to the agent transcript. Required or optional variables must be documented in the skill reference: `ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE`, `ZOTERO_API_KEY`, and any local-mode override or storage-path override introduced by the implementation.

## Planner Guidance

Prefer a single self-contained script with subcommands over multiple small scripts if that keeps invocation stable. Use PEP 723 inline script metadata so agents can run the bundled file from wherever the skill is installed, for example `uv run --script <skill-root>/scripts/zotero_tool.py ...`. Pin pyzotero in that script metadata and make the `version` or health command print the resolved package version so drift is visible.

## Results

The pyzotero command surface is implemented as a single self-contained PEP 723 script, [`skills/zotero-paper-reader/scripts/zotero_tool.py`](../../skills/zotero-paper-reader/scripts/zotero_tool.py), runnable from any install location via `uv run --script <skill-root>/scripts/zotero_tool.py <subcommand>`. Dependencies are pinned in the script's inline metadata (`pyzotero==1.13.0`, the planning baseline confirmed still current on PyPI on 2026-06-04) and locked into a reproducible sidecar lockfile [`scripts/zotero_tool.py.lock`](../../skills/zotero-paper-reader/scripts/zotero_tool.py.lock) (16 packages, hash-pinned). The `health` subcommand prints `pyzotero_version` so drift is visible.

### Command Surface

All required subcommands are present and emit indented JSON on stdout: `health`, `search` (metadata `qmode=titleCreatorYear`, and `--fulltext` → `qmode=everything`), `item`, `children`, `collections`, `tags`, `fulltext` (per-attachment `fulltext_item`), `doiindex` (DOI → item-key map over top-level items), and `pdf`. `search --fulltext` (library-wide full-text *search*) and `fulltext` (single-attachment full-text *retrieval*) are kept as separate subcommands per the task 01 contract. The `pdf` command preserves the legacy local-storage-first behavior — it checks `~/Zotero/storage/ATTACHMENT_KEY/*.pdf` first (emitting `source: local-storage`), then falls back to a Web API download via pyzotero (`zot.item` for the original filename, `zot.file` for bytes → `--out-dir`, default `/tmp`, emitting `source: web-download`), and exits non-zero if neither yields a ≥1 KB PDF. No raw MCP or curl calls remain.

### Access-Mode Detection

`make_client(prefer=...)` selects local vs. web. In `auto` mode it probes `http://localhost:23119/api/users/0/items` and uses local only on a 2xx response. A key correction over the task 01 draft: pyzotero 1.13.0 `local=True` still **requires** `library_id` and `library_type` (it raises `MissingCredentialsError` otherwise), and the local API serves the desktop's default library at id `0` — so the tool constructs `Zotero(library_id=0, library_type="user", local=True)`, not `library_id=None`. This was verified against the installed pyzotero 1.13.0 source (`_client.py`) and a live forced-local call that reached `http://localhost:23119/api/users/0/items` correctly. [`references/access-modes.md`](../../skills/zotero-paper-reader/references/access-modes.md) was updated to match.

### Deferred Boundary Resolved: Local Full-Text Search

The task 01 contract deferred whether the *local* API serves `qmode="everything"` full-text search. **Resolution: it does not** — `search --fulltext` routes unconditionally to the Web API and reports a clear error when Web API credentials are absent. The verification machine had Zotero Desktop running (connector port returned "Zotero is running") but the local API option was *disabled*: the `/api` path returned `403 Local API is not enabled`, so a live local full-text probe was not possible. The boundary is therefore set conservatively to Web-API-only, matching pyzotero's documented local-mode capability surface and the historical behavior of Zotero's local HTTP server. The "verify in task 02" markers in `access-modes.md` and `SKILL.md` are replaced with this verified answer (capability matrix row now reads `no` for local full-text search).

### Configuration and Secret Safety

Config resolves from environment variables first, then a project-local `Notes/.env` (env wins on conflict); values are never printed. Documented variables: `ZOTERO_LIBRARY_ID`, `ZOTERO_LIBRARY_TYPE` (default `user`), `ZOTERO_API_KEY`, plus the one override the implementation introduced — `pdf --out-dir` (no storage-path override; local PDFs use the standard `~/Zotero/storage/`). `health` reports only booleans (`config_present`, `web_api_configured`), never values.

**No-secret-leak verified live:** a forced web call with a fake API key produced a pyzotero `UserNotAuthorisedError` whose text contained the request URL but **not** the API key — pyzotero sends the key in the `Zotero-API-Key` HTTP header, not the URL, so it cannot appear in exception text. The `library_id` does appear in the URL, but it is a public identifier (visible in zotero.org URLs), not a secret. The regression test asserts the API key never appears in combined stdout+stderr.

### Verification

[`tests/test-zotero-tool.sh`](../../tests/test-zotero-tool.sh) — a durable, credential-free regression harness (18 checks, all passing) covering: `--help` lists every subcommand; `health` reports `pyzotero_version: 1.13.0` and the `active_mode` field and exits non-zero when no mode is usable; searches emit clean `error:` lines (not stack traces) with no access; `--fulltext` names its Web API requirement; and the no-secret-leak invariant. Run with `bash tests/test-zotero-tool.sh` from the repo root. No live Zotero/credentialed end-to-end run was possible on this machine (local API disabled, no Web API credentials present) — that end-to-end pass belongs to task 05's verification with real credentials.

### Deviation from Planned Files

The root task's "Planned Files" listed `pyproject.toml` and `uv.lock`. I did not create those, because the planner's Revision Note explicitly prohibits a project-style `uv run --project` layout (plugin-installed users lack the repo-relative path). The correct lock artifact for a self-contained PEP 723 script is the `uv lock --script` sidecar `zotero_tool.py.lock`, which `uv run --script` uses automatically from any install location. This satisfies the pinning/reproducibility intent of those planned files without the prohibited project dependency.
