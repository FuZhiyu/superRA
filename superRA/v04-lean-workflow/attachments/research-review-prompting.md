# Research: Review Prompting and Scheduling for Frontier Models

Hand-authored from a web-research agent dispatch, 2026-08-01. Sources cited inline; key source URLs listed at the end.

## (A) Key findings

**Anthropic Opus 5 prompting doc** (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5):

- Self-verification is now default behavior: "Claude Opus 5 verifies its own work without being told to. If your prompt contains explicit verification instructions ('include a final verification step for any non-trivial task,' 'use a subagent to verify'), remove them: instructions like these cause over-verification... The same applies to legacy harness scaffolding that adds separate verification steps."
- Self-correction likewise: "Claude Opus 5 catches and fixes its own mistakes well without prompting. Avoid instructing re-checks it already performs ('double-check your answer,' 're-verify before responding'); these compound with the model's own behavior and add cost without improving results."
- Explicit anti-pattern for verify-subagents: "do not use subagents to verify or double-check your own work."
- Review capability: "it finds real bugs at a high rate per pass, and its additional findings are mostly real issues rather than false positives. Accuracy holds at lower effort settings, which supports a fast pass at review time and a more thorough pass later."
- Calibration warning: "If your review prompt says 'only report high-severity issues' or 'be conservative,' the model may follow that instruction literally and report less; ask it to report everything and filter in a separate pass instead." Severity suppression belongs in a filter pass, not the finder prompt.
- Scope discipline: models over-expand tasks; recommended phrasing: "Deliver what was asked, at the scope intended... If the request seems mistaken or a better approach exists, say so in a sentence and continue with the task as asked rather than quietly narrowing, widening, or transforming it."
- Instruction-following is literal: strongly-worded instructions are followed literally and compound with defaults. "Positive examples of the communication style you want tend to be more effective than instructions about what not to do." Deliverable-length calibration: "cover the substance, but do not pad with filler sections, redundant summaries, or boilerplate."

