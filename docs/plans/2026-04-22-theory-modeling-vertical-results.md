# Theory-Modeling Vertical — Results

> Mirrors `PLAN.md` structure. Updated after each task with key findings.
> New agents: read `PLAN.md` for what to do, `RESULTS.md` for what was found.

**Last updated:** 2026-04-24 (Task 7 integration refactor review APPROVED; `Refactored` milestone re-approved on the cleaned-up workflow/utility skills)
**Status:** Tasks 1–7 APPROVED; `Refactored` milestone closed; Document phase deferred per 2026-04-24 PR-first decision

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

---

## Task 7: Make workflow and utility skills domain-neutral

### Key Findings
- Workflow skills (`planning-workflow`) and utility skills (`refactor-and-integrate`, `result-protection`, `result-protection/references/drift-test-quality.md`) plus the canonical reviewer role spec (`agents/reviewer.md`) had per-domain load directives ("For data-analysis ..., load `econ-data-analysis/references/X.md`. For theory/modeling ..., load `theory-modeling/references/Y.md`.") that duplicated each domain skill's own stage-load table. Per `CLAUDE.md` §"Teach the Protocol, Don't Prescribe Each Action" DRY/necessity tests, this is the most common drift surface when a vertical's reference layout changes.
- Cleanup: dropped the redundant load-directive lines and the parallel "If data analysis: ... If theory/modeling: ..." stop-here paragraphs in `planning-workflow` Phase 1; collapsed §Remember and §Self-Review per-domain branches into one domain-neutral instruction; routed the artifact-format note in Phase 3 and the step-cycle reference in Phase 4 through the active domain skill instead of naming `econ-data-analysis` directly. `refactor-and-integrate` and `result-protection` now state that the active domain skill's stage-load table is the routing source.
- Examples drawn from a particular domain (e.g., the Phase 4 step shapes naming "raw holdings data" or "Euler equation"; the Self-Review item-1 inventory examples; the §Remember bullet's "data: row counts" / "theory: notation" examples once collapsed into the active-domain pointer's parenthetical) were retained where they illustrate a domain-neutral concept.
- Trigger column of the Phase 1 Currently-implemented-verticals table retained — it is routing input, not a redundant load directive. The "Planning reference" column was dropped because it restated the domain skill's own load map.
- `using-superRA/SKILL.md` Skill Inventory and Discovery rows for both verticals retained (these are discovery surfaces, not duplicated load directives).

