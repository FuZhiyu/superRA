---
title: "Retire Upstream superpowers-Fork Remnants"
status: not-started
depends_on:  []
---

## Objective

Remove or rename the inert remnants of the upstream superpowers fork that predate superRA and no longer describe this repo: package.json and gemini-extension.json still carry the name/description "superpowers" (package.json main points at .opencode/plugins/superpowers.js); .opencode/ (INSTALL.md, plugins) and docs/superpowers/ document the upstream plugin; docs/testing.md describes testing upstream skills (subagent-driven-development); tests/subagent-driven-dev and tests/opencode test upstream behavior. For each: delete it, or rename/rewrite it to describe superRA, deciding per surface whether any harness support (e.g. Gemini, OpenCode) should be kept as real superRA packaging. Update scripts/bump-version.sh's .version-bump.json and RELEASE-NOTES.md if a versioned manifest is removed or renamed. Validation: no remaining "superpowers" identifier in shipped metadata; bump-version.sh --check clean; no dangling references (grep for the removed paths).

## Results

