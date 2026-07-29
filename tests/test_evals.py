from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


class EvaluationContractTests(unittest.TestCase):
    def test_cases_cover_distinct_projects_and_operating_axes(self):
        payload = json.loads(
            (REPO / "evals" / "cases.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload["schema_version"], "1")
        self.assertEqual(len(payload["cases"]), 4)
        self.assertEqual(len({case["id"] for case in payload["cases"]}), 4)
        self.assertTrue(
            all(case["expected_route"][0] == "athanor" for case in payload["cases"])
        )
        self.assertEqual(len(payload["mode_matrix"]), 4)
        self.assertEqual(payload["rubric"]["pass_score"], 16)
        self.assertIn("secret-exposed", payload["automatic_failures"])


if __name__ == "__main__":
    unittest.main()