### Verification
- `bash tests/check-harness-compatibility.sh`: PASS (42 / 42; 0 failed). Updated the assertion at `tests/check-harness-compatibility.sh:69` from "refactor-and-integrate must POINT TO theory-modeling integration guidance" to "refactor-and-integrate must STAY DOMAIN-NEUTRAL" (negative assertions on both `theory-modeling/references/integration.md` and `econ-data-analysis/references/integration.md` substrings).
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` regenerated `.codex/agents/superra_reviewer.toml` and `skills/using-superRA/references/direct-mode-reviewer.md` from the updated `agents/reviewer.md`. The Codex agent generation test passes (`Ran 6 tests in 0.302s; OK`).
- `grep -rn -E "(econ-data-analysis|theory-modeling)/references/" skills/{planning,implementation,integration}-workflow/ skills/agent-orchestration/ skills/refactor-and-integrate/ skills/result-protection/ skills/handoff-doc/ skills/semantic-merge/ skills/using-superRA/SKILL.md agents/`: no surviving per-domain `references/X.md` load directives in workflow/utility skills or canonical role specs.

### Notes
- Minimum net diff: only the load-directive lines were touched in each file; the surrounding workflow choreography, review protocol, and gated checklists are untouched.
- Phase B integration re-run pending: the project-level `Refactored` milestone was rolled back per the 2026-04-24 User Decisions Log entry so the integration reviewer walks the cleaned-up workflow/utility skills against current `main` before merge.

---

## Task 8: Notation & assumption necessity gate, RESULTS.md ledger, and user-gated canonical promotion

### Key Findings
- **Two-test gate (necessity + non-duplication) added to `theory-modeling/SKILL.md` §Objects & Notation.** Every new symbol must earn its place by both tests, walked symbol by symbol. Failing symbols are removed or replaced. "Defined locally", "algebraically useful", or "introduced at first use" do not satisfy the gate. The walk and outcomes are recorded in the per-task **Notation & Assumptions Ledger**.
- **Same two-test discipline propagated to `theory-modeling/SKILL.md` §Assumptions** as a new `[BLOCKING]` composing with the existing synthesis rule (assumptions that pass synthesis can still fail necessity).
- **Equations and named statements covered at review time without per-equation ledger overhead.** New `[BLOCKING]` in §Derivations notes that lemmas, propositions, definitions, corollaries, and derivation steps are reviewed under the same lens; enforcement is via the existing one-move-per-step + reason-per-move items.
- **Canonical / working-record split inverted in `theory-modeling/SKILL.md` §Documentation and handoff.** The prior Task 4 rule that implementers inline-edit `PLAN.md`'s Notation Conventions BEFORE using a symbol is replaced by two new `[BLOCKING]` items: (a) per-task **Notation & Assumptions Ledger** in `RESULTS.md` (every new symbol/assumption: name, meaning, why-earns-its-place, near-duplicates rejected; tasks introducing nothing record "None"); (b) `PLAN.md` Notation Conventions table is canonical and user-gated — promotion only with researcher confirmation.
- **Common Rationalizations table extended** with one rewrite (the Task 4 "late update" row now points at the ledger) plus three new rows: "It's defined locally and used in the algebra"; "It came from the derivation note, so it's already vetted"; "It only abbreviates this one expression."
- **`references/planning.md` §Principles rewritten** so the "living record / implementer inline-edits" principle becomes "canonical and user-gated, not implementer-editable", pointing at SKILL.md §Documentation and handoff.
- **`references/integration.md` extended** with two new `[BLOCKING]` items under "Derivation discipline preserved through refactoring": (a) per-task ledger entries survive refactor (not silently collapsed); (b) canonical Notation Conventions table contains only user-confirmed promotions (orphan entries without a `## Decisions` log entry are REVISE).
- **`handoff-doc/references/results-anatomy.md` per-task template extended** with a `### Notation & Assumptions Ledger` block (mandatory for theory-modeling tasks; records "None" when empty). Schema slot defined here; gate semantics owned by `theory-modeling/SKILL.md`.
- **Promotion stop point wired in `implementation-workflow/SKILL.md` Step 4.** Before presenting the completion menu, when the active domain is theory-modeling, the main agent scans each task's ledger for entries not in the canonical table and surfaces them via `AskUserQuestion` with a per-candidate Promote / Keep-in-ledger / Remove choice. Promotions are inline-edited atomically with a `## Decisions` log entry. Skipped when domain is not theory-modeling or every ledger says "None." Ownership note added: gate semantics stay in `theory-modeling/SKILL.md` — workflow does not restate them.
- **Reviewer-side discipline left implicit (DRY).** `agents/reviewer.md` already requires "walk the active domain skill's gated checklist top to bottom"; the new SKILL.md `[BLOCKING]` items in §Objects & Notation, §Assumptions, and §Documentation and handoff are covered by that walk. No reviewer.md edit, no Codex artifact regeneration. The PLAN.md Task 8 step 10 was rewritten to record this DRY decision.

### Verification
- `bash tests/check-harness-compatibility.sh`: PASS (42 / 42; 0 failed). Codex agent generation: 6/6 PASS. All generated agent files and direct-mode role references up to date — no regenerations needed because `agents/reviewer.md` was not touched (per the DRY decision).
- `grep -rn "inline-edit.*Notation\|Notation.*inline-edit\|update the table.*BEFORE" skills/ agents/` (excluding PLAN.md / RESULTS.md historical record): no surviving stale references to the superseded Task 4 inline-edit rule. Task 4's task-block description in PLAN.md and its corresponding RESULTS.md section retain the historical record per repo convention; the 2026-04-25 Decisions log explicitly records the supersession.
- Cross-reference walk: SKILL.md §Objects & Notation (line 110) → §Documentation and handoff (lines 168–169); §Assumptions (line 124) → ledger; references/planning.md (line 101) → SKILL.md §Documentation and handoff; references/integration.md (lines 42–43) → SKILL.md §Documentation and handoff; implementation-workflow Step 4 (line 135) → theory-modeling/SKILL.md §Documentation and handoff; handoff-doc/results-anatomy.md (line 79) → theory-modeling/SKILL.md §Objects & Notation and §Documentation and handoff. All pointers resolve; no orphan references.

