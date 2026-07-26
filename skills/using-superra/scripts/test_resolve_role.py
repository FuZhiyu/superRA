#!/usr/bin/env python3
"""Tests for packaged canonical-role resolution."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "skills" / "using-superra" / "scripts" / "resolve_role.py"


class ResolveRoleTests(unittest.TestCase):
    def test_resolves_packaged_roles_from_foreign_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            plugin_root = temp_dir / "plugin-cache" / "superra"
            script = plugin_root / "skills" / "using-superra" / "scripts" / SCRIPT.name
            script.parent.mkdir(parents=True)
            shutil.copy2(SCRIPT, script)

            agents = plugin_root / "agents"
            agents.mkdir()
            for role in ("implementer", "reviewer"):
                shutil.copy2(REPO_ROOT / "agents" / f"{role}.md", agents / f"{role}.md")

            foreign_project = temp_dir / "research-project"
            foreign_project.mkdir()
            for role in ("implementer", "reviewer"):
                completed = subprocess.run(
                    ["python3", str(script), role],
                    cwd=foreign_project,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    Path(completed.stdout.strip()),
                    (agents / f"{role}.md").resolve(),
                )


if __name__ == "__main__":
    unittest.main()
