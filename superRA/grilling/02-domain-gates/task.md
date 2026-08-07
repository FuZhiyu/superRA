---
title: "Retire the domain planning approval gates in favor of frontier questions"
status: revise
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

Survey artifacts move to `## Planner Guidance` on the governing task, matching what econ-data-analysis already does with its data inventory: theory-modeling's primitives and endogenous-object catalogues with their timing and solution-concept notes, and slide-design's audience, shared-context, missing-context, and divergent-priors record.

Decisions stay in `## Objective` as contract, because a reviewer rejects work against them: theory-modeling's canonical Notation Conventions, Assumptions, and Verification Plan; slide-design's talk objective and main-vs-backup policy; academic-writing's writing header.

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
- **slide-design.** The inventory records into `## Planner Guidance`; venue, audience makeup, the talk objective, and the main-vs-backup policy are frontier questions.

**No-silent-loss audit.** Every decision a retired gate forced now has a named home:

| Retired gate text | Where it went |
|---|---|
| econ step 6, "present the inventory … so gaps surface while the structure is still open" | gap-disposition question; the inventory keeps its existing `## Planner Guidance` home |
| econ sensitivity steps 1 and 5, "discuss which checks matter" / "ask the researcher" whether a failure is meaningful | two questions, the "research judgment, not an RA call" wording kept verbatim |
| theory step 6, "present the inventory and get researcher approval … confirm before task drafting" | write-into-two-homes step; four methodology questions |
| theory verification step 1, "discuss with the researcher which checks matter" | verification-mode question |
| academic-writing §Hard Gate, approval of target, mode, lanes, audience, build command, disposition | four questions; targets and build command reclassified as facts |
| slide-design, inventory recorded before decomposition | guidance for the record, objective for the two gated decisions, four questions |

**Kept intact.** theory-modeling's anti-speculation red flags and rationalizations, its user-gated Notation Conventions promotion rule, econ-data-analysis's file-system-before-asking discipline and pipeline-file requirement, and every `[BLOCKING]` implementation or review checklist item. `slide-design` SKILL.md's review-time check still resolves — §Audience-Context Inventory kept its heading.

**Verification.** `grep -rni "hard gate\|researcher approval\|get researcher\|present the inventory\|gate passes"` over `skills/`, `hooks/`, `README.md`, and `CLAUDE.md` leaves only INTEGRATE-phase approvals, HTML sanitization, and hook internals — no planning gate. All four references carry a §Frontier Contributions section, and no domain `SKILL.md` pointer dangles: none cited §Hard Gate, and the theory-modeling and slide-design rows point at headings that still exist.

**Objective corrected mid-implementation.** The task called for academic-writing's writing header to leave `## Objective`. It is mode, audience, lanes, and disposition — decisions a reviewer rejects work against, not survey — so it stayed, and theory-modeling's Verification Plan stayed with it on the same test. The rule applied is contract versus discovery, which is what the researcher's notation ruling turns on too.

## Review Notes

Tier `quick`. Focuses: no-silent-loss over the retired PLAN-phase approval gates, plus `CLAUDE.md` §Teach the Protocol and §Skill Prose Style over the four new §Frontier Contributions sections.

Findings 1 and 2 share one root: a descendant task read injects **only** the ancestor's `## Objective`, never its `## Planner Guidance` — [task_read.py:213](../../../skills/task-tree/scripts/task_read.py#L213) calls `_ancestor_objective`, and [academic-writing/SKILL.md:36](../../../skills/academic-writing/SKILL.md#L36) states the mechanism ("on the `## Objective` of the … ancestor task … so every writing agent inherits it via the ancestor chain"). Content moved into an ancestor's guidance leaves the descendant's injected context.

