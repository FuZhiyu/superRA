# Baseline IO: frontmatter, filename, paths, metadata

For a permanent standalone Markdown artifact outside a task directory.

## Resolve output path

1. A documentation or report path from project guidance (`CLAUDE.md`, `AGENTS.md`, project `README.md`, `.claude/` docs), when specified.
2. Else a location the invoking skill (e.g. `superintegrate`) specifies.
3. Else `./scratch/` (create if needed) — transient output only.

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

- `author`: wiki-link `[[Name]]` when the project uses wiki links (Obsidian-style notes); otherwise a plain name.
- `tags`: caller can add more (e.g., `"results"`, `"integration"`, `"30-minute"`).
- `project`: include if known from context or project guidance.
- `git_dirty`: record honestly — auditability, not gating. `false` at commit time, `true` while drafting.
- `permalink`: e.g. `analyses/bop/RESULTS` or `notes/2026-03-07-report-analysis`.

## Write the file

Write the caller's content verbatim after the frontmatter. Content violating `markdown.md` is the caller's responsibility — report back, never silently edit.

## Return a clickable link

```
Report saved: [REPORT_DIR/FILENAME.md](REPORT_DIR/FILENAME.md)
```

Path relative to the current working directory, so the link resolves in the terminal.
