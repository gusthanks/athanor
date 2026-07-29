from __future__ import annotations

import csv
import importlib.util
import json
import argparse
import concurrent.futures
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "plugins" / "athanor" / "skills"


def load_module(name: str, relative: str):
    path = SKILLS / relative
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scaffold_project = load_module(
    "scaffold_project", "athanor-init/scripts/scaffold_project.py"
)
scan_project = load_module("scan_project", "athanor-audit/scripts/scan_project.py")
apply_plan = load_module(
    "apply_plan", "athanor-organize/scripts/apply_plan.py"
)
repository_advisor = load_module(
    "repository_advisor", "athanor-chronicle/scripts/repository_advisor.py"
)
validate_project_os = load_module(
    "validate_project_os", "athanor-maintain/scripts/validate_project_os.py"
)
checkpoint = load_module(
    "checkpoint", "athanor-maintain/scripts/checkpoint.py"
)


class ScaffoldTests(unittest.TestCase):
    def test_preview_apply_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "project"
            root.mkdir()
            existing = root / "AGENTS.md"
            existing.write_text("project-specific", encoding="utf-8")

            preview = scaffold_project.scaffold(
                root, "Example Project", "alchemist", False
            )
            self.assertFalse((root / "athanor").exists())
            self.assertGreater(preview["summary"]["create"], 0)

            applied = scaffold_project.scaffold(
                root, "Example Project", "alchemist", True
            )
            self.assertEqual(existing.read_text(encoding="utf-8"), "project-specific")
            config = json.loads(
                (root / "athanor" / "config.json").read_text(encoding="utf-8")
            )
            self.assertEqual(config["project_name"], "Example Project")
            self.assertEqual(config["date_format"], "YYYY-MM-DD")
            self.assertEqual(config["schema_version"], "2")
            self.assertEqual(config["collaboration_style"], "alchemist")
            self.assertEqual(config["assurance_level"], "standard")
            self.assertTrue((root / "athanor" / "BOOTSTRAP-MERGE.md").exists())
            self.assertGreater(applied["summary"]["skip"], 0)

    def test_legacy_guardian_maps_to_two_axes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scaffold_project.scaffold(root, "Guarded Project", "guardian", True)
            config = json.loads(
                (root / "athanor" / "config.json").read_text(encoding="utf-8")
            )
            self.assertEqual(config["collaboration_style"], "alchemist")
            self.assertEqual(config["assurance_level"], "guardian")

    def test_scaffold_refuses_link_outside_project_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "project"
            outside = base / "outside"
            root.mkdir()
            outside.mkdir()
            linked = root / "athanor"
            if os.name == "nt":
                completed = subprocess.run(
                    [
                        "cmd.exe",
                        "/d",
                        "/c",
                        "mklink",
                        "/J",
                        str(linked),
                        str(outside),
                    ],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
            else:
                linked.symlink_to(outside, target_is_directory=True)

            with self.assertRaises(ValueError):
                scaffold_project.scaffold(
                    root, "Contained Project", "alchemist", True
                )
            self.assertFalse((outside / "PROJECT.md").exists())
            self.assertFalse((root / "AGENTS.md").exists())


class AuditTests(unittest.TestCase):
    def test_scan_uses_metadata_without_secret_values(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "README.md").write_text("# Example", encoding="utf-8")
            secret_value = "DO_NOT_LEAK_123"
            (root / ".env").write_text(f"TOKEN={secret_value}", encoding="utf-8")
            (root / "scratch.tmp").write_text("temporary", encoding="utf-8")

            report = scan_project.scan(root, 1)
            serialized = json.dumps(report)
            self.assertFalse(report["content_read"])
            self.assertIn(".env", report["sensitive_filename_candidates"])
            self.assertIn("scratch.tmp", report["temporary_file_candidates"])
            self.assertNotIn(secret_value, serialized)


class OrganizationTests(unittest.TestCase):
    def write_plan(self, path: Path, source: str, destination: str):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=sorted(apply_plan.REQUIRED_COLUMNS)
            )
            writer.writeheader()
            writer.writerow(
                {
                    "id": "ORG-001",
                    "action": "move",
                    "source": source,
                    "destination": destination,
                    "reason": "test",
                    "confidence": "high",
                    "risk": "low",
                    "approved": "true",
                }
            )

    def test_dry_run_then_apply_with_ledger(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "source.txt").write_text("same bytes", encoding="utf-8")
            plan = root / "plan.csv"
            self.write_plan(plan, "source.txt", "docs/destination.txt")

            result, code = apply_plan.run(root, plan, False, False, False, None)
            self.assertEqual(code, 0)
            self.assertEqual(result["mode"], "dry-run")
            self.assertTrue((root / "source.txt").exists())

            result, code = apply_plan.run(root, plan, True, True, False, None)
            self.assertEqual(code, 0)
            self.assertFalse((root / "source.txt").exists())
            self.assertEqual(
                (root / "docs" / "destination.txt").read_text(encoding="utf-8"),
                "same bytes",
            )
            self.assertTrue((root / "athanor" / "organization-ledger.csv").exists())
            self.assertEqual(
                result["applied"][0]["sha256_before"],
                result["applied"][0]["sha256_after"],
            )

    def test_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "source.txt").write_text("x", encoding="utf-8")
            plan = root / "plan.csv"
            self.write_plan(plan, "source.txt", "../outside.txt")
            result, code = apply_plan.run(root, plan, False, False, False, None)
            self.assertEqual(code, 2)
            self.assertTrue(result["errors"])


