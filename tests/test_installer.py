from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
INSTALLER_PATH = REPO / "scripts" / "install_athanor.py"
SPEC = importlib.util.spec_from_file_location("install_athanor", INSTALLER_PATH)
assert SPEC and SPEC.loader
install_athanor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(install_athanor)


def codex_plugin_output(version: str) -> str:
    return (
        f"{'PLUGIN':<34}{'STATUS':<20}{'VERSION':<14}PATH\n"
        f"{'athanor@athanor-community':<34}"
        f"{'installed, enabled':<20}{version:<14}Q:\\cache\\athanor\n"
    )


def create_minimal_source(root: Path, skill_names: tuple[str, ...]) -> None:
    manifest = root / "plugins" / "athanor" / ".codex-plugin" / "plugin.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps(
            {
                "name": "athanor",
                "version": "9.9.9",
                "description": "test",
                "license": "MIT",
                "skills": "./skills/",
            }
        ),
        encoding="utf-8",
    )
    skill_root = root / "plugins" / "athanor" / "skills"
    for name in skill_names:
        path = skill_root / name
        path.mkdir(parents=True, exist_ok=True)
        (path / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: test\n---\n",
            encoding="utf-8",
        )


class AgentInstallerTests(unittest.TestCase):
    def test_status_reports_registered_skill_removed_from_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            home = base / "home"
            create_minimal_source(source, ("athanor", "retired-skill"))
            install_athanor.install_agent("claude", source, home, "copy")

            shutil.rmtree(
                source / "plugins" / "athanor" / "skills" / "retired-skill"
            )
            status = install_athanor.agent_status("claude", source, home)

            self.assertFalse(status["healthy"])
            self.assertIn(
                ("retired-skill", "retired-present"),
                {(item["skill"], item["state"]) for item in status["skills"]},
            )
            self.assertTrue(
                any("retire it safely" in warning for warning in status["warnings"])
            )

    def test_registry_root_must_be_an_object(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / ".athanor-install.json"
            path.write_text("[]\n", encoding="utf-8")
            with self.assertRaises(install_athanor.InstallerError):
                install_athanor.load_registry(path)

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
            registry = json.loads(
                (target / ".athanor-install.json").read_text(encoding="utf-8")
            )
            self.assertEqual(registry["schema_version"], "2")
            self.assertEqual(
                registry["source_version"],
                install_athanor.plugin_manifest(REPO)["version"],
            )
            self.assertTrue(registry["skill_fingerprints"])

            removed = install_athanor.uninstall_agent(
                "claude", REPO, home, confirmed=True
            )
            backup = Path(removed["backup_root"])
            self.assertTrue(backup.is_dir())
            self.assertTrue((backup / "athanor" / "SKILL.md").is_file())
            self.assertFalse((target / "athanor").exists())

    def test_copy_refresh_backs_up_and_refuses_local_modification(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            install_athanor.install_agent("claude", REPO, home, "copy")
            refreshed = install_athanor.refresh_agent("claude", REPO, home)
            self.assertTrue(Path(refreshed["backup_root"]).is_dir())
            self.assertTrue(
                (Path(refreshed["backup_root"]) / ".athanor-install.json").is_file()
            )
            self.assertTrue(
                install_athanor.agent_status("claude", REPO, home)["healthy"]
            )

            copied_skill = home / ".claude" / "skills" / "athanor" / "SKILL.md"
            copied_skill.write_text(
                copied_skill.read_text(encoding="utf-8") + "\nlocal change\n",
                encoding="utf-8",
            )
            status = install_athanor.agent_status("claude", REPO, home)
            self.assertIn(
                "modified-copy",
                {item["state"] for item in status["skills"]},
            )
            with self.assertRaises(install_athanor.InstallerError):
                install_athanor.refresh_agent("claude", REPO, home)
            with self.assertRaises(install_athanor.InstallerError):
                install_athanor.install_agent("claude", REPO, home, "copy")

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
            refreshed = install_athanor.refresh_agent(
                "antigravity", REPO, home
            )
            self.assertTrue(
                all(
                    operation["action"] == "keep-link"
                    for operation in refreshed["operations"]
                )
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

    def test_copy_refresh_adds_and_retires_skills_recoverably(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            home = base / "home"
            create_minimal_source(source, ("athanor", "old-skill"))
            install_athanor.install_agent("claude", source, home, "copy")

            shutil.rmtree(
                source / "plugins" / "athanor" / "skills" / "old-skill"
            )
            create_minimal_source(source, ("athanor", "new-skill"))
            result = install_athanor.refresh_agent("claude", source, home)

            target = home / ".claude" / "skills"
            self.assertTrue((target / "new-skill" / "SKILL.md").is_file())
            self.assertFalse((target / "old-skill").exists())
            self.assertTrue(
                (Path(result["backup_root"]) / "old-skill" / "SKILL.md").is_file()
            )
            registry = json.loads(
                (target / ".athanor-install.json").read_text(encoding="utf-8")
            )
            self.assertEqual(set(registry["skills"]), {"athanor", "new-skill"})

    def test_copy_refresh_rolls_back_if_swap_fails_after_backup(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            home = base / "home"
            create_minimal_source(source, ("athanor",))
            install_athanor.install_agent("claude", source, home, "copy")
            destination = home / ".claude" / "skills" / "athanor"
            original = (destination / "SKILL.md").read_text(encoding="utf-8")
            real_move = shutil.move

            def fail_staging_move(source_path, destination_path, *args, **kwargs):
                if ".athanor-staging-" in str(source_path):
                    raise OSError("simulated staging failure")
                return real_move(source_path, destination_path, *args, **kwargs)

            with mock.patch.object(
                install_athanor.shutil, "move", side_effect=fail_staging_move
            ):
                with self.assertRaises(OSError):
                    install_athanor.refresh_agent("claude", source, home)

            self.assertTrue(destination.is_dir())
            self.assertEqual(
                (destination / "SKILL.md").read_text(encoding="utf-8"),
                original,
            )

    def test_link_refresh_adds_and_retires_skills(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            home = base / "home"
            create_minimal_source(source, ("athanor", "old-skill"))
            install_athanor.install_agent("antigravity", source, home, "link")

            shutil.rmtree(
                source / "plugins" / "athanor" / "skills" / "old-skill"
            )
            create_minimal_source(source, ("athanor", "new-skill"))
            result = install_athanor.refresh_agent("antigravity", source, home)

            target = home / ".gemini" / "config" / "skills"
            self.assertTrue(
                install_athanor.link_points_to(
                    source / "plugins" / "athanor" / "skills" / "new-skill",
                    target / "new-skill",
                )
            )
            self.assertFalse(install_athanor.path_present(target / "old-skill"))
            self.assertTrue(
                (Path(result["backup_root"]) / "retired-links.json").is_file()
            )


class CodexInstallerTests(unittest.TestCase):
    def test_status_parses_marketplace_and_plugin(self):
        def runner(arguments, **_kwargs):
            command = " ".join(arguments)
            if "marketplace list" in command:
                stdout = (
                    "MARKETPLACE ROOT\n"
                    "athanor-community C:\\\\src\\\\athanor\n"
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
                    codex_plugin_output(
                        install_athanor.plugin_manifest(REPO)["version"]
                    )
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

    def test_refresh_codex_reinstalls_even_when_present(self):
        calls: list[list[str]] = []

        def runner(arguments, **_kwargs):
            arguments = list(arguments)
            calls.append(arguments)
            command = " ".join(arguments)
            if command.endswith("marketplace list"):
                return subprocess.CompletedProcess(
                    arguments, 0, "athanor-community X\n", ""
                )
            if command.endswith("plugin list"):
                return subprocess.CompletedProcess(
                    arguments,
                    0,
                    codex_plugin_output(
                        install_athanor.plugin_manifest(REPO)["version"]
                    ),
                    "",
                )
            if command.endswith("plugin add athanor@athanor-community"):
                return subprocess.CompletedProcess(arguments, 0, "refreshed", "")
            return subprocess.CompletedProcess(arguments, 1, "", "unexpected")

        result = install_athanor.refresh_codex(REPO, runner=runner)
        self.assertTrue(result["after"]["healthy"])
        self.assertIn(
            ["codex", "plugin", "add", "athanor@athanor-community"],
            calls,
        )

    def test_codex_status_detects_stale_cache(self):
        def runner(arguments, **_kwargs):
            command = " ".join(arguments)
            if command.endswith("marketplace list"):
                return subprocess.CompletedProcess(
                    arguments, 0, "athanor-community X\n", ""
                )
            return subprocess.CompletedProcess(
                arguments, 0, codex_plugin_output("0.2.0"), ""
            )

        status = install_athanor.codex_status(runner, REPO)
        self.assertFalse(status["healthy"])
        self.assertFalse(status["fresh"])
        self.assertEqual(status["installed_version"], "0.2.0")


class DoctorTests(unittest.TestCase):
    def test_repository_status_reports_source_and_git(self):
        status = install_athanor.repository_status(REPO)
        self.assertEqual(
            status["version"], install_athanor.plugin_manifest(REPO)["version"]
        )
        self.assertEqual(status["skills"], 9)
        self.assertTrue(status["git"]["available"])


if __name__ == "__main__":
    unittest.main()
