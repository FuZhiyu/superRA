---
title: "Redesign refactor-and-integrate to Teach Objective and Method"
status: approved
depends_on:  []
tags: []
output:
  - skills/refactor-and-integrate/SKILL.md
created: 2026-06-19
---

## Objective

Rewrite `skills/refactor-and-integrate/SKILL.md` so it teaches the **objective** and the **method**, not a list of goal labels. The current skill opens with a technique list ("Tool skill for codebase coherence: convention fit, utility reuse, Project Doc Audit...") and pushes all substance into a checklist that names good outcomes ("Naming consistency", "Utility usage") without teaching how to reach them. An agent reading it pattern-matches the checklist labels and misses anything the checklist did not literally name. This rewrite makes the skill effective by stating why the work exists and teaching the identification protocol for each technique.

**The objective the skill must open with.** Every technique here serves human maintainability through two concrete ends: (1) the result reads as if one person wrote the whole codebase — *consistency* with the host project; (2) the surviving diff is the smallest one that achieves the task — *reviewability*. A human has to read, trust, and maintain this code later. State this first, before any technique, so a downstream agent can adapt to a hunk the checklist never anticipated.

**Target structure (all inline in SKILL.md — no new reference file):**

```
# Refactor and Integrate
[Objective: maintainability via consistency + minimum reviewable diff]
## Establish the baseline first   (the governing diff, merge-base semantics; what "minimum net diff" means)
## Fit to the codebase            (method: read the neighbors → match names, reuse utilities, follow patterns; document deviations)
## Triage every hunk              (walk the governing diff; every hunk earns its place)
## Consolidate for maintainability (new; generic simplification, never change behavior, scope to touched)
## Project Doc Audit              (keep; light edits)
## Sync Impact Context            (condense)
## Checklist                      (thin; points to the method, does not restate it)
## Final Diff Self-Check          (thin trail; points to the method)
```

**Required changes:**

1. **Objective-first opening.** Replace the technique-list intro with the maintainability objective above. Lead with the two ends (consistency, minimum reviewable diff) and why they matter to a human maintainer.

2. **Establish the baseline first.** Move the baseline definition to the top of the method, before triage — it is the playing field. Define the governing diff with merge-base semantics: to isolate *only the changes made on this branch*, use `BASE...HEAD` (three-dot) or equivalently `$(git merge-base BASE HEAD)..HEAD`. After Sync, `BASE_HEAD_SHA` is already an ancestor of `HEAD`, so the existing `BASE_HEAD_SHA..HEAD` (two-dot) is correct *there* and stays the post-sync command. For standalone work, use the merge-base of the work and the integration base, not a bare two-dot against a possibly-diverged base ref. Define plainly, in one or two sentences, what "minimum net diff" means: the smallest set of surviving hunks that achieves the task objective.

3. **Fit to the codebase — teach the method.** Replace the bare "Naming consistency / Utility usage" goal labels with the identification protocol: before keeping code, read its neighbors in the same module; find how this codebase names the same concept, what utilities already exist, what patterns it follows; match them so a reader cannot tell new code from old. An intentional deviation carries a one-line reason. This is the line-by-line *how*, not just the outcome.

4. **Triage every hunk — reframe, preserve behavior.** Teach: walk the governing diff hunk by hunk; every hunk must earn its place by contributing to the task objective; a hunk that does not, gets pruned. Keep all three branches of the prune rule that `01-min-net-diff-baseline` deliberately installed — (a) confident junk (debug prints, reformatting, speculative abstraction, dead helpers) → revert; (b) justified → keep and cite the source; (c) scope-ambiguous but plausibly load-bearing → keep and raise it, never revert on the agent's own authority, and a hunk covered by no source routes to `superplan §User Feedback and Changing the Task Tree`. **Preserve the never-silently-delete behavior** (it prevents Type II silent deletion of legitimate work). **Drop the verbose asymmetry explanation prose** ("deletion drops a hunk from the governing diff so no later reviewer sees what vanished, whereas a kept hunk stays reviewable...") — state the behavior plainly without the essay. Do not reintroduce a per-hunk classification taxonomy; the prior design session rejected that as a contingency tree.

