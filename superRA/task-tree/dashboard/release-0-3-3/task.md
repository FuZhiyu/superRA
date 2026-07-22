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
  manifests ([release.yml:31](../../../../.github/workflows/release.yml#L31)).
- Protection review found and closed one real gap in the existing release-note
  guard: extraction now rejects zero or multiple current-version sections,
  requires the unique section to appear directly below `Unreleased`, and still
  rejects an empty body
  ([release.yml:44](../../../../.github/workflows/release.yml#L44)). A fresh
  green run accepted the current 38-line section; in-memory duplicate-section
  and intervening-content perturbations were both rejected before the current
  source was rechecked green. No separate test file was needed because the
  strengthened workflow step is the executable release gate.
- Tag ownership remains protected by workflow scope and current repository
  state: automatic release runs trigger on `main`, and the workflow creates
  `v$VERSION` against the merged commit only after the manifest and note guards
  pass ([release.yml:3](../../../../.github/workflows/release.yml#L3),
  [release.yml:75](../../../../.github/workflows/release.yml#L75)). No tag points
  at the release-preparation branch HEAD.

## Review Notes

1. **MAJOR** — The new placement guard does not actually require the current
   version section to follow `Unreleased`. It checks only whether
   `notes[unreleased.end():match.start()]` contains text
   ([release.yml:56-71](../../../../.github/workflows/release.yml#L56-L71)); when
   the version heading is moved *above* `Unreleased`, that reversed slice is
   empty and the workflow accepts it. The current green, duplicate red, and
   intervening-content red checks are credible, but the displaced perturbation
   does not falsify the full ordering claim. Require `match.start()` to be after
   `unreleased.end()` as well as allowing only whitespace between them, then
   record red evidence for the above-`Unreleased` displacement and restore the
   current green source.

2. **MAJOR** — Tag creation is not constrained to a merged `main` commit.
   Although push-triggered runs are filtered to `main`, `workflow_dispatch`
   remains available without a ref guard
   ([release.yml:3-11](../../../../.github/workflows/release.yml#L3-L11)), and
   the release step targets the triggering `${{ github.sha }}`
   ([release.yml:75-89](../../../../.github/workflows/release.yml#L75-L89)). A
   manual dispatch against this release-preparation branch could therefore
   create `v0.3.3` before merge, contrary to the task's automation-owned,
   merged-main tag contract. Gate the release job/step on
   `refs/heads/main` (or otherwise resolve and verify the target is `main`)
   while preserving workflow-owned tag creation and safe reruns.
