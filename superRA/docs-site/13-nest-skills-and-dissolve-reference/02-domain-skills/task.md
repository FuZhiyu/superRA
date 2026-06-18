---
title: "Domain Skills: Overview + One Page Per Skill"
status: implemented
depends_on: 
  - 01-ia-and-scaffold

tags: []
created: 2026-06-17
---

## Objective

Turn `03-domain-skills/` from one flat page into an overview over one page per domain skill.

**Overview page (`docs/site/03-domain-skills/task.md`):** keep the framing paragraph (what a domain skill is — methodology for the agent, standard for the reviewer) and replace the three inline skill sections with a one-line entry per skill that links to its page: econ-data-analysis, theory-modeling, writing. Resolve the dangling `## On the roadmap` heading the current page ends on — either restore a short roadmap line (literature-review and simulation verticals are planned) or drop the heading; do not leave a bare heading.

**One page per skill** (the stubs scaffolded by `01`): `01-econ-data-analysis/`, `02-theory-modeling/`, `03-writing/`. Each page carries that skill's high-level design — the prose currently in the flat page is the starting material, kept or lightly expanded into a standalone page a reader lands on directly:

- `01-econ-data-analysis` — the Iron Law (describe before you transform), the describe–analyze–validate loop, pitfall catalogs; language-agnostic.
- `02-theory-modeling` — the four gates (Objects & Notation → Assumptions → Derivations → Verification & Rendering) and why their order is the order trust depends on.
- `03-writing` — preserve-substance / polish-prose across Review, Polish, Draft modes; note it is the domain skill most often invoked standalone on a manuscript.

Each page links to its `SKILL.md` as the authority and does not re-author agent-facing discipline (authority-not-paraphrase, per the root Conventions). One page per domain skill — no third level; the detail home is the SKILL.md.

Prose quality: this is reader-facing writing. Load the `writing` skill; no AI-flavored prose (`feedback_no_ai_flavored_prose`); lead each page with what the reader gets, then when to reach for it.

Validation: the overview links resolve to the three pages; each page stands on its own when landed on directly; no teaching from the current flat page is lost in the split.

## Results

`03-domain-skills/` is now an overview over one page per domain skill.

**Overview** ([docs/site/03-domain-skills/task.md](../../../../docs/site/03-domain-skills/task.md)): kept the framing paragraph unchanged (domain skill = methodology for the agent, standard for the reviewer). Replaced the three inline skill sections with a one-line entry per skill, each linking down via hash path (`#/03-domain-skills/01-econ-data-analysis`, `02-theory-modeling`, `03-writing`). Resolved the dangling `## On the roadmap` heading by restoring a short roadmap line (literature-review and simulation verticals planned; each composes with the existing workflow/utility skills).

**One page per skill**, each expanded from the flat-page prose into a standalone page that leads with what the reader gets, then when to reach for it, and ends with a single authority link to its `SKILL.md` (no re-authored agent-facing discipline, no third level):

- [01-econ-data-analysis](../../../../docs/site/03-domain-skills/01-econ-data-analysis/task.md) — Iron Law (describe before you transform), the describe–analyze–validate loop, per-operation pitfall catalogs, language-agnostic.
- [02-theory-modeling](../../../../docs/site/03-domain-skills/02-theory-modeling/task.md) — the four gates (Objects & Notation → Assumptions → Derivations → Verification & Rendering) and why the order is the order trust depends on.
- [03-writing](../../../../docs/site/03-domain-skills/03-writing/task.md) — preserve-substance / polish-prose across Review, Polish, Draft modes; noted as the domain skill most often invoked standalone on a manuscript.

No teaching from the flat page is lost: every concept (Iron Law, describe–analyze–validate, pitfall catalogs, four gates and their order, three writing modes, consistency checks, standalone-on-manuscript framing) moved to the per-skill pages; the overview keeps only framing plus links.

