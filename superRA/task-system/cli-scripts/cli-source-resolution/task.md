---
title: "Drift-free, install-free CLI source resolution via uv run --script"
status: not-started
depends_on: 
  - wrappers-and-hooks
  - unified-command-surface

tags: []
created: 2026-06-07
---

## Objective

Make every task-system Python execution run through a single model: resolve the package source from whatever is on disk (installed plugin or local checkout) and run the relevant script with `uv run --script <file>` (falling back to `python3 <file>`). The `superra` CLI must never install anything, never create a venv in the caller's project, and always reflect the live source — no version-keyed build cache between the source and what runs. GitHub is a last-resort fallback. There is no installable package and no `pyproject.toml`: PEP 723 inline metadata in each entry script is the single source of truth for dependencies.

The agent-facing entry point is the committed, self-resolving `<task-root>/superra` wrapper. Every agent — main, implementer, reviewer — invokes the CLI through that wrapper; no agent needs the task-system skill, the plugin path, or a PATH install to read or edit a task.

### Problem

Three defects motivate this rework. The first is the original report; the second and third were found while verifying the shipped `uvx`-based design and are demonstrated below.

1. **`uv run superra` provisions the caller's venv.** Running `uv run superra …` from a research project (not the superRA checkout) makes `uv` discover that project's `pyproject.toml` and try to provision its `.venv`, which fails when a `.venv` already exists (`File exists (os error 17)`) and is wrong regardless — the research environment must not be touched to run a task-tree CLI.

2. **`uvx --from <dir>` serves stale builds.** `uvx` keys its build cache on the package **version** (`0.1.2`), not source content. Editing the source without bumping the version makes `uvx --from <path>` reuse the old cached build. Confirmed live: a freshly added `wrapper` subcommand was invisible through `uvx --from <local dir>`, and `--refresh` / `--refresh-package` / `--reinstall` did **not** bust it — only `--no-cache` or a fresh cache dir did. This silently breaks the "always matches the installed version" promise whenever source content changes under a fixed version (a contributor editing the resolved checkout; the hook firing on every edit; a marketplace overwriting a version dir).

3. **Bootstrap is chicken-and-egg.** The agent-facing entry is the `<task-root>/superra` wrapper, but the docs told agents to create it with bare `superra wrapper init`, which presupposes a resolved `superra`. A fresh research project has none — the wrapper is the very thing that makes `superra` resolvable. `superplan` likewise bootstrapped trees with bare `superra task create`, so an agent in a fresh project gets "command not found" or falls back to `uv run superra` (defect 1).

`uv run --script` fixes all three at the root: with a PEP 723 block it is script-scoped (no project discovery, no caller venv — verified: without the block it *still* provisioned `.venv`, so the block is load-bearing), it reads the script file live each run (no version-keyed build cache), and it runs straight from the resolved source directory so the first call needs only that directory, not a pre-existing `superra`. The task-system core is effectively stdlib-only (the only third-party import, `pyyaml` in `_comments.py`, is lazy), so the `python3` fallback works almost everywhere; only comment-sidecar YAML parsing and the dashboard need declared deps.

### Scope

1. **Single execution model — `uv run --script` + `python3` fallback.** Every Python entry runs via `uv run --script <file>` with a `python3 <file>` fallback when `uv` is unavailable. Each entry script carries a PEP 723 block as the single source of truth for its dependencies:
   - `scripts/cli.py` — task + `wrapper` subcommand surface; deps `["pyyaml"]` (core is stdlib; pyyaml only for comment parsing).
   - `scripts/plan_dashboard.py` — dashboard; already carries the full web-stack block; already loose-script-ready (flat sibling imports, `if __package__` → `FileSystemLoader(Path(__file__).parent/…)` for templates/vendor).
   - `scripts/task_hook.py` — PostToolUse hook; stdlib-only block (no deps).
   `cli.py`'s `dashboard` subcommand must not pull the web stack onto the task hot path — the wrapper routes `dashboard` to `plan_dashboard.py` directly (see item 2), so `cli.py`'s block stays minimal.

