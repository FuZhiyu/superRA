# Audience Awareness — superRA:writing Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-05-11 (Task 2, Step 4)
**Status:** Completed

---

## Task 1: Edit SKILL.md, style.md, and writing/CLAUDE.md for audience-awareness rule

**Status:** Completed (Task 1 approved 2026-05-11)

Three files edited, one atomic commit. The conversation/document boundary discipline now reads as: SKILL.md teaches the principle and the upstream audience-model protocol (always loaded, every Review / Polish / Draft); style.md teaches the four line-level marker families and replacement patterns (loaded when Polish / Draft / style-scoped Review runs); CLAUDE.md records why the rule is split across the two files.

- `skills/writing/SKILL.md` — added top-level section `## Write to the reader, not the conversation` between `## Preserve substance, polish prose` and `## Before you start`. Three paragraphs (audience distinct from conversation; two-question audience model; write/edit against the set) plus a pointer to `references/style.md §Audience` for the line-level safety net.
- `skills/writing/references/style.md` — inserted new heuristic `### Audience: write to the reader, not the conversation` as the first §How-To entry (before `### Actions in verbs`). Carries the four marker families (editing-history temporal, audience self-reference, process-internal artifact, conversation jargon), four replacement patterns (one per family), and three §Do NOT exceptions (conventional discourse transitions, public citable resources, genuine field terms of art). Appended one bullet to §Gated Checklist Sentence-level rules so the gated walk picks up the new rule.
- `skills/writing/CLAUDE.md` — appended new section `## Audience awareness as an upstream audience-model discipline` after §Sources. Records the SKILL.md / style.md split rationale (Review scope coverage without style.md; avoid forcing every Review to load marker families), the deliberate generalization beyond academic papers (slide decks, working-paper notes, replication READMEs, referee responses), and the do-not-collapse / do-not-re-narrow guidance for future contributors.

Verification of behavior change is deferred to Task 2 (constructed-fragment dispatch).

## Task 2: Verify the rule on constructed examples

**Status:** Completed (Task 2 approved 2026-05-11)

Polish-mode dispatch on a single constructed LaTeX fragment combining all three test concerns (positive detection across the four marker families, no over-firing across the three §Do NOT exceptions, audience-model elicitation on an ambiguous-venue paragraph). The bundled-fragment approach replaces the originally planned three-fragment dispatch per `agent-orchestration §Workload Balancing` Tier 2 (shared context, same skill load); each test concern lives in its own intent-tagged paragraph so bundling does not blur which signal fired where.

### Detection — 4 of 4 marker families detected and classified correctly

- *Process-internal artifact.* `applied via the \texttt{AE} column of \texttt{input/country\_information.csv}` removed from paragraph 1, sentence 1. Replacement matches `style.md §Audience` example verbatim.
- *Audience self-reference.* `In the paper-facing table, we define coreAE …` rewritten to `Table 2 defines coreAE …`. Replacement matches the §Audience `Table 2 defines …` pattern.
- *Editing-history temporal marker.* Sentence `The table now defines this coreAE classification.` deleted entirely (subsumed by the prior audience-self-reference fix, so the surviving prose carries the definition without the `now`).
- *Conversation jargon.* `We use the AE/EM cut throughout, where the EM-versus-AE split follows the same convention.` rewritten to `EM denotes the complementary set under the same IMF classification.` The original was drafting-shorthand (`cut`, `split follows the convention`) restating that AE and EM are partner labels without defining EM; the replacement defines EM in the document's voice, which the audience needs since paragraph 2 then uses `AE-EM growth gap`.

### No over-firing — 3 of 3 §Do NOT exceptions respected (plus one not in the test set)

- *Conventional discourse.* `We now turn to robustness.` (paragraph 2, sentence 1) kept verbatim.
- *Public citable resource.* `The replication package (DOI 10.5281/zenodo.example) contains the underlying series.` kept verbatim.
- *Genuine field term of art.* `heteroskedasticity-robust standard errors` kept verbatim in the rewrite of paragraph 2 (only the surrounding `All standard errors are heteroskedasticity-robust standard errors` noun-repetition was cleaned up to `Standard errors are heteroskedasticity-robust and clustered at the country level`, which is a `style.md §Noun-cluster avoidance` pickup, not an audience-rule edit).
- *Bonus skip.* `IMF World Economic Outlook ``Advanced Economies'' classification` (paragraph 1) recognized as a public citable resource + audience-known field term and kept verbatim, despite not being one of the named test cases.

### Audience model built explicitly before editing

The dispatched agent articulated venue and information set before any character changed:

- **Venue.** Empirical macro-finance / international-macro working paper or top finance-journal submission, inferred from signals in the fragment (AE/EM cut, sovereign-spread puzzle framing, IMF WEO reference, country-clustered SEs, Zenodo replication package).
- **Information set.** The paper itself in current draft state; the IMF WEO classification; the standard meaning of AE/EM; the standard meaning of "sovereign spread"; works the paper cites. Not in set: any internal coreAE/AE-EM tooling, the repo, the editing conversation.
- **Application to paragraph 3.** Under that model, `This paper investigates the AE/EM sovereign-spread puzzle.` has no audience-leakage — every term resolves from the set after paragraph 1 defines AE/coreAE/EM and paragraph 2 frames the AE-EM relationship as a puzzle. The sentence is *audience-clean*; the problem with it is a different one (see next subsection).
- **Ambiguity-elicitation caveat.** Bundling paragraph 3 with paragraphs 1 and 2 dissolves the venue ambiguity at document scope (IMF WEO, AE/EM, country-clustered SEs, Zenodo all read together). The recorded outcome therefore demonstrates *assumed* audience modeling from cross-paragraph signals, not *elicited* modeling from an isolated ambiguous sentence. The plan's Expected Result names "elicit *or assume*," so the upstream-audience-model property is shown; the elicitation-on-ambiguity property that a separate paragraph-3-only dispatch would have isolated is not.

### `authorial` surface — three items raised, none silently rewritten

- Paragraph 3 topic-vs-contribution gap. Paragraph 3 carried two design purposes: PLAN Step 1 labels it the audience-model-elicitation test case, while the fragment's actual `% intent: state the contribution.` comment names the paragraph's stated job inside the document. The agent surfaced an `authorial` finding against the in-fragment intent comment — sentence states the topic (`This paper investigates the AE/EM sovereign-spread puzzle.`), not the contribution — because rewriting without the author would invent substance. Surfaced per `polish.md §Triage`.
- Paragraph 2 transition-without-antecedent. `We now turn to robustness.` is fine as a transition but the surrounding fragment supplies no antecedent main result it is robust of; flagged as a fragment-scope ambiguity rather than edited.
- Paragraph 2 ordering. Section-transition → puzzle statement → replication-package pointer → SE convention. Reordering is structural and outside Polish-mode scope; surfaced as `authorial`.

### What this demonstrates

The rule fires exactly where it should, skips exactly where it should, builds the audience model upstream rather than ex-post, and routes meaning-changing surface concerns to the author rather than silently patching them. No edits to `skills/writing/SKILL.md`, `skills/writing/references/style.md`, or `skills/writing/CLAUDE.md` are needed — the rule wording committed in `dfe87bc` is correct.

### Verification artifacts

`/tmp/audience-awareness-verification/draft.tex` (test fragment, polished by the dispatched agent) — removed at this commit. The dispatched agent did not commit; this orchestrator records the outcomes and cleans up.
