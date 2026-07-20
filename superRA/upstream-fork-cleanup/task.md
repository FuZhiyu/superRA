---
title: "Retire Upstream superpowers-Fork Remnants"
status: implemented
depends_on:  []
---

## Objective

Remove or rename the inert remnants of the upstream superpowers fork that predate superRA and no longer describe this repo: package.json and gemini-extension.json still carry the name/description "superpowers" (package.json main points at .opencode/plugins/superpowers.js); .opencode/ (INSTALL.md, plugins) and docs/superpowers/ document the upstream plugin; docs/testing.md describes testing upstream skills (subagent-driven-development); tests/subagent-driven-dev and tests/opencode test upstream behavior. For each: delete it, or rename/rewrite it to describe superRA, deciding per surface whether any harness support (e.g. Gemini, OpenCode) should be kept as real superRA packaging. Update scripts/bump-version.sh's .version-bump.json and RELEASE-NOTES.md if a versioned manifest is removed or renamed. Validation: no remaining "superpowers" identifier in shipped metadata; bump-version.sh --check clean; no dangling references (grep for the removed paths).

## Results

Removed the inactive upstream packaging instead of relabeling it: the root
`package.json` only pointed to the obsolete OpenCode plugin, and the Gemini
manifest had no superRA adapter. Removed the matching OpenCode plugin,
upstream changelog and design documents, and upstream-only test suites; the
maintained Claude, marketplace, and Codex manifests remain version-controlled in
[.version-bump.json](../../.version-bump.json).

Verification: `scripts/bump-version.sh --check` reports all three maintained
manifests at `0.3.1`; `tests/check-harness-compatibility.sh` passes; a sweep
of active sources finds no references to the removed paths or `superpowers`
in maintained plugin metadata. Historical planning and release records remain
as provenance for the retired upstream work.
