---
title: "Per-Domain Skill Loads Live Coverage"
status: not-started
depends_on:
  - 08-claude-sdk-load-harness
  - 09-codex-canary-and-dispatch-hook
tags: []
created: 2026-06-19
---

## Objective

Verify live, in both harnesses, that a domain-worded fixture task loads its domain skill (contracts LC003, LC011–LC014):

- `econ-data-analysis` — task wording about importing/cleaning/merging/regressing data
- `theory-modeling` — task wording about deriving/solving/proving
- `writing` — task wording about drafting/polishing reader-facing prose
- `slide-design` — task wording about creating/revising slides/Beamer

Include a **multi-domain** fixture whose wording matches more than one domain (e.g. derive a result *and* write it up) and assert **all** matching domain skills load, since the manifest requires loading every matching domain.

Deliverables:

- A parametrized set of domain fixtures (a minimal task whose objective text unambiguously triggers one domain) plus the multi-domain fixture, each with an assertion that the expected domain skill(s) are evidenced loaded — Claude via the 08 SDK skill-load hook, Codex via the 09 canary.

Success criteria: each domain skill is evidenced loaded on its triggering fixture in both harnesses; the multi-domain case loads all matching skills; a red case (domain skill not loaded on triggering wording) fails.

### Constraints

- Manual-only; consume the 08/09 harnesses.
- Keep fixture tasks shallow — domain-triggering *wording* without requiring real domain work (no actual regression, proof, or deck). The target is the load, not the output.

## Planner Guidance

Parametrize over a `{domain_skill, trigger_wording}` table. The multi-domain case is the load-bearing one — it proves the "load every matching domain" rule, not just first-match. Keep trigger wording close to the manifest's own trigger phrasing so the test reflects the documented contract.

All domain skills load via the `Skill` tool → caught by 08's `PreToolUse(matcher="Skill")` hook, tagged `subagent_skill_tool` (orchestrator-confirmed live that the hook fires for loads inside the dispatched subagent). Reuse it; no Read-hook/reference case here (unlike task 11's `planning-review`).

Match skill names with the plugin-prefix normalization task 11 established: live loads are `superRA:`-qualified (e.g. `superRA:econ-data-analysis`), so a bare expected name like `econ-data-analysis` must still match — reuse 11's normalized matcher rather than a raw string compare, or every assertion is a false negative (this was a live-caught bug in 11). The live SDK dispatch is mildly nondeterministic — default `CLAUDE_MODEL=sonnet`, assert across a small pass@k window, not a single shot. A domain whose triggering wording reliably does **not** load its skill (or the multi-domain case loading only one of several matching skills) is a real LC003/LC011–LC014 finding to record and escalate, not an assertion to relax.
