#!/usr/bin/env python3
"""Install Athanor for Codex, Claude Code, or Google Antigravity."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Sequence


MARKETPLACE_NAME = "athanor-community"
PLUGIN_SELECTOR = f"athanor@{MARKETPLACE_NAME}"
AGENT_TARGETS = {
    "claude": Path(".claude") / "skills",
    "antigravity": Path(".gemini") / "config" / "skills",
}


class InstallerError(RuntimeError):
    """A safe installation cannot continue."""


def utc_timestamp() -> str:
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def command_runner(
    arguments: Sequence[str], *, check: bool = False
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            list(arguments),
            check=check,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        raise InstallerError(f"Required command is unavailable: {arguments[0]}") from exc


def load_registry(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallerError(f"Invalid Athanor install registry: {path}: {exc}") from exc


def write_registry(path: Path, payload: dict) -> None:
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def discover_skills(repo_root: Path) -> list[Path]:
    skill_root = repo_root / "plugins" / "athanor" / "skills"
    if not skill_root.is_dir():
        raise InstallerError(f"Athanor skills directory not found: {skill_root}")
    skills = sorted(
        path for path in skill_root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file()
    )
    if not skills:
        raise InstallerError(f"No skills found under: {skill_root}")
    return skills


def same_location(first: Path, second: Path) -> bool:
    try:
        return first.resolve(strict=True) == second.resolve(strict=True)
    except (FileNotFoundError, OSError):
        return False


def path_present(path: Path) -> bool:
    return os.path.lexists(path)


def make_directory_link(source: Path, destination: Path) -> None:
    if os.name == "nt":
        result = command_runner(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(destination), str(source)]
        )
        if result.returncode != 0:
            message = (result.stderr or result.stdout).strip()
            raise InstallerError(
                f"Could not create directory junction {destination}: {message}"
            )
    else:
        destination.symlink_to(source, target_is_directory=True)


def remove_directory_link(path: Path) -> None:
    if os.path.islink(path):
        path.unlink()
        return
    if os.name == "nt":
        os.rmdir(path)
        return
    raise InstallerError(f"Refusing to remove a non-link directory: {path}")


def runtime_root(runtime: str, home: Path) -> Path:
    try:
        relative = AGENT_TARGETS[runtime]
    except KeyError as exc:
        raise InstallerError(f"Unsupported agent runtime: {runtime}") from exc
    return home / relative


def agent_status(runtime: str, repo_root: Path, home: Path) -> dict:
    sources = discover_skills(repo_root)
    target_root = runtime_root(runtime, home)
    registry_path = target_root / ".athanor-install.json"
    registry = load_registry(registry_path)
    registered_method = registry.get("method")
    registered_skills = set(registry.get("skills", []))
    states: list[dict[str, str]] = []
    for source in sources:
        destination = target_root / source.name
        if not path_present(destination):
            state = "missing"
        elif same_location(source, destination):
            state = "linked"
        elif (
            destination.is_dir()
            and registered_method == "copy"
            and source.name in registered_skills
        ):
            state = "copied"
        else:
            state = "collision"
        states.append(
            {
                "skill": source.name,
                "state": state,
                "destination": str(destination),
            }
        )
    return {
        "runtime": runtime,
        "target_root": str(target_root),
        "registry": str(registry_path),
        "skills": states,
        "healthy": all(item["state"] in {"linked", "copied"} for item in states),
    }


def install_agent(
    runtime: str,
    repo_root: Path,
    home: Path,
    method: str,
    dry_run: bool = False,
) -> dict:
    sources = discover_skills(repo_root)
    target_root = runtime_root(runtime, home)
    registry_path = target_root / ".athanor-install.json"
    registry = load_registry(registry_path) if target_root.exists() else {}
    registered_method = registry.get("method")
    registered_skills = set(registry.get("skills", []))

    operations: list[dict[str, str]] = []
    collisions: list[str] = []
    for source in sources:
        destination = target_root / source.name
        if not path_present(destination):
            operations.append(
                {
                    "action": f"create-{method}",
                    "skill": source.name,
                    "destination": str(destination),
                }
            )
        elif same_location(source, destination) and method == "link":
            operations.append(
                {
                    "action": "keep-link",
                    "skill": source.name,
                    "destination": str(destination),
                }
            )
        elif (
            method == "copy"
            and destination.is_dir()
            and registered_method == "copy"
            and source.name in registered_skills
        ):
            operations.append(
                {
                    "action": "keep-copy",
                    "skill": source.name,
                    "destination": str(destination),
                }
            )
        else:
            collisions.append(str(destination))
    if collisions:
        raise InstallerError(
            "Refusing to overwrite existing skill directories:\n- "
            + "\n- ".join(collisions)
        )

    result = {
        "runtime": runtime,
        "mode": "dry-run" if dry_run else "apply",
        "method": method,
        "target_root": str(target_root),
        "operations": operations,
    }
    if dry_run:
        return result

    target_root.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    try:
        for source, operation in zip(sources, operations):
            if operation["action"].startswith("keep-"):
                continue
            destination = target_root / source.name
            if method == "link":
                make_directory_link(source.resolve(), destination)
            else:
                shutil.copytree(source, destination)
            created.append(destination)
        write_registry(
            registry_path,
            {
                "schema_version": "1",
                "runtime": runtime,
                "method": method,
                "source": str(repo_root.resolve()),
                "installed_at": utc_timestamp(),
                "skills": [path.name for path in sources],
            },
        )
    except Exception:
        for destination in reversed(created):
            try:
                if method == "link":
                    remove_directory_link(destination)
                else:
                    shutil.rmtree(destination)
            except OSError:
                pass
        raise
    return result


def uninstall_agent(
    runtime: str,
    repo_root: Path,
    home: Path,
    confirmed: bool,
    dry_run: bool = False,
) -> dict:
    target_root = runtime_root(runtime, home)
    registry_path = target_root / ".athanor-install.json"
    registry = load_registry(registry_path)
    if not registry:
        return {
            "runtime": runtime,
            "mode": "dry-run" if dry_run else "apply",
            "operations": [],
            "message": "No Athanor install registry found.",
        }
    if not confirmed and not dry_run:
        raise InstallerError("Uninstall requires --yes")

    source_root = Path(registry.get("source", "")).expanduser()
    method = registry.get("method")
    skills = registry.get("skills", [])
    operations: list[dict[str, str]] = []
    for name in skills:
        destination = target_root / name
        source = repo_root / "plugins" / "athanor" / "skills" / name
        if not path_present(destination):
            operations.append({"action": "already-missing", "skill": name})
        elif method == "link" and same_location(source, destination):
            operations.append({"action": "remove-link", "skill": name})
        elif method == "copy" and source_root.resolve() == repo_root.resolve():
            operations.append({"action": "backup-copy", "skill": name})
        else:
            raise InstallerError(
                f"Refusing to remove unverified destination: {destination}"
            )

    backup_root = (
        target_root
        / ".athanor-backups"
        / utc_timestamp().replace(":", "").replace("-", "")
    )
    result = {
        "runtime": runtime,
        "mode": "dry-run" if dry_run else "apply",
        "method": method,
        "operations": operations,
        "backup_root": str(backup_root) if method == "copy" else None,
    }
    if dry_run:
        return result

    for operation in operations:
        destination = target_root / operation["skill"]
        if operation["action"] == "remove-link":
            remove_directory_link(destination)
        elif operation["action"] == "backup-copy":
            backup_root.mkdir(parents=True, exist_ok=True)
            shutil.move(str(destination), str(backup_root / destination.name))
    if method == "copy":
        backup_root.mkdir(parents=True, exist_ok=True)
        shutil.move(str(registry_path), str(backup_root / registry_path.name))
    elif registry_path.exists():
        registry_path.unlink()
    return result


def codex_status(
    runner: Callable[..., subprocess.CompletedProcess[str]] = command_runner,
) -> dict:
    marketplaces = runner(["codex", "plugin", "marketplace", "list"])
    plugins = runner(["codex", "plugin", "list"])
    marketplace_present = any(
        line.split(maxsplit=1)[0] == MARKETPLACE_NAME
        for line in marketplaces.stdout.splitlines()
        if line.strip() and not line.startswith("MARKETPLACE")
    )
    plugin_present = any(
        line.split(maxsplit=1)[0] == PLUGIN_SELECTOR
        for line in plugins.stdout.splitlines()
        if line.strip() and not line.startswith("PLUGIN")
    )
    return {
        "runtime": "codex",
        "marketplace": MARKETPLACE_NAME,
        "marketplace_present": marketplace_present,
        "plugin": PLUGIN_SELECTOR,
        "plugin_present": plugin_present,
        "healthy": marketplace_present and plugin_present,
    }


def install_codex(
    repo_root: Path,
    runner: Callable[..., subprocess.CompletedProcess[str]] = command_runner,
    dry_run: bool = False,
) -> dict:
    before = codex_status(runner)
    operations = []
    if not before["marketplace_present"]:
        operations.append(
            {
                "action": "add-marketplace",
                "command": f"codex plugin marketplace add {repo_root}",
            }
        )
    if not before["plugin_present"]:
        operations.append(
            {"action": "add-plugin", "command": f"codex plugin add {PLUGIN_SELECTOR}"}
        )
    result = {
        "runtime": "codex",
        "mode": "dry-run" if dry_run else "apply",
        "before": before,
        "operations": operations,
    }
    if dry_run:
        return result
    if not before["marketplace_present"]:
        completed = runner(
            ["codex", "plugin", "marketplace", "add", str(repo_root.resolve())]
        )
        if completed.returncode != 0:
            raise InstallerError(
                (completed.stderr or completed.stdout).strip()
                or "Could not add the Athanor marketplace."
            )
    refreshed = codex_status(runner)
    if not refreshed["plugin_present"]:
        completed = runner(["codex", "plugin", "add", PLUGIN_SELECTOR])
        if completed.returncode != 0:
            raise InstallerError(
                (completed.stderr or completed.stdout).strip()
                or "Could not install the Athanor plugin."
            )
    result["after"] = codex_status(runner)
    return result


def uninstall_codex(
    confirmed: bool,
    runner: Callable[..., subprocess.CompletedProcess[str]] = command_runner,
    dry_run: bool = False,
) -> dict:
    before = codex_status(runner)
    operations = (
        [{"action": "remove-plugin", "command": f"codex plugin remove {PLUGIN_SELECTOR}"}]
        if before["plugin_present"]
        else []
    )
    result = {
        "runtime": "codex",
        "mode": "dry-run" if dry_run else "apply",
        "before": before,
        "operations": operations,
    }
    if dry_run or not operations:
        return result
    if not confirmed:
        raise InstallerError("Uninstall requires --yes")
    completed = runner(["codex", "plugin", "remove", PLUGIN_SELECTOR])
    if completed.returncode != 0:
        raise InstallerError(
            (completed.stderr or completed.stdout).strip()
            or "Could not uninstall the Athanor plugin."
        )
    result["after"] = codex_status(runner)
    return result


def expand_targets(target: str) -> list[str]:
    if target == "all":
        return ["codex", "claude", "antigravity"]
    if target == "agents":
        return ["claude", "antigravity"]
    return [target]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install one canonical Athanor source across supported AI runtimes."
    )
    parser.add_argument(
        "--target",
        choices=("codex", "claude", "antigravity", "agents", "all"),
        required=True,
    )
    parser.add_argument(
        "--action", choices=("install", "status", "uninstall"), default="install"
    )
    parser.add_argument("--method", choices=("link", "copy"), default="link")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.expanduser().resolve()
    home = args.home.expanduser().resolve()
    results = []
    try:
        for runtime in expand_targets(args.target):
            if runtime == "codex":
                if args.action == "status":
                    result = codex_status()
                elif args.action == "install":
                    result = install_codex(repo_root, dry_run=args.dry_run)
                else:
                    result = uninstall_codex(args.yes, dry_run=args.dry_run)
            elif args.action == "status":
                result = agent_status(runtime, repo_root, home)
            elif args.action == "install":
                result = install_agent(
                    runtime,
                    repo_root,
                    home,
                    args.method,
                    dry_run=args.dry_run,
                )
            else:
                result = uninstall_agent(
                    runtime,
                    repo_root,
                    home,
                    args.yes,
                    dry_run=args.dry_run,
                )
            results.append(result)
    except InstallerError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2
    print(json.dumps({"ok": True, "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
