# Research: Communicate

Synthesis of three read-only research agents dispatched for thorough planning, 2026-08-06.

## Design conclusions

### One hierarchy, adapted by surface

Use three layers:

1. Outcome, decision, or present state.
2. Decision-relevant evidence, material caveat, and next action.
3. Linked mechanics and optional detail.

This combines bottom-line-up-front communication with progressive disclosure. It applies to chat, task results, planner updates, reviews, and handoffs through small adapters rather than separate style guides. Supporting guidance: [Army correspondence standard](https://home.army.mil/wood/application/files/3015/5751/8343/AR_25_50_Army_Correspondence.pdf), [ONS content structure](https://service-manual.ons.gov.uk/content/writing-for-users/structuring-content), and [Google technical-writing guidance](https://developers.google.com/tech-writing/one/documents).

The researcher set nested lists with short, complete sentences as the default rendering of this hierarchy. Top-level bullets carry takeaways; indentation reveals supporting evidence, caveats, and mechanics only as the reader digs deeper. Paragraphs remain for connected reasoning, narrative, or causality that a list would fragment. The target is a visible pyramid, not a paragraph wall or a flat list with no hierarchy.

Answer-first ordering is not mechanical. Exploratory work leads with provisional state and the unresolved branch; a caveat that changes the conclusion stays beside it. Academic exposition may need known-to-new or argument order rather than operational BLUF ([GOV.UK research background](https://www.gov.uk/government/publications/govuk-content-principles-conventions-and-research-background/govuk-content-principles-conventions-and-research-background)).

### Rewrite is a separate, on-demand protocol

`references/rewrite.md` should route three passes:

- **Patch:** the governing idea and order work; defects are local.
- **Structural rewrite:** chronology, stale headings, or duplicated homes obscure the hierarchy.
- **Stop:** sources conflict, truth is unclear, or deletion would decide an authorial or research question.

Before drafting, classify source units as `keep`, `point`, `merge`, `drop`, or `conflict`. Preserve exact literals—code, commands, paths, URLs, citations, equations, errors, names, dates, versions, numbers, units, and status tokens—and semantic invariants: propositions, conditions, caveats, commitments, dependencies, and claim strength.

Verify literals, meaning, truth, cold-readability, and the final diff. Word reduction is diagnostic, never the objective. Structural-editing support: [Australian Government Style Manual](https://www.stylemanual.gov.au/writing-and-designing-content/editing-and-proofreading) and [Google accessible-documentation guidance](https://developers.google.com/style/accessibility).

### Friction, not AI detection

The inspected [`avoid-ai-writing` version 3.23.1](https://github.com/conorbronsdon/avoid-ai-writing/commit/b72b7c42b196e113d2477c21c62df58061bc804f) is an 805-line authorship-style catalog. superRA should adapt only diagnostics with an observable reader cost:

- redundancy;
- indirection;
- unsupported abstraction or vague attribution;
- buried structure;
- ambiguity.

Do not adopt vocabulary tiers, banned-word tables, em-dash or formatting quotas, forced rhythm variation, type-token targets, personality injection, or “iterate until no patterns remain.” Preserve technical vocabulary, calibrated hedges, contrasts, bullets, punctuation, and voice unless they make retrieval or interpretation harder. Authorship detection also risks false positives for non-native English writers ([Liang et al., 2023](https://www.sciencedirect.com/science/article/pii/S2666389923001307)).

Independent adaptation needs only a pinned provenance note. Copying distinctive wording, examples, tables, or a substantial portion requires Conor Bronsdon's copyright and full [MIT notice](https://github.com/conorbronsdon/avoid-ai-writing/blob/main/LICENSE); wholesale vendoring would also require tracing its upstream adaptations.

## Validation cases

- Local padding: remove success narration while preserving sample, period, artifact, and caveat exactly.
- Stage-accreted task: rebuild around current findings; point at protection and commit evidence instead of retaining process telemetry.
- Cross-tree duplication: keep detailed values with their producing artifact, interpretation in the writeup, and a strictly shorter parent pointer.
- Conflicting counts: stop for evidence rather than keeping the latest mention.
- Frozen technical spans: retained literals compare byte-for-byte after a structural rewrite.
- Academic voice: remove repetition without strengthening a calibrated hedge or changing established terminology.
- Buried outcome: reorder outcome, evidence/caveat, then mechanics without breaking causal or temporal dependencies.
- Skimmability: convert a paragraph wall or flat bullet list into a nested pyramid without dropping relationships or creating fragments.
- Harmless marker: preserve an em dash, technical term, list, or first-person voice when it adds no reader cost.

## Enforcement implication

Discovery metadata makes a skill accessible; it does not make it universal. `communicate` should join `using-superra` in the always-loaded contract: the main-agent autoload chain and both role skills load it, and harness tests verify the load before human-facing work. Detailed rewrite, friction, and Markdown mechanics remain on demand.
