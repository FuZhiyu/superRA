# Baseline IO: frontmatter, filename, paths, metadata

Load when producing a **permanent** markdown artifact — one that will be committed and read by humans. Stage 1 `RESULTS.md` task sections do not need this.

## Resolve output path

1. Check project guidance (`CLAUDE.md`, `AGENTS.md`, project `README.md`, `.claude/` docs) for a documentation or report path.
2. If project guidance specifies a location, use it.
3. If the skill invoking you (e.g., `integration-workflow`) specifies a location, use that.
4. Otherwise, fall back to `./scratch/` (create if needed). Use `scratch/` for transient output only.

Define:
- `REPORT_DIR` = resolved directory
- `REPORT_ATTACHMENTS_DIR` = `${REPORT_DIR}/attachments` (or the directory the caller passed in)

## Gather metadata

```bash
# Git state
git log -1 --pretty=format:"%H"          # HEAD commit
git log -1 --pretty=format:"%s"          # HEAD commit subject
git diff --quiet; echo $?                # 0 = clean, 1 = dirty

# Timestamp
date -u +"%Y-%m-%dT%H:%M:%S"
```

Session ID: use context if available; otherwise generate `session-YYYYMMDD-HHMMSS`.

## Filename

`YYYY-MM-DD-report-[description].md` for standalone reports.

For `RESULTS.md` maturing at INTEGRATE Document, the filename is simply `RESULTS.md`, placed at the permanent location (not date-stamped). The name is the identity of the artifact across stages — do not rename.

## Frontmatter

```yaml
---
author: "[[UserName]]"
date: YYYY-MM-DD
timestamp: "YYYY-MM-DDTHH:MM:SS"
session_id: "[from context or session-YYYYMMDD-HHMMSS]"
git_commit: "[current HEAD]"
git_message: "[HEAD commit subject]"
git_dirty: true/false
tags: ["report"]
project: "[[ProjectName]]"
permalink: "[project-relative path without extension]"
---
```

Field notes:

- `author`: wiki-link format `[[Name]]` if the project uses wiki links (e.g., Obsidian-style notes). Otherwise a plain name.
- `tags`: caller can add more (e.g., `"results"`, `"integration"`, `"30-minute"`).
- `project`: include if known from context or project guidance.
- `git_message`: human-readable HEAD commit subject — pairs with `git_commit` for quick identification without a separate git lookup.
- `git_dirty`: record honestly. Stage 2 `RESULTS.md` should be written *as part of* the integration commit, so the expected state is `false` at commit time. If you are drafting before committing, `true` is fine — the record is for auditability, not gating.
- `permalink`: project-relative path with no extension. Example: `analyses/bop/RESULTS` or `notes/2026-03-07-report-analysis`.

## Write the file

Write the caller's content verbatim after the frontmatter. **No content modifications.** If the content violates `rich-content.md` or `final-form.md` rules, that is the caller's responsibility — report back but do not silently edit.

## Return a clickable link

After writing, print:

```
Report saved: [REPORT_DIR/FILENAME.md](REPORT_DIR/FILENAME.md)
```

Use the relative path from the current working directory so the link resolves in the terminal.
