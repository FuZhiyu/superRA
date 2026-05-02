---
author: "Julie Zhiyu Fu"
date: 2026-04-22
timestamp: "2026-04-22T20:28:59-0500"
session_id: "session-20260422-direct-mode-follow-up"
git_commit: "0af9f833767498e12d57d344e6a66be50319a110"
git_message: "results: fact-check direct-mode follow-up log"
git_dirty: true
tags: ["results", "integration"]
project: "superRA"
permalink: "docs/plans/2026-04-22-direct-mode-role-references-results"
---

# Direct-Mode Role References — Results

This follow-up closes the remaining direct-mode accessibility gap on the
Codex dispatch-preference branch. The main agent now loads the
direct-mode implementer and reviewer protocol from the shared
`skills/using-superRA/references/` surface rather than depending on raw
`agents/implementer.md` / `agents/reviewer.md`, and the harness
compatibility check now guards that path against regression. The
permanent plan companion is
[2026-04-22-direct-mode-role-references-plan.md](./2026-04-22-direct-mode-role-references-plan.md).

## Permanent Artifacts

- The direct-mode implementer mirror is
  [../../skills/using-superRA/references/direct-mode-implementer.md](../../skills/using-superRA/references/direct-mode-implementer.md).
- The direct-mode reviewer mirror is
  [../../skills/using-superRA/references/direct-mode-reviewer.md](../../skills/using-superRA/references/direct-mode-reviewer.md).
- The main-agent direct-mode load rule is
  [../../skills/using-superRA/references/main-agent.md](../../skills/using-superRA/references/main-agent.md).
- Contributor guidance for the manual-mirror rule is
  [../../CLAUDE.md](../../CLAUDE.md).
- The drift guard and compatibility gate are in
  [../../tests/check-harness-compatibility.sh](../../tests/check-harness-compatibility.sh).

## Implementation

- Added skill-owned direct-mode role mirrors for the implementer and
  reviewer protocol, each explicitly marked as a temporary manual mirror
  of the canonical `agents/*.md` file until an automated sync exists.
- Rewired the main-agent direct-mode contract to load those references
  from the shared skill surface instead of reading raw agent files.
- Added contributor guidance that any direct-mode-relevant change to the
  canonical role files must update the mirrors in the same change.
- Kept `.agents/skills/` in place because repo docs and the compatibility
  gate treat it as the repo-local Codex skill-discovery surface, not a
  stray generated-agent artifact.

## Integration Summary

- Phase A protected two branch-defining behaviors: the direct-mode load
  path itself and the regression assertions that reject a return to raw
  `agents/*.md` loads.
- The existing assertions in
  [../../tests/check-harness-compatibility.sh](../../tests/check-harness-compatibility.sh)
  now serve as the drift guard for this follow-up; the suite re-ran
  green on the integration baseline.
- `origin/main` remained the integration base for this branch, matching
  the open PR target and the earlier archived branch decision. It was
  already an ancestor of the current branch, so no mechanical merge
  commit was needed during Phase B.
- Phase B found one cumulative-diff cleanup item: trailing whitespace in
  `skills/using-superRA/references/main-agent.md`. After that fix,
  `git diff --check addc9ca7fe1bdbedb080d92095facb649074c1e4..HEAD` and
  the full compatibility suite both passed.

## Validation

- Primary validation entrypoint:
  `bash tests/check-harness-compatibility.sh`
- Supplementary integration cleanliness check:
  `git diff --check addc9ca7fe1bdbedb080d92095facb649074c1e4..HEAD`
- Both checks passed on this branch after the Phase B cleanup.
- PR [#19](https://github.com/FuZhiyu/superRA/pull/19) is open against
  `main` and has been marked ready for review.

## Scope Notes

- This record covers the post-archive direct-mode follow-up only. The
  original Codex dispatch-preference scope remains documented in
  [2026-04-22-codex-agent-dispatch-preference-plan.md](./2026-04-22-codex-agent-dispatch-preference-plan.md)
  and
  [2026-04-22-codex-agent-dispatch-preference-results.md](./2026-04-22-codex-agent-dispatch-preference-results.md).
- No `results_attachments/` directory or figure-materialization pass was
  needed for this follow-up.

## Reproducibility

Reproduce the branch validation from the repository root by running
`bash tests/check-harness-compatibility.sh`. The pre-restructure commit
for this permanent record is
`0af9f833767498e12d57d344e6a66be50319a110`
(`results: fact-check direct-mode follow-up log`).
