# Research: Prompting Concise, Information-Dense Writing

Hand-authored from a web-research agent dispatch, 2026-08-01. Sources cited inline.

## (A) Per-source findings

### Caveman (https://github.com/JuliusBrussee/caveman)

Techniques (from `skills/caveman/SKILL.md`, `caveman-compress`, `caveman-review`):

1. Deletion lists by category: "Drop: articles (a/an/the), filler (just/really/basically/actually/simply), pleasantries (sure/certainly/of course/happy to), hedging." Redundant-phrasing rewrites: "'in order to' → 'to', 'make sure to' → 'ensure', 'the reason is because' → 'because'".
2. Preserve-exactly invariants: code blocks, inline code, URLs, paths, commands, technical terms, proper nouns, dates/versions/numbers — "Anything inside ``` must be copied EXACTLY." Compression applies to prose only.
3. Sentence template: "`[thing] [action] [reason]. [next step].`" with paired bad/good example.
4. Intensity levels (lite/full/ultra) — lite keeps articles and full sentences ("No filler/hedging... Professional but tight"); this is the transferable level.
5. Tokenizer-aware anti-abbreviation rule: "never invent new abbreviations (cfg/impl/req/res/fn) — tokenizer split them same as full word: zero token saved, reader still decode... No causal arrows (→) either — own token, save nothing."
6. Auto-Clarity escape hatch: drop terse mode for security warnings, irreversible-action confirmations, order-dependent sequences, and whenever "compression itself creates technical ambiguity."
7. Persistence clause against style decay: "ACTIVE EVERY RESPONSE. No revert after many turns. No filler drift."
8. "State each fact once" (direct anti-duplication rule); compress mode: "Merge redundant bullets that say the same thing differently. Keep one example where multiple examples show the same pattern."
9. Review mode one-line finding format: "`L<line>: <problem>. <fix>.`"; drop "restating what the line does — the reviewer can read the diff"; keep "the *why* if the fix isn't obvious."
10. Honest measurement: the skill costs ~1–1.5k input tokens/turn; "on already-terse workloads they can go net-negative. The real win is readability and speed." README cites arXiv:2604.00025 (brevity constraints improved accuracy ~26 points on some benchmarks for large models).

### Karpathy skills (https://github.com/multica-ai/andrej-karpathy-skills)

About coding behavior, not prose — but three principles transfer to writing:

1. Think Before Coding → the pre-writing step: "State your assumptions explicitly. If uncertain, ask... If multiple interpretations exist, present them - don't pick silently."
2. Simplicity First → the anti-bloat test: "Minimum code that solves the problem. Nothing speculative... If you write 200 lines and it could be 50, rewrite it." Reviewer-persona test: "Would a senior engineer say this is overcomplicated? If yes, simplify."
3. Surgical Changes → editing existing files: "Touch only what you must. Clean up only your own mess... Every changed line should trace directly to the user's request."

Craft lesson: each principle is a bolded 5–10-word slogan + 4–5 bullets + a one-line test; the whole file is ~2.4KB. Tiny, sloganized, test-terminated principles beat long rule lists.

### Anthropic docs (Opus 5 / Fable 5 / best practices)

- Verbosity is a prompt problem, not an effort problem: "The effort parameter controls how much the model thinks rather than how much it says... To control response length, prompt for it explicitly." "A short conciseness instruction is effective"; in long prompts, add a short reminder near the end.
- **Written files are a separate axis from chat verbosity**: "files that Claude Opus 5 writes to disk (reports, Markdown documents, summaries) are often longer than on prior models. If your product includes Claude-authored documents, add explicit length calibration." Sample: "Match the length of written documents to what the task needs: cover the substance, but do not pad with filler sections, redundant summaries, or boilerplate." The most on-point official guidance for the task-file problem.
- Fable 5 brevity-by-selection doctrine (verbatim): "Being readable and being concise are different things, and readability matters more. The way to keep output short is to be selective about what you include (drop details that don't change what the reader would do next), not to compress the writing into fragments, abbreviations, arrow chains like A → B → fails, or jargon."
- Fable 5 instruction following: "you can steer most behaviors with a brief instruction rather than enumerating each behavior by name... A short brevity instruction is as effective as listing each pattern." And: "Skills developed for prior models are often too prescriptive for Claude Fable 5 and can degrade output quality."
- Re-grounding for cold readers: "The vocabulary you built up while working is yours, not theirs; leave it behind unless you re-introduce it... When you mention files, commits, flags, or other identifiers, give each one its own plain-language clause. Open with the outcome... If you have to choose between short and clear, choose clear."
- Grounding doubles as density: "Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for."
- Best practices: positive framing ("Tell Claude what to do instead of what not to do"); 3–5 examples are "one of the most reliable ways to steer output format, tone, and structure"; prompt style is contagious ("Match your prompt style to the desired output"); motivation generalizes ("Claude is smart enough to generalize from the explanation").

### Broader search

