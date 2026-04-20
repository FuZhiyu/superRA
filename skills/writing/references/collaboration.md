# Collaboration — Respect the user's in-progress work

> Load at the **IMPLEMENT phase** on every writing dispatch. The writing vertical is tight-collaboration territory: the user is often editing the same file you are. This reference teaches you to detect the user's in-progress work, respect it, and escalate rather than proceed when the request would take you beyond your authority. Severity markers: `[BLOCKING]` must fix to earn APPROVE; `[ADVISORY]` flaggable as MINOR.

This reference anchors the **Preserve** side of the Iron Law (main SKILL.md) at the operational level. It teaches specific detection patterns, escalation templates, and a decision matrix for "edit vs propose vs ask".

## Principle

The researcher's voice is the final voice (main SKILL.md §RA framing). The researcher is also frequently *still writing* — sections are in progress, sentences carry `[fill in]` placeholders, paragraphs are commented-out for rework, entire files may be mid-revision. **Unfinished is not an invitation; it is a DO-NOT-TOUCH flag.**

The rule: **never touch lines the user is actively editing unless the request names them.**

## Detection patterns

Before editing any file, scan for the following signals of in-progress work.

### Git-level signals

```bash
git status                # modified but uncommitted = user is working on these
git diff                  # read the in-flight changes
git log --oneline -5      # recent commits — if they're all from the user in the last hour, the file is live
```

Files with uncommitted edits from the user are **hot**. Rules:

