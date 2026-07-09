---
title: "Objective/Guidance Split: Contract vs. Planning Dossier"
status: implemented
depends_on:  []
---

## Objective

Rewrite the `## Objective` / `## Planner Guidance` spec so planners produce short contract objectives and information-bearing guidance, replacing the include-list framing that currently yields long objectives and boilerplate guidance.

- Rewrite `skills/superplan/references/task-tree-design.md` §Writing Objectives and Planner Guidance around the user-approved design: `## Objective` is the short contract (goal — often a close paraphrase of the user's request — binding decisions/constraints, validation criteria) gated by the admission test *"a line belongs only if the reviewer should reject work that violates it"*; `## Planner Guidance` is the planner's information handoff (what planning learned that the implementer would otherwise re-derive), advisory in force, gated by *"a line belongs only if it is task-specific and was learned during planning, not assumed."* The two tests and the section functions are settled user decisions; draft wording in `## Planner Guidance` below may be polished but not weakened.
- Update the echo characterizations in `skills/task-tree/references/task-file-contract.md` (the `## Planner Guidance` anatomy bullet) and `skills/superplan/SKILL.md` (§Overview split line; self-review item 5) to match the new framing.
- Preserve unchanged: §Context Distillation mechanics (scoped subsections stay inside `## Objective`; point-over-copy), the implementer deviation protocol in `agents/implementer.md`, and reviewer treatment of guidance in `agents/reviewer.md`.
- Every added or changed line passes the `CLAUDE.md` §Teach the Protocol DRY + Necessity gate — a `[BLOCKING]` review item per that section.
- Validation: `grep -rn "Planner Guidance" skills/ agents/` shows no characterization contradicting the new framing; the two admission tests appear in full only in task-tree-design.md, elsewhere at most as one-line echoes or pointers.

## Planner Guidance

Design rationale and touchpoint map from the planning conversation (2026-07-09).

### Root causes the rewrite addresses

1. The current "Include:" six-item list (task-tree-design.md:9-15) reads as a completeness checklist — a planner following it literally writes six paragraphs; nothing states what to *exclude* or how long an objective should be.
2. `## Planner Guidance` is defined only negatively ("optional and advisory … may adapt or ignore"), giving it no positive job: filler fits the definition, while anything the planner cares about flees to the objective — producing both observed symptoms from one asymmetry.
3. No routing test exists for important-but-not-normative content (candidate files, data quirks, route rationale), which therefore lands in the objective by default.

### Approved replacement text

For task-tree-design.md §Writing Objectives and Planner Guidance, keeping the existing implementer's-working-context paragraph, the "Steps vs. subtasks vs. suggestions" block, and the no-bulk-migration paragraph in place:

> `## Objective` is the contract — with the user at planning time, with the implementer and reviewer at dispatch. It states what must be true when the task is done, and nothing else. Keep it short: a goal statement (often a close paraphrase of the user's request) plus a few binding bullets.
>
> A line belongs in the objective only if the reviewer should reject work that violates it:
> - The goal — what the task must produce or verify, naming the artifacts that define its scope.
> - User or methodology decisions that must be preserved.
> - Constraints — what to avoid and what to keep intact.
> - Validation criteria — what must be checked for the task to be complete.
>
> Binding conventions that live elsewhere enter as pointers, not prose — see §Context Distillation. When an objective outgrows a short paragraph plus its must-bullets, either the task needs splitting (§Splitting Tasks) or the excess is information, which belongs in `## Planner Guidance`.
>
> [existing working-context paragraph stays here]
>
> `## Planner Guidance` is the planner's information handoff: what planning discovered that the implementer would otherwise re-derive. Candidate files and their roles, data locations and quirks found during exploration, the suggested route and why, known dead ends. It is advisory in force — any route satisfying `## Objective` is acceptable — but its content is findings, not filler.
>
> A line belongs in guidance only if it is task-specific and was learned during planning rather than assumed. If it would hold for any task in this domain, or the implementer's standing context already carries it, delete it. Omit the section when nothing qualifies.

Note the old list's "Relevant conventions" and "Input/output expectations" items are deliberately dropped from the must-list: outputs fold into the goal bullet (scope-defining artifacts), input details route to guidance, conventions route via the pointer sentence. User confirmed outputs-in-objective / inputs-in-guidance.

### Echo edits

- `task-file-contract.md` `## Planner Guidance` bullet: "planner-owned, optional; the planner's information handoff — findings from planning plus suggested route. Advisory: implementers may deviate …" (rest of bullet unchanged).
- `superplan/SKILL.md` §Overview: "binding vs. suggested content" → "contract vs. planning findings".
- `superplan/SKILL.md` self-review item 5: "Binding deliverables and constraints in `## Objective`; advisory hints in `## Planner Guidance`." → "The contract in `## Objective`; planning findings and suggested route in `## Planner Guidance`."

### Touchpoints verified as no-change (grep "Planner Guidance", 2026-07-09)

- `agents/implementer.md:20-22`, `agents/reviewer.md:26` — deviation protocol; already compatible ("advisory in force" preserves it). Since role specs stay untouched, the generated `direct-mode-implementer.md` / `direct-mode-reviewer.md` / `.codex/agents/*.toml` need no regeneration — do not hand-edit them.
- `superplan/references/planning-review.md:14` — reviews against task-tree-design.md by pointer; picks up the rewrite automatically.
- `task-tree/references/commands.md:21` ("seeds an advisory `## Planner Guidance` section") — accurate for force; leave.
- `handoff-doc/SKILL.md:13` — deprecated redirect pointing at the rewritten section; leave.

## Results

Rewrote `## Writing Objectives and Planner Guidance` in [task-tree-design.md](../../../../skills/superplan/references/task-tree-design.md#L5-L26) verbatim from the approved replacement text above: `## Objective` is now the short contract gated by the "reviewer should reject work that violates it" test, with the "Include:" six-item list replaced by four must-bullets (goal, decisions, constraints, validation) and a pointer sentence routing conventions to §Context Distillation and overflow to `## Planner Guidance`. `## Planner Guidance` is redefined as the planner's information handoff gated by the "task-specific and learned during planning, not assumed" test, replacing the purely negative "optional and advisory" framing. The existing working-context paragraph, the "Steps vs. subtasks vs. suggestions" block, and the no-bulk-migration paragraph were kept in place unchanged, as instructed.

Updated the two echo characterizations exactly as specified:
- [task-file-contract.md:22](../../../../skills/task-tree/references/task-file-contract.md#L22) — `## Planner Guidance` anatomy bullet now reads "the planner's information handoff — findings from planning plus suggested route. Advisory: implementers may deviate …" (rest of bullet unchanged).
- [superplan/SKILL.md:16](../../../../skills/superplan/SKILL.md#L16) — "binding vs. suggested content" → "contract vs. planning findings".
- [superplan/SKILL.md:115](../../../../skills/superplan/SKILL.md#L115) — self-review item 5 → "The contract in `## Objective`; planning findings and suggested route in `## Planner Guidance`."

**Preserved unchanged, verified by diff:** §Context Distillation mechanics (no lines touched), `agents/implementer.md` deviation protocol (no lines touched), `agents/reviewer.md` guidance treatment (no lines touched). The generated `direct-mode-implementer.md` / `direct-mode-reviewer.md` / `.codex/agents/*.toml` were left untouched since their source role specs did not change.

**Validation:**
- `grep -rn "Planner Guidance" skills/ agents/` — reviewed every hit; none characterizes the objective as "binding deliverables" vs. guidance as merely "suggested/optional filler" any more. `grep -rn "binding vs\|suggested content\|binding deliverables" skills/ agents/` returns no hits, confirming the old asymmetric framing is fully retired from prose (test-file string literals in `task-tree/scripts/test_task_tree.py` and `test_dashboard.py` only check for the literal heading `## Planner Guidance` existing in generated output, not for characterization language, so they needed no changes).
- The two admission tests ("a line belongs in the objective only if the reviewer should reject work that violates it" / "a line belongs in guidance only if it is task-specific and was learned during planning rather than assumed") appear in full only in `task-tree-design.md`; every other touchpoint references the section by pointer or restates only the one-line echo specified above.
- `uv run --script skills/report-in-markdown/scripts/check_markdown.py skills/superplan/references/task-tree-design.md skills/superplan/SKILL.md skills/task-tree/references/task-file-contract.md` → all three report `clean`.
- DRY + Necessity gate: every added/changed line either restates settled user-approved wording verbatim (the replacement block) or is a one-line echo pointing at the authoritative section (the two echo edits) — no new independent characterization was introduced anywhere else.
