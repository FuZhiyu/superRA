#!/usr/bin/env python3
"""CI-safe regression test locking in the live-harness deferred-import isolation.

The live runner (:mod:`sdk_load_harness`) is the only module that imports
``claude_agent_sdk``, and that import is deferred into ``run_skill_load_session``;
the per-stage / per-domain / always-loaded canary modules import the runner only
behind their own live entry points. Task 08's reviewer verified this isolation by
hand. This test makes it permanent: a future top-level ``from claude_agent_sdk
import ...`` (or a stray codex-cli import) in any of these modules — which would
pull a heavy optional dependency and a credentialed client onto the default
``pytest`` path — fails here instead of silently regressing.

Each module is imported in a fresh subprocess so this assertion is unaffected by
whatever the rest of the suite already loaded into ``sys.modules``. No model call
is made: importing a module only runs its top-level statements, which the deferred
pattern keeps free of SDK/codex-cli imports and of any network client construction.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Every live-harness module that must keep claude_agent_sdk / codex-cli off the
# default import path. sdk_load_harness owns the deferred SDK import; the three
# canary modules import the runner only behind their live entry points.
LIVE_HARNESS_MODULES = [
    "sdk_load_harness",
    "stage_loads_live",
    "domain_loads_live",
    "always_loaded_live",
]

# Substrings that must not appear in any sys.modules key after a bare import.
# claude_agent_sdk is the deferred SDK; the codex client/cli ships as `codex`-
# prefixed modules (codex_load_evidence is our own helper and is allowed).
_FORBIDDEN_MODULE_PREFIXES = ("claude_agent_sdk", "claude-agent-sdk")


def _imported_module_keys(module_name: str) -> list[str]:
    """Import ``module_name`` in a clean subprocess; return its sys.modules keys."""
    probe = (
        "import sys\n"
        f"sys.path.insert(0, {str(SCRIPT_DIR)!r})\n"
        f"import {module_name}\n"
        "import json\n"
        "print(json.dumps(sorted(sys.modules)))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"importing {module_name} failed:\n{result.stderr}"
    )
    import json

    return json.loads(result.stdout.strip().splitlines()[-1])


def test_live_harness_modules_do_not_import_claude_agent_sdk() -> None:
    """Importing any live-harness module must not pull claude_agent_sdk."""
    for module_name in LIVE_HARNESS_MODULES:
        keys = _imported_module_keys(module_name)
        leaked = [
            key
            for key in keys
            if any(prefix in key for prefix in _FORBIDDEN_MODULE_PREFIXES)
        ]
        assert not leaked, (
            f"{module_name} pulled claude_agent_sdk into sys.modules on import: "
            f"{leaked}. The SDK import must stay deferred inside the live entry "
            f"point, not run at module top level."
        )


def test_live_harness_modules_do_not_import_codex_cli() -> None:
    """Importing any live-harness module must not pull a codex-cli client.

    The codex client ships as ``codex``-prefixed modules; our own
    ``codex_load_evidence`` helper is the only allowed codex-prefixed import.
    """
    for module_name in LIVE_HARNESS_MODULES:
        keys = _imported_module_keys(module_name)
        leaked = [
            key
            for key in keys
            if (key == "codex" or key.startswith("codex."))
            and key != "codex_load_evidence"
        ]
        assert not leaked, (
            f"{module_name} pulled a codex-cli module into sys.modules on import: "
            f"{leaked}."
        )


def test_sdk_load_harness_defers_sdk_import_inside_a_function_body() -> None:
    """The SDK import lives inside a function body, not at module top level.

    A structural backstop to the sys.modules check: even if the SDK happened not
    to be installed in the test env (so an accidental top-level import would fail
    silently elsewhere), this confirms the only ``claude_agent_sdk`` import is
    indented (inside a function) rather than at column zero (module top level).
    The harness defers it into ``_run_session_async``, reached only via the live
    ``run_skill_load_session`` entry point.
    """
    source = (SCRIPT_DIR / "sdk_load_harness.py").read_text()
    import_lines = [
        line
        for line in source.splitlines()
        if "import claude_agent_sdk" in line or "from claude_agent_sdk" in line
    ]
    assert import_lines, "expected a claude_agent_sdk import in sdk_load_harness.py"
    for line in import_lines:
        assert line[:1].isspace(), (
            "claude_agent_sdk import must be deferred inside a function body "
            f"(indented), not at module top level; found: {line!r}"
        )
