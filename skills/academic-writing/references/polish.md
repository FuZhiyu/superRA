# Polish Mode

**Apply the [Polish bar](../SKILL.md#mode-routing) with the smallest edit that solves each problem.** Recast rough prose when asked. During triage, use the paper's established [writing conventions](conventions.md).

## Input shapes

- **Unstaged edits.** Use the working tree as the target, limited to diff hunks when requested. Treat the author's changes as the baseline for your diff audit.
- **Accepted review findings.** Use the accepted list or the task's bounded batch of `## Review Notes` as the scope. Surface an ambiguous or incorrect finding. Record why an accepted item was deferred.

## Edit vs propose vs ask

| Situation | Action |
|---|---|
| In scope and at the Polish bar | Edit according to [Fix tiers](review.md#fix-tiers). Use the same tiers for issues diagnosed during Polish and accepted review findings. |
| Recently author-edited lines with unclear scope | Ask whether to include them. |
| Outside scope | Propose a fix only where the issue clears the Polish bar. |
| Authorial decision | Ask the author per [Substance is the author's](../SKILL.md#substance-is-the-authors). |

## Intent comments

**Read existing intent comments before editing.** An intent comment above a paragraph (`% intent: …` in LaTeX or `<!-- intent: … -->` in Markdown or Quarto) describes its purpose. Follow the current request first, then the current text, then the intent comment. When text and comment conflict, ask which should govern. If asking is impractical, align the comment with the text and flag the change.

**Treat new intent comments as author decisions.** Surface the ambiguity and write a comment from the author's answer.
