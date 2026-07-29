#!/usr/bin/env python3
"""Create and inspect append-only Athanor session checkpoints."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
from pathlib import Path


SAFE_SLUG = re.compile(r"[^a-z0-9]+")
SECRET_PATTERNS = (
    re.compile(
        r"(?i)\b[\w-]*(secret|token|password|credential|api[_-]?key|private[_-]?key)"
        r"[\w-]*\s*[:=]\s*\S+"
    ),
    re.compile(r"(?i)\bauthorization\s*:\s*(bearer|basic)\s+\S+"),
    re.compile(
        r"\b(AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|"
        r"sk-[A-Za-z0-9_-]{20,})\b"
    ),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


def utc_timestamp() -> str:
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def filename_timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%M%S.%fZ")


def slugify(value: str) -> str:
    value = SAFE_SLUG.sub("-", value.lower()).strip("-")
    return value[:48] or "checkpoint"


def git_value(root: Path, *arguments: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def reject_secrets(values: list[str]) -> None:
    for value in values:
        if any(pattern.search(value) for pattern in SECRET_PATTERNS):
            raise ValueError(
                "Checkpoint text resembles a credential; store only safe names "
                "and metadata."
            )


def bullets(values: list[str], empty: str = "None recorded.") -> str:
    if not values:
        return f"- {empty}"
    return "\n".join(f"- {value}" for value in values)


def require_contained(root: Path, path: Path) -> Path:
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(
            f"Refusing to follow a path outside the project root: {path} -> "
            f"{resolved}"
        ) from exc
    return resolved


def checkpoint_directory(root: Path, create: bool = False) -> Path:
    root = root.expanduser().resolve()
    athanor = root / "athanor"
    if not athanor.is_dir():
        raise FileNotFoundError("Missing athanor/ project directory")
    require_contained(root, athanor)
    checkpoint_root = athanor / "checkpoints"
    require_contained(root, checkpoint_root)
    if create:
        checkpoint_root.mkdir(parents=True, exist_ok=True)
        require_contained(root, checkpoint_root)
    return checkpoint_root


def save_checkpoint(root: Path, args: argparse.Namespace) -> dict:
    root = root.expanduser().resolve()
    all_values = [
        args.goal,
        args.next_action,
        args.slug or "",
        *args.completed,
        *args.remaining,
        *args.blocker,
        *args.decision,
        *args.task,
        *args.path,
        *args.verification,
    ]
    reject_secrets(all_values)

    created = utc_timestamp()
    compact = filename_timestamp()
    checkpoint_root = checkpoint_directory(root, create=True)
    base = f"{compact}-{slugify(args.slug or args.goal)}"
    branch = git_value(root, "branch", "--show-current") or "not-applicable"
    commit = git_value(root, "rev-parse", "HEAD") or "not-applicable"
    content = (
        f"# Athanor Checkpoint — {args.goal}\n\n"
        f"- Created: {created}\n"
        f"- Branch: {branch}\n"
        f"- Commit: {commit}\n\n"
        "## Goal\n\n"
        f"{args.goal}\n\n"
        "## Completed\n\n"
        f"{bullets(args.completed)}\n\n"
        "## Decisions\n\n"
        f"{bullets(args.decision)}\n\n"
        "## Tasks\n\n"
        f"{bullets(args.task)}\n\n"
        "## Verification\n\n"
        f"{bullets(args.verification)}\n\n"
        "## Remaining\n\n"
        f"{bullets(args.remaining)}\n\n"
        "## Blockers\n\n"
        f"{bullets(args.blocker)}\n\n"
        "## Relevant paths\n\n"
        f"{bullets(args.path)}\n\n"
        "## Exact next action\n\n"
        f"{args.next_action}\n"
    )
    suffix = 1
    while True:
        label = f"{base}-{suffix:04d}"
        destination = checkpoint_root / f"{label}.md"
        try:
            with destination.open("x", encoding="utf-8", errors="strict") as handle:
                handle.write(content)
        except FileExistsError:
            suffix += 1
            continue
        break
    return {
        "action": "save",
        "path": str(destination),
        "created": created,
        "branch": branch,
        "commit": commit,
    }


def list_checkpoints(root: Path) -> dict:
    root = root.expanduser().resolve()
    athanor = root / "athanor"
    if not athanor.is_dir():
        checkpoint_root = athanor / "checkpoints"
        return {
            "action": "list",
            "root": str(checkpoint_root),
            "checkpoints": [],
        }
    require_contained(root, athanor)
    checkpoint_root = athanor / "checkpoints"
    require_contained(root, checkpoint_root)
    checkpoints = []
    if checkpoint_root.is_dir():
        resolved_root = checkpoint_root.resolve()
        for path in checkpoint_root.glob("*.md"):
            if path.is_symlink() or not path.is_file():
                continue
            try:
                resolved = path.resolve(strict=True)
            except OSError:
                continue
            if resolved.parent == resolved_root:
                checkpoints.append(path)
        checkpoints.sort(key=lambda path: path.name, reverse=True)
    return {
        "action": "list",
        "root": str(checkpoint_root),
        "checkpoints": [str(path) for path in checkpoints],
    }


def restore_checkpoint(root: Path, selected: Path | None) -> dict:
    root = root.expanduser().resolve()
    checkpoints = list_checkpoints(root)["checkpoints"]
    if selected is None:
        if not checkpoints:
            raise FileNotFoundError("No Athanor checkpoints found")
        path = Path(checkpoints[0]).resolve(strict=True)
    else:
        lexical = selected.expanduser()
        if lexical.is_symlink():
            raise ValueError("Checkpoint symlinks are not accepted")
        path = lexical.resolve()
        checkpoint_root = (root / "athanor" / "checkpoints").resolve()
        if path.parent != checkpoint_root:
            raise ValueError("Checkpoint must be directly inside athanor/checkpoints")
        if not path.is_file():
            raise FileNotFoundError(f"Checkpoint not found: {path}")

    text = path.read_text(encoding="utf-8")
    branch_match = re.search(r"^- Branch: (.+)$", text, re.MULTILINE)
    commit_match = re.search(r"^- Commit: (.+)$", text, re.MULTILINE)
    current_branch = git_value(root, "branch", "--show-current") or "not-applicable"
    current_commit = git_value(root, "rev-parse", "HEAD") or "not-applicable"
    warnings = []
    if branch_match and branch_match.group(1) != current_branch:
        warnings.append(
            f"Checkpoint branch is {branch_match.group(1)}; current branch is "
            f"{current_branch}."
        )
    if commit_match and commit_match.group(1) != current_commit:
        warnings.append("Repository commit changed after this checkpoint.")
    return {
        "action": "restore",
        "path": str(path),
        "current_branch": current_branch,
        "current_commit": current_commit,
        "warnings": warnings,
        "content": text,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or inspect append-only Athanor checkpoints."
    )
    parser.add_argument("root", type=Path, help="Project root")
    subparsers = parser.add_subparsers(dest="action", required=True)

    save = subparsers.add_parser("save")
    save.add_argument("--goal", required=True)
    save.add_argument("--next-action", required=True)
    save.add_argument("--slug")
    for option in (
        "completed",
        "remaining",
        "blocker",
        "decision",
        "task",
        "path",
        "verification",
    ):
        save.add_argument(f"--{option}", action="append", default=[])

    subparsers.add_parser("list")
    restore = subparsers.add_parser("restore")
    restore.add_argument("--checkpoint", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.action == "save":
            result = save_checkpoint(args.root, args)
        elif args.action == "list":
            result = list_checkpoints(args.root)
        else:
            result = restore_checkpoint(args.root, args.checkpoint)
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2
    print(json.dumps({"ok": True, "result": result}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
