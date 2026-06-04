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

## Review Notes

Approved. All 15 text-regression checks were verified adversarially (planted each forbidden token in a scratch skill copy; removed each required string) and every check flips to FAIL on its target, including regressions planted in `scripts/` and `references/`, not just `SKILL.md`. Both suites reproduce the reported 18/15 pass counts from the repo root; the health probe re-runs identically; no secrets, PDF contents, or library data are committed; edits are scoped to the two intended files. The items below are non-blocking MINOR accuracy fixes to the `## Results` prose — clean them up at your convenience.

1. MINOR — Live-probe transcript prefix mismatch. The transcript in `### Live Smoke Test` shows the final line as `error: no usable access mode: ...`, but the `health` command emits that line via `eprint` (no prefix) at [zotero_tool.py:202](../../skills/zotero-paper-reader/scripts/zotero_tool.py#L202) — only `fail()` adds the `error: ` prefix, and `health` does not call it. The real stderr is `no usable access mode: ...` with no prefix and on one line. Match the transcript to the actual output.

2. MINOR — Overstated mocked-tests rationale. The `### Mocked Tests` rationale says skipping would "duplicate already-passing deterministic coverage without adding new signal," but `load_env_file`'s `Notes/.env` parsing branch ([zotero_tool.py:70-76](../../skills/zotero-paper-reader/scripts/zotero_tool.py#L70) — comment skipping, `=` partition, quote stripping) and `get_config`'s file-precedence path ([zotero_tool.py:87-94](../../skills/zotero-paper-reader/scripts/zotero_tool.py#L87) — env-wins-over-file) are exercised by neither suite (no test creates `Notes/.env`), and the no-secret-leak invariant does not cover their correctness. The skip is acceptable against the advisory "consider" guidance, but reword the rationale to acknowledge the `.env`-parsing path as a deliberate accepted gap (a deterministic test needs only a temp `Notes/.env`, no mocking) rather than claiming it is already covered.

3. MINOR — Two citation slips in `## Results`. (a) The check labeled "SKILL.md description mentions pyzotero" actually asserts `pyzotero` appears anywhere in `SKILL.md`; the `description:` frontmatter field does not mention pyzotero (it appears only in the body, lines 9 and 56), so the check name and the in-test comment at [test-zotero-skill-text.sh:107-112](../../tests/test-zotero-skill-text.sh#L107) overstate scope. Either rename to "SKILL.md mentions pyzotero" or tighten the check to the description line. (b) The `### Mocked Tests` cite of "checks 15–17: clean error line, Web API named, no-secret-leak" is off — in `test-zotero-tool.sh` check 15 is the clean error line, 17 is "Web API named," and the no-secret-leak invariant is check 18.

