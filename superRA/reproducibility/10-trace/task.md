---
title: "Follow-up: `repro trace` Derives Deps and Outs from a Real Run"
status: postponed
depends_on: [02-runner]
---

## Objective

Add `superra repro trace <step>`: run the step under a file-open hook and report every file it read or wrote that the declaration omits, and every declared dep it never touched, so agents can verify or generate declarations from evidence.

- Julia steps: a preamble loaded with `-L` that wraps `Base.open` and records paths; Python steps: `sys.addaudithook("open")`; other commands: unsupported, say so.
- Output is a diff against the step's declaration; `--write` applies it to the task's `## Reproduction` section.
- Postponed: the Julia hook is the riskiest piece of the workstream and must not gate the pilots.

## Results
