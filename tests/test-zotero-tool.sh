#!/usr/bin/env bash
# Credential-free behavior checks for the zotero-paper-reader tool script.
# Exercises CLI parsing, version reporting, access-mode detection, clean error
# paths, and the no-secret-leak invariant without contacting a real library.
# Run from the repo root: bash tests/test-zotero-tool.sh

set -euo pipefail

cd "$(dirname "$0")/.."

SCRIPT="skills/zotero-paper-reader/scripts/zotero_tool.py"
SCRIPT_ABS="$(pwd)/$SCRIPT"
RUN=(uv run --quiet --script "$SCRIPT")

pass=0
fail=0
failed_names=()

record_pass() {
  printf 'PASS  %s\n' "$1"
  pass=$((pass + 1))
}

record_fail() {
  printf 'FAIL  %s\n' "$1"
  fail=$((fail + 1))
  failed_names+=("$1")
}

# Run the tool, capturing stdout, stderr, and exit code into globals.
run_tool() {
  TOOL_OUT="$("${RUN[@]}" "$@" 2>/tmp/zt_test_err)" && TOOL_RC=0 || TOOL_RC=$?
  TOOL_ERR="$(cat /tmp/zt_test_err)"
}

assert_rc() {
  local name="$1" want="$2"
  if [ "$TOOL_RC" = "$want" ]; then
    record_pass "$name"
  else
    printf '      want rc=%s got rc=%s\n' "$want" "$TOOL_RC"
    record_fail "$name"
  fi
}

assert_stdout_contains() {
  local name="$1" pattern="$2"
  if printf '%s' "$TOOL_OUT" | rg -q --fixed-strings -- "$pattern"; then
    record_pass "$name"
  else
    printf '      stdout missing: %s\n' "$pattern"
    record_fail "$name"
  fi
}

assert_combined_absent() {
  local name="$1" pattern="$2"
  if printf '%s%s' "$TOOL_OUT" "$TOOL_ERR" | rg -q --fixed-strings -- "$pattern"; then
    printf '      leaked pattern present: %s\n' "$pattern"
    record_fail "$name"
  else
    record_pass "$name"
  fi
}

# 1. Help works and lists every required subcommand.
run_tool --help
assert_rc "help exits 0" 0
for cmd in health libraries search item children collections tags fulltext doiindex pdf bibtex cite bibliography; do
  assert_stdout_contains "help lists '$cmd'" "$cmd"
done

# 2. Health reports the pinned pyzotero version and structured mode info.
#    The exit code depends on the real environment: 0 when a local Zotero API
#    is actually running on this machine, 1 when no access mode is available.
#    Branch so the check is deterministic either way.
unset ZOTERO_LIBRARY_ID ZOTERO_API_KEY ZOTERO_LIBRARY_TYPE
run_tool health
assert_stdout_contains "health reports pyzotero version" '"pyzotero_version": "1.13.0"'
assert_stdout_contains "health reports active_mode field" '"active_mode"'
assert_stdout_contains "health reports better_bibtex_available" '"better_bibtex_available"'
if printf '%s' "$TOOL_OUT" | rg -q --fixed-strings '"local_api_available": true'; then
  assert_rc "health exits 0 when local API is available" 0
else
  assert_rc "health exits non-zero with no access mode" 1
fi

# 3. Clean error (not a stack trace) when no mode is available. Force --mode web
#    with no credentials so the no-access path is deterministic even when a local
#    Zotero API is running on the test machine.
run_tool search "anything" --mode web
assert_rc "web search without creds exits 1" 1
[ -n "$TOOL_ERR" ] && grep -q '^error:' <<<"$TOOL_ERR" \
  && record_pass "search emits a clean 'error:' line" \
  || record_fail "search emits a clean 'error:' line"