1. `[BLOCKING]` **theory-modeling's `### Solution Concept` is in the wrong home by the file's own split rule.** [planning.md:11](../../../skills/theory-modeling/references/planning.md#L11) states the objective holds "the parts a reviewer rejects work against", and [planning.md:82](../../../skills/theory-modeling/references/planning.md#L82) names "Solution concept and equilibrium selection" a settled frontier decision — yet the block is written into `## Planner Guidance` at [planning.md:39-40](../../../skills/theory-modeling/references/planning.md#L39-L40). A reviewer does reject work against it: [theory-modeling/SKILL.md:131](../../../skills/theory-modeling/SKILL.md#L131) is `[BLOCKING]` "The active solution concept named before derivation starts", and the derivation happens in a descendant task that no longer inherits the name. Move `### Solution Concept` into the `## Objective` block.

2. `[BLOCKING]` **slide-design's audience-context inventory is now unreachable by the `[BLOCKING]` check that verifies against it.** [slide-design/SKILL.md:75](../../../skills/slide-design/SKILL.md#L75) requires a reviewer to "verify against the audience-context inventory recorded at planning time"; [integration.md:7](../../../skills/slide-design/references/integration.md#L7) checks the deck route against it at INTEGRATE. [planning.md:7](../../../skills/slide-design/references/planning.md#L7) now records it in the ancestor's `## Planner Guidance`, so neither agent sees it — and neither loads `references/planning.md`, which is PLAN-phase-only ([SKILL.md:17](../../../skills/slide-design/SKILL.md#L17)). `## Objective` listed this check under "Keep intact" while also directing the record to guidance; `## Results` tests only that the heading still resolves, which is the pointer, not the artifact. Resolve the conflict: either keep the inventory in the ancestor `## Objective`, or name the governing ancestor's `## Planner Guidance` as the retrieval path at both check sites — and record which, since it is an objective-internal conflict.

3. `[BLOCKING]` **The recommended-answer and carry-the-evidence rules are restated in all four new sections.** [grilling.md:22-24](../../../skills/superplan/references/grilling.md#L22-L24) owns both: "Recommended answer first, labeled `(Recommended)`, on every question" and "Carry the evidence. Name the survey finding or exploration result that raises the question." The copies: [econ planning.md:47](../../../skills/econ-data-analysis/references/planning.md#L47) "each carrying your recommended answer and the finding that raises it"; [theory planning.md:79](../../../skills/theory-modeling/references/planning.md#L79) and [academic-writing planning.md:9](../../../skills/academic-writing/references/planning.md#L9) "each carrying your recommended answer"; [theory planning.md:115](../../../skills/theory-modeling/references/planning.md#L115) "so recommend rather than choose"; [slide-design planning.md:23](../../../skills/slide-design/references/planning.md#L23) "Recommend an answer for each". [slide-design planning.md:23](../../../skills/slide-design/references/planning.md#L23) additionally paraphrases [grilling.md:15](../../../skills/superplan/references/grilling.md#L15) — whose own example is venue — with "Venue and audience makeup are researcher-held facts, so they are frontier questions … rather than inferences". Five copies of two rules, four files to drift. The `superplan §Grilling` pointer is already in each sentence: keep the pointer and the per-domain list, cut the paraphrased clauses.

4. `[ADVISORY]` **No review gate checks against the recorded talk objective or main-vs-backup policy**, so [slide-design planning.md:14](../../../skills/slide-design/references/planning.md#L14) "The two decisions the review gates check against" asserts a gate that does not exist — `[BLOCKING]` items [SKILL.md:77-78](../../../skills/slide-design/SKILL.md#L77-L78) judge backup splits on their own merits, and the one check against a recorded artifact ([SKILL.md:75](../../../skills/slide-design/SKILL.md#L75)) reads the inventory. The placement is right by contract-versus-discovery; the clause is a false rationale. Cut it.

5. `[ADVISORY]` **The "assumption map" label no longer appears in the artifact a `[BLOCKING]` gate names.** [theory-modeling/SKILL.md:153](../../../skills/theory-modeling/SKILL.md#L153) requires results checked "against the assumption map"; the retired step 6 labeled the objective subsection `**Model Inventory / Assumption Map:**`, and now the guidance block is `**Model inventory:**` ([planning.md:34](../../../skills/theory-modeling/references/planning.md#L34)) while the objective block carries no label ([planning.md:55-56](../../../skills/theory-modeling/references/planning.md#L55-L56)). Label the objective block so the gate names something an implementer can find.

6. `[ADVISORY]` **Same-file restatement in econ-data-analysis.** [planning.md:14](../../../skills/econ-data-analysis/references/planning.md#L14) "Planning guidance: it informs what tasks to write" and [planning.md:16](../../../skills/econ-data-analysis/references/planning.md#L16) "**Not objective content.** … A durable record … belongs in `## Planner Guidance`" now carry the same fact; cutting the "presented to the researcher" clause removed line 14's second one. Merge into line 16.

Out of focus, no action: `tests/harness-instruction-following/test_contract.py` fails `test_superimplement_executes_each_selected_seat_filler` and `test_superplan_routed_references_exist` — both pre-existing at the parent commit, as the dispatch stated. 13 pass.
