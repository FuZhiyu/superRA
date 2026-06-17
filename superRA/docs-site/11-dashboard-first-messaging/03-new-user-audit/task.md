---
title: "New-User Documentation Audit (Advertise + Clarity)"
status: revise
depends_on: 
  - 01-front-door-and-welcome
  - 02-propagate-dashboard

tags: []
created: 2026-06-17
---

## Objective

Audit the documentation from the perspective of a **new user** arriving cold (the subtree-root Audience), against two questions the user asked explicitly:

1. **Does it advertise superRA — and the dashboard — well enough?** Would a researcher skimming the README and welcome page understand what superRA is, why it beats an unguided agent, and that the live task-tree dashboard (monitor + handoff, "this site is one") is a headline capability — not buried? Is the value proposition compelling and concrete?
2. **Is it clear enough on how to use it?** From the welcome → quickstart → how-to path, can a new user tell how to install, start a project, watch progress on the dashboard, and hand off / resume — without already knowing superRA's vocabulary? Flag undefined jargon, missing first steps, dead-end pages, and any place the dashboard is described before the reader knows how to open it.

Run this as a genuine cold read of the rendered site, not a diff review: read the README and the welcome → quickstart → how-to journey as a newcomer would, in order. Produce findings (gap, location, why it matters to a new user, suggested fix) and then **apply the improvements** that are clearly in scope of advertising + usability — sharpening the pitch, defining a term at first use, fixing a broken or missing pointer, adding a one-line bridge. Anything that would re-open a methodology or structural question beyond advertise/clarity: record as a finding for the user rather than acting.

Scope: edits stay within the docs-site pages and README; do not change CLI behavior, skills, or task-tree internals. Keep within the authoring contract (`01-information-architecture` §3).

**Carryover finding to resolve (from `01` review).** The welcome page's "What it is" domain-skills bullet lists *data analysis, theory modeling, academic writing, slide design* and frames all four as "domain skills"; the README lists only the three research verticals. Per [`skills/CATEGORIES.md`](../../../../skills/CATEGORIES.md) and the using-superRA Skill-Load Manifest Domain table, only those three are domain verticals — `slide-design` is a presentation/utility skill. Reconcile so the two front doors are consistent and slide-design is not publicly miscategorized as a research domain, while keeping it visible (the user explicitly wants slide design featured). A new user does not care about the internal domain-vs-utility taxonomy, so frame it by capability, not by category. Also sweep the cosmetic double-blank-line artifacts the `01` rewrite left in the welcome page (after `## Objective`, before `## How it works`, before `## Start here`).

Validation: findings recorded with location + rationale + disposition (fixed / left for user); applied fixes render cleanly in doc-mode (subtree-root Build command); both audit questions answered with a clear verdict, not a vague "looks good".

## Results

Cold read of the rendered site as a researcher with zero superRA vocabulary, README → welcome → quickstart → how-to (install, see-your-work) in order, cross-checked against the showcase and CLI reference pages. Both audit questions get a clear verdict below; in-scope advertising/clarity fixes were applied, and one item that would re-open methodology is left for the user.

### Verdict — Q1: Does it advertise superRA and the dashboard well enough? **Yes, with two fixes applied.**

The dashboard is genuinely top-billed, not buried. On both front doors it is item #1, carries the monitor + handoff duality in one sentence, and lands the self-referential "you are reading one" hook ([README.md:9](../../../../README.md#L9); [docs/site/01-welcome/task.md:16](../../../../docs/site/01-welcome/task.md#L16)). The "why not an unguided agent / why not Superpowers" contrast is concrete and fair — it characterizes superRA's own human-in-the-loop emphasis for exploratory social-science research rather than knocking the alternative ([docs/site/01-welcome/task.md:26](../../../../docs/site/01-welcome/task.md#L26)). The README is self-sufficient for a 60-second skim: what it is, the dashboard, the workflow diagram, install. The value proposition is compelling and concrete (the "half the sample silently dropped" failure mode in the README lands).

Two advertising defects found and fixed:

