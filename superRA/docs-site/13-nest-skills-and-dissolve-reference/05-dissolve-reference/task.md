---
title: "Promote Glossary/FAQ/Hooks to Top Level, Renumber Showcase, Drop skills-and-agents"
status: not-started
depends_on: 
  - 01-ia-and-scaffold

tags: []
created: 2026-06-17
---

## Objective

Dissolve the standalone `05-reference/` section by promoting its cross-cutting pages to top level and dropping the one page the nested skills pages make redundant.

**Promote to top-level pages** (move out of `05-reference/`, renumbering to fill the freed slots):

- `05-reference/05-glossary` → `05-glossary`
- `05-reference/06-faq` → `06-faq`
- `05-reference/07-hooks` → `07-hooks`
- `06-showcase` → `08-showcase`

Sequence the moves to avoid transient prefix collisions (move `06-showcase` to `08-showcase` before promoting `06-faq`, etc.). Use `./superRA/superra task move --root docs/site …` so frontmatter/ordering stay correct, or `git mv` with a manual pass. Repoint only the moved pages' own internal `#/…` links; the site-wide repoint of links *into* them is task `06`.

**Drop `05-reference/04-skills-and-agents`.** Before deleting, confirm its content is either carried elsewhere or intentionally dropped: the domain/utility skill inventory is now the two overview pages plus their per-skill pages; the implementer/reviewer and Stage definitions are in the glossary and taught inline in the quickstart; the Stage→skill load manifest is agent-internal and stays in `using-superRA`, not the user-facing site. If any genuinely user-facing fact lives only on this page, fold it into the glossary or the relevant skill page before deleting — do not silently lose it.

**Leave the empty `05-reference/` parent for task `06` to remove** after all relocations (task `04` also moves pages out of it); removing it here would race with `04`.

User-facing framing: glossary, FAQ, and hooks are reader lookups — keep them oriented to what a researcher needs to know (which harness, when to skip a phase, what runs automatically), not to internal wiring. Load `writing`.

Validation: glossary/FAQ/hooks render at top level with their content intact; showcase renders at `08`; `skills-and-agents` is gone with no user-facing fact orphaned; `05-reference/` holds only the pages task `04` is relocating.

## Results

