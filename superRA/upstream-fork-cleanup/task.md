---
title: "Retire Upstream superpowers-Fork Remnants"
status: approved
depends_on:  []
---

## Objective

Remove or rename the inert remnants of the upstream superpowers fork that predate superRA and no longer describe this repo: package.json and gemini-extension.json still carry the name/description "superpowers" (package.json main points at .opencode/plugins/superpowers.js); .opencode/ (INSTALL.md, plugins) and docs/superpowers/ document the upstream plugin; docs/testing.md describes testing upstream skills (subagent-driven-development); tests/subagent-driven-dev and tests/opencode test upstream behavior. For each: delete it, or rename/rewrite it to describe superRA, deciding per surface whether any harness support (e.g. Gemini, OpenCode) should be kept as real superRA packaging. Release the completed cleanup as `0.3.2`: update all maintained plugin manifests through `scripts/bump-version.sh` and add the corresponding release note. Validation: no remaining "superpowers" identifier in shipped metadata; bump-version.sh --check clean; no dangling references (grep for the removed paths).

## Results

Removed the inactive upstream packaging instead of relabeling it: the root
manifest only pointed to the obsolete OpenCode plugin, and the alternate
harness manifest had no superRA adapter. Removed the matching OpenCode plugin,
upstream changelog and design documents, and upstream-only test suites; the
maintained Claude, marketplace, and Codex manifests remain version-controlled in
[.version-bump.json](../../.version-bump.json).

Released the cleanup as `0.3.2`. `scripts/bump-version.sh --audit` verifies
that the maintained Claude, marketplace, and Codex manifests are aligned, and
task-tree records are excluded from that audit as durable release context.
`tests/check-harness-compatibility.sh` passes after its adapter checks
were limited to the packaged Codex references. A sweep of every tracked
non-task source finds no references to the retired manifest names or removed
paths, and no `superpowers` identifier in maintained plugin metadata. The task
Objective names the retired paths as its implementation contract; historical
records preserve the retired material by description instead.

### Integration protection

The researcher selected the existing test gates rather than new drift tests.
The full task-tree suite passed with 712 passed, 2 skipped, and 5 expected
warnings; `tests/check-harness-compatibility.sh` passed its 7 checks; and
`scripts/bump-version.sh --audit` reported all `0.3.2` manifests aligned with
no undeclared version references.
