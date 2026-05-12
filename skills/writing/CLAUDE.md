# writing — Contributor Notes

> Read `superRA-dev/CLAUDE.md` for the repo-wide design rules (DRY, Necessity, ownership boundaries, anti-patterns). Apply them line by line when editing anything in this directory. This file records the high-level design choices specific to the writing vertical so future contributors do not re-litigate them.

## Why this skill exists

The first build (2026-04-19 → 2026-05-02) cloned `econ-data-analysis`'s skeleton — Iron Law plus three concurrent disciplines (Preserve / Improve / Verify) mirroring Describe / Analyze / Validate — and routed references by superRA workflow phase (PLAN / IMPLEMENT / INTEGRATE). The clone framing was not load-bearing for writing work: most writing is standalone, the three "disciplines" did not factor cleanly, "preserve voice" overspecified what to keep, and the per-phase reference loading misled an agent invoked without a workflow. The redesign keeps the substantive content (style rules, structure rules, eight consistency dimensions, refactor-and-compile, build commands) and rebuilds the skeleton around how the skill is actually used. The motivating lesson — **do not clone an architectural pattern from another vertical without checking that its axes are load-bearing for yours** — is why this contributor file exists.

## What composes vs. what is new

The redesign **moved within the existing domain-add-on slot**. No new `Stage:` value, no new workflow stage, no new orchestration mechanism. The Skill-Load Manifest row in `using-superra` already routed `superRA:writing` correctly; routing surface text was refreshed but the slot is unchanged. `planning-workflow`, `implementation-workflow`, `integration-workflow`, `agent-orchestration`, `result-protection`, `refactor-and-integrate`, `semantic-merge` all work unchanged. **If you find yourself adding a workflow stage or workflow-shaped concept here, stop**: the concern almost certainly belongs in a workflow skill, or this skill should be invoked from one of them.

## Preserve substance, polish prose

The single principle that replaced the Iron Law and the Three Concurrent Disciplines. **Preserve** the argument, the logic, the structure, the technical claims, the author's intent, the tone. **Polish** wording, sentence structure, clarity, parallelism, hedging calibration, flow, mechanical correctness. **Do not restructure or change claims unless explicitly asked.** It differs from the Iron Law in two specific ways: (1) "voice" as diction/register/sentence-shape is dropped — wording is the editing target, not a preservation target; (2) the strict "co-author would recognize the diff" test is gone, because in practice authors dump in-progress work and expect it cleaned up. The principle reads as one short paragraph in `SKILL.md`; there is no Common Rationalizations table and no doctrine.

## The rules are additive, not exhaustive

`SKILL.md` opens with an explicit framing: agents already know how to write, proofread, replace awkward wording, fix grammar and typos, and calibrate tone — this skill does not retrain that, it adds the discipline academic writing on shared author drafts needs. The risk this defends against is the agent reading a tightly-specified rule set (the edit-vs-propose-vs-ask matrix; the eight consistency dimensions; the mode-routing table) as the *complete* program and silently dropping its baseline writing competence. The framing line "Silence on a concern is not permission to ignore it" is load-bearing — without it, well-disciplined agents become rule-bound and miss the obvious typo that no rule names. When adding a new constraint here, check that it survives the additive framing: it should narrow or redirect a behavior the agent would otherwise produce, not stand in for the behavior itself.

## Mode, not phase, is the top-level axis

`SKILL.md` routes by **working mode** — Review, Polish, Draft — not by superRA workflow phase. The earlier per-phase routing was wrong because writing tasks are mode-shaped: a polish request is a polish request whether or not a `PLAN.md` exists, and the operational guidance (input shapes, edit-vs-propose-vs-ask, build discipline) does not vary by phase. Modes share knowledge files (style, structure, consistency dimensions, refactor-and-compile) but differ in workflow and authority. If a future change wants to reorganize the top-level routing back around phases or stages, revisit whether the candidate axis actually changes the operational guidance — modes do; phases do not.

## Load configuration is the authority grant

