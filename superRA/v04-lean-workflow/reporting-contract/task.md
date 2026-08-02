---
title: "Reporting Contract: Concise Writing and the Conversation Boundary"
status: implemented
depends_on: [role-skills]
---

## Objective

Establish one reporting contract covering everything agents write — task files, documents, and conversation — built on selection before writing, one home per fact, and pointers across homes.

- Teach principles, not rule catalogs: a small principle set with a paired example or two, written in the register it prescribes, placed where agents already are at write time. Agents apply the principle to cases the examples don't cover. The contract's own prose and examples must be as terse as the style they demand — very concise, easy to skim.
- Core principles: reporting is part of the task — a task is complete only when its report is digestible, so a real share of the task's thinking budget goes to planning the report (who reads this, what they'll do next, which few facts change that — everything else is omitted, not summarized); selecting findings is analysis — a finding is a result the researcher would quote or act on, and pipeline mechanics (a merge count, a completed step) surface only as caveats, never as key findings; lead with the outcome; short by selection, not compression (full sentences, no fragments, invented abbreviations, or arrow chains); state each fact once; plain words, consistent terminology; structural budgets over word counts.
- Write-time DRY: a fact's home is decided when the output is produced. When the deliverable is itself an artifact (a document, a code change), the artifact is the record — `## Results` points to it with at most a high-level summary, never restating its content or the diff. Generalizes the maturation-time trim-to-pointer disposition to write time.
- Conversation boundary: chat carries deltas and pointers — what changed at a high level plus the task-file/dashboard reference; content recorded in a task file is referenced, never reproduced. Extras the agent chose not to record go to conversation with an offer to add to `## Results` if the researcher wants them. Replace the unbounded `<summarize the results>` placeholder in `superimplement`; parent rollups link to child findings instead of restating their numbers.
- Results shape (`task-file-contract.md`): operationalize "terse" with an inclusion test mirroring the objective test (a line belongs in `## Results` only if a future reader needs it to use, reproduce, or trust the result); demote the five-slot template to an omit-by-default menu; rebalance the `using-superra` "self-contained account" line with point-over-copy (self-contained through self-orienting pointers, not restatement).
- End stage accretion: the final-diff-self-check trail (`refactor-and-integrate`) moves to the commit body; Protect decisions are not re-narrated into `## Results` (the protect commit records them).
- No decision ledgers: a researcher decision enters a task file by rewriting the owning objective or constraint to its current state — never as a dated "decisions" section or "per user decision <date>" note (the date belongs in git). Add dated decision logs to the stale-content classes in `task-file-contract.md`; sweep the instruction files that model the pattern (e.g. `writing/references/consistency/numerical.md:5`).
- Role skills carry only one-line hooks (a results-economy self-check item symmetric to the thin-results gate); the review skill's results-writing focus enforces this contract.
- Validation: each rule has one home with pointers elsewhere; no surviving instruction invites reproducing `## Results` in conversation or restating an artifact in `## Results`.

### Placement

One always-loaded instruction home; `report-in-markdown` becomes an on-demand reference behind a hook safety net:

- **Craft and boundary → `using-superra`.** The reporting principles (how to write, for files and conversation alike) and the boundary rules (which home owns which fact) land in the framework skill every agent already loads, next to §Task Interface's existing files-vs-commit-vs-return rules.
- **House conventions → inline in `using-superra`.** The setup-specific rules agents hit on nearly every write — file citations as clickable line anchors, figures under `attachments/` — are stated up front (a few lines), because leaving them to post-hoc correction means agents write them wrong every time and churn on hook feedback.
- **General mechanics → hook-backed, load-on-demand.** `report-in-markdown` survives as the reference for markdown mechanics (math renderer traps, tables, figure embedding, raw HTML) but drops out of the always-loaded set. The existing render-integrity hook is the safety net: when it fires, its warning tells the agent to load `report-in-markdown` for the proper form. Do not attempt to make the hook check everything the skill teaches — it catches what it catches; the skill is the authority the hook points to.
- Net effect: the always-loaded pair becomes one skill; prevention is reserved for the conventions with per-write frequency, detection covers the rest.

## Planner Guidance

