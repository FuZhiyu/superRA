# Markdown Style Guide — Results

> Mirrors PLAN.md structure. Updated after each task with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-27 (Task 1, Step 3)
**Status:** In Progress

---

## Task 1: Re-scope `report-in-markdown` skill body and extend rich-content reference

**Status:** IMPLEMENTED — pending review

### Key Findings
- `skills/report-in-markdown/SKILL.md` rewritten: frontmatter description updated to "Markdown style guide for any agent writing PLAN.md, RESULTS.md, status reports, or standalone markdown reports." Body trimmed to 40 lines (frontmatter + body). New §File-reference rule introduces the `[file.py:42](file.py#L42)` form with single-line, range, and whole-file variants. Load map preserved (renamed first row from "Implementer writing a text-only RESULTS.md task section / implementation-workflow reviewer" to "Implementer / reviewer writing routine task-block citations only" to reflect always-loaded scope). Removed the "Skip this skill for agent-only text handoffs" carve-out and the "Invocation contract" / "Figure directory" sections (their content is either redundant with the load map or one-line-pointable).
- `skills/report-in-markdown/references/rich-content.md` §File references extended: now ~22 lines (was 10). Adds single-line `#L42`, range `#L40-L50`, and whole-file forms in a citation-form table; expands the wrong/correct contrast to include the backtick-path anti-pattern; notes GitHub / GitLab / VS Code preview honor the anchors.
- `skills/CATEGORIES.md` Utility row for `report-in-markdown` updated to reflect the scope shift ("Markdown style guide … Loaded by every agent.").
- `README.md` Utility skills table row updated to surface the file-link rule and the always-loaded status.

### Notes
- The trimmed SKILL.md no longer carries the `## When to invoke` and `## Invocation contract` sections. Their content was: "Skip this skill for agent-only text handoffs" (now wrong — every agent loads it) and "Decide your caller role from the load map" (the load map is right there). Deleting them passes the DRY + Necessity gate.
- The Stage 2 fact-check in `references/final-form.md` already required markdown-link citations (line 71). This change makes Stage 1 consistent with Stage 2 — no behavior change in Stage 2.

## Task 2: Make `report-in-markdown` always-loaded in the Skill-Load Manifest

**Status:** Not started

## Task 2: Make `report-in-markdown` always-loaded in the Skill-Load Manifest

**Status:** Not started

## Task 3: Update canonical examples and conditional-load text in agent files and handoff-doc references

**Status:** Not started

## Task 4: Sweep for stale backtick-path citation samples across the repo

**Status:** Not started

## Task 5: Regenerate Codex named-agent artifacts and verify

**Status:** Not started
