---
title: "Domain Skills: Overview + One Page Per Skill"
status: approved
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
