---
title: "Retire the domain planning approval gates in favor of frontier questions"
status: approved
depends_on: [01-mechanism]
---

## Objective

Replace every PLAN-phase domain approval gate with named frontier questions, and move every domain planning survey out of `## Objective` into `## Planner Guidance`.

`skills/superplan/SKILL.md` Phase 2 keeps the domain survey as a requirement that precedes decomposition and drops the researcher-approval stop: the decisions the survey raises enter the frontier instead of an artifact the researcher signs off.

Each domain planning reference gains a named list of the decisions it contributes to the frontier, each stated so a recommended answer can be attached:

- [econ-data-analysis](../../../skills/econ-data-analysis/references/planning.md) — disposition of each data gap (acquire, scope down, proceed), which robustness checks matter for this study, and whether a borderline sensitivity failure is meaningful.
- [theory-modeling](../../../skills/theory-modeling/references/planning.md) — functional form, solution concept and equilibrium selection, normalizations, and which verification modes each result gets. The existing "escalate methodology choices — ask, don't choose" rule is this list, made explicit.
- [academic-writing](../../../skills/academic-writing/references/planning.md) — mode, audience, review lanes, and output disposition. §Hard Gate is retired; targets and the build command are facts the agent finds.
- [slide-design](../../../skills/slide-design/references/planning.md) — venue and audience, the talk objective, and the main-versus-backup policy.

Homes follow one test, applied per domain by the skill that owns the content: **binding goes in `## Objective`, information goes in `## Planner Guidance`.** Binding means a reviewer rejects work against it, and only the objective reaches descendants — a task read injects an ancestor's objective and nothing else.

- **Information:** econ-data-analysis's data inventory, which is explicitly not binding, and theory-modeling's catalogue of timing, primitives, and endogenous objects.
- **Binding:** theory-modeling's solution concept, canonical Notation Conventions, Assumptions, and Verification Plan; slide-design's whole audience-context inventory, which its `[BLOCKING]` review check judges the deck against; academic-writing's writing header.

Keep intact: the anti-speculation red flags, the pipeline-file requirement, every `[BLOCKING]` implementation and review checklist item, and `slide-design` SKILL.md's review-time check against the recorded audience context.

Sweep the retired gate's stale references, including the §Depth Tiers standard row, [harness-plan-mode.md](../../../skills/superplan/references/harness-plan-mode.md) "any domain hard gate is satisfied", and the §Self-Review inventory-coverage item in [build-and-review.md](../../../skills/superplan/references/build-and-review.md).

Validation: a no-silent-loss audit gate by gate — every decision a retired gate forced appears as a named frontier question or as a documented survey output, quoted side by side in `## Results`. `grep -rni "hard gate\|researcher approval\|get researcher\|present the inventory" skills/` returns nothing for planning gates, and all edited prose passes the `CLAUDE.md` §Teach the Protocol three tests.

## Planner Guidance

- The split rule is contract versus discovery, not artifact name: a reviewer-rejectable line is objective content wherever it came from. academic-writing's writing header is mode, audience, lanes, and disposition — decisions throughout — so it stays in the objective, and theory-modeling's Verification Plan stays with it as a validation criterion.
- The risk is softening discipline while removing the stop. Walk each gate's current text and place its content before deleting it: econ-data-analysis step 6 ("present the inventory to the researcher"), theory-modeling step 6 ("present the inventory and get researcher approval") plus its "never proceed to task drafting on a verbal description" red flag, academic-writing §Hard Gate, and slide-design's before-decomposition recording rule.
- Four planning references and one spine section, all prose, no code. `docs/plans/` holds dated historical records that keep the old gate language and stay untouched.

## Results

Every PLAN-phase approval gate is gone, and each of the four domain planning references now names the decisions it puts on the frontier.