# 4. Full-text search reaches the same access-mode resolution as plain search
#    (it is NOT web-only — the local API serves qmode=everything, verified live
#    in task 05). With --mode web and no credentials it errors naming the Web
#    API requirement. The local full-text path needs a live library and is
#    covered by task 05's smoke test, not this credential-free suite.
run_tool search "anything" --fulltext --mode web
assert_rc "web fulltext without creds exits 1" 1
grep -q 'Web API' <<<"$TOOL_ERR" \
  && record_pass "web fulltext error names Web API requirement" \
  || record_fail "web fulltext error names Web API requirement"

# 4b. An invalid --library spec is rejected deterministically (parse_library
#     raises before any access attempt — no local API or credentials needed).
run_tool search "anything" --library notanid
assert_rc "invalid --library exits 1" 1
grep -q 'invalid --library' <<<"$TOOL_ERR" \
  && record_pass "invalid --library names the problem" \
  || record_fail "invalid --library names the problem"

# 5. No-secret-leak invariant: a forced web call with fake creds must error
#    without echoing the API key anywhere in stdout or stderr.
SECRET="ZT_TEST_SECRET_DO_NOT_LEAK"
ZOTERO_LIBRARY_ID=99999 ZOTERO_API_KEY="$SECRET" ZOTERO_LIBRARY_TYPE=user \
  run_tool search "anything" --mode web
assert_combined_absent "API key never appears in output" "$SECRET"

# 6. Notes/.env parsing: with env vars unset, load_env_file must pick up a
#    project-local Notes/.env (resolved from cwd). Uses fake non-secret values;
#    the .env-sourced key must still never leak.
ENV_TMP="$(mktemp -d)"
mkdir -p "$ENV_TMP/Notes"
DOTENV_SECRET="ZT_DOTENV_SECRET_DO_NOT_LEAK"
cat >"$ENV_TMP/Notes/.env" <<EOF
ZOTERO_LIBRARY_ID=4242424
ZOTERO_API_KEY=$DOTENV_SECRET
ZOTERO_LIBRARY_TYPE=user
EOF
DOTENV_OUT="$(cd "$ENV_TMP" && uv run --quiet --script "$SCRIPT_ABS" health 2>/tmp/zt_dotenv_err)" || true
DOTENV_ERR="$(cat /tmp/zt_dotenv_err)"
printf '%s' "$DOTENV_OUT" | rg -q --fixed-strings -- '"ZOTERO_LIBRARY_ID": true' \
  && record_pass "Notes/.env library_id is read" \
  || record_fail "Notes/.env library_id is read"
printf '%s' "$DOTENV_OUT" | rg -q --fixed-strings -- '"ZOTERO_API_KEY": true' \
  && record_pass "Notes/.env api_key is read" \
  || record_fail "Notes/.env api_key is read"
if printf '%s%s' "$DOTENV_OUT" "$DOTENV_ERR" | rg -q --fixed-strings -- "$DOTENV_SECRET"; then
  record_fail ".env API key never appears in output"
else
  record_pass ".env API key never appears in output"
fi
rm -rf "$ENV_TMP"

# 7. bibtex selection guard: with no --item-key/--query/--doi it errors cleanly
#    before any library access (deterministic regardless of access mode).
run_tool bibtex
assert_rc "bibtex without a selection exits 1" 1
grep -q '^error:' <<<"$TOOL_ERR" \
  && grep -q -- '--item-key' <<<"$TOOL_ERR" \
  && record_pass "bibtex names the missing selection flags" \
  || record_fail "bibtex names the missing selection flags"

# 7b. bibtex rejects an invalid --library before any access (parse_library).
run_tool bibtex --item-key ABCD1234 --library notanid
assert_rc "bibtex invalid --library exits 1" 1
grep -q 'invalid --library' <<<"$TOOL_ERR" \
  && record_pass "bibtex invalid --library names the problem" \
  || record_fail "bibtex invalid --library names the problem"