2. **Resolver: keep the chain, change the terminal exec.** Preserve the bounded resolution chain (env var → local checkout → Claude cache → Codex cache → GitHub), single-sourced in `wrapper_resolver.py`. Changes:
   - Cache-branch existence test becomes `scripts/cli.py` (not `pyproject.toml`, which no longer exists).
   - Terminal exec becomes, per first argument: `dashboard` → `uv run --script <dir>/scripts/plan_dashboard.py …`; the hook entry → `uv run --script <dir>/scripts/task_hook.py`; everything else → `uv run --script <dir>/scripts/cli.py "$@"`. Each with a `python3 <file>` fallback.
   - Keep the speed gate (env read + one file test + one manifest read + one fixed-depth glob; no full-disk walk) and the no-hardcoded-paths invariant.

3. **Drop `pyproject.toml` and the package framing.** Remove `skills/task-system/pyproject.toml`, the `superra_task_system` console-entry/build manifest, and the `uv tool install` convenience guidance. PEP 723 blocks are now the only dependency declaration. The dashboard's `if __package__` branches stay (harmless) but the loose-script (`__package__ is None`) path is the only one exercised.

4. **GitHub last-resort fallback without a package build.** Since `uv run --script` cannot fetch a git subdirectory, the GitHub branch becomes: shallow-clone the repo to a cache dir (e.g. under the user cache), then `uv run --script <clone>/skills/task-system/scripts/cli.py …`. The clone is the only network step and only fires when no env var, checkout, or installed cache exists. The pin (ref) lives only in `wrapper_resolver.py`.

5. **Agent interface — the committed wrapper is the universal entry; subagents never load task-system.**
   - **Universal call form lives in `using-superRA §Task Interface`** (the only skill every agent — including implementer/reviewer subagents — preloads). Update it so the canonical read/edit invocation is the committed `<task-root>/superra` wrapper (e.g. `superRA/superra task read <path>`), which self-resolves and needs no skill load, no plugin path, and no PATH install. Subagents do **not** load `task-system`; tree-level tooling stays load-on-demand for orchestrators/planners only. Do not duplicate the call form into role specs — point to the universal interface.
   - **The wrapper must exist before any subagent is dispatched.** `superplan` creates `<task-root>/superra` at tree-creation time (via the bootstrap form below) and commits it with the tree, so every downstream agent finds a working `superRA/superra`.
   - **Bootstrap form is planner/main-only.** The first call in a fresh project — which creates the wrapper — uses the loaded task-system skill directory: `uv run --script <task-system skill-dir>/scripts/cli.py wrapper init`, following the `<skill-dir>` substitution convention already used by sibling skills. Documented in `task-system/SKILL.md` and wired into `superplan`'s tree-creation step. After the wrapper exists, everything uses `<task-root>/superra`.

6. **Wrapper / hook generation.** `superra wrapper init` and `superra wrapper render-hook` stay; regenerate the committed `<task-root>/superra` and `hooks/task-hook` to the new run-line (uv run --script + python3 fallback). Keep the byte-identity regression test between the committed `hooks/task-hook` and the generator. The hook's existing `uvx → python3` fallback becomes `uv run --script → python3`.

7. **Docs.** Rewrite `task-system/references/internals.md §Setup` and the `SKILL.md` invocation/dashboard rows to the `uv run --script` model: the committed wrapper is the canonical agent/end-user form, the skill-dir `uv run --script` form is the documented bootstrap, no package/console-entry/`uv tool install` framing. Add the bootstrap to `superplan`. (The `--root superRA` redundancy cleanup already landed and stays.)

8. **Tests.** Update `scripts/test_cli.py`: replace `uvx`-build assertions with `uv run --script` resolution/run-line assertions; assert no caller `.venv` is created when run from a project carrying a conflicting `.venv`; assert the `python3` fallback runs the core; assert the GitHub branch emits a clone-then-script form; keep the wrapper/hook byte-identity and idempotency tests.

### Constraints

- **Subagents (implementer/reviewer) load only `using-superRA` and `report-in-markdown`, never `task-system`.** Any CLI knowledge an executing agent needs to read or edit its task must live in `using-superRA §Task Interface` and resolve through the committed wrapper — not through the task-system skill, a skill-dir form, or a PATH `superra`.
- **No hardcoded plugin/cache/version paths in any committed artifact.** The wrapper and hook resolve at runtime from their own on-disk location.
- **Single-source the resolution chain and run-line in `wrapper_resolver.py`.** Duplicated resolver/run logic between the wrapper and the hook is the primary drift risk.

