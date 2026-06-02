---
title: "No-Knowledge-Lost Coverage Audit"
status: approved
depends_on:
  - 02-coupled-surfaces
  - 03-report-commit-model

tags: []
created: 2026-06-01
---

## Objective

Prove the **no-knowledge-lost invariant** from the parent §Conventions for the whole redesign. The pre-redesign baseline is commit `72671d50` (the last commit before the user's redesign edits and this subtree). Audit against that baseline's versions of the touched files, then confirm every intended change landed. Touched surfaces: `agents/implementer.md`, `agents/reviewer.md`, the two generated `direct-mode-*` references, the two `superra_*.toml`, `skills/using-superRA/SKILL.md`, `skills/report-in-markdown/SKILL.md`, `skills/superplan/references/thorough-planning.md`, the new planning-review reference, and `skills/codex-superra-setup/scripts/sync_codex_agents.py`.

**Method.** Snapshot the baseline versions (`git show <baseline-sha>:<path>`). Enumerate every distinct behavior-shaping instruction in the baseline surfaces. For each, record its new home and confirm it is reachable by the role that needs it through that role's real load path — or mark it an intentionally-dropped duplicate whose surviving copy is still reachable. Removing a duplicate is fine; removing or stranding the only copy is not.

**Must explicitly resolve:**
- The implementer Reproducibility sub-block the user deleted (re-runnable results, correct relative paths) — confirm it is covered by the active domain skills' checklists, or re-add a minimal cross-domain line.
- Planning-review mechanics — fully present in the new reference and reachable via the new manifest row.
- report-in-markdown load-map conditions — reachable after the §Load map removal.
- The ownership-boundary principle and the commit-message guidance — reachable in their new homes.
- The reporting-model collapse (task 03): the substance the old multi-field report carried (Summary, Key findings, Doc edits) now lives in the commit body + `## Results`, not stranded; and no report consumer (`agent-orchestration` §Handling Implementer Status / §Review Status Reference, `superimplement` Step 2) relied on a removed field.
- The §Task Interface planner-depth pointer (task anatomy / status lifecycle / objective+results templates → `task-system/references/planning.md`) that the user's wip edit dropped — confirm it stays reachable for implementer/reviewer subagents (currently via `task-system/SKILL.md`, which is load-on-demand). Surfaced by the task-02 review as an advisory.

**Also confirm:** generated artifacts match sources (`sync_codex_agents.py --scope project --check`), generator tests pass, and `task_check.py --plan-root superRA` is clean.

**Output:** a coverage table in `## Results` — each baseline unit → new home → reachable-by-role path → status (kept / relocated / dedup-survivor / re-added). Any genuinely lost unit is a `[BLOCKING]` finding to fix before this task is approved.

## Planner Guidance

This mirrors the approach proven in `../../lean-interface/05-coverage-audit`. Reuse its snapshot-and-enumerate method. The audit is read-and-verify plus small repair edits only; if it surfaces a large gap, that is a signal to re-dispatch the owning task (01 or 02), not to fix it wholesale here.

## Results

**Verdict: PASS — one knowledge gap found and repaired in-place; zero remaining LOST units, zero dangling pointers, all three blocking gates green.** Every distinct behavior-shaping instruction in the baseline surfaces is accounted for after the redesign and reachable by the role that needs it through that role's real load path. The one genuinely-stranded unit (the reviewer's methodology-deference stance) was the small repair edit this task is authorized to make; all other removals are duplicate-collapses, deliberate relocations with a surviving reachable copy, or the user's own intentional wip trims with reachable substance.

