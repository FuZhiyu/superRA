---
title: "Polish Pass: Fix Audience Leaks + Prose Quality Across Reading-Flow Pages"
status: approved
depends_on:
  - 02-quickstart
  - 03-domain-skills
  - 04-utility-skills
  - 05-finalize
  - 06-shorten-readme
  - 07-welcome-design-philosophy
tags: []
created: 2026-06-17
---

## Objective

A `writing`-skill **Polish pass** over the user-facing reading-flow prose. The content and structure are settled and approved; this pass improves *how it reads* and removes *audience leaks*. Sentence/paragraph scope — do not restructure pages or change which concepts each page covers.

**Targets:** `docs/site/01-welcome/task.md`, `docs/site/02-quickstart/task.md`, `docs/site/03-domain-skills/task.md`, `docs/site/04-utility-skills/task.md`, and the repo-root `README.md`. Build the audience model first (researchers adopting superRA), then check every sentence against it.

**Goal 1 — eliminate audience leaks.** The prose repeatedly addresses the wrong audience or names agent-facing internals the adopter does not need. The discipline is "write to the reader, not the conversation": never make the reader think about a thing only to tell them they don't use it.

- Worked example to fix: *"You read the tree not through the CLI — that is the agents' interface — but through the **dashboard**…"* → just *"You read the tree on the **dashboard**."* The CLI/agent-interface contrast should vanish, not be explained.
- Soften the `frontier` jargon in the Quickstart to the plain behavior (the agent automatically picks up the next task whose dependencies are satisfied; you watch the order unfold on the dashboard). The formal term stays only in Reference, which this task does not touch.
- Sweep for the same class of leak everywhere: references to the `superra` CLI surface, internal mechanisms (hooks, status rollup internals, load order), or "as we saw / as the conversation" framing. Surface behavior and design intent; cut the wiring.

**Goal 2 — prose quality.** Tighten wording, fix awkward or clunky sentences, parallelism, hedging, and flow so the pages read like clean published documentation. Preserve the argument, structure, technical claims, and the researcher-approved design-philosophy framing — polish the prose, not the substance.

**Verify:** `docs/build_site.sh` builds clean; the five pages pass the markdown self-diagnose; no `03-concepts`/`04-how-to` link regressions; the six-page structure and all approved content decisions are intact (slide-design still absent, dashboard-first framing preserved).

## Planner Guidance

Load the `writing` skill in Polish mode (`references/polish.md` + `references/style.md`; the audience-leak rule is `style.md §Audience: write to the reader, not the conversation`). The leaks are systemic, not one-off — read each page end to end against the audience model rather than fixing only the cited example. One paragraph per line.

## Results

Synthesis pass: I compared the pre-polish original in this worktree against three competing polish variants (branches `…/parallel/polish-a` "spare reference-doc", `polish-b` "researcher to researcher", `polish-c` "punchy and minimal") and assembled the strongest rendering of each passage into one file per target, enforcing one consistent voice across the site (plain, concrete, substance-first, spare-to-researcher).

**Audience model used:** a researcher adopting superRA — comfortable with git and an AI harness, not assumed to know plugin internals or superRA terminology. Every sentence checked against that information set.

**Per-file variant sourcing:**

- [docs/site/01-welcome/task.md](../../../../docs/site/01-welcome/task.md) — body prose from polish-c (drops "quietly"/"silently"/"far more" intensifiers, "intent-aware"→"intent-first", tightens the design-philosophy bullets). "Start here" list from polish-c's framing, which removes all five rhetorical-question hooks ("New to superRA and want to try it?", "Want proof it is real?") and converts them to declarative "To try it…" / "For…" leads. Rejected polish-a's showcase line ("Want to see a real project?") because it reintroduces a question hook.
- [docs/site/02-quickstart/task.md](../../../../docs/site/02-quickstart/task.md) — polish-c throughout; it was the most coherent single voice and nailed every passage. Fixes the three systemic leaks: the worked-example CLI/agent-interface contrast collapses to "You read the tree on the **dashboard**"; the prerequisite/runtime paragraph drops "run the `superra` CLI … mostly the agents' interface to the tree" in favor of "to launch the dashboard"; the `frontier` jargon at "Watch progress" softens to the plain behavior ("the agent picks up the next task whose dependencies are satisfied, and you watch the order unfold on the dashboard"). Also fixes "cross-cutting"→"domain-neutral" in the "Where to go next" list.
- [docs/site/03-domain-skills/task.md](../../../../docs/site/03-domain-skills/task.md) — polish-c (polish-a touched one line, polish-b judged the page clean and made no changes). Genuine prose tightening only: removes "silently"/"currently-implemented", fixes "an agent can check"→"an agent checks", "is built to grow"→"grows". No structural or content change.
- [docs/site/04-utility-skills/task.md](../../../../docs/site/04-utility-skills/task.md) — polish-c (polish-a unchanged, polish-b touched only the objective). Removes the remaining `frontier` leak in the task-tree section ("the *frontier* of tasks ready to work next"→"the set of tasks ready to work next"), per the directive that the formal term stays only in Reference. Kept polish-c's edits but dropped its stray double blank line before "## Standalone helpers".
- [README.md](../../../../README.md) — polish-c. Fixes the broken parallelism "folds each task into the existing codebase and maturing documentation"→"…and matures the documentation"; removes "quietly"/"silently"; tightens the "Why superRA?" bullets and the "Skills, Agents, and Hooks" section. "far more code than anyone will carefully review" kept in the complaint bullet (factual, not self-congratulatory).

**Voice convention:** polish-c was the strongest and most internally consistent variant on four of the five files, so blending leaned heavily on it; the welcome "Start here" list and the cross-file leak fixes were the main passage-level selections. No restructuring, no content/structure change, no concept moved between pages.

**Verification (run in this session):**

- `docs/build_site.sh` — builds clean; wrote `_site/{index,demo-tree,superra-dev-tree}.html`, all three files non-empty.
- `check_markdown.py` on all five files — each reports `clean`.
- Leak/AI-pattern grep across the five files (`03-concepts|04-how-to|cross-cutting|seamless|robust|leverage|the agents' interface|frontier`) — no matches.
- Six-page structure intact (slide-design absent, dashboard-first framing preserved); no dropped-page link regressions.
