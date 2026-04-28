# Markdown Style Guide — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-27 (Task 1 REVISE round)
**Status:** In Progress

---

## Task 1: Re-scope `report-in-markdown` skill body and extend rich-content reference

**Status:** IMPLEMENTED — REVISE round 1 fixes applied, pending re-review

### Key Findings
- `skills/report-in-markdown/SKILL.md` rewritten: frontmatter description updated to "Markdown style guide for any agent writing PLAN.md, RESULTS.md, status reports, or standalone markdown reports." Body trimmed to 39 lines (frontmatter + body). Opener softened in REVISE round 1 from "Every agent loads this skill" (factually false until Task 2 ships the manifest update) to "The markdown style guide for any agent writing markdown" (true regardless of Task 2). The DRY-flagged orientation paragraph dropped; its load-bearing hint folded into the opener as a clause. New §File-reference rule introduces the `[file.py:42](file.py#L42)` form with single-line, range, and whole-file variants. Load map preserved.
- `skills/report-in-markdown/references/rich-content.md` §File references extended: now ~22 lines (was 10). Adds single-line `#L42`, range `#L40-L50`, and whole-file forms in a citation-form table; expands the wrong/correct contrast to include the backtick-path anti-pattern; notes GitHub / GitLab / VS Code preview honor the anchors. REVISE round 1 standardized the "Correct" examples to plain link text (no backticks) to match SKILL.md.
- `skills/CATEGORIES.md` and `README.md` Utility row for `report-in-markdown` updated to "Markdown style guide for any agent writing markdown" (REVISE round 1 dropped the "Loaded by every agent" claim, deferring that to Task 2's manifest tightening).

### Notes
- The trimmed SKILL.md no longer carries the `## When to invoke` and `## Invocation contract` sections. Their content was: "Skip this skill for agent-only text handoffs" (now wrong) and "Decide your caller role from the load map" (the load map is right there). Deleting them passes the DRY + Necessity gate.
- The Stage 2 fact-check in `references/final-form.md` already required markdown-link citations (line 71). This change makes Stage 1 consistent with Stage 2 — no behavior change in Stage 2.

## Task 2: Make `report-in-markdown` always-loaded in the Skill-Load Manifest

**Status:** IMPLEMENTED — REVISE round 1 fix applied, pending re-review

### Key Findings
- `skills/using-superRA/SKILL.md` §Skill-Load Manifest explanatory paragraph rewritten: now names `superRA:using-superra` **and** `superRA:report-in-markdown` as the two skills every agent loads, with a one-sentence rationale ("every agent writes markdown") and a pointer to where the citation rule lives ("its body carries the always-applicable file-link citation rule, with deeper format discipline in references loaded on demand").
- `Stage: documentation` row in the Generic table simplified from "`handoff-doc` + `report-in-markdown`" to "`handoff-doc`" only. `report-in-markdown` is no longer listed per-Stage because it loads universally.
- Net manifest line change: +2 lines in the explanatory paragraph, –1 token in the documentation row. Total always-loaded surface growth from this commit: ~2 lines, comfortably under the 25-line budget set in PLAN.md §Expected Results.

### Notes
- The **Main agents additionally load** sentence below the domain-add-on table is unchanged. It mentions `references/main-agent.md`, `superRA:handoff-doc`, and `superRA:agent-orchestration` — none of which conflict with the new always-loaded pair.
- Domain add-on rows are unchanged; they continue to compose with the generic table.
- REVISE round 1 also rewrote the §Skill Inventory row at line 59 (caught by reviewer — Task 1's parallel update missed this in-file row). The inventory row now matches the CATEGORIES.md and README.md phrasing and explicitly says "always-loaded alongside `using-superra`."

## Task 3: Update canonical examples and conditional-load text in agent files and handoff-doc references

**Status:** IMPLEMENTED — pending review

### Key Findings
- `agents/implementer.md` updated in three places: (1) §Editing Etiquette gained a one-line "Cite source files as markdown links per `report-in-markdown` §File-reference rule" reminder; (2) lines 113–120 example blockquote rewritten so review items and `→ implemented:` annotations use markdown-link citations like `([Code/03.py:42](Code/03.py#L42))`; (3) line 128 conditional-load sentence reworded — `report-in-markdown` is now always loaded so the sentence only points at the heavier `rich-content.md` reference, not the parent skill.
- `agents/reviewer.md` updated in three places: (1) §Editing Etiquette gained the same one-line reminder; (2) §Verdict (line 83) "file:line, description, severity, what to fix" → "markdown-link citation (e.g., `[file.py:42](file.py#L42)`), description, severity, what to fix"; (3) §How You Write a Review (line 126) the same wording change applied to the per-issue item description.
- `skills/handoff-doc/SKILL.md` line 49 pointer extended from "Figure embedding" to "Figure embedding and code-file citations" — surfaces the link-citation rule for handoff-doc readers without restating it.
- `skills/handoff-doc/references/plan-anatomy.md` lines 215–216 review-notes example rewritten to markdown-link citations, matching the agent-body canonical example.

### Notes
- Codex generated artifacts (`skills/using-superRA/references/direct-mode-{implementer,reviewer}.md`, `.codex/agents/superra_{implementer,reviewer}.toml`) were intentionally NOT regenerated in this commit. Per PLAN.md header, regeneration happens in Task 5 once Tasks 3 and 4 (the agent-file edits) have both landed.

## Task 4: Sweep for stale backtick-path citation samples across the repo

**Status:** IMPLEMENTED — pending review

### Key Findings
Sweep ran two grep patterns:
1. `` (`<path>:<line>`) `` — backtick-wrapped path:line citations.
2. `<file:line + ...>` and `\`file:line\`` — file:line in instruction templates and prose.

Triage of hits and actions taken:

- **`agents/implementer.md:106`** — `<file:line + one-line fix description>` instruction template (the MINOR symmetry observation surfaced by the Task 3 reviewer). Rewrote to `<markdown-link citation + one-line fix description>` so the template parallels the canonical example two paragraphs below.
- **`agents/reviewer.md:137`** — `<file:line + fix description>` describing the implementer's annotation format on re-review. Rewrote to `<markdown-link citation + fix description>`. Also softened the trailing prose "Go to the cited `file:line` and verify" to "Follow the markdown link to the cited line and verify."
- **`skills/agent-orchestration/SKILL.md:163`** — canonical example blockquote in §Handling Reviewer Feedback used backtick-path form `` (`Code/03.py:42`) ``. Rewrote to markdown-link form `([Code/03.py:42](Code/03.py#L42))` for consistency with the agent-body example.
- **`skills/using-superRA/references/direct-mode-{implementer,reviewer}.md`** — these are generated artifacts. Left untouched; Task 5 regenerates them via `sync_codex_agents.py` from the updated `agents/*.md` source.
- **`skills/report-in-markdown/references/rich-content.md:105`** — intentional anti-pattern example labeled "Wrong (backtick path)". Left as-is; this is teaching the wrong form so readers recognize and avoid it.
- **`agents/implementer.md:105`** — descriptive prose "go to the cited `file:line` and fix the code". Reviewer flagged but said "remains a reasonable English description." Left as-is per reviewer's own judgment.

### Notes
- Final re-run of both grep patterns shows only the `direct-mode-*` generated files (Task 5 territory) and the rich-content.md anti-pattern example. No other backtick-path or `<file:line>` template residuals.

## Task 5: Regenerate Codex named-agent artifacts and verify

**Status:** IMPLEMENTED — pending review

### Key Findings
- Regeneration command: `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --force`. Wrote four files (two `.codex/agents/*.toml` named-agent specs, two `skills/using-superRA/references/direct-mode-*.md` direct-mode references).
- All four generated files now carry the markdown-link citation form in their canonical example blockquotes — `grep -n "Code/03.py#L42"` shows hits at line 112-113 in `direct-mode-implementer.md` and line 119-120 in `superra_implementer.toml`. Both review-item and `→ implemented:` annotation lines use the new form.
- Sweep on the generated files for residuals: zero `(\`Code/...:NN\`)` or `<file:line +` patterns remain — the regeneration picked up all of Task 3 + Task 4's source-file edits.
- Diff scope: 4 files, +22 / -18 lines, all confined to the canonical example blockquotes and the implementer-template line. No unrelated drift.

### Notes
- Used `python3` because `python` is not on the worktree shell PATH; the script accepts both interchangeably.
- Used `--scope project` (writes into the worktree's `.codex/agents/`). Global-scope regeneration into `~/.codex/agents/` is a separate concern owned by `codex-superra-setup` and not in scope for this task.