- avoid-ai-writing (https://github.com/conorbronsdon/avoid-ai-writing, 88KB catalog): tiered banned vocabulary; the treadmill test — "read each paragraph and ask 'what's actually new here?'... The tell is that you could cut 40-60% and lose no information. The fix: for each paragraph, name the one fact, claim, or turn it contributes. If there isn't one, cut it."; delete-the-clause test ("if the sentence still works after you delete the inflation clause, delete it"); structural bans ("It's not X — it's Y", hollow intensifiers, rule-of-three compulsion, bold overuse, generic conclusions). As a whole: a detector, too heavy to ship — mine a small banned list only.
- BLUF (https://en.wikipedia.org/wiki/BLUF_(communication), https://podrez.pl/en/bluf/): conclusion first; LLM-era twist — chunked retrieval means "every chunk understandable on its own"; front-loaded takeaways serve both humans and downstream agents reading fragments.
- Length-control research (https://arxiv.org/pdf/2508.13805, https://arxiv.org/pdf/2506.08686): exact word counts are poorly obeyed; structural budgets (N bullets, one paragraph, one line per finding) are followed far better.
- Outline-first (STORM, https://arxiv.org/pdf/2402.14207): plan-before-draft measurably improves quality; frame the pre-writing step as "decide," not "show your reasoning."

## (B) Keep/drop for the superRA house style

Keep: caveman-lite register (no filler/hedging/pleasantries, full sentences kept); preserve-exactly invariants; no invented abbreviations or arrow chains (caveman and Fable 5 docs agree from opposite directions); clarity escape hatch; state-each-fact-once; one-line finding format for reviews; slogan+test packaging; senior-colleague padding test; surgical edits; treadmill test; delete-the-clause test; BLUF; small banned list as examples; structural budgets; selection-not-compression doctrine; claims-need-evidence grounding.

Drop: caveman full/ultra grammar destruction; emoji severity; exact word/token caps; the 88KB catalog; paragraph-shuffle immunity (reference docs legitimately have independent sections); "sound human" goals; persistence machinery (chat-cost problem, not document quality).

## (C) Candidate rule set for results-file writing (~16 rules)

Before writing (selection):

1. Decide what the reader needs before touching the file: who reads this (future agent with no session context; human skimming), what they'll do with it, and which 3–7 facts change what they do next. Everything else is omitted, not summarized.
2. Check what is already recorded: facts carried by git history, the objective, another task file, or a linked artifact are cited by path/SHA, not restated. One home per fact.
3. Choose the shape before the words: one takeaway per section; a section with no takeaway doesn't exist.

Writing:

4. Lead with the outcome — first sentence of the file and of each section answers "what happened / what did we find."
5. Short by selection, not compression: drop details that don't change the reader's next action; no fragments, invented abbreviations, or arrow chains.
6. State each fact once; delete restatements-for-emphasis.
7. Numbers, commands, paths, error strings verbatim; every claim traceable to an artifact, output, or commit.
8. Plain words, short sentences, active voice ("use" not "utilize/leverage", "is" not "serves as", "to" not "in order to").
9. No hedging, intensifiers, or significance inflation; if a clause deletes cleanly, delete it.
10. Say the positive claim directly; never "it's not X, it's Y."
11. One idea per unit; bullets only for genuinely list-like content; never a bullet restating its neighbor.
12. One example where several show the same pattern.
13. Consistent terminology, defined at first use; no session-local vocabulary — cold readers get each identifier a plain-language clause.
14. Explain in full where compression risks misreading: surprising results, order-dependent procedures, destructive operations, caveats.

Editing / gate:

15. Touch only sections your work changed; supersede stale content, never append a second version of the truth.
16. Final pass per paragraph: "what's new here?" — no new fact/claim/decision → cut. Whole-file test: could a busy colleague act on this in one read without calling any of it padding?

## (D) Compliance mechanics — what makes models actually comply

1. Target the deliverable explicitly ("documents/files you write"), not just chat verbosity — they are separate behaviors.
2. Short contracts beat catalogs on frontier models; over-prescriptive skills degrade output.
3. Positive framing + motivation ("task files are re-read by cold-context agents; every extra paragraph is paid on every future read").
4. Paired bad/good examples are the highest-leverage single device — one before/after of a padded vs dense results section.
5. Prompt style is contagious: write the skill itself in the target style.
6. Structural budgets over word counts.
7. Pre-writing selection step framed as "decide," executed silently — no written per-item justification.
8. One self-audit revision pass converges; a third pass rarely finds more.
9. Reminder placement fights drift: full rule once + one-line reminder near the end of long prompts.
10. Beware literal obedience: "omit what doesn't change the reader's action" is safer than "keep under N words" (which silently drops substance).
11. The anti-compression guardrail is as necessary as the anti-verbosity rule — brevity instructions alone push models into fragments/jargon.
12. Grounding ("only report work you can point to evidence for") removes both fabrication and padding.

## Sources

https://github.com/JuliusBrussee/caveman · https://github.com/multica-ai/andrej-karpathy-skills · https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5 · https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5 · https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices · https://github.com/conorbronsdon/avoid-ai-writing · https://en.wikipedia.org/wiki/BLUF_(communication) · https://podrez.pl/en/bluf/ · https://arxiv.org/pdf/2508.13805 · https://arxiv.org/pdf/2506.08686 · https://arxiv.org/pdf/2402.14207 · https://developers.google.com/style
