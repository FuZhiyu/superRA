#!/usr/bin/env bash
# Credential-free behavior checks for the zotero-paper-reader tool script.
# Exercises parser and JSON contracts, typed failure identities, state-preserving
# guards, and the no-secret-leak invariant without contacting a real library.
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

assert_combined_absent() {
  local name="$1" pattern="$2"
  if printf '%s%s' "$TOOL_OUT" "$TOOL_ERR" | rg -q --fixed-strings -- "$pattern"; then
    printf '      leaked pattern present: %s\n' "$pattern"
    record_fail "$name"
  else
    record_pass "$name"
  fi
}

assert_error_identity() {
  local name="$1" want_code="$2" want_type="$3"
  if ERROR_JSON="$TOOL_ERR" WANT_CODE="$want_code" WANT_TYPE="$want_type" \
    python3 - <<'PY'
import json
import os

payload = json.loads(os.environ["ERROR_JSON"])
error = payload["error"]
assert set(error) == {"code", "type", "message"}, error
assert error["code"] == os.environ["WANT_CODE"], error
assert error["type"] == os.environ["WANT_TYPE"], error
assert isinstance(error["message"], str) and error["message"], error
PY
  then
    record_pass "$name"
  else
    record_fail "$name"
  fi
}

# 1. Parser command inventory and health JSON-field inventory are exact
#    structural contracts. Exercise the handler directly with deterministic
#    probes so no live Zotero state affects the JSON assertions.
STRUCT_OUT="$(uv run --quiet --with pyzotero==1.13.0 python - "$SCRIPT_ABS" <<'PY' 2>/tmp/zt_struct_err
import argparse
import contextlib
import importlib.util
import io
import json
import sys

spec = importlib.util.spec_from_file_location("zt", sys.argv[1])
zt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(zt)

parser = zt.build_parser()
subparsers = [
    action for action in parser._actions
    if isinstance(action, argparse._SubParsersAction)
]
assert len(subparsers) == 1, subparsers
assert set(subparsers[0].choices) == {
    "health", "libraries", "search", "item", "children", "collections",
    "tags", "fulltext", "doiindex", "pdf", "bibtex", "cite",
    "bibliography",
}, subparsers[0].choices

zt.local_api_available = lambda: False
zt.bbt_available = lambda: False
zt.pyzotero_version = lambda: "1.13.0"
zt.get_config = lambda: {
    "library_id": None, "library_type": "user", "api_key": None
}
buf = io.StringIO()
err = io.StringIO()
with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
    rc = zt.cmd_health(argparse.Namespace())
payload = json.loads(buf.getvalue())
assert rc == 1, rc
assert set(payload) == {
    "pyzotero_version", "local_api_available", "better_bibtex_available",
    "web_api_configured", "library_type", "active_mode", "config_present",
}, payload
assert set(payload["config_present"]) == {
    "ZOTERO_LIBRARY_ID", "ZOTERO_API_KEY"
}, payload
assert payload["pyzotero_version"] == "1.13.0", payload
assert payload["local_api_available"] is False, payload
assert payload["better_bibtex_available"] is False, payload
assert payload["web_api_configured"] is False, payload
assert payload["active_mode"] is None, payload
error = json.loads(err.getvalue())["error"]
assert error["code"] == "access_unavailable", error
assert error["type"] == "AccessUnavailableError", error
print("STRUCT_OK")
PY
)" || true
if [ "$STRUCT_OUT" = "STRUCT_OK" ]; then
  record_pass "parser commands and health JSON fields match inventories"
else
  printf '      structural contract failed: %s\n' "$(cat /tmp/zt_struct_err)"
  record_fail "parser commands and health JSON fields match inventories"
fi
rm -f /tmp/zt_struct_err

# 2. Health returns JSON and an exit code consistent with active_mode. The live
#    environment is intentionally allowed to provide or omit the local API.
unset ZOTERO_LIBRARY_ID ZOTERO_API_KEY ZOTERO_LIBRARY_TYPE
run_tool health
HEALTH_MODE="$(HEALTH_JSON="$TOOL_OUT" python3 - <<'PY'
import json
import os

