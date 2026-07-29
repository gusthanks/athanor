#!/usr/bin/env python3
"""Validate the structure and basic invariants of an Athanor-enabled project."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path


REQUIRED_ROOT = ("AGENTS.md",)
REQUIRED_ATHANOR = (
    "PROJECT.md",
    "DECISIONS.md",
    "TASKS.md",
    "TOOLS.md",
    "INTEGRATIONS.md",
    "ROSTER.md",
    "RISKS.md",
    "ORGANIZATION-REVIEW.md",
    "config.json",
)
VALID_MODES = {"scribe", "alchemist", "adept", "guardian"}
TOKEN_PATTERN = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an Athanor project OS.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser.parse_args()


def valid_iso_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return dt.date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def validate(root: Path) -> dict:
    root = root.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []
    if not root.is_dir():
        return {
            "root": str(root),
            "valid": False,
            "checks": [],
            "errors": ["Project root is missing or is not a directory."],
            "warnings": [],
        }

    for relative in REQUIRED_ROOT:
        path = root / relative
        if not path.is_file():
            errors.append(f"Missing required file: {relative}")
        else:
            checks.append(relative)

    athanor = root / "athanor"
    if not athanor.is_dir():
        errors.append("Missing required directory: athanor")
    else:
        checks.append("athanor/")
    for relative in REQUIRED_ATHANOR:
        path = athanor / relative
        display = f"athanor/{relative}"
        if not path.is_file():
            errors.append(f"Missing required file: {display}")
            continue
        checks.append(display)
        if path.suffix.lower() in {".md", ".json"}:
            text = path.read_text(encoding="utf-8")
            tokens = TOKEN_PATTERN.findall(text)
            if tokens:
                errors.append(
                    f"Unrendered template tokens in {display}: {', '.join(sorted(set(tokens)))}"
                )
            if "[UNKNOWN]" in text:
                warnings.append(f"Unresolved project facts remain in {display}")

    config_path = athanor / "config.json"
    if config_path.is_file():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"Invalid athanor/config.json: {exc}")
        else:
            if config.get("date_format") != "YYYY-MM-DD":
                errors.append("athanor/config.json must use date_format YYYY-MM-DD")
            if not valid_iso_date(config.get("created")):
                errors.append("athanor/config.json created must be YYYY-MM-DD")
            if config.get("mode") not in VALID_MODES:
                errors.append(
                    "athanor/config.json mode must be scribe, alchemist, adept, or guardian"
                )

    for directory in ("agents", "memory"):
        path = athanor / directory
        display = f"athanor/{directory}/"
        if not path.is_dir():
            warnings.append(f"Missing optional working directory: {display}")
        else:
            checks.append(display)

    claude = root / "CLAUDE.md"
    if not claude.exists():
        warnings.append("CLAUDE.md compatibility pointer is not present")

    return {
        "root": str(root),
        "valid": not errors,
        "checks": checks,
        "errors": errors,
        "warnings": sorted(set(warnings)),
    }


def main() -> int:
    args = parse_args()
    result = validate(args.root)
    if args.json_output:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        state = "PASS" if result["valid"] else "FAIL"
        print(f"{state}: {result['root']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
        print(f"Checks passed: {len(result['checks'])}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
