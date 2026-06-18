---
title: "Drift-free, install-free CLI source resolution via uv run --script"
status: approved
depends_on:
  - wrappers-and-hooks
  - unified-command-surface
tags: []
created: 2026-06-07
---

## Objective

Make every task-tree Python execution run through a single model: resolve the package source from whatever is on disk (installed plugin or local checkout) and run the relevant script with `uv run --script <file>` (falling back to `python3 <file>`). The `superra` CLI must never install anything, never create a venv in the caller's project, and always reflect the live source — no version-keyed build cache between the source and what runs. GitHub is a last-resort fallback. There is no installable package and no `pyproject.toml`: PEP 723 inline metadata in each entry script is the single source of truth for dependencies.

The agent-facing entry point is the committed, self-resolving `<task-root>/superra` wrapper. Every agent — main, implementer, reviewer — invokes the CLI through that wrapper; no agent needs the task-tree skill, the plugin path, or a PATH install to read or edit a task.

### Problem

Three defects motivate this rework. The first is the original report; the second and third were found while verifying the shipped `uvx`-based design and are demonstrated below.

1. **`uv run superra` provisions the caller's venv.** Running `uv run superra …` from a research project (not the superRA checkout) makes `uv` discover that project's `pyproject.toml` and try to provision its `.venv`, which fails when a `.venv` already exists (`File exists (os error 17)`) and is wrong regardless — the research environment must not be touched to run a task-tree CLI.

2. **`uvx --from <dir>` serves stale builds.** `uvx` keys its build cache on the package **version** (`0.1.2`), not source content. Editing the source without bumping the version makes `uvx --from <path>` reuse the old cached build. Confirmed live: a freshly added `wrapper` subcommand was invisible through `uvx --from <local dir>`, and `--refresh` / `--refresh-package` / `--reinstall` did **not** bust it — only `--no-cache` or a fresh cache dir did. This silently breaks the "always matches the installed version" promise whenever source content changes under a fixed version (a contributor editing the resolved checkout; the hook firing on every edit; a marketplace overwriting a version dir).

3. **Bootstrap is chicken-and-egg.** The agent-facing entry is the `<task-root>/superra` wrapper, but the docs told agents to create it with bare `superra wrapper init`, which presupposes a resolved `superra`. A fresh research project has none — the wrapper is the very thing that makes `superra` resolvable. `superplan` likewise bootstrapped trees with bare `superra task create`, so an agent in a fresh project gets "command not found" or falls back to `uv run superra` (defect 1).

`uv run --script` fixes all three at the root: with a PEP 723 block it is script-scoped (no project discovery, no caller venv — verified: without the block it *still* provisioned `.venv`, so the block is load-bearing), it reads the script file live each run (no version-keyed build cache), and it runs straight from the resolved source directory so the first call needs only that directory, not a pre-existing `superra`. The task-tree core is effectively stdlib-only (the only third-party import, `pyyaml` in `_comments.py`, is lazy), so the `python3` fallback works almost everywhere; only comment-sidecar YAML parsing and the dashboard need declared deps.

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

3. **Drop `pyproject.toml` and the package framing.** Remove `skills/task-tree/pyproject.toml`, the `superra_task_tree` console-entry/build manifest, and the `uv tool install` convenience guidance. PEP 723 blocks are now the only dependency declaration. The dashboard's `if __package__` branches stay (harmless) but the loose-script (`__package__ is None`) path is the only one exercised.

4. **GitHub last-resort fallback without a package build.** Since `uv run --script` cannot fetch a git subdirectory, the GitHub branch becomes: shallow-clone the repo to a cache dir (e.g. under the user cache), then `uv run --script <clone>/skills/task-tree/scripts/cli.py …`. The clone is the only network step and only fires when no env var, checkout, or installed cache exists. The pin (ref) lives only in `wrapper_resolver.py`.

