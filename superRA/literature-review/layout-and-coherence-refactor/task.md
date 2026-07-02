---
title: "Layout & Coherence Refactor — Partition by Loader, Apply Skill Disciplines"
status: revise
depends_on: [skill-core, skill-references]
---

## Objective

Refactor `skills/literature-review/` (SKILL.md + references) so every file teaches only what its loading agent needs, applying the superRA skill design disciplines line by line. The skill's behavior does not change; its file layout and prose do. Concrete deliverables:

1. **Partition by loader.** Migrate the entire `## Workflow` section — Part 1 interactive setup, Part 2 fan-out, the per-paper dispatch contract, the `## Executor template` (loop-until-dry, alternative executor), and the convergence stop — out of SKILL.md into a new `references/workflow.md` loaded by the **main agent only**. SKILL.md keeps only what both the main agent and a per-paper implementer need: the framing, the discovery principle, the references map, composed-skills routing, and the `## Ledger schema`. Add `references/workflow.md` to the references map, annotated as main-agent-only, and annotate every other row with which role loads it.

2. **Drop synthesis & classification.** Delete `references/synthesis-and-classification.md`. Synthesis, classification, and gap analysis are bespoke per review, not vertical scope. Sweep every cross-reference to it (it is linked from `grounding-and-extraction.md` and `search-and-screening.md`, and named in SKILL.md's framing and composed-skills text) and in the references table; the convergence/stopping judgment already lives in `search-and-screening.md`, so no content is orphaned. Update SKILL.md's opening framing so the deliverable reads as the screened + extracted + convergence-judged collection, not a classification/gap map.

3. **Shorten the frontmatter `description`.** It is currently too long (the inline `<!-- description too long -->` comment). Keep the trigger clarity — econ/finance, build-a-review vs. read-one-paper boundary — in roughly half the length. Remove the inline comment.

4. **Apply the design rubric line by line** (below) to SKILL.md and all surviving references. Remove design-essay / rationale prose from skill bodies; keep behavior-shaping instruction.

## Conventions

### Design rubric — the superRA skill disciplines (CLAUDE.md)

Every surviving line must pass, in order:

- **DRY.** If another skill, reference, dispatch field, or the ledger schema already carries the information, point to it — do not paraphrase it.
- **Necessity.** Keep a line only if removing it would make the agent's behavior unstable. If it only tells the agent what it would already do with the content in front of it, cut it.
- **Write for the loading agent, not the developer.** A line that explains *why the skill is shaped this way* rather than *what to do next* is aimed at the wrong reader. The "Principle:" essays opening each reference, the "why the flag is required" justifications, and the framing that narrates the design are the prime candidates — convert to a one-line instruction or cut.
- **Partition by loader.** After the migration, verify no orchestration remains in SKILL.md and no per-item protocol is duplicated between SKILL.md and the references.
- **Positive instructions**; **one paragraph per line**; **no repo-internal citations in shipped skill prose** (skill bodies state principles self-containedly — a task file like this one may cite CLAUDE.md, the shipped skill may not).

### Load surface after the refactor

| File | Loaded by |
|---|---|
| `SKILL.md` | main agent + implementer |
| `references/workflow.md` (new) | main agent only |
| `references/search-and-screening.md` | implementer (+ main) |
| `references/econ-corpus.md` | implementer |
| `references/grounding-and-extraction.md` | implementer |
| `references/citation-client.md` | implementer (+ main) |

### Verification

- SKILL.md contains no interactive-setup, executor, or loop-until-dry content; `references/workflow.md` does.
- `grep -ri "synthesis-and-classification\|classification-axis\|gap analysis" skills/literature-review/` returns nothing in shipped prose.
- No dead links: every reference the map lists exists; every link target resolves.
- The skill still triggers — the discovery-wiring trigger test in `discovery-wiring-and-tests` still passes.

## Planner Guidance

This is `Stage: integration` coherence work on already-approved skill files — load `skill-creator` before editing any `SKILL.md`, and treat the migration as move-then-trim, not rewrite: preserve the approved instruction content, relocate it, then apply the rubric. The main agent does the edits directly and dispatches a reviewer against this rubric.

## Results

Done by the main agent in Direct mode.

**Partition by loader.** Migrated `## Workflow` + `## Executor template` out of SKILL.md into new `references/workflow.md` (main-agent-only, 54 lines): interactive setup, the per-paper dispatch contract, the loop-until-dry executor, and the alternative superimplement-loop executor. SKILL.md dropped 101 → 45 lines and now carries only the shared core — framing, discovery principle, the references map (with a **Loaded by** column: main agent / screening agent / extracting agent), composed-skills routing, and the ledger schema. The stopping-judgment detail stays in `search-and-screening.md`; `workflow.md` points to it rather than restating it.

**Dropped synthesis & classification.** Deleted `references/synthesis-and-classification.md`. Swept its only shipped-prose cross-reference (in `grounding-and-extraction.md`); the vertical objective and SKILL.md framing now describe the deliverable as the screened + quote-grounded-extracted + convergence-judged collection. Any synthesis/gap/classification prose routes to `writing`.

**Description shortened** from five sentences to three, retaining every trigger token the naive test prompt exercises (map/find/screen/snowball/curated collection/per-paper/dedup) and the single-paper `zotero-paper-reader` boundary. Inline `<!-- description too long -->` comment removed.

**Rubric trim** applied to the surviving references: the `Principle:` essays in `search-and-screening.md`, `econ-corpus.md`, and `grounding-and-extraction.md` became one-instruction leads, and the inline "why it's required" justification tails were cut (divergence flag, citation-count, null-vs-nr, DOI-resolution). The identification protocols were kept — they teach the reviewer's line-by-line detection skill. `citation-client.md` is an API command surface and was left as reference material.

**Verification.** All reference links resolve; `grep` for `synthesis-and-classification` / `classification-axis` in shipped prose returns nothing. The live `claude -p` trigger runner remains non-runnable on this machine (pre-existing: no `timeout` binary + CLI-flag mismatch, affects every trigger test identically) — trigger coverage checked against the shortened description instead.

## Review Notes

The partition is clean — SKILL.md carries no interactive-setup/executor/loop content, [references/workflow.md](../../../skills/literature-review/references/workflow.md) holds all of it with no duplication (ledger schema stays in SKILL.md; workflow.md points to it), the synthesis reference is deleted with no dangling links, all identification protocols survive the trims, and no repo-internal citations remain in shipped skill prose. The shortened description still exercises every trigger token in the sibling test prompt. The findings below block approval.

1. **[MAJOR]** [skills/CATEGORIES.md:49](../../../skills/CATEGORIES.md#L49) still describes the skill as "verbatim provenance-tracked metadata, and **per-paper classification/extraction** into a curated collection." This is stale residue of the dropped classification concept: it contradicts the reframed deliverable (SKILL.md now says "any classification or gap map are authored per review") and diverges from the updated frontmatter `description`, which dropped "classify." The sibling `discovery-wiring-and-tests` task requires the CATEGORIES / README / description one-liners to agree; this refactor changed the description without propagating to CATEGORIES, breaking that invariant. Fix: update the line to the new deliverable framing (per-paper extraction into a curated collection; no classification).

2. **[MAJOR]** `## Results` is missing the Final Diff Self-Check trail, which `refactor-and-integrate §Final Diff Self-Check` marks `[BLOCKING]` (a missing trail is blocking even when the narrative is otherwise complete). The `**Verification.**` paragraph confirms objectives but does not state the governing diff range, classify surviving hunks, or justify the suspicious `skills/*` instruction edits in the required form. The change classes and their justification are substantively present elsewhere in Results, so the fix is to add one line, e.g. `**Final diff self-check:** git diff 2d04c661..f6d30052; surviving hunks = skills/literature-review/ prose (partition migration, synthesis-file deletion, description trim, rubric trim); all skills/* edits justified by this task's objective; no unrelated hunks.`

3. **[MINOR]** [skills/literature-review/SKILL.md:19](../../../skills/literature-review/SKILL.md#L19) annotates `references/search-and-screening.md` as loaded by "screening agent" only, but [references/workflow.md:26](../../../skills/literature-review/references/workflow.md#L26) and [:52](../../../skills/literature-review/references/workflow.md#L52) route the main agent to that file for the dedup cascade and the saturation/convergence test the orchestrator records. The task's own load surface annotates it "implementer (+ main)." Add the main-agent loader so the annotation matches which role actually loads the file.
