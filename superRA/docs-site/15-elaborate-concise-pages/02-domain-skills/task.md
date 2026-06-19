---
title: "Domain Skills: Elaborate Data-Analysis, Theory-Modeling, and Writing Pages"
status: approved
depends_on: []
tags: []
created: 2026-06-18
---

## Objective

**Second pass (depth).** The first-pass record below resolved every marker but read too terse for a new adopter. Redo these pages to the parent's [Revision standard](../task.md), matching the worktree-data-sync reference — read its before/after at commit `db54356c` (`git show db54356c`) first. Explain unfamiliar concepts plainly, lead with the user-facing choice shown as the prompt you give the agent, give worked examples (the writing-page modes especially want a concrete "what you say / what you get" per mode), and say why each option matters. Supersede the first-pass `## Results` with the second-pass account.

Resolve the researcher's markers on the three domain-skill pages, grounding every behavior claim in the owning `SKILL.md`.

**[01-econ-data-analysis](../../../../docs/site/03-domain-skills/01-econ-data-analysis/task.md).** The WIP renamed `## How you ask for it` to `## How to use` and left rough prose plus a literal `For example, ...` placeholder. Turn it into clean prose covering: (a) it loads automatically when data analysis is involved, so you do not name it; (b) the external-validation tip — when a prior study used the same dataset, ask the agent to add a test that reproduces a known published number, so the validate step has an external anchor, *with a concrete worked example replacing the `For example, ...` placeholder*; (c) composing with [`zotero-paper-reader`](../../../../docs/site/04-utility-skills/07-zotero-paper-reader/task.md) — ask the agent to search your Zotero library for papers using the same dataset and build those external-validation tests from them. Ground in `skills/econ-data-analysis/SKILL.md`.

**[02-theory-modeling](../../../../docs/site/03-domain-skills/02-theory-modeling/task.md).** The researcher swapped the opening failure example from the λ-overloading case to a placeholder-notation case and left it rough: *"making up placeholder notations $A$ $B$ for important variables like expected returns,"*. Polish into clean prose that parallels the original sentence's rhythm and keeps the closing payoff coherent ("one symbol meaning two things, and assumptions invented after the algebra needs them"). The example blockquote was removed; confirm the page still flows without it.

**[03-writing](../../../../docs/site/03-domain-skills/03-writing/task.md).** Two markers:
- *"a bit more on the value of the skill. 1) it was taught a good style of writing; 2) it can review the code-writing consistency; 3) it can revise and fix"* — add a short passage on what the skill brings beyond a bare agent: a trained academic-writing style, a consistency check across the eight dimensions (including code-vs-paper consistency), and in-place revision/fixing.
- *"a bit more details on how to invoke this skill ... separate different mode out rather than compact them in a single paragraph ... long-form review vs quick review etc."* — break the single compact Review/Polish/Draft paragraph into separated modes (this is the skill researchers invoke standalone most often), and within Review distinguish a quick single-lane review from a long-form / deep multi-lane review. Ground in `skills/writing/SKILL.md` (mode routing) and `references/long-form-review.md`.

