# Theory-Modeling Vertical — Results

> Mirrors `PLAN.md` structure. Updated after each task with key findings.
> New agents: read `PLAN.md` for what to do, `RESULTS.md` for what was found.

**Last updated:** 2026-04-23 (researcher-initiated restructure: `Define-Derive-Validate` replaced by a four-gate structure built around intuition/interpretability; Tasks 5 and 6 added; `Refactored` milestone rolled back for Phase B re-run after Task 6)
**Status:** Tasks 1–4 APPROVED and preserved under the new structure; Tasks 5 and 6 not started; Phase B integration review pending on the restructured skill

---

## Task 1: Create the `theory-modeling` domain skill and its stage-scoped references

**Status:** Implemented (review fixes incorporated)

### Key Findings
- Added `skills/theory-modeling/SKILL.md` with a proactive trigger surface, stage-scoped load table, an iron law centered on defined objects plus stated assumptions, and a shared `Define–Derive–Validate` checklist.
- The checklist makes notation discipline, interpretable primitive-level assumptions, stepwise derivations, and proof / special-case / numerical verification `[BLOCKING]` requirements.
- Added planning, drift-test, and integration references so the vertical has a complete PLAN / Phase A / Phase B path without inventing a new workflow or rendering utility.

### Notes
- The skill explicitly points human-facing equation/table/figure rendering back to `superRA:report-in-markdown`.
- Review feedback on the planning template has already been incorporated: the inventory now includes explicit sections for timing / information structure, solution concept, and notation conventions, and the hard gate no longer implies task drafting before researcher approval.

## Task 2: Wire the new vertical into runtime surfaces, docs, and discovery

**Status:** Implemented (review fixes incorporated)

### Key Findings
- Added `theory-modeling` to the `using-superRA` inventory and manifest, the `planning-workflow` routing table, and the `refactor-and-integrate` domain-specific integration pointers.
- Generalized the planning template and exit-plan-mode reminder so a second planning hard gate is first-class rather than a data-only exception.
- Updated contributor/runtime docs (`README.md`, `skills/CATEGORIES.md`, `CLAUDE.md`) to present theory/modeling as an implemented vertical, added `.agents/skills/theory-modeling`, and extended `tests/check-harness-compatibility.sh` with discovery/wiring assertions.

### Notes
- A review pass surfaced remaining single-vertical assumptions in the canonical agent prompts and generic integration/merge references; the task now includes fixes for those surfaces plus stronger compatibility assertions.
- The compatibility suite and targeted smoke checks are being treated as Task 3 verification rather than as Task 2 completion criteria.
- Generated `.codex/agents/*` artifacts were refreshed after the canonical agent prompt updates and are now in sync with the checked-in source prompts.

## Task 3: Verify the new vertical end to end and reconcile any drift

**Status:** Approved (final structural verification passed)

### Key Findings
- `bash tests/check-harness-compatibility.sh` passed after the final Task 3 fixes. The merge-quality portion now requires the generalized Tier 3 phrases `sample construction / model setup`, `specifications / solution concepts`, `data processing / derivation logic`, `results / headline outputs`, and `active domain-discipline artifacts`, and explicitly fails if stale data-only phrases such as `econometric specifications` or `removing data discipline artifacts` reappear.
- The same harness-compatibility run re-ran the embedded Codex agent generation checks (`python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py` and `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check`), and both passed.
- A targeted smoke check passed for repo-local discovery and routing semantics: `.agents/skills/theory-modeling` resolves to `../../skills/theory-modeling`, `planning-workflow` routes to `superRA:theory-modeling`, `using-superRA` lists the vertical in its manifest, and the `Model Inventory / Assumption Map` hard gate remains present in the theory-modeling planning reference.

### Notes
- Remaining risk: this pass was structural and workflow-facing. It did not run a live Claude/Codex end-to-end dispatch session against a toy modeling prompt in this turn.
- No generated artifacts needed reconciliation in this round because the only code changes were the merge-quality reference and the structural compatibility test.

