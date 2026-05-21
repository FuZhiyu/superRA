# research-project-setup CLI test suite

Headless end-to-end tests for the `research-project-setup` skill exercised
through both Claude Code (`claude -p`) and Codex CLI (`codex exec`). Covers
four scenarios — sandbox write, fresh-setup scaffold, retrofit, trigger
discovery — across both CLIs, for up to 8 test rows total.

## Run

```bash
bash skills/research-project-setup/tests/run_tests.sh                 # all 8 rows
bash skills/research-project-setup/tests/run_tests.sh --only claude   # 4 Claude rows
bash skills/research-project-setup/tests/run_tests.sh --only codex    # 4 Codex rows
bash skills/research-project-setup/tests/run_tests.sh --case A        # one scenario × both CLIs
bash skills/research-project-setup/tests/run_tests.sh --only claude --case C --keep --verbose
```

Flags:
- `--only claude|codex` — restrict to one CLI.
- `--case A|B|C|D` — run a single scenario.
- `--keep` — leave the `$HOME/rps-tests/*` artifacts on disk for inspection
  (also via `KEEP_ARTIFACTS=1`).
- `--verbose` — echo every CLI invocation.

Env overrides:
- `CLAUDE_MODEL` (default `claude-haiku-4-5-20251001`).
- `CODEX_MODEL` (default `gpt-5.4-mini`). The PLAN.md spec mentioned
  `gpt-5-mini`; on a ChatGPT-account Codex install that alias is not
  exposed (the API rejects it with "model is not supported"). The
  cheapest model exposed via `codex doctor` / `~/.codex/models_cache.json`
  on this install is `gpt-5.4-mini`.
- `AGENT_TIMEOUT` (seconds, default 300) — kill timer per agent
  invocation.

## Test matrix

All scratch dirs are created under `$HOME/rps-tests/` — that subtree sits
outside the template's default writable_roots (`/tmp`, `/private/tmp`,
`/var/folders`, `~/.venvs`, `~/.cache`, `~/.local/share/uv` — see
`template/.codex/config.toml`). Putting them anywhere inside that default
set would make the codex strict-profile assertion vacuously pass whether
or not `register_share_path_with_agents` ran.

| ID | Profile | Setup | What it proves |
|---|---|---|---|
| A | strict | Project + share under `$HOME/rps-tests/A-{proj,share}-*` (both outside default writable_roots) | The `register_share_path_with_agents` helper actually grants the agent permission to write into the absolute share-folder path. Negative-control: if you `python3 -c '... additionalDirectories=[]'` the Claude settings and `sed -i "\|<share>|d"` the Codex writable_roots, this test must FAIL. |
| B | permissive | Empty CWD under `$HOME/rps-tests/B-cwd-*` | The skill is invoked by a "create a new research project" prompt and the scaffolder runs end-to-end, producing `.claude/`, `.codex/`, share symlinks, and `Notes/setup_decisions.md`. |
| C | permissive | Scaffold under `$HOME/rps-tests/C-*` without `--with-overleaf` | The retrofit playbook for Overleaf applies — `overleaf-sync/` lands at the project root, `.gitignore` carries the playbook's entries, and a new feature commit is created. |
| D | permissive | Empty CWD under `$HOME/rps-tests/D-cwd-*`, fresh agent session | A bare trigger phrase ("I want to create a new research project") surfaces the `research-project-setup` skill or `create_project.sh` in the agent's response — i.e., skill discovery works from any CWD. |

## Profiles

- **strict** — Test A only. Claude runs with `--permission-mode acceptEdits`.
  Empirically this is the ONLY headless mode that makes
  `permissions.additionalDirectories` load-bearing: `default`, `auto`, and
  `dontAsk` all record Write attempts to any out-of-workspace path as
  `permission_denials` (no human to approve in headless), regardless of the
  registered `additionalDirectories`. `acceptEdits` auto-approves writes
  INSIDE workspace + `additionalDirectories` and STILL denies writes
  OUTSIDE that set — verified against a surgically-broken project
  (denials > 0 when the registration is stripped). Codex runs with
  `-s workspace-write -c approval_policy="never"` so sandbox-policy
  violations surface as errors rather than as approval prompts.
- **permissive** — Tests B/C/D. Claude runs with
  `--permission-mode bypassPermissions`. Codex runs with
  `--dangerously-bypass-approvals-and-sandbox`. These cases test skill
  routing and retrofit logic, not the sandbox plumbing, so we lift the
  permission gate to keep the cases deterministic.

## Skill discovery

Both CLIs need to find the in-development `research-project-setup` skill
on disk for tests B/C/D.

- **Claude.** `run_claude` adds `--plugin-dir <superRA-repo-root>` on every
  invocation, so the dev copy of the skill loads regardless of what
  superRA version is installed under `~/.claude/plugins/cache/`.