**Validation.** Markdown self-diagnose (`check_markdown.py`): all four pages clean. Doc-mode static export built clean (exit 0, `--doc-mode`, `--repo-file-base https://github.com/owner/superRA/blob/main`): the three down-links (`#/03-domain-skills/0{1,2,3}-…`) are present in the output and no un-rebased relative `skills/.../SKILL.md` href leaked. The per-skill pages use the same `[name](skills/<skill>/SKILL.md)` repo-file-link convention as the already-approved quickstart page; the export wires `REPO_FILE_BASE` globally, so the SKILL.md links rebase to the GitHub blob URL identically for these pages and the existing ones.

**Operating-manual rewrite (researcher feedback).** The three per-skill pages were rewritten from the initial nest-and-frame pass to the §Conventions skill-page quality bar — they had read like pitches, not manuals. A two-draft-then-synthesize pass (two independent drafters per page reading the real `SKILL.md` + references, a synthesizer fact-checking both against the skill file and merging the best) now makes each page state, concretely: the failure a bare agent produces that the skill prevents, what the skill does, and how a researcher invokes it with example prompts. theory-modeling leads with the symbol-means-two-things / back-filled-assumption failure and notation reuse across the four gates; writing teaches the polish-unstaged-diff pattern, in-text directives (`% TODO:`/`[fill in]`/`DO NOT EDIT`/`% intent:`), and Review/Polish/Draft triggers; econ-data-analysis leads with the silent-bad-merge / undescribed-panel failure and the describe→analyze→validate loop. The overview one-liners were rewritten to match. Doc-mode build clean; `check_markdown` clean on all four.

## Review Notes

1. **MAJOR — writing page overstates that every mode auto-runs all eight consistency dimensions over any target.** [docs/site/03-domain-skills/03-writing/task.md:31-33](../../../../docs/site/03-domain-skills/03-writing/task.md#L31-L33): the heading "Consistency checks every mode runs" plus "Whatever the mode, it runs eight consistency dimensions over the target. So a polish pass on one paragraph also catches a symbol that drifted from its first definition, a `\citet` that does not match your bibliography, a 'Section 3' where the rest of the paper writes '§3', or a coefficient rounded to three decimals in one table and two in another." misrepresents what the skill does. In [skills/writing/SKILL.md](../../../../skills/writing/SKILL.md) the Knowledge files table loads `references/consistency/*.md` only "when Review or polish *targets that consistency dimension*," and [skills/writing/references/polish.md:1-3](../../../../skills/writing/references/polish.md#L1-L3) scopes Polish to `style.md` by default — sentence-scope by default. A single-paragraph polish does not auto-scan the whole bibliography for `\citet` mismatches or compare rounding precision across two different tables; those are wider-scope dimension checks loaded on demand. This is the "what the skill actually does" fact-check the dispatch flagged. Fix: reframe so the dimensions are checks the skill *can* run / runs *when the target is in scope* (e.g. "across the eight consistency dimensions" rather than "every mode runs all eight over any target"), and drop the cross-table / whole-bibliography examples that imply a one-paragraph polish triggers a paper-wide scan. The eight dimension names themselves are accurate.
   → implemented: reframed the section to "Consistency checks, scaled to what you ask for" — the skill *carries* eight dimensions and *applies the ones your scope calls for* (sentence/paragraph polish stays local; "check citations" / "consistency sweep on §3" loads those; a full-paper review pulls in all). The cross-table/whole-bibliography catches are now explicitly attributed to a review pointed at the whole draft, not a one-paragraph polish. ([docs/site/03-domain-skills/03-writing/task.md:31](../../../../docs/site/03-domain-skills/03-writing/task.md#L31))

2. **MINOR — hype heading on the writing page.** [docs/site/03-domain-skills/03-writing/task.md:23](../../../../docs/site/03-domain-skills/03-writing/task.md#L23): "The killer pattern: polish a diff" uses a hype phrase the rest of the page otherwise avoids (`feedback_no_ai_flavored_prose`). The pattern itself is real and well-described. Suggest a plain heading, e.g. "Polish a diff" or "The unstaged-diff pattern."
