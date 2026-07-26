---
title: "Close Interactive Integration Contract Gaps"
status: approved
depends_on: []
---

## Objective

Resolve the integration review blockers as one coherent execution-contract repair: keep review now/defer/skip on the existing status lifecycle; wire superimplement to per-task main/subagent seat selection; make canonical role specs resolvable for main-filled and forced-inline seats in installed cross-repo use; add a minimal domain-neutral interactive self-review; remove DRY/Necessity duplication; and correct the conservative cleanup's narrow reproducibility accounting. Success: every recorded integration finding is accepted and fixed, current docs and tests reflect the same contract, packaged/generated access works, and full integration verification passes.

## Planner Guidance

The findings in superRA/interactive-mode/task.md and superRA/interactive-mode/prose-test-cleanup/task.md at review commit f88a42f5 are inputs except for the superseded durable-disposition finding: defer / skip leaves the task `implemented`, and the normal review gates remain unchanged. Reuse the existing status enum; do not add a review-status field. Keep role behavior in agents/*, harness resolution in the Codex adapter/setup owner, and changing-tree behavior in its reference. Load skill-creator before skills/* edits. Apply DRY/Necessity line by line and keep the diff bounded to these findings.

## Results

Resolved the integration-review findings:

- [interactive-mode.md](../../../skills/superplan/references/interactive-mode.md)
  performs a domain-neutral self-review and leaves deferred or skipped review
  at `implemented`.
- [superimplement/SKILL.md](../../../skills/superimplement/SKILL.md) selects
  the per-task seat structure and executes each filler through a structured
  main-role or dispatch route. [agent-orchestration/SKILL.md](../../../skills/agent-orchestration/SKILL.md)
  retains one seat-choice table and only the orchestration delta.
- [codex-instructions.md](../../../skills/using-superra/references/codex-instructions.md)
  routes main-filled and harness-forced-inline seats through `canonical-role`.
  [sync_codex_agents.py](../../../skills/codex-superra-setup/scripts/sync_codex_agents.py)
  resolves the canonical role spec from the plugin package, and its test now
  verifies resolution from a foreign project directory.
- [superplan/SKILL.md](../../../skills/superplan/SKILL.md) points to
  `changing-the-tree.md` without paraphrasing its drift, tracker, protocol, or
  stop rules.
- [prose-test-cleanup/task.md](../prose-test-cleanup/task.md) now records the
  reproducible narrow accounting: range `6be18283..64440306`, pathspecs
  `tests`, `:(glob)skills/**/test*.py`, and
  `:(glob)skills/**/tests/**`, with 349 additions, 2,386 deletions, and 43
  files.

Verification:

- Focused contract tests: `13 passed`.
- Task-tree and harness suites: `824 passed`, with four expected warnings.
- Harness compatibility and generated-agent equality: exit `0`.
- Codex hook suite: `15/15`.
- Zotero shell suite: `18/18`.
- Skill validation, Markdown integrity, Python compilation, and
  `git diff --check`: clean.
