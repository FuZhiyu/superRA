---
author: Zhiyu Fu
date: 2026-04-19
timestamp: "2026-04-19T20:02:22Z"
session_id: "session-20260419-200222Z"
git_commit: "d3fbcda14779403288653392d1e70f453af2d537"
git_message: "docs: record clean Codex integration review"
git_dirty: true
tags: ["results", "integration", "codex"]
project: "superRA"
permalink: "docs/plans/2026-04-17-codex-compatibility-results"
---

# superRA Codex Compatibility — Results

This branch adds Codex support to superRA without changing the canonical Claude-facing workflow. Shared skills remain in root `skills/`, role specs remain in `agents/`, Codex skill discovery is provided through the plugin surface, and named Codex agents are installed through `codex-superra-setup` rather than through plugin-managed agent files.

## Objective

Add coherent Codex support to superRA without regressing any Claude-facing workflow behavior.

## Data and Sources

No empirical dataset was used. The source material for this work is the repository itself: the Codex plugin manifest in [`.codex-plugin/plugin.json`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/.codex-plugin/plugin.json:1), the local marketplace entry in [`.agents/plugins/marketplace.json`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/.agents/plugins/marketplace.json:1), the Codex setup skill in [`skills/codex-superra-setup/SKILL.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/skills/codex-superra-setup/SKILL.md:1), the Codex install docs in [`.codex/INSTALL.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/.codex/INSTALL.md:1) and [`docs/README.codex.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/docs/README.codex.md:1), and the contributor guidance in [`CLAUDE.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/CLAUDE.md:13).

## Method

The integration pass was organized around three checks:

1. Verify that the Codex plugin surface points at the shared skills bundle and that the local marketplace entry exposes the repo as an installable plugin. [`.codex-plugin/plugin.json`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/.codex-plugin/plugin.json:16) [`.agents/plugins/marketplace.json`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/.agents/plugins/marketplace.json:8)
2. Verify that Codex named-agent installation is separated from the shared skill bundle and that the generated project-scoped agents are refreshed from the canonical role specs. [`skills/codex-superra-setup/SKILL.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/skills/codex-superra-setup/SKILL.md:8) [`skills/codex-superra-setup/scripts/sync_codex_agents.py`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/skills/codex-superra-setup/scripts/sync_codex_agents.py:1)
3. Verify that the top-level compatibility guard covers the Codex metadata, the shared harness adapters, the agent-generation checks, and the structural invariants suite. [`tests/check-harness-compatibility.sh`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/tests/check-harness-compatibility.sh:17)

## Results

### Codex surface

- The Codex plugin manifest points at `./skills/`, and the repo-local marketplace entry exposes `superra` as a local plugin install from `./`. [`.codex-plugin/plugin.json`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/.codex-plugin/plugin.json:16) [`.agents/plugins/marketplace.json`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/.agents/plugins/marketplace.json:8)
- Repo-local Codex discovery uses `.agents/skills/` symlinks, and the generated project-scoped agent files live in [`.codex/agents/superra_implementer.toml`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/.codex/agents/superra_implementer.toml:1) and [`.codex/agents/superra_reviewer.toml`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/.codex/agents/superra_reviewer.toml:1). [`.codex/INSTALL.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/.codex/INSTALL.md:44) [`docs/README.codex.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/docs/README.codex.md:25)
- The setup skill keeps the canonical role instructions in [`agents/implementer.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/agents/implementer.md:1) and [`agents/reviewer.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/agents/reviewer.md:1), and the generated agents are refreshed by [`skills/codex-superra-setup/scripts/sync_codex_agents.py`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/skills/codex-superra-setup/scripts/sync_codex_agents.py:1). [`skills/codex-superra-setup/SKILL.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/skills/codex-superra-setup/SKILL.md:76)

### Metadata and validation

- `CLAUDE.md` instructs contributors to run `bash tests/check-harness-compatibility.sh` for changes that touch shared skill metadata, plugin manifests, harness adapters, hooks, or agent-install surfaces. [`CLAUDE.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/CLAUDE.md:12)
- `AGENTS.md` and `AGENT.md` both resolve to `CLAUDE.md` in this worktree, keeping the contributor guidance single-sourced. [`CLAUDE.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/CLAUDE.md:58)
- `tests/check-harness-compatibility.sh` validates the Claude plugin metadata, the Codex plugin metadata, the shared harness adapters, the Codex agent-generation checks, and then runs `tests/structural-invariants.sh`. [`tests/check-harness-compatibility.sh`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/tests/check-harness-compatibility.sh:17)

### Integration readiness

- The Codex-facing install docs describe the split as intended: the plugin provides shared skills, and `codex-superra-setup` installs `superra_implementer` and `superra_reviewer` into either project or global scope. [`.codex/INSTALL.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/.codex/INSTALL.md:3) [`docs/README.codex.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/docs/README.codex.md:5)
- The root repo docs now state the same split: shared skills are packaged through the Codex plugin surface, and named agents are installed through the setup skill. [`README.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/README.md:130)
- The integration workflow docs treat `RESULTS.md` maturation as the final documentation step before merge readiness. [`skills/integration-workflow/SKILL.md`](/Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/codex-adaption/skills/integration-workflow/SKILL.md:1)

## Limitations

- No figures, tables, or other materialized attachments were produced in this pass, so there was nothing to move into an `attachments/` directory.
- This report covers repository configuration and documentation state only; it does not change `PLAN.md`.

## Reproducibility

Reproduce this state from commit `d3fbcda14779403288653392d1e70f453af2d537` with `bash tests/check-harness-compatibility.sh`.
