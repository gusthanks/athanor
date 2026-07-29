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
VALID_LEGACY_MODES = {"scribe", "alchemist", "adept", "guardian"}
VALID_COLLABORATION = {"scribe", "alchemist", "adept"}
VALID_ASSURANCE = {"lean", "standard", "guardian"}
VALID_TASK_STATUSES = {
    "proposed",
    "ready",
    "in-progress",
    "blocked",
    "done",
    "cancelled",
}
TOKEN_PATTERN = re.compile(r"\{\{[A-Z0-9_]+\}\}")
TASK_ID_PATTERN = re.compile(r"\bTASK-[A-Za-z0-9._-]+\b")


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


def split_markdown_row(line: str) -> list[str]:
    body = line.strip().strip("|")
    return [
        cell.strip().replace(r"\|", "|")
        for cell in re.split(r"(?<!\\)\|", body)
    ]


def parse_task_table(text: str) -> tuple[list[dict[str, str]], list[str]]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.strip().startswith("| ID |"):
            continue
        headers = split_markdown_row(line)
        if index + 1 >= len(lines):
            return [], ["TASKS.md task table has no separator row"]
        rows: list[dict[str, str]] = []
        warnings: list[str] = []
        for line_number, row_line in enumerate(lines[index + 2 :], start=index + 3):
            if not row_line.strip().startswith("|"):
                break
            cells = split_markdown_row(row_line)
            if len(cells) != len(headers):
                warnings.append(
                    f"TASKS.md row {line_number} has {len(cells)} cells; "
                    f"expected {len(headers)}"
                )
                continue
            rows.append(dict(zip(headers, cells)))
        return rows, warnings
    return [], []


def task_warnings(text: str) -> list[str]:
    warnings: list[str] = []
    rows, parse_warnings = parse_task_table(text)
    warnings.extend(parse_warnings)
    if not rows:
        return ["TASKS.md has no parseable task table"]
    headers = set(rows[0]) if rows else set()
    if "Depends on" not in headers:
        warnings.append("TASKS.md uses the v1 table without a Depends on column")
        return warnings

    tasks: dict[str, dict[str, str]] = {}
    for row in rows:
        task_id = row.get("ID", "")
        if not task_id:
            continue
        if task_id in tasks:
            warnings.append(f"Duplicate task ID: {task_id}")
            continue
        tasks[task_id] = row
    graph: dict[str, set[str]] = {}
    for task_id, row in tasks.items():
        status = row.get("Status", "").lower()
        if status and status not in VALID_TASK_STATUSES:
            warnings.append(f"{task_id} has unknown status: {status}")
        dependencies = set(TASK_ID_PATTERN.findall(row.get("Depends on", "")))
        graph[task_id] = dependencies
        if task_id in dependencies:
            warnings.append(f"{task_id} depends on itself")
        for dependency in sorted(dependencies):
            if dependency not in tasks:
                warnings.append(f"{task_id} references missing dependency {dependency}")
        if status == "ready":
            unfinished = [
                dependency
                for dependency in dependencies
                if tasks.get(dependency, {}).get("Status", "").lower() != "done"
            ]
            if unfinished:
                warnings.append(
                    f"{task_id} is ready but has unfinished dependencies: "
                    + ", ".join(sorted(unfinished))
                )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str, trail: list[str]) -> None:
        if task_id in visiting:
            cycle_start = trail.index(task_id)
            cycle = trail[cycle_start:]
            message = "Task dependency cycle: " + " -> ".join(cycle)
            if message not in warnings:
                warnings.append(message)
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in graph.get(task_id, set()):
            if dependency in graph:
                visit(dependency, trail + [dependency])
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in graph:
        visit(task_id, [task_id])
    return warnings


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

    schema_version = None
    config_path = athanor / "config.json"
    if config_path.is_file():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"Invalid athanor/config.json: {exc}")
        else:
            if not isinstance(config, dict):
                errors.append("Invalid athanor/config.json: root must be an object")
                config = {}
            schema_version = str(config.get("schema_version", ""))
            if config.get("date_format") != "YYYY-MM-DD":
                errors.append("athanor/config.json must use date_format YYYY-MM-DD")
            if not valid_iso_date(config.get("created")):
                errors.append("athanor/config.json created must be YYYY-MM-DD")
            if schema_version == "1":
                if config.get("mode") not in VALID_LEGACY_MODES:
                    errors.append(
                        "athanor/config.json v1 mode must be scribe, alchemist, "
                        "adept, or guardian"
                    )
                else:
                    legacy = config.get("mode")
                    mapped = (
                        "alchemist + guardian"
                        if legacy == "guardian"
                        else f"{legacy} + standard"
                    )
                    warnings.append(
                        "Project OS schema v1 is supported but should be reviewed "
                        f"for migration to v2 ({mapped})"
                    )
            elif schema_version == "2":
                if config.get("collaboration_style") not in VALID_COLLABORATION:
                    errors.append(
                        "athanor/config.json collaboration_style must be scribe, "
                        "alchemist, or adept"
                    )
                if config.get("assurance_level") not in VALID_ASSURANCE:
                    errors.append(
                        "athanor/config.json assurance_level must be lean, "
                        "standard, or guardian"
                    )
            else:
                errors.append("athanor/config.json schema_version must be 1 or 2")

    project_path = athanor / "PROJECT.md"
    if schema_version == "2" and project_path.is_file():
        project_text = project_path.read_text(encoding="utf-8")
        if "## Project invariants" not in project_text:
            warnings.append("PROJECT.md has no Project invariants section")

    tasks_path = athanor / "TASKS.md"
    if tasks_path.is_file():
        tasks_text = tasks_path.read_text(encoding="utf-8")
        warnings.extend(task_warnings(tasks_text))
        if schema_version == "2" and "## Current handoff" not in tasks_text:
            warnings.append("TASKS.md has no Current handoff section")

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