A subtle but load-bearing rule: **light vs deep polish is purely a load decision**. Light polish loads `polish.md` + `style.md`; deep (structural) polish loads `polish.md` + `style.md` + `structure.md`. There is no separate "deep polish" workflow, no procedural switch, no extra confirmation. The polish agent never has to reason "am I authorized to restructure?" — the loaded reference set answers that. `SKILL.md §Mode routing` only loads `structure.md` when the request explicitly authorizes structural edits, so an unauthorized restructure attempt fails closed at load time. Preserve this property when adding new modes or new authority distinctions: encode the distinction in *what loads*, not in conditional prose inside a single reference.

## Inline directives: TODO-as-task, DO-NOT-EDIT-as-hands-off

The default is **inverted from the prior build**. Inline `TODO`, `% TODO:`, `\todo{...}`, `[fill in]`, `??`, `XXX`, and crude or placeholder phrasing are **work assigned to the agent** — clean them up inside scope. The author signals leave-alone with an explicit `DO NOT EDIT` (or equivalent hands-off marker). The earlier `collaboration.md` made TODOs sacred and required the author to authorize edits, which was wrong for the dominant real workflow: the author dumps work-in-progress and expects it cleaned. Explicit hands-off markers cost the author one line; protecting every TODO by default cost every polish pass a confirmation round.

## Intent comments live in the file, not the conversation

When editing `.tex` / `.md` / `.qmd`, agents record paragraph and section purpose as inline comments (`% intent: …` for `.tex`, `<!-- intent: … -->` for `.md` / `.qmd`) on the line immediately above the paragraph. **Draft mode writes the intent first** from the user's request, as the drafting brief, and the comment ships with the prose. **Polish mode preserves pre-existing intent comments** (they guide the polish; on conflict between text and intent the text wins, since the author may have rewritten without updating the comment — ask, or update the intent to match the text and flag). **Polish mode does not invent intent comments** — intent always comes from the author, never from agent inference; if a paragraph lacks one and the polish needs the disambiguation, the agent asks. **Review mode** uses intent comments as the yardstick — drift between stated intent and prose is a finding.

Two design choices behind this. First, the convention lives in the source file rather than in the conversation because writing tasks span sessions and context windows: a fresh agent reading the `.tex` next month has only the file. Second, inferred intent comments were considered and rejected — a comment looks authoritative once written, and an agent's reading of the prose is exactly the kind of guess that future agents will mistake for the author's stated purpose. Leaving paragraphs uncommented is strictly safer than corrupting the intent surface with guesses.

## Reviewer-dispatch invariants leave this skill

Standalone invocations of `writing` terminate at edit + commit (or at findings + commit, for review mode). The "reviewer dispatch is never skipped" invariant from the earlier `workflow.md` was removed: that invariant belongs to `implementation-workflow` and the other workflow skills, which own it for any writing task that rides the full pipeline. Keeping it inside `writing` would have forced every standalone polish to dispatch a reviewer, which is wrong for the dominant use case (small iterative edits with the main agent). Parallel-dispatch for multi-dimensional consistency reviews survives in `review.md` as a behavior the review-mode agent applies when scope is multi-dimensional — that is a within-skill technique, not a workflow invariant.

## Multi-agent review pattern

The orchestration protocol for multi-dimensional / deep / full-paper review lives in `references/long-form-review.md`. Four design choices that future contributors should not re-litigate:

