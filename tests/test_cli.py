"""Tests for layer0.cli: the start-day/log-day CLI contract.

Seam: main(argv, data_dir=..., dashboard_path=..., clock=...) — the CLI
entry point, with paths and the clock injected so tests don't touch real
repo files or wall-clock time.
"""
from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from layer0.cli import main
from layer0.store import read_log, read_marker


class CliTests(unittest.TestCase):
    def _run(
        self, argv: list[str], data_dir: Path, dashboard_path: Path, when: datetime
    ) -> int:
        return main(
            argv,
            data_dir=data_dir,
            dashboard_path=dashboard_path,
            clock=lambda: when,
        )

    def test_start_day_writes_marker(self) -> None:
        with TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            when = datetime(2026, 9, 11, 8, 0, 0, tzinfo=timezone.utc)
            self._run(
                ["start-day", "--target-minutes", "30"],
                data_dir,
                Path(tmp) / "dashboard.html",
                when,
            )
            marker = read_marker(data_dir / ".in-progress.json")
            assert marker is not None
            self.assertEqual(marker["date"], "2026-09-11")
            self.assertEqual(marker["target_minutes"], 30)
            self.assertEqual(marker["started_at"], when.isoformat())

    def test_log_day_appends_entry_using_marker_and_regenerates_dashboard(self) -> None:
        with TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            dashboard_path = Path(tmp) / "dashboard.html"
            started = datetime(2026, 9, 11, 8, 0, 0, tzinfo=timezone.utc)
            self._run(["start-day", "--target-minutes", "30"], data_dir, dashboard_path, started)

            finished = datetime(2026, 9, 11, 8, 30, 0, tzinfo=timezone.utc)
            self._run(
                ["log-day", "--mission", "Intro to attention mechanisms"],
                data_dir,
                dashboard_path,
                finished,
            )

            entries = read_log(data_dir / "log.jsonl")
            self.assertEqual(len(entries), 1)
            entry = entries[0]
            self.assertEqual(entry["date"], "2026-09-11")
            self.assertEqual(entry["mission"], "Intro to attention mechanisms")
            self.assertEqual(entry["target_minutes"], 30)
            self.assertEqual(entry["started_at"], started.isoformat())
            self.assertEqual(entry["completed_at"], finished.isoformat())
            self.assertTrue(entry["completed"])
            self.assertIsNone(entry["exercise"])
            self.assertEqual(entry["streak_state"], "active")

            self.assertIsNone(read_marker(data_dir / ".in-progress.json"))
            self.assertTrue(dashboard_path.exists())

    def test_log_day_without_start_day_falls_back(self) -> None:
        with TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            dashboard_path = Path(tmp) / "dashboard.html"
            when = datetime(2026, 9, 11, 9, 0, 0, tzinfo=timezone.utc)
            self._run(["log-day", "--mission", "Solo session"], data_dir, dashboard_path, when)

            entries = read_log(data_dir / "log.jsonl")
            entry = entries[0]
            self.assertEqual(entry["started_at"], when.isoformat())
            self.assertIsNone(entry["target_minutes"])

    def test_log_day_ignores_stale_marker_from_a_different_day(self) -> None:
        with TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            dashboard_path = Path(tmp) / "dashboard.html"
            self._run(
                ["start-day", "--target-minutes", "30"],
                data_dir,
                dashboard_path,
                datetime(2026, 9, 10, 8, 0, 0, tzinfo=timezone.utc),
            )
            when = datetime(2026, 9, 11, 9, 0, 0, tzinfo=timezone.utc)
            self._run(["log-day", "--mission", "Next day"], data_dir, dashboard_path, when)

            entries = read_log(data_dir / "log.jsonl")
            entry = entries[0]
            self.assertEqual(entry["date"], "2026-09-11")
            self.assertEqual(entry["started_at"], when.isoformat())
            self.assertIsNone(entry["target_minutes"])
            self.assertIsNone(read_marker(data_dir / ".in-progress.json"))

    def test_log_day_parses_exercise_json(self) -> None:
        with TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            dashboard_path = Path(tmp) / "dashboard.html"
            when = datetime(2026, 9, 11, 9, 0, 0, tzinfo=timezone.utc)
            exercise = {
                "type": "quiz",
                "items": [{"topic": "scaled dot-product attention", "correct": True}],
            }
            self._run(
                ["log-day", "--mission", "m", "--exercise", json.dumps(exercise)],
                data_dir,
                dashboard_path,
                when,
            )
            entries = read_log(data_dir / "log.jsonl")
            self.assertEqual(entries[0]["exercise"], exercise)

    def test_log_day_streak_state_is_always_active_for_the_day_being_logged(self) -> None:
        # Calling log-day makes today completed, so by the state machine's own
        # rules today's own entry always reads "active" — even after a missed
        # day — because completion is never refused (ADR 0002).
        with TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            dashboard_path = Path(tmp) / "dashboard.html"
            self._run(
                ["log-day", "--mission", "day 1"],
                data_dir,
                dashboard_path,
                datetime(2026, 9, 9, 8, 0, 0, tzinfo=timezone.utc),
            )
            # 2026-09-10 missed entirely; log-day called on 2026-09-11.
            self._run(
                ["log-day", "--mission", "day after a miss"],
                data_dir,
                dashboard_path,
                datetime(2026, 9, 11, 8, 0, 0, tzinfo=timezone.utc),
            )
            entries = read_log(data_dir / "log.jsonl")
            self.assertEqual(entries[1]["streak_state"], "active")


if __name__ == "__main__":
    unittest.main()
