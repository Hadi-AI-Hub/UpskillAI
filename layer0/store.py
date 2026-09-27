"""Imperative Shell: JSONL log and marker-file I/O.

The log is append-only (one line per day). The marker file is a transient
record of an in-progress day, written by `start-day` and always deleted by
`log-day` regardless of whether it was used.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_log(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def append_entry(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def read_marker(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        result: dict[str, Any] = json.load(f)
        return result


def write_marker(path: Path, marker: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(marker, f)


def delete_marker(path: Path) -> None:
    path.unlink(missing_ok=True)
