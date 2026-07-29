#!/usr/bin/env python3
"""Preview or create Athanor project-memory files without overwriting anything."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


MODES = ("scribe", "alchemist", "adept", "guardian")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview or create a non-destructive Athanor project scaffold."
    )
    parser.add_argument("root", type=Path, help="Project root")
    parser.add_argument("--name", required=True, help="Human-readable project name")
    parser.add_argument("--mode", choices=MODES, default="alchemist")
    parser.add_argument(
        "--apply", action="store_true", help="Create missing files and directories"
    )
    return parser.parse_args()


def render_template(source: Path, project_name: str, mode: str) -> str:
    text = source.read_text(encoding="utf-8")
    return (
        text.replace("{{PROJECT_NAME}}", project_name)
        .replace("{{DATE}}", dt.date.today().isoformat())
        .replace("{{MODE}}", mode)
    )


def scaffold(root: Path, project_name: str, mode: str, apply: bool) -> dict:
    root = root.expanduser().resolve()
    template_root = Path(__file__).resolve().parent.parent / "assets" / "project-os"
    if not template_root.is_dir():
        raise FileNotFoundError(f"Template directory not found: {template_root}")
    if root.exists() and not root.is_dir():
        raise NotADirectoryError(f"Project root is not a directory: {root}")

    operations: list[dict[str, str]] = []
    conflicts: list[str] = []
    for source in sorted(path for path in template_root.rglob("*") if path.is_file()):
        relative = source.relative_to(template_root)
        target = root / relative
        if target.exists():
            operations.append(
                {"action": "skip", "path": relative.as_posix(), "reason": "exists"}
            )
            conflicts.append(relative.as_posix())
            continue
        operations.append({"action": "create", "path": relative.as_posix()})
        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render_template(source, project_name, mode), encoding="utf-8")

    for relative_dir in ("athanor/agents", "athanor/memory"):
        target_dir = root / relative_dir
        action = "skip" if target_dir.exists() else "create-directory"
        operations.append({"action": action, "path": relative_dir})
        if apply and not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)

    merge_note = "athanor/BOOTSTRAP-MERGE.md"
    if conflicts and apply:
        note_path = root / merge_note
        if not note_path.exists():
            note_path.parent.mkdir(parents=True, exist_ok=True)
            listed = "\n".join(f"- `{item}`" for item in conflicts)
            note_path.write_text(
                "# Bootstrap Merge Review\n\n"
                f"Created: {dt.date.today().isoformat()}\n\n"
                "Athanor preserved the following existing files. Review them and merge "
                "missing concepts manually; do not replace their project-specific rules.\n\n"
                f"{listed}\n",
                encoding="utf-8",
            )
            operations.append({"action": "create", "path": merge_note})
        else:
            operations.append(
                {"action": "skip", "path": merge_note, "reason": "exists"}
            )

    return {
        "mode": "apply" if apply else "preview",
        "root": str(root),
        "project_name": project_name,
        "collaboration_mode": mode,
        "operations": operations,
        "summary": {
            "create": sum(
                item["action"] in {"create", "create-directory"} for item in operations
            ),
            "skip": sum(item["action"] == "skip" for item in operations),
        },
    }


def main() -> int:
    args = parse_args()
    result = scaffold(args.root, args.name.strip(), args.mode, args.apply)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
