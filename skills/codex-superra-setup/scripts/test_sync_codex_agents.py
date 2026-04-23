#!/usr/bin/env python3
"""Tests for the superRA Codex agent sync script."""

from __future__ import annotations

import runpy
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "skills" / "codex-superra-setup" / "scripts" / "sync_codex_agents.py"
SCRIPT_NS = runpy.run_path(str(SCRIPT))


class SyncCodexAgentsTests(unittest.TestCase):
    def test_global_install_and_conflict_handling(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            home_dir = Path(home)
            target_dir = home_dir / ".codex" / "agents"

            self.run_script("--scope", "global", "--home-dir", str(home_dir))
            self.assertTrue((target_dir / "superra_implementer.toml").exists())
            self.assertTrue((target_dir / "superra_reviewer.toml").exists())

            self.run_script("--scope", "global", "--home-dir", str(home_dir))

            unmanaged = target_dir / "superra_reviewer.toml"
            unmanaged.write_text("name = \"custom\"\n", encoding="utf-8")
            failed = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--scope",
                    "global",
                    "--home-dir",
                    str(home_dir),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("Refusing to overwrite unmanaged file", failed.stderr)

            self.run_script(
                "--scope",
                "global",
                "--home-dir",
                str(home_dir),
                "--force",
            )
            self.assertIn(
                "superra_reviewer",
                unmanaged.read_text(encoding="utf-8"),
            )

    def test_project_check_matches_committed_generated_artifacts(self) -> None:
        self.run_script("--scope", "project", "--check")

    def test_committed_direct_mode_refs_match_generator(self) -> None:
        expected = SCRIPT_NS["render_all_direct_mode_refs"](REPO_ROOT)
        for relative_path, content in expected.items():
            self.assertEqual(
                (REPO_ROOT / relative_path).read_text(encoding="utf-8"),
                content,
            )

    def test_generated_direct_mode_refs_have_managed_headers(self) -> None:
        expected = SCRIPT_NS["render_all_direct_mode_refs"](REPO_ROOT)
        for relative_path, content in expected.items():
            self.assertIn("Managed by superRA codex-superra-setup", content)
            self.assertIn(
                "<!-- Regenerate with: rerun superRA:codex-superra-setup -->",
                content,
            )
            self.assertNotIn("temporary manual mirror", content.lower())
            self.assertNotIn(
                "skills/codex-superra-setup/scripts/sync_codex_agents.py",
                content,
            )

    def test_generated_direct_mode_refs_include_sync_context(self) -> None:
        expected = SCRIPT_NS["render_all_direct_mode_refs"](REPO_ROOT)
        implementer = expected[
            "skills/using-superRA/references/direct-mode-implementer.md"
        ]
        reviewer = expected["skills/using-superRA/references/direct-mode-reviewer.md"]

        self.assertIn("For `Stage: sync`, read", implementer)
        self.assertIn(
            "PLAN.md's header, `## Decisions`, existing `## Sync Map`",
            implementer,
        )
        self.assertIn("branch-level sync review", reviewer)
        self.assertIn("current base/ref/current", reviewer)

    def test_generated_agents_have_repo_agnostic_regenerate_hint(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            home_dir = Path(home)
            target_dir = home_dir / ".codex" / "agents"

            self.run_script("--scope", "global", "--home-dir", str(home_dir))
            generated = (target_dir / "superra_implementer.toml").read_text(
                encoding="utf-8"
            )
            self.assertIn(
                "# Regenerate with: rerun superRA:codex-superra-setup",
                generated,
            )
            self.assertNotIn(
                "skills/codex-superra-setup/scripts/sync_codex_agents.py",
                generated,
            )

    def run_script(self, *args: str) -> None:
        subprocess.run(
            ["python3", str(SCRIPT), *args],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