**Baseline:** pre-redesign SHA `72671d50` (last commit before the user's wip redesign edits `2398a188` and this subtree). Snapshots taken with `git show 72671d50:<path>` for all touched surfaces. The new planning-review reference ([planning-review.md](../../../../../skills/superplan/references/planning-review.md)) has no baseline — it is the relocation target for the reviewer's deleted §Planning Review Mode, so it is audited as a destination, not a source.

### Repair made by this task

The baseline reviewer persona carried a **methodology-deference stance**: *"The researcher chose the methodology — your job is to verify the implementation, not to second-guess the approach."* The redesign's new reviewer persona (which the user broadened with an own-judgment-beyond-checklists paragraph) dropped this line, and it had **no surviving home**: the §Review Protocol guidance-vs-objective framing protects the *implementer's* route choices, not the *researcher's* methodology choice from reviewer second-guessing. This was a stranded only-copy, not a dedup. Re-added one clause to the reviewer persona, worded to coexist with the own-judgment paragraph ([reviewer.md:11](../../../../../agents/reviewer.md#L11)): "The researcher chose the methodology — verify the implementation rather than second-guessing a sound approach you would have chosen differently." Regenerated the two reviewer artifacts ([direct-mode-reviewer.md](../../../../../skills/using-superRA/references/direct-mode-reviewer.md), [superra_reviewer.toml](../../../../../.codex/agents/superra_reviewer.toml)) so the clause propagated; `--check` exits 0.

### Coverage table

Classification key: **K** = kept-in-place, **R** = relocated (new home reachable by the consuming role), **D** = dedup-survivor (≥1 reachable copy remains), **ID** = intentionally dropped by an explicit decision (the user's wip edit and/or a task spec), with substance still reachable, **RA** = re-added by this task, **LOST** = no home found.

| # | Baseline unit | Baseline location | New home | Reachable-by path | Class |
|---|---|---|---|---|---|
| 1 | Reviewer "be thorough and adversarial / missed real issue worse than flagged non-issue" | reviewer persona | reviewer persona ([reviewer.md:15](../../../../../agents/reviewer.md#L15)) | reviewer (preload) | K |
| 2 | Reviewer methodology-deference ("verify, don't second-guess the approach") | reviewer persona | reviewer persona ([reviewer.md:11](../../../../../agents/reviewer.md#L11)) | reviewer (preload) | RA |
| 3 | Reviewer own-judgment-beyond-checklists paragraph (user-added) | reviewer persona | reviewer persona ([reviewer.md:17](../../../../../agents/reviewer.md#L17)) | reviewer (preload) | K |
| 4 | Implementer evidence-first / "Bad analysis worse than no analysis" stance | implementer persona + §Execution Protocol | §Execution Protocol ([implementer.md:27](../../../../../agents/implementer.md#L27)) | implementer (preload) | K |
| 5 | `## Dispatch Inputs` one-liner (both specs) | §Dispatch Inputs | folded into §Before You Start lead ([implementer.md:15](../../../../../agents/implementer.md#L15), [reviewer.md:21](../../../../../agents/reviewer.md#L21)) | both | R |
| 6 | Load-skills-per-manifest step (both) | §Before You Start #1 | §Before You Start #1 ([implementer.md:17](../../../../../agents/implementer.md#L17), [reviewer.md:23](../../../../../agents/reviewer.md#L23)) | both | K |
| 7 | Load `Additionally:`-named skill (both) | §Before You Start #2 | §Before You Start #2 | both | K |
| 8 | Read task via `task_read.py` + inherited context (both) | §Before You Start #3 | §Before You Start #3 ([implementer.md:19](../../../../../agents/implementer.md#L19), [reviewer.md:25](../../../../../agents/reviewer.md#L25)) | both | K |
| 9 | Implementer "delta is only a pointer / task.md authoritative" | impl §Before You Start #3 tail | dropped by user wip `2398a188`; task 03 spec says "preserve, do not revert." Reviewer retains "Paraphrased summaries are not authoritative" ([reviewer.md:25](../../../../../agents/reviewer.md#L25)) | impl: intentional user trim; substance survives in reviewer copy | ID |
| 10 | Implementer "apply scoped conventions in inherited context before editing" | impl §Before You Start #4 | dropped by user wip `2398a188` | impl: intentional user trim; convention-fit enforcement lives in `refactor-and-integrate` §Project Doc Audit (manifest-loaded at `Stage: integration`) | ID |
| 11 | Reviewer scoped-convention enforcement ("ignoring inherited convention = MAJOR finding", walk subtree READMEs, Project Doc Audit) | rev §Before You Start #4 | dropped by user wip `2398a188`; heavyweight enforcement reachable in `refactor-and-integrate` §Project Doc Audit ([SKILL.md:28](../../../../../skills/refactor-and-integrate/SKILL.md#L28), `[BLOCKING]` at [SKILL.md:91](../../../../../skills/refactor-and-integrate/SKILL.md#L91)) loaded by the integration reviewer | integration reviewer (manifest `integration` row) | ID |
| 12 | Implementer "Ask questions before starting if unclear" | impl §Before You Start #5 | §Escalation "Ask for clarification rather than guessing" ([implementer.md:136](../../../../../agents/implementer.md#L136)) | implementer | R |
| 13 | Reviewer "read the actual code, verify independently" | rev §Before You Start #5 + §Read Code First | §Before You Start #4 + §Read Files First ([reviewer.md:26](../../../../../agents/reviewer.md#L26), [reviewer.md:34](../../../../../agents/reviewer.md#L34)) | reviewer | K |
| 14 | Editing-discipline "read §Handoff at task end, not dispatch" pointer | both §Before You Start tail | dropped by user wip; §Handoff is self-evident on read — no behavior change | both | ID |
| 15 | Implementer evidence-before-claims 5-step gate | §Self-Review Before Reporting | §Self-Check #1 ([implementer.md:33](../../../../../agents/implementer.md#L33)) | implementer | R |
| 16 | Implementer completeness checks (spec done, outputs saved, Results carries summary) | §Self-Review Completeness | §Self-Check #2 ([implementer.md:43](../../../../../agents/implementer.md#L43)) | implementer | R |
| 17 | Implementer Reproducibility sub-block (format convention, re-runnable, relative paths) | §Self-Review Reproducibility | folded into §Self-Check #2 completeness bullet ([implementer.md:48](../../../../../agents/implementer.md#L48)); double-covered by `econ-data-analysis` (`[BLOCKING]` re-run describe, pipeline-file reproducibility, relative-path guidance) and `theory-modeling` Gate 4 Verification & Rendering | implementer + active domain skill | D |
| 18 | Implementer domain-checklist self-walk | §Self-Review Domain walk | §Self-Check #4 ([implementer.md:52](../../../../../agents/implementer.md#L52)) | implementer | R |
| 19 | Implementer pre-commit editing-hygiene checklist (edits inside task.md, no deleted review items, stale-content, figures, doc-before-report) | §Pre-Commit Self-Check | merged into §Self-Check #3 + #5 ([implementer.md:50](../../../../../agents/implementer.md#L50), [implementer.md:54](../../../../../agents/implementer.md#L54)); shared editing principles in `using-superra` §Task Interface | implementer | D |
| 20 | `## Handoff — Unified Across Stages` heading (both) | §Handoff heading | renamed `## Handoff` ([implementer.md:60](../../../../../agents/implementer.md#L60), [reviewer.md:89](../../../../../agents/reviewer.md#L89)); generator updated in lockstep | both | K |
| 21 | Editing Etiquette: shared-principles pointer + role-specific stay-within-task rule (both) | §Editing Etiquette | §Editing Etiquette ([implementer.md:76](../../../../../agents/implementer.md#L76), [reviewer.md:103](../../../../../agents/reviewer.md#L103)) | both | K |
| 22 | "What You Own, What You Don't" → positive framing | §What You Own, What You Don't | §What You Own ([implementer.md:64](../../../../../agents/implementer.md#L64), [reviewer.md:93](../../../../../agents/reviewer.md#L93)); "What You Don't" dropped per task 01 | both | ID |
| 23 | Implementer ownership (Results, status transitions, `→ implemented:`) | §What You Own | §What You Own ([implementer.md:66](../../../../../agents/implementer.md#L66)) | implementer | K |
| 24 | Implementer §How You Fix REVISE-round mechanics (orchestrator-annotation handling, `→ implemented:` append, example block) | §How You Fix | §How You Fix ([implementer.md:78](../../../../../agents/implementer.md#L78)) | implementer | K |
| 25 | Ownership-boundary principle (edit only what you own; raise others' content) | role specs §What You Own + using-superRA §Task Interface | using-superRA §Task Interface ([SKILL.md:47](../../../../../skills/using-superRA/SKILL.md#L47)) + each spec §What You Own | all (preload) | K/D |
| 26 | Reviewer §Review Protocol (Read Files First, Verify Independently, Severity, Verdict) | §Review Protocol | §Review Protocol ([reviewer.md:30](../../../../../agents/reviewer.md#L30)) | reviewer | K |
| 27 | Reviewer Planning Review Mode (handoff-readiness/design-review, task_check, verdict, note ownership, no-status-edit) | reviewer §Planning Review Mode + clauses in §Before You Start / §What You Own / §How You Write | [planning-review.md](../../../../../skills/superplan/references/planning-review.md) (whole) + one-line pointer in reviewer ([reviewer.md:28](../../../../../agents/reviewer.md#L28)) | reviewer via manifest `planning-review` row → reference | R |
| 28 | Severity/verdict defined once, referenced not restated | rev §Severity + §Verdict; §How You Write restated | defined once in §Review Protocol; §How You Write references it ([reviewer.md:107](../../../../../agents/reviewer.md#L107)) | reviewer | D |
| 29 | Reviewer §How You Write (first-review + re-review sequences, orchestrator-override handling, CRITICAL-no-silent-override, re-review scope, integration surviving-diff sweep) | §How You Write a Review | §How You Write a Review ([reviewer.md:105](../../../../../agents/reviewer.md#L105)) | reviewer | K |
| 30 | Commit-message guidance (subject `implement/review task <path>`, body=delta, verdict/status not in subject) | impl §Update and Commit + rev §How You Write commit step | §Commit ([implementer.md:104](../../../../../agents/implementer.md#L104), [reviewer.md:133](../../../../../agents/reviewer.md#L133)); resolves parent §Conventions Commit convention | both | R |
| 31 | Commit-hygiene staging rule (stage by path, no `-A`, `git diff --cached`) | both, inline | both §Commit point to `using-superra` §Commit Hygiene ([implementer.md:106](../../../../../agents/implementer.md#L106), [reviewer.md:135](../../../../../agents/reviewer.md#L135)) | both | D |
| 32 | Parallel-worktree return rule | impl §Update and Commit | §Report Format worktree-return bullet ([implementer.md:121](../../../../../agents/implementer.md#L121)) | implementer | R |
| 33 | Implementer report fields: Summary, Key findings, Concerns, Doc edits | §Report Format (multi-field) | collapsed (task 03): Summary→commit body + `## Results`; Key findings→`## Results`; Doc edits→commit delta; Concerns→`DONE_WITH_CONCERNS` enum + `## Results` caveat ([implementer.md:115](../../../../../agents/implementer.md#L115)) | implementer; orchestrator reads via commit + `## Results` | R/ID |
| 34 | Reviewer report fields: Review Summary, Headline findings, Doc edits | rev §Report Format | collapsed (task 03): content lives in `## Review Notes`; return = Assessment + SHA ([reviewer.md:143](../../../../../agents/reviewer.md#L143)) | reviewer; orchestrator reads `## Review Notes` | R/ID |
| 35 | Reviewer closing `ACTION REQUIRED (REVISE)` trailer | nested in §Handoff | superseded by the collapsed §Report Format (status enum drives re-dispatch); task 01 noted as trailer, task 03 collapsed reporting | reviewer | ID |
| 36 | report-in-markdown file-reference rule (markdown links, relative paths) | §File-reference rule | §File-reference rule ([SKILL.md:13](../../../../../skills/report-in-markdown/SKILL.md#L13)) | all (preload) | K |
| 37 | report-in-markdown Load map (rich-content / baseline-io load conditions, attachments default) | §Load map table | §References bullets each carry their "Load when…" condition ([SKILL.md:25-26](../../../../../skills/report-in-markdown/SKILL.md#L25)); `attachments/` defaults live in `rich-content.md` §Figures, loaded when figures in scope | all | D |
| 38 | using-superRA §Task Interface planner-depth pointer (task anatomy / status lifecycle / objective+results templates → planning.md) | §Task Interface | dropped from §Task Interface by user wip; reachable via `task-system/SKILL.md` §Routing → `references/planning.md` ([task-system SKILL.md:84](../../../../../skills/task-system/SKILL.md#L84)), load-on-demand. Executing agents need only read/edit (in §Task Interface) + status enum + body vocab (in role specs §What You Own); planner-depth is planner-facing | impl/rev via on-demand `task-system`; planner via manifest | R |
| 39 | using-superRA domain add-on routing table (econ/theory/writing trigger conditions) | §Domain add-ons (topic-driven) table | trigger conditions folded into §Skill Inventory domain rows ([SKILL.md:67-69](../../../../../skills/using-superRA/SKILL.md#L67)); §Domain add-ons now points to those descriptions ([SKILL.md:112](../../../../../skills/using-superRA/SKILL.md#L112)) | all | R |
| 40 | manifest `planning-review` row + "reviewer.md owns its mode" note | §Skill-Load Manifest | row now names `planning-review.md` as required skill + owner ([SKILL.md:99](../../../../../skills/using-superRA/SKILL.md#L99), [SKILL.md:106](../../../../../skills/using-superRA/SKILL.md#L106)) | all | R |
| 41 | thorough-planning §Planning Review reviewer-mechanics prose (verdict, note ownership) | thorough-planning.md §Planning Review | relocated to [planning-review.md](../../../../../skills/superplan/references/planning-review.md); thorough-planning keeps planner-facing dispatch context + pointer ([thorough-planning.md:129](../../../../../skills/superplan/references/thorough-planning.md#L129)) | planner (thorough-planning) / reviewer (reference) | R |
| 42 | sync_codex_agents.py heading-coupled parsing (`## Handoff`, `## Self-Check`, `## Report Format`, etc.) | generator | updated in lockstep to the renamed/restructured headings; `--check` exit 0, 7/7 tests pass | contributor | K |
| 43 | Both `direct-mode-*` refs + both `superra_*.toml` | generated artifacts | regenerated from the redesigned specs; `--check` exit 0 confirms in sync | direct-mode main agent / Codex | K |

**Every baseline unit is classified; none unclassified. One RA (the reviewer methodology-deference stance, repaired here). Zero remaining LOST.** Every ID unit ties to an explicit decision — either the user's wip commit `2398a188` (units 9–11, 14, the §Task Interface and report collapses), task 01's "drop What You Don't" decision (unit 22), or task 03's reporting collapse (units 33–35) — and each ID unit's behavior-shaping substance remains reachable by the role that needs it (convention-fit → `refactor-and-integrate` at integration; paraphrase-authority → reviewer copy; ask-questions → §Escalation).

### Report-consumer check (task 03 collapse)

No consumer relied on a removed report field. `agent-orchestration` §Review Status Reference ([SKILL.md:196](../../../../../skills/agent-orchestration/SKILL.md#L196)) reads `status:` frontmatter, not report prose. §Handling Implementer Status ([SKILL.md:213](../../../../../skills/agent-orchestration/SKILL.md#L213)) keys off the status enum (DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED), all still returned; "read the concerns" for DONE_WITH_CONCERNS now resolves to the commit body + `## Results`, exactly as the new implementer §Report Format states ([implementer.md:123](../../../../../agents/implementer.md#L123)). `superimplement` Step 2 reads `## Results` and the committed diff, not a Summary/Key-findings/Doc-edits field. Grep across `agent-orchestration/` and `superimplement/` for the old field names returns zero hits.

### Per-role reachability verdict — all PASS

- **Implementer (execution) — PASS.** Load path: `using-superra` + `report-in-markdown` (preload) + Stage manifest + on-demand. Read/edit interface, editing principles, ownership boundary (units 8, 21, 25) in using-superRA §Task Interface; status transitions + Results ownership + REVISE mechanics (23, 24) in its own spec §What You Own / §How You Fix; reproducibility (17) double-covered by spec + domain skill; ask-questions (12) in §Escalation. Planner-depth (38) reachable on-demand via `task-system`.
- **Reviewer (execution) — PASS.** Severity/verdict defined once (26, 28), planning-review mechanics fully in the manifest-loaded reference (27, 40), convention-fit enforcement reachable at integration via `refactor-and-integrate` (11), methodology-deference restored (2). Report content lives in `## Review Notes` (34).
- **Integration reviewer — PASS.** The heavyweight scoped-convention enforcement the user trimmed from §Before You Start is exactly the `refactor-and-integrate` §Project Doc Audit `[BLOCKING]` gate, loaded by the manifest `integration` row — the baseline line itself named that as its home.
- **Direct-mode main agent / Codex — PASS.** Both `direct-mode-*` refs and both `superra_*.toml` regenerated from the redesigned specs; `--check` exit 0, generator tests 7/7.

### Dangling-pointer sweep — zero in live surfaces

Grepped `skills/ agents/ README.md CLAUDE.md` for `Handoff — Unified`, `Planning Review Mode`, `§Self-Review Before Reporting`, `Pre-Commit Self-Check`, `What You Own, What You Don't`, `Domain add-ons (topic-driven)`, `## Load map`. Zero live pointers to a removed anchor. The only `Planning Review Mode` hits are in the generator test asserting the heading's **absence** (a positive relocation guard). CLAUDE.md §Ownership table row 68 correctly names `planning-review.md` as the new owner; the superplan and thorough-planning pointers resolve to the still-present `thorough-planning.md §Planning Review`.

### Verification commands run (all green)

- `git show 72671d50:<path>` for every touched surface (all present at baseline; planning-review.md is a new destination).
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` → exit 0 ("All generated agent files are up to date" + "All generated direct-mode role references are up to date").
- `uv run pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py` → 7 passed.
- `python3 skills/task-system/scripts/task_check.py --plan-root superRA` → "All checks passed. No issues found."
- Grep sweeps for removed report fields across `agent-orchestration/` and `superimplement/` → zero hits; dangling-anchor sweep across live surfaces → zero hits.