- If your edit needs to touch a hot file, read the uncommitted diff first.
- If the lines you would edit overlap with the lines the user just edited, **stop and ask**.
- If the overlap is accidental (you can do the job without touching the user's new lines), proceed around them.

### In-file signals

**Inline TODO markers — leave alone.**

- `TODO`, `TODO:`, `FIXME`, `XXX`, `HACK`
- LaTeX: `\todo{...}` (from `todonotes` package)
- Placeholder brackets: `[fill in]`, `[citation needed]`, `[TBD]`, `??`, `...`
- Author-note macros: `\mynote{...}`, `\todo[color=red]{...}`

These are deliberate flags. They mean "I will come back to this". Do not fill them in. Do not delete them. Do not edit the line they're on unless the edit is clearly orthogonal (typo three lines away).

**Commented-out text — leave alone.**

- LaTeX: `% this paragraph needs work`
- Markdown: HTML comments `<!-- ... -->` with prose inside
- Consecutive `%` lines containing sentence-structured prose

Commented-out text is the author's staging ground. Do not uncomment. Do not delete. Do not "clean up" commented-out content that looks stale — the author may be planning to revive it.

**Unfinished paragraphs.** Signals:

- Paragraphs ending mid-sentence or with `...`.
- Paragraphs with bullet-point skeletons waiting to be fleshed out (`• argue that X • show figure • conclude`).
- Paragraphs with bracketed self-notes inline (`the effect is (magnitude?) larger than predicted`).

**Recently-touched hunks.** If `git blame` shows a paragraph was last touched by the user in the past hour, treat it as hot. Editing a sentence the user just wrote is high-risk for overwriting in-flight changes.

### File-level signals

- File named `*-draft.tex`, `*-WIP.md`, `drafts/*.tex` — treat the whole file as hot.
- File present in `.gitignore` — usually not meant for agent edits; ask before touching.
- File marked read-only — respect the marker.

## The "edit vs propose vs ask" decision matrix

For any contemplated edit, route it through this matrix:

| The edit is... | And the request... | Action |
|---|---|---|
| Within scope of request, in stable (non-hot) lines | Explicit polish / proofread | **Edit.** Apply minimally. |
| Within scope of request, on a hot line | Explicit polish / proofread | **Ask first.** "I see you recently touched line N; should I include it in the polish?" |
| Within scope of request, on a line with TODO / placeholder | Explicit polish / proofread | **Skip with note.** "Line N has a TODO — leaving for author." |
| Outside explicit scope, sentence-level | Could be argued as within "polish" | **Propose.** "I noticed §4 has the same nominalization pattern; want me to apply the same polish there?" |
| Outside explicit scope, structural (reorder, merge paragraphs, add subsection) | Any polish / proofread / consistency request | **Propose, do not perform.** Iron Law §Scope violation if performed. |
| Any edit that would change meaning, claim, or argument | Any request | **Ask.** Even for polish. Meaning violation is never worth the risk. |
| Any edit to commented-out text | Any request | **Do not touch.** Ask if you think it's relevant. |

## Escalation patterns

### The "I noticed..." pattern (low-stakes proposal)

When you notice a nearby issue outside scope and want to flag it without performing the edit:

> "While polishing §3.2, I noticed §3.4 has a similar nominalization issue (`the quantification of response` on line 412). Want me to apply the same polish there, or is it intentional?"

### The "should I include..." pattern (scope-boundary question)

When scope is ambiguous:

> "The request was to polish §3.2. Does that include the footnotes in §3.2, or only the body text?"

### The "conflict with in-progress work" pattern (high-stakes)

When a hot line is in scope:

> "I see the commit from 23 minutes ago edited line 412 (`'beta'` → `'\beta'`). My planned polish touches line 412. Should I leave it alone, or include it in this pass?"

### The "structural proposal" pattern

When you think a structural change would help:

> "The current §3 first paragraph buries the main finding in the last sentence. The Pyramid Principle would suggest moving it up. This is a structural change — want me to proceed, or would you prefer to handle it yourself?"

### Tool choice

- **`AskUserQuestion`** — use when the harness exposes it (Claude Code does). Forces a structured response and logs the decision.
- **Plain text question in chat** — fallback when the tool is unavailable.

Per `superRA:using-superRA` §Universal Principles #4 and `handoff-doc` §User Decisions Log: **every user decision at an escalation point is logged into `PLAN.md` before you act on it.** If the workflow mode skips `PLAN.md` (direct-edit), the decision is preserved in the commit message and chat transcript.

## Framing proposed structural changes

When proposing a structural change, make it easy for the researcher to say yes or no:

1. **Show current state.** Brief outline of what's there now.
2. **Show proposed state.** Brief outline of what the change would produce.
3. **State the rationale.** One sentence — which rule / principle / reader concern motivates the change.
4. **State the cost.** What else moves? Will cross-references break? Does a table need reordering?
5. **Ask.** "Proceed, modify, or skip?"

Example:

> **Current §3 outline.** 3.1 Data sources. 3.2 Sample construction. 3.3 Summary statistics. 3.4 Identification.
>
> **Proposed §3 outline.** 3.1 Data sources. 3.2 Identification. 3.3 Sample construction. 3.4 Summary statistics.
>
> **Rationale.** Identification is the reader's first question after learning the data exist. Structure-checklist.md recommends methodology → sample → summary stats.
>
> **Cost.** Zero internal cross-references to §3.3 or §3.4 to update (checked with grep).
>
> **Proceed, modify, or skip?**

## What "voice preservation" means in practice

Voice is **diction + register + sentence-shape**. It is NOT claims, structure, or intent — those are owned by the Iron Law clauses separately.

Diff-level signals your edit preserved voice:

- Contractions: if the author uses `don't`, don't change to `do not`.
- Formality: if the author writes "we argue", don't escalate to "the authors argue" (or the reverse).
- Sentence-length variance: if the author writes punchy 10-word sentences, don't merge into 30-word academic megastructures.
- Technical register: if the author uses "treatment effect", don't globally substitute "effect of the treatment" (technically equivalent, stylistically different).
- Hedging style: if the author writes "X appears to", don't substitute "X seems to".
- Favored transitions: `However,` vs `That said,` — pick the author's.

When in doubt: **would the author's co-author recognize this as the author's paragraph?** If not, voice has drifted.

## Gated Checklist

> **Walked in addition to `skills/writing/SKILL.md` §Three Concurrent Disciplines — SKILL.md's Preserve quartet (no edits outside scope, voice preservation, in-progress-work respected, meaning preservation) is not repeated here. This file adds collaboration-specific detection and escalation gates.**

- `[BLOCKING]` **`git status` / `git diff` checked before editing any file** — in-flight user work identified.
- `[BLOCKING]` **Hot lines identified and handled explicitly** — either skipped, or the user was asked first (collaboration-specific detection).
- `[BLOCKING]` **Escalation template used** when an edit fell into the "propose" or "ask" row of the decision matrix — no silent performs.
- `[BLOCKING]` **User decisions from escalations logged** — per `handoff-doc` §User Decisions Log if `PLAN.md` is in use, or in the commit message if in a workflow mode that skips `PLAN.md`.
- `[ADVISORY]` **Scope-boundary ambiguities raised** — when unclear whether footnotes / boxes / captions / appendices are in scope, ask.
- `[ADVISORY]` **Nearby-but-out-of-scope issues flagged** for the researcher as low-stakes proposals.

## Reviewer verdict protocol

Walk top to bottom, never halt, return APPROVE / REVISE.