- **Orchestration-only reference.** The substance of every dimension already lives in its `consistency/<dim>.md`; `long-form-review.md` carries dispatch shape, the shared-doc convention, and the deep-mode multi-perspective rule, and points at the dimension files for everything else. If a candidate addition restates per-dimension judgment, it belongs in the dimension file, not here.
- **Shared doc is `REVIEW.md`, not `PLAN.md`.** Naming the review artifact `PLAN.md` would collide with the workflow's own `PLAN.md` whenever the review rides one. The two coexist by name and lifecycle: `PLAN.md` spans the project; `REVIEW.md` is born for one review and dies at closeout (delete or archive). A future "just reuse PLAN.md" suggestion needs to solve the collision before it is reopened.
- **No `consistency/proofreading.md`.** Mechanical proofreading (typos, grammar, punctuation) is baseline agent competence per `SKILL.md §These rules are additive` and does not need a dimension file. LaTeX-rendering hazards — the one mechanical concern that is not baseline — live with the build step in `refactor-and-compile.md` because that is where the binary fails.
- **No new `Stage:` value.** Review-as-data dispatch reuses `Stage: implementation`; the writing skill add-on already routes via the `using-superRA §Skill-Load Manifest` Domain add-ons table. Adding a `Stage: review` would fork the manifest for one workflow that fits the existing slot — which is the recurring memory rule for this repo.
- **Fix-tier (`mechanical` / `conventional` / `authorial`) in every `consistency/<dim>.md` output format.** Replaces an earlier binary `Auto-fixable: Yes / No` flag (2026-05-02 → 2026-05-05). The binary forced a continuous axis (supervision cost) into two buckets and pushed operational triage into the review output, which made the reviewer pre-judge what polish would do. The tier is honest about the spectrum and lets polish-mode shape C batch `mechanical`, log `conventional` per item, and surface `authorial` to the author. Defined once in `references/review.md §Fix tiers` and reused at a second call site (polish-mode internal triage — see §Polish-mode triage below); the eight `consistency/<dim>.md` output blocks reference the definition. (Tier names re-cut 2026-05-08 from the prior `judgment` / `decision` to `conventional` / `authorial` after the `judgment` vs `decision` line collapsed into agent confidence — the sequence/set/force test in `review.md §Fix tiers` is the load-bearing reason against re-introducing the older names.) If a future contributor wants to compress the tiers back to a flag, the binary's failure mode is the load-bearing reason it was rejected — re-litigating requires a new failure mode, not a preference for terseness.

## Polish-mode triage

Fix tiers are a **shared apply-discipline vocabulary** used at two call sites: review-mode output (the `Fix:` line in each `consistency/<dim>.md` finding) and polish-mode internal triage (the apply-vs-surface decision for each diagnosed issue in `polish.md §Triage`). One vocabulary, two call sites. A future contributor proposing a separate polish-side vocabulary must argue why two beat one for the same axis (supervision cost of being wrong about the fix).

The polish-mode call site exists to close an under-editing failure mode discovered 2026-05-06: a polish-mode pass shipped only typo fixes on a paragraph with substantive prose issues (weak topic sentence, nominalized opener, broken parallelism). Root cause was framing suppression — `polish.md §Minimal-edit discipline` named over-editing as the dominant failure mode and was silent on under-editing, which the agent read as "stay close to mechanical correctness." The fix is symmetric framing (over- and under-editing as equal failure modes; the minimal-edit rule constrains the size of each fix, not the count of fixes) plus a named surface path (`§Triage`) so that *not silently fixing* an `authorial`-tier issue is a recognized outcome rather than under-editing. Future contributors tempted to put back a "watch out for over-editing" warning without naming the symmetric failure must re-read this entry — the original framing's failure mode is the load-bearing reason against re-introducing the imbalance.

The original feedback note that triggered this work (`skills/writing/feedback_polish_under_editing.md`) was deleted after absorption; recover via `git log --diff-filter=D -- skills/writing/feedback_polish_under_editing.md`.

## Stage-scoped references

References load **only when the mode that needs them runs**. `review.md`, `polish.md`, `draft.md` are mode files and load by mode. `style.md`, `structure.md`, `consistency/*.md`, `refactor-and-compile.md` are knowledge files and load when the mode that needs them runs. `integration.md` loads only when the writing task is riding `integration-workflow`. There is no "load at every dispatch" reference — the body of `SKILL.md` carries everything that must be in scope unconditionally.

## What this skill deliberately does not carry