- **The spine.** [Phase 2](../../../skills/superplan/SKILL.md) keeps the survey as a requirement that precedes decomposition — "Run its planning survey before any task structure is drafted" — and drops the researcher-approval sentence. The §Depth Tiers standard row, [harness-plan-mode.md](../../../skills/superplan/references/harness-plan-mode.md), and the [§Self-Review](../../../skills/superplan/references/build-and-review.md) coverage item no longer speak of a domain hard gate.
- **econ-data-analysis.** Step 6 ("present the inventory to the researcher") becomes §Frontier Contributions: gap disposition, which robustness checks matter, and whether a borderline sensitivity failure is meaningful. The "one question at a time" instruction in step 1 went with it — it contradicted the round.
- **theory-modeling.** Step 6's "get researcher approval" becomes a write-into-two-homes step plus §Frontier Contributions: functional form, solution concept and equilibrium selection, normalizations, and verification mode per result. "Escalate methodology choices" survives, now pointing at that list.
- **academic-writing.** §Hard Gate is retired for §Frontier Contributions: mode, audience, review lanes, and disposition are questions; the writing targets and build command are facts to find.
- **slide-design.** Venue, audience makeup, the talk objective, and the main-vs-backup policy are frontier questions. The inventory stays in `## Objective`, unchanged.

**No-silent-loss audit.** Every decision a retired gate forced now has a named home:

| Retired gate text | Where it went |
|---|---|
| econ step 6, "present the inventory … so gaps surface while the structure is still open" | gap-disposition question; the inventory keeps its existing `## Planner Guidance` home |
| econ sensitivity steps 1 and 5, "discuss which checks matter" / "ask the researcher" whether a failure is meaningful | two questions, the "research judgment, not an RA call" wording kept verbatim |
| theory step 6, "present the inventory and get researcher approval … confirm before task drafting" | write-into-two-homes step; four methodology questions |
| theory verification step 1, "discuss with the researcher which checks matter" | verification-mode question |
| academic-writing §Hard Gate, approval of target, mode, lanes, audience, build command, disposition | four questions; targets and build command reclassified as facts |
| slide-design, inventory recorded before decomposition | four questions; the inventory keeps its `## Objective` home |

**Kept intact.** theory-modeling's anti-speculation red flags and rationalizations, its user-gated Notation Conventions promotion rule, econ-data-analysis's file-system-before-asking discipline and pipeline-file requirement, and every `[BLOCKING]` implementation or review checklist item. `slide-design` SKILL.md's review-time check still resolves — §Audience-Context Inventory kept its heading.

**Verification.** `grep -rni "hard gate\|researcher approval\|get researcher\|present the inventory\|gate passes"` over `skills/`, `hooks/`, `README.md`, and `CLAUDE.md` leaves only INTEGRATE-phase approvals, HTML sanitization, and hook internals — no planning gate. All four references carry a §Frontier Contributions section, and no domain `SKILL.md` pointer dangles: none cited §Hard Gate, and the theory-modeling and slide-design rows point at headings that still exist.

**Objective corrected twice, both times on the same test.** The task first called for academic-writing's writing header to leave `## Objective`; it is mode, audience, lanes, and disposition — decisions a reviewer rejects work against — so it stayed, and theory-modeling's Verification Plan stayed with it.

Review then showed the test has a second edge: a descendant task read injects an ancestor's `## Objective` and nothing else ([task_read.py:213](../../../skills/task-tree/scripts/task_read.py#L213)), so content in ancestor guidance never reaches the agent below. Two `[BLOCKING]` domain checks read exactly what this task had moved — theory-modeling requires the solution concept named before derivation starts, slide-design judges the deck against the recorded audience context. Both are binding, so the solution concept moved into the objective block and slide-design's inventory stayed where it was. econ-data-analysis's data inventory is not binding and keeps its guidance home. The rule is now stated in the objective, and each domain skill applies it to its own content.

The section rename this exposes — `## Planner Guidance` reads as advice when the real distinction is binding versus information — is [task-tree/details-rename](../../task-tree/details-rename/task.md), not this task.
