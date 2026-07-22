---
title: "Release Dashboard Fixes as 0.3.3"
status: approved
depends_on:  []
---

## Objective

Prepare patch release 0.3.3 in PR #49. Add a dated 0.3.3 section to RELEASE-NOTES.md covering dashboard hardening merged after v0.3.2 (PR #46) and the worktree image/reconnect fixes in issues #47-#48; bump every maintained version manifest with scripts/bump-version.sh 0.3.3; verify version check and audit are clean. Do not create a tag manually: the release workflow must create v0.3.3 from the merged main commit. Scope to release notes and version-managed manifests; generated artifacts: none.

## Results

- Added the dated `0.3.3` release section while preserving `Unreleased` above
  it. The notes cover the complete dashboard delta since `v0.3.2`: PR #46's
  state/rendering, asset, trust-boundary, event-loop, parse, SSE, lifecycle, and
  frontend-refresh hardening; issue #47's selected-worktree relative images;
  and issue #48's reconnect cache rebuild and scoped reload
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
  and the release workflow's exact extraction regex finds one non-empty 38-line
  `0.3.3` section with `Unreleased` above it. The release notes pass the
  Markdown checker; the dashboard suite passes 308 tests with two dependency
  warnings, and the complete task-tree script suite passes 731 tests with four
  expected/dependency warnings.

### Result Protection

- The release workflow already runs `scripts/bump-version.sh --check` before it
  reads the release version, protecting agreement across all maintained
  manifests ([release.yml:32](../../../../.github/workflows/release.yml#L32)).
- Protection review found and closed one real gap in the existing release-note
  guard: extraction now rejects zero or multiple current-version sections,
  requires the unique section to appear directly below `Unreleased`, and still
  rejects an empty body
  ([release.yml:45](../../../../.github/workflows/release.yml#L45)). A fresh
  green run accepted the current 38-line section; in-memory duplicate-section
  and intervening-content perturbations were rejected. The directional fix was
  additionally checked red with the version section moved above `Unreleased`,
  then the current source was restored and rechecked green. No separate test
  file was needed because the strengthened workflow step is the executable
  release gate.
- Tag ownership is protected at the job boundary: the release job runs only
  when `github.ref` is `refs/heads/main`, covering both push and manual dispatch,
  and creates `v$VERSION` against that main commit only after the manifest and
  note guards pass ([release.yml:23](../../../../.github/workflows/release.yml#L23),
  [release.yml:80](../../../../.github/workflows/release.yml#L80)). Static
  validation confirmed the main ref enables the job while a feature-branch ref
  does not; no tag points at the release-preparation branch HEAD.
