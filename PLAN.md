# Multi-Agent Review Protocol — Plan

> **For agentic workers:** REQUIRED DISCIPLINE. Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md edits. Load `document-skills:skill-creator` before editing any `references/*.md` or `SKILL.md`. Apply `superRA-dev/CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action` line-by-line on every line added (DRY + Necessity tests).

**Objective:** Add a multi-agent review orchestration protocol to `skills/writing` so a research draft can be reviewed across 8 dimensions with shared pre-built context, optional deep-mode multi-perspective reviewers, and a polish-mode-friendly findings artifact — sufficient parity to retire the third-party `draft-reviewer` plugin.

**Methodology:** Add one new reference (`long-form-review.md`) that teaches only deltas from the existing scaffold (PLAN.md anatomy, agent-orchestration dispatch, handoff-doc discipline) — points at those for everything it does not adapt. Thread a thoroughness slider through `review.md`. Port the auto-fixable flag mechanically across the 8 `consistency/*.md` files. Close two small substance gaps (writing-clarity heuristics in `style.md`; definition-clarity audit in `consistency/terminology.md`). Confirm or extend LaTeX-rendering coverage in `refactor-and-compile.md`. Update routing surfaces (`SKILL.md` knowledge-files row; `CLAUDE.md` design notes). Validate end-to-end by round-tripping a real review and comparing to draft-reviewer on the same draft. Retire the marketplace entry downstream in the dotfiles repo.

**Conventions:**
- Every line in `long-form-review.md` either teaches a delta from the existing scaffold or is deleted (DRY/Necessity gate).
- Reviewer dispatch (not implementer) is the role for review-as-data work; `subagent_type: "superRA:reviewer"`, `Stage: implementation`, writing skill add-on routes via the manifest. No new Stage value.
- Doc name: `REVIEW.md` at worktree root (not `PLAN.md` — collision with workflow PLAN.md).
- Header indices live under `## Project Conventions` (or `## Document Map` if scope grows).
- Multi-perspective deep mode = 3 reviewers per dimension, with stance + ordering variation.

**Output:**
- `skills/writing/references/long-form-review.md` (new, ~40 lines)
- Edited: `skills/writing/references/review.md`, `skills/writing/references/style.md`, `skills/writing/references/consistency/{terminology,notation,cross-references,citations,numerical,math,argument-logic,code-paper}.md`, `skills/writing/references/refactor-and-compile.md`, `skills/writing/SKILL.md`, `skills/writing/CLAUDE.md`
- Out-of-repo (Task 8): `~/Dropbox/app_settings/dotfiles/agents/.agents/plugins/marketplace.json` (draft-reviewer entry removed)

**Expected Results / Hypotheses:** Protocol covers the same dimension breadth as draft-reviewer (math / clarity / consistency / argument-logic / proofreading-via-baseline / citation / code-paper). Thoroughness slider exposes quick / standard / deep with deep dispatching 3 reviewers per dimension. Auto-fixable flag is consumable by polish-mode shape C without re-judging. Real-paper round-trip produces parity-class findings vs draft-reviewer.

**Sensitivity Analysis:** Round-trip validation (Task 7) is the gate for retirement (Task 8). If parity does not hold on the validation paper, pause Task 8 and triage.

**Pipeline:** N/A — contributor work on superRA itself, no script pipeline. Verification is real-use validation per Task 7.

---

## Workflow Status

- [x] **Plan approved** — researcher signed off on the plan
- [ ] **Execution complete** — Tasks 1–7 APPROVED
- [x] **Drift tests created** — N/A (no analysis results to protect; contributor work on skill text)
- [ ] **Integrated**
- [x] **Docs finalized** — N/A (no RESULTS.md to mature into permanent record; CLAUDE.md design notes land in Task 6)
- [ ] **Finished** — PR opened or merged into main

---

## Project Conventions

Walked at planning time (2026-05-02). Re-walk on-demand only.

