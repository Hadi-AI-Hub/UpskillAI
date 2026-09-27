"""Layer 1 -> Layer 0 CLI contract.

    start-day --target-minutes N
    log-day --mission "..." [--exercise '{"type":"quiz","items":[...]}']

Calling log-day at all is the completion signal — there is no --completed
flag (ADR 0002: completion is content-based, never refused by Layer 0).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from layer0.dashboard import render_dashboard
from layer0.state_machine import completed_dates_from_entries, compute_streak_state
from layer0.store import append_entry, delete_marker, read_log, read_marker, write_marker

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = REPO_ROOT / "layer0" / "data"
DEFAULT_DASHBOARD_PATH = REPO_ROOT / "dashboard.html"

Clock = Callable[[], datetime]


def _default_clock() -> datetime:
    return datetime.now().astimezone()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="upskill")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_day = subparsers.add_parser("start-day")
    start_day.add_argument("--target-minutes", type=int, required=True)

    log_day = subparsers.add_parser("log-day")
    log_day.add_argument("--mission", required=True)
    log_day.add_argument("--exercise")

    return parser


def run_start_day(args: argparse.Namespace, *, data_dir: Path, clock: Clock) -> None:
    now = clock()
    today = now.date()
    marker = {
        "date": today.isoformat(),
        "started_at": now.isoformat(),
        "target_minutes": args.target_minutes,
    }
    write_marker(data_dir / ".in-progress.json", marker)
    print(f"Started {today.isoformat()} (target {args.target_minutes} min).")


def run_log_day(
    args: argparse.Namespace, *, data_dir: Path, dashboard_path: Path, clock: Clock
) -> None:
    now = clock()
    today = now.date()
    marker_path = data_dir / ".in-progress.json"
    marker = read_marker(marker_path)

    if marker is not None and marker.get("date") == today.isoformat():
        started_at = marker["started_at"]
        target_minutes = marker.get("target_minutes")
    else:
        started_at = now.isoformat()
        target_minutes = None
    delete_marker(marker_path)

    exercise: dict[str, Any] | None = json.loads(args.exercise) if args.exercise else None

    log_path = data_dir / "log.jsonl"
    entries = read_log(log_path)
    completed_dates = completed_dates_from_entries(entries)
    completed_dates.add(today)
    streak_state = compute_streak_state(completed_dates, today)

    entry = {
        "date": today.isoformat(),
        "mission": args.mission,
        "target_minutes": target_minutes,
        "started_at": started_at,
        "completed_at": now.isoformat(),
        "completed": True,
        "exercise": exercise,
        "streak_state": streak_state,
    }
    append_entry(log_path, entry)

    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(render_dashboard(entries + [entry], today=today), encoding="utf-8")

    print(f"Logged {today.isoformat()}: streak {streak_state}.")


def main(
    argv: list[str] | None = None,
    *,
    data_dir: Path | None = None,
    dashboard_path: Path | None = None,
    clock: Clock | None = None,
) -> int:
    data_dir = data_dir or DEFAULT_DATA_DIR
    dashboard_path = dashboard_path or DEFAULT_DASHBOARD_PATH
    clock = clock or _default_clock

    args = build_parser().parse_args(argv)

    if args.command == "start-day":
        run_start_day(args, data_dir=data_dir, clock=clock)
    elif args.command == "log-day":
        run_log_day(args, data_dir=data_dir, dashboard_path=dashboard_path, clock=clock)

    return 0


if __name__ == "__main__":
    sys.exit(main())
