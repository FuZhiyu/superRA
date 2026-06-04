---
title: "Verify Zotero Skill Behavior"
status: implemented
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

**[tests/test-zotero-tool.sh](../../tests/test-zotero-tool.sh)** (pre-existing, task 02) — 18 checks: subcommand presence, health/version JSON, no-access error paths, no-secret-leak invariant. All 18 pass.

**[tests/test-zotero-skill-text.sh](../../tests/test-zotero-skill-text.sh)** (new, this task) — 15 checks in two groups:

- MCP regression guards (4 checks): `mcp__zotero`, `mcp_zotero`, `call_mcp`, `use_mcp_tool` must be absent from the entire skill tree.
- Stale-instruction guards (6 checks): `.claude/skills/mistral` hardcoded path, `.claude/skills/` prefix, `get_zotero_pdf.py`, `uv run --project`, `zotero-mcp-server`, `zotero_mcp` must all be absent.
- Positive invariants (5 checks): `SKILL.md` references `CLAUDE_SKILL_DIR`; `paper-reading.md` uses `uv run --script ${CLAUDE_SKILL_DIR}/scripts/zotero_tool.py`; `access-modes.md` documents the `403` edge case; script pins `pyzotero==1.13.0`; `SKILL.md` description mentions `pyzotero`.

All 15 pass.

### Verification Commands and Outcomes

```
$ bash tests/test-zotero-tool.sh
Passed: 18    Failed: 0

$ bash tests/test-zotero-skill-text.sh
Passed: 15    Failed: 0
```

### Live Smoke Test (health probe)

Attempted live `health` probe with no credentials set:

```
$ unset ZOTERO_LIBRARY_ID ZOTERO_API_KEY ZOTERO_LIBRARY_TYPE
$ uv run --quiet --script skills/zotero-paper-reader/scripts/zotero_tool.py health
{
  "pyzotero_version": "1.13.0",
  "local_api_available": false,
  "web_api_configured": false,
  "library_type": "user",
  "active_mode": null,
  "config_present": {
    "ZOTERO_LIBRARY_ID": false,
    "ZOTERO_API_KEY": false
  }
}
error: no usable access mode: enable the Zotero Desktop local API or
configure Web API credentials (see references/access-modes.md)
exit: 1
```

`local_api_available: false` — the Zotero Desktop local API is disabled on this machine (connector port answers but `/api` returns `403 Local API is not enabled`, consistent with the finding recorded in task 02). No Web API credentials are present. The full live smoke test (search, children, PDF-path retrieval, local full-text-search boundary probe) could not run; deterministic checks stand in. The `references/access-modes.md` conservative "unverified / Web-API-only" default for local full-text search is unchanged — a live probe was not possible.

### Mocked Tests

Mocked-pyzotero tests were considered. The two categories of logic that would benefit are `load_env_file` / `get_config` (pure Python, no pyzotero) and `make_client` error-message paths. The `make_client` web-credential-absent path is already exercised by `test-zotero-tool.sh` (checks 15–17: clean error line, `Web API` named, no-secret-leak), which covers the observable contract. The `load_env_file` / `get_config` functions are straightforward `os.environ` / `Path.read_text` logic; the no-secret-leak invariant in the existing test suite is the meaningful contract there. Mocked tests were not added — they would duplicate already-passing deterministic coverage without adding new signal.

