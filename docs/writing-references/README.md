# Writing-Skill Source Material

Sources distilled into `skills/writing/` during this branch. Read these to get the big picture before drafting or reviewing the skill files — the PLAN.md task descriptions are a condensed target, not a substitute for reading the originals.

## What each source contributes

| Source | Location | Feeds into |
|---|---|---|
| **Chaubey, *Research Writing*** | `docs/writing-references/Chaubey_Research_Writing.pdf` (committed) | Academic writing rules targeted at the economics audience — structure, precision, the author's mental model of the reader. Main input to `style.md` and `structure.md`. |
| **Little Red Schoolhouse (LRS) notes** | `/Users/zhiyufu/Dropbox/PhD/writing_resources/LittleRedHouse/` (Dropbox-synced, not committed) | University of Chicago ENGL 13000/33000 slides. 14 PDFs covering actions-in-verbs-vs-nominalization (1-1a), character (1-1b), coherence/cohesion (2), old→new information flow (3-4), introductions (5, 6), argument structure (Arg 1–3), downstream revision (DS 1–2), triage. Main input to `style.md` (LRS 1-1a, 1-1b, 2, 3-4) and `structure.md` (LRS 5, 6, Arg 1–3). |
| **Pyramid Principle (Minto)** | Web — see the reference list below | MECE grouping, governing idea, horizontal/vertical logic, SCQ (Situation–Complication–Question) framing. Main input to `structure.md`. |
| **`draft-reviewer:*` plugin subagents** | `~/.claude/plugins/draft-reviewer/` | Seven subagents define the dimension split for `consistency/*.md`. Harvest the *dimensions* — the actual rule content is re-derived in superRA's style so the plugin is a harvest target, not a runtime dependency. |
| **`skills/econ-data-analysis/`** | repo | Architectural template for the writing skill — Iron Law pattern, §Three Concurrent Disciplines, §Pitfalls, stage-scoped references under `references/`. |

## Pyramid Principle reference list

Primary web sources gathered during Phase 1 research:

- McKinsey — MECE Principle: https://www.mckinsey.com/alumni/news-and-events/global-news/alumni-news/barbara-minto-mece-i-invented-it-so-i-get-to-say-how-to-pronounce-it
- StrategyU — Pyramid Principle Part 1: https://strategyu.co/pyramid-principle-partone/
- Mental Models — Minto Pyramid: https://mental-models.com/minto-pyramid/
- Think Insights — SCQA Logic: https://thinkinsights.net/strategy/scqa-logic
- ModelThinkers — Minto Pyramid & SCQA: https://modelthinkers.com/mental-model/minto-pyramid-scqa
- Management Consulted — SCQA Framework: https://managementconsulted.com/scqa-framework/

## Supporting economics-writing guidance

- Brandeis Writing Program — Writing Tips for Economics Papers: https://www.brandeis.edu/writing-program/resources/faculty/wi-instructor-resources/econ-tips.html
- Center for Global Development — How to Write an Introduction: https://www.cgdev.org/blog/how-write-introduction-your-development-economics-paper
- IZA — Writing Tips for Economics Research Papers (DP 15057): https://docs.iza.org/dp15057.pdf
- Bellemare — How to Write Applied Papers in Economics: https://marcfbellemare.com/wordpress/wp-content/uploads/2020/09/BellemareHowToPaperSeptember2020.pdf
- Conversable Economist — Writing the Intro: https://conversableeconomist.com/2020/02/17/writing-the-intro-to-your-economics-research-paper/

## Before drafting or reviewing, read

1. **For `style.md`:** LRS 1-1a (actions), LRS 1-1b (character), LRS 2 (coherence/cohesion), LRS 3-4 (info flow); Chaubey sections on sentence-level clarity.
2. **For `structure.md`:** LRS 5, LRS 6 (introductions), LRS Arg 1–3 (argument structure), LRS triage; Chaubey sections on paper structure; all Pyramid Principle web sources.
3. **For `consistency/*.md`:** The corresponding `draft-reviewer:*` subagent definition + `skills/econ-data-analysis/SKILL.md` §Three Concurrent Disciplines as the severity-marker model.
4. **For `refactor-and-compile.md`:** LaTeX/Quarto build docs + your real experience fixing compile errors.
5. **For `collaboration.md`:** `/CLAUDE.md` §Design Principles (RA framing, autonomous-with-human-in-the-loop) + LRS argument slides (authorial intent is central there).
6. **For `planning.md` + `workflow.md`:** `skills/econ-data-analysis/references/planning.md` as the template, plus the plan at `/Users/zhiyufu/.claude/plans/bubbly-wondering-parnas.md` for the four-mode design.
7. **For `integration.md`:** `skills/econ-data-analysis/references/integration.md` as the template.
