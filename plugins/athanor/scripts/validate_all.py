#!/usr/bin/env python3
"""Portable structural validation for the Athanor plugin source tree."""

from __future__ import annotations

import json
import py_compile
import re
import sys
from pathlib import Path


FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
NAME = re.compile(r"^name:\s*(\S+)\s*$", re.MULTILINE)
DESCRIPTION = re.compile(r"^description:\s*(.+)\s*$", re.MULTILINE)


def main() -> int:
    plugin_root = Path(__file__).resolve().parent.parent
    failures: list[str] = []
    skills = sorted((plugin_root / "skills").glob("*/SKILL.md"))
    if not skills:
        failures.append("No skills found")
    for skill_file in skills:
        text = skill_file.read_text(encoding="utf-8")
        match = FRONTMATTER.match(text)
        if not match:
            failures.append(f"{skill_file}: missing YAML frontmatter")
            continue
        frontmatter = match.group(1)
        if not NAME.search(frontmatter):
            failures.append(f"{skill_file}: missing name")
        if not DESCRIPTION.search(frontmatter):
            failures.append(f"{skill_file}: missing single-line description")
        yaml_path = skill_file.parent / "agents" / "openai.yaml"
        if not yaml_path.is_file():
            failures.append(f"{skill_file.parent}: missing agents/openai.yaml")

    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"Invalid plugin manifest: {exc}")
    else:
        for key in ("name", "version", "description", "license", "skills"):
            if not manifest.get(key):
                failures.append(f"Plugin manifest missing {key}")

    repository_root = plugin_root.parents[1]
    scripts = (
        sorted(plugin_root.glob("skills/*/scripts/*.py"))
        + sorted((repository_root / "scripts").glob("*.py"))
        + [Path(__file__).resolve()]
    )
    for script in scripts:
        try:
            py_compile.compile(str(script), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append(f"{script}: {exc}")

    if failures:
        print("Athanor validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        f"Athanor validation passed: {len(skills)} skills, "
        f"{len(scripts)} Python scripts, valid plugin manifest."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