5. **Agent interface — the committed wrapper is the universal entry; subagents never load task-tree.**
   - **Universal call form lives in `using-superra §Task Interface`** (the only skill every agent — including implementer/reviewer subagents — preloads). Update it so the canonical read/edit invocation is the committed `<task-root>/superra` wrapper (e.g. `superRA/superra task read <path>`), which self-resolves and needs no skill load, no plugin path, and no PATH install. Subagents do **not** load `task-tree`; tree-level tooling stays load-on-demand for orchestrators/planners only. Do not duplicate the call form into role specs — point to the universal interface.
   - **The wrapper must exist before any subagent is dispatched.** `superplan` creates `<task-root>/superra` at tree-creation time (via the bootstrap form below) and commits it with the tree, so every downstream agent finds a working `superRA/superra`.
   - **Bootstrap form is planner/main-only.** The first call in a fresh project — which creates the wrapper — uses the loaded task-tree skill directory: `uv run --script <task-tree skill-dir>/scripts/cli.py wrapper init`, following the `<skill-dir>` substitution convention already used by sibling skills. Documented in `task-tree/SKILL.md` and wired into `superplan`'s tree-creation step. After the wrapper exists, everything uses `<task-root>/superra`.

6. **Wrapper / hook generation.** `superra wrapper init` and `superra wrapper render-hook` stay; regenerate the committed `<task-root>/superra` and `hooks/task-hook` to the new run-line (uv run --script + python3 fallback). Keep the byte-identity regression test between the committed `hooks/task-hook` and the generator. The hook's existing `uvx → python3` fallback becomes `uv run --script → python3`.

7. **Docs.** Rewrite `task-tree/references/internals.md §Setup` and the `SKILL.md` invocation/dashboard rows to the `uv run --script` model: the committed wrapper is the canonical agent/end-user form, the skill-dir `uv run --script` form is the documented bootstrap, no package/console-entry/`uv tool install` framing. Add the bootstrap to `superplan`. (The `--root superRA` redundancy cleanup already landed and stays.)

8. **Tests.** Update `scripts/test_cli.py`: replace `uvx`-build assertions with `uv run --script` resolution/run-line assertions; assert no caller `.venv` is created when run from a project carrying a conflicting `.venv`; assert the `python3` fallback runs the core; assert the GitHub branch emits a clone-then-script form; keep the wrapper/hook byte-identity and idempotency tests.

### Constraints

- **Subagents (implementer/reviewer) load only `using-superra` and `report-in-markdown`, never `task-tree`.** Any CLI knowledge an executing agent needs to read or edit its task must live in `using-superra §Task Interface` and resolve through the committed wrapper — not through the task-tree skill, a skill-dir form, or a PATH `superra`.
- **No hardcoded plugin/cache/version paths in any committed artifact.** The wrapper and hook resolve at runtime from their own on-disk location.
- **Single-source the resolution chain and run-line in `wrapper_resolver.py`.** Duplicated resolver/run logic between the wrapper and the hook is the primary drift risk.

### Validation

- From a non-checkout project that already has a conflicting `.venv`: `superRA/superra task tree` runs and creates **no** `.venv` in the project.
- Editing a resolved source script is reflected on the next wrapper call with no `--refresh` / cache-bust (proves no version-keyed staleness).
- `python3 <dir>/scripts/cli.py task tree` runs the core with no third-party deps installed (proves the fallback and stdlib-only core).
- `superRA/superra dashboard` launches via `uv run --script plan_dashboard.py` and renders templates/vendor from `__file__`-relative paths.
- Resolver picks env var → checkout → Claude manifest → Codex glob → GitHub clone, in order; speed gate holds (no full-disk walk).
- GitHub branch shallow-clones and runs `uv run --script <clone>/…/cli.py` when no local source exists.
- A simulated subagent with only `using-superra` loaded can read its task via `superRA/superra task read <path>`; no active doc tells a subagent to load `task-tree` to read a task.
- After `superplan` creates a tree, `<task-root>/superra` is present, executable, and committed.
- `skills/task-tree/pyproject.toml` is removed and nothing in `skills`/`hooks`/`README.md` references it or `uv tool install` as the normal path.
- `superra wrapper init` writes an executable, resolver-carrying wrapper; re-run is byte-identical; committed `hooks/task-hook` is byte-identical to the generator.

## Planner Guidance