**Anthropic Code Review product** (https://claude.com/blog/code-review, https://code.claude.com/docs/en/code-review, https://www.infoq.com/news/2026/04/claude-code-review/):

- Architecture: parallel finder agents by issue class → a verification step that tries to disprove each finding ("checks candidates against actual code behavior to filter out false positives") → dedupe → severity rank. Result: "less than 1% of findings are marked incorrect."
- Depth scales with change size: "Large or complex changes get more agents and a deeper read; trivial ones get a lightweight pass." Small PRs (<50 lines): 31% have findings, avg 0.5 issues — most small changes yield nothing, supporting skip/light policies.
- Two severities that matter: Important ("a bug that should be fixed before merging") vs Nit ("worth fixing but not blocking"), plus Pre-existing. Default focus: "correctness: bugs that would break production, not formatting preferences or missing test coverage."
- Reviews never block: "Findings are tagged by severity and don't approve or block your PR."
- Effort ↔ confidence: "At `low` and `medium`, the review reports only the findings it's most confident in... `high` through `max` cast a wider net."

**Cloudflare AI review at scale** (https://blog.cloudflare.com/ai-code-review/):

- "telling an LLM what not to do is where the actual prompt engineering value resides" — each agent prompt has a "What NOT to Flag" section (theoretical risks with unlikely preconditions, defense-in-depth when primary defenses are adequate, issues in unchanged code). [Researcher declined this device for superRA.]
- Coordinator pass "drops speculative issues, nitpicks, false positives, and convention-contradicted findings." Net ~1.2 findings/review.
- Verdict bias toward approval: only critical/production-safety findings block; warnings → approved-with-comments.

**Cross-model review evidence** (https://arxiv.org/html/2607.21656v1):

- "Claude Opus 4.7 review raises Codex GPT-5.5 drafts from 71.6% to 89.7%; Codex GPT-5.5 self review raises them to 84.5%... Codex GPT-5.5 reviewing Claude Opus 4.7 drafts drops the pass rate from 91.4% to 82.8%." Claude reviewing Claude: 91.4% → 91.4% (no change).
- Conclusion: "If Claude Opus 4.7 writes the draft, submit it as is, because no reviewer we tested beats Claude Opus 4.7 working alone." Review only pays when reviewer ≥ writer capability; equal-strength independent review of frontier output measured zero gain and weaker reviewers actively harmed. (Caveat: LiveCodeBench-style tasks and pass-rate metric — not research-workflow correctness.)
- Counterpoint on recall (https://zylos.ai/research/2026-03-01-multi-model-ai-code-review-convergence/): multiple independent passes + aggregation raised recall +118% over a single pass, at cost.
- Heterogeneous-tool evidence (https://addyosmani.com/blog/agentic-code-review/): of bugs caught by 4 commercial reviewers, "93.4% were caught by exactly one of the four tools" — reviewers have nearly disjoint findings; same-family self-review risks correlated blind spots.

**Nitpick calibration has a prompting ceiling** (https://www.zenml.io/llmops-database/improving-ai-code-review-bot-comment-quality-through-vector-embeddings, https://www.greptile.com/docs/how-greptile-works/nitpicks):

- Greptile: "prompting doesn't solve this problem, LLMs are poor evaluators of comment severity, and the definition of a 'nit' is subjective and varies from team to team." Their fix: learned per-team filtering from accept/reject signal (addressed rate 19% → 55%+). Implication: capture the researcher's accept/reject taste over time rather than hardcoding a rubric.
- Noise cost framing (https://www.codeant.ai/blogs/prevent-ai-code-review-overload): real issues get "buried among 60 AI-generated nitpicks"; 70–90% of comments ignored.

**Risk-tiered review policy** (https://codex.danielvaughan.com/2026/05/24/human-review-bottleneck-code-review-strategies-agent-output/, https://www.augmentcode.com/guides/adversarial-code-review, Osmani):

- "Tier by risk, not by author"; "review depth set by blast radius rather than guilt." Example tiers: critical paths → full independent + human; new deps/schema/concurrency → focused; feature code with tests → skim; mechanical/generated → auto-approve on CI.
- Deterministic gates (tests, lint, types) run before any LLM review; LLM review spends only where deterministic gates can't reach.

## (B) Prompting techniques for calibrated, non-pedantic review

1. Find-then-filter, not suppressed-finder: never tell the finder "only report high-severity" — filter at adjudication.
2. Disproof pass: a finding survives only with `file:line` evidence — "behavior claims need a citation in the source, not an inference from naming."
3. Two-severity verdicts: blocking ("should be fixed before merging") vs non-blocking; only blocking findings can produce REVISE.
4. Define blocking positively and per-domain (e.g. data analysis: wrong merge keys, silent row loss, look-ahead bias).
5. Cap nit volume ("at most five nits; mention the rest as a count"); lead the summary with "No blocking issues" when true.
6. Re-review convergence: rounds after the first report blocking findings only — no new nit classes.
7. Summary-shape: open with a one-line tally.
8. Effort as the confidence dial: low effort → high-confidence findings only.
9. Senior-engineer bar as a second-pass filter criterion: "Would a senior engineer block on this?"
10. Know the ceiling: static rubrics drift from team taste; capture accept/reject signal.

## (C) Design options for when to review

1. **Risk-tiered scheduling** (strongest consensus): classify tasks by blast radius; critical/result-bearing → independent review, standard-with-tests → self-review + gates, mechanical → none. Mitigate misclassification with "when unsure, review."
2. **Author-relative review**: skip independent review when the writer is frontier-class and the reviewer would be same-or-weaker; reserve for weaker implementers or correlated-blind-spot classes (research validity, evidence reading).
3. **On-demand / agent-requested**: self-review default; independent pass when the implementer flags uncertainty; pair with hard triggers so critical paths can't opt out.
4. **Batched / boundary review**: review accumulated work at phase boundaries (pre-INTEGRATE/PR) rather than per task; later detection = bigger rework, so keep per-task review for irreversible steps.
5. **Manual + subscribe**: default none; user or agent opts a task in; periodic sampled deep review as drift control.
6. **Two-speed**: fast low-effort pass per task + thorough high-effort pass at integration.
7. **Non-blocking reviewer**: findings + tally, never gates alone; orchestrator/user adjudicates.

superRA v0.4 chose 3+4+6 combined: triggered per-task review (user request / planner mark / implementer concern) + INTEGRATE-boundary thorough pass + tier/focus scoping per dispatch.

## (D) Implications for superRA instruction wording generally

- Delete verification scaffolding ("verify your work," "double-check," "re-run to confirm," verify-subagents) from skills and role bodies — it now causes over-verification.
- Strong instructions are followed literally and compound — absolute checklist phrasing executes even when redundant; the cost is behavioral, not just context weight.
- Positive exemplars for style; explicit exclusions only where scope precision matters.
- Adopt the scope-constraint phrasing ("Deliver what was asked, at the scope intended...") in the implement role.
- Never write "only report high-severity" into a reviewer prompt.
- Keep spawn counts low ("If one subagent can complete the task, use one").
- Deliverable-length line for reports: "cover the substance, but do not pad with filler sections, redundant summaries, or boilerplate."

## Sources

https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5 · https://claude.com/blog/code-review · https://code.claude.com/docs/en/code-review · https://blog.cloudflare.com/ai-code-review/ · https://arxiv.org/html/2607.21656v1 · https://addyosmani.com/blog/agentic-code-review/ · https://codex.danielvaughan.com/2026/05/24/human-review-bottleneck-code-review-strategies-agent-output/ · https://www.zenml.io/llmops-database/improving-ai-code-review-bot-comment-quality-through-vector-embeddings · https://zylos.ai/research/2026-03-01-multi-model-ai-code-review-convergence/ · https://www.infoq.com/news/2026/04/claude-code-review/ · https://www.greptile.com/docs/how-greptile-works/nitpicks · https://www.codeant.ai/blogs/prevent-ai-code-review-overload · https://www.augmentcode.com/guides/adversarial-code-review