class ChronicleTests(unittest.TestCase):
    def test_advice_is_conservative_and_content_free(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "app.py").write_text("print('ok')", encoding="utf-8")
            secret_value = "ANOTHER_SECRET_VALUE"
            (root / ".env").write_text(secret_value, encoding="utf-8")
            (root / "audio.wav").write_bytes(b"RIFF")
            report = repository_advisor.advise(root, 10 * 1024 * 1024)
            serialized = json.dumps(report)
            self.assertFalse(report["content_read"])
            self.assertEqual(
                report["groups"]["git_normal_candidate"][0]["path"], "app.py"
            )
            self.assertEqual(
                report["groups"]["secret_manager_or_human_review"][0]["path"],
                ".env",
            )
            self.assertEqual(
                report["groups"]["asset_storage_or_lfs"][0]["path"], "audio.wav"
            )
            self.assertNotIn(secret_value, serialized)


class MaintenanceTests(unittest.TestCase):
    def test_config_root_must_be_an_object(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scaffold_project.scaffold(root, "Invalid Config", "alchemist", True)
            (root / "athanor" / "config.json").write_text(
                "[]\n", encoding="utf-8"
            )

            result = validate_project_os.validate(root)

            self.assertFalse(result["valid"])
            self.assertIn(
                "Invalid athanor/config.json: root must be an object",
                result["errors"],
            )

    def test_escaped_pipe_in_task_cell_is_parsed(self):
        text = """# Work Ledger

| ID | Outcome | Owner | Status | Depends on | Next action | Evidence | Updated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-001 | Compare A \| B | Ada | done | — | Complete | doc \| review | 2026-07-29 |
"""
        rows, warnings = validate_project_os.parse_task_table(text)
        self.assertEqual(warnings, [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Outcome"], "Compare A | B")
        self.assertEqual(rows[0]["Evidence"], "doc | review")

    def test_scaffold_validates_with_unknown_warnings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scaffold_project.scaffold(root, "Valid Project", "guardian", True)
            result = validate_project_os.validate(root)
            self.assertTrue(result["valid"])
            self.assertTrue(result["warnings"])

    def test_schema_v1_remains_valid_with_migration_warning(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scaffold_project.scaffold(root, "Legacy Project", "alchemist", True)
            config_path = root / "athanor" / "config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["schema_version"] = "1"
            config["mode"] = "guardian"
            config.pop("collaboration_style")
            config.pop("assurance_level")
            config_path.write_text(
                json.dumps(config, indent=2) + "\n", encoding="utf-8"
            )
            result = validate_project_os.validate(root)
            self.assertTrue(result["valid"])
            self.assertTrue(
                any("schema v1" in warning for warning in result["warnings"])
            )

    def test_task_dependency_cycle_is_reported(self):
        text = """# Work Ledger

| ID | Outcome | Owner | Status | Depends on | Next action | Evidence | Updated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-001 | First | A | blocked | TASK-002 | Wait | x | 2026-07-29 |
| TASK-002 | Second | B | blocked | TASK-001 | Wait | x | 2026-07-29 |
"""
        warnings = validate_project_os.task_warnings(text)
        self.assertTrue(any("cycle" in warning.lower() for warning in warnings))

    def test_duplicate_task_id_is_reported(self):
        text = """# Work Ledger

| ID | Outcome | Owner | Status | Depends on | Next action | Evidence | Updated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-001 | First | A | ready | — | Work | x | 2026-07-29 |
| TASK-001 | Duplicate | B | blocked | TASK-002 | Wait | x | 2026-07-29 |
"""
        warnings = validate_project_os.task_warnings(text)
        self.assertIn("Duplicate task ID: TASK-001", warnings)


class CheckpointTests(unittest.TestCase):
    def args(self, **overrides):
        values = {
            "goal": "Continue the pilot",
            "next_action": "Review TASK-002",
            "slug": None,
            "completed": ["TASK-001 done"],
            "remaining": ["TASK-002"],
            "blocker": [],
            "decision": ["DEC-001"],
            "task": ["TASK-002"],
            "path": ["athanor/TASKS.md"],
            "verification": ["validator passed"],
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def test_checkpoint_is_append_only_and_restorable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "athanor").mkdir()
            first = checkpoint.save_checkpoint(root, self.args())
            second = checkpoint.save_checkpoint(root, self.args())
            self.assertNotEqual(first["path"], second["path"])
            listed = checkpoint.list_checkpoints(root)
            self.assertEqual(len(listed["checkpoints"]), 2)
            restored = checkpoint.restore_checkpoint(root, None)
            self.assertEqual(restored["path"], str(Path(second["path"]).resolve()))
            self.assertIn("Exact next action", restored["content"])

    def test_checkpoint_rejects_secret_assignment(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "athanor").mkdir()
            with self.assertRaises(ValueError):
                checkpoint.save_checkpoint(
                    root,
                    self.args(completed=["API_KEY=do-not-store"]),
                )
            with self.assertRaises(ValueError):
                checkpoint.save_checkpoint(
                    root,
                    self.args(completed=["Authorization: Bearer not-a-real-token"]),
                )
            with self.assertRaises(ValueError):
                checkpoint.save_checkpoint(
                    root,
                    self.args(slug="password=do-not-store"),
                )

    def test_concurrent_checkpoints_never_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "athanor").mkdir()
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                results = list(
                    executor.map(
                        lambda _: checkpoint.save_checkpoint(root, self.args()),
                        range(8),
                    )
                )
            paths = {result["path"] for result in results}
            self.assertEqual(len(paths), 8)
            self.assertTrue(all(Path(path).is_file() for path in paths))

    def test_checkpoint_refuses_link_outside_project_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "project"
            outside = base / "outside"
            root.mkdir()
            outside.mkdir()
            linked = root / "athanor"
            if os.name == "nt":
                completed = subprocess.run(
                    [
                        "cmd.exe",
                        "/d",
                        "/c",
                        "mklink",
                        "/J",
                        str(linked),
                        str(outside),
                    ],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
            else:
                linked.symlink_to(outside, target_is_directory=True)

            with self.assertRaises(ValueError):
                checkpoint.save_checkpoint(root, self.args())
            self.assertFalse((outside / "checkpoints").exists())


if __name__ == "__main__":
    unittest.main()