**What already exists and stays** (from the prior `uvx`-based implementation, commits `5de74de9..76473463`): `scripts/wrapper_resolver.py` as the single-source generator rendering both shell artifacts; the bounded resolution chain and its priority order; the `superra wrapper init` / `render-hook` subcommands; the byte-identity regression test; the `--root` auto-detect doc cleanup; `cli.py`'s flat-import fallback (`sys.path.insert` + package-or-flat `importlib`). Reuse all of it.

**What changes:** the terminal exec form (`uvx --from <dir> superra` → `uv run --script <dir>/scripts/<entry>` + `python3` fallback, routed by subcommand); the cache-branch existence test (`pyproject.toml` → `scripts/cli.py`); deletion of `pyproject.toml` and package framing; the GitHub branch (uvx-git → shallow-clone + script); PEP 723 blocks added to `cli.py` and `task_hook.py` (`plan_dashboard.py` already has one); and the agent-interface + bootstrap docs (items 5, 7).

Keep the resolver and run-line single-sourced in `wrapper_resolver.py` — render both the wrapper and the hook from it, embedded (not sourced), since the wrapper lives where it cannot source from the plugin before resolving it.

Generated role/Codex artifacts are out of scope unless a change touches canonical agent specs. Item 5 edits `using-superra §Task Interface` (a skill, not an agent spec) and `superplan` — these are not generated. If any edit reaches `agents/implementer.md` or `agents/reviewer.md`, regenerate via `skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` rather than hand-editing.

## Results

Reworked the task-tree CLI to a single, install-free execution model: resolve the source dir from disk, then run the relevant loose entry script with `uv run --script <file>` (falling back to `python3 <file>`). There is no installable package and no `pyproject.toml` — PEP 723 inline-metadata blocks in each entry script are the single dependency source of truth. The agent-facing entry is the committed self-resolving `superRA/superra` wrapper; subagents read/edit tasks through it without loading `task-tree`.

### Execution model and entry scripts