- Ranked diagnosis of what makes task files long, with `file:line` evidence and live examples: [writing-surfaces map](../attachments/map-writing-surfaces.md); candidate rules and compliance mechanics (short contracts beat catalogs; paired examples are the highest-leverage device; file verbosity needs targeting separate from chat verbosity; the anti-compression guardrail is as necessary as the anti-verbosity rule): [concise-writing research](../attachments/research-concise-writing.md) §C–D.
- The objective-side economy discipline to mirror (rejection test, overflow valve, point-over-copy ladder) exists at `task-tree-design.md` §Writing Objectives and §Context Distillation — cite it; add the missing trim counterpart to its §Objective rewrites on scope expansion.
- Showcase/docs exemplar rewrite is out of v0.4 scope; touch `docs/site` only where statements are invalidated.

## Results

The contract lives in one new section, [`using-superra/SKILL.md` §Reporting](../../../skills/using-superra/SKILL.md) — seven principles, a padded/selected example pair, the conversation boundary, and the two house conventions — and `report-in-markdown` is now load-on-demand behind the render-integrity hook. Every other file changed only to point at that section or to stop contradicting it. The two researcher-decided principles lead the section: reporting is half the task (a real share of the task's thinking goes to planning the report), and selecting findings is analysis (a finding is a result the researcher would quote or act on — the example pair now demotes an accurate merge-count bullet on exactly this bar, and `task-file-contract.md`'s `### Key Findings` menu row cites it).

Where the surrounding rules landed:

- Inclusion test, subsection menu (the five-slot template is now an omit-by-default table), dated-decision-ledger stale class, and the generalized link-don't-copy rollup rule: [`task-file-contract.md` §Results Shape](../../../skills/task-tree/references/task-file-contract.md).
- Two-directional results gate and the completion-menu line that replaced `<summarize the results>`: [`superimplement/SKILL.md`](../../../skills/superimplement/SKILL.md).
- Final-diff self-check trail moved from `## Results` to the commit body: [`refactor-and-integrate/SKILL.md`](../../../skills/refactor-and-integrate/SKILL.md). Protect decisions stay in the protect commit: [`protect.md`](../../../skills/superintegrate/references/protect.md).
- Objective-rewrite trim counterpart: [`task-tree-design.md`](../../../skills/superplan/references/task-tree-design.md). Duplication symptom for consolidation: [`consolidation.md`](../../../skills/superplan/references/consolidation.md).
- One-line results-economy self-check in [`implement-task`](../../../skills/implement-task/SKILL.md); the reviewer's `results-writing` focus repointed to §Reporting.

The hook is the detection half of the design: when `md_integrity` finds an issue on an edited task-tree `.md`, [`task_hook.py`](../../../skills/task-tree/scripts/task_hook.py) now appends a line telling the agent to load `report-in-markdown`. Verified by calling `_markdown_integrity_feedback` on a file with a swallowed `$$` block and a `\Var` macro — three feedback lines, the last one the skill pointer — and on a clean file, which returns nothing.

Dropping `report-in-markdown` from the always-loaded set changed the loading contract, so `ALWAYS_LOADED_SKILLS` is now a one-element tuple and the Codex canary fixture names the skill explicitly, making it evidence for the on-demand path instead of the always-loaded one. `uv run --with pytest --with pyyaml python -m pytest tests/harness-instruction-following -q` → 125 passed; the task-tree suite → 695 passed, 4 skipped.

Deliberate duplication: the citation and figure conventions now appear both in §Reporting and in `report-in-markdown` / `task-file-contract.md` §Figure Embedding. §Placement calls for this — they are hit on nearly every write, so prevention beats post-hoc correction — with `report-in-markdown` remaining the authority on the full form.

Not swept: this repo's own task files still carry `**Final diff self-check:**` trails and duplicated results, and `docs/site` still shows a one-finding `### Key Findings` example. Both fall under the parent's out-of-scope note on exemplar rewriting and task-file hygiene.

## Review Notes