### Verification Commands
```bash
bash tests/check-harness-compatibility.sh

python3 - <<'PY'
import os
from pathlib import Path

link = Path('.agents/skills/theory-modeling')
assert link.is_symlink(), '.agents/skills/theory-modeling must be a symlink'
assert os.readlink(link) == '../../skills/theory-modeling', os.readlink(link)
using_text = Path('skills/using-superRA/SKILL.md').read_text(encoding='utf-8')
planning_text = Path('skills/planning-workflow/SKILL.md').read_text(encoding='utf-8')
theory_planning_text = Path('skills/theory-modeling/references/planning.md').read_text(encoding='utf-8')
assert 'superRA:theory-modeling' in using_text, 'using-superRA manifest must mention theory-modeling'
assert '`superRA:theory-modeling`' in planning_text, 'planning-workflow routing must mention theory-modeling'
assert 'Model Inventory / Assumption Map' in theory_planning_text, 'theory-modeling planning reference must expose the hard gate'
print('theory-modeling discovery/routing smoke check passed')
PY
```

## Task 4: Tighten notation discipline — strengthen the ordering check and add an explicit Notation Conventions update mechanism

**Status:** Implemented

### Key Findings
- Rewrote the `Define` §`[BLOCKING]` *"Every symbol is defined before first use"* item in `skills/theory-modeling/SKILL.md` to require narrative-order introduction (a symbol may not appear in any derivation, equation, proof step, or verification before the paragraph/table that introduces it) and to name `PLAN.md`'s Notation Conventions table as the authoritative cross-task source for reused symbols.
- Added a new `[BLOCKING]` item in `Documentation and handoff` requiring implementers to inline-edit the Notation Conventions table BEFORE using any newly introduced symbol in algebra, committed atomically with the derivation work. Defers to `superRA:handoff-doc` for inline-edit mechanics rather than restating them.
- Mirrored the update mechanism in `skills/theory-modeling/references/planning.md` under Principles so the planning reference flags the Notation Conventions table as a living record maintained through implementation, not a one-time planning artifact.
- Added a new row to the Common Rationalizations table capturing the late-update failure mode: "I'll update the Notation Conventions table after the derivation is clean." → "Late notation updates mean the derivation was written against undefined symbols; update the table first, then derive."

### Final checklist wording
- `Define`: "Every symbol is introduced in narrative order before first use: primitives, choice variables, state variables, parameters, shocks, constraints, value objects, prices, and equilibrium conditions. A symbol may not appear in any derivation, equation, proof step, or verification before the paragraph or table that introduces it. For symbols reused across tasks, `PLAN.md`'s Notation Conventions table is the authoritative source - reuse its meaning rather than redefining the symbol locally."
- `Documentation and handoff` (new item): "When implementation introduces a symbol not yet in `PLAN.md`'s Notation Conventions table, update the table via inline-edit BEFORE using the symbol in algebra, and commit the `PLAN.md` edit atomically with the derivation work. Follow `superRA:handoff-doc` inline-edit discipline."
- `references/planning.md` Principles (new bullet): "Notation Conventions is a living record, not a one-time planning artifact - when implementation introduces a symbol not yet in the table, the implementer inline-edits the Notation Conventions table BEFORE using the symbol in algebra, and commits the `PLAN.md` edit atomically with the derivation work. The table remains the authoritative cross-task source of symbol meanings throughout the workflow."

### Notes
- Placement of the update-mechanism rule: put it in `Documentation and handoff` per dispatch steering — it is about maintaining `PLAN.md` Notation Conventions, not about whether a symbol is defined in-task. The existing `Define` ordering rule carries the pure narrative-order requirement; the handoff rule carries the cross-task PLAN.md editing obligation. The two compose without overlap.
- Minimum-net-diff preserved: only the one pre-existing `Define` bullet was rewritten, one bullet was inserted into `Documentation and handoff`, one row was appended to the Common Rationalizations table, and one bullet was inserted into `references/planning.md` Principles. No adjacent items, sections, or reviewer protocols were touched.
- Internal consistency: the new items reinforce the Iron Law ("NO DERIVATION WITHOUT DEFINED OBJECTS AND STATED ASSUMPTIONS") and sit alongside — without duplicating — the existing `Derive` item on reused-symbol consistency and the existing Common Rationalization on late assumption cleanup.

## Task 5: Restructure the `theory-modeling` SKILL body around intuition/interpretability as the through-line

**Status:** Implemented