- **`scripts/cli.py`** ([../../../../skills/task-tree/scripts/cli.py:1-14](../../../../skills/task-tree/scripts/cli.py#L1-L14)) carries a PEP 723 block with deps `["pyyaml"]` (core is stdlib; pyyaml is the lazy comment-parser import in `_comments.py`).
- **`scripts/task_hook.py`** ([../../../../skills/task-tree/scripts/task_hook.py:1-7](../../../../skills/task-tree/scripts/task_hook.py#L1-L7)) carries a stdlib-only block (`dependencies = []`).
- **`scripts/plan_dashboard.py`** already carried the full web-stack block and was already loose-script-ready (flat sibling imports, `__file__`-relative `FileSystemLoader`/`_resource_dir` for templates and vendor when `__package__ is None`). It now accepts the user-facing `dashboard …` surface ([../../../../skills/task-tree/scripts/plan_dashboard.py:2108-2122](../../../../skills/task-tree/scripts/plan_dashboard.py#L2108-L2122)): a leading `dashboard` token delegates to `cli.py`'s dashboard handler so the surface translation (`export`→`generate`, default→`serve`, `stop`, `artifact`) keeps its single home in `cli.py`, while the web stack stays off `cli.py`'s PEP 723 block.

### Resolver and run-line (single-sourced in `wrapper_resolver.py`)

[../../../../skills/task-tree/scripts/wrapper_resolver.py](../../../../skills/task-tree/scripts/wrapper_resolver.py) renders both committed shell artifacts from one bash resolver string. Changes vs. the prior `uvx` design:

- **Cache-branch existence test** is now `scripts/cli.py` (the package's `pyproject.toml` no longer exists).
- **Terminal exec** is `_superra_run_entry`: `uv run --script <dir>/scripts/<entry>` with a `python3 <file>` fallback, routed by first argument — `dashboard` → `plan_dashboard.py`; the hook → `task_hook.py`; everything else → `cli.py`.
- **GitHub fallback** is now a shallow clone: `_superra_resolve_source` emits `GIT:<repo>@<ref>`, and `_superra_github_clone` clones (or TTL-gated fetch-resets an existing clone) to `${XDG_CACHE_HOME:-~/.cache}/superra/superRA-<ref>`, then runs the loose `cli.py` from inside the clone (since `uv run --script` cannot fetch a git subdirectory). Fires only when env var, checkout, and installed caches all miss. **Revise round:** the GIT branch is gated by `GITHUB_REF_HAS_SUBDIR` (`"0"` today) — while the pinned `main` does not yet carry `skills/task-tree`, the branch fails fast (no clone) instead of cloning the whole repo only to fail the `cli.py` test; flip the flag to `"1"` once the pin carries the subdir. The refresh `git fetch` is gated behind a `GITHUB_FETCH_TTL_SECONDS` (24 h) stamp file, so a reused clone is no longer a network round-trip on every call/hook fire. The `records[0]` arbitrary-record fallback in the Claude manifest probe was dropped (it could resolve to another project's install path).
- The bounded resolution chain (env var → checkout → Claude manifest → Codex depth-3 glob → GitHub) and the speed gate are preserved. Speed-gate cost per branch is O(1) but not literally "one file test": each branch probes the canonical `task-tree` plus the legacy `task-system` alias (up to two file tests), the Claude branch runs a python3 heredoc for the manifest read, and the Codex branch runs one fixed-depth glob — the first match short-circuits, so a resolved local checkout never reaches the manifest read or glob. No full-disk walk. The pin (ref `main`) lives only in `wrapper_resolver.py`.

The committed `superRA/superra` ([../../../../superRA/superra](../../../superra)) and `hooks/task-hook` ([../../../../hooks/task-hook](../../../../hooks/task-hook)) were regenerated to this run-line and are byte-identical to the generator. **Both** are now pinned by byte-identity tests (`test_committed_hook_shim_matches_generator` and the new `test_committed_wrapper_matches_generator`), so a resolver-chain edit that skips regeneration fails CI.

### Dashboard import-error handling (revise round)

`uv run --script cli.py dashboard …` runs script-scoped under `cli.py`'s PEP 723 block, which omits the web stack, so importing `plan_dashboard` (FastAPI at module top) raised a raw `ModuleNotFoundError`. [`_run_dashboard`](../../../../skills/task-tree/scripts/cli.py#L135) now catches that `ImportError` and prints an actionable message — naming the missing module and pointing at the `superra` wrapper or the direct `plan_dashboard.py` entry — then exits 1, instead of leaking a traceback. Pinned by `test_dashboard_missing_web_stack_reports_friendly_error`.

### Package framing dropped

Removed `skills/task-tree/pyproject.toml` and `scripts/__init__.py` (the version-stub package namespace). The dashboard's `if __package__` branches stay as harmless fallbacks; only the loose-script (`__package__ is None`) path is exercised. The `.gitignore` ([../../../../skills/task-tree/.gitignore](../../../../skills/task-tree/.gitignore)) was rewritten from package-build outputs to incidental uv/Python artifacts. This supersedes the `uv-package` sibling's build-manifest deliverable.

### Agent interface and bootstrap

- `using-superra §Task Interface` ([../../../../skills/using-superra/SKILL.md:45](../../../../skills/using-superra/SKILL.md#L45)) now names the committed `./superRA/superra task read <path>` wrapper as the canonical read/edit form for every agent (main/implementer/reviewer), explicitly noting it needs no skill load, plugin path, or PATH install — verified by reading this very task through the wrapper with only that interface.
- `superplan §Creating Tasks` ([../../../../skills/superplan/SKILL.md:99-117](../../../../skills/superplan/SKILL.md#L99-L117)) creates the wrapper first at tree-creation time via the planner-only bootstrap `uv run --script <skill-dir>/scripts/cli.py wrapper init`, then uses `./superRA/superra …` for all subsequent calls, so every downstream agent finds a working wrapper.
- The bootstrap form and the `<skill-dir>` substitution convention are documented in `task-tree/SKILL.md` ([../../../../skills/task-tree/SKILL.md:43](../../../../skills/task-tree/SKILL.md#L43)) and `references/internals.md §Setup`.

### Docs

`references/internals.md` §Setup / §Hook Architecture / §Dashboard / §GitHub-Actions, `task-tree/SKILL.md`, and root `CLAUDE.md §Local Task-Tree CLI Development` were rewritten to the `uv run --script` model (no `uvx`/`uv tool install`/`uv run --project`/console-entry framing). The GitHub Actions workflow template ([../../../../skills/task-tree/scripts/templates/superra-dashboard-artifact.yml:50](../../../../skills/task-tree/scripts/templates/superra-dashboard-artifact.yml#L50)) and its two render tests now use `uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard export`.

### Verification (empirical, not code-reading)

- **No caller venv (root-cause fix a).** Ran `uv run --script .../cli.py task tree` from a scratch project carrying both a `pyproject.toml` and a pre-existing empty `.venv`. The CLI read the scratch tree and exited 0; the `.venv` stayed empty and no `pyvenv.cfg`/dist-info appeared anywhere in the project. Pinned by `test_uv_run_script_creates_no_caller_venv_with_conflicting_project` ([../../../../skills/task-tree/scripts/test_cli.py](../../../../skills/task-tree/scripts/test_cli.py)).
- **Live source, no cache-bust (root-cause fix b).** Injected a unique marker into `cli.py`'s parser help and re-ran `uv run --script cli.py --help` with no `--refresh`/`--no-cache`/version bump — the marker appeared on the very next run, proving no version-keyed build cache sits between source and execution.
- **python3 fallback / stdlib-only core.** `python3 cli.py task tree` ran the core successfully under a system `python3` that has no `pyyaml` installed, proving the lazy import and the uv-free fallback. Pinned by `test_python3_fallback_runs_core_without_third_party_deps`.
- **Dashboard route.** `./superRA/superra dashboard export` and `uv run --script plan_dashboard.py dashboard export` both rendered a standalone HTML (markdown-it + `window.STANDALONE = true`) with templates/vendor loaded from `__file__`-relative paths. Pinned by `test_uv_run_script_exports_dashboard_from_file_relative_assets`.
- **Resolver order + GitHub fail-fast/clone.** Bash probes of the rendered resolver confirm env var → `DIR:`, Claude-manifest-over-codex, codex highest-semver within depth bound, and skip-cache-lacking-`cli.py`. **Revise round:** with `GITHUB_REF_HAS_SUBDIR="0"`, an empty environment now makes `_superra_resolve_source` return non-zero with no output (fail fast, no clone) — pinned by `test_resolver_fails_fast_when_no_source_and_pin_lacks_subdir`. With the flag forced to `"1"`, it emits `GIT:…@main` (`test_resolver_emits_github_spec_when_pin_carries_subdir`) and the GitHub branch, driven against a local bare remote (no network), shallow-clones to the user cache and resolves to `<clone>/skills/task-tree` (`test_resolver_github_branch_clones_then_resolves_loose_script`).
- **Subagent read.** Read this task through `./superRA/superra task read …` with only the `using-superra` interface — no `task-tree` load.
- **Byte-identity.** Regenerated `superRA/superra` and `hooks/task-hook`; both diff-clean against the generator. `test_committed_hook_shim_matches_generator`, `test_committed_wrapper_matches_generator`, and `test_generated_wrapper_and_hook_are_valid_bash` pass.

### Version-robust autodetect (lazy-iterdir guard)

The documented fresh-project bootstrap (`uv run --script <skill-dir>/scripts/cli.py wrapper init`, no `--root`) routes the first call through `autodetect_plan_root`, which probes non-existent `<current>/superRA` candidates via [`_has_child_task_dir`](../../../../skills/task-tree/scripts/_task_io.py#L30). `Path.iterdir()` is lazy, so on Python ≤3.12 the `FileNotFoundError` fired on consumption inside the `any(...)` generator, escaping the `try/except OSError` and crashing the bootstrap with `rc=1` (3.13/3.14 mask it via changed `iterdir()` error timing). Fixed by materializing the listing inside the guard — `children = list(directory.iterdir())` — in `_has_child_task_dir` and the same-shaped sibling helper [`_is_task_root`](../../../../skills/task-tree/scripts/_worktree_discovery.py#L154). Verified: all 30 `test_cli.py` tests pass under 3.12, and the bare bootstrap returns `rc=0` in a fresh `mktemp -d` under uv's default `--script` interpreter selection.

**Test suite:** full task-tree suite green from live source — `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts` → **631 passed, 2 skipped** (was 596 before the revise-round additions across this dispatch).