payload = json.loads(os.environ["HEALTH_JSON"])
assert payload["pyzotero_version"] == "1.13.0", payload
assert isinstance(payload["better_bibtex_available"], bool), payload
assert payload["active_mode"] in (None, "local", "web"), payload
print(payload["active_mode"] or "none")
PY
)"
if [ "$HEALTH_MODE" != "none" ]; then
  assert_rc "health exits 0 when local API is available" 0
else
  assert_rc "health exits non-zero with no access mode" 1
fi

# 3. Forced Web mode without credentials has a stable typed identity independent
#    of the diagnostic message.
run_tool search "anything" --mode web
assert_rc "web search without creds exits 1" 1
assert_error_identity \
  "web search without creds is typed" \
  "access_unavailable" "AccessUnavailableError"

# 4. Full-text search reaches the same access-mode resolution as plain search
#    (it is NOT web-only — the local API serves qmode=everything, verified live
#    in task 05). The local full-text path needs a live library and is covered by
#    task 05's smoke test, not this credential-free suite.
run_tool search "anything" --fulltext --mode web
assert_rc "web fulltext without creds exits 1" 1
assert_error_identity \
  "web fulltext without creds is typed" \
  "access_unavailable" "AccessUnavailableError"

# 4b. An invalid --library spec is rejected deterministically (parse_library
#     raises a typed error before any access attempt).
run_tool search "anything" --library notanid
assert_rc "invalid --library exits 1" 1
assert_error_identity \
  "invalid --library is typed" \
  "invalid_library" "InvalidLibraryError"

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
if DOTENV_JSON="$DOTENV_OUT" python3 - <<'PY'
import json
import os

present = json.loads(os.environ["DOTENV_JSON"])["config_present"]
assert present == {"ZOTERO_LIBRARY_ID": True, "ZOTERO_API_KEY": True}, present
PY
then
  record_pass "Notes/.env presence fields are true"
else
  record_fail "Notes/.env presence fields are true"
fi
if printf '%s%s' "$DOTENV_OUT" "$DOTENV_ERR" | rg -q --fixed-strings -- "$DOTENV_SECRET"; then
  record_fail ".env API key never appears in output"
else
  record_pass ".env API key never appears in output"
fi
rm -rf "$ENV_TMP"

# 7. Selection and library guards carry typed identities before library access.
run_tool bibtex
assert_rc "bibtex without a selection exits 1" 1
assert_error_identity \
  "bibtex missing selection is typed" \
  "selection_required" "SelectionRequiredError"

# 7b. bibtex rejects an invalid --library before any access (parse_library).
run_tool bibtex --item-key ABCD1234 --library notanid
assert_rc "bibtex invalid --library exits 1" 1
assert_error_identity \
  "bibtex invalid --library is typed" \
  "invalid_library" "InvalidLibraryError"

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

# 9. Cite selection / target guards return typed identities and leave the .bib
#    target byte-for-byte unchanged.
GUARD_TMP="$(mktemp -d)"
GUARD_BIB="$GUARD_TMP/guard.bib"
printf '@article{sentinel,\n  title = {Keep Me},\n}\n' >"$GUARD_BIB"
GUARD_BEFORE="$(cksum "$GUARD_BIB")"

run_tool cite --bib "$GUARD_BIB"
assert_rc "cite without a selection exits 1" 1
assert_error_identity \
  "cite missing selection is typed" \
  "selection_required" "SelectionRequiredError"

# Neither/both of --tex / --markdown is an error (the guard fires before access).
run_tool cite --item-key ABCD1234 --bib "$GUARD_BIB"
assert_rc "cite without a target exits 1" 1
assert_error_identity \
  "cite missing target is typed" \
  "citation_target_required" "CitationTargetError"

run_tool cite --item-key ABCD1234 --tex "$GUARD_TMP/a.tex" \
  --markdown "$GUARD_TMP/a.md" --bib "$GUARD_BIB"
