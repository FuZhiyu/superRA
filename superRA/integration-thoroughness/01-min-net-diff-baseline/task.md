---
title: "Ternary, Asymmetric Minimum-Net-Diff Prune Rule"
status: approved
depends_on: []
tags: []
output:
  - skills/refactor-and-integrate/SKILL.md
created: 2026-06-18
---

## Objective

Replace the binary prune rule in `skills/refactor-and-integrate/SKILL.md` with a ternary, asymmetric one so integration pruning can no longer silently delete legitimate work (Type II) or silently retain scope creep (Type I). The justification baseline is already the union of sources the skill lists (`§Minimum Net Diff` para 1); this task adds the third branch and the asymmetry, it does not re-enumerate the sources.

Edit `§Minimum Net Diff` and the parallel `§Final Diff Self-Check` step 5 ("Prune or record"), which currently both say a hunk without justification is reverted **or** justified:

- **Never silently delete.** Deletion removes a hunk from the governing diff so no later reviewer can see what vanished; retention is reversible. So the dangerous direction is gated and uncertainty defaults to keep.
- **Confident junk → revert.** Debug prints, reformatting, speculative abstraction, dead helpers — where reverting loses no real work. (Unchanged from today.)
- **Justified → keep + cite** the specific source (objective, checklist item, task-file coherence, doc currency, logged user decision, or supplied Sync impact).
- **Scope-ambiguous but plausibly load-bearing → keep, and raise it** — never revert on the agent's own authority. The implementer raises it as a `## Review Notes` item (mechanism owned by [02-implementer-integration-self-review](../02-implementer-integration-self-review/task.md) and the orchestrator choreography in [03-superintegrate-integrate-restructure](../03-superintegrate-integrate-restructure/task.md)); a hunk genuinely needed but covered by **no** source is evidence the task tree is stale and routes to `superplan §User Feedback and Changing the Task Tree`, not a prune and not a silent keep.

Keep the deletion-symmetry already present (base-current deletions/relocations need a warrant too). Do not add a per-hunk classification taxonomy or new section — the design session rejected that as a contingency tree that multiplies the rubber-stampable surface; this is a framing change of the existing prune step, ~3–4 sentences.

Validation: the edited `§Minimum Net Diff` and `§Final Diff Self-Check` name all three branches and the never-silently-delete asymmetry; the `superplan` routing for the no-source case is stated once; passes the `CLAUDE.md §Teach the Protocol` DRY + Necessity tests (no restating of the source list, no taxonomy).

## Results

Replaced the binary prune rule with the ternary, asymmetric one in two places in [skills/refactor-and-integrate/SKILL.md](../../../skills/refactor-and-integrate/SKILL.md).

- **§Minimum Net Diff** ([SKILL.md:26](../../../skills/refactor-and-integrate/SKILL.md#L26)): the "revert it or record the justification" sentence is now a ternary, asymmetric rule. It opens with the never-silently-delete asymmetry (deletion drops a hunk so no later reviewer sees what vanished; uncertainty defaults to keep), then names all three branches — confident junk → revert; justified → keep + cite "one of the sources in para 1" (no re-enumeration); scope-ambiguous but plausibly load-bearing → keep and raise, never revert on own authority, with the no-source case routing once to `superplan §User Feedback and Changing the Task Tree`. The base-current deletion/relocation symmetry is preserved ("The same warrant gates base-current deletions and relocations.").
- **§Final Diff Self-Check step 5** ([SKILL.md:55](../../../skills/refactor-and-integrate/SKILL.md#L55)): retitled from "Prune or record" to "Prune asymmetrically", deferring to §Minimum Net Diff rather than re-stating the rule. It names the three branches and the `## Review Notes`-vs-status-return handoff target for the raised hunk; the `superplan` routing lives only in §Minimum Net Diff (stated once, per objective).

No new section or per-hunk taxonomy added — this is a framing change of the existing prune step. The source list (para 1) is referenced, not restated, in both edits, satisfying the `CLAUDE.md §Teach the Protocol` DRY + Necessity tests.

**Verification:** `uv run --script skills/report-in-markdown/scripts/check_markdown.py skills/refactor-and-integrate/SKILL.md` → `clean`. Both edited sections name all three branches and the never-silently-delete asymmetry; `superplan` routing appears once.

**Final diff self-check:** `git diff b0865e11..HEAD -- skills/refactor-and-integrate/SKILL.md`; the two surviving hunks (§Minimum Net Diff prune sentence, §Final Diff Self-Check step 5) are both `skills/*` instruction-prose edits — the suspicious class — each justified line by line against this task objective: the new prune sentence names all three branches + the never-silently-delete asymmetry and references "the sources in para 1" rather than re-enumerating them; step 5 defers to §Minimum Net Diff and adds only the `## Review Notes`-vs-status-return handoff target. No restatement of the source list, no per-hunk taxonomy, no new section — passes `CLAUDE.md §Teach the Protocol` DRY + Necessity. No codebase-fit change needed this integration pass; `check_markdown.py` clean.