1. **[MAJOR]** The canonical task-file example in [`task-tree/SKILL.md:55-61`](../../../skills/task-tree/SKILL.md#L55-L61) still models the shape this task demoted: a `### Key Findings` heading over a single bullet plus a `### Notes` heading over a single bullet. The new menu in [`task-file-contract.md:74`](../../../skills/task-tree/references/task-file-contract.md#L74) says to add `### Key Findings` only when more than one finding needs separating, and to omit every entry by default. This is an instruction surface (not a docs-site exemplar), it is the most-read illustration of a `task.md` in the repo, and planners scaffolding from it will keep producing the scaffolded shape — so the two skill files now teach opposite defaults. Rewrite the example's `## Results` as the two plain lines the menu implies, or state in the example that the subsections are shown for format illustration only.
   → implemented: example `## Results` rewritten to two plain lines, headings removed ([task-tree/SKILL.md](../../../skills/task-tree/SKILL.md))

2. **[MINOR]** [`task_add_result.py:74`](../../../skills/task-tree/scripts/task_add_result.py#L74) unconditionally creates a `### Key Findings` subsection when `superra task add-result --finding` writes to a task with no results yet, so the tooling emits the omit-by-default subsection on the first finding. Either make the subsection conditional on a second finding arriving or record why the CLI keeps a fixed anchor despite the new default. Deciding this may be out of the task's intended scope — raise it rather than absorb it if so.
   → implemented: kept the fixed anchor; rationale recorded under the subsection menu ([task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md))

3. **[MINOR]** Deleting the whole provenance line from [`consistency/numerical.md`](../../../skills/writing/references/consistency/numerical.md) removed more than the dated decision the objective's sweep targeted. The seven sibling dimension files all still carry a `Source dimensions harvested from …` line at line 5 (e.g. [`citations.md:5`](../../../skills/writing/references/consistency/citations.md#L5)); numerical.md is now the only one without one. Restore the provenance sentence with the `(per user decision 2026-04-19 …)` clause dropped.
   → implemented: provenance sentence restored with the dated clause dropped

4. **[MINOR]** [`refactor-and-integrate/SKILL.md:91`](../../../skills/refactor-and-integrate/SKILL.md#L91) keeps a "with no commit, put the same line in the status return" fallback, while [line 96](../../../skills/refactor-and-integrate/SKILL.md#L96) now has the integration reviewer look for the trail only "in the integrate commits under that range" and marks a missing trail `[BLOCKING]`. In the no-commit case the reviewer cannot see the trail and the blocking gate fires on a compliant implementer. Name where the reviewer looks when no commit exists, or drop the fallback.
   → implemented: fallback replaced — a no-change pass carries the trail on an empty commit so the reviewer finds it under the range

5. **[MINOR]** [`docs/site/04-utility-skills/task.md:21`](../../../docs/site/04-utility-skills/task.md#L21) still bills `report-in-markdown` as "the one style guide every agent follows," which reads as the always-loaded framing the child page and `CLAUDE.md` both dropped in this change. The parent constraint requires updating `docs/site` statements this task invalidates.
   → implemented: reworded to "the house style guide"

6. **[MINOR]** `CODEX_ALWAYS_LOADED_CANARIES` in [`always_loaded_live.py:33-36`](../../../tests/harness-instruction-following/always_loaded_live.py#L33-L36) now bundles one always-loaded canary and one on-demand canary; the docstring above it was updated but the constant name still asserts the retired grouping. Rename it to match what it now covers.
   → implemented: renamed to `CODEX_SKILL_LOAD_CANARIES` (all three files)

7. **[MINOR]** Pre-existing, surfaced while checking the adjacent test edits: `test_red_static_backbone_missing_skill` in [`test_always_loaded_live.py:76-90`](../../../tests/harness-instruction-following/test_always_loaded_live.py#L76-L90) still writes `agents/implementer.md` and `agents/reviewer.md` fixtures, but `check_claude_always_loaded_static` reads `skills/*/SKILL.md`. The test passes only because the role-skill files are absent from `tmp_path`, so it no longer exercises the missing-skill path it claims. Belongs to whichever task owns the retired `agents/` surface, not necessarily this one.
   → implemented: fixture now writes role-skill `SKILL.md` files whose §Before You Start omits the load line, exercising the missing-skill path; separate maintenance commit