# 8. Unit-test the reusable bib-sync helpers (dedup-append, minimal touch) by
#    importing the module — no Zotero/BBT/library access. These helpers back the
#    --bib master sync and are reused by the citation features in sibling tasks.
SYNC_TMP="$(mktemp -d)"
SYNC_OUT="$(BIBDIR="$SYNC_TMP" uv run --quiet --with pyzotero==1.13.0 python - "$SCRIPT_ABS" <<'PY' 2>/tmp/zt_sync_err
import importlib.util, os, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("zt", sys.argv[1])
zt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(zt)
bib = Path(os.environ["BIBDIR"]) / "master.bib"
entry = "@article{smith2020key,\n  title = {A Title},\n  author = {Smith, J.},\n}\n"
added, skipped = zt.sync_bib(bib, entry)
assert added == ["smith2020key"] and skipped == [], (added, skipped)
# Idempotence: a second identical sync adds nothing.
added2, skipped2 = zt.sync_bib(bib, entry)
assert added2 == [] and skipped2 == ["smith2020key"], (added2, skipped2)
# Existing entries untouched: exactly one @article block.
text = bib.read_text()
assert text.count("@article{") == 1, text
# A new key appends; the old one stays skipped (minimal touch, order preserved).
two = entry + "\n@book{jones2019other,\n  title = {Other},\n}\n"
added3, skipped3 = zt.sync_bib(bib, two)
assert added3 == ["jones2019other"] and skipped3 == ["smith2020key"], (added3, skipped3)
keys = zt.bib_entry_keys(bib.read_text())
assert keys == ["smith2020key", "jones2019other"], keys
print("SYNC_OK")
PY
)"
if printf '%s' "$SYNC_OUT" | rg -q --fixed-strings 'SYNC_OK'; then
  record_pass "sync_bib dedup-appends and preserves existing entries"
else
  printf '      sync helper failed: %s\n' "$(cat /tmp/zt_sync_err)"
  record_fail "sync_bib dedup-appends and preserves existing entries"
fi
rm -rf "$SYNC_TMP" /tmp/zt_sync_err

# 9. cite selection / target guards (deterministic — argparse and the guard run
#    before any library access).
run_tool cite --bib /tmp/zt_cite_guard.bib
assert_rc "cite without a selection exits 1" 1
grep -q '^error:' <<<"$TOOL_ERR" \
  && grep -q -- '--item-key' <<<"$TOOL_ERR" \
  && record_pass "cite names the missing selection flags" \
  || record_fail "cite names the missing selection flags"

# Neither/both of --tex / --markdown is an error (the guard fires before access).
run_tool cite --item-key ABCD1234 --bib /tmp/zt_cite_guard.bib
assert_rc "cite without a target exits 1" 1
grep -q 'exactly one' <<<"$TOOL_ERR" \
  && record_pass "cite requires exactly one target (none given)" \
  || record_fail "cite requires exactly one target (none given)"

run_tool cite --item-key ABCD1234 --tex /tmp/a.tex --markdown /tmp/a.md --bib /tmp/zt_cite_guard.bib
assert_rc "cite with both targets exits 1" 1
grep -q 'exactly one' <<<"$TOOL_ERR" \
  && record_pass "cite requires exactly one target (both given)" \
  || record_fail "cite requires exactly one target (both given)"

# bibliography selection guard.
run_tool bibliography
assert_rc "bibliography without a selection exits 1" 1
grep -q -- '--item-key' <<<"$TOOL_ERR" \
  && record_pass "bibliography names the missing selection flags" \
  || record_fail "bibliography names the missing selection flags"

# 10. Unit-test the citation-insertion + hardened entry-detection helpers by
#     importing the module — no Zotero/BBT/library access. Covers \cite/[@key]
#     insertion, marker replace-in-place, missing-marker error, and the
#     hardened split_bib_entries (a "@type{...}" token inside a field value must
#     NOT become a phantom entry — the helper backing every reused .bib write).
UNIT_TMP="$(mktemp -d)"
UNIT_OUT="$(WORKDIR="$UNIT_TMP" uv run --quiet --with pyzotero==1.13.0 python - "$SCRIPT_ABS" <<'PY' 2>/tmp/zt_unit_err
import importlib.util, os, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("zt", sys.argv[1])
zt = importlib.util.module_from_spec(spec); spec.loader.exec_module(zt)
work = Path(os.environ["WORKDIR"])

