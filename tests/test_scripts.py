from __future__ import annotations

import csv
import importlib.util
import json
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
            self.assertTrue((root / "athanor" / "BOOTSTRAP-MERGE.md").exists())
            self.assertGreater(applied["summary"]["skip"], 0)


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
    def test_scaffold_validates_with_unknown_warnings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scaffold_project.scaffold(root, "Valid Project", "guardian", True)
            result = validate_project_os.validate(root)
            self.assertTrue(result["valid"])
            self.assertTrue(result["warnings"])


if __name__ == "__main__":
    unittest.main()
