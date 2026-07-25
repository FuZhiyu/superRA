---
title: "Always-Loaded Skill Canary Task"
status: not-started
depends_on: []
tags: [fixture, canary]
output:
  - always-loaded-evidence.json
created: 2026-06-19
---

## Objective

Read this task with `./superRA/superra task read
always-loaded-task`. You are an implementer; load the skills your role spec tells
you to load before acting. This task proves the two always-loaded skills reached
your context by asking for one skill-unique side effect from each. Do not edit
source code, install anything, or run a test suite.

Do exactly this, in order:

1. Following `superRA:report-in-markdown`, run that skill's own markdown
   self-diagnose CLI on this task file — the script is named in the skill body
   (`check_markdown.py`). Running it is the report-in-markdown canary.
2. Write `always-loaded-evidence.json` at the workspace root with exactly:

```json
{
  "schema_version": 1,
  "report_in_markdown_canary": "check_markdown.py",
  "using_superra_canary": "superra task read"
}
```

The `report_in_markdown_canary` value is the self-diagnose script name from the
report-in-markdown body. The `using_superra_canary` value is the wrapper-read
command form `superRA:using-superra` prescribes for reading a task (`superra task
read <path>`), not a bare file read. Both values are only knowable from the
respective skill bodies, so filling them proves the bodies loaded.