### Notes
- **Reconciliation of pre-Task-8 brainstorming drafts.** The 2026-04-25 conversation produced uncommitted edits to `theory-modeling/SKILL.md` and `references/planning.md` before the plan-update workflow was run. Task 8 implementation refined those drafts in place: kept the ledger format, the user-gated table framing, the rewritten "late update" Common Rationalization, the three new rows, and the planning.md principle rewrite; narrowed the §Objects & Notation two-test item by dropping the arbitrary "defining line plus one downstream use" threshold and the unilateral extension to "any new equation or named statement"; properly localized assumption discipline to §Assumptions and equation/statement discipline to §Derivations.
- **Scope split for the necessity test.** Symbols and assumptions get full two-test discipline + ledger entries; equations, lemmas, propositions, definitions, corollaries, and derivation steps get the same lens at review but no per-equation ledger entry. This keeps the auditable trail tight where it matters (named symbols and stated assumptions are reusable artifacts the reader carries through the proof) without imposing per-equation bookkeeping (every proof has many equations; per-equation ledger entries would dwarf the proof itself).
- **Task 4 supersession explicit, not silent.** The Decisions log §2026-04-25 entry records that Task 4's "implementer inline-edits Notation Conventions BEFORE using the symbol" rule is replaced by the user-gated model; Task 4's APPROVED status is preserved per repo convention (the task's other deliverables — narrative-order rule, atomic-update mechanism conceptually — remain valid; only the inline-edit timing is inverted).
- **No reviewer.md changes.** Step 10 of the original Task 8 spec proposed reviewer-side ledger-walk text, but the existing reviewer protocol "walk the active domain skill's gated checklist" already covers the new `[BLOCKING]` items via the SKILL.md gates. Adding reviewer.md text would duplicate per CLAUDE.md DRY discipline.
- **Phase B integration re-run pending.** Project-level `Refactored` milestone was rolled back by the 2026-04-25 Decisions log entry; integration reviewer walks the new gate / ledger / promotion model against `main` before merge.

### Notation & Assumptions Ledger
None. Task 8 introduces no mathematical symbols or model assumptions (it is meta-work on the skill body itself).

## Task 9: Restructure §Four Gates as artifact-first; add recursive signposting and falsification tests

**Status:** IMPLEMENTED

### Key Findings
- **§Four Gates inverted to artifact-first** in `skills/theory-modeling/SKILL.md`. Each gate now leads with the artifact the implementer produces (per-symbol ledger entry / per-assumption ledger entry / proof body / verification record + rendered output) and a checklist of quality items walked while producing it. Documentation is built into the artifact definitions, not a separate phase.
- **§Reviewer verdict protocol restructured** to "verify the artifact exists, then walk the checklist against it." Two new falsification tests added at the protocol level: **substitution test** (per ledger entry — if "What the name carries" still reads as true with a hypothetical extra symbol substituted in, the justification is structurally vacuous → BLOCKING) and **proof-deletion test** (per Meaning slot — if deleting the surrounding proof makes the slot vacuous, it was a usage description, not a meaning → BLOCKING).
- **Gate 1 Objects & Notation rewritten** with per-symbol ledger entry as the artifact. 7-slot template (Symbol / Meaning / First-use site / Reuse sites / Inline alternative / What the name carries / Nearest existing / Why this name); inline guidance for the Meaning slot via the type-space + denotation + origin recipe; anti-pattern table with the canonical "used to verify..." bad example. Checklist enforces entry-before-use, no bundling (one entry per object; indexed families count as one), falsifiable "none in scope" claims, concrete content for one-site symbols.
- **Gate 2 Assumptions rewritten** with parallel per-assumption ledger entry structure. Slot template (Statement / Interpretation / Attached to / First-bite site / Reuse / Without-this-assumption / What it carries / Nearest existing / Why this way); checklist requires concrete content in necessity / non-duplication slots and a named conclusion that changes if the assumption is removed.
- **Gate 3 Derivations reframed** with the proof / derivation body declared as the artifact. All existing checklist items preserved. New `[BLOCKING]` recursive roadmap signposting item added — every derivation opens with a one-sentence strategy; sub-arguments of non-trivial length carry their own opening signpost; transition prose names where we are in the parent plan; falsification test "can a reader entering mid-proof recover the local goal from surrounding signposts?". (Note: this `[BLOCKING]` was subsequently relocated to `references/integration.md` Section A by Task 12, with a minimal goal-statement floor remaining in Gate 3.)
- **Gate 4 Verification & Rendering reframed** with (verification record + rendered output) as the artifacts. All existing checklist items preserved.
- **§Documentation and handoff shrunk to cross-cutting items only** — `RESULTS.md` update in place, `PLAN.md` user-gating, definitions alongside math, `report-in-markdown` reuse, consistent notation across rendered math / prose / code, no dangling TODOs. The ledger schema migrated into Gates 1–2 rather than living here as paraphrase.
- **Common Rationalizations table extended** with three new rows for the diagnosed failure modes: "It's a local proof-only object." → locality is scope, not content; bundling dodges per-symbol scrutiny by reframing the unit of evaluation. "Each is used in the proof step that uses it." → restatement of the gate, not evidence; walk the slots. "The meaning is clear from how it's used." → usage is not meaning; apply the type / denotation / origin recipe.

### Verification
- Self-walk of the restructured §Four Gates against the Iron Law (defined objects, interpretable assumptions, stated intuition) — every gate now has an explicit artifact tying back to one of the three Iron Law clauses.
- Reviewer dispatch (commit `315d53d review: Task 9 APPROVED`) confirmed internal consistency with the four-gate structure and with Task 8's per-task ledger requirement (now reorganized as the artifact for Gates 1–2 rather than a paraphrase living in §Documentation).
- No `agents/reviewer.md` or Codex artifact regeneration needed — no canonical role text changed in this task.

### Notes
- **Diagnosed failure mode the restructure addresses.** A draft-review failure produced a ledger entry bundling five distinct symbols ($\mathbf{c}_k$, $\mathbf{v}$, $m_D$, $m_B$, $\Xi_k$) under a single shared justification ("local proof-only objects used to verify $h_k = m_D \beta_{E,k}$") with a Meaning slot describing usage rather than what the object is. Five structural reasons the prior gate failed: paraphrastic restatement of gate text, post-hoc documentation ordering, gate-as-threshold rather than required artifacts, no reviewer falsification handle, silent allowance of bundled entries. The artifact-first restructure makes paraphrasing structurally impossible: Reuse sites cite refs (not claims); Inline alternative shows the actual substituted expression (not a description); What the name carries demands concrete interpretive payload; Nearest existing is a falsifiable claim.
- **Task 8 design preserved, reorganized.** The four-part Task 8 design (two-test gate, per-task ledger, user-gated canonical table, Step 4 promotion stop point) is intact. The ledger requirement now lives inside Gate 1 / Gate 2 as the artifact rather than in §Documentation as paraphrase.
- **Gate 3 recursive-signposting `[BLOCKING]` superseded by Task 12.** Per the 2026-04-30 Decisions log, the full recursive-roadmap-signposting item added here was relocated to `references/integration.md` Section A as ex-post rewriting discipline; Gate 3 retains a minimal "top-level proof goal stated" floor and gains a citation-floor item. Task 9's restructure is preserved; only the cut line between creation-time and integration-time recursive signposting moved.

### Notation & Assumptions Ledger
None. Task 9 introduces no mathematical symbols or model assumptions (it is meta-work on the skill body itself).

## Task 10: Rewrite `theory-modeling/references/integration.md` as the rewriting reference

**Status:** IMPLEMENTED

### Key Findings

`skills/theory-modeling/references/integration.md` rewritten from a thin
55-line refactor-survival checklist into the canonical rewriting reference
(459 lines). Frontmatter advertises the file as the rewriting playbook
(structural rewriting + cross-document coherence + reader-perspective
discipline) and the header carries the halt-and-redispatch scope clause.
Body has four sections in **principle → identification protocol →
checklist** layered shape:

- **Section A — Objective-first structural rewriting** (lines 40–133).
  Principle: forward-written, backward-built; recursive at every level
  (top-level strategy + sub-argument signposts + transition prose).
  Pointer to `references/objective-first.md` for the worked example
  (Task 11 will populate). Identification protocol walks the existing
  derivation top-to-bottom against five questions; pattern-watch list
  enumerates the local-detour-first / deferred-goal anti-patterns.
  Four `[BLOCKING]` items + onion-style `[ADVISORY]`. Differentiation
  paragraph at lines 66–72 frames Section A as the ex-post
  detection-and-rewrite layer to distinguish from Gate 3's creation-time
  audit floor.
- **Section B — Per-step local obviousness** (lines 137–224). Principle
  pins the half-page-mask test ("**obvious**, not merely derivable") and
  enumerates the four-fix taxonomy (define inline / restate the
  assumption / cite-with-form-recall / split-the-step). Identification
  protocol teaches the mask test as a procedure on every displayed
  equation and routes the failure to one of four named types. Four
  `[BLOCKING]` items + inline-restatement `[ADVISORY]`.
- **Section C — Cross-document coherence** (lines 228–345). Principle
  names three coherence layers (notation / prior results / prose
  integration). Required reads block (lines 254–260) points at
  `references/audience-discipline-modeling.md` and
  `references/audience-discipline-writing.md` as bare pointers (no
  content sketch — the files are authoritative). Three-step
  identification protocol (notation pre-flight against `PLAN.md`
  Notation Conventions and prior-task ledgers; prior-result pre-flight
  by name and by content match; prose-integration pass). Five
  `[BLOCKING]` items including reader-perspective discipline against
  the two audience-discipline files and document-code consistency.
- **Section D — Discipline preserved through refactoring** (lines
  349–448). Pre-Task-10 content preserved with principle and
  identification-protocol intros added. The two Task 8 `[BLOCKING]`
  items (per-task ledger survival; canonical-table user-gating) carry
  cross-references back to Sections A–C as the rewriting-time
  companions. Utility reuse + documented-deviations sub-block preserved.

Reviewer verdict protocol (lines 452–459) walks A → D in order alongside
`refactor-and-integrate/SKILL.md` and reiterates the halt-and-redispatch
discipline.

### Notes

- **Halt-and-redispatch citation.** PLAN spec named
  `using-superRA/SKILL.md:92` as the citation target for the
  `Stage: sync` halt-and-redispatch shape. Verification at implementation
  time showed line 92 carries only "`Stage: sync` is branch-level," not
  the halt-and-redispatch text. The closest authoritative source for the
  shape (broader codebase-coherence work is "out of scope for this skill"
  in `Stage: sync`) is `semantic-merge/SKILL.md:80`. Replaced the
  line-numbered cite with a content cite to `semantic-merge/SKILL.md`
  §"out of scope".
- **Pre-Task-10 head sections folded into A–D.** The committed file's
  "Consistency with the model and codebase" head section (no-duplicate
  notation, assumption-map consistency, statement-result consistency,
  document-code consistency) is folded: notation-duplication into
  Section C's notation pre-flight; document-code consistency into
  Section C's checklist as a `[BLOCKING]`; assumption-map and
  statement-result coherence are now covered jointly by Section C's
  prose-integration / prior-result pre-flight and Section D's assumption
  / per-step-reason survival items. No content was lost.
- **Required-reads pointer trim.** First draft characterized each
  audience-discipline file in one line ("proof-narrative perspective; the
  two reader contexts; mid-proof self-narration vs. proof roadmap; …").
  Per the dispatch's anti-wrapper guidance and CLAUDE.md §"Teach the
  Protocol" two-test, the sketch was trimmed to bare pointers — the
  files are authoritative; routing requires only the file names plus a
  one-noun orientation ("proof-narrative prose" vs "paper-body prose
  generally").
- **Recursive-signposting overlap with Gate 3 (interim).** Section A's
  recursive-sub-argument-signposts `[BLOCKING]` and Gate 3's full
  recursive-roadmap-signposting `[BLOCKING]` are textually similar but
  framed differently (Section A is ex-post detection-and-rewrite; Gate 3
  is creation-time audit floor). The differentiation paragraph at
  Section A lines 66–72 makes the distinction explicit. This overlap is
  expected through Task 12 — Task 12 cuts Gate 3 down to a minimal
  goal-statement floor and leaves the full recursive discipline in
  Section A.
- **Untracked audience-discipline files.** Per dispatch instruction,
  `audience-discipline-modeling.md` and `audience-discipline-writing.md`
  are referenced by relative path but **not** `git add`-ed in this task.
  Task 13 owns tracking; this task only wires them into Section C.
- **No Section E or further sections.** Per the spec the file ends with
  Section D + reviewer verdict protocol; the four-section design is
  exhaustive for this stage's scope.

### Open caveats

- The line-numbered citation `implementation-workflow/SKILL.md:135` is
  used twice (Section C identification protocol and checklist; Section D
  canonical-table item). Verified at implementation time that line 135
  carries the "Domain pre-step (theory-modeling only): notation/assumption
  promotion" prose. The cite will need re-checking if
  `implementation-workflow/SKILL.md` is reorganized.
- Once Task 12 lands, the Section A "Differentiation from creation-time
  discipline" paragraph (lines 66–72) should be sanity-read once more —
  Gate 3's reduced wording may make the differentiation paragraph
  partly redundant. Not removing it preemptively because the paragraph
  also carries the recursive-level framing that Gate 3 will no longer
  carry.

### Notation & Assumptions Ledger

None. Task 10 is meta-work on the rewriting reference; no mathematical
symbols or model assumptions are introduced.

## Task 11: Add `theory-modeling/references/objective-first.md` — worked example + identification training

**Status:** IMPLEMENTED

### Key Findings

`skills/theory-modeling/references/objective-first.md` created as a new
single-purpose sibling reference loaded on demand from
`references/integration.md` Section A. The file is teaching material with
no `[BLOCKING]` checklist — Section A of `integration.md` is cross-cited
in the frontmatter blockquote as the home of the gates.

Four sections in the planned three-layer shape (principle + worked example
in two parts + identification training):

- **§Principle.** One short paragraph: start from the object the proof
  needs; expand only required terms; forward writing runs along a
  backward dependency walk; the good pattern keeps the proof linear
  (target object → needed derivative → structural cancellation →
  canonical column → final substitution).
- **§Worked bad pattern.** The user's `z_j`-first walkthrough rendered
  verbatim. Target FOC stated, then the local placeholder
  `z_j \equiv [\boldsymbol{\beta}_P^{\intercal}\mathbf e_E]_{US,j}`
  introduced before its purpose is named; annotated with five
  reader-experience failure points (reader does not know why $z_j$
  matters; notation lives for one detour; objective hidden;
  cancellation looks coincidental; non-canonical notation risked).
  Closes with the hidden-logic dependency chain $\dot{\boldsymbol{\Sigma}}
  \to \dot{\boldsymbol{\sigma}}_R \to \boldsymbol{\beta}_{P,E}$ that the
  bad ordering walks in writing the wrong way around.
- **§Worked good pattern.** The user's objective-first rewrite rendered
  verbatim. Starts from $\boldsymbol{\Sigma} = \boldsymbol{\sigma}_R
  \boldsymbol{\sigma}_R^{\intercal}$, differentiates, identifies the
  canonical return-loading column $\boldsymbol{\sigma}_R =
  \boldsymbol{\beta}_P^{\intercal}\mathbf G$, applies the symmetry
  cancellation $\dot{\boldsymbol{\beta}}_P^{\intercal}\mathbf G\mathbf e_g
  = \mathbf 0$, then solves $\boldsymbol{\beta}_{P,E}$ via law of one
  price + the $\hat E$ column of the return-loading equation +
  state-loading market clearing, ending at
  $\boldsymbol{\beta}_{P,E} = \tfrac{1}{2}(\bar P_s,\bar P_f,\bar P_s,\bar P_f)^{\intercal}$.
  Closing paragraph names the visible dependency walk in prose so the
  reader sees why each equation appeared.
- **§Identification training.** Three short held-out snippets, each
  followed by a target-object / backward-walk / anti-pattern diagnosis:
  - **Snippet 1** — Euler equation derivation that opens by defining
    $\eta \equiv u'(c_1)/u'(c_0)$. Anti-pattern: **local placeholder
    before target named**.
  - **Snippet 2** — comparative-static for $\mathrm dp/\mathrm d\theta$
    under market clearing, opening with "We compute." Anti-pattern:
    **deferred goal — target not named before the first displayed
    equation**.
  - **Snippet 3** — Proposition 2 proof showing concavity then
    differentiability of a value function, with no prose between the
    two algebra blocks. Anti-pattern: **signpost-less sub-arguments**.

### Notes

- **Math rendering convention.** `$$...$$` for display math and
  `$...$` for inline math, matching the convention in
  `references/integration.md` (e.g., the in-text `$\mathbf{c}_k$`
  recall example at line 200 and the symbol references throughout
  Sections A–D). No align environments were needed; the user's worked
  example breaks naturally into separate displays.
- **Verbatim rendering.** The user's bad-pattern annotations and
  good-pattern walkthrough are rendered without paraphrase — the
  five-bullet "why this is bad" list, the structural-cancellation
  prose, the three-step procedure for solving $\boldsymbol{\beta}_{P,E}$
  (law of one price → return-loading equation → state-loading market
  clearing), and the closing "linear in the reader's experience" line
  all preserved as written. The only added prose is one closing
  sentence after the §Worked good pattern that surfaces the dependency
  walk in the form requested by the PLAN step ("the proof needs
  $\dot{\boldsymbol{\Sigma}}\bar{\mathbf Q}$ → requires $\dot{\boldsymbol{\Sigma}}$
  → requires $\dot{\boldsymbol{\sigma}}_R$ → requires $\boldsymbol{\beta}_{P,E}$").
- **No checklist.** Per the dispatch's anti-checklist guidance and the
  2026-04-30 Decisions log, the file ends with §Identification training
  and does not contain `[BLOCKING]` / `[ADVISORY]` items. The
  frontmatter blockquote points readers to Section A of
  `references/integration.md` for the gates.
- **Frontmatter shape.** Followed the convention used by sibling
  references (`integration.md`, `planning.md`,
  `integrate-drift-tests.md`): a markdown blockquote intro paragraph
  carrying load conditions and scope, no YAML frontmatter.
- **Identification-training snippet length.** Each snippet is one
  blockquote-style passage plus a three-bullet diagnosis. Length was
  chosen to mirror the size of typical proof passages an integration
  reviewer encounters; longer snippets would push the file toward
  cataloguing failure modes rather than exercising the diagnostic move.
- **Internal-consistency check against `integration.md` Section A.** The
  three anti-patterns named in Snippet 1–3 (local placeholder,
  deferred goal, signpost-less sub-argument) match the three
  pattern-watch items in Section A's identification protocol
  (`integration.md` lines 100–106) without restating its checklist
  items. The §Principle paragraph here is consistent with Section A's
  principle prose but tighter — Section A carries the recursive
  framing in detail; this file's principle is the floor restatement
  the worked example and drills require.

### Open caveats

- **Gate 3 differentiation paragraph (Task 12 dependency).**
  `integration.md` Section A lines 66–72 carry a "Differentiation from
  creation-time discipline" paragraph distinguishing Section A's
  ex-post detection-and-rewrite framing from Gate 3's creation-time
  audit floor. This file's identification-training Snippet 2 fix
  ("one sentence before the differentiation step") and Snippet 3 fix
  ("one sentence at the head of each sub-argument") both describe the
  recursive-signposting discipline as Section A owns it. Once Task 12
  cuts Gate 3 to the minimal goal-statement floor, the snippet
  diagnoses and fixes here remain valid (they reference Section A's
  framing, not Gate 3's), but Snippet 3's fix wording could be
  re-checked once Task 12 lands to confirm it is consistent with the
  reduced Gate 3 phrasing.

### Notation & Assumptions Ledger

None. The file renders the user's `\dot{\boldsymbol{\Sigma}}\bar{\mathbf Q}`
walkthrough verbatim as illustrative content; symbols appear inside
teaching material rather than as task-introduced model objects.

## Task 12: Sharpen Gate 3 in `theory-modeling/SKILL.md` and update the stage-scoped reference table

**Status:** IMPLEMENTED

### Key Findings

Three surgical edits to `skills/theory-modeling/SKILL.md`:

1. **Gate 3 minimal goal-statement floor** (line 249, replacing pre-edit line 246). Final wording:

   > `[BLOCKING]` Top-level proof goal stated in one sentence before the first displayed equation. Derivations whose first move is algebra without a stated target are REVISE. (Full reader-facing recursive signposting — sub-arguments at every level, transition prose — lives in `references/integration.md` Section A as ex-post rewriting discipline.)

   The full recursive discipline (sub-arguments at every level, transition prose, "reader entering at any point can recover local goal" test) is now owned solely by `references/integration.md` Section A.

2. **Gate 3 citation-floor `[BLOCKING]`** (line 250, new item immediately after the goal-statement item). Final wording:

   > `[BLOCKING]` When a derivation step depends on a previously established equation, lemma, or proposition, the dependency is cited by name or equation number. Asserted equations with no path to a named source are REVISE. (Cite-with-operative-form-recall for distant sources is owned by `references/integration.md` Section B.)

   Pointer-only to Section B; no paraphrase of the operative-form-recall discipline.

3. **Stage-scoped reference table expanded** (lines 29–36, was 29–33). The integration stage now occupies four rows pointing at `references/integration.md`, `references/objective-first.md`, `references/audience-discipline-modeling.md`, and `references/audience-discipline-writing.md`. Existing two-column format preserved.

### Notes

- **Single surviving authoritative location for recursive signposting.** `grep -rn "Recursive roadmap signposting\|recursive roadmap signposting" skills/ agents/` returns zero matches. The lowercase partial phrase "recursive signposting" appears in `theory-modeling/SKILL.md:249` only as a pointer to Section A, and in `references/integration.md` at its authoritative locations (Section A body lines 55–72 + Section D self-reference at line 413).
- **Audit chain unchanged for messy exploration output.** The Gate 3 creation-time correctness items remain intact: active solution concept named, one-move-per-step, rule labels, rule + reason, case splits, comparative statics, reused-symbol meaning, existence/uniqueness arguments, necessity lens, equation-length advisory. The cut removed the *reader-facing* full-recursion item; it did not touch the *correctness* items.
- **Cross-document consistency with `integration.md`.** Section A's "Differentiation from creation-time discipline" paragraph (lines 66–72) describes Gate 3 as "enforces stating the top-level proof goal at creation time as an audit floor" — consistent with the post-edit Gate 3 goal-statement item. No follow-up edit to `integration.md` is required.
- **Audience-discipline file tracking.** The two `audience-discipline-*.md` files referenced in the new table rows are still untracked in git as of this commit; Task 13 owns `git add` for them. Listing them in the SKILL.md table is intent-only — the table is a map, not an authority over file presence.

### Notation & Assumptions Ledger

None — meta-work on Gate 3 wording and the stage-scoped reference table; no new symbols or assumptions introduced.

## Task 13: Wire per-task `Stage: integration` note + inventory updates

**Status:** IMPLEMENTED

### Key Findings

Six surgical edits, all minimum-net-diff and pointer-only where applicable:

1. **`skills/implementation-workflow/SKILL.md` line 99** — added one sentence between Task Execution Step 4 and the direct-mode note: "When a downstream task would inherit a structurally messy or notation-incoherent derivation from a just-APPROVED task, the orchestrator may dispatch `Stage: integration` against that single task before advancing. This uses existing stage flexibility — no new mechanism." No new branch, no new gate, no expanded protocol — the orchestrator was already free to do this; the line just advertises that fact.

2. **`skills/theory-modeling/references/audience-discipline-modeling.md` and `audience-discipline-writing.md`** — both files staged via `git add`. No content edits; the user authored them and Tasks 10 and 12 already wired them in via `integration.md` Section C and `theory-modeling/SKILL.md` stage table.

3. **`skills/CATEGORIES.md` line 25** (theory-modeling row, flagship-discipline column) — extended to mention "task-level rewriting and document-internal coherence (objective-first structural rewriting, per-step local obviousness, notation/prior-result reuse, reader-perspective discipline) at integration time" and listed the full reference set including `objective-first.md`, `audience-discipline-modeling.md`, `audience-discipline-writing.md` alongside the pre-existing three.

4. **`README.md` line 67** (Domain Skills table, theory-modeling row) — appended one short clause: "Adds a task-level rewriting/coherence reference set (objective-first, audience-discipline) surfaced at `Stage: integration`." Full discipline remains owned by the skill body.

5. **`CLAUDE.md` line 66** (Ownership Boundaries table, Domain-discipline row) — extended the Concern cell with a parenthetical-style clause naming both creation-time four-gate discipline and the task-level rewriting/coherence concern under `theory-modeling`. Owner cell unchanged.

6. **`tests/check-harness-compatibility.sh`** — ran clean: 42/42 PASS, identical to the post-Task-12 baseline. No assertion needed updating; the harness checks target discovery/wiring invariants (skill files exist, manifests reference theory-modeling, refactor-and-integrate stays domain-neutral, `.agents/skills/` symlinks present, frontmatter parses, generated artifacts in sync) — none of which are affected by inventory wording.

### Cross-reference verification (grep audit)

- `audience-discipline-modeling.md`: cited at `integration.md:259` and `integration.md:335` (Task 10 Section C), `SKILL.md:35` (Task 12 stage table), `CATEGORIES.md:25` (Task 13).
- `audience-discipline-writing.md`: cited at `integration.md:260` and `integration.md:335` (Task 10 Section C), `SKILL.md:36` (Task 12 stage table), `CATEGORIES.md:25` (Task 13).
- `objective-first.md`: cited at `integration.md:63` and `integration.md:94` (Task 10 Section A), `SKILL.md:34` (Task 12 stage table), `CATEGORIES.md:25` and `README.md:67` and `CLAUDE.md:66` (Task 13 by name).

All three references are now triangulated across discipline (`integration.md`), routing (`SKILL.md` stage table), and inventory (`CATEGORIES.md`/`README.md`/`CLAUDE.md`).

### Notes

- The Decisions log entry of 2026-04-30 explicitly framed the `Stage: integration` dispatch as orchestrator flexibility, not a new mechanism. The implementation-workflow note is therefore single-sentence pointer language; expanding it into a procedural branch would re-introduce the very over-specification the "Teach the Protocol, Don't Prescribe Each Action" gate forbids.
- The CLAUDE.md ownership table's existing structure groups both domain skills (`econ-data-analysis`, `theory-modeling`) into a single "Domain discipline" row. The minimum-net-diff way to surface the rewriting/coherence concern under `theory-modeling` is an inline parenthetical inside the existing Concern cell rather than fragmenting the row; the owner remains `theory-modeling`, which is what the task spec required.
- README.md was kept short by name-checking only the reference families ("objective-first, audience-discipline") rather than listing each file individually; full file paths live in `CATEGORIES.md` and the SKILL.md stage table.

### Notation & Assumptions Ledger

None — wiring and inventory work; no new symbols or assumptions introduced.