- **Codex.** Codex has no per-invocation `--plugin-dir` flag, so Test D
  (only) symlinks the skill into `~/.codex/skills/research-project-setup`
  for the duration of the test and removes the symlink in its `EXIT`
  trap. Tests B and C give the agent the absolute path to
  `create_project.sh` in the prompt, so codex does not need skill
  discovery for those.

## Final agent prompts (after iteration)

Tuning the prompts to reliably trigger the right behavior across both
CLIs took a few rounds. The final phrasings live in the case scripts;
the gist:

- **Test A (sandbox).** `"Create a file at the absolute path
  <SHARE>/Notes/test.txt containing exactly the word hello (one word, no
  quotes, no trailing newline beyond what your editor adds). Use the
  absolute path I gave; do not use any relative path or symlink. Do not
  print anything else."` — using the absolute share-folder path (not
  the in-project `Notes/` symlink) forces the write target to resolve
  outside the project root.
- **Test B (fresh setup).** Hard-codes the exact `bash create_project.sh
  ...` command line because the bare "create a new research project"
  prompt was nondeterministic about which absolute paths the model would
  invent. Also explicitly names `Notes/setup_decisions.md` so the agent
  doesn't skip the decision log.
- **Test C (retrofit).** Names the skill template path explicitly
  (`$SKILL_ROOT/template/overleaf-sync`) and the commit title
  (`add: Overleaf subtree sync`) — a short open-ended "add Overleaf
  sync" prompt did not reliably copy the directory.
- **Test D (discovery).** Open-ended ("I want to create a new research
  project. Which skill or script in this installation handles that?").
  This is the discovery case — over-specifying defeats the point.

## Negative-control regression check

Test A's strict assertions are only useful if they actually fail when
`register_share_path_with_agents` doesn't run. To prove they do:

```bash
# Tighter per-invocation timeout so a denied write that retries/stalls is
# killed quickly.
export AGENT_TIMEOUT=90

# 1. Scaffold normally — both paths under $HOME/rps-tests/ so the share
#    sits outside default writable_roots.
mkdir -p "$HOME/rps-tests"
PROJ=$(mktemp -d "$HOME/rps-tests/neg-proj-XXXX")
SHARE=$(mktemp -d "$HOME/rps-tests/neg-share-XXXX")
bash skills/research-project-setup/scripts/create_project.sh "$PROJ/NegCtrl" --share-path "$SHARE"

# 2. Surgically remove the registered share path from BOTH settings files.
python3 -c "import json,sys; p=sys.argv[1]; d=json.load(open(p)); d['permissions']['additionalDirectories']=[]; json.dump(d, open(p,'w'), indent=2)" \
  "$PROJ/NegCtrl/.claude/settings.local.json"
sed -i.bak "\|\"$SHARE|d" "$PROJ/NegCtrl/.codex/config.toml"

# 3. Re-run Test A against the broken project — wrap each CLI re-run in an
#    outer 180s wall-clock guard so we never hang.
run_with_outer_timeout() {
    if command -v gtimeout >/dev/null 2>&1; then gtimeout --kill-after=10 180 "$@"
    elif command -v timeout >/dev/null 2>&1; then timeout --kill-after=10 180 "$@"
    else perl -e 'use POSIX; alarm 180; exec @ARGV' "$@"; fi
}
run_with_outer_timeout bash skills/research-project-setup/tests/cases/test_a_sandbox.sh claude
# Expect non-zero exit (FAIL). A zero exit is an UNEXPECTED PASS.
run_with_outer_timeout bash skills/research-project-setup/tests/cases/test_a_sandbox.sh codex

# 4. Guarded cleanup.
case "$PROJ"  in "$HOME/rps-tests/"*) rm -rf "$PROJ"  ;; esac
case "$SHARE" in "$HOME/rps-tests/"*) rm -rf "$SHARE" ;; esac
unset AGENT_TIMEOUT
```

See RESULTS.md Task 8 for the run that proved this.

## Debugging a flaky case

LLM responses are nondeterministic; a single FAIL is not yet a real
failure. Before declaring a regression:

```bash
# Re-run the failing row in isolation with verbose logging and keep
# artifacts on disk for inspection.
bash skills/research-project-setup/tests/run_tests.sh \
    --only claude --case C --keep --verbose
ls "$HOME/rps-tests/C-"*
```

If two runs in a row both fail with the same assertion, the regression
is real. Investigate the case script + agent prompt, not the harness.

## Directory layout

```
tests/
  README.md            this file
  run_tests.sh         runner — flags + matrix loop
  lib/common.sh        shared helpers (scaffold/cleanup/run/assert)
  cases/
    test_a_sandbox.sh
    test_b_fresh.sh
    test_c_retrofit.sh
    test_d_discovery.sh
```
