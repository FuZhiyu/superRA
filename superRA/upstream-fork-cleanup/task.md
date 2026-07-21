---
title: "Retire Upstream superpowers-Fork Remnants"
status: implemented
depends_on:  []
---

## Objective

Remove or rename the inert remnants of the upstream superpowers fork that predate superRA and no longer describe this repo: package.json and gemini-extension.json still carry the name/description "superpowers" (package.json main points at .opencode/plugins/superpowers.js); .opencode/ (INSTALL.md, plugins) and docs/superpowers/ document the upstream plugin; docs/testing.md describes testing upstream skills (subagent-driven-development); tests/subagent-driven-dev and tests/opencode test upstream behavior. For each: delete it, or rename/rewrite it to describe superRA, deciding per surface whether any harness support (e.g. Gemini, OpenCode) should be kept as real superRA packaging. Remove tests whose sole oracle is literal prose in skill, agent, adapter, or workflow documentation; preserve tests of structured metadata, generated-artifact equality, machine-contract tokens, parser output, hooks, commands, and observable behavior. Release the completed cleanup as `0.3.2`: update all maintained plugin manifests through `scripts/bump-version.sh` and document every user-visible change included in the release. Validation: no remaining "superpowers" identifier in shipped metadata; bump-version.sh --check clean; no dangling references (grep for the removed paths); maintained test suites pass without prose-pinning assertions.

## Revision Notes

The researcher widened the cleanup after integration review: remove brittle exact-prose assertions across the maintained test surface and add the dashboard worktree-URL fix omitted from the `0.3.2` release notes. Reopen implementation and review; preserve structural and behavioral coverage rather than replacing deleted assertions with new wording pins.

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

Removed the harness contract tests whose only oracle was literal wording in
skill, agent, adapter, or workflow prose. The remaining static checks parse
Markdown tables, role frontmatter, hook registries, and generated artifacts;
fixture tests continue to verify task-read ordering, dispatch events, parser
output, and other observable behavior. The load-contract ledger and its README
now classify task-read and orchestration coverage as fixture-based instead of
claiming deleted prose checks. The `0.3.2` notes also record the dashboard fix
that preserves the invoking worktree in launch and reuse URLs.

### Integration protection

The researcher selected the existing test gates rather than new drift tests.
The harness instruction-following suite passed with 139 tests. The full
task-tree suite passed with 712 passed, 2 skipped, and 3 expected warnings;
`tests/check-harness-compatibility.sh` passed its 7 checks;
`scripts/bump-version.sh --audit` reported all `0.3.2` manifests aligned with
no undeclared version references; `superra task check` and the Markdown checks
passed.

**Final diff self-check:** `git diff 191313153ae54446bf6f6808a0ee3df693705e17..HEAD`; surviving change classes are the retired upstream packaging, documentation, and tests; maintained-manifest version and release-note updates; compatibility-check cleanup; prose-pinning test removal with structured/behavioral coverage retained; and synchronized release automation. The audit configuration retains only extant historical records and deliberate filename classes. The dashboard code, instructions, and task records in the range are already-approved incoming merge content, retained as documented in `a5b2a716`; no scope-ambiguous or suspicious hunk remains. Project-doc audit found no stale root-level claims or dangling references to removed paths.

The matured root rollup now identifies the task-tree workstream as in progress and the docs-site workstream as postponed while retaining their shipped and prior-integration context.
