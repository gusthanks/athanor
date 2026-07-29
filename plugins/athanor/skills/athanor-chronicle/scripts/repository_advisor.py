#!/usr/bin/env python3
"""Classify repository candidates conservatively using paths and metadata."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
from pathlib import Path


IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "vendor",
    "coverage",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".cache",
    ".pytest_cache",
}
LOCAL_DIRS = {"node_modules", "dist", "build", "coverage", ".cache", "__pycache__"}
LOCAL_SUFFIXES = {".tmp", ".temp", ".log", ".swp", ".idlk", ".crdownload"}
SECRET_EXACT = {
    ".env",
    ".env.local",
    ".env.production",
    "credentials.json",
    "service-account.json",
    "id_rsa",
    "id_ed25519",
}
SECRET_PARTS = ("secret", "credential", "private-key", "private_key", "token")
LFS_SUFFIXES = {
    ".7z",
    ".aep",
    ".ai",
    ".blend",
    ".c4d",
    ".fig",
    ".indd",
    ".kra",
    ".mov",
    ".mp3",
    ".mp4",
    ".pdf",
    ".psb",
    ".psd",
    ".sketch",
    ".wav",
    ".zip",
}
ASSET_SUFFIXES = {
    ".avi",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".raw",
    ".wav",
    ".webm",
}
NORMAL_SUFFIXES = {
    ".c",
    ".cpp",
    ".css",
    ".csv",
    ".go",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".svg",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a metadata-only repository candidate report."
    )
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--lfs-mib", type=int, default=10)
    return parser.parse_args()


def utc_timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def sensitive_name(name: str) -> bool:
    lowered = name.lower()
    return lowered in SECRET_EXACT or any(part in lowered for part in SECRET_PARTS)


def classify(relative: Path, size: int, lfs_bytes: int) -> tuple[str, str]:
    filename = relative.name.lower()
    suffix = relative.suffix.lower()
    parts = {part.lower() for part in relative.parts[:-1]}
    if filename == ".env.example":
        return "git_normal_candidate", "safe environment-variable name template"
    if sensitive_name(filename):
        return "secret_manager_or_human_review", "sensitive filename indicator"
    if parts & LOCAL_DIRS or suffix in LOCAL_SUFFIXES:
        return "local_ignored", "generated, temporary, cache, or local artifact"
    if suffix in ASSET_SUFFIXES:
        return "asset_storage_or_lfs", "heavy media or source asset"
    if size >= lfs_bytes or suffix in LFS_SUFFIXES:
        return "git_lfs_candidate", "large or binary working format"
    if suffix in NORMAL_SUFFIXES or filename in {
        ".gitignore",
        ".gitattributes",
        ".editorconfig",
        "dockerfile",
        "makefile",
        "license",
    }:
        return "git_normal_candidate", "text, code, configuration, or small canonical asset"
    return "human_review", "format or business sensitivity needs context"


def advise(root: Path, lfs_bytes: int) -> dict:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Project root is not a directory: {root}")
    groups: dict[str, list[dict[str, object]]] = collections.defaultdict(list)
    skipped: collections.Counter[str] = collections.Counter()
    errors: list[dict[str, str]] = []
    for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        next_dirs = []
        for directory in sorted(dirs):
            child = current_path / directory
            if directory in IGNORED_DIRS:
                skipped[directory] += 1
            elif child.is_symlink():
                skipped["symlink-directory"] += 1
            else:
                next_dirs.append(directory)
        dirs[:] = next_dirs
        for filename in sorted(files):
            path = current_path / filename
            relative = path.relative_to(root)
            if path.is_symlink():
                skipped["symlink-file"] += 1
                continue
            try:
                size = path.stat().st_size
            except OSError as exc:
                errors.append({"path": relative.as_posix(), "error": str(exc)})
                continue
            group, reason = classify(relative, size, lfs_bytes)
            groups[group].append(
                {"path": relative.as_posix(), "bytes": size, "reason": reason}
            )
    return {
        "schema_version": "1",
        "generated_at": utc_timestamp(),
        "root": str(root),
        "content_read": False,
        "repository_state": {
            "git_directory": (root / ".git").exists(),
            "gitignore": (root / ".gitignore").exists(),
            "gitattributes": (root / ".gitattributes").exists(),
        },
        "lfs_threshold_bytes": lfs_bytes,
        "groups": {
            name: sorted(items, key=lambda item: str(item["path"]))
            for name, items in sorted(groups.items())
        },
        "skipped_directories": dict(skipped),
        "errors": errors,
        "limitations": [
            "Classification uses filenames, extensions, paths, and size only.",
            "No secret-file content or business sensitivity was inspected.",
            "Git is history and collaboration; it is not a complete backup strategy.",
            "All candidates require review before staging or publishing.",
        ],
    }


def markdown(report: dict) -> str:
    lines = [
        "# Athanor Repository Advice",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "This metadata-only report proposes candidates; it does not stage, commit, "
        "publish, or read file contents.",
        "",
        "## Repository state",
        "",
    ]
    for key, value in report["repository_state"].items():
        lines.append(f"- {key}: {'yes' if value else 'no'}")
    for group, items in report["groups"].items():
        lines.extend(["", f"## {group.replace('_', ' ').title()}", ""])
        if not items:
            lines.append("None detected.")
        for item in items:
            lines.append(
                f"- `{item['path']}` — {item['bytes']} bytes — {item['reason']}"
            )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = advise(args.root, args.lfs_mib * 1024 * 1024)
    (output / "repository-advice.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output / "repository-advice.md").write_text(markdown(report), encoding="utf-8")
    print(f"Wrote {output / 'repository-advice.json'}")
    print(f"Wrote {output / 'repository-advice.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