assert_rc "cite with both targets exits 1" 1
assert_error_identity \
  "cite ambiguous target is typed" \
  "citation_target_required" "CitationTargetError"

if [ "$(cksum "$GUARD_BIB")" = "$GUARD_BEFORE" ]; then
  record_pass "cite guards leave bibliography unchanged"
else
  record_fail "cite guards leave bibliography unchanged"
fi

# bibliography selection guard.
run_tool bibliography
assert_rc "bibliography without a selection exits 1" 1
assert_error_identity \
  "bibliography missing selection is typed" \
  "selection_required" "SelectionRequiredError"

# 10. Unit-test the citation-insertion + hardened entry-detection helpers by
#     importing the module — no Zotero/BBT/library access. Covers \cite/[@key]
#     insertion, marker replace-in-place, missing-marker error, and the
#     hardened split_bib_entries (a "@type{...}" token inside a field value must
#     NOT become a phantom entry — the helper backing every reused .bib write).
UNIT_TMP="$(mktemp -d)"
UNIT_OUT="$(WORKDIR="$UNIT_TMP" uv run --quiet --with pyzotero==1.13.0 python - "$SCRIPT_ABS" <<'PY' 2>/tmp/zt_unit_err
import argparse, contextlib, importlib.util, io, json, os, sys
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

# insert_citation: missing marker has an exact type and leaves the draft unchanged.
texn = work / "nomarker.tex"
texn.write_text("No marker.\n")
try:
    zt.insert_citation(texn, "\\cite{k3}", "NOPE")
    raise SystemExit("missing marker did not raise")
except zt.MarkerNotFoundError as exc:
    assert exc.code == "marker_not_found", exc.code
    pass
assert texn.read_text() == "No marker.\n", texn.read_text()

# check_draft_target validates without mutating: a missing draft and a missing
# marker both raise, and it never writes. This is what lets cmd_cite reject a
# bad target BEFORE syncing the master .bib (so a typo cannot pollute it).
absent = work / "does_not_exist.tex"
try:
    zt.check_draft_target(absent, None)
    raise SystemExit("missing draft did not raise")
except zt.DraftNotFoundError as exc:
    assert exc.code == "draft_not_found", exc.code
    pass
assert not absent.exists(), "check_draft_target created the draft"
texc = work / "checkmarker.tex"
texc.write_text("No marker here.\n")
try:
    zt.check_draft_target(texc, "NOPE")
    raise SystemExit("missing marker did not raise in check_draft_target")
except zt.MarkerNotFoundError as exc:
    assert exc.code == "marker_not_found", exc.code
    pass
assert texc.read_text() == "No marker here.\n", texc.read_text()
zt.check_draft_target(texc, None)  # existing draft, no marker -> ok, no write
assert texc.read_text() == "No marker here.\n", texc.read_text()

# Generic exception diagnostics redact configured secrets while retaining a
# stable machine-readable fallback identity.
secret = "ZT_UNIT_SECRET_DO_NOT_LEAK"
os.environ["ZOTERO_API_KEY"] = secret
class Parser:
    def parse_args(self, _argv):
        def explode(_args):
            raise ValueError(f"transport included {secret}")
        return argparse.Namespace(func=explode)
zt.build_parser = Parser
stderr = io.StringIO()
with contextlib.redirect_stderr(stderr):
    assert zt.main([]) == 1
diagnostic = stderr.getvalue()
assert secret not in diagnostic, diagnostic
error = json.loads(diagnostic)["error"]
assert error["code"] == "unexpected_error", error
assert error["type"] == "ValueError", error

print("UNIT_OK")
PY
)" || true
if printf '%s' "$UNIT_OUT" | rg -q --fixed-strings 'UNIT_OK'; then
  record_pass "cite/insert + hardened entry-detection helpers behave"
else
  printf '      unit helper failed: %s\n' "$(cat /tmp/zt_unit_err)"
  record_fail "cite/insert + hardened entry-detection helpers behave"
fi
rm -rf "$UNIT_TMP" "$GUARD_TMP" /tmp/zt_unit_err

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi
exit 0