Success: all markers removed; every claim traceable to the owning `SKILL.md`; pages stay within the agent-first / non-obvious-only / no-AI-prose gates (elaboration closes a reader gap, it does not re-narrate the skill's internal discipline).

## Planner Guidance

These three pages link to their `SKILL.md` as the authority — keep the page a short orientation and point there for the full gate/mode/dimension lists rather than reproducing them.

## Results

Second-pass account (supersedes the first-pass record). The first pass resolved every marker but read too terse for a new adopter; this pass redid the three pages to the [Revision standard](../task.md) demonstrated on [04-utility-skills/06-worktree-data-sync](../../../../docs/site/04-utility-skills/06-worktree-data-sync/task.md) (`git show db54356c`): scannable `###` subsections one idea each, the user-facing choice led as the prompt you give the agent, a worked example per option, and the consequence that makes each option matter. No markers remain on any of the three pages.

### [01-econ-data-analysis](../../../../docs/site/03-domain-skills/01-econ-data-analysis/task.md)

Restructured `## How to use` from one prose block into three `###` subsections, each leading with the decision the reader makes and a worked prompt:

- *State your expectation up front* — the expectation becomes the validate-step baseline; the worked merge prompt is followed by a before/after consequence (without the row-count clause the agent has no number to be surprised by; with it, an 80,000-fund result — the one-to-many fan-out signature — stops the run). Grounds in [SKILL.md §Validate "Row count matches expectation" / "Task objective expectations comparison"](../../../../skills/econ-data-analysis/SKILL.md).
- *Anchor the validate step to a published number* — replaced the bare CRSP-Compustat mention with a concrete prompt (reproduce the Fama-French value-minus-growth spread for 1963–1991 before the main regression) plus the consequence (a spread at half the published value localizes the bug to sample construction, found on a pre-vetted number). Grounds in [SKILL.md §Validate "Reference verification" / "Property check"](../../../../skills/econ-data-analysis/SKILL.md) — external benchmark for key variables, growth/spread figures verified against published cases.
- *Planning a multi-step study* — kept the Data Inventory gate, reworded the trailing payoff into a plain consequence.

### [02-theory-modeling](../../../../docs/site/03-domain-skills/02-theory-modeling/task.md)

Opening failure example already polished to the throwaway-symbol-reused case (marker resolved first pass); closing payoff "one symbol meaning two things, and assumptions invented after the algebra needs them" stays coherent and the page flows without the removed blockquote. Brought `## How to ask for it` to the depth bar: added a worked prompt (derive FOCs, then verify by substituting back into the budget constraint) and made the two explicit requests — reuse existing notation, verify before reporting — each carry the failure it steers (a second name for an already-named quantity; a clean-looking derivation that does not satisfy the original conditions). Grounds in [SKILL.md §Non-default constraints + Gate 1 / Gate 4](../../../../skills/theory-modeling/SKILL.md).

### [03-writing](../../../../docs/site/03-domain-skills/03-writing/task.md)

Value passage (trained academic-writing style, eight-dimension consistency check incl. code-vs-paper, in-place revision) kept from the first pass. Rewrote `## How you ask for it` into a `###` subsection per mode, each with a worked **what you say / what you get** pair:

- *Review* — findings only, no edits; what-you-get example shows a code-vs-paper finding (abstract says "significant", Table 2 reports p = 0.11). Quick (single agent, one pass) vs long-form (lane split, one focused reviewer per lane in parallel) distinguished, with the reason a generalist reads each lane more shallowly. Grounds in [SKILL.md §Mode routing](../../../../skills/writing/SKILL.md), [review.md §Thoroughness / §Multi-lane reviews](../../../../skills/writing/references/review.md), [long-form-review.md §Trigger](../../../../skills/writing/references/long-form-review.md). The page collapses the skill's Quick/Standard/Deep thoroughness into the reader-facing quick/long-form split — a deliberate docs simplification, not a behavior claim.
- *Polish* — in-place edits, substance preserved; restructuring opt-in.
- *Draft* — outline first, then voice-matched prose.
- The two non-obvious moves (polish-your-own-diff, leave-directives-in-text) retained; tightened the diff-polish bullet phrasing.

### Gate self-check

- Agent-first: every mode/option led as the natural-language request, CLI/flags left to the linked `SKILL.md`.
- Non-obvious-only: added depth closes adopter gaps (how to ask, the worked example, why it matters); no skill-internal gate/dimension/pitfall catalogs re-narrated — those stay behind the `SKILL.md` links.
- No-AI-prose: scanned for banned markers (none); removed two trailing-payoff em-dashes introduced mid-edit (econ line 17, writing diff bullet).
- `report-in-markdown` self-diagnose: all three pages report `clean`.
