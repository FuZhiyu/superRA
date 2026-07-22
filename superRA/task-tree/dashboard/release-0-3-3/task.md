---
title: "Release Dashboard Fixes as 0.3.3"
status: not-started
depends_on:  []
---

## Objective

Prepare patch release 0.3.3 in PR #49. Add a dated 0.3.3 section to RELEASE-NOTES.md covering dashboard hardening merged after v0.3.2 (PR #46) and the worktree image/reconnect fixes in issues #47-#48; bump every maintained version manifest with scripts/bump-version.sh 0.3.3; verify version check and audit are clean. Do not create a tag manually: the release workflow must create v0.3.3 from the merged main commit. Scope to release notes and version-managed manifests; generated artifacts: none.

## Results
