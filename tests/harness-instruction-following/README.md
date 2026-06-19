# Harness Instruction-Following Audit

`load_contract.json` is the compact source-of-truth audit for planned harness instruction-following tests. It lists source paths, triggers, expected evidence, and whether each check is CI-safe or requires manual live Claude/Codex evidence.

| Area | Entries | Primary check class |
|---|---:|---|
| Manifest, roles, generated agents | LC001-LC006 | static plus live transcript |
| Stage loads | LC007-LC010 | static plus live transcript |
| Domain loads | LC011-LC014 | static plus live transcript |
| `superra task read` behavior | LC015-LC018 | fixture, with selected live transcript checks |
| Hook registries | LC019 | static and fixture |
| Workflow orchestration | LC020-LC022 | static plus manual live transcript |

Static findings are included in the JSON under `static_findings`. They should become lint or follow-up issues, not live-agent behavior assertions.
