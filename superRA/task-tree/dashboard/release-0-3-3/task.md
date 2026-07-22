---
title: "Release Dashboard Fixes as 0.3.3"
status: revise
depends_on:  []
---

## Objective

Prepare patch release 0.3.3 in PR #49. Add a dated 0.3.3 section to RELEASE-NOTES.md covering dashboard hardening merged after v0.3.2 (PR #46) and the worktree image/reconnect fixes in issues #47-#48; bump every maintained version manifest with scripts/bump-version.sh 0.3.3; verify version check and audit are clean. Do not create a tag manually: the release workflow must create v0.3.3 from the merged main commit. Scope to release notes and version-managed manifests; generated artifacts: none.

## Results

- Added the dated `0.3.3` release section while preserving `Unreleased` above
  it. The notes cover the complete dashboard delta since `v0.3.2`: PR #46's
  state/rendering, asset, trust-boundary, event-loop, parse, SSE, and lifecycle
  hardening; issue #47's selected-worktree relative images; and issue #48's
  reconnect cache rebuild and scoped reload
  ([RELEASE-NOTES.md:3](../../../../RELEASE-NOTES.md#L3)).
- Ran `scripts/bump-version.sh 0.3.3`; the maintained Claude plugin,
  marketplace, and Codex manifests now agree at `0.3.3`
  ([plugin.json:4](../../../../.claude-plugin/plugin.json#L4),
  [marketplace.json:12](../../../../.claude-plugin/marketplace.json#L12),
  [Codex plugin.json:3](../../../../.codex-plugin/plugin.json#L3)). No tag was
  created or pushed; the main-branch release workflow remains responsible for
  creating `v0.3.3` from the merged commit.
- Verification passed: `scripts/bump-version.sh --check` reports all three
  manifests synchronized, `--audit` reports no undeclared `0.3.3` references,
  and the release workflow's exact extraction regex finds one non-empty 34-line
  `0.3.3` section with `Unreleased` above it. The release notes pass the
  Markdown checker; the dashboard suite passes 308 tests with two dependency
  warnings, and the complete task-tree script suite passes 731 tests with four
  expected/dependency warnings.

## Review Notes

1. **MAJOR** — The `0.3.3` section does not yet cover the complete PR #46
   delta required by the objective. Its PR #46 bullets cover eight hardening
   workstreams through lifecycle robustness
   ([RELEASE-NOTES.md:9-28](../../../../RELEASE-NOTES.md#L9-L28)), but omit the
   merged frontend-polish workstream: debounced and single-pass sidebar
   filtering ([dashboard.js:619-648](../../../../skills/task-tree/scripts/templates/dashboard.js#L619-L648),
   [test_dashboard.py:2603-2666](../../../../skills/task-tree/scripts/test_dashboard.py#L2603-L2666)),
   title-aware children-panel cache invalidation
   ([dashboard.js:1177-1199](../../../../skills/task-tree/scripts/templates/dashboard.js#L1177-L1199)),
   and refresh-on-open worktree selection without redundant option rebuilds
   ([dashboard.js:2405-2436](../../../../skills/task-tree/scripts/templates/dashboard.js#L2405-L2436)).
   Add a concise user-facing clause or bullet covering that final PR #46
   workstream, then update the section-length/result evidence and rerun the
   exact release-note extraction check.