# Hardened entry detection: an @type{...,} token inside a field value is part of
# the enclosing entry, not a phantom entry. The real entry is captured intact.
phantom = (
    "@article{real2020key,\n"
    "  title = {A Real Paper},\n"
    "  abstract = {We compare to @inproceedings{notakey, a prior approach}.},\n"
    "}\n"
)
assert zt.bib_entry_keys(phantom) == ["real2020key"], zt.bib_entry_keys(phantom)
ents = zt.split_bib_entries(phantom)
assert len(ents) == 1 and "notakey" in ents[0][1] and "abstract" in ents[0][1], ents

# Nested braces in a title are balanced into one entry; two real entries split.
two = (
    "@article{a2020,\n  title = {Nested {Brace} Title},\n}\n\n"
    "@book{b2019,\n  title = {Other},\n}\n"
)
assert zt.bib_entry_keys(two) == ["a2020", "b2019"], zt.bib_entry_keys(two)

# sync_bib over the phantom case adds exactly the one real key (no bogus key).
added, skipped = zt.sync_bib(work / "p.bib", phantom)
assert added == ["real2020key"] and skipped == [], (added, skipped)

# insert_citation: append.
tex = work / "draft.tex"
tex.write_text("Intro.\n")
zt.insert_citation(tex, "\\cite{k1}", None)
assert "\\cite{k1}" in tex.read_text(), tex.read_text()

# insert_citation: marker replace-in-place (marker gone, citation present once).
texm = work / "marker.tex"
texm.write_text("See CITEHERE for details.\n")
zt.insert_citation(texm, "\\cite{k2}", "CITEHERE")
out = texm.read_text()
assert "CITEHERE" not in out and out.count("\\cite{k2}") == 1, out

# insert_citation: missing marker errors and leaves the draft unchanged.
texn = work / "nomarker.tex"
texn.write_text("No marker.\n")
try:
    zt.insert_citation(texn, "\\cite{k3}", "NOPE")
    raise SystemExit("missing marker did not raise")
except RuntimeError:
    pass
assert texn.read_text() == "No marker.\n", texn.read_text()

# check_draft_target validates without mutating: a missing draft and a missing
# marker both raise, and it never writes. This is what lets cmd_cite reject a
# bad target BEFORE syncing the master .bib (so a typo cannot pollute it).
absent = work / "does_not_exist.tex"
try:
    zt.check_draft_target(absent, None)
    raise SystemExit("missing draft did not raise")
except RuntimeError:
    pass
assert not absent.exists(), "check_draft_target created the draft"
texc = work / "checkmarker.tex"
texc.write_text("No marker here.\n")
try:
    zt.check_draft_target(texc, "NOPE")
    raise SystemExit("missing marker did not raise in check_draft_target")
except RuntimeError:
    pass
assert texc.read_text() == "No marker here.\n", texc.read_text()
zt.check_draft_target(texc, None)  # existing draft, no marker -> ok, no write
assert texc.read_text() == "No marker here.\n", texc.read_text()

print("UNIT_OK")
PY
)"
if printf '%s' "$UNIT_OUT" | rg -q --fixed-strings 'UNIT_OK'; then
  record_pass "cite/insert + hardened entry-detection helpers behave"
else
  printf '      unit helper failed: %s\n' "$(cat /tmp/zt_unit_err)"
  record_fail "cite/insert + hardened entry-detection helpers behave"
fi
rm -rf "$UNIT_TMP" /tmp/zt_unit_err /tmp/zt_cite_guard.bib

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi
exit 0