### Key Findings
- Rewrote the Iron Law to `NO MANIPULATION WITHOUT DEFINED OBJECTS, INTERPRETABLE ASSUMPTIONS, AND STATED INTUITION`, with the three-line expansion on symbol meaning, plain-language assumption interpretation, and one-sentence reason per non-trivial move. Extended the "No exceptions" bullets to cover intuition, interpretability, and reason-per-move without dropping the original ones (hidden restrictions, mid-derivation renaming, primitive-to-endogenous shifts, memory of prior drafts, back-up-means-back-up).
- Replaced the `Define-Derive-Validate` section with a four-gate structure — **Objects & Notation → Assumptions → Derivations → Verification & Rendering** — organized around the reader's trust chain. Every load-bearing `[BLOCKING]` / `[ADVISORY]` item from the prior checklist was relocated verbatim to the appropriate gate; none reworded or weakened. Task 4's narrative-ordering rule stays in **Objects & Notation**, and Task 4's atomic `PLAN.md` Notation-Conventions-update rule stays in **Documentation and handoff** referencing `superRA:handoff-doc` for inline-edit mechanics.
- Added the five new `[BLOCKING]` items verbatim as specified: intuition-per-new-symbol under Objects & Notation; interpretability-per-assumption and synthesis-preferred under Assumptions; reason-per-move under Derivations; economic-interpretation of special/limiting cases under Verification & Rendering.
- Added four new Common Rationalizations rows for the intuition-failure modes: "The intuition is obvious." / "I'll add interpretation after the algebra is clean." / "Weaker assumptions are always safer." / "This assumption is technical, not economic." Each paired with a reality statement written in the same style as existing rows.
- Updated all internal SKILL.md references away from `Define-Derive-Validate`: the reviewer-protocol pointer now reads "Walk the four gates top to bottom", the section heading and intro paragraph use "The Four Gates", and the top-of-file summary names the four gates explicitly. The Stage-scoped discipline subsection and Key References block never named `Define-Derive-Validate` and required no edit.

### Final checklist structure (four gates)
- **Objects & Notation** (4 BLOCKING + 1 ADVISORY): narrative-order introduction + PLAN.md Notation Conventions authoritative; notation explicit/interpretable or conventional; intuition/mnemonic per new symbol (NEW); domains/units/signs; advisory literature-matching notation.
- **Assumptions** (3 BLOCKING): attached-to-primitives; plain-language interpretation per assumption (NEW); prefer synthesis over scattered weak restrictions with reviewer judgement margin (NEW).
- **Derivations** (8 BLOCKING + 1 ADVISORY): solution concept named; one move per step; state rule being used; rule + one-sentence reason per non-trivial step (NEW); case splits; comparative statics; reused-symbol consistency; existence/uniqueness arguments; advisory short equations.
- **Verification & Rendering** (7 BLOCKING + 1 ADVISORY): verification modes; numerical with explicit params; special/limiting cases vs intuition; special/limiting cases interpreted economically (NEW); assumption-map check-back; CAS transcription; rendering clarity; advisory multiple parameter sets.
- **Implementation standards** and **Documentation and handoff** blocks preserved as-is, including Task 4's atomic Notation-Conventions update rule.

### Notes
- Task scope was SKILL.md only; `references/planning.md` and `references/integration.md` still reference `Define-Derive-Validate` in two spots (planning.md line 155, integration.md line 10). Task 6 propagates the intuition/interpretability gates into those references and handles those renames.
- Sanity check — internal consistency: the new Iron Law names the three pillars (objects, interpretable assumptions, stated intuition); the four gates instantiate them; the Common Rationalizations table now covers the failure mode for each pillar. Task 4's notation/update rules compose cleanly under **Objects & Notation** and **Documentation and handoff** without overlap with the new intuition-per-symbol rule (Task 4: ordering + PLAN.md sync; new: intuition/mnemonic content of the entry).
- No regressions: every original load-bearing item is preserved verbatim under a gate; reviewer-verdict protocol unchanged (two verdicts, no halt-on-failure, re-review discipline).

## Task 6: Propagate intuition/interpretability gates into `references/planning.md` and touch up `references/integration.md`

**Status:** Implemented

