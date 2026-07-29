#!/usr/bin/env python3
"""Validate, simulate, or apply an approved file-movement plan."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import shutil
from pathlib import Path, PurePosixPath


REQUIRED_COLUMNS = {
    "id",
    "action",
    "source",
    "destination",
    "reason",
    "confidence",
    "risk",
    "approved",
}
TRUE_VALUES = {"true", "yes", "1", "approved"}
HIGH_RISK_EXTENSIONS = {
    ".aep",
    ".ai",
    ".blend",
    ".c4d",
    ".fig",
    ".indd",
    ".kra",
    ".psb",
    ".psd",
    ".sketch",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run by default; move approved rows only when explicitly applied."
    )
    parser.add_argument("root", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--ack-backup", action="store_true")
    parser.add_argument(
        "--allow-high-risk",
        action="store_true",
        help="Acknowledge movement of high-risk editable binary formats",
    )
    parser.add_argument("--ledger", type=Path)
    return parser.parse_args()


def utc_timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_target(root: Path, raw: str) -> Path:
    normalized = raw.strip().replace("\\", "/")
    pure = PurePosixPath(normalized)
    if not normalized or pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"Path must be relative and stay inside the root: {raw!r}")
    candidate = (root / Path(*pure.parts)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Path escapes project root: {raw!r}") from exc
    return candidate


def read_plan(plan_path: Path) -> list[dict[str, str]]:
    with plan_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Plan is missing columns: {', '.join(sorted(missing))}")
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in reader
        ]


def prepare(root: Path, rows: list[dict[str, str]], allow_high_risk: bool) -> dict:
    approved: list[dict[str, object]] = []
    skipped: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []
    destinations: set[Path] = set()
    sources: set[Path] = set()

    for index, row in enumerate(rows, start=2):
        row_id = row.get("id") or f"line-{index}"
        if row.get("approved", "").lower() not in TRUE_VALUES:
            skipped.append({"id": row_id, "reason": "not approved"})
            continue
        if row.get("action", "").lower() not in {"move", "rename"}:
            errors.append({"id": row_id, "error": "action must be move or rename"})
            continue
        try:
            source = safe_target(root, row["source"])
            destination = safe_target(root, row["destination"])
        except ValueError as exc:
            errors.append({"id": row_id, "error": str(exc)})
            continue
        if source == destination:
            errors.append({"id": row_id, "error": "source equals destination"})
        elif source in sources:
            errors.append({"id": row_id, "error": "duplicate source"})
        elif destination in destinations:
            errors.append({"id": row_id, "error": "duplicate destination"})
        elif not source.is_file():
            errors.append({"id": row_id, "error": "source is missing or not a file"})
        elif source.is_symlink():
            errors.append({"id": row_id, "error": "symlink sources are not supported"})
        elif destination.exists():
            errors.append({"id": row_id, "error": "destination already exists"})
        elif (
            source.suffix.lower() in HIGH_RISK_EXTENSIONS
            or row.get("risk", "").lower() == "high"
        ) and not allow_high_risk:
            errors.append(
                {
                    "id": row_id,
                    "error": "high-risk move requires --allow-high-risk",
                }
            )
        else:
            sources.add(source)
            destinations.add(destination)
            approved.append(
                {
                    "id": row_id,
                    "action": row["action"].lower(),
                    "source": source,
                    "destination": destination,
                    "source_relative": source.relative_to(root).as_posix(),
                    "destination_relative": destination.relative_to(root).as_posix(),
                    "reason": row["reason"],
                    "confidence": row["confidence"],
                    "risk": row["risk"],
                }
            )
    return {"approved": approved, "skipped": skipped, "errors": errors}


def append_ledger(ledger: Path, record: dict[str, str]) -> None:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    exists = ledger.exists()
    with ledger.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(record))
        if not exists:
            writer.writeheader()
        writer.writerow(record)


def run(
    root: Path,
    plan: Path,
    apply: bool,
    ack_backup: bool,
    allow_high_risk: bool,
    ledger: Path | None,
) -> tuple[dict, int]:
    root = root.expanduser().resolve()
    plan = plan.expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Project root is not a directory: {root}")
    if apply and not ack_backup:
        raise ValueError("--apply requires --ack-backup")
    rows = read_plan(plan)
    prepared = prepare(root, rows, allow_high_risk)
    result: dict[str, object] = {
        "mode": "apply" if apply else "dry-run",
        "root": str(root),
        "plan": str(plan),
        "approved": [
            {
                key: str(value) if isinstance(value, Path) else value
                for key, value in operation.items()
                if key not in {"source", "destination"}
            }
            for operation in prepared["approved"]
        ],
        "skipped": prepared["skipped"],
        "errors": prepared["errors"],
        "applied": [],
    }
    if prepared["errors"]:
        return result, 2
    if not apply:
        return result, 0

    ledger_path = (
        ledger.expanduser().resolve()
        if ledger
        else root / "athanor" / "organization-ledger.csv"
    )
    try:
        ledger_path.relative_to(root)
    except ValueError as exc:
        raise ValueError("Ledger must be inside the project root") from exc

    for operation in prepared["approved"]:
        source = operation["source"]
        destination = operation["destination"]
        before_hash = sha256(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        after_hash = sha256(destination)
        if before_hash != after_hash:
            raise RuntimeError(
                f"Hash mismatch after moving {operation['source_relative']}"
            )
        record = {
            "timestamp": utc_timestamp(),
            "id": str(operation["id"]),
            "action": str(operation["action"]),
            "source": str(operation["source_relative"]),
            "destination": str(operation["destination_relative"]),
            "sha256_before": before_hash,
            "sha256_after": after_hash,
            "status": "moved",
        }
        append_ledger(ledger_path, record)
        result["applied"].append(record)
    result["ledger"] = str(ledger_path)
    return result, 0


def main() -> int:
    args = parse_args()
    result, code = run(
        args.root,
        args.plan,
        args.apply,
        args.ack_backup,
        args.allow_high_risk,
        args.ledger,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