5. **Consolidate for maintainability — new section.** Teach that minimum net diff is not only deletion: look across the surviving hunks and ask whether the same objective can be reached with a simpler, more host-consistent change. Teach the eye plus a few concrete, generic cues — repeated procedure → extract a helper; near-duplicate of an existing module/dataset → extend it minimally rather than fork; nested conditionals → flatten; comments that restate obvious code → cut. Keep helpful abstractions; clarity over brevity. Two guardrails need the non-rigid framing, because the obvious "safe" version is wrong for research integration:
   - **Net-minimum diff, not files-you-touched.** The target is the smallest net diff that leaves the codebase consistent and maintainable. That often means reaching into existing shared code to extend a utility in a minimal way rather than leaving it untouched and duplicating the logic — the minimal extension *is* the net-min-diff move. Do not teach "only refine code you already touched" as a boundary; teach net-minimum diff as the objective.
   - **The drift suite is the behavior guardrail, not behavior-invariance.** Consolidating toward host conventions can shift a result slightly; that is acceptable as long as the drift tests still pass. When a consistency or consolidation fix *does* move a protected result, treat it as a signal to investigate — the inconsistency may have been producing the wrong number — adjudicated per the drift-test discipline the workflow already runs around Integrate, never silently reverted to preserve the old output and never silently re-expected. Do not write an absolute "never change behavior."

   This section must stay **domain-agnostic** so it applies across data analysis, theory, writing, and future verticals. Domain-specific consolidation rules (redundant intermediary datasets, variable-construction consistency, etc.) stay in the domain `integration.md` references and are not absorbed here.

6. **Fix the "documentation currency" terminology.** Rename it to plain language (e.g. "Docs match the code" / "Stale docs"). If the renamed phrase changes the descriptive list in `skills/econ-data-analysis/references/integration.md` line 5 (which currently reads "...PR-friendly diffs, documentation currency..."), update that one phrase so it still names this skill's concern.

7. **Loosen the domain-skill load note.** The current line ("The active domain skill's stage-load table routes any domain-specific integration reference...") is too rigid. Reword to: load whichever domain skill(s) the work actually touches.

8. **Deduplicate the prune logic.** It is currently stated three times — `§Minimum Net Diff` prose, the Checklist, and `§Final Diff Self-Check`. Collapse to one authoritative method section (the triage above); the Checklist and Final Diff Self-Check become thin pointers to it (the self-check keeps its trail-recording mechanics but stops re-narrating the triage rules).

### Constraints

- **Keep externally-referenced named concepts stable** so callers do not dangle. `skills/superintegrate/SKILL.md` depends on the named concepts "Project Doc Audit", "minimum net diff", and the "Final Diff Self-Check" trail (it dispatches integration agents that produce and verify that trail). These names must survive the restructure as recognizable sections/concepts. Grep `skills/superintegrate/SKILL.md` after the rewrite to confirm every concept it names still resolves.
- This task edits a **skill**, not `agents/*`, so no generated-artifact regeneration (`sync_codex_agents.py`) is needed. The parent's skill-creator and `CLAUDE.md §Teach the Protocol` DRY + Necessity conventions apply: self-apply both tests to every added line.
- Apply the `writing` skill's prose discipline: plain substance-first prose (no AI-flavored tics, no rhetorical hooks, no "not just X but Y"), one paragraph per line, no cross-skill pattern citations, and no citations to repo-internal contributor docs (`CLAUDE.md`/`AGENTS.md`) inside the shipped skill body — state principles self-containedly.
- Approved task bodies under `integration-thoroughness` (01–03) reference `§Minimum Net Diff` and `§Final Diff Self-Check`; leaving stable anchor names keeps those historical records accurate. Do not edit those approved task bodies.

### Validation

- The skill states the maintainability objective (consistency + minimum reviewable diff) before any technique.
- Fit, Triage, and Consolidate each teach a method an agent can apply line by line, not a goal label.
- The baseline/governing-diff definition appears before triage and states the merge-base semantics correctly.
- The ternary triage behavior is intact (all three branches + never-silently-delete + `superplan` routing for the no-source case); the asymmetry essay is gone; no classification taxonomy was introduced.
- The Consolidate section is present, domain-agnostic, teaches the eye plus concrete cues, frames net-minimum diff (including minimal extension of existing code) rather than a touched-files boundary, and defers to the drift suite as the behavior guardrail (no absolute "never change behavior").
- "Documentation currency" is renamed; the `econ-data-analysis/references/integration.md` phrase is reconciled.
- The prune logic is stated once; the Checklist and Final Diff Self-Check are pointers, not restatements.
- `grep` confirms every concept `superintegrate` names still resolves in the rewritten skill.
- Every surviving line passes the DRY + Necessity tests.

## Results