### Validation

- From a non-checkout project that already has a conflicting `.venv`: `superRA/superra task tree` runs and creates **no** `.venv` in the project.
- Editing a resolved source script is reflected on the next wrapper call with no `--refresh` / cache-bust (proves no version-keyed staleness).
- `python3 <dir>/scripts/cli.py task tree` runs the core with no third-party deps installed (proves the fallback and stdlib-only core).
- `superRA/superra dashboard` launches via `uv run --script plan_dashboard.py` and renders templates/vendor from `__file__`-relative paths.
- Resolver picks env var → checkout → Claude manifest → Codex glob → GitHub clone, in order; speed gate holds (no full-disk walk).
- GitHub branch shallow-clones and runs `uv run --script <clone>/…/cli.py` when no local source exists.
- A simulated subagent with only `using-superRA` loaded can read its task via `superRA/superra task read <path>`; no active doc tells a subagent to load `task-system` to read a task.
- After `superplan` creates a tree, `<task-root>/superra` is present, executable, and committed.
- `skills/task-system/pyproject.toml` is removed and nothing in `skills`/`hooks`/`README.md` references it or `uv tool install` as the normal path.
- `superra wrapper init` writes an executable, resolver-carrying wrapper; re-run is byte-identical; committed `hooks/task-hook` is byte-identical to the generator.

## Planner Guidance

**What already exists and stays** (from the prior `uvx`-based implementation, commits `5de74de9..76473463`): `scripts/wrapper_resolver.py` as the single-source generator rendering both shell artifacts; the bounded resolution chain and its priority order; the `superra wrapper init` / `render-hook` subcommands; the byte-identity regression test; the `--root` auto-detect doc cleanup; `cli.py`'s flat-import fallback (`sys.path.insert` + package-or-flat `importlib`). Reuse all of it.

**What changes:** the terminal exec form (`uvx --from <dir> superra` → `uv run --script <dir>/scripts/<entry>` + `python3` fallback, routed by subcommand); the cache-branch existence test (`pyproject.toml` → `scripts/cli.py`); deletion of `pyproject.toml` and package framing; the GitHub branch (uvx-git → shallow-clone + script); PEP 723 blocks added to `cli.py` and `task_hook.py` (`plan_dashboard.py` already has one); and the agent-interface + bootstrap docs (items 5, 7).

Keep the resolver and run-line single-sourced in `wrapper_resolver.py` — render both the wrapper and the hook from it, embedded (not sourced), since the wrapper lives where it cannot source from the plugin before resolving it.

Generated role/Codex artifacts are out of scope unless a change touches canonical agent specs. Item 5 edits `using-superRA §Task Interface` (a skill, not an agent spec) and `superplan` — these are not generated. If any edit reaches `agents/implementer.md` or `agents/reviewer.md`, regenerate via `skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` rather than hand-editing.

## Results

(Pending re-implementation under the `uv run --script` design. The prior `uvx`-based implementation is in git history — commits `5de74de9` through `76473463` — and is being reworked per ## Revision Notes; reuse the surviving infrastructure listed in ## Planner Guidance.)

## Revision Notes

**Substantive rework (status reset to not-started).** The shipped design resolved the installed source on disk and ran it with `uvx --from <source> superra`. Verification surfaced two blocking defects: `uvx --from <dir>` serves **stale builds** (cache keyed on package version `0.1.2`; not bustable by `--refresh`/`--reinstall`, only `--no-cache`/fresh-cache — demonstrated by a new subcommand being invisible), which silently breaks the drift-free promise; and the **bootstrap was chicken-and-egg** (creating the wrapper required an already-resolved `superra`). Reworked to a single `uv run --script` model that reads source live (no version cache) and is project-independent given a PEP 723 block, with a `python3` fallback. `pyproject.toml` and the installable-package framing are dropped — PEP 723 blocks become the single dependency source of truth — which supersedes the `uv-package` sibling's build-manifest deliverable. Added an explicit agent-interface scope item: the committed `<task-root>/superra` wrapper is the universal entry for main/implementer/reviewer, taught in `using-superRA §Task Interface`; subagents never load `task-system`; the skill-dir bootstrap is planner-only and `superplan` creates the wrapper at tree-creation time. GitHub fallback reworked from uvx-git to shallow-clone + `uv run --script`.
