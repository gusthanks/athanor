#!/usr/bin/env python3
"""Install Athanor for Codex, Claude Code, or Google Antigravity."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Sequence


MARKETPLACE_NAME = "athanor-community"
PLUGIN_SELECTOR = f"athanor@{MARKETPLACE_NAME}"
RUNTIME_ADAPTERS = {
    "codex": {
        "display_name": "Codex",
        "kind": "native-plugin",
        "restart_hint": "Start a new Codex thread after refresh.",
    },
    "claude": {
        "display_name": "Claude Code",
        "kind": "skill-directory",
        "target": Path(".claude") / "skills",
        "methods": ("link", "copy"),
        "restart_hint": "Start a new Claude session after source changes.",
    },
    "antigravity": {
        "display_name": "Google Antigravity",
        "kind": "skill-directory",
        "target": Path(".gemini") / "config" / "skills",
        "methods": ("link", "copy"),
        "restart_hint": "Start a new Antigravity session after source changes.",
    },
}
IGNORED_FINGERPRINT_PARTS = {"__pycache__", ".DS_Store"}


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
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallerError(f"Invalid Athanor install registry: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise InstallerError(
            f"Invalid Athanor install registry: {path}: root must be an object"
        )
    return payload


def write_registry(path: Path, payload: dict) -> None:
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def unique_backup_root(target_root: Path) -> Path:
    parent = target_root / ".athanor-backups"
    base = utc_timestamp().replace(":", "").replace("-", "")
    candidate = parent / base
    suffix = 2
    while candidate.exists():
        candidate = parent / f"{base}-{suffix}"
        suffix += 1
    return candidate


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def directory_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root)
        if any(part in IGNORED_FINGERPRINT_PARTS for part in relative.parts):
            continue
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256_file(path)))
    return digest.hexdigest()


def plugin_manifest(repo_root: Path) -> dict:
    path = repo_root / "plugins" / "athanor" / ".codex-plugin" / "plugin.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallerError(f"Invalid Athanor plugin manifest: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise InstallerError(
            f"Invalid Athanor plugin manifest: {path}: root must be an object"
        )
    return payload


def source_metadata(repo_root: Path) -> dict:
    manifest = plugin_manifest(repo_root)
    try:
        completed = command_runner(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"]
        )
    except InstallerError:
        commit = None
    else:
        commit = completed.stdout.strip() if completed.returncode == 0 else None
    return {
        "version": manifest.get("version"),
        "commit": commit,
        "manifest_sha256": sha256_file(
            repo_root / "plugins" / "athanor" / ".codex-plugin" / "plugin.json"
        ),
        "skill_fingerprints": {
            skill.name: directory_fingerprint(skill)
            for skill in discover_skills(repo_root)
        },
    }


def installation_registry_payload(
    runtime: str,
    method: str,
    repo_root: Path,
    installed_at: str | None = None,
) -> dict:
    source = source_metadata(repo_root)
    return {
        "schema_version": "2",
        "runtime": runtime,
        "method": method,
        "source": str(repo_root.resolve()),
        "source_version": source["version"],
        "source_commit": source["commit"],
        "source_manifest_sha256": source["manifest_sha256"],
        "installed_at": installed_at or utc_timestamp(),
        "refreshed_at": utc_timestamp(),
        "skills": sorted(source["skill_fingerprints"]),
        "skill_fingerprints": source["skill_fingerprints"],
    }


def same_location(first: Path, second: Path) -> bool:
    try:
        return first.resolve(strict=True) == second.resolve(strict=True)
    except (FileNotFoundError, OSError):
        return False


def link_points_to(source: Path, destination: Path) -> bool:
    if not path_present(destination):
        return False
    try:
        return destination.resolve(strict=False) == source.resolve(strict=False)
    except OSError:
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
        adapter = RUNTIME_ADAPTERS[runtime]
    except KeyError as exc:
        raise InstallerError(f"Unsupported agent runtime: {runtime}") from exc
    if adapter["kind"] != "skill-directory":
        raise InstallerError(f"Runtime has no skill-directory root: {runtime}")
    return home / adapter["target"]


def agent_status(runtime: str, repo_root: Path, home: Path) -> dict:
    sources = discover_skills(repo_root)
    source_info = source_metadata(repo_root)
    target_root = runtime_root(runtime, home)
    registry_path = target_root / ".athanor-install.json"
    registry = load_registry(registry_path)
    registered_method = registry.get("method")
    registered_skills = set(registry.get("skills", []))
    registered_fingerprints = registry.get("skill_fingerprints", {})
    warnings: list[str] = []
    if registry and registry.get("schema_version") != "2":
        warnings.append(
            "Legacy installation registry lacks version and fingerprint metadata."
        )
    states: list[dict[str, str]] = []
    for skill_source in sources:
        destination = target_root / skill_source.name
        if not path_present(destination):
            state = "missing"
        elif same_location(skill_source, destination):
            state = "linked"
        elif (
            destination.is_dir()
            and registered_method == "copy"
            and skill_source.name in registered_skills
        ):
            current = directory_fingerprint(destination)
            expected = source_info["skill_fingerprints"][skill_source.name]
            registered = registered_fingerprints.get(skill_source.name)
            if registered and current != registered:
                state = "modified-copy"
            elif current != expected:
                state = "stale-copy"
            elif not registered:
                state = "copied-unverified"
            else:
                state = "copied"
        else:
            state = "collision"
        states.append(
            {
                "skill": skill_source.name,
                "state": state,
                "destination": str(destination),
            }
        )
    if any(item["state"] == "copied-unverified" for item in states):
        warnings.append(
            "Copied-skill freshness is unverified; review before refreshing."
        )
    if (
        registry.get("source_version")
        and registry.get("source_version") != source_info["version"]
    ):
        warnings.append(
            "The installation registry references a different source version."
        )
    for name in sorted(registered_skills - set(source_info["skill_fingerprints"])):
        destination = target_root / name
        state = "retired-present" if path_present(destination) else "retired-missing"
        states.append(
            {
                "skill": name,
                "state": state,
                "destination": str(destination),
            }
        )
        warnings.append(
            f"Registered skill {name} no longer exists in the source; refresh "
            "the runtime to retire it safely."
        )
    return {
        "runtime": runtime,
        "target_root": str(target_root),
        "registry": str(registry_path),
        "source_version": source_info["version"],
        "source_commit": source_info["commit"],
        "registered_version": registry.get("source_version"),
        "restart_hint": RUNTIME_ADAPTERS[runtime]["restart_hint"],
        "warnings": warnings,
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
    source_info = source_metadata(repo_root)
    target_root = runtime_root(runtime, home)
    registry_path = target_root / ".athanor-install.json"
    registry = load_registry(registry_path) if target_root.exists() else {}
    registered_method = registry.get("method")
    registered_skills = set(registry.get("skills", []))

    operations: list[dict[str, str]] = []
    collisions: list[str] = []
    unsafe_copies: list[str] = []
    for skill_source in sources:
        destination = target_root / skill_source.name
        if not path_present(destination):
            operations.append(
                {
                    "action": f"create-{method}",
                    "skill": skill_source.name,
                    "destination": str(destination),
                }
            )
        elif same_location(skill_source, destination) and method == "link":
            operations.append(
                {
                    "action": "keep-link",
                    "skill": skill_source.name,
                    "destination": str(destination),
                }
            )
        elif (
            method == "copy"
            and destination.is_dir()
            and registered_method == "copy"
            and skill_source.name in registered_skills
        ):
            if (
                directory_fingerprint(destination)
                != source_info["skill_fingerprints"][skill_source.name]
            ):
                unsafe_copies.append(str(destination))
                continue
            operations.append(
                {
                    "action": "keep-copy",
                    "skill": skill_source.name,
                    "destination": str(destination),
                }
            )
        else:
            collisions.append(str(destination))
    if collisions or unsafe_copies:
        messages = []
        if collisions:
            messages.append(
                "Refusing to overwrite existing skill directories:\n- "
                + "\n- ".join(collisions)
            )
        if unsafe_copies:
            messages.append(
                "Refusing to re-register copied skills whose contents differ "
                "from the source. Review, back up, or uninstall them first:\n- "
                + "\n- ".join(unsafe_copies)
            )
        raise InstallerError(
            "\n".join(messages)
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
            installation_registry_payload(runtime, method, repo_root),
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


def refresh_agent(
    runtime: str,
    repo_root: Path,
    home: Path,
    dry_run: bool = False,
) -> dict:
    sources = discover_skills(repo_root)
    source_by_name = {source.name: source for source in sources}
    target_root = runtime_root(runtime, home)
    registry_path = target_root / ".athanor-install.json"
    registry = load_registry(registry_path)
    if not registry:
        raise InstallerError(
            f"No Athanor install registry found for {runtime}; install it first."
        )
    registered_source_value = registry.get("source")
    registered_source = (
        Path(registered_source_value).expanduser()
        if registered_source_value
        else None
    )
    if registered_source is None or not same_location(registered_source, repo_root):
        raise InstallerError(
            "Refusing to refresh an installation registered to another source: "
            f"{registered_source}"
        )
    method = registry.get("method")
    if method not in {"link", "copy"}:
        raise InstallerError(f"Unsupported registered installation method: {method}")

    registered_skills = set(registry.get("skills", []))
    registered_fingerprints = registry.get("skill_fingerprints", {})
    operations: list[dict[str, str]] = []
    for source in sources:
        destination = target_root / source.name
        if method == "link":
            if not path_present(destination):
                action = "create-link"
            elif link_points_to(source, destination):
                action = "keep-link"
            else:
                raise InstallerError(
                    f"Refusing to repair an unverified link or collision: {destination}"
                )
        else:
            if not path_present(destination):
                action = "add-copy"
            elif source.name not in registered_skills or not destination.is_dir():
                raise InstallerError(
                    f"Refusing to replace an unverified copied skill: {destination}"
                )
            else:
                registered_fingerprint = registered_fingerprints.get(source.name)
                if not registered_fingerprint:
                    raise InstallerError(
                        "Refusing to refresh a legacy copied skill without a "
                        f"content fingerprint: {destination}"
                    )
                if directory_fingerprint(destination) != registered_fingerprint:
                    raise InstallerError(
                        "Refusing to overwrite a copied skill changed after install: "
                        f"{destination}"
                    )
                action = "replace-copy"
        operations.append(
            {
                "action": action,
                "skill": source.name,
                "destination": str(destination),
            }
        )

    for name in sorted(registered_skills - set(source_by_name)):
        destination = target_root / name
        if not path_present(destination):
            action = "already-retired"
        elif method == "link":
            old_source = repo_root / "plugins" / "athanor" / "skills" / name
            if not link_points_to(old_source, destination):
                raise InstallerError(
                    f"Refusing to retire an unverified link: {destination}"
                )
            action = "retire-link"
        else:
            fingerprint = registered_fingerprints.get(name)
            if (
                not fingerprint
                or not destination.is_dir()
                or directory_fingerprint(destination) != fingerprint
            ):
                raise InstallerError(
                    f"Refusing to retire an unverified copied skill: {destination}"
                )
            action = "retire-copy"
        operations.append(
            {
                "action": action,
                "skill": name,
                "destination": str(destination),
            }
        )

    needs_backup = method == "copy" or any(
        operation["action"] == "retire-link" for operation in operations
    )
    backup_root = unique_backup_root(target_root)
    result = {
        "runtime": runtime,
        "mode": "dry-run" if dry_run else "apply",
        "method": method,
        "operations": operations,
        "backup_root": str(backup_root) if needs_backup else None,
        "restart_hint": RUNTIME_ADAPTERS[runtime]["restart_hint"],
    }
    if dry_run:
        return result

    if method == "link":
        created: list[str] = []
        retired: list[tuple[str, Path]] = []
        try:
            if needs_backup:
                backup_root.mkdir(parents=True)
                shutil.copy2(registry_path, backup_root / registry_path.name)
                retired_links = [
                    {
                        "skill": operation["skill"],
                        "target": str(
                            repo_root
                            / "plugins"
                            / "athanor"
                            / "skills"
                            / operation["skill"]
                        ),
                    }
                    for operation in operations
                    if operation["action"] == "retire-link"
                ]
                (backup_root / "retired-links.json").write_text(
                    json.dumps(retired_links, indent=2) + "\n",
                    encoding="utf-8",
                )
            for operation in operations:
                name = operation["skill"]
                destination = target_root / name
                if operation["action"] == "create-link":
                    make_directory_link(source_by_name[name].resolve(), destination)
                    created.append(name)
                elif operation["action"] == "retire-link":
                    old_source = repo_root / "plugins" / "athanor" / "skills" / name
                    remove_directory_link(destination)
                    retired.append((name, old_source))
            write_registry(
                registry_path,
                installation_registry_payload(
                    runtime,
                    method,
                    repo_root,
                    installed_at=registry.get("installed_at"),
                ),
            )
        except Exception:
            for name in reversed(created):
                destination = target_root / name
                if path_present(destination):
                    remove_directory_link(destination)
            for name, old_source in reversed(retired):
                destination = target_root / name
                if not path_present(destination):
                    try:
                        make_directory_link(old_source, destination)
                    except Exception:
                        pass
            raise
        return result

    staging_root = target_root / f".athanor-staging-{os.getpid()}"
    if path_present(staging_root):
        raise InstallerError(f"Refusing to reuse staging directory: {staging_root}")
    applied: list[tuple[str, str]] = []
    try:
        staging_root.mkdir(parents=True)
        for source in sources:
            shutil.copytree(source, staging_root / source.name)
        backup_root.mkdir(parents=True)
        shutil.copy2(registry_path, backup_root / registry_path.name)
        for operation in operations:
            action = operation["action"]
            name = operation["skill"]
            destination = target_root / name
            backup = backup_root / name
            if action == "replace-copy":
                shutil.move(str(destination), str(backup))
                applied.append((action, name))
                shutil.move(str(staging_root / name), str(destination))
            elif action == "add-copy":
                shutil.move(str(staging_root / name), str(destination))
                applied.append((action, name))
            elif action == "retire-copy":
                shutil.move(str(destination), str(backup))
                applied.append((action, name))
        write_registry(
            registry_path,
            installation_registry_payload(
                runtime,
                method,
                repo_root,
                installed_at=registry.get("installed_at"),
            ),
        )
    except Exception:
        for action, name in reversed(applied):
            destination = target_root / name
            backup = backup_root / name
            if action in {"replace-copy", "add-copy"} and destination.is_dir():
                shutil.rmtree(destination)
            if action in {"replace-copy", "retire-copy"} and backup.exists():
                shutil.move(str(backup), str(destination))
        raise
    finally:
        if staging_root.exists():
            shutil.rmtree(staging_root)
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
        source = source_root / "plugins" / "athanor" / "skills" / name
        if not path_present(destination):
            operations.append({"action": "already-missing", "skill": name})
        elif method == "link" and link_points_to(source, destination):
            operations.append({"action": "remove-link", "skill": name})
        elif method == "copy" and source_root.resolve() == repo_root.resolve():
            operations.append({"action": "backup-copy", "skill": name})
        else:
            raise InstallerError(
                f"Refusing to remove unverified destination: {destination}"
            )

    backup_root = unique_backup_root(target_root)
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


def parse_codex_plugin_version(output: str, selector: str) -> str | None:
    columns: tuple[int, int, int] | None = None
    for line in output.splitlines():
        if (
            line.startswith("PLUGIN")
            and "STATUS" in line
            and "VERSION" in line
            and "PATH" in line
        ):
            columns = (
                line.index("STATUS"),
                line.index("VERSION"),
                line.index("PATH"),
            )
            continue
        if columns is None:
            continue
        status_start, version_start, path_start = columns
        if line[:status_start].strip() != selector:
            continue
        return line[version_start:path_start].strip() or None
    return None


def codex_status(
    runner: Callable[..., subprocess.CompletedProcess[str]] = command_runner,
    repo_root: Path | None = None,
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
    installed_version = parse_codex_plugin_version(
        plugins.stdout, PLUGIN_SELECTOR
    )
    source_version = (
        plugin_manifest(repo_root).get("version") if repo_root is not None else None
    )
    fresh = (
        installed_version == source_version
        if installed_version is not None and source_version is not None
        else None
    )
    warnings = []
    if plugin_present and repo_root is not None and installed_version is None:
        warnings.append("Codex did not report the installed plugin version.")
    if fresh is False:
        warnings.append(
            f"Codex has Athanor {installed_version}; source is {source_version}."
        )
    return {
        "runtime": "codex",
        "marketplace": MARKETPLACE_NAME,
        "marketplace_present": marketplace_present,
        "plugin": PLUGIN_SELECTOR,
        "plugin_present": plugin_present,
        "installed_version": installed_version,
        "source_version": source_version,
        "fresh": fresh,
        "warnings": warnings,
        "healthy": (
            marketplace_present
            and plugin_present
            and (repo_root is None or fresh is True)
        ),
    }


def install_codex(
    repo_root: Path,
    runner: Callable[..., subprocess.CompletedProcess[str]] = command_runner,
    dry_run: bool = False,
) -> dict:
    before = codex_status(runner, repo_root)
    operations = []
    if not before["marketplace_present"]:
        operations.append(
            {
                "action": "add-marketplace",
                "command": f"codex plugin marketplace add {repo_root}",
            }
        )
    if not before["plugin_present"] or before["fresh"] is not True:
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
    refreshed = codex_status(runner, repo_root)
    if not refreshed["plugin_present"] or refreshed["fresh"] is not True:
        completed = runner(["codex", "plugin", "add", PLUGIN_SELECTOR])
        if completed.returncode != 0:
            raise InstallerError(
                (completed.stderr or completed.stdout).strip()
                or "Could not install the Athanor plugin."
            )
    result["after"] = codex_status(runner, repo_root)
    return result


def refresh_codex(
    repo_root: Path,
    runner: Callable[..., subprocess.CompletedProcess[str]] = command_runner,
    dry_run: bool = False,
) -> dict:
    before = codex_status(runner, repo_root)
    operations = []
    if not before["marketplace_present"]:
        operations.append(
            {
                "action": "add-marketplace",
                "command": f"codex plugin marketplace add {repo_root}",
            }
        )
    operations.append(
        {"action": "refresh-plugin", "command": f"codex plugin add {PLUGIN_SELECTOR}"}
    )
    result = {
        "runtime": "codex",
        "mode": "dry-run" if dry_run else "apply",
        "source_version": plugin_manifest(repo_root).get("version"),
        "before": before,
        "operations": operations,
        "restart_hint": RUNTIME_ADAPTERS["codex"]["restart_hint"],
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
    completed = runner(["codex", "plugin", "add", PLUGIN_SELECTOR])
    if completed.returncode != 0:
        raise InstallerError(
            (completed.stderr or completed.stdout).strip()
            or "Could not refresh the Athanor plugin."
        )
    result["after"] = codex_status(runner, repo_root)
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


def git_value(repo_root: Path, arguments: Sequence[str]) -> str | None:
    try:
        completed = command_runner(["git", "-C", str(repo_root), *arguments])
    except InstallerError:
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def repository_status(repo_root: Path, check_updates: bool = False) -> dict:
    manifest = plugin_manifest(repo_root)
    skills = discover_skills(repo_root)
    result = {
        "path": str(repo_root),
        "version": manifest.get("version"),
        "skills": len(skills),
        "manifest_sha256": sha256_file(
            repo_root / "plugins" / "athanor" / ".codex-plugin" / "plugin.json"
        ),
        "git": {
            "available": False,
            "branch": None,
            "commit": None,
            "dirty": None,
            "upstream": None,
            "ahead": None,
            "behind": None,
            "update_state": "unknown",
            "candidate_version": None,
            "fetch_attempted": check_updates,
            "fetch_error": None,
        },
        "state": "pass",
        "recommendations": [],
    }
    inside = git_value(repo_root, ["rev-parse", "--is-inside-work-tree"])
    if inside != "true":
        result["state"] = "warning"
        result["recommendations"].append(
            "The canonical source is not a Git checkout; updates must be managed manually."
        )
        return result

    git = result["git"]
    git["available"] = True
    git["branch"] = git_value(repo_root, ["branch", "--show-current"])
    git["commit"] = git_value(repo_root, ["rev-parse", "HEAD"])
    status = command_runner(["git", "-C", str(repo_root), "status", "--porcelain"])
    git["dirty"] = status.returncode != 0 or bool(status.stdout.strip())

    if check_updates:
        try:
            fetched = command_runner(
                ["git", "-C", str(repo_root), "fetch", "--quiet", "--prune"]
            )
        except InstallerError as exc:
            git["fetch_error"] = str(exc)
            result["state"] = "warning"
            result["recommendations"].append(
                "Git is unavailable; remote update metadata was not checked."
            )
            return result
        if fetched.returncode != 0:
            git["fetch_error"] = (fetched.stderr or fetched.stdout).strip()
            result["state"] = "warning"
            result["recommendations"].append(
                "Could not refresh remote update metadata; local status is still valid."
            )

    upstream = git_value(
        repo_root,
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
    )
    git["upstream"] = upstream
    if not upstream:
        git["update_state"] = "no-upstream"
        result["state"] = "warning"
        result["recommendations"].append(
            "Configure an upstream branch before using the guided update lifecycle."
        )
        return result

    counts = git_value(
        repo_root,
        ["rev-list", "--left-right", "--count", f"HEAD...{upstream}"],
    )
    if counts:
        left, right = counts.split()
        git["ahead"], git["behind"] = int(left), int(right)
        if git["ahead"] and git["behind"]:
            git["update_state"] = "diverged"
            result["state"] = "warning"
            result["recommendations"].append(
                "The source diverged from its upstream; do not update automatically."
            )
        elif git["behind"]:
            git["update_state"] = "behind"
            result["state"] = "warning"
            if git["dirty"]:
                result["recommendations"].append(
                    "Commit or preserve local changes before reviewing an update."
                )
            else:
                result["recommendations"].append(
                    "Review changes, then use git pull --ff-only."
                )
        elif git["ahead"]:
            git["update_state"] = "ahead"
        else:
            git["update_state"] = "up-to-date"

    candidate = command_runner(
        [
            "git",
            "-C",
            str(repo_root),
            "show",
            f"{upstream}:plugins/athanor/.codex-plugin/plugin.json",
        ]
    )
    if candidate.returncode == 0:
        try:
            git["candidate_version"] = json.loads(candidate.stdout).get("version")
        except json.JSONDecodeError:
            result["state"] = "warning"
            result["recommendations"].append(
                "The upstream plugin manifest could not be validated."
            )
    return result


def project_os_status(repo_root: Path, project_root: Path | None) -> dict | None:
    if project_root is None:
        return None
    validator_path = (
        repo_root
        / "plugins"
        / "athanor"
        / "skills"
        / "athanor-maintain"
        / "scripts"
        / "validate_project_os.py"
    )
    spec = importlib.util.spec_from_file_location(
        "athanor_validate_project_os", validator_path
    )
    if not spec or not spec.loader:
        raise InstallerError(f"Could not load project validator: {validator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate(project_root)


def doctor(
    target: str,
    repo_root: Path,
    home: Path,
    project_root: Path | None = None,
    check_updates: bool = False,
) -> dict:
    runtime_results = []
    for runtime in expand_targets(target):
        try:
            status = (
                codex_status(repo_root=repo_root)
                if runtime == "codex"
                else agent_status(runtime, repo_root, home)
            )
        except InstallerError as exc:
            status = {
                "runtime": runtime,
                "healthy": False,
                "error": str(exc),
            }
        runtime_results.append(status)
    repository = repository_status(repo_root, check_updates=check_updates)
    project = project_os_status(repo_root, project_root)
    healthy = (
        repository["state"] != "fail"
        and all(item.get("healthy", False) for item in runtime_results)
        and (project is None or project.get("valid", False))
    )
    return {
        "runtime": "doctor",
        "healthy": healthy,
        "repository": repository,
        "runtimes": runtime_results,
        "project": project,
    }


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
        "--action",
        choices=("install", "status", "refresh", "doctor", "uninstall"),
        default="install",
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
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Optional Athanor-enabled project to include in doctor output",
    )
    parser.add_argument(
        "--check-updates",
        action="store_true",
        help="Fetch remote metadata during doctor without changing the working tree",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.expanduser().resolve()
    home = args.home.expanduser().resolve()
    results = []
    try:
        if args.action == "doctor":
            result = doctor(
                args.target,
                repo_root,
                home,
                project_root=(
                    args.project_root.expanduser().resolve()
                    if args.project_root
                    else None
                ),
                check_updates=args.check_updates,
            )
            print(json.dumps({"ok": True, "results": [result]}, indent=2))
            return 0 if result["healthy"] else 1
        for runtime in expand_targets(args.target):
            if runtime == "codex":
                if args.action == "status":
                    result = codex_status(repo_root=repo_root)
                elif args.action == "install":
                    result = install_codex(repo_root, dry_run=args.dry_run)
                elif args.action == "refresh":
                    result = refresh_codex(repo_root, dry_run=args.dry_run)
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
            elif args.action == "refresh":
                result = refresh_agent(
                    runtime,
                    repo_root,
                    home,
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