### Repo root
- `/Users/zhiyufu/Dropbox/package_dev/superRA-domain-writing-skills/CLAUDE.md` (HEAD): Contributor guidelines for superRA. Treat skill/agent edits as skill creation; load `skill-creator` before editing any `SKILL.md`. The DRY/Necessity gate (§Teach the Protocol, Don't Prescribe Each Action) is the most important rule — every instruction line either shapes behavior or is deleted, applied line-by-line by both implementer and reviewer. Ownership table assigns each concern to a single owner; new content goes to the owner of that concern, not duplicated. Lean agents, rich references; flat skill layout.
- `/Users/zhiyufu/Dropbox/package_dev/superRA-domain-writing-skills/README.md` (HEAD): User-facing product model.

### Module-level docs walked
- `skills/writing/CLAUDE.md` (HEAD): Records design choices for the writing vertical: mode (not phase) is top-level axis; load configuration is authority grant (light vs deep polish); intent comments live in the file, never inferred; rules are additive to baseline agent competence. The §Reviewer-dispatch invariants leave this skill section is load-bearing for the new protocol — confirms standalone review terminates at edit + commit, parallel-dispatch for multi-dim review is owned by the skill not the workflow.
- `skills/writing/SKILL.md` (HEAD): Three modes (Review / Polish / Draft), Knowledge files table, mode-routing.
- `skills/writing/references/review.md` (HEAD): Existing review-mode workflow, classification taxonomy, multi-dim parallel-dispatch pattern, intent-comments-as-yardstick.
- `skills/writing/references/consistency/*.md` (HEAD, all 8): Per-dimension reviewer references with output formats. Auto-fixable flag is the planned mechanical addition in Task 3.
- `skills/writing/references/style.md`, `structure.md`, `polish.md`, `draft.md`, `refactor-and-compile.md`, `integration.md` (HEAD): Existing knowledge files; only `style.md` and `refactor-and-compile.md` are touched in this work.

### Not walked (not reachable from the planned diff)
- `skills/{econ-data-analysis,theory-modeling,planning-workflow,implementation-workflow,integration-workflow,agent-orchestration,handoff-doc,result-protection,refactor-and-integrate,report-in-markdown,semantic-merge,worktree-data-sync,codex-superra-setup,using-superRA}/` — out-of-scope; this is writing-skill contributor work.
- `agents/` — agent role specs unchanged.
- `.codex/` — generated; touched only by `sync_codex_agents.py`.

---

### Task 1: Author `long-form-review.md`
**Depends on:** *(none)*
**Review status:** APPROVED

**Script:** `skills/writing/references/long-form-review.md` (new file)
**Input:** `skills/writing/references/review.md` (for trigger context); `skills/writing/CLAUDE.md` §Reviewer-dispatch invariants leave this skill (for the standalone-vs-workflow rule); `superRA:handoff-doc references/plan-anatomy.md` and `references/results-anatomy.md` (for what NOT to restate); `superRA:agent-orchestration` (for what NOT to restate)
**Output:** `skills/writing/references/long-form-review.md`, ~40 lines

- [x] **Step 1: Author the new reference**

Sections, in order:

1. **Trigger.** Load when scope is multi-dimensional (>1 `consistency/<dim>.md`), thoroughness is `deep`, or the target is a full-paper / pre-submission / R&R pass. (One paragraph.)

2. **Doc convention.** Named `REVIEW.md` at the worktree root (never `PLAN.md` — collision when a workflow's own PLAN.md is in play). Anatomy: PLAN.md-shaped per `superRA:handoff-doc references/plan-anatomy.md`. Inline-edit + atomic-commit discipline carries over from `superRA:handoff-doc` SKILL.md. Three adaptations:
   - **Header indices.** Shared context — notation index (key symbols → meaning + location), terminology index (key terms → definition + first-use), figures-and-tables index, cross-reference index — lives under `## Project Conventions`. For long manuscripts where the indices grow large, promote to a sibling `## Document Map` section. Orchestrator builds these once before dispatch so each parallel reviewer reads the indices instead of re-reading the manuscript cold.
   - **Per-aspect blocks ARE task blocks** per `plan-anatomy.md §Task Block Anatomy`. One block per dimension (or, in deep mode, per perspective). `**Depends on:** *(none)*` — they are parallel. Reviewer findings land in the existing review-notes blockquote inside the task block. Each finding follows the loaded `consistency/<dim>.md` output format including the `Auto-fixable: Yes / No` line.
   - **Final summary block.** Closeout artifact at the top of REVIEW.md: severity × auto-fixable counts table; top-3 priorities; pointer to each per-aspect block; auto-fixable batch table for polish-mode shape C handoff. Built by the orchestrator (or one optional final-summary reviewer pass over the assembled doc).
   - `## Workflow Status` rollup is **optional** for review-as-data — omit standalone; when a workflow rides this work, that workflow's own PLAN.md owns the rollup.

3. **Dispatch convention.** Use canonical reviewer template per `superRA:agent-orchestration §Dispatch Templates` — `subagent_type: "superRA:reviewer"`, `Stage: implementation` (no new Stage value; writing skill add-on routes via the manifest). The manuscript is the implicit "implementer output" being audited; reviewers append findings to their assigned per-aspect block in REVIEW.md instead of returning APPROVE/REVISE on a commit. Parallel-dispatch + worktree-isolation pattern applies directly. **No reviewer-of-reviewer pass** — the assembled REVIEW.md *is* the artifact; chaining adversarial review over the findings is recursion. Optional final-summary reviewer pass over the assembled doc is allowed if the orchestrator wants a sanity check.

4. **Multi-perspective deep mode.** When thoroughness is `deep`, dispatch 2–3 reviewers per dimension with diverse stances ("skeptical referee" / "constructive mentor" / "domain expert") and ordering ("forward" / "backward from conclusions" / "most complex first"). Each reviewer writes findings into its own per-perspective task block under that dimension. Closeout merges and weights by multi-agent confirmation.

The reference does **not** restate plan-anatomy task-block format, dispatch-template fields, handoff-doc inline-edit rules, or `consistency/*.md` content. Pointer-only for those.

- [x] **Step 2: Self-apply DRY + Necessity tests line-by-line**

For every line: (a) is the information already in `handoff-doc/references/plan-anatomy.md`, `agent-orchestration` dispatch templates, `review.md`, or a `consistency/<dim>.md`? If yes, point and delete the restatement. (b) Would the agent's behavior be unstable without this line? If no, delete it.

- [x] **Step 3: Update PLAN.md (mark steps `[x]`, set Review status: IMPLEMENTED), update RESULTS.md, commit atomically**

Commit message: `skill: writing — add long-form-review.md (multi-agent review protocol)`. Includes the new file + PLAN.md + RESULTS.md updates.

---

### Task 2: Thoroughness slider + cross-pointer in `review.md`
**Depends on:** Task 1
**Review status:** APPROVED

**Script:** `skills/writing/references/review.md`
**Input:** Task 1 output (`long-form-review.md`)
**Output:** Edited `skills/writing/references/review.md`

- [x] **Step 1: Add §Thoroughness section after §Workflow**

Three modes (Quick / Standard / Deep), pointer-only at `long-form-review.md` for protocol mechanics. Deep tagged "for pre-submission / R&R rounds" with the multi-perspective dispatch rule explicitly owned by `long-form-review.md` (not restated). Standard cross-references the existing §Multi-dimensional consistency reviews section to avoid restating the parallel-per-dimension mechanism. Closing line tells the agent to infer thoroughness from scope and use `AskUserQuestion` only when ambiguous, so the default is silent inference rather than a user round-trip.

- [x] **Step 2: Extend §Multi-dimensional consistency reviews paragraph**

Appended one sentence: "When N > 1, load `long-form-review.md` for the shared review-doc protocol." Pointer-only — header-indices content stays owned by `long-form-review.md` per the DRY/Necessity gate, not paraphrased here.

- [x] **Step 3: Self-apply DRY + Necessity tests on the additions**

Walked every added line. KEEP rationale per line: header is the new section, Quick/Standard/Deep entries are the new axis-to-behavior mapping (Standard uses same-file pointer, Deep uses cross-file pointer), closing line tells the agent that thoroughness inference is silent by default. The PLAN draft's "3 reviewers per dim with stance + ordering variation" qualifier on Deep was deleted as a restatement of the rule owned by `long-form-review.md`. The PLAN draft's "so each reviewer reads pre-built notation / terminology / cross-reference indices" tail on the cross-pointer was deleted as a restatement of `long-form-review.md`'s header-indices content.

- [x] **Step 4: Update PLAN.md, update RESULTS.md, commit atomically**

Commit message: `skill: writing — review.md: thoroughness slider + long-form-review pointer`.

---

### Task 3: Auto-fixable flag in 8 `consistency/*.md` output formats
**Depends on:** *(none)*
**Review status:** *(set during execution)*

**Script:** `skills/writing/references/consistency/{terminology,notation,cross-references,citations,numerical,math,argument-logic,code-paper}.md`
**Input:** existing 8 files
**Output:** all 8 files with `Auto-fixable: Yes / No` line in their Output format block

- [ ] **Step 1: Add `Auto-fixable: Yes / No` line to each file's Output format block**

For each of the 8 files, locate the `## Output format` section (typically a fenced code block with `Location:`, `Recommendation:`, etc.) and add one line as the last field:

```
Auto-fixable: Yes / No
```

Mechanical addition. Eight files, eight one-line additions, no other changes.

- [ ] **Step 2: Update PLAN.md, update RESULTS.md, commit atomically**

Commit message: `skill: writing — consistency/*.md: auto-fixable flag in output formats`.

---

### Task 4: Substance gaps — `style.md` + `consistency/terminology.md`
**Depends on:** *(none)*
**Review status:** *(set during execution)*

**Script:** `skills/writing/references/style.md`, `skills/writing/references/consistency/terminology.md`
**Input:** existing files
**Output:** edited files

- [ ] **Step 1: Add run-on / nested-clause / vague-modifier guidance to `style.md`**

In the sentence-level rules section, add a short paragraph (4–6 lines) covering:

- Run-on / nested-clause: flag sentences with 3+ embedded clauses or > 40 words that lose subject-verb tracking. Recommended fix: split.
- Vague modifiers: flag "various", "some", "several", "a number of" — the prose almost always benefits from a count or scope.

These are heuristics, additive to baseline agent writing competence. Phrase as "consider splitting" / "consider quantifying" — not blocking gates.

- [ ] **Step 2: Add §Definition-clarity audit to `consistency/terminology.md`**

Short subsection (4–6 lines): for each key term, the definition should be explicit (not assumed by the reader), precise (not circular — "X is defined as X-related"), consistent with field norms. Definitions stated in math but not in prose (or vice versa) are a flag. The reviewer flags drift; the author owns the canonical form.

- [ ] **Step 3: Self-apply DRY + Necessity tests on the additions**

- [ ] **Step 4: Update PLAN.md, update RESULTS.md, commit atomically**

Commit message: `skill: writing — close clarity heuristic + definition-audit gaps`.

---

### Task 5: LaTeX-rendering coverage in `refactor-and-compile.md`
**Depends on:** *(none)*
**Review status:** *(set during execution)*

**Script:** `skills/writing/references/refactor-and-compile.md`
**Input:** existing file
**Output:** verified or extended file

- [ ] **Step 1: Read `refactor-and-compile.md`; verify LaTeX hazards coverage**

Hazards to verify present:
- Unescaped `%`, `&`, `#`, `_` in text mode
- Broken `??` cross-references
- Missing bibliography entries
- Overfull / underfull hbox warnings
- Unclosed math-mode delimiters (unmatched `$`)
- Equation numbering gaps

If all are covered, no edit needed — record verification in this task's RESULTS.md note.

If any are missing, add a §LaTeX-rendering hazards subsection (~10 lines) listing only the missing items, one short bullet per item.

- [ ] **Step 2: Self-apply DRY + Necessity tests on any addition**

- [ ] **Step 3: Update PLAN.md, update RESULTS.md, commit atomically (only if edits were needed)**

Commit message (if edited): `skill: writing — refactor-and-compile.md: LaTeX-rendering hazards`. If verified-only with no edit, the RESULTS.md note + PLAN.md status flip lands with the next task's commit (Task 6).

---

### Task 6: Routing surfaces — `SKILL.md` knowledge-files row + `CLAUDE.md` design notes
**Depends on:** Task 1
**Review status:** *(set during execution)*

**Script:** `skills/writing/SKILL.md`, `skills/writing/CLAUDE.md`
**Input:** Task 1 output
**Output:** edited files

- [ ] **Step 1: Add row to `SKILL.md` §Knowledge files table**

Add this row at the appropriate position in the Knowledge files table:

| `references/long-form-review.md` | Multi-dimensional review (N > 1 consistency dimensions), `deep` thoroughness, or full-paper / pre-submission scope. |

- [ ] **Step 2: Add §Multi-agent review pattern subsection to `skills/writing/CLAUDE.md`**

10–15 lines recording four design choices:

(a) The protocol lives in a separate reference because each `consistency/<dim>.md` already owns its substance — `long-form-review.md` is orchestration only (DRY).

(b) The doc is named `REVIEW.md` not `PLAN.md` to avoid collision when a workflow's own PLAN.md is in play. The two coexist by name and lifecycle: PLAN.md spans the project; REVIEW.md is born for one review and dies after closeout.

(c) We did not add a `consistency/proofreading.md`. Mechanical proofreading (typos / grammar / punctuation) is baseline competence per `SKILL.md §These rules are additive`. LaTeX-rendering hazards live with the build step in `refactor-and-compile.md`.

(d) Stage value is `implementation` (no new Stage). Writing skill add-on already routes via the `using-superRA §Skill-Load Manifest` Domain add-ons table. Memory rule: do not add new `Stage:` values.

- [ ] **Step 3: Self-apply DRY + Necessity tests on the additions**

- [ ] **Step 4: Update PLAN.md, update RESULTS.md, commit atomically**

Commit message: `skill: writing — SKILL.md routing + CLAUDE.md design notes for multi-agent review`.

---

### Task 7: Real-paper validation
**Depends on:** Task 1, Task 2, Task 3, Task 4, Task 5, Task 6
**Review status:** *(set during execution)*

**Script:** N/A — manual orchestrated validation pass
**Input:** A research draft of the user's choosing
**Output:** Validation note in RESULTS.md confirming the protocol round-trips correctly and findings are at parity with draft-reviewer

- [ ] **Step 1: Stop point — ask user which paper draft to use**

User-facing question via `AskUserQuestion` (or plain text fallback): "Which paper draft should I use for validation? (a path to a `.tex` / `.md` / `.qmd` file). The validation will round-trip a multi-dim review using the new protocol and compare findings to a draft-reviewer pass on the same draft."

Log the answer in `## Decisions` before dispatching.

- [ ] **Step 2: Round-trip a multi-dim standard review**

Run a standard-thoroughness multi-dim review on the chosen draft using the new protocol. Confirm:
- Orchestrator builds the header indices once before dispatch (notation, terminology, figures, cross-refs).
- Parallel reviewers append findings cleanly to their assigned per-aspect task blocks.
- Closeout summary assembles correctly with severity × auto-fixable counts table.
- Auto-fixable flag is set on findings.

- [ ] **Step 3: Round-trip a deep-mode review on the same draft (if user has bandwidth)**

Run a deep review with multi-perspective dispatch (3 reviewers) on at least one dimension. Confirm dedup of findings across perspectives works; multi-agent-confirmed findings are weighted higher in the closeout summary.

- [ ] **Step 4: Compare to draft-reviewer output on the same draft**

Run the existing `draft-reviewer` plugin on the same draft. Compare per-dimension findings — confirm substance parity (acknowledging stylistic differences in framing). Document any genuine substance gaps in RESULTS.md; if a gap is found that blocks retirement, escalate.

- [ ] **Step 5: Validate quick-mode opt-out**

Run a small short-paragraph review with `quick` thoroughness. Confirm `long-form-review.md` is **not** loaded — it must be opt-in only.

- [ ] **Step 6: Update PLAN.md, update RESULTS.md, commit atomically**

Commit message: `validation: writing — multi-agent review protocol round-tripped vs draft-reviewer`.

---

### Task 8: Retire `draft-reviewer` (downstream of Task 7)
**Depends on:** Task 7
**Review status:** *(set during execution)*

**Script:** `~/Dropbox/app_settings/dotfiles/agents/.agents/plugins/marketplace.json` (out of repo)
**Input:** Task 7 validation note confirming substance parity
**Output:** `marketplace.json` with the `draft-reviewer` entry removed; cached plugin directory optionally archived

- [ ] **Step 1: Verify marketplace.json path and current entry**

```bash
grep -n "draft-reviewer" ~/Dropbox/app_settings/dotfiles/agents/.agents/plugins/marketplace.json || echo "not found in expected path; locate via:"
find ~/Dropbox/app_settings/dotfiles -name "marketplace.json" 2>/dev/null
```

- [ ] **Step 2: Remove the `draft-reviewer` entry from marketplace.json**

Edit `marketplace.json` in the dotfiles repo. Commit there with a separate commit (NOT in the writing-skills repo). Commit message: `agents: retire draft-reviewer plugin (superseded by writing skill multi-agent review)`.

- [ ] **Step 3: Optionally archive the cached plugin directory**

```bash
mkdir -p ~/.claude/plugins/cache/agent-contract/_archived/
mv ~/.claude/plugins/cache/agent-contract/draft-reviewer ~/.claude/plugins/cache/agent-contract/_archived/draft-reviewer 2>/dev/null || true
```

- [ ] **Step 4: Confirm removal**

Restart Claude Code session and confirm the `draft-reviewer:*` agents are no longer listed in `Agent` subagent types.

- [ ] **Step 5: Update PLAN.md (mark IMPLEMENTED)**

Task 8 does NOT ride the writing-skills PR. Mark IMPLEMENTED only after the dotfiles change is committed there.
