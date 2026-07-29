from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
INSTALLER_PATH = REPO / "scripts" / "install_athanor.py"
SPEC = importlib.util.spec_from_file_location("install_athanor", INSTALLER_PATH)
assert SPEC and SPEC.loader
install_athanor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(install_athanor)


class AgentInstallerTests(unittest.TestCase):
    def test_copy_install_status_and_recoverable_uninstall(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            result = install_athanor.install_agent(
                "claude", REPO, home, "copy"
            )
            self.assertEqual(result["method"], "copy")

            target = home / ".claude" / "skills"
            skills = install_athanor.discover_skills(REPO)
            self.assertEqual(
                sorted(path.name for path in skills),
                sorted(
                    path.name
                    for path in target.iterdir()
                    if path.is_dir() and not path.name.startswith(".")
                ),
            )
            status = install_athanor.agent_status("claude", REPO, home)
            self.assertTrue(status["healthy"])
            self.assertTrue(
                all(item["state"] == "copied" for item in status["skills"])
            )

            removed = install_athanor.uninstall_agent(
                "claude", REPO, home, confirmed=True
            )
            backup = Path(removed["backup_root"])
            self.assertTrue(backup.is_dir())
            self.assertTrue((backup / "athanor" / "SKILL.md").is_file())
            self.assertFalse((target / "athanor").exists())

    def test_link_install_status_and_uninstall_preserves_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            source_skill = REPO / "plugins" / "athanor" / "skills" / "athanor"
            install_athanor.install_agent(
                "antigravity", REPO, home, "link"
            )
            status = install_athanor.agent_status("antigravity", REPO, home)
            self.assertTrue(status["healthy"])
            self.assertTrue(
                all(item["state"] == "linked" for item in status["skills"])
            )

            install_athanor.uninstall_agent(
                "antigravity", REPO, home, confirmed=True
            )
            self.assertTrue((source_skill / "SKILL.md").is_file())
            self.assertFalse(
                (home / ".gemini" / "config" / "skills" / "athanor").exists()
            )

    def test_collision_refuses_before_creating_other_skills(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            target = home / ".claude" / "skills"
            collision = target / "athanor"
            collision.mkdir(parents=True)
            (collision / "SKILL.md").write_text("unrelated", encoding="utf-8")

            with self.assertRaises(install_athanor.InstallerError):
                install_athanor.install_agent(
                    "claude", REPO, home, "copy"
                )
            self.assertFalse((target / "athanor-help").exists())
            self.assertEqual(
                (collision / "SKILL.md").read_text(encoding="utf-8"), "unrelated"
            )

    def test_dry_run_does_not_create_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            result = install_athanor.install_agent(
                "claude", REPO, home, "link", dry_run=True
            )
            self.assertEqual(result["mode"], "dry-run")
            self.assertFalse((home / ".claude").exists())


class CodexInstallerTests(unittest.TestCase):
    def test_status_parses_marketplace_and_plugin(self):
        def runner(arguments, **_kwargs):
            command = " ".join(arguments)
            if "marketplace list" in command:
                stdout = (
                    "MARKETPLACE ROOT\n"
                    "athanor-community Q:\\\\gustavo\\\\athanor\n"
                )
            else:
                stdout = (
                    "PLUGIN STATUS\n"
                    "athanor@athanor-community installed\n"
                )
            return subprocess.CompletedProcess(arguments, 0, stdout, "")

        status = install_athanor.codex_status(runner)
        self.assertTrue(status["healthy"])

    def test_install_uses_exact_codex_commands(self):
        state = {"marketplace": False, "plugin": False}
        calls: list[list[str]] = []

        def runner(arguments, **_kwargs):
            arguments = list(arguments)
            calls.append(arguments)
            command = " ".join(arguments)
            if command.endswith("marketplace list"):
                body = (
                    "athanor-community X\n" if state["marketplace"] else ""
                )
                return subprocess.CompletedProcess(arguments, 0, body, "")
            if command.endswith("plugin list"):
                body = (
                    "athanor@athanor-community installed\n"
                    if state["plugin"]
                    else ""
                )
                return subprocess.CompletedProcess(arguments, 0, body, "")
            if "marketplace add" in command:
                state["marketplace"] = True
                return subprocess.CompletedProcess(arguments, 0, "added", "")
            if command.endswith("plugin add athanor@athanor-community"):
                state["plugin"] = True
                return subprocess.CompletedProcess(arguments, 0, "installed", "")
            return subprocess.CompletedProcess(arguments, 1, "", "unexpected")

        result = install_athanor.install_codex(REPO, runner=runner)
        self.assertTrue(result["after"]["healthy"])
        self.assertIn(
            ["codex", "plugin", "marketplace", "add", str(REPO.resolve())],
            calls,
        )
        self.assertIn(
            ["codex", "plugin", "add", "athanor@athanor-community"],
            calls,
        )


if __name__ == "__main__":
    unittest.main()