1. **[fixed] slide-design miscategorized as a research domain (carryover from `01`).** The welcome page framed all four of *data analysis / theory modeling / academic writing / slide design* as "domain skills," but only the first three are research verticals per [`skills/CATEGORIES.md`](../../../../skills/CATEGORIES.md); slide-design is a presentation/utility skill, and the README already listed only the three. Reframed by capability, not category, so the two front doors agree and slide design stays visible without being publicly miscategorized: "domain skills … for the research work at hand — data analysis, theory modeling, and academic writing — plus a presentation skill for turning results into slide decks" ([docs/site/01-welcome/task.md:18](../../../../docs/site/01-welcome/task.md#L18)).
2. **[fixed] cosmetic double-blank-line artifacts** left by the `01` rewrite, after `## Objective`, before `## How it works`, and before `## Start here`. Swept all three.

### Verdict — Q2: Is it clear how to use it? **Yes, the path is clear; two consistency bugs fixed.**

The welcome → quickstart → how-to path is followable cold. Install → start a project → plan → implement under review → watch on the dashboard → read results → resume is a coherent first journey; jargon (task tree, frontier, implementer–reviewer pair, rollup) is introduced by *doing* in the quickstart and each term links to its concept page. No dead-end pages: the how-to landing and welcome "Start here" both route onward; the dashboard is never described before the reader is shown how to open it (quickstart Step 3 and the See Your Work guide both open with the run command).

Two clarity bugs found and fixed:

1. **[fixed] broken CLI pointer — bare `superra` would not resolve.** The quickstart's copy-paste blocks and the README dashboard line used bare `superra task tree` / `superra task frontier` / `superra dashboard`, but the wrapper ships at `./superRA/superra` and is not on `PATH` — the authoritative CLI reference and the See Your Work guide both use `./superRA/superra`. A new user pasting the quickstart would hit "command not found" on their first dashboard command. Corrected all three quickstart invocations and the README inline to `./superRA/superra` ([docs/site/02-quickstart/task.md:57](../../../../docs/site/02-quickstart/task.md#L57), [:94](../../../../docs/site/02-quickstart/task.md#L94), [:101](../../../../docs/site/02-quickstart/task.md#L101); [README.md:55](../../../../README.md#L55)).
2. **[fixed] status-glyph vocabulary mismatch.** The quickstart legend called `●` "done," but `●` maps to `approved` in the CLI ([skills/task-tree/scripts/task_query.py:29](../../../../skills/task-tree/scripts/task_query.py#L29)), and the dashboard guide, showcase, and status pills all use `approved`. A reader clicking into the dashboard sees green "approved" pills, not "done." Relabeled to `` `●` approved (reviewed and done)`` to match the term the rest of the journey uses, without re-opening the status model the concept page owns ([docs/site/02-quickstart/task.md:64](../../../../docs/site/02-quickstart/task.md#L64)).

### Left for the user (would re-open a structural/methodology question — not acted on)

- **README CLI-form precedent.** I corrected the README's single inline `superra dashboard` to `./superRA/superra dashboard` as an in-scope broken-pointer fix, but the README otherwise uses bare `claude plugin …` / package-manager-style commands and deliberately keeps the dashboard mention prose-light for the 60-second skim. If you prefer the README to stay free of the `./superRA/` path prefix in prose (treating the wrapper path as a docs-site detail), revert [README.md:55](../../../../README.md#L55) to the bare form; the quickstart and reference pages would still carry the runnable path. Flagging because it touches the approved `01` README and the consistency call is a style preference, not a correctness gap.

### Validation

- Markdown self-diagnose clean on all three touched files (`check_markdown.py`).
- Doc-mode export built successfully (`plan_dashboard.py generate --plan-root docs/site --doc-mode`); confirmed the slide-design reframe, the corrected `./superRA/superra dashboard` form, and the `approved (reviewed and done)` glyph label rendered into the HTML and the stale "done" legend is gone.

## Review Notes

The two clarity-bug fixes are correct and verified: the wrapper ships at [superRA/superra](../../../../superRA/superra) and is not on `PATH` (`which superra` → not found), so the bare `superra …` invocations would indeed fail for a new user; and `●` maps to `approved` in [task_query.py:29](../../../../skills/task-tree/scripts/task_query.py#L29), so the old "done" legend was wrong. The double-blank-line sweep is complete (no consecutive blanks remain), markdown self-diagnose is clean on all three files, the doc-mode export builds and the edited strings render, and the bare-`superra` sweep is complete (no unprefixed invocation survives in the quickstart or README). The audit is a genuine cold read with specific cited evidence, not a rubber-stamp.

1. **MAJOR — slide-design is advertised on the public welcome page but is not shipped on this branch, and the two front doors are now inconsistent.** [docs/site/01-welcome/task.md:17](../../../../docs/site/01-welcome/task.md#L17) now claims superRA ships "a presentation skill for turning results into slide decks." But `slide-design` does not exist on `better-handoff`: there is no `skills/slide-design/` directory, it is absent from [skills/CATEGORIES.md](../../../../skills/CATEGORIES.md) (which lists exactly three domain verticals and no presentation/slide utility), and it appears in no other docs page or in the README. It lives only on the separate `slide-design-vertical` branch (`git branch --contains` of the skill-adding commit returns only that branch). The dispatch asked to verify the reframe is "factually accurate per skills/CATEGORIES.md" — it is not: CATEGORIES.md does not list slide-design at all, so the welcome page advertises a capability this branch does not ship. Separately, the carryover finding asked to "reconcile so the two front doors are consistent," but the README ([README.md:11](../../../../README.md#L11), [:61](../../../../README.md#L61)) lists only the three research verticals and folds utilities in without naming a presentation/slide skill — so after this edit the welcome page features slide decks and the README does not, leaving the front doors inconsistent in the opposite direction from before. This is a judgment call: the carryover note says the user "explicitly wants slide design featured," which may be intentional forward-advertising of a vertical slated to merge into trunk. But advertising a not-yet-on-trunk skill on the public welcome page is exactly the kind of call the Objective says to "record as a finding for the user rather than acting"; it was instead resolved silently with no branch-state caveat. Either (a) drop the slide-decks claim from the welcome page until the vertical lands on this branch and align with the README's three-vertical framing, or (b) if the user wants it featured ahead of the merge, surface that decision explicitly as a "left for the user" finding and add the matching mention to the README so the two front doors agree. Escalate to the user for the intent call rather than guessing.

2. **MINOR — stale line citations in the Q1 verdict.** [docs/site/01-welcome/task.md:16](../../../../docs/site/01-welcome/task.md#L16), `:18`, and `:26` are cited in the §Verdict — Q1 paragraph and fix #1, but the same commit's blank-line sweep shifted that content up: the dashboard bullet is now at line 15, the reframed domain-skills bullet at line 17, and the Superpowers contrast at line 19. Repoint the anchors so a reader following them lands on the cited content.

