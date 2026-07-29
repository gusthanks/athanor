#!/usr/bin/env python3
"""Create a content-free metadata inventory of a project."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
from pathlib import Path


IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
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
SECRET_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "credentials.json",
    "service-account.json",
    "id_rsa",
    "id_ed25519",
}
SECRET_PARTS = ("secret", "credential", "private-key", "private_key", "token")
TEMP_SUFFIXES = {".tmp", ".temp", ".bak", ".swp", ".idlk", ".crdownload"}
CONTEXT_NAMES = {
    "agents.md",
    "agent.md",
    "claude.md",
    "readme.md",
    "project.md",
    "decisions.md",
    "tasks.md",
    "tools.md",
    "integrations.md",
    "roster.md",
    "risks.md",
    "brand.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan project paths and metadata only.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--large-mib", type=int, default=25, help="Large-file threshold in MiB"
    )
    return parser.parse_args()


def iso_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def relative_text(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def looks_sensitive(name: str) -> bool:
    lowered = name.lower()
    return lowered in SECRET_NAMES or any(part in lowered for part in SECRET_PARTS)


def scan(root: Path, large_bytes: int) -> dict:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Project root is not a directory: {root}")

    extension_counts: collections.Counter[str] = collections.Counter()
    top_level_counts: collections.Counter[str] = collections.Counter()
    ignored: collections.Counter[str] = collections.Counter()
    large_files: list[dict[str, object]] = []
    sensitive_paths: list[str] = []
    temporary_paths: list[str] = []
    context_paths: list[str] = []
    nested_repositories: list[str] = []
    errors: list[dict[str, str]] = []
    total_files = 0
    total_bytes = 0

    for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        kept_dirs: list[str] = []
        for directory in sorted(dirs):
            directory_path = current_path / directory
            relative = relative_text(directory_path, root)
            if directory == ".git":
                if current_path != root:
                    nested_repositories.append(relative.rsplit("/", 1)[0])
                ignored[directory] += 1
                continue
            if directory in IGNORED_DIRS:
                ignored[directory] += 1
                continue
            if directory_path.is_symlink():
                ignored["symlink-directory"] += 1
                continue
            kept_dirs.append(directory)
        dirs[:] = kept_dirs

        for filename in sorted(files):
            path = current_path / filename
            if path.is_symlink():
                ignored["symlink-file"] += 1
                continue
            relative = relative_text(path, root)
            try:
                size = path.stat().st_size
            except OSError as exc:
                errors.append({"path": relative, "error": str(exc)})
                continue
            total_files += 1
            total_bytes += size
            extension = path.suffix.lower() or "[no extension]"
            extension_counts[extension] += 1
            first = relative.split("/", 1)[0]
            top_level_counts[first] += 1
            if size >= large_bytes:
                large_files.append({"path": relative, "bytes": size})
            if looks_sensitive(filename):
                sensitive_paths.append(relative)
            if path.suffix.lower() in TEMP_SUFFIXES:
                temporary_paths.append(relative)
            if filename.lower() in CONTEXT_NAMES:
                context_paths.append(relative)

    return {
        "schema_version": "1",
        "generated_at": iso_utc(),
        "root": str(root),
        "content_read": False,
        "summary": {
            "files": total_files,
            "bytes": total_bytes,
            "large_file_threshold_bytes": large_bytes,
        },
        "extension_counts": dict(extension_counts.most_common()),
        "top_level_file_counts": dict(top_level_counts.most_common()),
        "ignored_directories": dict(ignored.most_common()),
        "large_files": sorted(large_files, key=lambda item: (-int(item["bytes"]), str(item["path"]))),
        "sensitive_filename_candidates": sorted(set(sensitive_paths)),
        "temporary_file_candidates": sorted(set(temporary_paths)),
        "context_document_candidates": sorted(set(context_paths)),
        "nested_repository_candidates": sorted(set(nested_repositories)),
        "errors": errors,
        "limitations": [
            "Classification uses paths and metadata only.",
            "Sensitive filenames are warnings; no file content was read.",
            "Absence of an expected filename does not prove a missing capability.",
        ],
    }


def markdown(report: dict) -> str:
    summary = report["summary"]

    def path_list(items: list, empty: str = "None detected.") -> str:
        if not items:
            return empty
        lines = []
        for item in items:
            if isinstance(item, dict):
                lines.append(f"- `{item['path']}` — {item['bytes']} bytes")
            else:
                lines.append(f"- `{item}`")
        return "\n".join(lines)

    return f"""# Athanor Project Scan

Generated: {report['generated_at']}

This is a path-and-metadata inventory. File contents and secret values were not read.

## Summary

- Files: {summary['files']}
- Bytes: {summary['bytes']}
- Large-file threshold: {summary['large_file_threshold_bytes']} bytes

## Context document candidates

{path_list(report['context_document_candidates'])}

## Large files

{path_list(report['large_files'])}

## Sensitive filename candidates

{path_list(report['sensitive_filename_candidates'])}

## Temporary file candidates

{path_list(report['temporary_file_candidates'])}

## Nested repository candidates

{path_list(report['nested_repository_candidates'])}

## Interpretation limits

{path_list(report['limitations'])}
"""


def main() -> int:
    args = parse_args()
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = scan(args.root, args.large_mib * 1024 * 1024)
    (output / "athanor-scan.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output / "athanor-scan.md").write_text(markdown(report), encoding="utf-8")
    print(f"Wrote {output / 'athanor-scan.json'}")
    print(f"Wrote {output / 'athanor-scan.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