- **Severity tagging on heuristic style/structure rules.** The earlier `[BLOCKING]` / `[ADVISORY]` decoration on style and structure heuristics was the symptom of the doctrinal framing. Heuristics with explicit "do NOT apply when …" exceptions are not verdict-determining. Severity tagging survives only on `consistency/*.md` reviewer outputs (where it shapes the output format) and on `refactor-and-compile.md` build gates (where it gates a real binary).
- **Reviewer verdict protocol boilerplate.** Each knowledge file used to carry a `## Reviewer verdict protocol` block; that ritual lives in workflow skills now and is gone from the writing references.
- **The Iron Law and the Three Concurrent Disciplines.** Replaced wholesale by Preserve substance, polish prose. Cross-references to `§Three Concurrent Disciplines §Verify` and "Walked in addition to SKILL.md §Three Concurrent Disciplines" were swept across all knowledge files and routing surfaces.

## Extension patterns

**Adding a new check or rule.** Decide which mode needs it. If it is a sentence-level rule, it belongs in `style.md`; structural, in `structure.md`; consistency-dimension-specific, in the relevant `consistency/*.md`; build-related, in `refactor-and-compile.md`. Walk the DRY/Necessity tests in repo `CLAUDE.md` before merging — most candidate rules are restatements of an existing one.

**Adding a new mode.** Strong default: don't. Three modes cover Review / Polish / Draft, which is the actual taxonomy of how authors invoke writing help. If a new mode is genuinely needed, give it its own mode file with workflow + authority, route it from `SKILL.md §Mode routing`, and check that the loaded reference set is the authority grant — not a procedural switch in prose.

**Adding a new knowledge file.** Only when the content has a load condition the existing files cannot trigger. Add the row to `SKILL.md §Knowledge files` with an explicit "load when". References stay one level deep from `SKILL.md`. The eight `consistency/*.md` files are an exception — they are split for parallel-reviewer dispatch, and that split is load-bearing.

**Tightening reviewer-dispatch behavior.** First check whether the change belongs in a workflow skill (almost always yes). The writing skill itself does not enforce reviewer dispatch; behavior changes that look like "every polish must X" are workflow-level.

## History

The skill was first built across eight tasks on the `domain/writing-skills` branch (2026-04-19 → 2026-05-02), then redesigned across five tasks on the same branch (2026-05-02). The first build's per-phase routing and Iron-Law-and-Disciplines framing came from cloning `econ-data-analysis`; the redesign replaced both with mode-based routing and the Preserve-substance-polish-prose principle. The `TODO`-as-task default, the load-as-authority-grant rule, the intent-comment discipline, and the reviewer-dispatch-leaves-this-skill decision all emerged from concrete user feedback during planning; if a future change triggers the instinct to reverse any of them, re-read the §Decisions entries on the original `PLAN.md` (preserved in git history on this branch).


## Sources

- Chaubey, V. (2018), *The Little Book on Research Writing* (BulletBooks).
- Minto, B. *The Pyramid Principle* — governing idea, MECE, SCQ.
- Little Red Schoolhouse (UChicago ENGL 13000/33000) — actions-in-verbs, character, cohesion, information flow, argument structure.

## Audience awareness as an upstream audience-model discipline

(2026-05-11.) `SKILL.md §Write to the reader, not the conversation` carries the principle and the upstream protocol — identify the audience, build their information set, check every term and reference against it before editing. The principle is in `SKILL.md` (not in a reference) because it is unconditional: every Review, Polish, and Draft task starts the same way, and `style.md` is not loaded by every Review scope. `style.md §Audience` carries the line-level marker families and replacement patterns; it is the safety net for sentence-scoped editing when the upstream check did not catch a leak. The split is the same pattern used for "Preserve substance, polish prose" (principle in SKILL.md, operational guidance in references).

The rule is framed around "any audience-bound document," not solely the academic paper, even though academic papers are the skill's primary case. The deliberate generalization keeps the principle usable when the skill polishes a slide deck, a working-paper note, a replication-package README, or a referee response. Examples in both SKILL.md and `style.md §Audience` stay paper-flavored so the canonical case reads cleanly; the marker families themselves do not name the document type.

Future contributors tempted to collapse the rule into a single location should re-check: collapsing into `style.md` would lose the Review-scope coverage that does not load style; collapsing into SKILL.md would force every Review agent to load the marker families even when style is not in scope. Future contributors tempted to re-narrow the rule to "academic paper" specifically should re-check which non-paper documents the writing skill is being invoked on; the breadth is intentional and cheap.
