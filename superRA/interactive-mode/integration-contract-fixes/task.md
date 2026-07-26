---
title: "Close Interactive Integration Contract Gaps"
status: implemented
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
- [canonical-role.md](../../../skills/using-superra/references/canonical-role.md)
  and [resolve_role.py](../../../skills/using-superra/scripts/resolve_role.py)
  provide the shared packaged-role resolver. The
  [Claude adapter](../../../skills/using-superra/references/claude-instructions.md)
  and [Codex adapter](../../../skills/using-superra/references/codex-instructions.md)
  both route main-filled and forced-inline seats through it, and
  [test_resolve_role.py](../../../skills/using-superra/scripts/test_resolve_role.py)
  verifies both roles from a foreign project against a copied plugin layout.
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

Accepted-fix verification:

- Shared packaged-role resolver: `1 passed`; Codex agent generation: `3 passed`.
- Focused execution-contract tests: `32 passed`.
- Full CI-safe harness suite: `126 passed`.
- Harness compatibility and generated-agent equality: exit `0`.
- Five edited skill directories passed `quick_validate.py`; Markdown integrity
  and `git diff --check` were clean.

**Final diff self-check:** `git diff 84d451deff42cab17944fd8ab038ca8d092428d1 --cached`
against the complete staged candidate tree; surviving-change classes are the
interactive execution-mode contract and docs, shared packaged canonical-role
resolution, task-tree/harness contract coverage, conservative prose-test
cleanup, and task records. Suspicious hunk justifications: the cross-repo role
resolution edits in `skills/using-superra/` and the two harness adapters close
Review Note 1; the domain-neutral interactive self-review and main/subagent
seat-execution edits implement this task's objective; the `superplan` and
`superimplement` deletions remove the Review Note 3 DRY/Necessity echoes; the
deleted generated direct-mode references are authorized by
[drop-direct-generated](../drop-direct-generated/task.md); and the broad test
deletions retain only structured contract coverage per
[prose-test-cleanup](../prose-test-cleanup/task.md). Project-doc walk-up found
no stale claim in the root `CLAUDE.md`, root `README.md`, or harness
[README.md](../../../tests/harness-instruction-following/README.md). No
unjustified or scope-ambiguous hunk remains.

## Review Notes

1. MAJOR — [agent-orchestration/SKILL.md:95](../../../skills/agent-orchestration/SKILL.md#L95), [codex-instructions.md:20](../../../skills/using-superra/references/codex-instructions.md#L20), and [codex-superra-setup/SKILL.md:74-83](../../../skills/codex-superra-setup/SKILL.md#L74-L83). The shared seat contract requires every main-filled seat to resolve and load the canonical role spec, but the only executable resolution rule lives in the Codex-only adapter/setup skill. No Claude adapter or shared resolver tells a Claude main-seat filler how to turn the packaged plugin into an absolute role path; the committed Claude fixture invents `/plugin/superRA/...` and invokes the Codex setup script, so it does not prove that the shipped instructions can discover that path in cross-repo plugin use. This leaves one supported harness unable to execute the new main-implementer/main-reviewer structures from the documented contract. Add a harness-appropriate packaged-role resolver for Claude (or move canonical-role resolution to a genuinely shared owner and have each adapter point to it), then cover discovery from a foreign project rather than only parsing a fabricated absolute-path transcript.
   → implemented: added a shared packaged-role resolver, routed both adapters to it, and covered copied-plugin discovery from a foreign project ([resolve_role.py](../../../skills/using-superra/scripts/resolve_role.py), [test_resolve_role.py](../../../skills/using-superra/scripts/test_resolve_role.py)).

2. MAJOR — [task.md:40-48](task.md#L40-L48) and [interactive-mode/task.md:84-95](../task.md#L84-L95). This task's implementer changed the governing diff after the umbrella trail was written but never recorded a Final-Diff-Self-Check in this assigned task. The umbrella trail still generically justifies all `skills/*` instruction edits and does not identify the later cross-repo role-resolution, self-review, or seat-execution hunks that triggered this fix task. This fails the integration-stage `[BLOCKING]` freshness gate even though `origin/main...HEAD` currently resolves to the supplied base range. Recompute `git diff 84d451deff42cab17944fd8ab038ca8d092428d1..HEAD` after the accepted fixes and add a fresh, task-local trail that classifies and justifies those suspicious instruction hunks.
   → implemented: added the fresh task-local candidate-tree audit above, including explicit justifications for cross-repo role resolution, interactive self-review, seat execution, and the DRY cleanup ([task.md](task.md)).

3. MAJOR — [superplan/SKILL.md:34](../../../skills/superplan/SKILL.md#L34), [superplan/SKILL.md:64-70](../../../skills/superplan/SKILL.md#L64-L70), and [superimplement/SKILL.md:20-24](../../../skills/superimplement/SKILL.md#L20-L24). Several surviving instruction additions fail the repository's `[BLOCKING]` DRY + Necessity test. The superplan routing spine describes what `interactive-mode.md` fuses, enumerates the mechanics in `decomposition.md`, and repeats that reference's self-review checklist immediately while requiring it to be loaded. Superimplement's top-level process repeats the seat-selection, seat-execution, and verdict loop defined again at [superimplement/SKILL.md:76-89](../../../skills/superimplement/SKILL.md#L76-L89), while its interactive route at [superimplement/SKILL.md:93](../../../skills/superimplement/SKILL.md#L93) paraphrases the loaded reference's self-review/review-disposition contract. Removing these echoes would not change behavior because the authoritative references or detailed step are already loaded in the same path. Keep only the routing/choreography needed to reach each owner and delete the duplicate summaries.
   → implemented: reduced both workflow spines to routing and phase choreography while leaving the detailed procedures in their loaded owners ([superplan/SKILL.md](../../../skills/superplan/SKILL.md), [superimplement/SKILL.md](../../../skills/superimplement/SKILL.md)).