### Key Findings
- `references/planning.md` Model Inventory template now captures interpretability at planning time: the **Assumptions** table has a new **Interpretation** column with a concrete example row ("risk aversion bounded" / preferences / ensures the value function is finite / "risk aversion bounded so the value function is finite") showing the target one-short-phrase shape for downstream implementers, and the **Notation Conventions** section explicitly requires the **Why this notation** column for non-conventional symbols while allowing conventional symbols (`r`, `beta`, `w`) to record "conventional" and skip further justification.
- Added one §Principles bullet, **"Interpretability is blocking; prefer synthesis"**, that points at `skills/theory-modeling/SKILL.md` §Assumptions for the full checklist rather than restating the four-gate `[BLOCKING]` items locally. Task 4's **"Notation Conventions is a living record, not a one-time planning artifact"** bullet is preserved verbatim.
- Added three bullets to §Common mistakes and three Never-items to §Red Flags — Hard Gate Protection that name the intuition-failure modes implementers must not defer: "notation interpretation TBD", "assumption interpretation later", and "scattered weak assumptions that could be synthesized".
- `references/integration.md` §"Derivation discipline preserved through refactoring" gained three new `[BLOCKING]` items that verify each new-symbol intuition, each assumption interpretation, and each derivation-step reason present in the original work survives refactor rather than being collapsed into opaque prose or code comments. Each new item points at the matching SKILL.md gate rather than duplicating its text.
- Cleaned up two lingering `Define-Derive-Validate` mentions: `references/planning.md` §"Handoff to Implementation" now names the new through-line (intuition + interpretability + stated reason running across the four gates Objects & Notation / Assumptions / Derivations / Verification & Rendering); `references/integration.md` opening paragraph's verdict-protocol pointer now references `theory-modeling/SKILL.md ## The Four Gates` instead of `# Define-Derive-Validate`. A `grep` across `skills/theory-modeling/` confirms no D-D-V references remain.

### Final wording
- **planning.md §Assumptions table header:** `| Assumption | Applies to | Role in the model | Interpretation | Notes |` with the concrete example row showing the target one-short-phrase shape.
- **planning.md §Notation Conventions prose (new):** "The **Why this notation** column is required for every non-conventional symbol — record the intuition or mnemonic that justifies the choice. Conventional symbols already fixed by the literature (for example `r` for an interest rate, `beta` for a discount factor, `w` for a wage) may leave the column as 'conventional' and skip further justification."
- **planning.md §Principles (new bullet):** "**Interpretability is blocking; prefer synthesis** — every assumption must carry a plain-language interpretation a researcher can defend at planning time, and when multiple scattered weak restrictions can be replaced by a single stronger interpretable primitive, prefer the synthesis. See `skills/theory-modeling/SKILL.md` §Assumptions for the full checklist; do not restate it here."
- **planning.md §Common mistakes (three new items):** "**'Notation interpretation TBD.'** A symbol without a stated intuition at planning time becomes a symbol nobody owns at implementation time." / "**'Assumption interpretation later.'** Assumption interpretations drafted after the algebra has been written are usually post-hoc rationalizations of whatever the derivation happened to need." / "**'Scattered weak assumptions that could be synthesized.'** A list of narrowly-scoped technical restrictions is harder to defend than a single stronger primitive with a clean economic reading; synthesize at planning time rather than after implementation."
- **planning.md §Red Flags — Never (three new items):** "Leave a new symbol's intuition or mnemonic as 'TBD' in the Notation Conventions table." / "Write an assumption row whose **Interpretation** column is blank or says 'later' / 'to be explained'." / "Enumerate multiple weak technical assumptions where a single stronger interpretable primitive is clearly available — synthesize instead."
- **integration.md §Derivation discipline preserved through refactoring (three new `[BLOCKING]` items):** "**Stated intuition for new symbols survives.** ..." / "**Assumption interpretations survive.** ..." / "**Per-step reasons survive.** ..." — each names the matching SKILL.md gate (Objects & Notation / Assumptions / Derivations) rather than duplicating its checklist.

### Notes
- Single source of truth preserved: the new references point at SKILL.md's four-gate checklist rather than restating its items. The Task 4 Principles bullet on the Notation Conventions living-record rule is untouched.
- Example discipline for the Interpretation column matches the researcher's target shape ("risk aversion bounded so the value function is finite") without prescribing specific economic content beyond the one concrete example row needed for downstream implementers.
- Minimum-net-diff preserved: only the two references were touched; both stale D-D-V mentions were replaced in place (no "Previously..." framing); no existing `[BLOCKING]` / `[ADVISORY]` items were reworded; no adjacent sections touched.