Rewrote [skills/refactor-and-integrate/SKILL.md](../../../skills/refactor-and-integrate/SKILL.md) so it opens with the maintainability objective and teaches the identification method behind each technique, replacing the technique-list intro and the goal-label checklist. Reconciled one downstream phrase in [skills/econ-data-analysis/references/integration.md:5](../../../skills/econ-data-analysis/references/integration.md#L5).

**New skill structure** (all inline, no new reference file):

- **Objective-first opening** ([SKILL.md:6-15](../../../skills/refactor-and-integrate/SKILL.md#L6-L15)): leads with the human maintainer and the two ends — *consistency* (reads as one author) and *minimum reviewable diff* — then tells the agent how to act on a hunk no rule anticipated. Replaces the old "Tool skill for codebase coherence: convention fit, utility reuse..." technique list.
- **§Establish the baseline first**: governing-diff definition moved to the top of the method. One merge-base rule — `git diff BASE...HEAD` (three-dot), equivalently `$(git merge-base BASE HEAD)..HEAD`, or an explicit dispatch range — and defines "minimum net diff" plainly as the smallest surviving-hunk set that achieves the task objective.
- **§Fit the host project**: teaches the read-the-neighbors method (names, utilities, patterns; match so a reader cannot tell new from old; deviation carries a one-line reason), replacing the bare "Naming consistency / Utility usage" labels.
- **§Triage every hunk**: the single authoritative prune section. Keeps all three branches from `01-min-net-diff-baseline` (confident junk → revert; justified → keep, tracing to a source in your head with no per-hunk citation; scope-ambiguous-but-load-bearing → keep + raise, `superplan` routing for the no-source case) plus the never-silently-delete behavior and the base-current deletion/relocation symmetry. Drops the asymmetry explanation entirely and states the rule plainly; introduces no per-hunk taxonomy.
- **§Consolidate for maintainability** ([SKILL.md:51-65](../../../skills/refactor-and-integrate/SKILL.md#L51-L65)): new, domain-agnostic. Teaches the eye plus concrete cues (repeated procedure → helper; near-duplicate → extend not fork; nested conditionals → flatten; redundant comments → cut), frames net-minimum diff (including minimal extension of shared code) rather than a touched-files boundary, and defers to the drift suite as the behavior guardrail (no absolute "never change behavior"). Defers domain-specific consolidation rules to the domain `integration.md` references.
- **§Project Doc Audit** kept with light edits; **§Sync Impact Context** kept; **§Final Diff Self-Check** ([SKILL.md:86-98](../../../skills/refactor-and-integrate/SKILL.md#L86-L98)) keeps its trail-recording mechanics but step 5 now points to §Triage instead of re-narrating the rules; **§Checklist** ([SKILL.md:99-132](../../../skills/refactor-and-integrate/SKILL.md#L99-L132)) thinned to pass/fail points that reference each method section.
- **Terminology fix**: "Documentation currency" → "Docs match the code" ([SKILL.md:127](../../../skills/refactor-and-integrate/SKILL.md#L127)); the `econ-data-analysis` ref phrase reconciled to "docs matching the code".
- **Domain-load note loosened** ([SKILL.md:15](../../../skills/refactor-and-integrate/SKILL.md#L15)): "Load whichever domain skill(s) the work actually touches."

**Prune logic deduplicated**: stated once in §Triage; §Final Diff Self-Check step 5 and the Checklist are pointers, not restatements.

**Post-review refinements** (completion stop, co-edited with the researcher): unified the baseline to the single three-dot merge-base rule (the post-Sync two-dot is its collapsed form, reached via the explicit-range path superintegrate passes); reduced the Justified branch to a mental source-trace with no per-hunk citation; generalized the framing so it reads for prose, notes, and slides as well as code (opening, §Fit the host project, Consolidate cues), keeping the drift-suite guardrail data-flavored by design; renamed §Fit to the codebase → §Fit the host project (no external reference depends on that heading). `check_markdown.py` re-run: clean.

**Validation evidence:**

- Maintainability objective (consistency + minimum reviewable diff) appears before any technique — confirmed at SKILL.md:6-15.
- Fit / Triage / Consolidate each teach a method, not a goal label — confirmed by re-read.
- Baseline/governing-diff definition precedes triage with correct merge-base semantics — §Establish the baseline first precedes §Triage every hunk.
- Ternary triage behavior intact (all three branches + never-silently-delete + `superplan` routing); asymmetry essay gone (`grep` for "no later reviewer sees what vanished" / "whereas a kept hunk stays reviewable so" → 0 hits); no classification taxonomy introduced.
- Consolidate section present, domain-agnostic, eye + concrete cues, net-minimum framing, drift-suite guardrail, no absolute "never change behavior."
- `grep skills/superintegrate/SKILL.md` named concepts — "Project Doc Audit", "minimum net diff", "Final Diff Self-Check" — all resolve in the rewritten skill (the first two as concept text + sections, the last as a section heading).
- `check_markdown.py` on the rewritten skill: clean.

**Final diff self-check:** `git diff <pre-edit>..HEAD -- skills/refactor-and-integrate/SKILL.md skills/econ-data-analysis/references/integration.md`; two surviving change classes — (1) full rewrite of `refactor-and-integrate/SKILL.md` (this task's objective: objective-first + method-teaching restructure), (2) one-phrase reconciliation in `econ-data-analysis/references/integration.md:5` (required change #6). Both are `skills/*` instruction-prose edits (the suspicious class), each justified line by line against this task objective; no taxonomy, no asymmetry essay, no new reference file — passes the DRY + Necessity tests.

